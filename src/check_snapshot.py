"""
Sửa lỗi: đo ĐÚNG độ mới của bộ dữ liệu.

LỖI CŨ trong pull_metadata.py: nó gọi sorted() trên chuỗi 'DD/MM/YYYY'.
Sắp xếp chuỗi thì '31/12/2025' > '19/05/2026' vì '3' > '1'. Nên nó báo
"mới nhất = 31/12/2025" và tôi kết luận "bộ dữ liệu thiếu 8 tháng".
KẾT LUẬN ĐÓ SAI. Bảng quan hệ có văn bản tháng 5/2026 tra ngược được.

Đây đúng là loại lỗi cả dự án sinh ra để chống: một phép tính sai âm thầm,
không báo lỗi, đẻ ra một câu khẳng định nghe rất chắc chắn.

Chạy:  python src/check_snapshot.py
"""

import sys
from collections import Counter
from datetime import datetime


def doc_ngay(s):
    try:
        return datetime.strptime(str(s).strip(), "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("Chay:  pip install datasets")
        return 1

    print("Dang tai metadata ...")
    tat_ca = load_dataset("th1nhng0/vietnamese-legal-documents", "metadata")
    ds = tat_ca["train" if "train" in tat_ca else list(tat_ca.keys())[0]]

    raw = ds["ngay_ban_hanh"]
    ngay, hong = [], 0
    for s in raw:
        d = doc_ngay(s)
        if d:
            ngay.append(d)
        elif s:
            hong += 1

    print(f"\nTong dong           : {len(raw):,}")
    print(f"Ngay doc duoc       : {len(ngay):,}")
    print(f"Ngay SAI DINH DANG  : {hong:,}   <- neu > 0, phai xem la gi")
    print(f"Ngay TRONG          : {len(raw)-len(ngay)-hong:,}")

    if not ngay:
        print("Khong doc duoc ngay nao. Bao cho Claude.")
        return 1

    ngay.sort()
    print("\n" + "=" * 58)
    print("DO MOI THAT SU CUA BO DU LIEU")
    print(f"  Cu nhat : {ngay[0]:%d/%m/%Y}")
    print(f"  Moi nhat: {ngay[-1]:%d/%m/%Y}   <-- con so that")
    print("=" * 58)

    theo_nam = Counter(d.year for d in ngay)
    print("\nSo van ban theo nam (10 nam gan nhat):")
    for nam in sorted(theo_nam)[-10:]:
        print(f"  {nam}: {theo_nam[nam]:>7,}")

    nam_moi = max(theo_nam)
    if theo_nam.get(nam_moi, 0) < 500:
        print(f"\nLUU Y: nam {nam_moi} chi co {theo_nam[nam_moi]:,} van ban.")
        print("Co the la nam do chua crawl xong, khong phai nam do it van ban.")
        print("=> Van ban 2026 CO trong kho nhung co the CHUA DAY DU.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
