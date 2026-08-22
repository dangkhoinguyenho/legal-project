# Kết quả chạy thử bộ dữ liệu vbpl — 22/08/2026

Chạy `src/pull_metadata.py`. **22/23 văn bản tìm thấy.** Nhưng bốn phát hiện dưới đây
quan trọng hơn con số đó, và hai trong số chúng đã phá thiết kế ban đầu.

---

## 1. Văn bản duy nhất không tìm thấy là văn bản ĐÚNG RA phải không tìm thấy

`[MAT] 253/TANDTC-PC` — Công văn.

Nghiên cứu về thứ bậc pháp lý kết luận: **công văn không phải văn bản quy phạm pháp
luật**, nên nó không có trong cơ sở dữ liệu VBQPPL của vbpl.vn.

Dự đoán từ lý thuyết → dữ liệu độc lập xác nhận. Đây là bằng chứng phần nghiên cứu
thứ bậc là đúng, chứ không phải suy diễn.

Hệ quả: `CV253-2018` phải nằm ngoài quy trình kiểm hiệu lực tự động. Nó có nhánh riêng.

---

## 2. ⚠️ `ngay_het_hieu_luc` TRỐNG ở cả 22/22 văn bản

Thiết kế cũ của tôi định dùng trường này làm nguồn chính để biết văn bản còn sống không.
**Trường đó không có dữ liệu.** Không phải "đôi khi trống" — trống hết.

→ `force_check` phải dựa vào `tinh_trang_hieu_luc` (chuỗi tiếng Việt) và
`ngay_co_hieu_luc`, không dựa vào trường này.

---

## 3. ⚠️ Có BA trạng thái, không phải hai — và 9/22 là trạng thái thứ ba

| Trạng thái | Số văn bản |
|---|---|
| Còn hiệu lực | 13 |
| **Hết hiệu lực một phần** | **9** |
| Hết hiệu lực | 0 |

"Hết hiệu lực một phần" nghĩa là **một số điều đã chết, một số còn sống**. Mà dữ liệu
**không nói điều nào**. Trạng thái ở mức văn bản; hiệu lực thật ở mức điều khoản.

Và nó không phải chuyện hiếm gặp — nó dính vào văn bản `core`:

- **Nghị định 126/2014/NĐ-CP** (core) → một phần
- **Bộ luật Tố tụng dân sự 2015** (core) → một phần
- **Luật Nhà ở 2023**, **Luật Doanh nghiệp 2020**, **Nghị định 101/2024**,
  **Nghị định 104/2025**, **Luật 43/2024**, **Luật 85/2025**, **Nghị định 82/2020**

→ `force_check` phải có kết luận thứ ba: `HET_HIEU_LUC_MOT_PHAN` = *"không kết luận
được ở mức văn bản, phải kiểm tay điều khoản được trích"*. Không được coi là an toàn,
cũng không được coi là hỏng.

Đây là **giới hạn thật của dự án** và phải viết vào DISCLAIMER.md.

---

## 4. ⚠️ `linh_vuc` không dùng để lọc được — DATA-BUILD-PLAN sai chỗ này

Kế hoạch gốc viết: *"Filter to the chosen branch using the legal-sector metadata field."*

Dữ liệu thật:

| Văn bản | `linh_vuc` | `nganh` |
|---|---|---|
| **Bộ luật Tố tụng dân sự 2015** | `Chưa phân loại` | *(trống)* |
| **Pháp lệnh 05/2024/UBTVQH15** | `Chưa phân loại` | *(trống)* |
| Nghị định 207/2025 (mang thai hộ) | `Chưa phân loại` | `Y tế` |
| TTLT 01/2016 | `Dân sự - Kinh tế` | `Kiểm sát, Tòa án, Tư pháp` |

Lọc theo `linh_vuc` sẽ **bỏ sót Bộ luật Tố tụng dân sự** — một văn bản core. Và bỏ sót
im lặng: không báo lỗi, chỉ là thiếu.

Quyết định dùng **allowlist viết tay** thay vì lọc theo metadata giờ được dữ liệu chứng
minh là đúng. Không phải vì cẩn thận thừa — vì cách kia hỏng thật.

---

## 5. Độ mới của snapshot

`ngay_ban_hanh` mới nhất trong toàn bộ 171.556 dòng: **31/12/2025**. Hôm nay 22/08/2026.

→ **Thiếu khoảng 8 tháng văn bản.** Không văn bản 2026 nào có trong bộ dữ liệu.

Chưa ảnh hưởng allowlist hiện tại (văn bản mới nhất là 106/2025/QH15). Nhưng:

- 8 án lệ mới áp dụng từ 01/7/2026 sẽ **không** có ở đây (án lệ cũng không phải VBQPPL)
- Nghị định 49/2026/NĐ-CP (sửa Nghị định 101/2024) sẽ **không** có
- Trạng thái hiệu lực phản ánh thời điểm crawl, không phải hôm nay

⚠️ Một điểm chưa rõ: **106/2025/QH15 có `ngay_co_hieu_luc = 01/07/2026` nhưng trạng thái
đã là "Còn hiệu lực".** Nghĩa là "Còn hiệu lực" có thể mang nghĩa *"chưa bị bãi bỏ"* chứ
không phải *"đang áp dụng hôm nay"*. Chưa xác minh được.

→ Vì vậy `force_check` **không tin một tín hiệu nào cả**. Nó tính từ ngày, đối chiếu với
chuỗi trạng thái, và nếu hai bên mâu thuẫn thì **báo lỗi to** thay vì chọn bừa một bên.

---

## Tóm tắt: dùng được, nhưng không như kế hoạch ban đầu

| | Kế hoạch cũ | Sự thật |
|---|---|---|
| Kích thước | "4 GB, cân nhắc streaming" | **15 MB** cho metadata |
| Số dòng | 153.420 (theo trang mô tả) | **171.556** |
| Lọc theo `linh_vuc` | cách chính | **hỏng** — bỏ sót BLTTDS |
| `ngay_het_hieu_luc` | nguồn chính để check | **trống 22/22** |
| Trạng thái hiệu lực | 2 giá trị | **3** — 9/22 là "một phần" |
| Độ mới | chưa biết | tới **31/12/2025**, thiếu 8 tháng |
