"""
Effectiveness check — deterministic, no model involved.

WHY THIS WAS REWRITTEN
======================
Version 1 asked one question: "is this document in force today?" and BLOCKED
anything that was not. The eval set proved that wrong on its first real case.

Bản án 111/2024/HNGĐ-ST, decided 30/8/2024, cites in its Căn cứ block:

    "Các Điều 95, 97, 98 Luật hôn nhân và gia đình năm 2000;
     ... Khoản 2, khoản 3 Điều 170 Luật đất đai năm 2013."

Both statutes are long replaced. The court was still right: the property was
formed while they were in force. Điều 58 khoản 2 Luật Ban hành VBQPPL requires
applying the document in force AT THE TIME OF THE EVENT.

Án lệ 03/2016/AL goes further — it cites Luật HNGĐ 1986 and Bộ luật Dân sự 1995,
both dead before the án lệ was even published, and it remains in effect today.

So "hết hiệu lực" is NOT an error. The real error is the opposite: citing a
document that did not yet exist when the facts happened.

THE CORE IDEA: a fact pattern has SEVERAL time anchors, not one.

    2005 ────── 2015 ────── 2023 ────── 2024
    married     bought      divorced    judgment
                land
       |          |            |
       +- LHNGĐ 2000 ----------+- LHNGĐ 2014

"Is this asset chung or riêng" is judged by the law at acquisition.
"How is it divided" is judged by the law at divorce. Both are correct, at once.

So this module labels rather than blocks, and every label is tied to a named
anchor — never to "today".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

# ---- Verdicts ----
CON_HIEU_LUC = "CON_HIEU_LUC"              # in force at the anchor
LUAT_CU_HOP_LE = "LUAT_CU_HOP_LE"          # dead now, alive then -> LEGITIMATE
MOT_PHAN = "HET_HIEU_LUC_MOT_PHAN"         # partially dead, needs article check
CHUA_RA_DOI = "CHUA_RA_DOI"                # not yet in force then -> REAL ERROR
DA_CHET_TRUOC_MOC = "DA_CHET_TRUOC_MOC"    # already dead then -> REAL ERROR
THIEU_DU_LIEU = "THIEU_DU_LIEU"
MAU_THUAN = "MAU_THUAN_DU_LIEU"
NGAY_VO_LY = "NGAY_VO_LY"

# Only these block a citation. Note what is NOT here: LUAT_CU_HOP_LE.
CHAN = {CHUA_RA_DOI, DA_CHET_TRUOC_MOC, THIEU_DU_LIEU, MAU_THUAN, NGAY_VO_LY}

# Format-valid is not the same as plausible. The corpus contains a document
# dated 13/03/3024, which parses cleanly and is nonsense.
NAM_SOM_NHAT, NAM_MUON_NHAT = 1945, 2100


@dataclass
class Moc:
    """A named point in time that a citation is ABOUT."""
    ten: str      # e.g. "tài sản hình thành", "ly hôn", "xét xử"
    ngay: date


@dataclass
class KetQua:
    ma: str
    so_hieu: str
    moc: str
    thong_diep: str

    @property
    def bi_chan(self) -> bool:
        return self.ma in CHAN

    @property
    def can_kiem_tay(self) -> bool:
        return self.ma == MOT_PHAN

    def __str__(self) -> str:
        return f"[{self.ma}] {self.so_hieu} @ {self.moc}: {self.thong_diep}"


def doc_ngay(s) -> date | None:
    """vbpl uses DD/MM/YYYY. Returns None on empty or malformed input."""
    s = str(s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def ngay_hop_ly(d: date | None) -> bool:
    return d is None or NAM_SOM_NHAT <= d.year <= NAM_MUON_NHAT


def kiem_tra(doc: dict, moc: Moc, ngay_het_suy_ra: date | None = None) -> KetQua:
    """Check one document against ONE time anchor.

    `ngay_het_suy_ra` lets the caller supply an expiry date derived from the
    relationship graph. This matters: `ngay_het_hieu_luc` is empty in all 22
    documents we pulled, so the graph is often the only way to know WHEN a
    document died. Example: 22/2000/QH10 was ended by 52/2014/QH13, whose
    ngay_co_hieu_luc is 01/01/2015 -> that is when LHNGĐ 2000 died.
    """
    so_hieu = (doc.get("so_ky_hieu") or "?").strip()
    trang_thai = (doc.get("tinh_trang_hieu_luc") or "").strip()
    hl_tu = doc_ngay(doc.get("ngay_co_hieu_luc"))
    het = doc_ngay(doc.get("ngay_het_hieu_luc")) or ngay_het_suy_ra

    def kq(ma, msg):
        return KetQua(ma, so_hieu, moc.ten, msg)

    # --- Gate 0: implausible dates ---
    for ten, d in (("ngay_co_hieu_luc", hl_tu), ("ngay_het_hieu_luc", het)):
        if not ngay_hop_ly(d):
            return kq(NGAY_VO_LY, f"{ten}={d} parses but year is outside "
                                  f"[{NAM_SOM_NHAT},{NAM_MUON_NHAT}]. Data is broken.")
    if not ngay_hop_ly(moc.ngay):
        return kq(NGAY_VO_LY, f"anchor date {moc.ngay} is implausible.")

    if hl_tu is None:
        return kq(THIEU_DU_LIEU, "no ngay_co_hieu_luc — cannot place it in time.")
    if not trang_thai:
        return kq(THIEU_DU_LIEU, "no tinh_trang_hieu_luc.")

    # --- Gate 1: did it exist yet? This is the REAL error. ---
    if moc.ngay < hl_tu:
        return kq(CHUA_RA_DOI,
                  f"in force from {hl_tu:%d/%m/%Y}, which is AFTER "
                  f"{moc.ten} ({moc.ngay:%d/%m/%Y}). Cannot govern these facts.")

    # --- Gate 2: had it already died by then? Also an error. ---
    if het is not None and moc.ngay >= het:
        return kq(DA_CHET_TRUOC_MOC,
                  f"expired {het:%d/%m/%Y}, before {moc.ten} ({moc.ngay:%d/%m/%Y}).")

    # It was alive at the anchor. Now describe its status TODAY.
    co_mot_phan = "một phần" in trang_thai.lower()
    chet_bay_gio = trang_thai.lower().startswith("hết hiệu lực") and not co_mot_phan

    # Cross-check: two independent signals must agree.
    if het is not None and not chet_bay_gio and not co_mot_phan:
        return kq(MAU_THUAN,
                  f"expiry date {het:%d/%m/%Y} but status is {trang_thai!r}. "
                  "Signals disagree — not guessing.")

    if chet_bay_gio:
        return kq(LUAT_CU_HOP_LE,
                  f"no longer in force today, but WAS in force at {moc.ten} "
                  f"({moc.ngay:%d/%m/%Y}). Citing it is correct — Điều 58 khoản 2.")
    if co_mot_phan:
        return kq(MOT_PHAN,
                  "partially expired. The data does not say which articles — "
                  "check the cited article against article_status.csv.")
    return kq(CON_HIEU_LUC, f"in force at {moc.ten} ({moc.ngay:%d/%m/%Y}).")


def kiem_tra_nhieu_moc(doc: dict, mocs: list[Moc],
                       ngay_het_suy_ra: date | None = None) -> list[KetQua]:
    """A property case spans several anchors. Check the document against each."""
    return [kiem_tra(doc, m, ngay_het_suy_ra) for m in mocs]
