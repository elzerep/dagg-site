# FS5 Claude writer lane B — WorkGraph, Build, Trust

Status: active; final refreshed Fable checksum verdict returned `ACTIVATED`
and this lane is dispatched under the exclusive ownership below.

## Objective

Implement the reconciled FS5 authority for WorkGraph, Build and Trust. Prove
the same constructed record through retained context, governed build and
withheld execution. Each route must own a different visual and interaction
job; do not repeat one dashboard or hero template. Do not invent copy, proof,
claims, colors, type, icons, assets, breakpoints or interaction patterns.

## Read first

1. `CLAUDE.md`
2. `design/golden-standard/FABLE-5.1-WHOLE-SITE-GOLDEN-STANDARD-PLAN.md`
   sections 4, 5, 7, 8.2, 8.4, 9.3, 9.4, 9.5, 10 and 12
3. `design/golden-standard/packages/FS5-DRAFT-ROUTE-SPECIFICITY-AND-EXECUTION-PROOF.md`
4. `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`
5. `design/golden-standard/narrative/COPY-UNIT-MANIFEST.json`
6. `design/golden-standard/narrative/EVIDENCE-LEDGER.md`
7. the WorkGraph, Build and Trust page maps
8. `design/golden-standard/image-system/IMAGE-LIBRARY-CATALOG.md`
9. `design/golden-standard/image-system/ASSET-REGISTRY.json`
10. these exact current slot manifests:
    `design/golden-standard/image-system/slot-manifests/workgraph.json` and
    `design/golden-standard/image-system/slot-manifests/build.json`. Trust has
    no bitmap slot manifest in FS5.

## Exclusive file ownership

Edit only:

- `preview/golden-standard/routes/workgraph/src/body.html`
- `preview/golden-standard/routes/workgraph/src/direction.css`
- `preview/golden-standard/routes/workgraph/src/direction.js`
- `preview/golden-standard/routes/build/src/body.html`
- `preview/golden-standard/routes/build/src/direction.css`
- `preview/golden-standard/routes/build/src/direction.js`
- `preview/golden-standard/routes/trust/src/body.html`
- `preview/golden-standard/routes/trust/src/direction.css`
- `preview/golden-standard/routes/trust/src/direction.js`
- `evidence/FULL-SITE-STAGING/FS5-LANE-B-IMPLEMENTATION-REPORT.md`

No other file may be changed. Lane A never touches these files.

## Protected runner contracts

- Preserve one route root each: `[data-workgraph]`, `[data-build]` and
  `[data-trust]`.
- Preserve WorkGraph hooks `[data-workgraph-page]`, `[data-workgraph-record]`,
  `[data-workgraph-record-state]`, `[data-workgraph-source]`,
  `[data-workgraph-lifecycle]` and all ordered `[data-workgraph-section]` values.
- Preserve Build hooks `[data-build-opening-stage]`, its five named
  `[data-build-opening-stage-row]` values, `[data-build-factory-progress]`,
  `[data-build-factory-stages]`, `[data-build-stage]`, `[data-build-status]`,
  `[data-build-pause]`, `[data-build-replay]` and `[data-build-inspect]`.
- Preserve Trust hooks `[data-trust]`, `[data-trust-control]` and the ordered
  `[data-trust-section]` values.
- Preserve every other existing runner-facing class, data attribute, form name,
  ARIA state and exact section value unless this package explicitly replaces it.
- The complete exact unit `workgraph.control.narrative` remains one contiguous
  `data-copy-ref` subtree; its H2 and bodies may not be split across decorative
  wrappers.
- `node tools/build_golden_standard_previews.mjs --check` may report
  `outputs-stale` for WorkGraph, Build or Trust because this lane edits their
  source without assembling. That is expected and must be reported; every other
  check must pass.

## Non-negotiable implementation rules

- Exact accepted copy only. Every public text unit must implement the matching
  `data-copy-ref`, `data-copy-kind` and `data-copy-scope` entry from
  `design/golden-standard/narrative/COPY-UNIT-MANIFEST.json`; no public text or accessible label may
  remain uncovered or nest another copy reference.
- Pause, Resume, Replay and Inspect are authored as static HTML controls and
  hidden only while inert; JavaScript may enhance their state but may not be
  their sole source.
- DOM order is identical at every width; never use CSS `order`.
- WorkGraph puts the disclosure and retained record in the first viewport;
  evidence and operating state remain progressive. The assigned image belongs
  to Context, never the hero.
- The single WorkGraph `<main>` carries both `[data-workgraph]` and
  `[data-workgraph-page]`; its default-visible Owner and Permission rows carry
  `[data-workgraph-record-field="owner"]` and
  `[data-workgraph-record-field="permission"]`.
- WorkGraph lifecycle advances and reverses by scroll while record identity,
  Owner and Permission remain stable; reduced motion and missing observer
  resolve on Learn and true no-JS keeps the whole sequence legible.
- WorkGraph's initial source lens is `Meeting`: its button is pressed in source
  and the static status reads `Meeting source highlights the fields retained
  from that source`. JavaScript changes
  the lens and status only after an actual pointer, keyboard or touch selection;
  it may not rewrite the initial state on load.
- Build loads no hero bitmap. Its first proof is the static, coded five-row
  Factory stage, marked once with `[data-build-opening-stage]`. The later
  Factory instrument has two real plans and a finite, pausable, governed
  progression.
- The opening rows carry, in order,
  `[data-build-opening-stage-row="approved-intervention"]`,
  `[data-build-opening-stage-row="specification-permission"]`,
  `[data-build-opening-stage-row="evaluation"]`,
  `[data-build-opening-stage-row="review-state"]` and
  `[data-build-opening-stage-row="evidence-return"]`.
- Build carries `One governed capability, two surfaces` as exact copy and truth
  boundary only in FS5. Do not create a toggle, customer-interface panel, prompt
  surface or second product carrier; the stateful proof is assigned to FS6.
- True no-JavaScript Build exposes the resolved Factory status exactly as
  `Governed review complete`, renders all six stages in order and hides inert
  playback controls.
- Trust opens copy-first, then shows the three-step control path with action
  withheld, permission and accountable owner visible without disclosure.
- Trust removes the stale opening `aria-label="Illustrative control path"`;
  visible provenance names the band. The sole state is
  `Human decision recorded. Release withheld.` Its finite settle starts only
  when the band enters view, resolves immediately for reduced motion or missing
  observers, and remains resolved without JavaScript.
- Every representative artifact has page disclosure before its first
  synthetic identifier and local provenance. Never imply a live deployment.
- No remote dependency, publication, deployment, commit, push or assembly.

## Self-check and report

Run source-level checks and
`node tools/build_golden_standard_previews.mjs --check` only. The report lists
failures first, exact changed files, default/progressive/first-section counts,
all viewport and reduced-motion/no-JS checks that can be proved before
assembly, and every deviation (expected: none).
