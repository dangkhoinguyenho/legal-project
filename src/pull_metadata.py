"""
Bước 2a — kéo phần metadata của bộ dữ liệu vbpl và tìm các văn bản trong allowlist.

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

# Tên cột có thể khác với trang mô tả -> script tự dò trong các tên có thể có.
COT_SO_HIEU = ["so_ky_hieu", "so_hieu", "number", "document_number"]
COT_NGAY_BH = ["ngay_ban_hanh", "issued_date", "date"]
COT_HIEU_LUC = ["tinh_trang_hieu_luc", "status", "trang_thai"]


def chuan_hoa(s) -> str:
    """Bỏ dấu cách, chuyển hoa, bỏ ký tự lạ — để so số hiệu cho khớp."""
    return re.sub(r"[^A-Z0-9/\-]", "", str(s or "").upper())


def tim_cot(co_san, ung_vien):
    """Trả về tên cột đầu tiên trong `ung_vien` mà thực sự có trong dữ liệu."""
    for c in ung_vien:
        if c in co_san:
            return c
    return None


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("THIEU THU VIEN. Chay:  pip install datasets pandas")
        return 1

    if not ALLOWLIST.exists():
        print(f"KHONG TIM THAY {ALLOWLIST}")
        return 1

    with ALLOWLIST.open(encoding="utf-8") as f:
        allow = [r for r in csv.DictReader(f) if r["so_hieu"].strip()]
    muc_tieu = {chuan_hoa(r["so_hieu"]): r for r in allow}
    print(f"Allowlist: {len(muc_tieu)} van ban co so hieu\n")

    # --- Tải. KHÔNG lấy config 'content' — cái đó mới là vài GB. ---
    print(f"Dang tai metadata tu {DATASET} ...")
    try:
        tat_ca = load_dataset(DATASET, "metadata")
    except Exception as e:
        print(f"TAI THAT BAI: {type(e).__name__}: {e}")
        print("\nBao lai loi nay cho Claude, dung tu sua.")
        return 1

    # Không đoán tên split nữa — dò.
    ten_split = "train" if "train" in tat_ca else list(tat_ca.keys())[0]
    ds = tat_ca[ten_split]
    cols = list(ds.column_names)

    print(f"Tai xong: {len(ds):,} dong  (split='{ten_split}')")
    print(f"Cac cot co that trong du lieu:\n  {cols}\n")

    c_so = tim_cot(cols, COT_SO_HIEU)
    c_ngay = tim_cot(cols, COT_NGAY_BH)
    c_hl = tim_cot(cols, COT_HIEU_LUC)

    if not c_so:
        print(f"KHONG TIM THAY COT SO HIEU. Da thu: {COT_SO_HIEU}")
        print("Gui danh sach cot o tren cho Claude.")
        return 1
    print(f"Dung cot so hieu   : {c_so}")
    print(f"Dung cot ngay bh   : {c_ngay or '(khong co)'}")
    print(f"Dung cot hieu luc  : {c_hl or '(khong co)'}\n")

    # --- PHÉP THỬ 1: dữ liệu mới tới đâu? ---
    if c_ngay:
        ngay = sorted(d for d in ds[c_ngay] if d)
        if ngay:
            print("=" * 62)
            print("PHEP THU 1 - DO MOI CUA DU LIEU")
            print(f"  Cu nhat : {ngay[0]}")
            print(f"  Moi nhat: {ngay[-1]}")
            print("  -> Neu moi nhat < 2025-07 thi snapshot DA CU.")
            print("=" * 62 + "\n")

    # --- PHÉP THỬ 2: tìm được bao nhiêu văn bản? ---
    tim_thay = {}
    for row in ds:
        k = chuan_hoa(row.get(c_so))
        if k in muc_tieu and k not in tim_thay:
            tim_thay[k] = row

    print("=" * 62)
    print("PHEP THU 2 - TIM CAC VAN BAN TRONG ALLOWLIST")
    print("=" * 62)
    thieu = []
    for k, r in muc_tieu.items():
        hit = tim_thay.get(k)
        if hit:
            tt = (hit.get(c_hl) if c_hl else None) or "(trong)"
            print(f"  [CO ] {r['so_hieu']:38} | {tt}")
        else:
            print(f"  [MAT] {r['so_hieu']:38} | {r['ten_van_ban'][:38]}")
            thieu.append(r)
    print(f"\n  Tim thay {len(tim_thay)}/{len(muc_tieu)}")

    # --- Ghi kết quả ---
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if tim_thay:
        fieldnames = cols
        with OUT_MATCHED.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            for row in tim_thay.values():
                w.writerow({k: row.get(k) for k in fieldnames})
        print(f"\n  Da ghi: {OUT_MATCHED.relative_to(REPO)}")

    print("\n" + "=" * 62)
    if thieu:
        print(f"KET QUA: THIEU {len(thieu)} VAN BAN.")
        print("Gui phan [MAT] o tren cho Claude.")
    else:
        print("KET QUA: DU HET. Bo du lieu dung duoc.")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
