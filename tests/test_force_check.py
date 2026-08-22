"""
Test cho force_check.

11/14 test ở ReefCommand là negative control — test chứng minh check THẬT SỰ
bắt được thứ nó nói là bắt được. Ở đây cũng vậy: phần lớn test dưới đây kiểm
rằng check ĐỔ đúng lúc, không phải rằng nó chạy trơn tru.

Chạy:  python -m pytest tests/ -v
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from force_check import (  # noqa: E402
    CHUA_CO_HIEU_LUC, HET_HIEU_LUC, MAU_THUAN, MOT_PHAN, NGAY_VO_LY, OK,
    THIEU_DU_LIEU, kiem_tra,
)

# Dữ liệu thật lấy từ data/raw/metadata_matched.csv
LUAT_HNGD = {
    "so_ky_hieu": "52/2014/QH13",
    "ngay_co_hieu_luc": "01/01/2015",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Còn hiệu lực",
}
ND126 = {  # core, nhưng "một phần"
    "so_ky_hieu": "126/2014/NĐ-CP",
    "ngay_co_hieu_luc": "15/02/2015",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Hết hiệu lực một phần",
}
LUAT_THADS_2025 = {  # hiệu lực 01/07/2026
    "so_ky_hieu": "106/2025/QH15",
    "ngay_co_hieu_luc": "01/07/2026",
    "ngay_het_hieu_luc": "",
    "tinh_trang_hieu_luc": "Còn hiệu lực",
}


# ---------- POSITIVE ----------

def test_van_ban_con_hieu_luc_thi_qua():
    kq = kiem_tra(LUAT_HNGD, date(2024, 6, 1))
    assert kq.ma == OK and not kq.bi_chan


# ---------- NEGATIVE CONTROLS ----------

def test_bat_duoc_van_ban_da_bi_thay_the():
    """Luật HNGĐ 2000 đã bị Luật 2014 thay. Trích nó = sai luật."""
    cu = {
        "so_ky_hieu": "22/2000/QH10",
        "ngay_co_hieu_luc": "01/01/2001",
        "ngay_het_hieu_luc": "01/01/2015",
        "tinh_trang_hieu_luc": "Hết hiệu lực",
    }
    assert kiem_tra(cu, date(2024, 6, 1)).ma == HET_HIEU_LUC


def test_bat_duoc_luat_chua_ra_doi_tai_thoi_diem_su_viec():
    """Điều 58 khoản 2: áp dụng văn bản có hiệu lực TẠI THỜI ĐIỂM sự việc.
    Vụ ly hôn 2019 không được trích Luật Công chứng 2024."""
    lcc = {
        "so_ky_hieu": "46/2024/QH15",
        "ngay_co_hieu_luc": "01/07/2025",
        "ngay_het_hieu_luc": "",
        "tinh_trang_hieu_luc": "Còn hiệu lực",
    }
    assert kiem_tra(lcc, date(2019, 3, 1)).ma == CHUA_CO_HIEU_LUC


def test_van_ban_moi_van_bi_chan_neu_su_viec_xay_ra_truoc():
    """Luật THADS 2025 có hiệu lực 01/07/2026. Sự việc 01/2026 -> chưa áp dụng."""
    assert kiem_tra(LUAT_THADS_2025, date(2026, 1, 15)).ma == CHUA_CO_HIEU_LUC


def test_het_hieu_luc_mot_phan_khong_duoc_coi_la_an_toan():
    """9/22 văn bản là 'một phần'. Dữ liệu KHÔNG nói điều nào chết.
    Check phải nói ra, không được im lặng cho qua."""
    kq = kiem_tra(ND126, date(2024, 6, 1))
    assert kq.ma == MOT_PHAN
    assert kq.can_kiem_tay


def test_thieu_ngay_hieu_luc_thi_bi_chan_chu_khong_doan():
    thieu = {
        "so_ky_hieu": "X/2020/NĐ-CP",
        "ngay_co_hieu_luc": "",
        "ngay_het_hieu_luc": "",
        "tinh_trang_hieu_luc": "Còn hiệu lực",
    }
    kq = kiem_tra(thieu, date(2024, 6, 1))
    assert kq.ma == THIEU_DU_LIEU and kq.bi_chan


def test_ngay_va_trang_thai_mau_thuan_thi_do_to():
    """Ngày nói đã chết, chuỗi nói còn sống -> dữ liệu hỏng. Không được chọn bừa một bên."""
    xau = {
        "so_ky_hieu": "Y/2018/NĐ-CP",
        "ngay_co_hieu_luc": "01/01/2019",
        "ngay_het_hieu_luc": "01/01/2020",
        "tinh_trang_hieu_luc": "Còn hiệu lực",
    }
    kq = kiem_tra(xau, date(2024, 6, 1))
    assert kq.ma == MAU_THUAN and kq.bi_chan


def test_ngay_sai_dinh_dang_khong_bi_hieu_nham():
    """vbpl dùng DD/MM/YYYY. Nếu gặp YYYY-MM-DD thì phải báo thiếu, không được đoán."""
    sai = {
        "so_ky_hieu": "Z/2020/NĐ-CP",
        "ngay_co_hieu_luc": "2020-09-01",
        "ngay_het_hieu_luc": "",
        "tinh_trang_hieu_luc": "Còn hiệu lực",
    }
    assert kiem_tra(sai, date(2024, 6, 1)).ma == THIEU_DU_LIEU


def test_bat_duoc_ngay_dung_dinh_dang_nhung_vo_ly():
    """Trong kho vbpl CO THAT mot van ban de ngay 13/03/3024.
    Kiem dinh dang cho qua vi no dung dinh dang. Phai kiem ca muc hop ly."""
    rac = {
        "so_ky_hieu": "R/3024/NĐ-CP",
        "ngay_co_hieu_luc": "13/03/3024",
        "ngay_het_hieu_luc": "",
        "tinh_trang_hieu_luc": "Còn hiệu lực",
    }
    kq = kiem_tra(rac, date(2024, 6, 1))
    assert kq.ma == NGAY_VO_LY and kq.bi_chan


def test_ngay_su_viec_vo_ly_cung_bi_chan():
    assert kiem_tra(LUAT_HNGD, date(3024, 1, 1)).ma == NGAY_VO_LY
