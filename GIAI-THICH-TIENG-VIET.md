# Giải thích lại toàn bộ ý tưởng, và bước 1 cụ thể

---

## Phần 1 — Ý tưởng, nói lại thật đơn giản

### Vấn đề

Ở Việt Nam, muốn biết chia tài sản khi ly hôn thế nào, **đọc mỗi Luật Hôn nhân và Gia
đình là không đủ.** Luật nói nguyên tắc chung. Muốn biết áp dụng thật sự ra sao, phải đọc
thêm:

- Nghị định hướng dẫn Luật
- Thông tư liên tịch hướng dẫn Tòa án xử
- Nghị quyết của Hội đồng Thẩm phán
- Bộ luật Dân sự (vì tài sản là quan hệ dân sự)
- Luật Đất đai (nếu tài sản là nhà đất — mà phần lớn là nhà đất)
- Án lệ liên quan

Một người bình thường không biết danh sách này. Ngay cả sinh viên luật cũng phải mất thời
gian mới ráp đủ. **Đó chính là vấn đề bạn định giải quyết.**

### Công cụ này làm gì

Người dùng nhập một tình huống bằng lời thường:

> *"Vợ chồng cưới năm 2010. Nhà mua năm 2015, sổ đỏ đứng tên chồng. Vợ ở nhà nuôi con
> không đi làm. Giờ ly hôn."*

Công cụ trả về **bộ hồ sơ pháp lý đầy đủ cần đọc**:

- Điều nào của Luật HNGĐ 2014 điều chỉnh việc này
- Nghị định / Thông tư / Nghị quyết nào hướng dẫn chính những Điều đó
- Điều nào của Bộ luật Dân sự, Luật Đất đai liên quan
- Án lệ nào có liên quan (và ghi rõ: án lệ là **tham khảo bắt buộc nghiên cứu, không phải
  ràng buộc tuyệt đối** như án lệ Anh–Mỹ)
- Chỗ nào giữa các văn bản đó **mâu thuẫn / mơ hồ / bỏ trống**
- **Văn bản nào đã hết hiệu lực** — cái này quan trọng, nói ở dưới

### Công cụ này KHÔNG làm gì — và đây mới là phần quan trọng nhất

- ❌ **Không nói người đó nên làm gì.** Không tư vấn.
- ❌ **Không dự đoán tòa sẽ xử thế nào.**
- ❌ **Không soạn đơn từ để nộp thật.**
- ❌ **Không trả lời khi trong kho tài liệu không có căn cứ.** Phải nói "không tìm thấy",
  tuyệt đối không được bịa ra từ trí nhớ của model.

Nói cách khác: nó là **"đây là toàn bộ những gì bạn cần đọc trước khi bắt đầu"**, không
phải chatbot trả lời câu hỏi pháp luật.

### Vì sao phải khắt khe như vậy

Đây là failure mode nổi tiếng của AI pháp lý: **model bịa ra số hiệu bản án, số điều luật
trông y như thật.** Luật sư ở Mỹ đã bị tòa phạt vì nộp hồ sơ có trích dẫn do AI bịa.
DoNotPay bị FTC phạt 193.000 USD.

Nên kiến trúc phải giống hệt ReefCommand:

| ReefCommand | Dự án này |
|---|---|
| Danh mục cách chữa san hô viết tay, có trích dẫn | Danh sách ~15 văn bản viết tay (allowlist) |
| Model chỉ được **chọn** trong danh mục, không được **thêm** | Model chỉ được trích dẫn văn bản có trong allowlist |
| 9 check chặn build nếu thiếu trích dẫn | Check mọi trích dẫn phải giải được ra ID thật |
| Provenance: live / cached / simulated | Provenance: còn hiệu lực / hết hiệu lực / ngày snapshot |
| 4 nguyên nhân chấm điểm độc lập, không cộng thành 100% | Các vấn đề pháp lý chấm điểm độc lập |
| Đúng **1** thành phần được tự quyết | Đúng **1** bước gọi model (`judge.py`) |

### Điểm mạnh nhất — cái tôi đề nghị làm điểm nhấn

Mọi chatbot luật Việt Nam hiện nay đều sẵn sàng trích dẫn cho bạn **một nghị định đã hết
hiệu lực** mà không báo gì.

Năm 2025 Việt Nam sáp nhập tỉnh, đổi sang tòa án 2 cấp từ 1/7/2025 — hàng loạt văn bản bị
thay thế. Ngay cả Bộ luật Tố tụng dân sự 2015 cũng đã sửa đổi bổ sung năm 2025.

Bộ dữ liệu có sẵn 3 trường:

