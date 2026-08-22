# Allowlist — CHỐT v1

**15 văn bản.** File máy đọc: `allowlist.csv`. Đây là output của **Bước 1**.

**Quy tắc bất di bất dịch:** hệ thống **không bao giờ** được trích dẫn văn bản không có
trong file này. Model được **chọn** trong danh sách, không được **thêm** vào danh sách.
Đây là danh mục cách chữa san hô của ReefCommand, áp cho luật.

| scope | Số lượng | Nghĩa |
|---|---|---|
| `core` | 4 | Trực tiếp về chia tài sản. Được trích dẫn |
| `related` | 6 | Luật khác, cần khi tài sản là nhà đất / vốn góp / khi ra tòa. Được trích dẫn |
| `control` | 5 | Nằm trong kho nhưng **phải KHÔNG bao giờ** xuất hiện trong câu trả lời về chia tài sản. Nếu xuất hiện → retrieval hỏng → test đỏ |

Tập **án lệ** (~5–10 cái, lọc từ 90 án lệ có hiệu lực từ 1/7/2026) nằm ở file riêng
`anle.csv`, làm ở Bước 2 — cấu trúc dữ liệu khác hẳn văn bản quy phạm.

---

## Ba câu hỏi mở — đã tự tra và trả lời

### 1. Nhóm `related` có thiếu luật nào không? → **Có. Luật Doanh nghiệp.**

**Điều 64 Luật HNGĐ 2014** quy định riêng về *chia tài sản chung của vợ chồng đưa vào kinh
doanh*. Nếu tài sản chung là **phần vốn góp hoặc cổ phần**, không thể trả lời chỉ bằng
Luật HNGĐ — phải đụng tới Luật Doanh nghiệp (chuyển nhượng phần vốn góp, quyền ưu tiên mua
của thành viên khác, điều lệ công ty).

Đây cũng là một nguồn *bất cập* đã được công bố: Tạp chí Luật sư Việt Nam có bài phân tích
riêng về vướng mắc khi chia **cổ phiếu** lúc ly hôn theo Luật HNGĐ 2014. Ứng viên tốt cho
eval set ở Bước 4.

→ **Thêm Luật Doanh nghiệp 2020 (59/2020/QH14) vào `related`.**

*Đã cân nhắc và loại:* Luật Bảo hiểm xã hội (lương hưu). Điều 59–64 không có quy định
riêng về lương hưu, và đưa vào là mở rộng phạm vi không có căn cứ điều luật. Nếu eval set
sau này gặp vụ án thật về lương hưu thì thêm — thêm vì có bằng chứng, không vì phòng xa.

### 2. Nhóm `control` có cái nào thực ra liên quan không? → **Không.**

Đã xem lại cả 5. Bốn cái là mang thai hộ / sàng lọc trước sinh / chi phí y tế — quan hệ
nhân thân và y tế, không phải quan hệ tài sản. Cái thứ năm (NĐ 82/2020) là xử phạt hành
chính — khác hẳn loại quan hệ pháp luật.

Cả 5 ở lại trong kho **đúng vì chúng không liên quan**. Đó là công dụng của chúng.

### 3. Công văn 253/TANDTC-PC → **`related`, không phải `core`.**

Hai lý do:

- **Nội dung:** nó về thẩm quyền và thủ tục khi có yếu tố người Việt Nam ở nước ngoài,
  không phải về nguyên tắc chia tài sản.
- **Giá trị pháp lý:** Công văn **không phải văn bản quy phạm pháp luật**. Nó là văn bản
  hướng dẫn nghiệp vụ nội bộ ngành Tòa án. Thấp hơn nghị định và thông tư.

Trong hệ thống nó phải mang **nhãn provenance riêng**, giống hệt cách án lệ phải mang nhãn
"tham khảo, không ràng buộc tuyệt đối". Ba mức giá trị pháp lý khác nhau, ba nhãn khác
nhau — không được trộn.

---

## Bốn văn bản cần bản hợp nhất, không phải bản gốc

Không phải là nghi ngờ nguồn — là sự thật về văn bản: bản gốc đã bị sửa, đọc bản gốc là
đọc luật cũ.

| Văn bản | Tình trạng |
|---|---|
| Bộ luật Tố tụng dân sự 2015 | **Đã xác nhận** có sửa đổi bổ sung 2025 |
| Luật Đất đai 2024 | Chưa tra — đợt cải cách 2025 nhiều khả năng có đụng |
| Luật Nhà ở 2023 | Chưa tra — như trên |
| Luật Doanh nghiệp 2020 | Chưa tra — đã biết có sửa đổi 2022 |

**`force_check.py` (Bước 3) sẽ tự trả lời cả bốn.** Nó đọc `tinh_trang_hieu_luc`,
`ngay_co_hieu_luc`, `ngay_het_hieu_luc` từ bộ dữ liệu vbpl và đối chiếu với file này. Sai
lệch → test đỏ. Không ai phải kiểm tay.

---

## Negative control bắt buộc cho Bước 3

Hai cái, và cả hai phải **thật sự đỏ** trước khi tin `force_check.py`:

1. Thêm **Luật Hôn nhân và Gia đình 2000** (đã bị Luật 2014 thay thế) vào allowlist
   → build **phải đỏ** với lý do "hết hiệu lực".
2. Thêm một số hiệu **bịa** (ví dụ `999/2099/NĐ-CP`) vào allowlist
   → build **phải đỏ** với lý do "không tìm thấy trong kho".

Một check chưa từng bắt được gì thì không chứng minh được gì.

---

## Nguồn

- [Danh sách văn bản hướng dẫn Luật HNGĐ 2014, cập nhật 27/11/2025 (LuatVietnam)](https://luatvietnam.vn/hon-nhan/danh-sach-van-ban-huong-dan-luat-hon-nhan-gia-dinh-2014-cap-nhat-27-11-2025-605-105563-article.html)
- [Chia tài sản chung của vợ chồng là cổ phiếu khi ly hôn — bất cập và kiến nghị (Tạp chí Luật sư Việt Nam)](https://lsvn.vn/chia-tai-san-chung-cua-vo-chong-la-co-phieu-khi-ly-hon-theo-luat-hon-nhan-va-gia-dinh-2014-mot-so-van-de-bat-cap-va-kien-nghi-hoan-thien-1718378883-a144530.html)
- [Chia tài sản chung của vợ chồng đưa vào kinh doanh — Điều 64 (Thư viện Pháp luật)](https://thuvienphapluat.vn/phap-luat/quy-dinh-ve-dua-tai-san-chung-cua-vo-chong-vao-kinh-doanh-nhu-the-nao-khi-ly-hon-thi-viec-chia-tai--583333-39591.html)
- [Nguyên tắc chia tài sản chung của vợ chồng khi ly hôn (Tạp chí Tòa án nhân dân)](https://tapchitoaan.vn/bai-viet/phap-luat/nguyen-tac-chia-tai-san-chung-cua-vo-chong-khi-ly-hon)
