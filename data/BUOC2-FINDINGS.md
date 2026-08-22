# Kết quả task lớn — allowlist v4, bản có thẩm quyền, hiệu lực mức điều khoản

**22/08/2026.** Tài liệu này thay thế phần "Độ mới của snapshot" trong
`DATASET-FINDINGS.md`, vốn dựa trên một phép tính sai.

---

## 0. Hai lỗi của tôi, sửa trước

**Lỗi 1 — sắp xếp chuỗi thay vì sắp xếp ngày.** `sorted()` trên `'DD/MM/YYYY'`
cho `'31/12/2025' > '19/05/2026'` vì `'3' > '1'`. Tôi kết luận *"bộ dữ liệu thiếu
8 tháng"*. **Sai.** Số thật: kho phủ tới khoảng **tháng 5–6/2026** (4.601 văn bản
năm 2026). Cũ khoảng 2–3 tháng.

**Lỗi 2 — kiểm định dạng nhưng không kiểm mức hợp lý.** Script báo
`Ngay SAI DINH DANG: 0` trong khi kho có văn bản đề ngày **13/03/3024**. Nó đúng
định dạng nên lọt qua. Đã thêm chặn khoảng năm `[1945, 2100]` vào `force_check`,
kèm test dùng chính ca 3024 này.

---

## 1. 🔴 Bẫy suýt phá hỏng dự án: quan hệ `Hợp nhất` KHÔNG nói VBHN là văn bản gì

Cạnh `Hợp nhất` nối một VBHN với **văn bản gốc VÀ từng văn bản sửa đổi**. Vì luật
Việt Nam hay ra luật tổng hợp sửa nhiều luật không liên quan, một VBHN nối tới cả
những luật chẳng dính dáng gì tới nó.

Nếu đọc ngây thơ như tôi định làm, corpus sẽ chứa những thứ này:

| Đồ thị làm ta tưởng | Sự thật |
|---|---|
| `35/VBHN-VPQH` = bản hợp nhất **Luật Đất đai** | Là **Luật Tổ chức chính quyền địa phương** |
| `43/VBHN-VPQH` = bản hợp nhất **Luật Doanh nghiệp** | Là **Luật Thủy lợi** |
| `105/VBHN-VPQH` = bản hợp nhất **Bộ luật TTDS** | Là **Luật Tư pháp người chưa thành niên** |

Ba lần sai, đều là **sai im lặng** — corpus vẫn chạy, vẫn trả kết quả, chỉ là trả
Luật Thủy lợi cho câu hỏi chia tài sản.

**Bẫy phụ: số hiệu VBHN đặt lại mỗi năm.** `109/VBHN-VPQH` năm 2025 là Luật Tố
tụng hành chính; năm 2026 là Luật Công chứng. **Khóa phải là (số hiệu, ngày).**

→ `src/graph.py` **ném exception** khi ai đó cố suy chiều từ nhãn `Hợp nhất`.
Không cảnh báo, không đoán — chặn. Có test.

---

## 2. 🟢 Hiệu lực mức điều khoản — làm được, đúng như Kenny nói

`data/article_status.csv`, 12 dòng đầu tiên. Ví dụ quan trọng nhất:

> **Nghị định 126/2014 — Điều 19 đến Điều 50 ĐÃ CHẾT từ 01/01/2016**, bị bãi bỏ
> bởi **Điều 45 khoản 2 Nghị định 123/2015/NĐ-CP**. Cùng lúc, **điểm a khoản 1
> Điều 63** cũng chết, và **khoản 2 Điều 63** bị sửa.
>
> Khối chết là **Chương III — quan hệ HNGĐ có yếu tố nước ngoài**, tức phần hộ
> tịch. **Phần chế độ tài sản vợ chồng nằm ở Chương II, trước Điều 19, còn
> nguyên vẹn.**

Trước đây tôi viết *"hết hiệu lực một phần, dữ liệu không nói điều nào, phải kiểm
tay"*. Bây giờ hệ thống nói được **chính xác điều nào**. Đây là thứ không chatbot
luật nào trên thị trường làm.

Và nó xác nhận: **Nghị định 123/2015 phải nằm trong allowlist** — không phải vì
nội dung hộ tịch, mà vì nó là văn bản giết một phần văn bản core.

---

## 3. 🟢 Tin tốt lớn nhất: Điều 33–64 Luật HNGĐ CHƯA HỀ BỊ SỬA

Luật HNGĐ 2014 chỉ bị sửa **đúng một lần trong lịch sử**, bởi **Luật 81/2025/QH15**,
và nội dung sửa là **một cụm từ ở khoản 3 Điều 123**:

> Thay *"Tòa án nhân dân cấp huyện"* bằng *"Tòa án nhân dân khu vực"*.

Xác nhận chéo bằng **VBHN 121/VBHN-VPQH (27/08/2025)**, chỉ hợp nhất với đúng
Luật 81/2025.

**Toàn bộ phần chia tài sản — Điều 33 đến 64 — đứng nguyên từ 2014.** Lõi của dự
án là phần ổn định nhất trong cả hệ thống pháp luật quanh nó.

---

## 4. Bản có thẩm quyền cho từng văn bản

⚠️ **Pháp lệnh 01/2026/UBTVQH16, hiệu lực 01/07/2026**, vừa đổi địa vị của VBHN:

