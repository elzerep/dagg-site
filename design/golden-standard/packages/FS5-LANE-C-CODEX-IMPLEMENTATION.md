# FS5 Codex lane C — Assessment, Impact and shared chrome

Status: active after the exact Fable 5.1 activation verdict and the required
doc-only scope reconciliation.

## Objective

Make Assessment, Impact and the shared header/footer exactly measurable by the
FS5 copy and interaction rig without redesigning them. Preserve the accepted
route composition and shared navigation behavior. This lane supplies exact
copy ownership, truthful preview states and accessible names; it does not add
claims, decoration, imagery, routes or publication behavior.

## Read first

1. `CLAUDE.md`
2. `design/golden-standard/FABLE-5.1-WHOLE-SITE-GOLDEN-STANDARD-PLAN.md`
   sections 4, 5, 7, 8.2–8.5, 9.7, 9.8, 10 and 12
3. `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`
4. `design/golden-standard/narrative/COPY-UNIT-MANIFEST.json`
5. `design/golden-standard/narrative/EVIDENCE-LEDGER.md`
6. the Assessment and Impact page maps
7. `design/golden-standard/packages/FS5-FABLE-5.1-ACTIVATION-REVIEW.md`

## Exclusive file ownership

Edit only:

- `preview/golden-standard/routes/assessment/src/body.html`
- `preview/golden-standard/routes/assessment/src/direction.css`
- `preview/golden-standard/routes/assessment/src/direction.js`
- `preview/golden-standard/routes/impact/src/body.html`
- `preview/golden-standard/routes/impact/src/direction.css`
- `preview/golden-standard/routes/impact/src/direction.js`
- `preview/golden-standard/shared/chrome/header.html`
- `preview/golden-standard/shared/chrome/footer.html`
- `preview/golden-standard/shared/chrome/chrome.css`
- `preview/golden-standard/shared/chrome/chrome.js`
- `preview/golden-standard/component-library/script.js` (only the four
  responsive Build-preview copy hooks; no visual or behavioral redesign)
- `evidence/FULL-SITE-STAGING/FS5-LANE-C-IMPLEMENTATION-REPORT.md`

No Claude lane may touch these files. Lane C never touches Home,
Transformation, WorkGraph, Build, Trust or Company source files. It never
redesigns the component library and never touches tokens, assets, images,
tests, runner or assembled `index.html` files. The one component-library
exception is the exact keyed ownership on the four existing JS-created
responsive preview controls named by the manifest.

## Exact implementation rules

- Every public text unit and accessible-only string implements the exact
  `data-copy-ref`, `data-copy-kind`, `data-copy-scope` and, when applicable,
  `data-copy-state` entry in `narrative/COPY-UNIT-MANIFEST.json`.
- A visible-text copy reference owns a complete unit and may not contain
  another visible-text copy reference. An accessible-only ancestor may contain
  visible child units only where the manifest declares that ancestor with
  `accessibleAttribute: true`. No visible or accessible string remains
  uncovered.
- Assessment uses the FS5 local-preview success tuple, never the FS6 delivery
  promise. Its form makes no outbound request, uses the exact validation and
  submitting states, focuses the first invalid field and exposes the exact
  no-JavaScript mail path.
- The opening action carries `[data-assessment-primary-action]`. The submit
  button and polite live region both begin at `data-copy-state="idle"`, use the
  exact manifest state on every transition and remain enabled during the
  450 ms local check. A local in-flight guard permits the duplicate state but
  prevents a second timer and any request.
- Assessment's submit control reaches at least 48×48 CSS px on touch. The scope
  card and position action remain inside the first viewport at 1440×900 and
  390×844. Its H1 uses a balanced `min(18ch, 100%)` measure and remains within
  three measured line boxes at 1440, 1024 and 390 without shrinking type. Do
  not add an image.
- Impact remains an internal, non-published staging route. Keep it absent from
  header and footer. Preserve `Approved proof · none published` and the exact
  public empty-slot disclosure. Do not invent a client, result, metric, quote,
  case, deployment or logo.
- Shared chrome preserves the current information architecture and Build
  adaptive disclosure. Its first destination is the real Build overview URL;
  the disclosure trigger remains `Build` and is not converted into a nested
  link.
- The four Build destination units and four proof-inset units use the eight
  exact sibling references in the copy manifest. Do not wrap the entire list
  in an aggregate copy reference.
- Both theme-swapped logo images inside the labelled brand-home link are
  decorative (`alt=""`). The footer logo alone carries the exact `Dagg` alt
  unit. The local FS5 footer omits Privacy and Terms; those routes remain FS6
  publication dependencies.
- Header behavior remains equivalent for pointer, keyboard, touch, coarse and
  hybrid input: pointer intent, leave grace, Escape layering, focus restore,
  mobile focus containment, background inertness and scroll lock.
- Native disclosure semantics carry expanded/collapsed state. Do not invent
  `menu`, `flyout` or state suffixes in accessible names.
- DOM and reading order stay identical at every width. Never use CSS `order`.
- Do not change palette, type, spacing tokens, icons, breakpoints or motion
  timing. Do not add remote dependencies.
- Do not assemble, commit, push, deploy, publish or promote canonical routes.

## Self-check and report

Run source-level checks and
`node tools/build_golden_standard_previews.mjs --check` only. The report lists:

1. failures first;
2. every changed file and reason;
3. Assessment default, progressive and first-section counts using §10.4;
4. exact form validation, submitting, success and no-JavaScript strings;
5. exact Impact status and disclosure plus confirmation that Impact remains
   absent from shared navigation;
6. every shared accessible label and Build flyout destination/state;
7. source-level keyboard, touch and reduced-motion/no-JavaScript checks;
8. every deviation from authority, expected to be none;
9. an explicit statement that nothing was assembled or published.

Lane C is complete only when the strict copy manifest can be satisfied without
an uncovered string, nested reference, invented copy or weakened interaction.

## Required execution sequence

1. Implement and source-check the shared header/footer slice first. Do not touch
   Lane A or Lane B files.
2. Once the chrome slice is stable, Fable must confirm the refreshed contract
   and manifest checksums recorded in
   `FS5-FABLE-5.1-ACTIVATION-REVIEW.md`. Only after the exact refreshed
   activation verdict may Lane A and Lane B run in parallel under their
   exclusive scopes.
3. After both writer reports exist, finish the Impact and Assessment source in
   this lane.
4. No lane assembles. Codex assembles exactly once after all three lane reports
   and source checks pass.
