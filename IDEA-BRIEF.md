# Idea brief — property-division document/conflict assistant

**Paste this at the start of the next session, alongside START-HERE-Kenny.md, to continue from here.**

---

## The idea, one paragraph

A tool scoped to one narrow branch of Vietnamese family law — property division in
divorce (`chia tài sản khi ly dị`) — that takes a fact pattern and produces the
complete, correctly-cited stack of governing documents (base law article, every
decree/circular that implements it, relevant án lệ or court decisions), flags
whether any of those documents genuinely conflict, and stops there. It never tells
anyone what should happen to them. It is an automated version of "assemble
everything you'd need to read before you could even attempt this," not a chatbot
that answers questions.

## Why this branch, specifically

- It is Kenny's own worked example from law school: the base law
  (Luật Hôn nhân và Gia đình / Luật Dân sự) alone cannot answer the question —
  you need the implementing decrees/circulars too.
- It is one of the domains the VLegal-Bench benchmark paper's own data collection
  named ("marriage and family"), but that paper never tested a single-branch,
  specialized approach — it only tested general-purpose, all-of-Vietnamese-law
  models. That gap is the novelty.
- It sits entirely outside what already exists:
  - DVC AI (government) covers 15 services, all civil registration/welfare
    paperwork (birth, marriage, death registration, welfare certifications) —
    zero dispute-type procedures.
  - The Ministry of Justice's "AI Luật" chatbot and commercial competitors
    (ailuat.luatvietnam.vn, trolyluat.ai.vn, vnptai.io) all explicitly limit
    themselves to general Q&A with citations, not situation-specific advice.
  - DoNotPay was fined $193K by the FTC (Feb 2025) for claiming AI-lawyer-level
    performance it never substantiated — the cautionary tale for the "just give
    advice" version of this idea.

## What the AI/LLM actually does — and does not do

Same split as ReefCommand: exactly one component is allowed to use judgment;
everything else is rules and lookups.

**Deterministic (code, not model):**
- Pull the base article + every decree/circular that amends or implements it,
  using the citation-relationship graph already available in the vbpl.vn
  dataset (~898K relationship entries: citations, amendments, repeals).
- Validate every citation shown actually resolves to a real document ID before
  it's displayed — fails loudly if not (the DATA-08 pattern).

**Model (the one bounded judgment call):**
- Given the graph-filtered candidate set, score which legal issues the fact
  pattern actually raises (support scores per issue, not one confident answer
  — same shape as ReefCommand's four independently-scored causes).
- For document pairs the graph has already flagged as related, judge whether
  they actually conflict in meaning. The model is never asked to search for
  conflicts across the whole corpus freely — only to judge pairs a deterministic
  lookup already identified as connected.

## Case law sources, kept honestly separate

- **Án lệ** (72 currently in effect): officially selected by the Supreme
  People's Court, persuasive guidance — courts are expected to study and apply
  them, but they are **not strictly binding**, unlike common-law precedent.
  Label this distinction explicitly in any output.
- **Full-text judgments** from `congbobanan.toaan.gov.vn`: much larger pool,
  but data quality/completeness as of today (2026) is unverified — the only
  detailed account found was from the portal's first year (2018), when only
  ~1/5 of judgments were actually being published. Check current state before
  relying on it; use a small, hand-vetted slice rather than assuming bulk
  quality.

## What this refuses to do (non-negotiable)

- No advice on what a specific person should do about their situation.
- No drafting of anything meant to actually be filed or signed.
- No prediction of how a court or official would rule.
- No answer at all when the corpus doesn't actually support one — must say
  "not found," never fall back on the model's parametric memory.

## How to know it actually works

Build a small hand-checked test set (~30-50 fact patterns, verified using
Kenny's own legal training) within this one branch. Measure accuracy on:
1. Article/document-set prediction
2. Conflict detection between flagged-related provisions

...against a plain "just ask a general LLM" baseline. VLegal-Bench found the
best general model hit only 43.83% on article prediction, and 16 of 23 models
scored 0.00 on conflict detection (defaulted to "no conflict" every time). Beating
that baseline on this narrow slice, even modestly, is a specific, defensible
result — not a vibe-based demo.

## Still open — not decided yet

- **Who this is ultimately for.** Currently shaped as a study/verification tool
  for someone with legal training (a law student, a junior lawyer — or Kenny
  himself) rather than a layperson product. Fine for a portfolio piece, but
  worth deciding explicitly before scoping the interface.
- **How far to push the model side.** Tier A (retrieval + bounded judgment,
  no training) is buildable in weeks. Tier B (actually fine-tuning a small
  model, e.g. LoRA on an open Vietnamese base model, on this branch's corpus)
  is a genuine stretch goal for later, once Tier A is working and measured —
  not something to attempt on day one alongside everything else that's new.

## Not yet done

- Pressure-test skill (the four questions: what is this *not*, who'd object,
  what's the evidence against it working, which checks fail loudly vs silently)
  has not been formally run yet.
- No repo, no code, no architecture decisions made.
- Next real step, when Kenny is ready: run the pressure-test, then size a
  first milestone small enough to actually finish.
