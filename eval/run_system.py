"""
Run the 6 fact patterns through the pipeline and score against ground truth.

Ground truth = what the courts actually cited (eval/expected_citations.csv).
Scored two ways, because `bat_buoc` is our judgment, not the court's:
    FULL     — every expected citation
    ESSENTIAL— only bat_buoc = yes

FP06 is scored separately: it must return NOTHING.

Run:  python eval/run_system.py
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from force_check import Moc          # noqa: E402
from pipeline import chay            # noqa: E402

FP = REPO / "eval" / "fact_patterns.csv"
EC = REPO / "eval" / "expected_citations.csv"

# Map the human document names in expected_citations.csv to allowlist doc_keys.
TEN_SANG_KEY = {
    "Luật Hôn nhân và Gia đình 2014": "L52-2014",
    "Bộ luật Dân sự 2015": "BLDS-2015",
    "TTLT 01/2016/TTLT-TANDTC-VKSNDTC-BTP": "TTLT01-2016",
    "Nghị quyết 326/2016/UBTVQH14": "NQ326-2016",
    "Luật Đất đai 2024": "LDD-2024",
    "Luật Nhà ở 2023": "LNO-2023",
    "Luật Doanh nghiệp 2020": "LDN-2020",
    # Not in the corpus — superseded law and án lệ. Counted as misses, honestly.
    "Luật Hôn nhân và Gia đình 2000": None,
    "Luật Đất đai 2013": None,
    "Bộ luật Dân sự 2005": None,
    "Án lệ 82/2025/AL": None,
    "Luật Các tổ chức tín dụng": None,
}

# Anchors per pattern, read from the facts.
MOCS = {
    "FP01": [Moc("tài sản hình thành", date(2015, 6, 1)), Moc("ly hôn", date(2023, 9, 13))],
    "FP02": [Moc("tặng cho", date(2009, 6, 1)), Moc("ly hôn", date(2023, 3, 22))],
    "FP03": [Moc("phát sinh nợ", date(2016, 6, 1)), Moc("ly hôn", date(2024, 8, 20))],
    "FP04": [Moc("sống chung", date(2014, 1, 1)), Moc("ly hôn", date(2021, 1, 6))],
    "FP05": [Moc("chuyển nhượng", date(2013, 7, 9)), Moc("ly hôn", date(2022, 1, 13))],
    "FP06": [Moc("hiện tại", date(2026, 8, 27))],
}


def tach_dieu(s: str) -> list[int]:
    """'Điều 95, 97, 98' -> [95,97,98];  'khoản 2 Điều 170' -> [170]"""
    s = str(s or "")
    parts = re.split(r"Điều", s)
    out = []
    for p in parts[1:]:
        out += [int(x) for x in re.findall(r"\b(\d{1,3})\b", p.split("Bộ luật")[0])]
    if not out:
        out = [int(x) for x in re.findall(r"\b(\d{1,3})\b", s)]
    return sorted(set(out))


def main() -> int:
    with FP.open(encoding="utf-8") as f:
        patterns = list(csv.DictReader(f))
    with EC.open(encoding="utf-8") as f:
        expected = list(csv.DictReader(f))

    ky_vong = {}
    for r in expected:
        pid = r["pattern_id"]
        if not r["van_ban"]:
            ky_vong.setdefault(pid, [])
            continue
        key = TEN_SANG_KEY.get(r["van_ban"].strip(), "?")
        for d in tach_dieu(r["dieu"]):
            ky_vong.setdefault(pid, []).append(
                (f"{key}#D{d}" if key else None, r["van_ban"], d, r["bat_buoc"] == "yes"))

    tong = {"full_hit": 0, "full_all": 0, "ess_hit": 0, "ess_all": 0,
            "ngoai_corpus": 0, "control_ro": 0, "tra_ve": 0, "tra_ve_dung": 0}
    tai_k = {k: {"hit": 0, "all": 0} for k in (5, 8, 10, 20)}
    duyet = []   # rows for Kenny to review

    for p in patterns:
        pid = p["id"]
        kq, cd = chay(p["tinh_huong"], MOCS[pid], k=12)
        tra_ve = {c.ref for c in kq}
        xep = [c.ref for c in kq]            # ranked, best first
        ctrl = []

        print("=" * 74)
        print(f"{pid} — {p['nhom_van_de']}   (kỳ vọng: {p['ky_vong']})")
        print("=" * 74)

        if pid == "FP06":
            for c in kq:
                print(f"  RÒ RỈ: {c.so_hieu} Điều {c.dieu} — {c.tieu_de[:52]}")
                print(f"         nguồn: {c.nguon}")
            ok = len(kq) == 0
            print(f"  Trả về {len(kq)} điều. Đúng phải là 0.  -> {'ĐẠT' if ok else 'HỎNG'}")
            print(f"  (retrieval chặn {cd['control_ro']} control, {cd['ngoai_pham_vi']} ngoài phạm vi)")
            tong["control_ro"] += cd["control_ro"]
            continue

        for ref, ten, d, bb in ky_vong.get(pid, []):
            if ref is None:
                mark, note = "—", "ngoài corpus"
                tong["ngoai_corpus"] += 1
            else:
                hit = ref in tra_ve
                mark = "HIT " if hit else "MISS"
                note = ref
                tong["full_all"] += 1
                tong["full_hit"] += int(hit)
                if bb:
                    tong["ess_all"] += 1
                    tong["ess_hit"] += int(hit)
            sao = "*" if bb else " "
            print(f"  {mark}{sao} {ten[:38]:<38} Điều {d:<4} {note}")

        tong["control_ro"] += cd["control_ro"]
        # PRECISION: of what we returned, how much did the court actually cite?
        dung = {r for r, _t, _d, _b in ky_vong.get(pid, []) if r}
        # Dump the ranked list so Kenny can mark what is genuinely irrelevant.
        # Court "Căn cứ" blocks are NOT a list of every relevant article, so
        # counting "court did not cite it" as "wrong" measures the wrong thing.
        for i, c in enumerate(kq, 1):
            duyet.append({"pattern": pid, "thu_hang": i, "so_hieu": c.so_hieu,
                          "dieu": c.dieu, "tieu_de": c.tieu_de[:70],
                          "toa_co_vien_dan": "co" if c.ref in dung else "",
                          "nguon": c.nguon, "lien_quan_khong": ""})
        for K in tai_k:
            top = set(xep[:K])
            tai_k[K]["hit"] += len(top & dung)
            tai_k[K]["all"] += len(dung)
        trung = tra_ve & dung
        tong["tra_ve"] += len(tra_ve)
        tong["tra_ve_dung"] += len(trung)
        print(f"  (trả về {len(kq)} điều, {len(trung)} trong số đó tòa có viện dẫn)")
        print(f"   chặn {cd['control_ro']} control, {cd['ngoai_pham_vi']} ngoài phạm vi "
              f"| embed: {'có' if cd['co_embed'] else 'KHÔNG'}")

    print("\n" + "=" * 74)
    print("TỔNG KẾT   (* = bắt buộc)")
    print("=" * 74)
    fa, fh = tong["full_all"], tong["full_hit"]
    ea, eh = tong["ess_all"], tong["ess_hit"]
    print(f"  Recall FULL      : {fh}/{fa} = {fh/max(fa,1)*100:.0f}%")
    print(f"  Recall ESSENTIAL : {eh}/{ea} = {eh/max(ea,1)*100:.0f}%")
    print(f"  Ngoài corpus     : {tong['ngoai_corpus']} (luật cũ + án lệ, chưa có)")
    print(f"  Control bị chặn  : {tong['control_ro']} (chặn = tốt)")
    tv, tvd = tong["tra_ve"], tong["tra_ve_dung"]
    print(f"  Tổng trả về      : {tv} điều")
    print("\n  RECALL@k — chỉ tính k điều ĐẦU TIÊN của danh sách xếp hạng.")
    print("  Đây mới là so sánh công bằng: baseline trả ~8 trích dẫn mỗi ca.")
    for K in sorted(tai_k):
        h, a = tai_k[K]["hit"], tai_k[K]["all"]
        dau = "   <-- so sánh công bằng với baseline" if K == 8 else ""
        print(f"    recall@{K:<3}: {h}/{a} = {h/max(a,1)*100:.0f}%{dau}")
    print(f"\n  Baseline (AI thường, không corpus): recall ~55%, precision chưa đo")
    # Write the review file.
    out = REPO / "eval" / "de_duyet.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(duyet[0].keys()))
        w.writeheader(); w.writerows(duyet)
    print(f"\n  Đã ghi {out.name} ({len(duyet)} dòng) để Kenny duyệt.")
    print("  Mở bằng Excel. Cột 'lien_quan_khong': ghi 'x' vào những điều")
    print("  KHÔNG liên quan gì tới tình huống. Không cần nhớ luật — chỉ cần")
    print("  nhìn tên điều và thấy nó vô lý.")
    print("\n  ĐÃ BỎ chỉ số precision cũ: nó tính 'toà không viện dẫn' = 'sai',")
    print("  mà hai chuyện đó khác nhau. Điều 33 rõ ràng liên quan tới FP01")
    print("  nhưng không nằm trong phần Căn cứ — cách đo cũ tính nó là sai.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
