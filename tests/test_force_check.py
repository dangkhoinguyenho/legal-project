"""
Tests for force_check.

Most of these are negative controls — tests that prove the check actually
catches what it claims to catch. The headline test is
`test_ban_an_that_vien_dan_luat_2000_khong_bi_chan`: it is taken verbatim from
a real judgment, and version 1 of this module FAILED it.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from force_check import (  # noqa: E402
    CHUA_RA_DOI, CON_HIEU_LUC, DA_CHET_TRUOC_MOC, LUAT_CU_HOP_LE, MAU_THUAN,
    MOT_PHAN, NGAY_VO_LY, THIEU_DU_LIEU, Moc, kiem_tra, kiem_tra_nhieu_moc,
)

# Real rows from data/raw/metadata_matched.csv
LUAT_HNGD_2014 = {
    "so_ky_hieu": "52/2014/QH13",
    "ngay_co_hieu_luc": "01/01/2015",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Còn hiệu lực",
}
ND126 = {
    "so_ky_hieu": "126/2014/NĐ-CP",
    "ngay_co_hieu_luc": "15/02/2015",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Hết hiệu lực một phần",
}
LUAT_CONG_CHUNG_2024 = {
    "so_ky_hieu": "46/2024/QH15",
    "ngay_co_hieu_luc": "01/07/2025",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Còn hiệu lực",
}
# Not in our corpus. Expiry derived from the graph: 22/2000 was ended by
# 52/2014, whose ngay_co_hieu_luc is 01/01/2015.
LUAT_HNGD_2000 = {
    "so_ky_hieu": "22/2000/QH10",
    "ngay_co_hieu_luc": "01/01/2001",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Hết hiệu lực",
}
HET_HNGD_2000 = date(2015, 1, 1)

# Anchors taken from Bản án 111/2024/HNGĐ-ST
MOC_KET_HON = Moc("kết hôn", date(2005, 10, 11))
MOC_LY_HON = Moc("ly hôn", date(2023, 9, 13))
MOC_XET_XU = Moc("xét xử", date(2024, 8, 30))


# ---------------- THE TEST VERSION 1 FAILED ----------------

def test_ban_an_that_vien_dan_luat_2000_khong_bi_chan():
    """Bản án 111/2024/HNGĐ-ST cites Điều 95, 97, 98 Luật HNGĐ 2000 for property
    formed in a marriage from 2005. Version 1 blocked this. It is correct law."""
    kq = kiem_tra(LUAT_HNGD_2000, MOC_KET_HON, ngay_het_suy_ra=HET_HNGD_2000)
    assert kq.ma == LUAT_CU_HOP_LE
    assert not kq.bi_chan, "a real court cited this correctly — must not be blocked"


def test_cung_van_ban_do_nhung_o_moc_ly_hon_thi_sai():
    """The same statute at the divorce anchor (2023) IS an error — it was dead
    by then. Same document, different anchor, opposite verdict."""
    kq = kiem_tra(LUAT_HNGD_2000, MOC_LY_HON, ngay_het_suy_ra=HET_HNGD_2000)
    assert kq.ma == DA_CHET_TRUOC_MOC and kq.bi_chan


# ---------------- NEGATIVE CONTROLS ----------------

def test_bat_duoc_luat_chua_ra_doi():
    """Citing Luật Công chứng 2024 for a 2019 event: the statute did not exist."""
    kq = kiem_tra(LUAT_CONG_CHUNG_2024, Moc("giao dịch", date(2019, 3, 1)))
    assert kq.ma == CHUA_RA_DOI and kq.bi_chan


def test_mot_phan_khong_duoc_coi_la_an_toan():
    kq = kiem_tra(ND126, MOC_LY_HON)
    assert kq.ma == MOT_PHAN and kq.can_kiem_tay


def test_thieu_ngay_thi_chan_chu_khong_doan():
    doc = dict(LUAT_HNGD_2014, ngay_co_hieu_luc="")
    assert kiem_tra(doc, MOC_LY_HON).ma == THIEU_DU_LIEU


def test_hai_tin_hieu_mau_thuan_thi_do_to():
    doc = {"so_ky_hieu": "X", "ngay_co_hieu_luc": "01/01/2019",
           "ngay_het_hieu_luc": "01/01/2030", "tinh_trang_hieu_luc": "Còn hiệu lực"}
    assert kiem_tra(doc, MOC_LY_HON).ma == MAU_THUAN


def test_nam_3024_bi_bat():
    """The corpus really contains a document dated 13/03/3024."""
    doc = dict(LUAT_HNGD_2014, ngay_co_hieu_luc="13/03/3024")
    assert kiem_tra(doc, MOC_LY_HON).ma == NGAY_VO_LY


def test_ngay_sai_dinh_dang_khong_bi_doan_bua():
    doc = dict(LUAT_HNGD_2014, ngay_co_hieu_luc="2015-01-01")
    assert kiem_tra(doc, MOC_LY_HON).ma == THIEU_DU_LIEU


# ---------------- POSITIVE ----------------

def test_luat_hien_hanh_o_moc_ly_hon():
    assert kiem_tra(LUAT_HNGD_2014, MOC_LY_HON).ma == CON_HIEU_LUC


def test_mot_van_ban_nhieu_moc_cho_ket_qua_khac_nhau():
    """The whole point: one statute, three anchors, three different verdicts."""
    ra = kiem_tra_nhieu_moc(LUAT_HNGD_2014, [MOC_KET_HON, MOC_LY_HON, MOC_XET_XU])
    assert [k.ma for k in ra] == [CHUA_RA_DOI, CON_HIEU_LUC, CON_HIEU_LUC]
