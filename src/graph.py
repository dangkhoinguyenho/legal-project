"""
Mô hình quan hệ giữa các văn bản — giải mã từ dữ liệu vbpl thật.

CHIỀU QUAN HỆ (giải được bằng cách soi các cặp đối xứng trong 574 quan hệ):
Mỗi dòng là (doc_id, other_doc_id, relationship), và `relationship` mô tả
`other_doc_id` LÀ GÌ, nhìn từ trang của `doc_id`. Kiểm bằng ca đã biết đáp án:

    (52/2014, 22/2000, 'Thay thế')                    -> 52/2014 thay thế 22/2000  ĐÚNG
    (22/2000, 52/2014, 'Văn bản quy định hết hiệu lực') -> 52/2014 giết 22/2000    ĐÚNG
    (81/2025, 52/2014, 'Sửa đổi, bổ sung')            -> 81/2025 sửa 52/2014       ĐÚNG

═══════════════════════════════════════════════════════════════════════════
BẪY LỚN NHẤT — quan hệ 'Hợp nhất' KHÔNG nói VBHN đó là văn bản gì
═══════════════════════════════════════════════════════════════════════════
Cạnh 'Hợp nhất' nối VBHN với văn bản gốc VÀ với TỪNG văn bản sửa đổi. Vì luật
Việt Nam hay ra luật tổng hợp sửa nhiều luật khác nhau, một VBHN nối tới cả
những luật chẳng liên quan gì tới nó.

Đọc ngây thơ sẽ dẫn tới các kết luận SAI sau, đã kiểm chứng:

    35/VBHN-VPQH   thật ra là Luật TỔ CHỨC CHÍNH QUYỀN ĐỊA PHƯƠNG
                   (đồ thị làm ta tưởng là Luật Đất đai)
    43/VBHN-VPQH   thật ra là Luật THỦY LỢI
                   (đồ thị làm ta tưởng là Luật Doanh nghiệp)
    105/VBHN-VPQH  thật ra là Luật TƯ PHÁP NGƯỜI CHƯA THÀNH NIÊN
                   (đồ thị làm ta tưởng là Bộ luật Tố tụng dân sự)

=> KHÔNG BAO GIỜ suy ra bản hợp nhất của một luật chỉ từ cạnh 'Hợp nhất'.
   Phải xác minh tên VBHN bằng nguồn ngoài. Hàm dưới đây CHẶN việc đó.

BẪY THỨ HAI: số hiệu VBHN ĐẶT LẠI MỖI NĂM. '109/VBHN-VPQH' năm 2025 là Luật
Tố tụng hành chính; năm 2026 là Luật Công chứng. Khóa phải là (số hiệu, ngày).
"""

from __future__ import annotations

# other_doc_id là KẺ TÁC ĐỘNG, doc_id là kẻ bị tác động
OTHER_TAC_DONG = {
    "Văn bản quy định hết hiệu lực": "thay_the",
    "Văn bản quy định hết hiệu lực 1 phần": "sua_mot_phan",
    "Văn bản sửa đổi": "sua_doi",
    "Văn bản bổ sung": "bo_sung",
    "Văn bản HD, QĐ chi tiết": "huong_dan",
}

# doc_id là KẺ TÁC ĐỘNG, other_doc_id là kẻ bị tác động
DOC_TAC_DONG = {
    "Thay thế": "thay_the",
    "Bãi bỏ": "bai_bo",
    "Sửa đổi, bổ sung": "sua_doi",
    "Văn bản được sửa đổi": "sua_doi",
    "Văn bản bị hết hiệu lực 1 phần": "sua_mot_phan",
    "Quy định chi tiết, hướng dẫn thi hành": "huong_dan",
}

# Không xác định được chiều bằng nhãn -> phải xác minh ngoài
KHONG_SUY_DUOC = {
    "Hợp nhất": "VBHN noi toi ca van ban goc LAN cac van ban sua doi. "
                "Khong suy ra duoc day la ban hop nhat cua luat nao.",
    "Dẫn chiếu": "Chi la tham chieu, khong doi hieu luc.",
    "Văn bản dẫn chiếu": "Chi la tham chieu, khong doi hieu luc.",
    "Hướng dẫn áp dụng": "Van ban hanh chinh, khong phai VBQPPL.",
    "Giải thích": "Khong doi hieu luc.",
    "Đình chỉ thi hành": "Hiem, phai xem tung ca.",
}

NHIEU = {"Căn cứ", "Văn bản căn cứ"}


class QuanHeKhongSuyDuoc(Exception):
    """Ném ra khi ai đó cố suy chiều từ một nhãn không cho phép suy."""


def phan_tich(doc_id: str, other_doc_id: str, relationship: str) -> dict | None:
    """Trả về {'tac_dong': ai, 'bi_tac_dong': ai, 'hanh_vi': gì} hoặc None nếu là nhiễu.

    Ném QuanHeKhongSuyDuoc với nhãn 'Hợp nhất' — cố tình, để không ai
    vô tình lặp lại lỗi 35/VBHN-VPQH.
    """
    if relationship in NHIEU:
        return None
    if relationship in KHONG_SUY_DUOC:
        raise QuanHeKhongSuyDuoc(f"{relationship!r}: {KHONG_SUY_DUOC[relationship]}")
    if relationship in OTHER_TAC_DONG:
        return {"tac_dong": other_doc_id, "bi_tac_dong": doc_id,
                "hanh_vi": OTHER_TAC_DONG[relationship], "nhan_goc": relationship}
    if relationship in DOC_TAC_DONG:
        return {"tac_dong": doc_id, "bi_tac_dong": other_doc_id,
                "hanh_vi": DOC_TAC_DONG[relationship], "nhan_goc": relationship}
    raise QuanHeKhongSuyDuoc(f"Nhan la: {relationship!r}. Chua co trong mo hinh.")


def ai_giet(doc_id: str, quan_he: list[dict]) -> list[dict]:
    """Những văn bản làm `doc_id` hết hiệu lực toàn bộ hoặc một phần."""
    ra = []
    for r in quan_he:
        try:
            kq = phan_tich(r["doc_id"], r["other_doc_id"], r["relationship"])
        except QuanHeKhongSuyDuoc:
            continue
        if kq and kq["bi_tac_dong"] == doc_id and kq["hanh_vi"] in {
                "thay_the", "bai_bo", "sua_mot_phan", "sua_doi"}:
            ra.append(kq)
    return ra
