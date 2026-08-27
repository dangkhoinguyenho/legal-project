# Disclaimer

**This tool does not give legal advice. Read this before using anything it produces.**

## What it does

Given a description of a property-division situation (`chia tài sản chung của vợ
chồng`), it assembles the stack of Vietnamese legal documents that govern that
kind of situation, and labels each citation with whether that document was in
force **at the time the facts happened**.

## What it does not do, and will not do

- **It does not tell you what to do about your situation.** It is not advice.
- **It does not predict how a court or official will decide.** No such feature exists.
- **It does not draft anything to be filed or signed.**
- **It does not answer when the corpus does not support an answer.** It says
  "not found" rather than guessing. That is deliberate.

## Known limits, stated plainly

- **The corpus is a fixed list of documents.** Anything outside that list cannot
  be cited, however relevant. The list is in `data/allowlist.csv`.
- **Luật Đất đai 2024 is missing its full text.** The source dataset has an empty
  record. Land questions are therefore incompletely grounded.
- **The data snapshot ends around May–June 2026.** Anything issued after that is
  absent.
- **Nine of twenty-two documents are `hết hiệu lực một phần`** — partially expired.
  For most of them the data does not say which articles died. Where we know, it is
  recorded in `data/article_status.csv`; where we do not, the output says so.
- **`án lệ` are not `văn bản quy phạm pháp luật`.** Under Nghị quyết
  04/2019/NQ-HĐTP Điều 8 judges must study and apply them where the legal situation
  is similar, and under Điều 9 an án lệ is automatically annulled when a change in
  law makes it inappropriate. They are labelled separately in any output.
- **`công văn` are not `văn bản quy phạm pháp luật` at all** and cannot be the
  legal basis of a decision.
- **`văn bản hợp nhất` may be cited as of 01/07/2026** (Pháp lệnh 01/2026/UBTVQH16),
  but where a consolidated text differs from its source documents, **the source
  documents prevail**.

## If this matters to you

Talk to a qualified Vietnamese lawyer. This tool exists to shorten the reading
list, not to replace the reader.
