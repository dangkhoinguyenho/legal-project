"""
Build embeddings for the corpus so retrieval can bridge the vocabulary gap.

WHY THIS EXISTS — the measured reason, not a guess.
The BM25-only run scored 46% and lost ALL its points on two patterns:
    FP03 (nợ chung)          0/6
    FP05 (trước kết hôn)     0/5
The facts say "nợ", "vay", "ngân hàng". Điều 37 says "nghĩa vụ chung về tài sản".
Almost no shared words, so keyword search never reaches it. That gap between how
people describe facts and how statutes are written is what embeddings close.

MODEL: AITeamVN/Vietnamese_Embedding (bge-m3 based, purpose-built for Vietnamese).
First run downloads roughly 2 GB and then caches. Encoding ~2,400 articles on CPU
takes a few minutes; the result is cached to disk and reused.

Run:  python src/embed.py
Out:  data/corpus/embeddings.npy  +  embeddings.refs.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTICLES = REPO / "data" / "corpus" / "articles.jsonl"
VEC = REPO / "data" / "corpus" / "embeddings.npy"
REFS = REPO / "data" / "corpus" / "embeddings.refs.json"

MODEL = "AITeamVN/Vietnamese_Embedding"
# Smaller fallback if the machine cannot hold the big one.
MODEL_NHO = "dangvantuan/vietnamese-embedding"


def van_ban_de_nhung(a: dict) -> str:
    """Title carries most of the signal; include a slice of the body for context."""
    return f"{a['so_hieu']} Điều {a['dieu']}. {a['tieu_de']}\n{a['noi_dung'][:1200]}"


def main() -> int:
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("Missing packages. Run:")
        print("    pip install sentence-transformers numpy")
        print("(this pulls in torch — a few hundred MB)")
        return 1

    if not ARTICLES.exists():
        print(f"Missing {ARTICLES} — run src/parse_articles.py first.")
        return 1

    arts = [json.loads(l) for l in ARTICLES.open(encoding="utf-8") if l.strip()]
    print(f"{len(arts):,} article units to encode")

    ten = MODEL_NHO if "--nho" in sys.argv else MODEL
    print(f"Loading {ten} ... (first run downloads the model)")
    try:
        m = SentenceTransformer(ten)
    except Exception as e:
        print(f"Could not load {ten}: {type(e).__name__}: {str(e)[:160]}")
        print("Try the smaller model:  python src/embed.py --nho")
        return 1

    texts = [van_ban_de_nhung(a) for a in arts]
    print("Encoding — this takes a few minutes on CPU ...")
    V = m.encode(texts, batch_size=8, show_progress_bar=True,
                 normalize_embeddings=True, convert_to_numpy=True)

    VEC.parent.mkdir(parents=True, exist_ok=True)
    np.save(VEC, V)
    REFS.write_text(json.dumps({"model": ten, "refs": [a["ref"] for a in arts]},
                               ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {V.shape} -> {VEC.relative_to(REPO)}")

    # Sanity check: a debt query should rank Điều 37 near the top.
    q = "vợ chồng vay tiền ngân hàng và nợ tiền mua thức ăn chăn nuôi khi ly hôn ai trả"
    qv = m.encode([q], normalize_embeddings=True, convert_to_numpy=True)[0]
    top = (V @ qv).argsort()[::-1][:8]
    print(f"\nSanity check — query: {q}")
    for i in top:
        a = arts[i]
        print(f"   {a['so_hieu']:<20} Điều {a['dieu']:<4} {a['tieu_de'][:48]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
