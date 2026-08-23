"""
Bước 3a — kéo TOÀN VĂN của các văn bản trong allowlist.

VẤN ĐỀ VỀ KÍCH THƯỚC:
  metadata.parquet       ~15 MB
  relationships.parquet  ~9 MB
  content.parquet        ~3,9 GB    <-- phần nặng
Ta chỉ cần 22 văn bản trong số 178.665. Đọc tuần tự cả file để tìm 22 cái là
phí (~45 phút ở tốc độ 1,4 MB/s).

CÁCH NHANH (mặc định): dùng DuckDB đọc parquet qua HTTP với "row-group pruning"
— nó chỉ tải các khối chứa id ta cần, bỏ qua phần còn lại. Thường nhanh hơn
nhiều lần.

CÁCH DỰ PHÒNG: nếu DuckDB không chạy, tự động quay lại streaming tuần tự.

Peek (đã chạy, giữ lại để tra cứu):
    python src/pull_content.py --peek
Chạy thật:
    python src/pull_content.py
Ép dùng cách chậm:
    python src/pull_content.py --stream
"""

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
OUT_DIR = REPO / "data" / "raw" / "content"

DATASET = "th1nhng0/vietnamese-legal-documents"
PARQUET = ("https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents"
           "/resolve/main/data/content.parquet")

RE_DIEU = re.compile(r"Điều\s+(\d+)\s*[.\-–]", re.IGNORECASE)


def bo_the_html(s: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def doc_allowlist():
    if not MATCHED.exists():
        print(f"Chua co {MATCHED}. Chay src/pull_metadata.py truoc.")
        return None
    with MATCHED.open(encoding="utf-8") as f:
        return {r["id"]: r["so_ky_hieu"] for r in csv.DictReader(f)}


def luu(rid, html, so_hieu):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{rid}.html").write_text(html or "", encoding="utf-8")
    txt = bo_the_html(html or "")
    n_dieu = len(set(RE_DIEU.findall(txt)))
    print(f"  [LAY] {so_hieu:34} {len(html or ''):>9,} ky tu | {n_dieu:>3} Dieu")
    return n_dieu


def cach_nhanh(can_tim):
    try:
        import duckdb
    except ImportError:
        print("Chua co duckdb -> quay ve cach cham.")
        print("Muon nhanh hon, chay:  pip install duckdb\n")
        return None
    print("Dung DuckDB doc parquet qua HTTP (chi tai khoi chua id can) ...")
    ids = ",".join(f"'{i}'" for i in can_tim)
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    q = f"SELECT id, content_html FROM read_parquet('{PARQUET}') WHERE CAST(id AS VARCHAR) IN ({ids})"
    try:
        rows = con.execute(q).fetchall()
    except Exception as e:
        print(f"DuckDB loi: {type(e).__name__}: {e}\n-> quay ve cach cham.\n")
        return None
    ra = {}
    for rid, html in rows:
        rid = str(rid)
        ra[rid] = luu(rid, html, can_tim.get(rid, "?"))
    return ra


def cach_cham(can_tim):
    from datasets import load_dataset
    print("Doc tuan tu (streaming). Se lau, ~30-45 phut.\n")
    ds = load_dataset(DATASET, "content", split="data", streaming=True)
    ra = {}
    for i, row in enumerate(ds, 1):
        if i % 5000 == 0:
            print(f"  ... da luot {i:,} dong, tim thay {len(ra)}/{len(can_tim)}")
        rid = str(row.get("id"))
        if rid in can_tim and rid not in ra:
            ra[rid] = luu(rid, row.get("content_html"), can_tim[rid])
            if len(ra) == len(can_tim):
                print("\n  Da du. Dung som.")
                break
    return ra


def peek():
    from datasets import load_dataset
    ds = load_dataset(DATASET, "content", split="data", streaming=True)
    for row in ds:
        txt = bo_the_html(row["content_html"])
        print(f"id={row['id']}  dai {len(row['content_html']):,}")
        print(txt[:300])
        print(f">>> khop 'Dieu': {RE_DIEU.findall(txt)[:15]}")
        break


def main() -> int:
    if "--peek" in sys.argv:
        peek()
        return 0
    can_tim = doc_allowlist()
    if can_tim is None:
        return 1
    print(f"Can lay toan van {len(can_tim)} van ban\n")

    ra = None if "--stream" in sys.argv else cach_nhanh(can_tim)
    if ra is None:
        ra = cach_cham(can_tim)

    print(f"\n{'='*62}")
    print(f"KET QUA: lay duoc {len(ra)}/{len(can_tim)} van ban")
    thieu = [v for k, v in can_tim.items() if k not in ra]
    if thieu:
        print("KHONG CO TOAN VAN:")
        for x in thieu:
            print(f"  {x}")
    # Phép thử: văn bản lớn mà tách ra quá ít Điều là dấu hiệu HTML bẩn
    nghi_ngo = [(k, can_tim[k], v) for k, v in ra.items() if v < 3]
    if nghi_ngo:
        print("\nCANH BAO - tach duoc DUOI 3 Dieu, co the HTML bi loi:")
        for k, sh, n in nghi_ngo:
            print(f"  {sh:34} chi {n} Dieu")
    print(f"{'='*62}")
    print(f"Da luu: {OUT_DIR.relative_to(REPO)}")
    print("\nGui cho Claude toan bo phan in ra tu 'Can lay toan van' tro xuong.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
