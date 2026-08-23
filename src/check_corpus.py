"""
Bước 3b — kiểm tra toàn vẹn corpus, và vá chỗ hổng.

VÌ SAO CÓ FILE NÀY:
`pull_content.py` lấy được 22/22 văn bản, không lỗi, không cảnh báo gì.
Nhưng **Luật Đất đai 2024 (31/2024/QH15) chỉ có 318 byte** — một cái bảng HTML
RỖNG. Luật này có 260 Điều. Bản ghi tồn tại, có id, join đúng với metadata và
relationships — chỉ là KHÔNG CÓ NỘI DUNG.

Không có gì trong metadata hay bảng quan hệ lộ ra điều đó. Chỉ có đếm số Điều
mới bắt được.

NGUYÊN NHÂN CÓ THỂ LÀ LỖI CỦA TÔI: `pull_metadata.py` viết
    if key in muc_tieu and key not in tim_thay
tức là gặp số hiệu trùng thì LẤY CÁI ĐẦU TIÊN, bỏ qua các bản ghi sau — âm thầm.
Nếu kho có nhiều bản ghi cho cùng một số hiệu, ta có thể đã bốc trúng bản rỗng.

Script này:
  1. Đếm Điều cho từng file trong corpus, so với số Điều KỲ VỌNG viết tay
  2. Với văn bản hỏng, tìm MỌI bản ghi khác cùng số hiệu trong metadata
  3. Thử lấy toàn văn của các bản ghi thay thế đó

Chạy:  python src/check_corpus.py
"""

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MATCHED = REPO / "data" / "raw" / "metadata_matched.csv"
CONTENT = REPO / "data" / "raw" / "content"

DATASET = "th1nhng0/vietnamese-legal-documents"
PARQUET = ("https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents"
           "/resolve/main/data/content.parquet")

RE_DIEU = re.compile(r"Điều\s+(\d+)\s*[.\-–]", re.IGNORECASE)

# Số Điều kỳ vọng — tra tay từ nguồn ngoài. Đây là NEGATIVE CONTROL cho corpus:
# nếu parse ra lệch nhiều so với đây thì corpus hỏng, dù script không báo lỗi.
KY_VONG = {
    "52/2014/QH13": 133,
    "91/2015/QH13": 689,
    "92/2015/QH13": 517,
    "31/2024/QH15": 260,
    "27/2023/QH15": 198,
    "59/2020/QH14": 218,
    "46/2024/QH15": 76,
    "01/2016/TTLT-TANDTC-VKSNDTC-BTP": 9,
    "01/2024/NQ-HĐTP": 12,
}
NGUONG = 0.90  # parse được dưới 90% số Điều kỳ vọng -> coi là hỏng


def bo_the_html(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"[ \t]+", " ", s)


def dem_dieu(html):
    return len(set(RE_DIEU.findall(bo_the_html(html))))


def chuan_hoa(s):
    return re.sub(r"[^A-Z0-9/\-]", "", str(s or "").upper())


def main() -> int:
    if not MATCHED.exists():
        print("Chua co metadata_matched.csv")
        return 1
    with MATCHED.open(encoding="utf-8") as f:
        docs = list(csv.DictReader(f))

    print("=" * 66)
    print("KIEM TRA TOAN VEN CORPUS")
    print("=" * 66)
    hong = []
    for d in docs:
        p = CONTENT / f"{d['id']}.html"
        if not p.exists():
            print(f"  [THIEU FILE] {d['so_ky_hieu']}")
            hong.append(d)
            continue
        html = p.read_text(encoding="utf-8")
        n = dem_dieu(html)
        kv = KY_VONG.get(d["so_ky_hieu"])
        if kv:
            ty_le = n / kv
            dat = ty_le >= NGUONG
            dau = "OK " if dat else "HONG"
            print(f"  [{dau}] {d['so_ky_hieu']:34} {n:>4}/{kv:<4} Dieu ({ty_le*100:.0f}%)")
            if not dat:
                hong.append(d)
        else:
            dau = "OK " if n >= 3 else "HONG"
            print(f"  [{dau}] {d['so_ky_hieu']:34} {n:>4}      Dieu (khong co ky vong)")
            if n < 3:
                hong.append(d)

    if not hong:
        print("\nCorpus toan ven. Khong can va.")
        return 0

    print(f"\n{len(hong)} van ban hong. Di tim ban ghi thay the ...\n")

    try:
        from datasets import load_dataset
        import duckdb
    except ImportError:
        print("Can:  pip install datasets duckdb")
        return 1

    # Tìm MỌI bản ghi trong metadata có cùng số hiệu (không chỉ cái đầu)
    print("Dang doc metadata de tim ban ghi trung so hieu ...")
    tat_ca = load_dataset(DATASET, "metadata")
    ds = tat_ca["train" if "train" in tat_ca else list(tat_ca.keys())[0]]
    can = {chuan_hoa(d["so_ky_hieu"]): d for d in hong}
    ung_vien = {k: [] for k in can}
    for r in ds:
        k = chuan_hoa(r.get("so_ky_hieu"))
        if k in ung_vien:
            ung_vien[k].append((str(r["id"]), r.get("ngay_ban_hanh"), r.get("title", "")[:60]))

    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    for k, ds_uv in ung_vien.items():
        sh = can[k]["so_ky_hieu"]
        print(f"\n{sh}: tim thay {len(ds_uv)} ban ghi trong metadata")
        for rid, ngay, tit in ds_uv:
            print(f"   id={rid:>10}  {ngay}  {tit}")
        if len(ds_uv) <= 1:
            print("   -> Chi co 1 ban ghi. Kho THUC SU khong co toan van van ban nay.")
            continue
        ids = ",".join(f"'{i}'" for i, _, _ in ds_uv)
        q = (f"SELECT id, content_html FROM read_parquet('{PARQUET}') "
             f"WHERE CAST(id AS VARCHAR) IN ({ids})")
        for rid, html in con.execute(q).fetchall():
            n = dem_dieu(html or "")
            print(f"   id={rid}: {len(html or ''):>9,} ky tu, {n:>4} Dieu", end="")
            kv = KY_VONG.get(sh)
            if kv and n / kv >= NGUONG:
                (CONTENT / f"{can[k]['id']}.html").write_text(html, encoding="utf-8")
                print("   <== DUNG CAI NAY, da ghi de")
            else:
                print("   (van hong)")

    print("\nChay lai script nay de kiem tra sau khi va.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
