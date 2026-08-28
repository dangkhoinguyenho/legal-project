"""
Retrieval — find candidate articles from a plain-language fact pattern.

BM25, implemented here rather than pulled from a library, so every line is
readable and there is no hidden behaviour.

VIETNAMESE TOKENISATION, HONESTLY: proper Vietnamese needs word segmentation
(underthesea / pyvi), because "tài sản" is ONE word written as two syllables.
We do not use those. Instead we index unigrams AND bigrams of syllables, so
"tài sản" is captured as the bigram "tài_sản". This is a poor man's segmenter.
It is good enough to measure, and it is a known weakness to revisit if recall
is bad.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTICLES = REPO / "data" / "corpus" / "articles.jsonl"

K1, B = 1.5, 0.75

# Very common syllables that carry no signal in legal text.
STOP = {
    "của", "và", "các", "có", "trong", "được", "là", "cho", "với", "này",
    "thì", "về", "khi", "hoặc", "theo", "tại", "đã", "để", "một", "những",
    "người", "quy", "định", "trường", "hợp", "nếu", "mà", "không", "phải",
}


def lam_sach_truy_van(s: str) -> str:
    """Strip what carries no legal signal: amounts, dates, areas, anonymised
    initials. A fact pattern says "127,8 m2", "43.000.000 đồng", "ông L",
    "31/12/2002" — none of that appears in a statute, and embeddings average
    the whole query, so this noise drags the vector toward generic articles.
    The sanity check in embed.py found Điều 60 at rank 7 with a SHORT query;
    the full fact pattern buried it."""
    s = re.sub(r"\d[\d.,]*\s*(m2|m²|đồng|triệu|tỷ)?", " ", s)
    s = re.sub(r"\b(ông|bà|anh|chị)\s+[A-ZĐ]\b", " ", s)
    s = re.sub(r"\bnăm\s+\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tach_tu(s: str) -> list[str]:
    """Lowercase, strip punctuation, return unigrams + bigrams."""
    s = re.sub(r"[^\w\sÀ-ỹ]", " ", str(s or "").lower())
    syl = [t for t in s.split() if t and t not in STOP]
    bigrams = [f"{syl[i]}_{syl[i+1]}" for i in range(len(syl) - 1)]
    return syl + bigrams


class BM25:
    def __init__(self, docs: list[dict], field=lambda d: d["tieu_de"] + " " + d["noi_dung"]):
        self.docs = docs
        self.toks = [tach_tu(field(d)) for d in docs]
        self.len = [len(t) for t in self.toks]
        self.avg = sum(self.len) / max(len(self.len), 1)
        self.tf = [Counter(t) for t in self.toks]
        df = Counter()
        for t in self.toks:
            df.update(set(t))
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def tim(self, truy_van: str, k: int = 10) -> list[tuple[dict, float]]:
        q = tach_tu(truy_van)
        diem = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for w in q:
                f = tf.get(w, 0)
                if not f:
                    continue
                s += self.idf.get(w, 0) * (f * (K1 + 1)) / (
                    f + K1 * (1 - B + B * self.len[i] / max(self.avg, 1)))
            if s > 0:
                diem.append((i, s))
        diem.sort(key=lambda x: -x[1])
        return [(self.docs[i], s) for i, s in diem[:k]]


def nap_corpus() -> list[dict]:
    if not ARTICLES.exists():
        raise FileNotFoundError(f"{ARTICLES} missing — run src/parse_articles.py first.")
    with ARTICLES.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------- embeddings

VEC = REPO / "data" / "corpus" / "embeddings.npy"
REFS = REPO / "data" / "corpus" / "embeddings.refs.json"


class Embed:
    """Semantic search. Optional — falls back silently if not built yet."""

    def __init__(self, docs: list[dict]):
        self.san_sang = False
        if not (VEC.exists() and REFS.exists()):
            return
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return
        meta = json.loads(REFS.read_text(encoding="utf-8"))
        self.V = np.load(VEC)
        theo_ref = {d["ref"]: d for d in docs}
        self.docs = [theo_ref.get(r) for r in meta["refs"]]
        if len(self.docs) != len(self.V) or any(d is None for d in self.docs):
            print("  [embed] corpus and embeddings disagree — rebuild with src/embed.py")
            return
        self.model = SentenceTransformer(meta["model"])
        self.san_sang = True

    def tim(self, truy_van: str, k: int = 10) -> list[tuple[dict, float]]:
        if not self.san_sang:
            return []
        qv = self.model.encode([truy_van], normalize_embeddings=True,
                               convert_to_numpy=True)[0]
        diem = self.V @ qv
        top = diem.argsort()[::-1][:k]
        return [(self.docs[i], float(diem[i])) for i in top]


def hop_nhat(bm: list[tuple[dict, float]], em: list[tuple[dict, float]],
             k: int = 12) -> list[tuple[dict, float, str]]:
    """INTERLEAVE the two lists: bm25#1, embed#1, bm25#2, embed#2, ...

    v1 (rank fusion) flattened ranks into noise — 1/(60+rank) spans 15% across
    a 12-item list. Recall fell 46% -> 38%.

    v2 (union) appended ALL of BM25 and then ALL of embeddings. Measured with
    eval/diagnose_ranking.py, that put every embeddings-only correct answer at
    position 10 or worse:

        Đ59 #10   Đ60 #11   Đ213 #13   Đ7 #14   Đ37 #14   Đ43 #17   Đ63 #32
        all of them  nguon=embed

    Embeddings' best result was queuing behind BM25's twenty-fourth. That is
    not a ranking, it is a filing order.

    v3 alternates, so rank 1 of either method beats rank 2 of the other. An
    article found by BOTH keeps its earlier position and is marked, which lets
    the pipeline put it in the top band — and band 0 is measurably the good
    one: its hits land at positions 1, 1, 1, 3, 3, 5.
    """
    thu_tu: list[tuple[dict, float, str]] = []
    da_co: dict[str, int] = {}

    def them(d, sc, ten):
        ref = d["ref"]
        if ref in da_co:                       # seen already -> mark agreement
            i = da_co[ref]
            dd, ss, ng = thu_tu[i]
            if ten not in ng:
                thu_tu[i] = (dd, ss, ng + "+" + ten)
            return
        da_co[ref] = len(thu_tu)
        thu_tu.append((d, sc, ten))

    for i in range(max(len(bm), len(em))):
        if i < len(bm):
            them(bm[i][0], bm[i][1], "bm25")
        if i < len(em):
            them(em[i][0], em[i][1], "embed")
    return thu_tu
