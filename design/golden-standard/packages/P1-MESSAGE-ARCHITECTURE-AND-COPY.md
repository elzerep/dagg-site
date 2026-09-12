# P1 · Message architecture and final copy

Status: accepted P1R1 by Codex
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Revision base commit: `b03ca11e7b6098ea67fae342e2db65bec8ee8190`
Gate type: operating acceptance by Codex

## 1. Objective

Freeze the homepage argument, supporting-page roles, evidence boundaries and visible copy for the direction slice before visual design begins. Claude must not invent positioning or prose while designing P4.

## 2. Final copy

Use `../narrative/VERTICAL-SLICE-COPY.md` verbatim in every direction. Layout may change; wording may not. If copy cannot fit a materially superior composition, report the exact collision to Codex instead of rewriting.

## 3. Authoritative inputs

- `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
- `../reference-audits/ANTHROPIC-OPENAI-RECIPE.md`
- `../reference-audits/PALANTIR-RECIPE.md`
- `../reference-audits/xai-current/XAI-CURRENT-AUDIT.md`
- `../narrative/HOMEPAGE-MESSAGE-ARCHITECTURE.md`
- `../narrative/PAGE-BRIEFS.md`
- `../narrative/EVIDENCE-LEDGER.md`
- `../narrative/VERTICAL-SLICE-COPY.md`

## 4. Files owned by P1

- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md` — package sequence only.
- `design/golden-standard/narrative/HOMEPAGE-MESSAGE-ARCHITECTURE.md`
- `design/golden-standard/narrative/PAGE-BRIEFS.md`
- `design/golden-standard/narrative/EVIDENCE-LEDGER.md`
- `design/golden-standard/narrative/VERTICAL-SLICE-COPY.md`
- `design/golden-standard/packages/P1-MESSAGE-ARCHITECTURE-AND-COPY.md`
- `tools/check_p1_copy.py`
- `evidence/P1R1/copy-check.json`

## 5. Immutable decisions

- Homepage is the executive memo, not the Transformation page.
- Primary navigation: `Transformation · WorkGraph · Build · Impact · Company · Start an assessment`.
- WorkGraph remains top-level and central, but is not the entire company story.
- Dagg Factory is the lead mechanism under Build.
- Operate remains under Build and may not imply current `Systems operated` evidence.
- Aloi appears under Impact, not as a named homepage feature.
- Image language is abstract-first and must not use generated workshop people.
- No circuit-board, node-cloud, terminal-wall or slide-deck aesthetic.
- No unsupported claims, fabricated product states or customer-like synthetic data.

## 6. Deliverables

- Accepted message architecture.
- Accepted route-level page briefs.
- Accepted evidence ledger and provenance labels.
- Final visible copy for the complete P4 vertical slice.
- Machine-readable copy-budget and narrative-integrity report.
- Updated package sequence placing narrative before foundations and design directions.

## 7. Acceptance tests

- The H1 explains the company transition without making WorkGraph the company promise.
- The complete slice moves consequence → decision → context → build/control → assessment.
- The same constructed `Supplier payment exception` appears in the hero, WorkGraph, Factory bill of materials and operating record without changing its owner, evidence, permission or outcome.
- Preserve, simplify, automate, rebuild and retire each have distinct selection and refusal logic.
- WorkGraph visibly connects strategy, Factory and later operating decisions.
- The hero uses one bounded lifecycle demonstration with pause/replay; WorkGraph owns manual lifecycle inspection and does not repeat the hero as five tabs.
- The operating record includes a boundary stop, accountable human decision and way back.
- The hero carries the one exact shared page disclosure and every constructed artifact has its exact local provenance label.
- Only the hero and assessment close use button-level CTAs; supporting-route actions are contextual text links.
- No named client, invented metric, `LIVE`, `Systems operated`, `10x`, `100x`, `1000x` or `fully autonomous` claim appears.
- Every route has one question, decision, dominant object, semantic motion, boundary and next action.
- H1 is 6–12 words; each homepage H2 is 4–9 words; leads are 18–32 words and body paragraphs are 20–45 words unless an artifact state requires less.
- Default visible copy is 600–800 words; all interactive states combined are no more than 1,100 words.
- The page expresses both compounding loops without implying that client-specific context crosses customer boundaries.
- A design implementer can build the P4 slice without writing new visible copy.

## 8. Stop condition

Do not begin P2/P3/P4 from legacy copy. The four files under `narrative/` are the source of truth. A later copy change requires a new Codex decision and a recorded revision here.

## 9. Prior acceptance record

Accepted by Codex on 2026-08-30 after three independent red-team passes:

- Anthropic/OpenAI narrative and copy gate: PASS.
- Palantir evidence, provenance and control gate: PASS.
- xAI/SpaceXAI page-role and motion gate: PASS.

Mechanical checks:

- H1: 14 words.
- Primary button actions: 2, hero and assessment only.
- Contextual supporting-page links: 4.
- Full constructed-example disclosures: 4, one at every artifact.
- Five decision outcomes: one unique state each.
- Final copy including all interactive states: 1,342 words, below the 1,450-word ceiling.
- Forbidden public claims in final copy: 0.
- Markdown whitespace errors: 0.

This record applies to the original P1 revision. It was reopened after the company story, execution edge, two compounding loops and public copy ceilings were sharpened. The revised acceptance record must be generated from `tools/check_p1_copy.py`; the old counts are not current gates.

## 10. Revision acceptance record

Accepted by Codex on 2026-08-30 after three independent revision passes:

- Anthropic/OpenAI narrative and compression gate: PASS.
- Palantir mechanism, provenance and control gate: PASS after two correction rounds.
- xAI/SpaceXAI consequence, motion and progressive-state gate: PASS.

Mechanical gate from `evidence/P1R1/copy-check.json`:

- Status: PASS, 17/17 checks.
- Source SHA-256: `4189196a5418e9b8e941ea3a26ffe949783c093c94ce941ea49c42470d3ca042`.
- Checker SHA-256: `77dc5dd6169ade4ea37048beebcb0bd086b007579ae73edc9b337d878e3491ce`.
- H1: 12 words; H2s: 7–9 words; body blocks: 21–45 words.
- Default visible copy: 784 words.
- All interactive states: 1,098 words.
- Shared page disclosures: 1, located in the hero; all four local provenance checks pass.
- WorkGraph record schema and both Factory modes are complete.
- Canonical payment-draft state, human decision and concrete way back are checker-enforced.
- Forbidden public claims: 0.

P1R1 is frozen for P4. A design collision must be reported; it does not authorize copy invention.
