# Baseline run — general LLM, no corpus, no retrieval

**22/08/2026.** First real number of the project.

**Method.** The 6 fact patterns were given to a general-purpose model in a **clean
context that had never seen `expected_citations.csv`**, with tools disabled, phrased
the way a user would ask. Scoring is against what the **courts actually cited** in
the `Căn cứ` blocks (and, for FP05, the án lệ's own
*"Quy định của pháp luật liên quan"* section).

Only substantive citations counted — `bat_buoc = yes` and `loai ∈ {noi_dung,
luat_cu, an_le}`. Procedural, án phí and interest boilerplate excluded from scoring.

---

## The headline number is NOT what I predicted

| Fact pattern | Substantive hits | Score |
|---|---|---|
| FP01 — nhà đất, sổ đỏ một tên | Đ59 ✓, Đ62 ✓, BLDS Đ213 ✓ (Đ219 ✗), TTLT nêu được văn bản nhưng **không biết là Điều 7** | **3.0 / 6** |
| FP02 — cha mẹ tặng riêng | Đ33 ✓, Đ43 ✓, Đ59 ✓ — trượt Đ61, Đ62, Đ63 | **3 / 6** |
| FP03 — nợ chung | Đ37 ✓, Đ60 ✓ | **2 / 2** |
| FP04 — sống chung với gia đình | Đ61 ✓, Đ59 ✓ | **2 / 2** |
| FP05 — mua trước đăng ký kết hôn | Đ3 kh13 ✓, Đ33 ✓, BLDS 2015 Đ208 ✓ — **trượt án lệ**, trượt toàn bộ nhóm luật cũ | **1.5 / 5** |
| **Tổng** | | **11.5 / 21 ≈ 55%** |

**I expected this to be far worse, and I was wrong.** On the core family-law
articles — Đ33, Đ37, Đ43, Đ59, Đ60, Đ61 — the baseline is **good**. Those are the
famous articles; a general model knows them.

**So "AI hallucinates legal citations" is not the honest argument here.** It didn't
invent a single article number. It even volunteered its own uncertainty twice, in
writing, and told the user to go verify. That is better behaviour than I assumed.

If the project's pitch is "the baseline makes things up," the pitch is false and a
mentor will break it in one question. The real argument is narrower and stronger.

---

## Where it actually fails — four failure modes, all verified

### 1. 🔴 Silent staleness — cited a decree replaced last year

For FP06 the baseline cited:

> "Nghị định 10/2015/NĐ-CP (sửa đổi, bổ sung bởi Nghị định 98/2016/NĐ-CP)"

**Nghị định 10/2015/NĐ-CP was replaced by Nghị định 207/2025/NĐ-CP.** Confirmed
twice: in our own relationship graph
(`207/2025/NĐ-CP → Thay thế → 10/2015/NĐ-CP`) and independently by search.

The model stated it as current law. **No warning, no hedge, no date.** This is the
failure `force_check` exists for, caught on the first run.

### 2. 🔴 Misattribution — right rule, wrong article

For FP01 and FP04 the baseline cited **"Điều 29 khoản 2"** for the rule that
*"Lao động của vợ, chồng trong gia đình được coi như lao động có thu nhập."*

I checked the statute. That phrase is in **Điều 59 khoản 2 điểm b**. Điều 29 is
*"Nguyên tắc chung về chế độ tài sản của vợ chồng"* and does not contain it.

The rule is real, the quote is nearly verbatim, the article number is wrong. **This
is more dangerous than an invented citation** — an invented article fails the moment
anyone looks it up; a real article with the wrong number looks correct until someone
reads it.

### 3. 🔴 Temporal blindness — 0 / 2

Neither FP01 nor FP05 produced a single citation to law in force at the time the
property was formed. The baseline answered as if only current law existed.

Ground truth for FP01 includes **Điều 95, 97, 98 Luật HNGĐ 2000** and **khoản 2, 3
Điều 170 Luật Đất đai 2013** — a 2024 judgment applying repealed statutes, correctly,
under Điều 58 khoản 2. The baseline gave neither. It also cited **Điều 98 Luật Đất
đai 2013** where the court cited **Điều 170** — wrong article, right statute.

### 4. 🔴 No scope — FP06 failed completely

Expected output: **empty**. Out of scope for a property-division tool.

Baseline output: **8 citations**, confident and detailed — Đ95, 96, 97, 98, 99, 100
LHNGĐ, Nghị định 10/2015, Thông tư 57/2015, plus Bộ luật Hình sự Đ187.

A general model has no scope to be outside of, so it answers everything. It cannot
say "not my job" because it was never given a job boundary. **This is the single
clearest gap, and it is structural, not a matter of model quality.**

### One thing it got right that deserves credit

On FP05 the baseline **refused to invent an án lệ number**:

> "Tôi không đủ tin cậy để khẳng định chính xác số hiệu án lệ (có thể thuộc nhóm án
> lệ công bố năm 2023) — bạn nên tra trực tiếp trên Cổng thông tin án lệ."

It guessed the wrong year (the answer is **Án lệ 82/2025/AL**) but it declined to
fabricate. Report this honestly. A baseline that behaves well in one respect makes
the comparison credible in the others.

---

## What this means for the project's claim

The claim has to change. **Not** *"the baseline invents citations, mine doesn't."*
It doesn't invent them.

The defensible claim, with this evidence behind it:

> A general model recovers the well-known articles of Luật Hôn nhân và Gia đình at
> roughly 55% on real judgments. What it does not do is tell you **whether the law
> it cites is still in force**, **which law governed the facts at the time they
> happened**, **which án lệ applies**, or **when the question is outside its scope**.
> Those four are deterministic checks over a fixed corpus, not model capabilities.

Each of the four maps to a component already designed:

| Failure | Component |
|---|---|
| Silent staleness | `force_check.py` |
| Misattribution | validation layer — citation must resolve to a real article in corpus |
| Temporal blindness | `force_check.py` temporal rework (not yet written) |
| No scope | `allowlist.csv` + the `control` group |

---

## Caveats — stated so nobody overreads this

1. **n = 6.** Five real cases. Indicative, not a measurement. Expand to ~30 before
   putting a percentage in front of anyone.
2. **One model, one run.** No sampling, no variance. A different model, or the same
   model on a different day, will score differently.
3. **`bat_buoc` is my judgment, not the court's.** In both judgments I checked, every
   article appeared **only** in the `Căn cứ` block and was never discussed in
   "Nhận định". So "essential vs incidental" is inference. The full-set score should
   be reported alongside this one. Four calls are still marked `chua_kiem`.
4. **FP03 is a weak case.** The court recorded a settlement — *"các đương sự đã thoả
   thuận được với nhau về các khoản nợ"* — rather than deciding. The baseline scored
   2/2 on it, which flatters the baseline on the easiest item.
5. **Scoring by hand.** No scoring script yet, so this is not yet reproducible.
