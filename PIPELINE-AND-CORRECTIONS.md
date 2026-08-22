# Pipeline, structure, and four corrections to the brief

**Written after reading START-HERE-Kenny.md, IDEA-BRIEF.md and DATA-BUILD-PLAN.md, and
doing independent verification of every load-bearing factual claim in them.**

Read section 1 first. It contains things in your existing plan that are wrong, and you
asked to be told immediately with evidence.

---

## 1. Four corrections — the evidence went against you

### 1.1 The VLegal-Bench comparison does not work as framed. This is the big one.

Your IDEA-BRIEF says: *"VLegal-Bench found the best general model hit only 43.83% on
article prediction, and 16 of 23 models scored 0.00 on conflict detection. Beating that
baseline on this narrow slice, even modestly, is a specific, defensible result."*

I read the paper. Three problems.

**Problem one — it is a different task.** VLegal-Bench Task 3.1 (article/clause
prediction) is **multiple-choice and closed-book**. The model picks from a supplied list
of options with no corpus, no retrieval, testing what the model memorised. Your system is
open-set retrieval: it goes and finds articles in a corpus. A retrieval score and a
closed-book multiple-choice accuracy are not the same number, and putting them side by
side in a pitch is the same category of false claim as the two that got caught in your
hackathon pitch. It would get you destroyed by anyone who has read the paper.

**Problem two — 43.83% is not a general model.** That score belongs to
`qwen3-4b-legal-pretrain`, a model already pre-trained on legal text. GPT-4o scored 38.83%
and GPT-4o-mini 35.33%. Small difference, but "the best general model" is inaccurate.

**Problem three — conflict detection is not unsolved.** "16 of 23 models scored 0.00" is
true, and it is a real finding about most models defaulting to "no conflict." But the best
score on that task was **86.41 Y-F1** (CMC-AI-Legal-32B, the paper authors' own domain
model), and GPT-4o got 27.21 Y-F1 — not zero. If you say "nobody can do conflict
detection," the paper you are citing contradicts you on its own results table.

**What to do instead.** Drop the cross-paper comparison entirely. Run **your own baseline
on your own eval set**: the same fact patterns, the same required output format, a general
LLM with no corpus versus your system. Same task, same data, same scoring — that is a
comparison that survives a question. Keep VLegal-Bench as background motivation only:
*"a 2025 benchmark showed most models default to 'no conflict', which is why I built a
system that cannot silently do that."* That sentence is true and defensible. The
percentage comparison is not.

