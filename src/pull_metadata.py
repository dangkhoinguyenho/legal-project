"""
Bước 2a — kéo phần metadata của bộ dữ liệu vbpl và tìm 24 văn bản trong allowlist.

MỤC ĐÍCH THẬT của script này KHÔNG phải là lấy dữ liệu.
Nó là PHÉP THỬ: bộ dữ liệu trên Hugging Face có đủ mới để dùng được không?

Nếu nó không tìm thấy Luật Công chứng 2024 hay Luật Thi hành án dân sự 2025
(hai văn bản rất mới), nghĩa là snapshot đã cũ -> toàn bộ kế hoạch Tier A phải đổi.
Thà biết bây giờ còn hơn biết sau khi đã viết 500 dòng code.

Chạy:  python src/pull_metadata.py
"""

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ALLOWLIST = REPO / "data" / "allowlist.csv"
OUT_DIR = REPO / "data" / "raw"
OUT_MATCHED = OUT_DIR / "metadata_matched.csv"

DATASET = "th1nhng0/vietnamese-legal-documents"


def chuan_hoa(s: str) -> str:
    """Bỏ dấu cách, chuyển hoa, bỏ ký tự lạ — để so số hiệu cho khớp.
    '01/2016/TTLT-TANDTC-VKSNDTC-BTP' và '01/2016/TTLT-TANDTC-VKSNDTC-BTP ' là một."""
    return re.sub(r"[^A-Z0-9/\-]", "", (s or "").upper())


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("THIEU THU VIEN. Chay lenh nay truoc:")
        print("    pip install datasets pandas")
        return 1

    # --- 1. Đọc allowlist ---
    if not ALLOWLIST.exists():
        print(f"KHONG TIM THAY {ALLOWLIST}")
        return 1

    with ALLOWLIST.open(encoding="utf-8") as f:
        allow = [r for r in csv.DictReader(f) if r["so_hieu"].strip()]

    muc_tieu = {chuan_hoa(r["so_hieu"]): r for r in allow}
    print(f"Allowlist: {len(muc_tieu)} van ban co so hieu\n")

    # --- 2. Tải metadata (KHÔNG tải content — content mới là 4GB) ---
    print(f"Dang tai metadata tu {DATASET} ... (vai phut, ~vai tram MB)")
    try:
        ds = load_dataset(DATASET, "metadata", split="train")
    except Exception as e:
        print(f"TAI THAT BAI: {type(e).__name__}: {e}")
        print("\nBao lai loi nay cho Claude, dung tu sua.")
        return 1

    print(f"Tai xong: {len(ds):,} dong\n")

    # --- 3. PHÉP THỬ SỐ 1: dữ liệu mới tới đâu? ---
    ngay = [d for d in ds["ngay_ban_hanh"] if d]
    if ngay:
        print("=" * 60)
        print("PHEP THU 1 - DO MOI CUA DU LIEU")
        print(f"  Ngay ban hanh cu nhat : {min(ngay)}")
        print(f"  Ngay ban hanh moi nhat: {max(ngay)}")
        print("  -> Neu moi nhat < 2025-07, snapshot DA CU. Bao cho Claude.")
        print("=" * 60 + "\n")

    # --- 4. PHÉP THỬ SỐ 2: tìm được bao nhiêu trong 24 văn bản? ---
    tim_thay: dict[str, dict] = {}
    for row in ds:
        key = chuan_hoa(row.get("so_ky_hieu", ""))
        if key in muc_tieu and key not in tim_thay:
            tim_thay[key] = row

    print("=" * 60)
    print("PHEP THU 2 - TIM 24 VAN BAN TRONG ALLOWLIST")
    print("=" * 60)

    thieu = []
    for key, r in muc_tieu.items():
        hit = tim_thay.get(key)
        if hit:
            print(f"  [CO ] {r['so_hieu']:38} | {hit.get('tinh_trang_hieu_luc') or '(trong)'}")
        else:
            print(f"  [MAT] {r['so_hieu']:38} | {r['ten_van_ban'][:40]}")
            thieu.append(r)

    print(f"\n  Tim thay {len(tim_thay)}/{len(muc_tieu)}")

    # --- 5. Ghi kết quả ---
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if tim_thay:
        cols = list(next(iter(tim_thay.values())).keys())
        with OUT_MATCHED.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for row in tim_thay.values():
                w.writerow(row)
        print(f"\n  Da ghi: {OUT_MATCHED.relative_to(REPO)}")

    # --- 6. Kết luận ---
    print("\n" + "=" * 60)
    if thieu:
        print(f"KET QUA: THIEU {len(thieu)} VAN BAN.")
        print("Chup man hinh phan [MAT] o tren gui cho Claude.")
        print("Neu thieu cac van ban 2024-2025 -> snapshot cu -> phai doi ke hoach.")
    else:
        print("KET QUA: DU CA 24. Bo du lieu dung duoc.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