| | Điều 4 Pháp lệnh hợp nhất |
|---|---|
| Cũ (2012) | VBHN dùng chính thức trong việc **áp dụng và thi hành** |
| Mới (từ 01/07/2026) | VBHN dùng làm **căn cứ chính thức trong VIỆN DẪN và áp dụng** |

Trước 01/7/2026 **không** viện dẫn VBHN an toàn được; từ 01/7/2026 thì được. Hôm
nay 22/08/2026 → **được viện dẫn**. Nhưng định dạng trích dẫn vẫn phải nêu tên
luật gốc kèm *"(hợp nhất tại VBHN số …)"* → corpus phải giữ **cả hai định danh**.

**Quy tắc sai số:** nếu VBHN khác văn bản gốc do lỗi kỹ thuật thì **văn bản gốc
thắng**. Nên VBHN có thẩm quyền để viện dẫn, nhưng **không phải chân lý cuối cùng
về câu chữ**. Corpus phải giữ cả hai.

| Luật gốc | Bản phải dùng | Ngày |
|---|---|---|
| Luật HNGĐ 2014 | **VBHN 121/VBHN-VPQH** | 27/08/2025 |
| Bộ luật Dân sự 2015 | **bản gốc — chưa hề bị sửa, không có VBHN** | 24/11/2015 |
| Bộ luật TTDS 2015 | **VBHN 21/VBHN-VPQH** | 12/02/2026 |
| Luật Đất đai 2024 | **VBHN 44/VBHN-VPQH** | 16/03/2026 |
| Luật Nhà ở 2023 | **VBHN 79/VBHN-VPQH** | 26/03/2026 |
| Luật Doanh nghiệp 2020 | **VBHN 67/VBHN-VPQH** | 15/08/2025 |
| Luật Công chứng 2024 | **VBHN 109/VBHN-VPQH** | 19/05/2026 |
| TTLT 01/2016 | **bản gốc — chưa hề bị sửa** | 06/01/2016 |

⚠️ **Kho VBHN được biết là chưa đầy đủ.** Pháp lệnh 01/2026 đặt hạn **30/09/2026**
để hợp nhất nốt tồn đọng. Nên **không có VBHN không chứng minh được là luật chưa
bị sửa.**

---

## 5. Ba nhãn SAI trong đồ thị vbpl

| Đồ thị nói | Sự thật |
|---|---|
| `07/2026/TTLT-VKSNDTC-TANDTC` **sửa BLTTDS 2015** | **Không thể.** Thông tư liên tịch không có thẩm quyền sửa bộ luật do Quốc hội ban hành. Nó là văn bản phối hợp thi hành. Nhãn sai → **loại** |
| `90/2025/QH15` là **luật nhà ở** | Là **luật tổng hợp về đấu thầu, đầu tư, hải quan, thuế**. Chỉ bãi bỏ đúng *điểm b khoản 3 Điều 33* Luật Nhà ở → **loại** |
| `147/2025` và `130/2025` là **luật sửa Đất đai** | `147/2025` là **Luật Địa chất khoáng sản**; `130/2025` là **Luật Hàng không dân dụng**. Cả hai đều **không đụng** Điều 27 hay Điều 135 → **loại** |

Bài học: **nhãn quan hệ trong đồ thị là gợi ý, không phải sự thật.** Mỗi cạnh
quan trọng phải xác minh bằng nguồn ngoài trước khi đưa vào corpus.

---

## 6. Thay đổi trong allowlist: 24 → 27 văn bản

**Thêm** — `81/2025` (bằng chứng Đ33–64 còn nguyên), `76/2025` (sửa Luật DN),
`04/2026/QH16` (sửa Luật Công chứng, **hiệu lực 01/01/2027, chưa áp dụng**),
`123/2015` (giết Đ19–50 của NĐ 126/2014), `109/2026` (giết NĐ 82/2020).

**Loại** — `07/2026/TTLT`, `90/2025`, `147/2025`, `130/2025` (xem mục 5).

**Đổi trạng thái** — `82/2020/NĐ-CP` **đã hết hiệu lực 18/05/2026**. Giữ lại làm
negative control: hệ thống phải **chặn** nó, và đó là ca kiểm thử thật thay vì
ca bịa.

**Nhóm mới `scope=metadata`** (7 văn bản): không được trích cho câu hỏi chia tài
sản, nhưng bắt buộc có để biết văn bản khác còn sống tới đâu.

Hai điều quan trọng cho Điều 64 LHNGĐ (chia tài sản đưa vào kinh doanh):
**Luật Doanh nghiệp Điều 53** (xử lý phần vốn góp **khi ly hôn**) và **Điều 127**
(chuyển nhượng cổ phần) — **cả hai đều chưa bị sửa** bởi Luật 76/2025.

---

## 7. Chưa xác minh được

1. Danh sách **đầy đủ** các điều mà Luật 04/2026/QH16 sửa (chắc chắn có Đ3, 19, 44, 66).
2. Ngày hiệu lực của 04/2026/QH16: nguồn chính thức ghi **01/01/2027**, một nguồn
   thứ cấp ghi 01/7/2027.
3. Danh sách văn bản được hợp nhất bên trong **109/VBHN-VPQH (19/05/2026)** — Công
   báo trả về lược đồ rỗng, các trang thương mại chưa index.
4. **Nghị quyết 326/2016** (án phí) — vẫn chỉ có nguồn thứ cấp.
5. `44/VBHN-VPQH` và `67/VBHN-VPQH` có còn là bản mới nhất tính tới 22/08/2026 không.
