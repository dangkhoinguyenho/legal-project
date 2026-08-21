# Data-gathering & build plan

**Paste this into the new Cowork session (with Opus) alongside START-HERE-Kenny.md
and IDEA-BRIEF.md. This plan was written by Sonnet after a long discussion — the
new session won't remember any of that discussion, so everything it needs is
here.**

---

## 0. Before touching any code — two decisions the new session must make with Kenny

**0a. Confirm the branch.** The idea works for any narrow branch of Vietnamese
law — the plan below uses **property division in divorce** (`chia tài sản khi
ly dị`) as the worked example throughout, because it's the most-researched
option so far. Kenny also raised **commercial law** as an alternative. Quick
honest recap for whoever picks this up: commercial/contract law is the most
crowded corner of the market already (Harvey, Spellbook, Luminance all live
there, built for big companies); family-law disputes had almost nobody
building for them. Neither is wrong — just confirm the choice explicitly
before step 1, because it changes which documents get filtered out of the
corpus in step 2.

**0b. Run the pressure-test skill** (it's in Kenny's available skills) on the
chosen branch before writing any code. START-HERE-Kenny.md calls this
non-optional. Four questions: what is this *not*, who'd object and why, what's
the evidence against it working, which checks fail loud vs. silent.

---

## 1. What data this project actually needs

Three tiers, in order of how much manual care each one needs:

| Tier | What | Size | Effort |
|---|---|---|---|
| A | Base law + implementing decrees/circulars | Large but already scraped by someone else | Filter, don't re-scrape |
| B | Án lệ (official precedents) | Tiny — 72 total | Careful manual/light-script collection |
| C | Full-text court judgments | Potentially large, quality unverified | Small hand-vetted subset only |

### Tier A — base law + decrees/circulars

Don't scrape vbpl.vn from scratch. Someone already did it:

- **Dataset:** `anhquan12/vietnamese-legal-documents` on Hugging Face. 153,420
  metadata records, 178,665 full-text documents, 897,890 relationship entries
  (citations / amendments / repeals). Source: vbpl.vn (Ministry of Justice's
  official portal). Documents are public domain; the compiled dataset is
  CC BY 4.0.
- Two similarly-named datasets exist (`vohuutridung/vietnamese-legal-documents`,
  `minhdoan17/vietnamese-legal-documents`) — worth comparing row counts and
  recency before committing to one. Community-scraped data varies in quality.
- **Steps:**
  1. Download via the `datasets` Python library or direct HF file download.
  2. Filter to the chosen branch using the legal-sector metadata field, or by
     keyword match on title/full text (e.g. "hôn nhân và gia đình" for family
     law; "thương mại", "doanh nghiệp" for commercial).
  3. Use the relationships table to build, for every base article in scope,
     the full chain of decrees/circulars that amend or implement it. This
     chain *is* the "graph" the rest of the system leans on.
  4. **Verify before trusting at scale**: hand-check 10-20 relationships
     Kenny already knows the answer to, from his own legal training. This is
     the same move that caught the reef-hours bug in ReefCommand — a data
     source is not trustworthy until someone who knows the domain has checked
     a sample of it.

### Tier B — án lệ (official precedents)

- 72 currently in effect (verify current count — it changes over time; one
  source already found 91 in effect as of mid-2026, so recheck at build time).
- Source: thuvienphapluat.vn's án lệ index, or the Supreme People's Court's
  own án lệ portal.
