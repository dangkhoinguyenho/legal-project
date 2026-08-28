"""
The end-to-end path. Fact pattern in, document stack out.

    tình huống -> tìm điều (BM25 + embeddings) -> lọc phạm vi
               -> mở rộng theo đồ thị -> dán nhãn hiệu lực -> in ra

NO MODEL IS CALLED IN THIS FILE. Everything here is rules and lookups.
Nothing outside data/allowlist.csv can appear, by construction.

THE SCOPE GATE (new, and it is the FP06 fix)
--------------------------------------------
The first run returned 10 articles for a mang thai hộ question that should have
returned nothing, 6 of them from the `control` group. The reason: `control` only
marks whole DOCUMENTS, and Luật HNGĐ is a `core` document that also happens to
contain Điều 95-100 about mang thai hộ. Document-level scope cannot express that.

So data/scope_articles.csv names the ARTICLE RANGES this tool answers about —
Đ29-50 and Đ59-64 of Luật HNGĐ, not Đ95-100. Two rules follow:

  1. `control` documents never reach the output. If any are retrieved that is a
     retrieval defect and gets counted, not printed.
  2. If nothing in scope survives, the answer is "không tìm thấy" — never the
     next-best thing.

Run:  python src/pipeline.py
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from force_check import Moc, kiem_tra          # noqa: E402
from retrieve import (BM25, Embed, hop_nhat, lam_sach_truy_van,  # noqa: E402
                      nap_corpus)

REPO = Path(__file__).resolve().parent.parent
RELATIONS = REPO / "data" / "article_relations.csv"
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
SCOPE = REPO / "data" / "scope_articles.csv"


@dataclass
class TrichDan:
    ref: str
    so_hieu: str
    dieu: int
    tieu_de: str
    rank: int
    scope: str
    nguon: str
    nhan_hieu_luc: str
    ghi_chu: str
    thu_hang: int = 999   # display order; lower is more confident


def nap_pham_vi() -> dict[str, list[tuple[int, int]]]:
    g = defaultdict(list)
    if SCOPE.exists():
        with SCOPE.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                g[r["doc_key"]].append((int(r["tu_dieu"]), int(r["den_dieu"])))
    return g


def trong_pham_vi(d: dict, pv) -> bool:
    return any(a <= d["dieu"] <= b for a, b in pv.get(d["doc_key"], []))


def nap_do_thi() -> dict[str, list[str]]:
    g = defaultdict(list)
    if RELATIONS.exists():
        with RELATIONS.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                s, t = r["source_ref"].strip(), r["target_ref"].strip()
                if "#" in s and "#" in t:
                    g[s].append(t)
                    g[t].append(s)
    return g


def nap_metadata() -> dict[str, dict]:
    with MATCHED.open(encoding="utf-8") as f:
        return {r["so_ky_hieu"]: r for r in csv.DictReader(f)}


def chay(tinh_huong: str, mocs: list[Moc], k: int = 12, mo_rong: bool = True,
         dung_embed: bool = True):
    """Returns (citations, diagnostics)."""
    corpus = nap_corpus()
    bm = BM25(corpus)
    em = Embed(corpus) if dung_embed else None
    pv, do_thi, meta = nap_pham_vi(), nap_do_thi(), nap_metadata()
    theo_ref = {d["ref"]: d for d in corpus}

    # Retrieve wider than we display: the scope gate removes what does not belong.
    tv = lam_sach_truy_van(tinh_huong)
    bm_hits = bm.tim(tv, k * 2)
    em_hits = em.tim(tv, k * 2) if (em and em.san_sang) else []
    tron = hop_nhat(bm_hits, em_hits, k) if em_hits else [
        (d, s, "bm25") for d, s in bm_hits]

    chan_doan = {"tim_duoc": len(tron), "control_ro": 0, "ngoai_pham_vi": 0,
                 "co_embed": bool(em_hits)}

    ket_qua: dict[str, TrichDan] = {}

    def them(d: dict, nguon: str, thu_hang: int = 999):
        if d["ref"] in ket_qua:
            return
        if d["scope"] == "control":
            chan_doan["control_ro"] += 1     # counted, never printed
            return
        if not trong_pham_vi(d, pv):
            chan_doan["ngoai_pham_vi"] += 1
            return
        md = meta.get(d["so_hieu"])
        if md:
            kq = None
            for m in mocs:
                kq = kiem_tra(md, m)
                if not kq.bi_chan:
                    break
            nhan, ghi = kq.ma, kq.thong_diep
        else:
            nhan, ghi = "THIEU_METADATA", "not in metadata_matched.csv"
        ket_qua[d["ref"]] = TrichDan(d["ref"], d["so_hieu"], d["dieu"],
                                     d["tieu_de"], d["rank"], d["scope"],
                                     nguon, nhan, ghi, thu_hang)

    # ORDER MATTERS: this is a reading list, and nobody reads item 30.
    #
    # BUG FIXED HERE. v1 put graph-expanded articles LAST, below everything the
    # machine retrieved. That was backwards, and it was measured:
    #     recall@5 21%, recall@8 21%, recall@20 47%
    # Positions 6-8 held nothing correct; over half the right answers sat at
    # 11-20. FP02's six hits came almost entirely from graph expansion — the
    # hand-built map — which I had ranked below noisy machine guesses.
    #
    # article_relations.csv is the most trustworthy thing in this system: a
    # human wrote every edge and checked it against the statute. It belongs
    # near the top, not the bottom.
    #
    # New order:
    #   0  found by BM25 AND embeddings independently   (two methods agreeing)
    #   1  graph neighbour of a band-0 article          (human map, strong seed)
    #   2  found by one method
    #   3  graph neighbour of a band-2 article          (human map, weak seed)
    for i, (d, _s, src) in enumerate(tron):
        band = 0 if "+" in src else 2
        them(d, src, band * 1000 + i)

    if mo_rong:
        hat_giong = sorted(ket_qua.values(), key=lambda x: x.thu_hang)
        for c in hat_giong:
            band_moi = 1 if c.thu_hang < 1000 else 3
            for nb in do_thi.get(c.ref, []):
                if nb in theo_ref:
                    them(theo_ref[nb], f"mở rộng từ {c.ref.split('#')[1]}",
                         band_moi * 1000 + (c.thu_hang % 1000))

    xep = sorted(ket_qua.values(), key=lambda x: x.thu_hang)
    return xep, chan_doan


def in_ra(tinh_huong: str, mocs: list[Moc], kq, cd):
    print("=" * 80)
    print("TÌNH HUỐNG\n  " + tinh_huong.strip().replace("\n", "\n  "))
    print("\nMỐC THỜI GIAN")
    for m in mocs:
        print(f"  {m.ten}: {m.ngay:%d/%m/%Y}")
    print("-" * 80)
    if not kq:
        print("  KHÔNG TÌM THẤY")
        print("  Câu hỏi này nằm ngoài phạm vi công cụ (chia tài sản vợ chồng),")
        print("  hoặc kho tài liệu không có căn cứ để trả lời.")
        print("-" * 80)
        print(f"  chẩn đoán: {cd}")
        print("=" * 80)
        return
    print(f"{'VĂN BẢN':<16}{'ĐIỀU':<7}{'HẠNG':<6}{'HIỆU LỰC':<24}NGUỒN")
    print("-" * 80)
    for i, c in enumerate(kq, 1):
        print(f"{i:>3}. {c.so_hieu[:13]:<14}Đ{c.dieu:<5}{c.rank:<5}"
              f"{c.nhan_hieu_luc:<23}{c.nguon[:20]}")
    print("-" * 80)
    print(f"  {len(kq)} điều trong phạm vi | "
          f"control chặn: {cd['control_ro']} | ngoài phạm vi: {cd['ngoai_pham_vi']} | "
          f"embeddings: {'có' if cd['co_embed'] else 'KHÔNG'}")
    print("=" * 80)


if __name__ == "__main__":
    th = ("Vợ chồng kết hôn năm 2005. Năm 2010 mua một mảnh đất, giấy chứng nhận "
          "quyền sử dụng đất chỉ đứng tên người chồng. Vợ làm nội trợ. Năm 2024 "
          "ly hôn, tranh chấp mảnh đất này là tài sản chung hay riêng và chia thế nào.")
    mocs = [Moc("tài sản hình thành", date(2010, 6, 1)), Moc("ly hôn", date(2024, 3, 1))]
    kq, cd = chay(th, mocs)
    in_ra(th, mocs, kq, cd)
