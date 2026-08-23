"""
Bước 3c — tìm Luật Đất đai 2024 ở bộ dữ liệu KHÁC.

TÌNH HÌNH: bộ th1nhng0 có bản ghi cho 31/2024/QH15 nhưng content_html RỖNG
(318 byte, một cái bảng trống). Chỉ có 1 bản ghi, nên không phải lỗi trùng id.
Kho này THỰC SỰ không có toàn văn Luật Đất đai 2024.

Có vài bộ khác cùng cào từ vbpl.vn. Script thử từng bộ, tìm số hiệu, và đếm Điều.

Chạy:  python src/find_missing_doc.py
"""

import re
import sys

CAN_TIM = "31/2024/QH15"
KY_VONG = 260  # Luật Đất đai 2024 có 260 Điều

UNG_VIEN = [
    "vohuutridung/vietnamese-legal-documents",
    "minhdoan17/vietnamese-legal-documents",
    "doanhieung/vbpl",
    "tmquan/vbpl-vn",
    "Monmoonluna/vbpl-vn-legal-corpus",
]

RE_DIEU = re.compile(r"Điều\s+(\d+)\s*[.\-–]", re.IGNORECASE)


def bo_the(s):
    s = re.sub(r"<[^>]+>", " ", str(s or ""))
    return s.replace("&nbsp;", " ")


def chuan_hoa(s):
    return re.sub(r"[^A-Z0-9/\-]", "", str(s or "").upper())


def thu_mot_bo(ten):
    from datasets import get_dataset_config_names, load_dataset
    print(f"\n{'='*64}\n{ten}\n{'='*64}")
    try:
        cfgs = get_dataset_config_names(ten)
    except Exception as e:
        print(f"  KHONG MO DUOC: {type(e).__name__}: {str(e)[:120]}")
        return None
    print(f"  cac config: {cfgs}")

    for cfg in cfgs[:3]:
        try:
            d = load_dataset(ten, cfg, streaming=True)
            split = list(d.keys())[0]
            ds = d[split]
        except Exception as e:
            print(f"  [{cfg}] khong load duoc: {str(e)[:90]}")
            continue

        cols = None
        muc = chuan_hoa(CAN_TIM)
        found = None
        for i, row in enumerate(ds):
            if cols is None:
                cols = list(row.keys())
                print(f"  [{cfg}] split='{split}' cot={cols}")
            if i > 60000:
                break
            # tìm số hiệu ở BẤT KỲ cột chuỗi nào
            for v in row.values():
                if isinstance(v, str) and len(v) < 200 and chuan_hoa(v) == muc:
                    found = row
                    break
            if found:
                break
        if found:
            print(f"  >>> TIM THAY {CAN_TIM} sau {i:,} dong")
            for k, v in found.items():
                s = str(v)
                if len(s) > 400:
                    n = len(set(RE_DIEU.findall(bo_the(s))))
                    dat = "DUNG DUOC" if n >= KY_VONG * 0.9 else "van thieu"
                    print(f"      {k}: {len(s):,} ky tu, {n} Dieu  <-- {dat}")
                    if n >= KY_VONG * 0.9:
                        return (ten, cfg, k, s)
                else:
                    print(f"      {k}: {s[:70]!r}")
        else:
            print(f"  [{cfg}] khong thay {CAN_TIM} trong {i:,} dong da luot")
    return None


def main():
    try:
        import datasets  # noqa
    except ImportError:
        print("Chay:  pip install datasets")
        return 1

    print(f"Tim toan van {CAN_TIM} (ky vong {KY_VONG} Dieu)")
    for ten in UNG_VIEN:
        kq = thu_mot_bo(ten)
        if kq:
            bo, cfg, cot, html = kq
            from pathlib import Path
            out = Path(__file__).resolve().parent.parent / "data" / "raw" / "content" / "177815.html"
            out.write_text(html, encoding="utf-8")
            print(f"\n{'*'*64}")
            print(f"THANH CONG. Lay tu: {bo} / config={cfg} / cot={cot}")
            print(f"Da ghi de: {out.name}")
            print(f"Chay lai:  python src/check_corpus.py")
            print(f"{'*'*64}")
            return 0

    print(f"\n{'!'*64}")
    print("KHONG BO NAO CO TOAN VAN LUAT DAT DAI 2024.")
    print("Bao cho Claude - se chuyen sang phuong an khac.")
    print(f"{'!'*64}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