```
tinh_trang_hieu_luc   -- còn hiệu lực / hết hiệu lực
ngay_co_hieu_luc      -- ngày bắt đầu có hiệu lực
ngay_het_hieu_luc     -- ngày hết hiệu lực
```

Nên bạn **viết code kiểm tra được** — không cần model, không cần đoán:

> Văn bản này có còn hiệu lực **vào ngày xảy ra sự việc** không?

Nếu không → dán nhãn `ĐÃ HẾT HIỆU LỰC`, không bao giờ âm thầm bỏ qua, không bao giờ âm
thầm hiển thị như bình thường.

**Negative control chứng minh check này thật:** bỏ Luật Hôn nhân và Gia đình **2000** (đã
bị thay bởi bản 2014) vào allowlist → build **phải đỏ**. Một check chưa từng bắt được gì
thì không chứng minh được gì cả — đúng như bạn đã viết trong START-HERE.

---

## Phần 2 — Bạn hiểu đúng chỗ nào, và hiểu sai chỗ nào

### ✅ Bạn hiểu ĐÚNG

> *"our first step is to build the dataset right? It is to create a connection between 15
> legal docs about hôn nhân & gia đình"*

**Chính xác.** Đó đúng là bước 1. Và lý do nó là bước 1: bộ dữ liệu trên Hugging Face chỉ
có quan hệ **văn bản → văn bản**:

```
doc_id | other_doc_id | relationship
```

Nó chỉ nói được *"Nghị định 126/2014 có liên quan tới Luật 52/2014"*. Nó **không** nói được
*"Điều 59 Luật HNGĐ được hướng dẫn bởi Điều 7 Thông tư liên tịch 01/2016"*.

Mà cái thứ hai mới là toàn bộ giá trị của dự án. **Không ai đưa sẵn cho bạn.** Phải tự
xây. Đó là "connection between 15 legal docs" mà bạn vừa nói — bạn nói đúng.

### ❌ Bạn hiểu SAI

> *"I need to download 15 docs and read it myself, which I cannot anymore"*

**Không phải vậy. Và tôi đọc được — tôi vừa đọc xong trong lúc trả lời tin nhắn này.**

Ví dụ, tôi vừa mở Nghị quyết 01/2024/NQ-HĐTP và đọc ra:

- Nó có **12 Điều**
- Ban hành 16/5/2024, có hiệu lực 1/7/2024
- Nó hướng dẫn các Điều **51, 55, 56, 66, 81, 82, 85** của Luật HNGĐ 2014
- **Điều 5** của nó hướng dẫn Điều 66 Luật HNGĐ (hạn chế phân chia di sản)
- Nó **không** thay thế Thông tư liên tịch 01/2016 — hai văn bản cùng tồn tại

Đó chính là loại thông tin dùng để xây "connection". Tôi làm được việc đó, hàng loạt, cho
cả 15 văn bản. Bạn **không cần** ngồi đọc lại từ đầu.

Xin lỗi vì tài liệu trước tôi viết chưa rõ chỗ này. Tôi viết *"[Kenny, no code]"* làm bạn
tưởng là *"Kenny đọc hết một mình"*. Không phải.

---

## Phần 3 — Ranh giới thật: tôi đọc được, nhưng có một việc tôi KHÔNG được làm

Đây là chỗ tôi phải nói thẳng, vì nó quyết định dự án có giá trị hay không.

**Tôi soạn được:**

- ✅ Allowlist — 15 văn bản nào thuộc phạm vi (đây là việc tra cứu, tôi làm tốt)
- ✅ Article map — Điều nào hướng dẫn Điều nào (phần lớn **văn bản tự nói ra**: thông tư
  ghi rõ "hướng dẫn Điều 59")
- ✅ Danh sách án lệ liên quan tới nhánh này
- ✅ Danh sách các mâu thuẫn đã được nhà nghiên cứu công bố, kèm link

**Tôi KHÔNG được soạn: đáp án đúng của bộ test (eval set).**

Lý do không phải là "Kenny phải nhớ luật". Lý do là **logic vòng tròn**:

> Nếu tôi viết câu hỏi, rồi tôi viết luôn đáp án, rồi hệ thống của bạn (cũng dùng model)
> trả lời — thì bài test đó đo cái gì?
>
> Nó chỉ đo **model có đồng ý với chính nó không**. Nó không đo được hệ thống của bạn có
> đúng luật không.
>
> Con số bạn báo cáo cuối cùng sẽ **vô nghĩa**. Và nếu ai đó hỏi "đáp án đúng ở đâu ra?"
> mà câu trả lời là "AI viết", toàn bộ kết quả sụp đổ.