- For each one, capture: number, the underlying case, the issuing decision
  date, and — most important — the extracted legal principle ("nội dung án
  lệ"), plus which base article it relates to.
- Filter to the chosen branch. Small enough (dozens, not thousands) to do
  carefully by hand or with a light script, not a scraping project.
- Label these explicitly as **persuasive, not binding** everywhere they
  appear in the system's output — this distinction matters and a generic
  tool would get it wrong.

### Tier C — full-text court judgments

- Source: `congbobanan.toaan.gov.vn`, the official judgment-publication
  portal.
- **Do not assume this is a clean, complete dataset.** The only detailed
  account found of its real-world state is from 2018 (its first year), when
  only about 1/5 of judgments were actually being published, and digitizing
  one judgment reportedly took a clerk a full workday. That's 8 years old —
  it may be much better now, or it may not be. First move: go check the
  portal's current scale and searchability directly, and check its terms of
  use/robots.txt before scraping anything.
- Given that uncertainty, plan for a **small, hand-vetted set** (dozens, not
  an attempted bulk ingest) for the chosen branch — quality over volume.
- Backup/comparison source: luatvietnam.vn has its own "bản án" section,
  worth checking as a possibly cleaner alternative.

---

## 2. The evaluation set — this is Kenny's task, not the AI's

Build 30-50 fact patterns in the chosen branch, each with a known-correct
answer (which articles/decrees/án lệ apply; whether anything conflicts),
verified using Kenny's own legal training — not generated by AI and not
"looks right." This is ground truth. A simple spreadsheet is enough:

`fact_pattern | expected_documents | expected_conflicts | notes`

This one is explicitly not something to delegate — the value of the whole
evaluation later depends on this being genuinely correct, checked by someone
who actually knows the law, the same way Kenny's own legal-training edge
caught the impossible dive-hours number in ReefCommand.

---

## 3. System architecture (for Opus to implement)

Same split discussed at length in this session: one bounded model judgment,
everything else deterministic.

1. **Ingest & structure** the branch-scoped corpus from Tier A/B/C into a
   simple local store (a folder of structured JSON is enough for v1; no need
   for heavy infrastructure yet).
2. **Deterministic graph lookup**: given a base article, return everything
   that amends/implements/references it, straight from the Tier A
   relationships table. No model involved.
3. **Retrieval**: given a fact pattern (plain-language input), retrieve
   candidate relevant base articles — embeddings + keyword search is enough
   for v1, doesn't need to be sophisticated yet.
4. **The one bounded model step**: given the retrieved candidates and their
   graph-connected documents, the model scores which legal issues the fact
   pattern raises, and — only for document pairs the graph has already
   flagged as related — judges whether they actually conflict. Explicit
   instruction to the model: cite only documents present in context, never
   invent, and say "not found" rather than guess.
5. **Validation layer**: before anything is shown, check every citation
   resolves to a real document ID in the corpus. Fail loudly if not — this is
   the DATA-08 pattern from ReefCommand, applied here.
6. **Evaluation**: run the hand-built test set from step 2 through (a) a
   plain "just ask a general LLM" baseline and (b) this system. Report
   accuracy on article/document prediction and conflict detection for both,
   honestly — including if the system doesn't beat the baseline yet.

---

## 4. Suggested milestone order

1. Confirm branch + run pressure-test (section 0)
2. Tier A data pull + verification sample (section 1)
3. Tier B án lệ collection for the branch (section 1)
4. Check Tier C portal's current real-world state; pull small vetted set only
   if it's viable (section 1)
5. Kenny builds the hand-checked eval set, in parallel with 2-4 (section 2)
6. Build deterministic graph lookup + retrieval (architecture steps 1-3)
7. Build the one bounded model step (architecture step 4)
8. Build the validation layer (architecture step 5)
9. Run baseline vs. system on the eval set, report the real numbers
   (architecture step 6)

Each milestone should produce something checkable before moving to the next
— don't build 3 through 9 before confirming 1 and 2 are actually solid, the
same "wrong five-line plan is cheap, wrong 200-line file is expensive"
principle from Kenny's own rules.

---

## 5. What NOT to do

- Don't bulk-scrape congbobanan.toaan.gov.vn before checking its current
  state and terms of use.
- Don't skip the hand-verification step on Tier A — an unverified data source
  is worse than no data source, because it fails silently.
- Don't let the model touch the eval set's ground truth — that has to come
  from Kenny.
- Don't expand past one branch until the first one is measured and working.
