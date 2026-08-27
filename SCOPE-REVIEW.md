# Scope review — 23/08/2026

Kenny asked: *are we still in the original scope, and if not, what are we now?*

## The original, from IDEA-BRIEF

> "takes a fact pattern and produces the complete, correctly-cited stack of
> governing documents ... flags whether any of those documents genuinely
> conflict, and stops there."

Three parts: **assemble**, **flag conflicts**, **refuse to advise**.

## What actually happened to each

| Part | State |
|---|---|
| **Assemble the document stack** | Intact. Every piece built serves it. Not yet running end to end. |
| **Flag conflicts** | **Shrank, and nobody decided to shrink it.** |
| **Refuse to advise** | Intact and now stronger — FP06 tests it, and the baseline fails it. |

## The one real drift: conflict detection

IDEA-BRIEF made conflict detection the novelty, citing VLegal-Bench. Two findings
undercut that, and the project quietly moved without a decision:

1. **Điều 58 Luật Ban hành VBQPPL makes conflict RESOLUTION arithmetic.** Higher
   rank wins; same body, later date wins. That was going to be a model job. It is
   now `resolve()` — a few lines of code. Good news, but it means the model's role
   shrank to "do these two provisions actually say different things?"
2. **The three real defects we found in Tạp chí Tòa án are not conflicts** — one
   timing contradiction, one scope gap, one vague criterion. Printing "CONFLICT"
   for those would be wrong.

Meanwhile something else grew into the gap: **temporal correctness**. Not planned.
It emerged because the data made it cheap (`tinh_trang_hieu_luc`, dates,
amendment edges) and the eval set made it interesting (a 2024 judgment correctly
citing 2000 law).

## So what are we now

**The product is unchanged. The differentiator moved.**

> A tool that assembles the complete, correctly-cited stack of Vietnamese law
> governing a property-division fact pattern — and, unlike anything else
> available, tells you for each citation whether it was in force **at the time
> the facts happened**, not merely today.

That is not straying. That is finding the edge. But it should be **named on
purpose**, not inherited from a side remark of mine — so IDEA-BRIEF needs
updating to say it.

## Honest cost of the drift

- The VLegal-Bench framing in IDEA-BRIEF is now **doubly wrong**: wrong because
  the task is not comparable, and wrong because conflict detection is no longer
  the headline.
- `article_relations.csv` has a `tension` relation type that nothing uses yet.
- The five-way label (`CONFLICT / AMBIGUITY / GAP / OVERLAP / NO_ISSUE`) is
  designed and unbuilt. Keep it — it is honest — but it is no longer the pitch.

## The bigger risk, which is not drift

Ten scripts, all data. **Zero lines that turn a fact pattern into an answer.**
The corpus, the graph, the eval set and the baseline all exist to serve a system
that does not exist. Every further week on data raises the chance the system
never gets built.

## Decisions needed from Kenny

1. **Confirm the restated identity above**, and I rewrite IDEA-BRIEF to match.
2. **Confirm conflict detection drops from headline to secondary feature** —
   still built, no longer the claim.
3. **Next: thin end-to-end path, even if the output is bad.**
   `tình huống → BM25 → mở rộng theo đồ thị → dán nhãn hiệu lực → in ra`,
   measured on the 6 patterns. A bad working system beats a perfect dataset.
