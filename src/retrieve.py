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
    """UNION, not fusion. Embeddings may ADD results, never displace BM25's.

    WHY NOT RANK FUSION — this was measured, not guessed.
    v1 used reciprocal rank fusion, score = 1/(60 + rank), then cut to k.
    With only 12 candidates per list that constant flattens everything:

        rank 1  -> 1/61 = 0.01639
        rank 12 -> 1/72 = 0.01389        a 15% spread across the WHOLE list

    So ordering among single-source hits became close to arbitrary, and FP02
    lost Điều 61 and Điều 63 — correct BM25 hits pushed out by mediocre
    embedding hits. Recall fell 46% -> 38%.

    RRF's k=60 assumes lists of several hundred. Ours are twelve. Rather than
    tune a constant on six examples, take the union and let the scope gate and
    the graph handle precision — both of which are already measured to work.
    """
    ra: list[tuple[dict, float, str]] = []
    da_co: set[str] = set()
    for ten, ds in (("bm25", bm), ("embed", em)):
        for d, sc in ds:
            if d["ref"] in da_co:
                for i, (dd, ss, ng) in enumerate(ra):
                    if dd["ref"] == d["ref"] and ten not in ng:
                        ra[i] = (dd, ss, ng + "+" + ten)
                continue
            da_co.add(d["ref"])
            ra.append((d, sc, ten))
    return ra