Source: [VLegal-Bench, arXiv 2512.14554](https://arxiv.org/html/2512.14554v1)

### 1.2 The relationship graph is document-level, not article-level

Your DATA-BUILD-PLAN says step 3 of Tier A is *"for every base article in scope, the full
chain of decrees/circulars that amend or implement it. This chain **is** the graph the
rest of the system leans on."*

I checked the dataset schema. The `relationships` config has exactly three fields:

```
doc_id | other_doc_id | relationship
```

Document to document. It will tell you *"Nghị định 126/2014 relates to Luật 52/2014."* It
will **not** tell you *"Điều 59 of the Law is implemented by Điều 7 of Thông tư liên tịch
01/2016."* That second thing is the entire value of your idea, and it is not in the
dataset. Nobody hands it to you.

This is not fatal — it is actually the best news in this document, and I explain why in
section 3.1. But your plan currently assumes a free asset that does not exist, and the
build order changes because of it.

Source: [th1nhng0/vietnamese-legal-documents](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents)
(`anhquan12/...` is the same 153,420 / 178,665 / 897,890 dataset — same rows, same schema,
CC BY 4.0, sourced from vbpl.vn)

### 1.3 Tier C is far bigger than you think — and family law is the largest slice of it

Your plan treats `congbobanan.toaan.gov.vn` as probably-broken based on a 2018 account
that only ~1/5 of judgments were being published.

That figure is eight years stale. As of **January 2026**, nearly **2 million** judgments
and decisions are published on the portal. Breakdown:

| Case type | Published |
|---|---|
| **Hôn nhân & gia đình** | **~955,000** |
| Civil | 399,000+ |
| Criminal | 387,000+ |
| Commercial | 35,426 |
| Administrative | 24,542 |
| Labour | 9,475 |

Family and marriage is not a neglected corner of that portal. It is the **largest single
category, roughly half of everything published.** This is a strong point in favour of your
chosen branch and you should know it.

Caveat, stated honestly: I could not reach the portal's `robots.txt` or terms of use from
here — both fetches failed. So "is scraping it permitted" is **unresolved**, and my
recommendation in section 4 keeps Tier C off the critical path until you check that
yourself in a browser.

Source: [Báo Chính phủ, Jan 2026](https://baochinhphu.vn/gan-2-trieu-ban-an-quyet-dinh-duoc-cong-bo-tren-cong-thong-tin-dien-tu-nganh-toa-an-102260128153545772.htm)

### 1.4 Án lệ count, and a live example of why hand-verification is not optional

Your brief says 72 án lệ; a note in the plan says one source found 91.

Current answer: **90 in effect from 1 July 2026**, after Quyết định 162/QĐ-CA of 29 May
2026 added 8 more. Numbering runs 01/2016/AL through 90/2026/AL.

Note what happened while I checked. One page's **title** said 91 and its **body** said 90.
That is the exact shape of the reef dive-hours bug: a number that looks fine, is wrong,
and nothing tests it. Verify the count against the Supreme Court's own portal
(`anle.toaan.gov.vn`), not an aggregator, and record the date you checked it.

Sources: [CLEAD list](https://clead.vn/blogs/tin-tuc-phap-luat/danh-sach-90-an-le-co-hieu-luc-tu-1-7-2026) ·
[LSVN on the 8 new án lệ](https://lsvn.vn/them-8-an-le-moi-ap-dung-tu-ngay-01-7-2026-duoc-toa-an-nhan-dan-toi-cao-cong-bo-a174150.html)

---

## 2. What the research confirmed — the parts of your plan that hold up

**The branch is correctly chosen.** Luật Hôn nhân và Gia đình 2014 is still in force in
2026, with no replacement drafted. Its implementing stack is real and finite:

- Luật Hôn nhân và Gia đình 2014 (133 articles, 9 chapters) — property division sits in
  Điều 33–46, 47–50, 59–64
- Nghị định 126/2014/NĐ-CP — detailed implementation
- Thông tư liên tịch 01/2016/TTLT-TANDTC-VKSNDTC-BTP — Điều 7 carries the division
  principles
- Nghị quyết 01/2024/NQ-HĐTP — judicial guidance on marriage/family cases
- Nghị định 207/2025/NĐ-CP — assisted reproduction / surrogacy
- Nghị định 82/2020/NĐ-CP — administrative penalties
- Plus Bộ luật Dân sự 2015 and Luật Đất đai where marital property is land

That is roughly **10 to 15 documents**. Small enough to hold in your head. That is the
right size for a first solo project.

**Your "base law alone cannot answer it" premise is correct and documented.** Tạp chí Tòa
án nhân dân — the Supreme Court's own journal — publishes an analysis of property-division
principles that names three specific defects:

1. **Điều 47 timing contradiction.** It requires the agreed property regime to be
   established *before* marriage, while simultaneously declaring it effective *from the
   date of marriage registration*.
2. **Retroactivity gap.** The agreed regime is only available to couples married after
   1 Jan 2015; earlier marriages are excluded.
3. **Unquantified criteria.** "Contribution of effort" and "fault" have no measurement
   standard, producing inconsistent application across courts.

This matters for a reason beyond confirmation: **it is where your conflict ground truth
comes from.** Do not invent conflicts. Harvest them from tapchitoaan.vn, danchuphapluat.vn,
kiemsat.vn and the VKSND provincial sites, which regularly publish "vướng mắc / bất cập"
pieces naming specific provisions. Every conflict in your eval set then carries a citation
to a legal professional who identified it. That is provenance, applied to ground truth.

Source: [Tạp chí Tòa án nhân dân](https://tapchitoaan.vn/bai-viet/phap-luat/nguyen-tac-chia-tai-san-chung-cua-vo-chong-khi-ly-hon)

**The dataset gives you one check nobody else does well.** The metadata config carries
`tinh_trang_hieu_luc` (validity status), `ngay_co_hieu_luc` (effective date),
`ngay_het_hieu_luc` (expiry date) and `linh_vuc` (legal field). Which means you can build
a deterministic **"is this document actually still in force on the date of these facts"**
check that fails the build loudly. See section 3.2 — I think this, not conflict detection,
is the strongest thing in the project.

**Retrieval is a solved-enough problem for you.** `AITeamVN/Vietnamese_Embedding` exists
and is usable off the shelf. BM25 with Vietnamese tokenisation (`underthesea` or `pyvi`)
is a genuinely strong legal-retrieval baseline. Start with BM25 alone — it is debuggable,
you can read why it matched, and you can add embeddings later as a measured improvement
rather than an assumption.

---

## 3. The two things that are actually the project

Everything else is plumbing. These two are where the value is, and both are made of your
legal training rather than your code.

### 3.1 The article-level map (the thing that does not exist yet)

Because the dataset stops at document level (correction 1.2), *someone* has to write down
the article-to-article links. For 15 documents in one branch, that is on the order of
60–100 rows. A CSV:

```
source_ref, target_ref, relation_type, note, source_citation
L52-2014#D59.K2, TTLT01-2016#D7.K4, implements, "division principles detail", <url>
L52-2014#D47, L52-2014#D48, tension, "timing contradiction", tapchitoaan.vn/...
```

`relation_type` ∈ `implements | amends | replaces | cross_references | tension`

A few evenings of work for someone with your training. Impossible for someone without it.
**This hand-built map is the project's actual asset** — it is what makes the system
specialised rather than "RAG over Vietnamese law," which a hundred people have built. Do
not let a model write it. The moment a model fills this in, the project is worth nothing.

### 3.2 The force check, which I think should be the headline

Every Vietnamese legal chatbot on the market will happily cite you a repealed decree. The
2025 restructuring — province mergers, the two-tier court system from 1 July 2025 — churned
a large volume of documents. A snapshot dataset on Hugging Face makes this *worse*, because
the snapshot freezes a validity status that has since changed.

So build the check that catches it:

- every document in your allowlist must have a validity status in the corpus, or the build
  fails
- every citation shown must be in force **on the date of the fact pattern**, or it is
  labelled `NO LONGER IN FORCE` — never silently dropped, never silently shown
- the snapshot date of your corpus is stamped on every output

Negative control that proves it works: put a known-repealed document in the allowlist —
Luật Hôn nhân và Gia đình **2000** is the obvious candidate — and assert the build fails.
A check that has never caught anything proves nothing.

This is your DATA-08 pattern, transplanted. It is deterministic, it fails loud, and it is
demonstrably absent from the products you listed as competitors.

---

## 4. The pipeline

Nine stages. Each one is deterministic **except S6**, which is the single bounded model
call — the same shape as ReefCommand's one judging component.

```
  S0  SCOPE LOCK           hand-written document allowlist        [Kenny, no code]
       |
  S1  INGEST               HF snapshot -> filter -> parse to article units
       |
  S2  FORCE CHECK          validity status / dates; fails loudly
       |
  S3  RELATION GRAPH       layer 1: doc->doc from dataset (free)
       |                   layer 2: article->article hand map    [Kenny, no code]
       |
  S4  RETRIEVE             fact pattern -> candidate article units (BM25)
       |
  S5  EXPAND               pull graph neighbours of each candidate
       |
=======|===================================================================
  S6  JUDGE                THE ONE MODEL STEP
       |                   - support scores per legal issue (independent)
       |                   - typed label for graph-linked pairs ONLY
       |                   - may cite only IDs present in its context
=======|===================================================================
       |
  S7  VALIDATE             every cited ID resolves; in allowlist; in force;
       |                   án lệ labelled persuasive-not-binding;
       |                   zero grounded citations -> "not found", never prose
       |
  S8  REPORT               document stack + provenance + snapshot date
       |
  S9  EVALUATE             baseline (LLM, no corpus) vs system, same eval set
```

**Stage detail, and what proves each one worked:**

| Stage | What it does | The check that proves it |
|---|---|---|
| S0 | ~15 doc IDs in a text file. Nothing may ever be cited that is not on this list. This is the reef treatment catalog: the model selects, it cannot add. | You can name every document from memory and say why it is there |
| S1 | Download the HF slice, filter by `linh_vuc` + allowlist, parse `content_html` into article units with stable IDs (`L52-2014#D59.K2`) | Article count for two documents matches your own hand count |
| S2 | Read `tinh_trang_hieu_luc`, `ngay_co_hieu_luc`, `ngay_het_hieu_luc` | Add Luật HNGĐ 2000 to the allowlist → build must fail |
| S3 | Layer 1 free from the dataset; layer 2 is your CSV | **Every ref in the CSV resolves to a real article unit, or fail.** This is DATA-08 |
| S4 | BM25 over article units, Vietnamese tokenised | recall@10 on the eval set — measured and reported even if it is bad |
| S5 | Graph neighbours of each retrieved article. No model. | Deterministic: same input, same output, every time |
| S6 | One model call. Full text of the expanded set in context. | Feed it a criminal-law fact pattern → must return "not found", not confident family law |
| S7 | Citation resolver + force check + label enforcement | Hand-craft a model output citing a fabricated article ID → must be rejected |
| S8 | Assemble output with provenance on every element | Every displayed item carries a source label and a snapshot date |
| S9 | Two runs, one eval set, one scoring script | Baseline's hallucinated-citation rate — see below |

**On S6 — say "conflict" less.** Look again at the three defects from Tạp chí Tòa án in
section 2. Not one of them is a true conflict where two provisions say opposite things.
One is an internal timing contradiction, one is a scope limitation, one is vagueness. If
your system prints "CONFLICT" for those it is simply wrong, and a lawyer will catch it in
five seconds.

Use a typed label instead:

`CONFLICT` · `AMBIGUITY` · `GAP` · `OVERLAP` · `NO_ISSUE`

Harder to get right, much harder to be wrong in an embarrassing way, and it is a more
interesting result to present. "Most models default to NO_ISSUE; mine distinguishes four
kinds of trouble" is a better sentence than a percentage.

**On S9 — the number that will actually land.** Not accuracy. **Hallucinated citation
rate.** Run the ungrounded baseline on your eval set and count how many articles it cites
that do not exist, or exist but say something else. That number will not be small, and it
is the failure mode that got real lawyers sanctioned in real courts. Then point at S7 and
say: mine is structurally zero, and here is the negative control test that proves the
check is real rather than decorative.

That is your ReefCommand moment. It is the same move — a check that catches something —
and it is the strongest thing you can put in front of an audience.

---

## 5. Repo structure

```
vn-property-division/
  README.md
  DISCLAIMER.md              <- write this on day one, before any code
  data/
    raw/                     <- HF snapshot slice. NEVER edited by hand
    allowlist.txt            <- S0. ~15 doc IDs
    corpus/                  <- S1 output. one JSON per document
    map/
      article_relations.csv  <- S3 layer 2. YOUR hand-built map
      anle.csv               <- Tier B, filtered to this branch
    eval/
      fact_patterns.csv      <- ground truth. YOURS. no model touches it
  src/
    ingest.py                <- S1
    force_check.py           <- S2
    graph.py                 <- S3
    retrieve.py              <- S4, S5
    judge.py                 <- S6   (the only file that calls a model)
    validate.py              <- S7
    report.py                <- S8
  tests/
    test_force_check.py      <- incl. the repealed-document negative control
    test_validate.py         <- incl. the fabricated-citation negative control
    test_graph.py            <- incl. the unresolvable-ref negative control
  eval/
    run_baseline.py
    run_system.py
    score.py
    RESULTS.md               <- written after, not before. real numbers only
```

Two rules the layout is enforcing. **Exactly one file calls a model** (`judge.py`) — if
you find yourself importing an LLM client into `retrieve.py`, something has gone wrong.
And `data/eval/` is yours; nothing generates into it.

---

## 6. Where to start — the honest answer

**Not with code, and not with the data pull.**

Your DATA-BUILD-PLAN puts "Tier A data pull" as milestone 2. But after correction 1.2, the
Tier A pull is one afternoon: download, filter to 15 documents, done. It is not a
milestone, it is a chore. Meanwhile the two things the project actually rests on — the
allowlist and the eval set — need no code at all and gate everything downstream.

**Step 1 — the allowlist. One afternoon, no code.** Open a text file. Write the ~15
documents. For each: the ID, why it is in scope, and the date you verified it is in force
on vbpl.vn. When you can say why each one is there, you have the spine of the project.

**Step 2 — five fact patterns. Not thirty.** Your plan says 30–50. Write **five** first.
Five is enough to discover that your output format is wrong — and it will be wrong the
first time. Thirty written against a wrong schema is thirty thrown away. Expand to 30 in
week five, after the pipeline shape is settled.

**Step 3 — run the pressure-test.** Still not done, and START-HERE calls it non-optional.
I have partly answered question three for you in section 1 — the strongest evidence
against this working is that your headline comparison does not hold. Questions 1, 2 and 4
are still open and you should do them yourself.

Then, and only then, S1 and S2.

**Rough sizing, part-time, solo, honest:**

| Week | What | Ends with |
|---|---|---|
| 1 | S0 allowlist, 5 fact patterns, pressure-test, S1 ingest, S2 force check | The repealed-document test fails the build. Demonstrable |
| 2 | S3 — the hand map plus the resolver | Every ref resolves, or CI is red |
| 3 | S4/S5 retrieval | A measured recall@10 number, reported honestly |
| 4 | S6 judge, S7 validate, negative controls | Criminal fact pattern returns "not found" |
| 5 | Eval set to 30, run S9, write RESULTS.md | Two real numbers, side by side |

Five weeks part-time. Every week ends with something you can show, and if you stop after
week 2 you still have a working, tested, cited artefact — which is more than most solo
projects produce.

**What I would cut from v1 outright:** Tier C court judgments. 955,000 family judgments
are tempting, but you cannot reach the terms of use, "hand-vetted small slice" is a
research project of its own, and nothing in stages S0–S9 needs it. Name it as future work
and move on. Tier B (án lệ) stays, but as ~5–10 rows filtered to this branch inside S0,
not a milestone of its own.

**Also on day one, before any code:** write `DISCLAIMER.md`. Not a footer. A file, in the
repo root, linked from the README, and reproduced on any interface you build. It says this
assembles documents and does not give advice, does not predict outcomes, may be out of
date as of the stamped snapshot, and that án lệ are persuasive guidance rather than
binding precedent. Write it before the code exists, so the code has to live up to it
rather than the other way round.

---

## 7. Two decisions I could not make for you

**Who this is for.** Your brief flags it as undecided and it changes the build. A tool for
someone with legal training can print raw article text and typed relation labels and
assume the reader knows what a thông tư liên tịch is. A tool for a layperson needs
explanation, which means more model-generated prose, which means more surface for exactly
the failure mode you are trying to design out. I would pick the trained reader — it is
safer, it is closer to your own worked example, and it is a defensible portfolio piece.
But it is your call and it should be explicit before you design any interface.

**Whether "conflict detection" stays the headline.** I have argued in section 4 for a
five-way typed label and for making the force check the headline instead. The counter-
argument is that conflict detection is the more novel-sounding claim and novelty is worth
something in a portfolio. My view: the force check is more likely to actually work, is
easier to prove, and is unambiguously absent from the competitors you named. Novelty you
cannot demonstrate is worth less than a plain thing that provably works.

---

## Sources

- [VLegal-Bench: Cognitively Grounded Benchmark for Vietnamese Legal Reasoning of LLMs (arXiv 2512.14554)](https://arxiv.org/html/2512.14554v1)
- [th1nhng0/vietnamese-legal-documents (Hugging Face)](https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents)
- [anhquan12/vietnamese-legal-documents (Hugging Face)](https://huggingface.co/datasets/anhquan12/vietnamese-legal-documents)
- [Gần 2 triệu bản án, quyết định được công bố (Báo Chính phủ, Jan 2026)](https://baochinhphu.vn/gan-2-trieu-ban-an-quyet-dinh-duoc-cong-bo-tren-cong-thong-tin-dien-tu-nganh-toa-an-102260128153545772.htm)
- [Danh sách án lệ có hiệu lực từ 1/7/2026 (CLEAD)](https://clead.vn/blogs/tin-tuc-phap-luat/danh-sach-90-an-le-co-hieu-luc-tu-1-7-2026)
- [Thêm 8 án lệ mới áp dụng từ 01/7/2026 (LSVN)](https://lsvn.vn/them-8-an-le-moi-ap-dung-tu-ngay-01-7-2026-duoc-toa-an-nhan-dan-toi-cao-cong-bo-a174150.html)
- [Nguyên tắc chia tài sản chung của vợ chồng khi ly hôn (Tạp chí Tòa án nhân dân)](https://tapchitoaan.vn/bai-viet/phap-luat/nguyen-tac-chia-tai-san-chung-cua-vo-chong-khi-ly-hon)
- [Luật Hôn nhân gia đình mới nhất 2026 và văn bản hướng dẫn (Thư viện Pháp luật)](https://thuvienphapluat.vn/phap-luat/ho-tro-phap-luat/luat-hon-nhan-gia-dinh-moi-nhat-2026-tong-hop-van-ban-huong-dan-luat-hon-nhan-gia-dinh-moi-nhat-291055-249586.html)
- [AITeamVN/Vietnamese_Embedding (Hugging Face)](https://huggingface.co/AITeamVN/Vietnamese_Embedding)
- [Thẩm quyền Tòa án sau sáp nhập địa giới từ 01/7/2025 (Apolat Legal)](https://apolatlegal.com/jurisdiction-of-peoples-courts-after-administrative-boundary-mergers-as-of-july-1-2025/)

**Not verified — check these yourself before relying on them:**

- `congbobanan.toaan.gov.vn` terms of use and `robots.txt` — both fetches failed from here.
  Open it in a browser before any scraping.
- The exact snapshot date of the Hugging Face dataset — not stated on the dataset card.
  This determines how stale your validity statuses are, which matters after the 2025
  restructuring.
- The án lệ count of 90 — one aggregator page's title and body disagreed with each other.
  Confirm against `anle.toaan.gov.vn` directly and record the date you checked.
