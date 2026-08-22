# Bộ đề (eval set) — 6 fact pattern đầu tiên

**Đây là output của task lớn thứ hai.** Sáu ca: 4 bản án thật, 1 án lệ, 1 ca âm.

**Đáp án không do Kenny nhớ ra, không do Claude bịa ra.** Bốn ca đầu lấy nguyên
văn khối *"Căn cứ"* trong phần QUYẾT ĐỊNH của bản án — tức điều luật do **thẩm
phán** viện dẫn. Ca thứ năm lấy từ mục *"Quy định của pháp luật liên quan đến án
lệ"* do **Hội đồng Thẩm phán TANDTC** công bố.

---

## 🔴 Bộ đề vừa phá một giả định trong `force_check.py`

Đây là lý do phải viết 5 ca trước khi xây tiếp — và nó xuất hiện ngay ở ca đầu tiên.

**Bản án 111/2024/HNGĐ-ST**, tuyên ngày **30/8/2024**, viện dẫn trong phần Căn cứ:

> "Các Điều **95, 97, 98 Luật hôn nhân và gia đình năm 2000**;
> Điều 59, Điều 62, Điều 131 Luật Hôn nhân và gia đình năm 2014;
> Khoản 2, khoản 3 Điều 170 **Luật đất đai năm 2013**."

**Luật HNGĐ 2000 đã bị Luật 2014 thay thế. Luật Đất đai 2013 đã bị Luật 2024 thay
thế.** Vậy mà một bản án năm 2024 viện dẫn cả hai — **và hoàn toàn đúng luật**, vì
tài sản hình thành trong thời kỳ các luật đó còn hiệu lực (Điều 58 khoản 2 Luật
Ban hành VBQPPL: áp dụng văn bản có hiệu lực **tại thời điểm xảy ra sự việc**).

Án lệ 03/2016/AL còn cực đoan hơn: nó viện dẫn **Điều 14 Luật HNGĐ 1986** và
**Điều 242, khoản 2 Điều 176 Bộ luật Dân sự 1995**. Cả ba đã chết từ trước khi án
lệ được công bố. **Án lệ vẫn đang có hiệu lực.**

### Thiết kế cũ của tôi sẽ trả lời sai

```
force_check(Luật HNGĐ 2000, ngay_su_viec=2024) -> HET_HIEU_LUC -> CHẶN
```

Chặn một trích dẫn mà tòa án thật đã dùng đúng. **Nếu tôi không đọc bản án thật,
lỗi này sẽ nằm im trong hệ thống cho tới lúc có người biết luật nhìn vào.**

### Vì sao sai: "ngày sự việc" không phải MỘT ngày

Một vụ chia tài sản trải qua nhiều thời kỳ pháp luật:

```
2005 ────────── 2013 ──────── 2015 ────────── 2023 ──── 2024
kết hôn         mua đất       Luật 2014       ly hôn    xét xử
                              có hiệu lực
   │               │                             │
   └─ LHNGĐ 2000 ──┘                             └─ LHNGĐ 2014
      Luật ĐĐ 2013                                  Luật ĐĐ 2024?
```

Câu hỏi *"tài sản này là chung hay riêng"* xét theo luật **lúc hình thành tài sản**.
Câu hỏi *"chia thế nào khi ly hôn"* xét theo luật **lúc ly hôn**. Cùng một vụ, hai
mốc thời gian, hai bộ luật — **cả hai đều đúng**.

### Thiết kế mới

`force_check` **không được CHẶN** văn bản đã hết hiệu lực. Nó phải **DÁN NHÃN**:

| Nhãn | Nghĩa |
|---|---|
| `CON_HIEU_LUC` | Còn hiệu lực tại mốc thời gian của vấn đề này |
| `LUAT_AP_DUNG_CHO_SU_VIEC_CU` | Đã hết hiệu lực chung, **nhưng đúng** cho mốc này |
| `SAI_MOC_THOI_GIAN` | Trích luật chưa ra đời tại mốc này — **đây mới là lỗi thật** |

Và mỗi trích dẫn phải kèm **mốc thời gian nó áp dụng cho**, không phải một câu
"còn/hết hiệu lực" chung chung.

Đây là thay đổi lớn cho `force_check.py` + test. Chưa làm — ghi ra đây trước.

---

## Sáu ca, và vì sao chọn đúng sáu ca này

| ID | Nhóm vấn đề | Điều quyết định | Nguồn |
|---|---|---|---|
| **FP01** | Nhà đất, sổ đỏ một tên, vợ nội trợ | Đ59, Đ62 + **TTLT Đ7** | Bản án 111/2024/HNGĐ-ST |
| **FP02** | Cha mẹ tặng riêng cho một bên | **Đ43** (tài sản riêng) | Bản án 14/2023/HNGĐ-PT |
| **FP03** | Nợ chung | **Đ37, Đ60** | Bản án 32/2024/HNGĐ-ST |
| **FP04** | Sống chung với gia đình | **Đ61** | Bản án 02/2021/HNGĐ-ST |
| **FP05** | Mua trước khi đăng ký kết hôn | **Án lệ 82/2025/AL** | QĐ 339a/QĐ-CA |
| **FP06** | **CA ÂM — ngoài phạm vi** | phải trả **rỗng** | (ca kiểm thử) |

