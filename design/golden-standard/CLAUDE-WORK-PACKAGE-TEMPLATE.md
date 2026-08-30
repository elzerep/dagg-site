# Claude Code work-package template

Package: `P# · Name`  
Status: ready / running / review / accepted / rejected  
Authority: `DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Base commit: `<full hash>`
Gate type: `operating acceptance by Codex` / `direction choice by Christian` / `publication by Christian`

## 1. Objective

One outcome only. Describe what must become true when the package is accepted.

## 2. Final copy — use verbatim

Provide every visible headline, paragraph, label, caption, CTA and accessible name. Claude may fix an obvious typo only if it is reported as a deviation. It may not rewrite register or invent supporting copy.

## 3. Authoritative inputs

- Masterplan section(s):
- Accepted screenshot/mock:
- Accepted asset(s):
- Accepted tokens/components:
- Page brief:

## 4. Files owned by this package

Only these files may be created or changed:

- `<path>`

If another file is required, stop and report the dependency. Do not widen scope silently.

## 5. Immutable files and decisions

Do not change:

- `<path or decision>`

Explicit visual invariants:

- palette roles;
- type roles;
- grid/gutters;
- image grammar;
- motion meaning;
- accepted components outside scope.

## 6. Deliverables

- Implementation files.
- Exact-revision local preview.
- Desktop and mobile renders.
- Interaction states.
- Evidence JSON.
- Deviation report.

## 7. Behavior and visual contract

State the required layout, hierarchy, interaction, transitions, focus behavior, mobile transformation, reduced-motion state and no-JS fallback.

## 8. Executable acceptance tests

Every test states both the assertion and its coverage.

Examples:

- Five user selections produce five unique specified titles and bodies.
- At 320, 360, 390, 768, 1024 and 1440 px, document `scrollWidth === clientWidth`.
- Every rendered HTML and SVG text element has computed size ≥12 px.
- Every interactive target has rendered bounds ≥44×44 px.
- Zero `href="#"` and every visible CTA reaches its specified route.
- Zero console errors after every interaction state.
- Reduced motion contains no timer-dependent blank content.
- With JavaScript disabled, all core argument and links remain visible.

Do not scan a hand-picked selector list when the requirement applies to the rendered document.

## 9. Required visual evidence

- Full-page screenshots: 1440, 390, 360, 320.
- Viewport screenshots for every interaction state that changes composition.
- Reduced-motion screenshot.
- No-JS screenshot.
- Same-state comparison against the accepted design/reference.

Screenshots must show the exact base/implementation commit and content-hashed assets.

## 10. Performance budget

- LCP <2.5 s mobile.
- INP <200 ms.
- CLS <0.1.
- State package-specific image/font/JS budgets.

## 11. Evidence JSON

Write the schema defined in the masterplan with package, commit, asset revision, viewport results, text coverage, touch-target minimum, contrast, links, console, reduced-motion, no-JS, screenshot paths and deviations.

## 12. Stop conditions

Stop and report before changing code if:

- the final copy does not fit the accepted component without breaking its contract;
- an immutable file or decision must change;
- required provenance is missing;
- the package depends on an unaccepted component;
- the exact-revision preview cannot be proven.

Do not continue to another package.

Do not ask Christian for an implementation or taste decision unless this package is explicitly marked as a direction-choice gate. Routine decisions and package acceptance belong to Codex.

## 13. Required completion report

Return in this order:

1. Deviations or failures first.
2. Exact commit and files changed.
3. Evidence JSON path.
4. Screenshot paths.
5. Tests run and their coverage.
6. What is ready for Codex review.

Do not use “verified,” “complete” or “production-ready” unless every stated gate has authoritative evidence.
