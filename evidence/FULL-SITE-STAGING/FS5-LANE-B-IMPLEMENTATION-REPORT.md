# FS5 Lane B implementation report — WorkGraph, Build, Trust

Date: 3 September 2026  
Writer: Claude Code (Fable 5.1), Lane B under `FS5-LANE-B-CLAUDE-WRITER.md`  
State: source complete for the nine owned route files; nothing assembled,
committed, pushed, deployed or published  
Authority read in full: `CLAUDE.md`; the Fable plan §4, 5, 7, 8.2, 8.4, 9.3,
9.4, 9.5, 10, 12; `FS5-DRAFT-ROUTE-SPECIFICITY-AND-EXECUTION-PROOF.md`;
`FULL-SITE-CONTENT-CONTRACT.md`; `COPY-UNIT-MANIFEST.json`;
`EVIDENCE-LEDGER.md`; the WorkGraph, Build and Trust page maps;
`IMAGE-LIBRARY-CATALOG.md`; `ASSET-REGISTRY.json`; slot manifests
`workgraph.json` and `build.json`; `P4R4-CHRISTIAN-AUTHORITATIVE-ADDENDUM.md`;
`P4R5B-COMPONENT-INTELLIGENCE-REVISION.md`; the three authority PDFs
(`Dagg-Image-Language-System.pdf`, `Dagg-Design-System-Foundations.pdf`,
`Dagg-Component-and-Interaction-Library.pdf`, hashes verified against
`CLAUDE.md`); `FS5-VISUAL-PAIR-REVIEW-PROTOCOL.md`; the runner
`tools/capture_fs5_evidence.py` and `tests/test_fs5_candidate.py` as the
measurement contract.

Authority hashes at implementation time (recomputed, match the manifest):

- content contract `c7068104a28fa6a2e6f104daecbdec8410ec5c719fcf00f55f47432ed03a07dc`
- copy-unit manifest `c6c8c2f227588bc9ee2ae050423e3a009ad656b8d34d6050623e223c77302f82`
- Fable plan `730bcdb35b28613c03b01044cfac91d585dea20baa478da1ce1f20aea5f0dc60`

## 1. Failures, holds and deviations first

1. **Expected assembler failure.** `node tools/build_golden_standard_previews.mjs --check`
   reports one failure, `outputs-stale`, for every route and direction
   output plus the build manifest. Lane B edited WorkGraph, Build and Trust
   source without assembling; Lane A and Lane C source changes also predate
   this run. All six other checks pass (shared-hash equality, local refs,
   no inline vector markup, no text-symbol icons, no-JS completeness, no
   copied shared DOM).
2. **Route root placement (deviation, needs a one-line Codex decision).** The
   package says the single WorkGraph `<main>` carries both `[data-workgraph]`
   and `[data-workgraph-page]`. The assembler writes `<main>` hooks only from
   `routes/workgraph/src/meta.json`, which Lane B does not own. Lane B placed
   `data-workgraph` on the body wrapper `<div class="workgraph" data-workgraph>`
   (the same pattern Lane A uses for `[data-home]`), so the manifest route
   root, `routeOf()` and every copy scope resolve; `<main>` still carries
   `data-workgraph-page` from the existing meta.json. If Codex wants both
   hooks on `<main>`, the smallest correction is
   `"mainDataHooks": ["data-workgraph", "data-workgraph-page"]` in meta.json
   and removal of the wrapper attribute; either form keeps exactly one route
   root.
3. **Not proven before assembly (no browser run is authorised for this lane).**
   All rendered claims below are source-level. Specifically unproven:
   first-viewport geometry at 1440×900, 1024×768 and 390×844; the WorkGraph
   lifecycle carrier hitting connect/decide/build/learn at the runner's four
   scroll positions (row heights were sized analytically for a 900 px
   viewport, see §4); the 232 px minimum track that keeps the compact
   sticky record card above the steps below 1180 px; Factory pass timing
   (unchanged FS2 constants 880/950 ms wide, 580/650 ms narrow, five
   intervals ≈ 6.3 s wide); axe results for `role="group"` labels; line
   counts and 200 % reflow.
4. **Static word counts are an approximation of the runner's rendered count.**
   They honour closed `<details>`, `hidden` and `aria-hidden` and treat the
   JavaScript-only lens and plan-selector controls as rendered. The Factory
   status line is progressive scope and changes during the pass, so the
   rendered progressive figure will vary by a few words.
