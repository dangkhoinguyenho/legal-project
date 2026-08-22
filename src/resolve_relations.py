"""
Bước 2c — dịch id thành số hiệu, lọc nhiễu, và tìm CHÍNH XÁC văn bản nào làm
văn bản của ta hết hiệu lực một phần.

Kết quả chạy pull_relations.py cho thấy bảng quan hệ CÓ đúng loại quan hệ ta cần:
    'Văn bản quy định hết hiệu lực 1 phần'   <- cái gì làm ta chết một phần
    'Văn bản bị hết hiệu lực 1 phần'
    'Sửa đổi, bổ sung' / 'Văn bản sửa đổi' / 'Văn bản được sửa đổi'
    'Bãi bỏ' / 'Thay thế' / 'Hợp nhất'

NHƯNG 6.596/7.183 (92%) là 'Căn cứ' — nghĩa là "văn bản kia lấy ta làm căn cứ".
Đó là nhiễu: mọi nghị định đều ghi căn cứ vào luật gốc. Phải lọc bỏ.

Script này cũng chạy MỘT PHÉP THỬ ÂM: có bao nhiêu id KHÔNG tra ngược được ra
số hiệu? Dữ liệu có hai kiểu id lẫn lộn (số '47412' và uuid 'fbaf8e60-...'),
nghĩa là bộ dữ liệu ghép từ hai lần crawl. Nếu id không tra được mà ta lặng lẽ
bỏ qua, đó là lỗi im lặng — đúng loại nguy hiểm nhất.

Chạy:  python src/resolve_relations.py
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
RELS = REPO / "data" / "raw" / "relations_matched.csv"
OUT = REPO / "data" / "raw" / "relations_resolved.csv"

DATASET = "th1nhng0/vietnamese-legal-documents"

BO_QUA = {"Căn cứ", "Văn bản căn cứ"}          # nhiễu: ai lấy ta làm căn cứ
QUAN_TRONG = {                                   # thứ thật sự đổi hiệu lực
    "Văn bản quy định hết hiệu lực 1 phần",
    "Văn bản bị hết hiệu lực 1 phần",
    "Văn bản quy định hết hiệu lực",
    "Văn bản hết hiệu lực",
    "Sửa đổi, bổ sung", "Văn bản sửa đổi", "Văn bản được sửa đổi",
    "Văn bản bổ sung", "Bãi bỏ", "Thay thế", "Hợp nhất",
}


def main() -> int:
    try:
        from datasets import load_dataset
    except ImportError:
        print("Chay:  pip install datasets")
        return 1
    for p in (MATCHED, RELS):
        if not p.exists():
            print(f"Chua co {p}. Chay pull_metadata.py va pull_relations.py truoc.")
            return 1

    with MATCHED.open(encoding="utf-8") as f:
        cua_ta = {r["id"]: r["so_ky_hieu"] for r in csv.DictReader(f)}
    with RELS.open(encoding="utf-8") as f:
        rels = list(csv.DictReader(f))
    print(f"{len(rels):,} quan he, {len(cua_ta)} van ban cua ta\n")

    # --- Bảng tra id -> số hiệu, từ TOÀN BỘ metadata ---
    print("Dang tai metadata de tra nguoc id ...")
    tat_ca = load_dataset(DATASET, "metadata")
    ds = tat_ca["train" if "train" in tat_ca else list(tat_ca.keys())[0]]
    tra = {}
    for r in ds:
        tra[str(r["id"])] = (r.get("so_ky_hieu") or "?", r.get("loai_van_ban") or "",
                             r.get("ngay_ban_hanh") or "", r.get("title") or "")
    print(f"Bang tra: {len(tra):,} van ban\n")

    # --- PHÉP THỬ ÂM: id nào không tra được? ---
    tat_id = {r["doc_id"] for r in rels} | {r["other_doc_id"] for r in rels}
    mat = {i for i in tat_id if i not in tra}
    uuid_mat = {i for i in mat if "-" in i}
    print("=" * 64)
    print("PHEP THU AM - ID KHONG TRA NGUOC DUOC")
    print(f"  Tong id       : {len(tat_id):,}")
    print(f"  Khong tra duoc: {len(mat):,}  ({len(mat)/max(len(tat_id),1)*100:.1f}%)")
    print(f"    trong do uuid: {len(uuid_mat):,}")
    if mat:
        print("  -> Quan he tro toi van ban KHONG co trong kho.")
        print("     KHONG duoc lang le bo qua. Phai danh dau 'khong tra duoc'.")
    print("=" * 64 + "\n")

    # --- Lọc nhiễu ---
    sach = [r for r in rels if r["relationship"] not in BO_QUA]
    print(f"Sau khi bo {BO_QUA}: {len(rels):,} -> {len(sach):,} quan he\n")

    # --- Cái gì làm văn bản của ta hết hiệu lực / bị sửa? ---
    tac_dong = defaultdict(list)
    for r in sach:
        if r["relationship"] not in QUAN_TRONG:
            continue
        s, d = r["doc_id"], r["other_doc_id"]
        if d in cua_ta:
            tac_dong[cua_ta[d]].append((s, r["relationship"], "den"))
        if s in cua_ta:
            tac_dong[cua_ta[s]].append((d, r["relationship"], "di"))

    print("=" * 64)
    print("VAN BAN NAO LAM VAN BAN CUA TA THAY DOI HIEU LUC")
    print("=" * 64)
    for so_hieu in sorted(set(cua_ta.values())):
        muc = tac_dong.get(so_hieu, [])
        if not muc:
            continue
        print(f"\n{so_hieu}")
        for oid, rel, huong in sorted(set(muc)):
            if oid in tra:
                sh, loai, ngay, _ = tra[oid]
                print(f"   {'<-' if huong=='den' else '->'} {rel:38} {sh:30} ({ngay})")
            else:
                print(f"   {'<-' if huong=='den' else '->'} {rel:38} [KHONG TRA DUOC id={oid}]")

    # --- Ghi ra ---
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["doc_id", "doc_so_hieu", "relationship",
                    "other_doc_id", "other_so_hieu", "other_ngay_ban_hanh", "tra_duoc"])
        for r in sach:
            s, d = r["doc_id"], r["other_doc_id"]
            ss = tra.get(s, ("", "", "", ""))
            dd = tra.get(d, ("", "", "", ""))
            w.writerow([s, ss[0], r["relationship"], d, dd[0], dd[2],
                        "yes" if (s in tra and d in tra) else "no"])
    print(f"\nDa ghi: {OUT.relative_to(REPO)}  ({len(sach):,} dong)")
    print("\nGui cho Claude: phan PHEP THU AM va phan VAN BAN NAO LAM ... THAY DOI HIEU LUC.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
