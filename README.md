# vn-property-division

Assembles the stack of Vietnamese law governing a **property-division on divorce**
(`chia tài sản chung của vợ chồng khi ly hôn`) fact pattern, and labels each
citation with whether it was in force **at the time the facts happened**.

It assembles documents. **It does not give advice** — see [DISCLAIMER.md](DISCLAIMER.md).

## Status

Data layer built and verified. **The system itself is not built yet** — there is
no path from a fact pattern to an answer.

| Stage | State |
|---|---|
| Allowlist (27 documents, ranked by legal force) | done |
| Corpus (22 full texts) | done — 21/22 verified against hand-counted articles |
| Relationship graph + direction model | done |
| Effectiveness check (temporal) | done |
| Eval set (6 fact patterns from real judgments) | done |
| Baseline measured | done — 55% |
| Retrieval | **not built** |
| The one model step | **not built** |
| Validation layer | **not built** |
| Output assembly | **not built** |

## Layout

```
data/
  allowlist.csv          the ONLY documents that may ever be cited
  article_relations.csv  article-to-article map (hand-built)
  article_status.csv     which articles are dead, and since when
  HIERARCHY.md           legal force ranking + Điều 58 conflict rules
  raw/content/           22 full texts
eval/
  fact_patterns.csv      6 cases, 4 from real judgments
  expected_citations.csv ground truth = what the courts actually cited
  RESULTS-baseline.md    the 55% number and how it was reached
src/                     pull + check scripts, force_check, graph
tests/                   18 tests, 13 of them negative controls
memory/                  one short file per working day
```

## Design rules

1. **Exactly one file may call a model.** Everything else is rules and lookups.
2. **The model selects from `allowlist.csv`. It can never add to it.**
3. **Every check must be able to fail loudly, and must have a test proving it does.**
4. **`data/eval/` is ground truth.** No model writes into it.

## Setup

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```
