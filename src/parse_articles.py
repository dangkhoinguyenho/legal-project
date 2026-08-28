"""
Split each document's HTML into ARTICLE UNITS.

An article unit is the smallest thing the system is allowed to cite:
    {ref: "TTLT01-2016#D7", so_hieu: "01/2016/TTLT-...", dieu: 7,
     tieu_de: "Nguyên tắc giải quyết tài sản...", noi_dung: "..."}

`ref` is the stable ID used everywhere else — in article_relations.csv, in the
validation layer, in the output. Nothing may be cited that does not have one.

Run:  python src/parse_articles.py
Out:  data/corpus/articles.jsonl
"""

import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "data" / "raw" / "content"
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
ALLOWLIST = REPO / "data" / "allowlist.csv"
OUT = REPO / "data" / "corpus" / "articles.jsonl"

# "Điều 7." / "Điều 7 -" / "Điều 7 –" at the start of a line-ish position.
RE_DIEU = re.compile(r"(?:^|\n)\s*Điều\s+(\d+)\s*[.\-–]\s*", re.MULTILINE)


def to_text(html: str) -> str:
    """HTML -> plain text, keeping line breaks so article headings stay findable."""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</h\d>", "\n", s, flags=re.I)
    s = re.sub(r"</td>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"),
                 ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        s = s.replace(a, b)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def split_articles(text: str):
    """Yield (dieu_so, tieu_de, noi_dung) for each Điều found."""
    hits = list(RE_DIEU.finditer(text))
    for i, m in enumerate(hits):
        so = int(m.group(1))
        start = m.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        body = text[start:end].strip()
        # First line is the article heading; the rest is the body.
        parts = body.split("\n", 1)
        tieu_de = parts[0].strip()[:200]
        noi_dung = parts[1].strip() if len(parts) > 1 else ""
        yield so, tieu_de, noi_dung


def main() -> int:
    if not MATCHED.exists():
        print(f"Missing {MATCHED} — run src/pull_metadata.py first.")
        return 1
    with MATCHED.open(encoding="utf-8") as f:
        meta = {r["id"]: r for r in csv.DictReader(f)}
    with ALLOWLIST.open(encoding="utf-8") as f:
        allow = {r["so_hieu"]: r for r in csv.DictReader(f) if r["so_hieu"]}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    n_doc = n_art = 0
    seen_refs = set()
    with OUT.open("w", encoding="utf-8") as out:
        for doc_id, m in meta.items():
            p = CONTENT / f"{doc_id}.html"
            if not p.exists():
                continue
            so_hieu = m["so_ky_hieu"]
            a = allow.get(so_hieu)
            if not a:
                print(f"  [SKIP] {so_hieu} not in allowlist")
                continue
            text = to_text(p.read_text(encoding="utf-8"))
            k = 0
            for so, tieu_de, noi_dung in split_articles(text):
                ref = f"{a['doc_key']}#D{so}"
                if ref in seen_refs:      # duplicate Điều number in one document
                    continue              # (table of contents, appendix) -> keep first
                seen_refs.add(ref)
                out.write(json.dumps({
                    "ref": ref,
                    "doc_key": a["doc_key"],
                    "so_hieu": so_hieu,
                    "rank": int(a["rank"]),
                    "scope": a["scope"],
                    "dieu": so,
                    "tieu_de": tieu_de,
                    "noi_dung": noi_dung,
                }, ensure_ascii=False) + "\n")
                k += 1
            n_doc += 1
            n_art += k
            print(f"  {so_hieu:34} {k:>4} articles")

    print(f"\n{n_doc} documents -> {n_art:,} article units")
    print(f"Written: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
