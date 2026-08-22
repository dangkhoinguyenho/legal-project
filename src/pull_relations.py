"""
Bước 2b — kéo bảng quan hệ, tìm văn bản nào sửa đổi/thay thế văn bản trong allowlist.

VÌ SAO CÓ FILE NÀY: Kenny chỉ ra rằng luật Việt Nam LUÔN ghi rõ nó sửa điều nào
của văn bản nào. Đúng. Ví dụ Luật 85/2025/QH15 ghi thẳng:
    "sửa đổi, bổ sung Điều 18, Điều 35, Điều 36, ... khoản 3 và khoản 4 Điều 53 ..."
    "Bãi bỏ khoản 7 Điều 194", "Bãi bỏ khoản 4 Điều 34"

Thông tin đó KHÔNG có trong config 'metadata' (chỗ tôi nhìn lúc đầu), nhưng nó có ở:
    1. config 'relationships'  -> văn bản NÀO sửa văn bản nào   <- file này
    2. config 'content'        -> ĐIỀU NÀO bị sửa (nằm trong toàn văn)

Script này làm bước 1, và trả lời: bảng quan hệ có dùng được không?

Chạy:  python src/pull_relations.py
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
OUT = REPO / "data" / "raw" / "relations_matched.csv"

DATASET = "th1nhng0/vietnamese-legal-documents"


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("Chay:  pip install datasets")
        return 1

    if not MATCHED.exists():
        print(f"Chua co {MATCHED}. Chay src/pull_metadata.py truoc.")
        return 1

    with MATCHED.open(encoding="utf-8") as f:
        docs = list(csv.DictReader(f))
    ten = {d["id"]: d["so_ky_hieu"] for d in docs}
    print(f"Theo doi {len(ten)} van ban trong allowlist\n")

    print("Dang tai bang quan he ...")
    try:
        tat_ca = load_dataset(DATASET, "relationships")
    except Exception as e:
        print(f"TAI THAT BAI: {type(e).__name__}: {e}")
        print("Bao lai cho Claude, dung tu sua.")
        return 1

    split = "train" if "train" in tat_ca else list(tat_ca.keys())[0]
    ds = tat_ca[split]
    cols = list(ds.column_names)
    print(f"Tai xong: {len(ds):,} dong  (split='{split}')")
    print(f"Cac cot: {cols}\n")

    # Dò tên cột thay vì đoán.
    c_src = next((c for c in ["doc_id", "source_id", "id"] if c in cols), None)
    c_dst = next((c for c in ["other_doc_id", "target_id", "related_id"] if c in cols), None)
    c_rel = next((c for c in ["relationship", "relation", "type"] if c in cols), None)
    if not all([c_src, c_dst, c_rel]):
        print(f"KHONG DOAN DUOC COT. Gui danh sach cot o tren cho Claude.")
        return 1
    print(f"Dung cot: nguon={c_src}  dich={c_dst}  quan_he={c_rel}\n")

    # --- Lọc: mọi quan hệ mà MỘT ĐẦU là văn bản của ta ---
    lien_quan = []
    for row in ds:
        s, d = str(row.get(c_src)), str(row.get(c_dst))
        if s in ten or d in ten:
            lien_quan.append({c_src: s, c_dst: d, c_rel: row.get(c_rel)})

    print("=" * 64)
    print(f"PHEP THU 1 - CO BAO NHIEU QUAN HE DINH TOI ALLOWLIST: {len(lien_quan):,}")
    print("=" * 64)

    kieu = Counter(r[c_rel] for r in lien_quan)
    print("\nCAC LOAI QUAN HE CO THAT (day la thu quan trong nhat):")
    for k, n in kieu.most_common():
        print(f"  {n:6,}  {k!r}")

    # --- Cái gì SỬA văn bản của ta? ---
    print("\n" + "=" * 64)
    print("PHEP THU 2 - VAN BAN NAO SUA/THAY THE VAN BAN CORE CUA TA")
    print("=" * 64)
    tac_dong = defaultdict(list)
    for r in lien_quan:
        d = r[c_dst]
        if d in ten:
            tac_dong[ten[d]].append((r[c_src], r[c_rel]))

    for so_hieu in sorted(ten.values()):
        ds_td = tac_dong.get(so_hieu, [])
        print(f"\n  {so_hieu}  ({len(ds_td)} quan he den)")
        for src, rel in ds_td[:8]:
            print(f"      <- id={src:8} {rel!r}")
        if len(ds_td) > 8:
            print(f"      ... con {len(ds_td)-8}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[c_src, c_dst, c_rel])
        w.writeheader()
        w.writerows(lien_quan)
    print(f"\nDa ghi: {OUT.relative_to(REPO)}  ({len(lien_quan):,} dong)")
    print("\nGui cho Claude: phan 'CAC LOAI QUAN HE CO THAT' va vai dong dau cua PHEP THU 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
