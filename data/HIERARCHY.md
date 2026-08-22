# Thứ bậc hiệu lực pháp lý và quy tắc xử lý xung đột

**Đây là phát hiện quan trọng nhất từ đợt nghiên cứu này. Nó thay đổi kiến trúc dự án.**

---

## 1. Luật nền đã đổi — và nó mới đổi năm ngoái

Quy tắc về thứ bậc văn bản và cách xử lý mâu thuẫn nằm ở **Luật Ban hành văn bản quy phạm
pháp luật**. Bản đang áp dụng:

| | Văn bản | Ngày | Hiệu lực |
|---|---|---|---|
| Luật gốc | **Luật số 64/2025/QH15** | 19/02/2025 | **01/4/2025** |
| Luật sửa đổi | **Luật số 87/2025/QH15** | 25/6/2025 | **01/7/2025** |
| Bản hợp nhất | **54/VBHN-VPQH (2025)** | — | bản phải trích dẫn |

**Luật cũ 80/2015/QH13 đã HẾT HIỆU LỰC** từ 01/4/2025 (Điều 71).

Nghĩa là: mọi tài liệu, bài viết, hay kiến thức nói về "Điều 156 Luật Ban hành VBQPPL"
đều đang nói về luật đã chết. Điều tương ứng bây giờ là **Điều 58**.

---

## 2. Thứ bậc — Điều 4 Luật 64/2025/QH15

15 khoản. Đây là thứ tự Kenny hỏi. Cột `rank` trong `allowlist.csv` chính là số này.

| rank | Loại văn bản |
|---|---|
| 1 | Hiến pháp |
| **2** | **Bộ luật, luật, nghị quyết của Quốc hội** |
| **3** | **Pháp lệnh, nghị quyết của UBTVQH**; nghị quyết liên tịch với UBTƯMTTQ |
| 4 | Lệnh, quyết định của Chủ tịch nước |
| **5** | **Nghị định, nghị quyết của Chính phủ** |
| 6 | Quyết định của Thủ tướng Chính phủ |
| **7** | **Nghị quyết của Hội đồng Thẩm phán TANDTC** |
| **8** | **Thông tư** của Chánh án TANDTC / Viện trưởng VKSNDTC / Bộ trưởng / Tổng KTNN |
| **9** | **Thông tư liên tịch** giữa các chức danh trên |
| 10–15 | Văn bản của chính quyền địa phương (tỉnh, xã) |

Ngoài hệ thống này (tôi đánh rank 98–99 để code phân biệt):

| rank | | Vì sao ngoài |
|---|---|---|
| 98 | **Án lệ** | Không có trong Điều 4, không thỏa định nghĩa VBQPPL ở Điều 2 |
| 99 | **Công văn** | Là văn bản hành chính. **Không được làm căn cứ pháp lý** |

---

## 3. Quy tắc xử lý xung đột — Điều 58

**Đây là chỗ thay đổi kiến trúc.** Nguyên văn các khoản quan trọng:

> **Khoản 2.** Văn bản QPPL được áp dụng đối với hành vi, sự kiện xảy ra **tại thời điểm
> mà văn bản đó đang có hiệu lực**.
>
> **Khoản 3.** Trường hợp các văn bản QPPL có quy định khác nhau về cùng một vấn đề thì
> **áp dụng văn bản có hiệu lực pháp lý cao hơn**.
>
> **Khoản 4.** Trường hợp các văn bản QPPL **do cùng một cơ quan ban hành** có quy định
> khác nhau về cùng một vấn đề thì áp dụng quy định của văn bản **ban hành sau**.

### Ý nghĩa với dự án: một phần lớn "conflict detection" là CODE, không phải model

Kenny từng định giao việc phát hiện mâu thuẫn cho model. Nhưng luật đã cho sẵn thuật toán:

```
def resolve(a, b):                       # a, b là hai điều khoản mâu thuẫn
    if not a.is_vbqppl or not b.is_vbqppl:
        return "NGOAI_HE_THONG"          # án lệ / công văn - xử lý riêng
    if a.rank != b.rank:
        return a if a.rank < b.rank else b        # Điều 58 khoản 3
    if a.co_quan_ban_hanh == b.co_quan_ban_hanh:
        return a if a.ngay_ban_hanh > b.ngay_ban_hanh else b   # khoản 4
    return "KHONG_CO_QUY_TAC"            # cùng cấp, khác cơ quan → luật không giải
```

Model chỉ còn phải làm **một việc**: *hai điều khoản này có thật sự nói khác nhau về
cùng một vấn đề không?* Việc "vậy áp dụng cái nào" là **số học**, không cần phán đoán.

Đúng tinh thần ReefCommand: cắt phần model được quyết xuống nhỏ nhất có thể.

### Ví dụ có thật, ngay trong allowlist

| | rank | Cơ quan |
|---|---|---|
| **Nghị quyết 01/2024/NQ-HĐTP** | **7** | Hội đồng Thẩm phán TANDTC |
| **TTLT 01/2016** | **9** | TANDTC + VKSNDTC + BTP |

TTLT 01/2016 Điều 7 là văn bản mang **nguyên tắc chia tài sản** — trái tim của dự án. Nó
lại là văn bản **thấp nhất** trong nhóm VBQPPL ở đây. Nếu nó mâu thuẫn với NQ 01/2024,
**NQ 01/2024 thắng** theo Điều 58 khoản 3.