**FP01 vs FP02 là cặp đối chứng có chủ đích.** Cả hai đều là "tài sản liên quan cha
mẹ / đứng tên một người", nhưng kết quả **ngược nhau**:

- FP02: cha mẹ tặng **riêng cho chồng** → **tài sản riêng**, vợ chỉ được **30% công sức**
- Án lệ 03/2016/AL: cha mẹ cho **cả hai vợ chồng** → **tài sản chung**

Khác nhau ở *tặng cho ai*. Nếu hệ thống trả cùng một bộ điều luật cho cả hai, nó
chưa phân biệt được — và đó là loại sai một luật sư phát hiện trong năm giây.

**FP06 là ca âm và nó nhắm thẳng vào nhóm `control`.** Corpus **có chứa** Nghị định
207/2025 và các Thông tư BYT về mang thai hộ. Câu hỏi FP06 hỏi đúng về mang thai hộ.
Đáp án đúng vẫn là **"ngoài phạm vi, không trả lời"** — vì công cụ này là công cụ
chia tài sản. Nếu hệ thống trả về nhóm control, nó **fail**, dù các văn bản đó có
thật và đúng chủ đề. Đây là test khó nhất trong sáu ca.

---

## Định dạng đầu ra — quyết định rút ra từ chính bộ đề

Trước khi có bộ đề, chưa ai quyết hệ thống in ra cái gì. Đọc 4 bản án thật cho ba
kết luận:

**1. Không phải trích dẫn nào cũng ngang nhau.** Bản án 111/2024 viện dẫn cả điều
về án phí (NQ 326) lẫn điều về nguyên tắc chia (TTLT Đ7). Trộn chung là vô dụng.
Cột `loai` trong `expected_citations.csv` phân ra: `noi_dung`, `luat_cu`,
`thu_tuc`, `an_phi`, `lai_suat`, `chuyen_tiep`, `an_le`.

**Chỉ chấm điểm trên `bat_buoc = yes`.** Bỏ sót Điều 7 TTLT là hỏng; bỏ sót điều
án phí thì không.

**2. Mỗi trích dẫn cần bốn thông tin, không phải một.**
`(văn bản, điều, rank theo Điều 4, mốc thời gian áp dụng)`

**3. Án lệ và công văn phải có nhãn riêng.** Án lệ 82/2025 tự nêu **cả luật cũ lẫn
điều tương ứng của luật hiện hành** — kỹ thuật soạn thảo giữ cho án lệ sống qua
các lần đổi bộ luật. Hệ thống phải giữ được cặp đó, không được rút gọn.

---

## Cách chấm điểm

Trên các dòng `bat_buoc = yes`:

- **Article-set F1** — so tập điều trả về với tập điều tòa đã viện dẫn
- **Tỉ lệ trích dẫn bịa** — trích dẫn không tồn tại trong corpus. Hệ thống này
  phải bằng **0 tuyệt đối** (chặn ở lớp validate); baseline sẽ không bằng 0
- **Độ chính xác nhãn thời gian** — có nhận ra Luật HNGĐ 2000 là `luat_cu` hợp lệ
  chứ không phải lỗi không
- **FP06 tính riêng** — chỉ đạt khi trả về **rỗng**

---

## Việc của Kenny

Với mỗi ca, mở link và trả lời ba câu — **đối chiếu, không phải nhớ lại**:

1. Phần tình huống tôi tóm có **đúng bản án** không, hay tôi thêm bớt?
2. Khối `Căn cứ` trong bản án có **đúng** những điều tôi ghi ở
   `expected_citations.csv` không?
3. Cột `bat_buoc` tôi đánh có hợp lý không — điều nào tôi cho là phụ mà thực ra
   quan trọng?

Nếu ba câu này ổn, bộ đề thành ground truth và mọi thứ sau đó có thước đo.

---

## Chưa xác minh được

1. Bốn khối `Căn cứ` được trích **hai lần bằng hai prompt khác nhau và khớp từng
   chữ**, nhưng qua công cụ đọc web chứ không phải curl trực tiếp. Nên bạn mở link
   kiểm lại.
2. **Bản án 111/2024**: ngày cấp Giấy chứng nhận ra kết quả không nhất quán giữa
   hai lần trích (26/8/2005 và 26/7/2016). **Không dùng ngày này** cho tới khi kiểm.
3. **Bản án 111/2024**: người vợ *"làm nghề nội trợ và buôn bán trái cây"* — không
   phải hoàn toàn không có thu nhập. Đừng mô tả ca này là "vợ không có thu nhập".
4. Án lệ 03/2016/AL còn hiệu lực: xác nhận qua thuvienphapluat, **chưa** đối chiếu
   được cổng chính thức `anle.toaan.gov.vn` (trang JS trả về cache cũ, vẫn ghi 72 án lệ).
