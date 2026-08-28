"""
Temporal eval — measure the thing that actually makes this project different.

WHY THIS EXISTS
The whole project rests on one claim: it tells you which law was in force AT THE
TIME THE FACTS HAPPENED, not merely today. That claim has never been measured.
`force_check` has unit tests; nothing has ever run it over realistic cases.

WHY WE CAN INVENT THE CASES OURSELVES — and why that is not cheating.
For article prediction the ground truth needs a judge, so we take it from real
judgments. Here it does not. The right answer is DATE ARITHMETIC:

    Luật HNGĐ 2000    in force 01/01/2001 -> 01/01/2015
    Luật HNGĐ 2014    in force from 01/01/2015
    Bộ luật Dân sự 2005  in force 01/01/2006 -> 01/01/2017
    Bộ luật Dân sự 2015  in force from 01/01/2017

Land bought 15/03/2013 -> governed by Luật HNGĐ 2000. That is a fact, checkable
by anyone with a calendar. No legal judgment involved, so we can generate as
many cases as we like without inventing ground truth.

Every expiry date below is DERIVED, not asserted: X died when the statute that
replaced it took effect, and the replacement relation comes from the vbpl graph.

Run:  python eval/run_temporal.py
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from force_check import (  # noqa: E402
    CHUA_RA_DOI, CON_HIEU_LUC, DA_CHET_TRUOC_MOC, LUAT_CU_HOP_LE, MOT_PHAN,
    Moc, kiem_tra,
)

MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"

# Superseded statutes. Not in the corpus, so their metadata is written here.
# Expiry = the day the replacing statute took effect (from the vbpl graph).
LUAT_CU = {
    "22/2000/QH10": {  # Luật HNGĐ 2000, replaced by 52/2014 (hl 01/01/2015)
        "so_ky_hieu": "22/2000/QH10", "ngay_co_hieu_luc": "01/01/2001",
        "ngay_het_hieu_luc": "", "tinh_trang_hieu_luc": "Hết hiệu lực",
        "het_suy_ra": date(2015, 1, 1)},
    "33/2005/QH11": {  # BLDS 2005, replaced by 91/2015 (hl 01/01/2017)
        "so_ky_hieu": "33/2005/QH11", "ngay_co_hieu_luc": "01/01/2006",
        "ngay_het_hieu_luc": "", "tinh_trang_hieu_luc": "Hết hiệu lực",
        "het_suy_ra": date(2017, 1, 1)},
    "45/2013/QH13": {  # Luật Đất đai 2013, replaced by 31/2024
        "so_ky_hieu": "45/2013/QH13", "ngay_co_hieu_luc": "01/07/2014",
        "ngay_het_hieu_luc": "", "tinh_trang_hieu_luc": "Hết hiệu lực",
        "het_suy_ra": date(2024, 8, 1)},
}

# (document, anchor name, anchor date, expected verdict, why)
CA_KIEM_TRA = [
    ("22/2000/QH10", "mua đất", date(2013, 3, 15), LUAT_CU_HOP_LE,
     "Đất mua 2013 — Luật HNGĐ 2000 còn hiệu lực lúc đó. Trích là ĐÚNG."),
    ("22/2000/QH10", "ly hôn", date(2024, 6, 20), DA_CHET_TRUOC_MOC,
     "Ly hôn 2024 — luật này chết từ 2015. Trích cho mốc này là SAI."),
    ("22/2000/QH10", "kết hôn", date(1999, 5, 1), CHUA_RA_DOI,
     "Kết hôn 1999 — luật 2000 chưa ra đời."),
    ("52/2014/QH13", "mua đất", date(2013, 3, 15), CHUA_RA_DOI,
     "BẪY: hầu hết chatbot trả lời bằng Luật 2014 cho MỌI vụ. Sai cho mốc 2013."),
    ("52/2014/QH13", "ly hôn", date(2024, 6, 20), CON_HIEU_LUC,
     "Ly hôn 2024 — Luật HNGĐ 2014 đang có hiệu lực."),
    ("33/2005/QH11", "giao dịch", date(2010, 8, 1), LUAT_CU_HOP_LE,
     "Giao dịch 2010 — BLDS 2005 còn hiệu lực."),
    ("33/2005/QH11", "giao dịch", date(2020, 8, 1), DA_CHET_TRUOC_MOC,
     "Giao dịch 2020 — BLDS 2005 đã chết từ 2017."),
    ("91/2015/QH13", "giao dịch", date(2010, 8, 1), CHUA_RA_DOI,
     "BLDS 2015 chưa ra đời năm 2010."),
    ("45/2013/QH13", "cấp sổ đỏ", date(2016, 4, 10), LUAT_CU_HOP_LE,
     "Sổ đỏ cấp 2016 — Luật Đất đai 2013 còn hiệu lực."),
    ("45/2013/QH13", "cấp sổ đỏ", date(2025, 4, 10), DA_CHET_TRUOC_MOC,
     "Sổ đỏ cấp 2025 — Luật Đất đai 2013 đã chết."),
    ("46/2024/QH15", "công chứng", date(2019, 3, 1), CHUA_RA_DOI,
     "Luật Công chứng 2024 có hiệu lực 01/07/2025. Không thể áp cho 2019."),
    ("46/2024/QH15", "công chứng", date(2026, 3, 1), CON_HIEU_LUC,
     "Công chứng 2026 — luật này đang áp dụng."),
    ("106/2025/QH15", "thi hành án", date(2026, 1, 15), CHUA_RA_DOI,
     "Luật THADS 2025 chỉ có hiệu lực từ 01/07/2026."),
    ("106/2025/QH15", "thi hành án", date(2026, 8, 1), CON_HIEU_LUC,
     "Thi hành án 08/2026 — đã có hiệu lực."),
    ("126/2014/NĐ-CP", "ly hôn", date(2024, 6, 20), MOT_PHAN,
     "Hết hiệu lực một phần — phải kiểm tay điều được trích."),
    ("01/2016/TTLT-TANDTC-VKSNDTC-BTP", "ly hôn", date(2024, 6, 20), CON_HIEU_LUC,
     "TTLT 01/2016 chưa hề bị sửa."),
    ("01/2016/TTLT-TANDTC-VKSNDTC-BTP", "ly hôn", date(2015, 6, 20), CHUA_RA_DOI,
     "TTLT có hiệu lực 01/03/2016 — không áp được cho vụ 2015."),
    ("31/2024/QH15", "cấp sổ đỏ", date(2024, 9, 1), CON_HIEU_LUC,
     "⚠️ CA NGHI NGỜ: metadata ghi hiệu lực 01/01/2025, nhưng Luật 43/2024 đã "
     "dời về 01/08/2024. Nếu ra CHUA_RA_DOI thì metadata sai, không phải code."),
]


def main() -> int:
    with MATCHED.open(encoding="utf-8") as f:
        meta = {r["so_ky_hieu"]: r for r in csv.DictReader(f)}

    print("=" * 78)
    print("TEMPORAL EVAL — luật nào có hiệu lực lúc sự việc xảy ra")
    print("=" * 78)
    dat = sai = 0
    that_bai = []
    for so_hieu, ten_moc, ngay, ky_vong, ly_do in CA_KIEM_TRA:
        cu = LUAT_CU.get(so_hieu)
        doc = cu if cu else meta.get(so_hieu)
        if not doc:
            print(f"  [THIẾU] {so_hieu} không có trong metadata")
            continue
        het = cu["het_suy_ra"] if cu else None
        kq = kiem_tra(doc, Moc(ten_moc, ngay), ngay_het_suy_ra=het)
        ok = kq.ma == ky_vong
        dat += ok
        sai += not ok
        dau = "ĐẠT " if ok else "HỎNG"
        print(f"\n  [{dau}] {so_hieu:<34} {ten_moc} {ngay:%d/%m/%Y}")
        print(f"         kỳ vọng: {ky_vong}")
        if not ok:
            print(f"         thực tế: {kq.ma}  <-- KHÁC")
            that_bai.append((so_hieu, ten_moc, ky_vong, kq.ma, ly_do))
        print(f"         {ly_do}")

    print("\n" + "=" * 78)
    print(f"KẾT QUẢ: {dat}/{dat+sai} đạt")
    if that_bai:
        print(f"\n{len(that_bai)} ca hỏng:")
        for sh, tm, kv, tt, ld in that_bai:
            print(f"  {sh} @ {tm}: kỳ vọng {kv}, ra {tt}")
    print("\nĐỂ SO SÁNH: AI thường được 0/2 ở phần thời gian trong bộ đề bản án")
    print("thật — nó trả lời như thể chỉ có luật hiện hành tồn tại.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
