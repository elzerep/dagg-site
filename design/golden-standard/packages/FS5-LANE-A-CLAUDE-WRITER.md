# FS5 Claude writer lane A — Home, Transformation, Company

Status: active; final refreshed Fable checksum verdict returned `ACTIVATED`
and this lane is dispatched under the exclusive ownership below.

## Objective

Implement the reconciled FS5 authority for Home, Transformation and Company.
Preserve the founder-selected Home hero exactly. Make the three routes feel
materially distinct while using the existing Dagg brand and image-language
system. Do not invent copy, proof, claims, colors, type, icons, assets,
breakpoints or interaction patterns.

## Read first

1. `CLAUDE.md`
2. `design/golden-standard/FABLE-5.1-WHOLE-SITE-GOLDEN-STANDARD-PLAN.md`
   sections 4, 5, 7, 8.2, 8.4, 9.1, 9.2, 9.6, 10 and 12
3. `design/golden-standard/packages/FS5-DRAFT-ROUTE-SPECIFICITY-AND-EXECUTION-PROOF.md`
4. `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`
5. `design/golden-standard/narrative/HOME-NARRATIVE-FOUNDER-RESET.md`
6. `design/golden-standard/narrative/COPY-UNIT-MANIFEST.json`
7. `design/golden-standard/narrative/EVIDENCE-LEDGER.md`
8. `design/golden-standard/design-mapping/HOME-FS5-PAGE-MAP.md` and the
   current Transformation and Company page maps
9. `design/golden-standard/image-system/IMAGE-LIBRARY-CATALOG.md`
10. `design/golden-standard/image-system/ASSET-REGISTRY.json`
11. these exact current slot manifests:
    `design/golden-standard/image-system/slot-manifests/home.json`,
    `design/golden-standard/image-system/slot-manifests/transformation.json`
    and `design/golden-standard/image-system/slot-manifests/company.json`

## Exclusive file ownership

Edit only:

- `preview/golden-standard/home/src/body.html`
- `preview/golden-standard/home/src/direction.css`
- `preview/golden-standard/home/src/direction.js`
- `preview/golden-standard/routes/transformation/src/body.html`
- `preview/golden-standard/routes/transformation/src/direction.css`
- `preview/golden-standard/routes/transformation/src/direction.js`
- `preview/golden-standard/routes/company/src/body.html`
- `preview/golden-standard/routes/company/src/direction.css`
- `evidence/FULL-SITE-STAGING/FS5-LANE-A-IMPLEMENTATION-REPORT.md`

No other file may be changed. Lane B never touches these files.

## Protected runner contracts

- Preserve one route root each: `[data-home]`, `[data-transformation]` and
  `[data-company]`.
- Preserve Home hooks `[data-home-hero-image]`, `[data-home-primary-action]`,
  `[data-home-execution]`, `[data-home-execution-states]`,
  `[data-home-execution-status]`, `[data-home-pause]` and `[data-home-replay]`.
- Preserve Transformation hooks `[data-transformation-outcome-strip]`, exactly
  five `[data-transformation-index-label]` nodes, the seven ordered
  `[data-transformation-section]` values and `[data-transformation-provenance]`.
- Preserve Company hooks `[data-company-seam]`, `[data-company-accountability]`
  and the three named `[data-company-accountability-row]` values.
- Preserve every other existing runner-facing class, data attribute, form name,
  ARIA state and exact section value unless this package explicitly replaces it.
- The complete exact unit `transformation.roadmap.narrative` remains one
  contiguous `data-copy-ref` subtree; its H2/body/closing paragraph may not be
  split across decorative wrappers. The same rule applies to
  `company.close.narrative`; the leadership group follows it as a sibling and
  remains separate from the narrative unit.
- `node tools/build_golden_standard_previews.mjs --check` may report
  `outputs-stale` for Home, Transformation or Company because this lane edits
  their source without assembling. That is expected and must be reported; every
  other check must pass.

## Non-negotiable implementation rules

- Exact accepted copy only. Every public text unit must implement the matching
  `data-copy-ref`, `data-copy-kind` and `data-copy-scope` entry from
  `design/golden-standard/narrative/COPY-UNIT-MANIFEST.json`; no public text or accessible label may
  remain uncovered or nest another copy reference.
- Pause, Resume and Replay are authored as static HTML controls and hidden only
  while inert; JavaScript may enhance their state but may not be their sole
  source.
- DOM order is identical at every width; never use CSS `order`.
- Home hero bytes, source selection, crop, H1 and lead remain protected.
- Remove stale Home accessible labels `Illustrative WorkGraph continuity` and
  `Retained company context`; visible manifest copy already names those
  objects and no uncovered accessible string is allowed.
- Home's execution sequence is finite, pausable, visibility-aware and resolved
  immediately under reduced motion; true no-JS keeps all states in DOM order.
- True no-JavaScript Home exposes the resolved status exactly as `Human decision
  recorded. Release remains withheld.` and hides inert playback controls.
- Transformation uses only the assigned 4:5 T-DF-01 carrier in the first
  viewport, marks the complete five-label opening strip once with
  `[data-transformation-outcome-strip]`, marks each label with
  `[data-transformation-index-label]`, and exposes all five outcomes without
  requiring a tap on compact layouts.
- Company is proposition → registered 5:2 seam → three accountability rows,
  with the complete opening chain marked once as
  `[data-company-accountability]`.
  The seam carries `[data-company-seam]`; the three rows carry
  `[data-company-accountability-row="decision"]`,
  `[data-company-accountability-row="build"]` and
  `[data-company-accountability-row="escalation"]`.
  The seam is 640×256 at 1440, fills a responsive seven-column 5:2 carrier at
  1024 (capped at 640 px), and is 350×140 at 390; it is never cropped. The first
  two rows must be fully inside the 1440 and 1024 first viewports. At 390 the
  chain and at least the first 44 px of its Decision row must begin in view.
- No remote dependency, publication, deployment, commit, push or assembly.

## Self-check and report

Run source-level checks and
`node tools/build_golden_standard_previews.mjs --check` only. The report lists
failures first, exact changed files, default/progressive/first-section counts,
all viewport and reduced-motion/no-JS checks that can be proved before
assembly, protected Home copy and asset hashes against
`evidence/FULL-SITE-STAGING/FS5-PROTECTED-INVARIANT-BASELINE.json`, and every
deviation (expected: none).
