"""
Why is recall@8 stuck at 21% when recall over the whole list is 71%?

The ranking fix (promoting the hand-built map from last to second) changed
NOTHING — every number identical to the digit. So my theory about where the
correct answers sit must be wrong.

This script stops theorising and prints, for every expected citation:
    - what position it landed at in the ranked list
    - which band it came from (retrieval-both / map-strong / retrieval-one /
      map-weak)
    - the source that produced it

Whatever pattern shows up in the "position" column is the actual problem.

Run:  python eval/diagnose_ranking.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "eval"))

from pipeline import chay                                   # noqa: E402
from run_system import MOCS, TEN_SANG_KEY, tach_dieu        # noqa: E402

FP = REPO / "eval" / "fact_patterns.csv"
EC = REPO / "eval" / "expected_citations.csv"


def ten_band(t: int) -> str:
    return {0: "0 tìm-cả-hai", 1: "1 map-mạnh",
            2: "2 tìm-một", 3: "3 map-yếu"}.get(t // 1000, f"? {t}")


def main() -> int:
    with FP.open(encoding="utf-8") as f:
        patterns = [r for r in csv.DictReader(f) if r["id"] != "FP06"]
    with EC.open(encoding="utf-8") as f:
        expected = list(csv.DictReader(f))

    ky_vong = {}
    for r in expected:
        if not r["van_ban"]:
            continue
        key = TEN_SANG_KEY.get(r["van_ban"].strip(), "?")
        if not key:
            continue
        for d in tach_dieu(r["dieu"]):
            ky_vong.setdefault(r["pattern_id"], []).append(
                (f"{key}#D{d}", r["van_ban"], d, r["bat_buoc"] == "yes"))

    vi_tri_tat_ca = []
    band_dem = {}

    for p in patterns:
        pid = p["id"]
        kq, _cd = chay(p["tinh_huong"], MOCS[pid], k=12)
        vi_tri = {c.ref: (i + 1, c) for i, c in enumerate(kq)}

        print("=" * 76)
        print(f"{pid} — {p['nhom_van_de']}    ({len(kq)} điều trả về)")
        print("=" * 76)
        print(f"  {'VỊ TRÍ':<8}{'BAND':<16}{'ĐIỀU':<26}NGUỒN")
        print("  " + "-" * 72)
        for ref, ten, d, bb in ky_vong.get(pid, []):
            sao = "*" if bb else " "
            if ref in vi_tri:
                i, c = vi_tri[ref]
                b = ten_band(c.thu_hang)
                band_dem[b] = band_dem.get(b, 0) + 1
                vi_tri_tat_ca.append(i)
                canh = "  <-- ngoài top 8" if i > 8 else ""
                print(f"  #{i:<7}{b:<16}{ten[:18]:<19}Đ{d:<5}{c.nguon[:20]}{canh}")
            else:
                print(f"  {'--':<8}{'KHÔNG TÌM THẤY':<16}{ten[:18]:<19}Đ{d:<5}")
        print()

    print("=" * 76)
    print("TỔNG HỢP — các điều ĐÚNG nằm ở đâu")
    print("=" * 76)
    if vi_tri_tat_ca:
        vi_tri_tat_ca.sort()
        print(f"  Tìm thấy {len(vi_tri_tat_ca)} điều đúng trong danh sách")
        print(f"  Vị trí   : {vi_tri_tat_ca}")
        trong8 = sum(1 for v in vi_tri_tat_ca if v <= 8)
        print(f"  Trong top 8 : {trong8}")
        print(f"  Ngoài top 8 : {len(vi_tri_tat_ca) - trong8}")
    print("\n  Các điều đúng đến từ band nào:")
    for b, n in sorted(band_dem.items()):
        print(f"    {b:<18} {n}")
    print("\n  ĐỌC KẾT QUẢ:")
    print("   - Nếu điều đúng phần lớn ở band '3 map-yếu' -> phải nâng band đó lên")
    print("   - Nếu ở band '2 tìm-một' nhưng vị trí lớn  -> quá nhiều rác band 0/1 chen trước")
    print("   - Nếu ở band '0 tìm-cả-hai' mà vị trí vẫn lớn -> retrieval xếp hạng kém")
    return 0


if __name__ == "__main__":
    sys.exit(main())