Đây là ca kiểm thử đầu tiên nên viết cho `resolve()`.

### Ba cái bẫy — phải biết trước

**Bẫy 1: Khoản 4 hẹp hơn tưởng.** Nó chỉ áp dụng khi **cùng một cơ quan ban hành**. Hai
văn bản cùng cấp mà khác cơ quan thì **luật không cho quy tắc nào**. Code phải trả về
`KHONG_CO_QUY_TAC` và nói thật, không được đoán "cái mới hơn thắng".

**Bẫy 2: KHÔNG có quy tắc luật chuyên ngành thắng luật chung.** Điều 58 không có
*lex specialis*. Khoản 6 nói mọi ngoại lệ phải **do Quốc hội quy định** trong luật cụ thể.
Nên không được tự suy "Luật HNGĐ là luật chuyên ngành nên thắng Bộ luật Dân sự" — cả hai
đều rank 2, khác cơ quan? Không, cùng là Quốc hội → khoản 4 áp dụng → cái ban hành sau.
Nhưng phải kiểm từng ca, không suy diễn.

**Bẫy 3: Khoản 2 = check hiệu lực theo thời điểm.** Áp dụng văn bản có hiệu lực **tại
thời điểm xảy ra sự việc**, không phải hôm nay. Vụ chia tài sản năm 2016 phải dùng Luật
Công chứng 2014, không phải 2024. `force_check.py` phải nhận **ngày sự việc** làm tham số,
không được mặc định hôm nay.

---

## 4. Án lệ — tôi đã nói sai với Kenny, phải sửa

Tôi đã bảo án lệ là *"tham khảo, không ràng buộc tuyệt đối"*. IDEA-BRIEF cũng viết
*"persuasive guidance — not strictly binding"*.

**Nói vậy là quá nhẹ.** Nghị quyết 04/2019/NQ-HĐTP (sửa bởi NQ 02/2025/NQ-HĐTP, hợp nhất
tại **11/VBHN-TANDTC**), **Điều 8**:

> "Khi xét xử, Thẩm phán, Hội thẩm **phải** nghiên cứu, áp dụng án lệ, bảo đảm những vụ
> việc có tình huống pháp lý tương tự thì **phải** được giải quyết như nhau."

"Phải", không phải "nên". Cách mô tả đúng gồm ba ý, không được rút gọn thành một:

1. **Không phải VBQPPL** — không nằm trong thứ bậc Điều 4
2. **Bắt buộc nghiên cứu và áp dụng** khi tình huống pháp lý tương tự (Điều 8)
3. **Đương nhiên bị bãi bỏ** khi pháp luật thay đổi làm nó không còn phù hợp (Điều 9)

⚠️ Còn một điểm tôi **chưa xác minh**: thủ tục để thẩm phán *không* áp dụng án lệ (phải
nêu rõ lý do trong bản án?). Phải tra trước khi viết nhãn cuối cùng vào hệ thống.

Nhãn trong hệ thống phải nói đủ ba ý trên. Nếu chỉ ghi "tham khảo" là **sai luật**, và đó
đúng là loại sai mà cả dự án này sinh ra để tránh.

---

## 5. Bốn chỗ allowlist v1 của tôi đã lỗi thời

| Chỗ sai | Sự thật |
|---|---|
| "Luật HNGĐ 2014 chưa bị sửa" | **Đã sửa** bởi Luật 81/2025/QH15. Phải dùng **VBHN 121/VBHN-VPQH (2025)**. Đ38–42 và Đ59–64 nội dung không đổi, nhưng phải giữ bản hợp nhất |
| BLTTDS 2015 "cần bản hợp nhất" | Cụ thể là **Luật 85/2025/QH15**, hiệu lực 01/7/2025. **Bỏ tòa cấp huyện** — sơ thẩm nay là **Tòa án nhân dân khu vực**. Mọi câu trả lời về "kiện ở đâu" mà thiếu cái này là sai |
| Không có Luật Công chứng | **Luật Công chứng 2024 (46/2024/QH15)**, hiệu lực 01/7/2025, thay bản 2014. Đ38.2 LHNGĐ dẫn tới nó |
| Không có Luật THADS | **Luật THADS 2025 (106/2025/QH15)**, hiệu lực **01/7/2026** — mới đúng 2 tháng trước hôm nay |

---

## 6. Chưa xác minh được — ghi rõ để không ai tưởng là đã chắc

1. **Nghị quyết 326/2016/UBTVQH14 (án phí)** — chỉ xác nhận qua nguồn thứ cấp; vbpl.vn
   không truy cập được.
2. **Thủ tục thẩm phán không áp dụng án lệ** — chưa tra.
3. **Miễn thuế TNCN khi chuyển tài sản giữa vợ chồng** có còn trong Luật Thuế TNCN 2025
   (109/2025/QH15, hiệu lực 01/7/2026) hay không — chưa tra. Chỉ cần nếu hệ thống trả lời
   câu hỏi về thuế.
4. **Điều kiện tách thửa** khi chia đất bằng hiện vật — biết là có, chưa tra số điều.

Cả bốn đều sẽ bị `force_check.py` bắt nếu sai, trừ mục 2 và 3 (chúng là câu hỏi nội dung,
không phải hiệu lực) — hai cái đó phải tra tay trước khi dùng.
