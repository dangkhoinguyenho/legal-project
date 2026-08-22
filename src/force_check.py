"""
Kiểm tra hiệu lực của văn bản — lớp kiểm tra tất định (không dùng model).

Đây là DATA-08 của dự án này: check phải ĐỔ TO khi sai, không được im lặng bỏ qua.

THIẾT KẾ DỰA TRÊN DỮ LIỆU THẬT, không dựa trên trang mô tả:

1. `ngay_het_hieu_luc` TRỐNG ở cả 22/22 văn bản đã lấy về -> KHÔNG dùng nó làm
   nguồn chính. Thiết kế cũ của tôi giả định trường này có dữ liệu. Sai.

2. `tinh_trang_hieu_luc` có ba giá trị, không phải hai:
   "Còn hiệu lực" / "Hết hiệu lực" / "Hết hiệu lực một phần"
   9/22 văn bản là "một phần" — kể cả Nghị định 126/2014 và BLTTDS 2015, đều là
   văn bản core. "Một phần" nghĩa là MỘT SỐ ĐIỀU đã chết, nhưng dữ liệu KHÔNG
   nói điều nào. Nên không được coi là an toàn, cũng không được coi là hỏng.

3. Điều 58 khoản 2 Luật BHVBQPPL: áp dụng văn bản có hiệu lực TẠI THỜI ĐIỂM
   XẢY RA SỰ VIỆC. Nên hàm này bắt buộc nhận `ngay_su_viec`, không mặc định hôm nay.

NGUYÊN TẮC: dùng HAI tín hiệu độc lập (ngày và chuỗi trạng thái). Nếu chúng
mâu thuẫn nhau -> báo lỗi to. Một tín hiệu im lặng sai thì nguy hiểm hơn hai
tín hiệu cãi nhau.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

# --- Kết luận có thể có ---
OK = "OK"                              # dùng được
CHUA_CO_HIEU_LUC = "CHUA_CO_HIEU_LUC"  # trích luật chưa ra đời tại thời điểm đó
HET_HIEU_LUC = "HET_HIEU_LUC"          # trích luật đã chết
MOT_PHAN = "HET_HIEU_LUC_MOT_PHAN"     # phải kiểm tay ở mức điều khoản
THIEU_DU_LIEU = "THIEU_DU_LIEU"        # không đủ dữ liệu để kết luận
MAU_THUAN = "MAU_THUAN_DU_LIEU"        # hai tín hiệu cãi nhau -> dữ liệu có vấn đề

CHAN = {CHUA_CO_HIEU_LUC, HET_HIEU_LUC, THIEU_DU_LIEU, MAU_THUAN}


@dataclass
class KetQua:
    ma: str
    so_hieu: str
    thong_diep: str

    @property
    def bi_chan(self) -> bool:
        """True = KHÔNG được phép trích dẫn văn bản này."""
        return self.ma in CHAN

    @property
    def can_kiem_tay(self) -> bool:
        return self.ma == MOT_PHAN


def doc_ngay(s: str | None) -> date | None:
    """Dữ liệu vbpl dùng DD/MM/YYYY. Trả None nếu trống hoặc sai định dạng."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except ValueError:
        return None


def kiem_tra(doc: dict, ngay_su_viec: date) -> KetQua:
    """doc = một dòng metadata từ vbpl. ngay_su_viec = ngày xảy ra sự việc."""
    so_hieu = (doc.get("so_ky_hieu") or "?").strip()
    trang_thai = (doc.get("tinh_trang_hieu_luc") or "").strip()
    hl_tu = doc_ngay(doc.get("ngay_co_hieu_luc"))
    het = doc_ngay(doc.get("ngay_het_hieu_luc"))

    # --- Tín hiệu 1: ngày ---
    if hl_tu is None:
        return KetQua(THIEU_DU_LIEU, so_hieu,
                      "Thiếu ngay_co_hieu_luc — không kết luận được. Kiểm tay trên vbpl.vn.")
    if ngay_su_viec < hl_tu:
        return KetQua(CHUA_CO_HIEU_LUC, so_hieu,
                      f"Có hiệu lực từ {hl_tu:%d/%m/%Y}, sau sự việc {ngay_su_viec:%d/%m/%Y}.")
    ngay_noi_chet = het is not None and ngay_su_viec >= het

    # --- Tín hiệu 2: chuỗi trạng thái ---
    if not trang_thai:
        return KetQua(THIEU_DU_LIEU, so_hieu, "Thiếu tinh_trang_hieu_luc.")
    co_mot_phan = "một phần" in trang_thai.lower()
    chuoi_noi_chet = trang_thai.lower().startswith("hết hiệu lực") and not co_mot_phan

    # --- Đối chiếu hai tín hiệu ---
    if ngay_noi_chet != chuoi_noi_chet and not co_mot_phan:
        return KetQua(MAU_THUAN, so_hieu,
                      f"Ngày và trạng thái mâu thuẫn: het={het}, trang_thai={trang_thai!r}. "
                      "Dữ liệu có vấn đề — không được đoán.")
    if chuoi_noi_chet or ngay_noi_chet:
        return KetQua(HET_HIEU_LUC, so_hieu, f"Đã hết hiệu lực ({trang_thai}).")
    if co_mot_phan:
        return KetQua(MOT_PHAN, so_hieu,
                      "Hết hiệu lực MỘT PHẦN. Dữ liệu không nói điều nào đã chết — "
                      "phải kiểm tay điều khoản được trích trên vbpl.vn.")
    return KetQua(OK, so_hieu, f"Còn hiệu lực tại {ngay_su_viec:%d/%m/%Y}.")


def kiem_tra_ca_bo(docs: list[dict], ngay_su_viec: date) -> list[KetQua]:
    return [kiem_tra(d, ngay_su_viec) for d in docs]
