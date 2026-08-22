"""Test mô hình quan hệ. Phần lớn là negative control."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest  # noqa: E402
from graph import QuanHeKhongSuyDuoc, ai_giet, phan_tich  # noqa: E402


# ---------- POSITIVE: ca đã biết đáp án ----------

def test_luat_hngd_2014_thay_the_ban_2000():
    kq = phan_tich("52/2014/QH13", "22/2000/QH10", "Thay thế")
    assert kq["tac_dong"] == "52/2014/QH13"
    assert kq["bi_tac_dong"] == "22/2000/QH10"


def test_chieu_nguoc_lai_cho_cung_mot_su_that():
    """vbpl ghi cùng một sự thật ở cả hai trang, với hai nhãn khác nhau."""
    kq = phan_tich("22/2000/QH10", "52/2014/QH13", "Văn bản quy định hết hiệu lực")
    assert kq["tac_dong"] == "52/2014/QH13"
    assert kq["bi_tac_dong"] == "22/2000/QH10"


def test_luat_81_2025_sua_luat_hngd():
    kq = phan_tich("81/2025/QH15", "52/2014/QH13", "Sửa đổi, bổ sung")
    assert kq["tac_dong"] == "81/2025/QH15"
    assert kq["hanh_vi"] == "sua_doi"


# ---------- NEGATIVE CONTROLS ----------

def test_hop_nhat_bi_chan_chu_khong_doan_bua():
    """BẪY THẬT: 35/VBHN-VPQH là Luật Tổ chức chính quyền địa phương,
    KHÔNG phải Luật Đất đai — dù đồ thị nối nó với Luật Đất đai.
    Code phải TỪ CHỐI suy, không được đoán."""
    with pytest.raises(QuanHeKhongSuyDuoc):
        phan_tich("31/2024/QH15", "35/VBHN-VPQH", "Hợp nhất")


def test_nhan_la_thi_bao_loi_chu_khong_im_lang():
    with pytest.raises(QuanHeKhongSuyDuoc):
        phan_tich("A", "B", "Một nhãn chưa từng thấy")


def test_can_cu_bi_coi_la_nhieu():
    assert phan_tich("A", "B", "Căn cứ") is None


def test_dan_chieu_khong_doi_hieu_luc():
    with pytest.raises(QuanHeKhongSuyDuoc):
        phan_tich("A", "B", "Dẫn chiếu")


def test_ai_giet_bo_qua_hop_nhat_thay_vi_do_vo():
    """ai_giet() gặp 'Hợp nhất' thì bỏ qua, không được crash cả mẻ."""
    qh = [
        {"doc_id": "123/2015/NĐ-CP", "other_doc_id": "126/2014/NĐ-CP",
         "relationship": "Sửa đổi, bổ sung"},
        {"doc_id": "126/2014/NĐ-CP", "other_doc_id": "X/VBHN", "relationship": "Hợp nhất"},
        {"doc_id": "999", "other_doc_id": "126/2014/NĐ-CP", "relationship": "Căn cứ"},
    ]
    ra = ai_giet("126/2014/NĐ-CP", qh)
    assert len(ra) == 1
    assert ra[0]["tac_dong"] == "123/2015/NĐ-CP"