5. **Build default-visible copy sits exactly at the ceiling.** 533 of 535
   words. No default-scope text may be added anywhere on Build.
6. **Rejected approach recorded, not applied.** `/tmp` could not be written
   in this session (outside allowed paths), so the reconciliation script ran
   inline via `python3 -`; no file was created outside Lane B ownership.

Deviations from the package other than item 2: none found.

## 2. Files changed (exactly the owned set)

| File | Why |
|---|---|
| `preview/golden-standard/routes/workgraph/src/body.html` | Recomposed Position as proposition + coded WG-034 record (disclosure, provenance, identity, Decision/Owner/Permission default rows, `Provenance and history` disclosure with Evidence, Operating state, Reason, Provenance, History); index band moved inside `position`; Context now carries WG-DF-OE-01; lifecycle paragraph two and four descriptions moved under `Why the record persists`; carrier reduced to identity, single state line and invariants; every text node keyed to the manifest. |
| `preview/golden-standard/routes/workgraph/src/direction.css` | 5/7 hero grid with actions placed by grid (no `order`), 14 px Ink instrument, JS-only lenses, Context settle, lifecycle geometry (30/54/58/33 vh rows at ≥1180×720; compact sticky card via a 232 px minimum track below 1180), 7/5 control split with the boundary beside the reasoning, 5/7 close. |
| `preview/golden-standard/routes/workgraph/src/direction.js` | Context settle starts on section entry; lens status and `data-copy-state` change only after a real selection (Meeting authored in HTML); lifecycle carrier writes the single state line and `data-copy-state`; reduced motion / missing observer resolve on Learn. |
| `preview/golden-standard/routes/build/src/body.html` | Removed the hero `<picture>` (B-OE-MS-01 no longer loads); added the static five-row opening stage with the five named row hooks and the disclosure above it; Factory identity is one contiguous default unit; plan selectors, plan details, six-stage pass, status and controls keyed; `One governed capability, two surfaces` is copy-only; Pause/Replay/Inspect authored `hidden`; numerals removed from DOM. |
| `preview/golden-standard/routes/build/src/direction.css` | 5/7 Paper opening with coral rule on Approved intervention and sage on Review state; CSS counters for stage numerals; Factory workspace grid; one restrained Machine Signal bar inside the pass; reduced-motion zeroing. |
| `preview/golden-standard/routes/build/src/direction.js` | Dropped the hero settle; status copy and `data-copy-state` now follow the manifest enum (initial, intervention, specification, architecture, build, evaluation, paused, resolved); Inspect shown only for reduced motion / missing observer; focus suspension limited to interactive descendants; unselected plan gets `aria-hidden`. |
| `preview/golden-standard/routes/trust/src/body.html` | Added the six `data-trust-section` anchors; control-path band recomposed with `01 Action withheld`, `02 Permission`, `03 Accountable owner`, provenance `Constructed control path` and the sole state `Human decision recorded. Release withheld.`; removed `aria-label="Illustrative control path"`, `Authority resolved` and `aria-live`; permission field values now lower-case exact copy; record disclosure summary split into the two keyed units. |
| `preview/golden-standard/routes/trust/src/direction.css` | Band as a 14 px Ink instrument (coral rule at 01, sage at 03), settle keyed to `data-trust-ready`, 5/7 models and diligence grids with grid placement. |
| `preview/golden-standard/routes/trust/src/direction.js` | Settle starts only when the band enters view; reduced motion or missing observer resolve immediately. |
| `evidence/FULL-SITE-STAGING/FS5-LANE-B-IMPLEMENTATION-REPORT.md` | This report. |

No other file was touched. Protected hashes for the contract, manifest and
plan match the manifest's `authorityHashes` (see header).

## 3. Source-level reconciliation results

Method: an inline Python emulation of the runner's copy rules over each
`body.html` (comments stripped): every text node must have exactly one
nearest `data-copy-ref`; unit text is the newline join of descendant text
nodes; kind, scope and nearest section anchor must match; accessible
attributes need an accessible-attribute owner; visible-text units may nest
only under accessible-attribute owners; multiplicity must match; ids unique;
no heading skips.

| Route | Section anchors in DOM order | Units reconciled | Uncovered text / accessible strings | Nested-ref violations |
|---|---|---|---|---|
| WorkGraph | position, record, lifecycle, control, close | 29 / 29 | 0 / 0 | 0 |
| Build | position, modes, factory, trust, operate | 31 / 31 | 0 / 0 | 0 (three found and fixed: the `Constructed build plans` group now holds only the two selectors) |
| Trust | position, control-path, permission, record, models, diligence | 19 / 19 | 0 / 0 | 0 |