Đây đúng là điều DATA-BUILD-PLAN đã cảnh báo: *"Don't let the model touch the eval set's
ground truth."* Cảnh báo đó đúng, và tôi phải giữ nó.

### Nhưng — giải pháp không phải là bắt bạn nhớ lại luật

Đây là chỗ tôi nghĩ kế hoạch cũ sai, và tôi đề nghị đổi.

**Đáp án đúng không đến từ trí nhớ của bạn. Cũng không đến từ tôi. Nó đến từ bản án thật
do thẩm phán viết.**

Nhớ con số tôi tìm được: cổng `congbobanan.toaan.gov.vn` đã công bố **~955.000 bản án hôn
nhân & gia đình** (tính tới tháng 1/2026 — nhóm lớn nhất trong gần 2 triệu bản án).

Một bản án thật có sẵn **cả hai vế**:

| Bản án có sẵn | Dùng làm gì |
|---|---|
| Phần "Nội dung vụ án" | → chính là **fact pattern** (câu hỏi) |
| Phần "Nhận định của Tòa án" / "Áp dụng Điều..." | → chính là **đáp án đúng** (tòa đã áp dụng điều nào) |

Đáp án do **thẩm phán** viết. Không phải bạn nhớ lại. Không phải tôi bịa ra.

### Vậy việc của bạn là gì

Bạn chuyển từ **người phải nhớ luật** → thành **người kiểm tra**.

Cụ thể, với mỗi mục tôi soạn, bạn chỉ cần trả lời được:

1. Cái này có **thuộc chủ đề chia tài sản ly hôn** không? (có / không)
2. Trích dẫn này **có thật sự nói như vậy** không? (mở link ra, đọc 1 đoạn, so)
3. Có cái gì **rõ ràng vô lý** không?

Câu 1 và câu 3 bạn làm được ngay. Câu 2 là **đọc để đối chiếu, không phải nhớ lại** — nhẹ
hơn nhiều, và chính là kỹ năng mà việc bạn từng học luật vẫn còn nguyên giá trị, kể cả sau
nhiều năm.

Đây cũng chính xác là việc bạn đã làm ở ReefCommand: bạn không tự nghĩ ra số giờ lặn. Bạn
**nhìn vào số có sẵn và thấy nó vô lý** — 5.0 giờ cần, đội mạnh nhất chỉ có 4.7. Đó là
kiểm tra, không phải sáng tạo. Và nó là thứ giá trị nhất trong cả dự án.

---

## Phần 4 — Bước 1 cụ thể, làm ngay hôm nay

**Bước 1 = chốt allowlist. ~15 văn bản. Chưa viết dòng code nào.**

Tôi đã soạn sẵn bản nháp ở dưới. Việc của bạn: **duyệt** — giữ, bỏ, hoặc thêm.

### Bản nháp allowlist (tôi soạn — bạn duyệt)

**Nhóm A — lõi, chắc chắn giữ**

| # | Văn bản | Số hiệu | Vì sao trong phạm vi |
|---|---|---|---|
| 1 | Luật Hôn nhân và Gia đình 2014 | 52/2014/QH13 | Luật gốc. Chia tài sản nằm ở Điều 33–46 (tài sản chung/riêng), 47–50 (chế độ thỏa thuận), 59–64 (nguyên tắc chia khi ly hôn) |
| 2 | Nghị định 126/2014/NĐ-CP | 126/2014/NĐ-CP | Nghị định quy định chi tiết thi hành Luật số 1 |
| 3 | Thông tư liên tịch 01/2016 | 01/2016/TTLT-TANDTC-VKSNDTC-BTP | Điều 7 hướng dẫn trực tiếp **nguyên tắc chia tài sản** |
| 4 | Nghị quyết 01/2024/NQ-HĐTP | 01/2024/NQ-HĐTP | HĐTP TANDTC hướng dẫn Điều 51, 55, 56, 66, 81, 82, 85. Có hiệu lực 1/7/2024 |

**Nhóm B — luật liên quan, gần như chắc chắn cần**

| # | Văn bản | Số hiệu | Vì sao trong phạm vi |
|---|---|---|---|
| 5 | Bộ luật Dân sự 2015 | 91/2015/QH13 | Sở hữu chung, giao dịch, thời hiệu |
| 6 | Luật Đất đai 2024 | 31/2024/QH15 | Phần lớn tài sản tranh chấp là nhà đất |
| 7 | Luật Nhà ở 2023 | 27/2023/QH15 | Sở hữu nhà ở |
| 8 | Bộ luật Tố tụng dân sự 2015 | 92/2015/QH13 | ⚠️ **Đã sửa đổi bổ sung 2025** — phải lấy bản hợp nhất |

**Nhóm C — cần bạn quyết**

| # | Văn bản | Số hiệu | Câu hỏi cho bạn |
|---|---|---|---|
| 9 | Nghị định 82/2020/NĐ-CP | 82/2020/NĐ-CP | Xử phạt hành chính. **Có thuộc phạm vi chia tài sản không, hay ngoài phạm vi?** Tôi nghiêng về **bỏ** |
| 10 | Nghị định 207/2025/NĐ-CP | 207/2025/NĐ-CP | Mang thai hộ / hỗ trợ sinh sản. **Có liên quan chia tài sản không?** Tôi nghiêng về **bỏ** |
| 11 | Nghị định 123/2015/NĐ-CP | 123/2015/NĐ-CP | Đăng ký hộ tịch. Tôi nghiêng về **bỏ** — đăng ký, không phải tranh chấp |
| 12 | Án lệ (nhánh HNGĐ) | — | 90 án lệ đang có hiệu lực từ 1/7/2026. Cần lọc ra khoảng 5–10 cái liên quan tài sản vợ chồng |

**⚠️ Cần kiểm tra riêng — tôi chưa xác minh được:**

- **Luật Đất đai 2024 và Luật Nhà ở 2023 có bị sửa trong đợt cải cách 2025 không.**
  Tôi chưa kiểm tra. Phải xác minh trước khi chốt.
- **Ngày snapshot của bộ dữ liệu Hugging Face.** Trang dataset không ghi. Nếu snapshot cũ
  hơn 1/7/2025 thì trường `tinh_trang_hieu_luc` đã lạc hậu và cả check hiệu lực sẽ sai
  một cách âm thầm — đúng loại lỗi nguy hiểm nhất theo tiêu chí của bạn.

### Vậy hôm nay bạn làm gì

Ba việc, không cần code, không cần nhớ luật:

1. **Đọc bảng trên. Trả lời 3 câu hỏi ở Nhóm C** (giữ hay bỏ mục 9, 10, 11).
2. **Nhìn Nhóm A và B, nói xem tôi có bỏ sót văn bản nào không.** Chỉ cần cảm giác
   "hình như thiếu cái gì đó về..." là đủ — tôi sẽ đi tra.
3. **Quyết định phạm vi:** chỉ chia tài sản **khi ly hôn**, hay bao gồm cả chia tài sản
   **trong thời kỳ hôn nhân** (Điều 38–42)? Cái này thay đổi allowlist. Tôi nghiêng về
   **chỉ ly hôn** cho v1 — hẹp hơn, dễ xong hơn.

Xong 3 việc đó là bước 1 hoàn thành. Sau đó tôi đi lấy văn bản, tách ra thành từng Điều,
và soạn bản nháp article map để bạn duyệt tiếp.

---

## Phần 5 — Thứ tự các bước, nhìn tổng thể

```
BƯỚC 1  Chốt allowlist ~15 văn bản          <- ĐANG Ở ĐÂY. Tôi soạn, bạn duyệt
   |
BƯỚC 2  Tôi lấy văn bản, tách thành từng Điều, soạn article map
   |     Bạn kiểm tra mẫu ~10 dòng
   |
BƯỚC 3  Viết check hiệu lực (code)
   |     Negative control: bỏ Luật HNGĐ 2000 vào -> build phải đỏ
   |
BƯỚC 4  Lấy 5 bản án thật từ congbobanan -> làm eval set đầu tiên
   |     Đáp án do thẩm phán viết, không phải bạn nhớ
   |
BƯỚC 5  Retrieval (tìm điều luật từ tình huống)
   |
BƯỚC 6  Bước gọi model duy nhất + lớp validate
   |
BƯỚC 7  Mở rộng eval lên ~30 bản án, chạy baseline vs hệ thống, báo cáo số thật
```

Khoảng **5 tuần làm bán thời gian**. Mỗi tuần kết thúc bằng một thứ **chạy được và cho
xem được**.

---

## Một điều tôi chưa xác minh được, nói trước cho rõ

Ở Bước 4 tôi đề nghị lấy bản án từ `congbobanan.toaan.gov.vn`. **Tôi chưa mở được
robots.txt và điều khoản sử dụng của cổng đó** — cả hai lần fetch đều lỗi.

Nên trước khi lấy bản án hàng loạt, bạn phải tự mở trình duyệt kiểm tra điều khoản. Nếu
không được phép lấy tự động, phương án dự phòng là **chép tay 5–10 bản án** — vẫn đủ cho
eval set đầu tiên, chỉ chậm hơn.

Tôi không muốn bạn xây cả kế hoạch trên một giả định mà tôi chưa kiểm chứng được.