Every `exactStates` unit is authored with a valid `data-copy-state`:
WorkGraph lens status `meeting`, carrier state `learn`; Build pause toggle
`pause`, sequence status `resolved` (JavaScript sets `initial` once it owns
the pass). `node --check` passes for all three scripts.

## 4. Copy counts (static, §10.4 method)

| Route | Default | Band | Progressive (rendered, JS on) | Ceiling | First section | Band |
|---|---:|---|---:|---|---:|---|
| WorkGraph | 367 | 320–430 | 13 | 320 | 106 | 95–115 |
| Build | 533 | 360–535 | 178 | 360 | 118 | 110–125 |
| Trust | 385 | 300–420 | 0 | 320 | 44 | 30–50 |

Cross-check: summing the manifest's own default `exactText` units gives
365 / 533 / 385; WorkGraph's extra two rendered words are the single
`exactStates` carrier line, which the manifest sum excludes.

## 5. Package rules, checked at source

- Route roots `[data-workgraph]`, `[data-build]`, `[data-trust]` present once
  each; all listed WorkGraph, Build and Trust hooks present, including
  `[data-workgraph-record-field="owner"|"permission"]` on default rows, the
  five ordered `[data-build-opening-stage-row]` values inside one
  `[data-build-opening-stage]`, `[data-trust-control]` once on the band.
- `workgraph.control.narrative` is one contiguous subtree (H2, paragraph,
  boundary) rendered through `display: contents`.
- No CSS `order` anywhere in the three stylesheets (a grep for `order:`
  matches only `border:` declarations); reading order is identical at every
  width, and grid placement only moves the hero actions, the lifecycle card,
  the control boundary and the close lead.
- WorkGraph: disclosure precedes the record; the bitmap loads only in
  Context via `[data-workgraph-context-picture]` with desktop 1568×1003 and
  portrait 1122×1402 sources; Meeting is pressed in source with the exact
  static status; the lifecycle authored state is resolved (`Evidenced /
  Learn`, mode `resolved`) so no-JS, reduced motion and a missing observer
  read the same truth; no Machine Signal, icon row or node graph.
- Build: no `<img>`/`<picture>` and no B-OE-MS-01 reference in source; the
  stage is static `<dl>` text; two plans with both resolved-state lines in
  the default path; no toggle, panel or prompt surface for the two-surfaces
  copy; true no-JS status reads `Governed review complete`, six stages in
  order, all three playback controls `hidden`; Impact link absent.
- Trust: copy-first opening, then the band with action withheld, permission
  and accountable owner visible without disclosure; stale label and
  `Authority resolved` removed; single state string; settle starts on band
  entry, resolves immediately under reduced motion or without an observer,
  and CSS shows the resolved band without `.cl-enhanced`; OR-021 keeps
  page disclosure before its identifier and local provenance.
- Icons: zero on all three routes; disclosures use native markers.
- Colour: coral only at judgment (WorkGraph Decision row and Decide state,
  Build Approved intervention and Intervention hold, Trust Action withheld,
  rebuild-mode mark); sage only at permission, verification and resolved
  states.

## 6. Lifecycle carrier geometry rationale (unproven until assembly)

The runner samples the WorkGraph state at scroll offsets `(H − 0.4V)·i/3`
and `(H − V)·i/3` inside the lifecycle section and expects Connect, Decide,
Build, Learn in turn, while the carrier logic keeps the accepted 45 % focus
line. Solving both lanes at 1440×900 requires the section to exceed roughly
2,000 px and the Learn row plus trailing content to exceed 495 px. The
stylesheet therefore sets 30 / 54 / 58 / 33 vh row minimums at ≥1180×720,
a 64 px section padding-bottom and the disclosure and link after the steps.
Slack against the derived bounds is 50–130 px depending on intro wrap. If
the assembled run misses a state, adjust only those four `min-height`
values; no copy or hook change is needed.

## 7. What remains for Codex

1. Decide item 2 (route root on `<main>` via meta.json, or keep the wrapper).
2. Assemble once, freeze the snapshot and run the FS5 runner; the items in
   §1.3 are the first things to read in `route-matrix.json`,
   `interactions.json` and `resilience.json`.
3. Independent Fable acceptance against the promoted package.

Nothing was assembled, committed, pushed, deployed or published.
