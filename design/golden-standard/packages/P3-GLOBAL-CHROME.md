# P3 · Global chrome: header, navigation and footer

Status: accepted by Codex
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
Base commit: `772ea9d875ac79fcfb1bef7c339150e81f66b516`
Gate type: operating acceptance by Codex

## 1. Objective

Build the shared navigation frame that every P4 direction and every later page
inherits. P3 proves information architecture, route clarity, adaptive ground,
keyboard behavior, mobile disclosure and the editorial footer. It does not
design a homepage hero, a WorkGraph mechanism or a page direction.

## 2. Final visible copy — use verbatim

### Header

- Transformation
- WorkGraph
- Build
- Impact
- Company
- Start an assessment
- Menu
- Close

The Dagg logotype returns to the specimen root.

### Footer

**Descriptor**
Strategy, context and execution for the AI-native company.

**Explore**

- Transformation
- WorkGraph
- Build
- Impact

**Company**

- Company
- Start an assessment

**Trust & contact**

- Trust
- hello@dagg.ai
- Privacy
- Terms

**Legal line**
© 2026 Dagg. All rights reserved.

### Route prototype

**Marker**
Dagg / Route prototype

**Route note**
Production content is owned by P11. This route exists in P3 only to prove navigation behavior.

Each route shell uses its navigation label as H1. No other visible explanatory
copy may be invented.

## 3. Authoritative inputs

- `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`, Parts III–V.
- `../narrative/PAGE-BRIEFS.md`.
- `../system/tokens.css` and `../system/TOKENS.md`.
- Existing real Dagg logotype assets under `assets/`.
- The immutable preview server accepted in P0R2.

## 4. Files owned by P3

Only these paths may be created or changed:

- `CLAUDE.md` — active-package pointer only.
- `design/golden-standard/packages/P3-GLOBAL-CHROME.md` — status and acceptance record only.
- `design/golden-standard/system/chrome.css`
- `design/golden-standard/system/chrome.js`
- `preview/golden-standard/chrome/**`
- `tests/test_p3_chrome.py`
- `tools/capture_p3_evidence.py`
- `evidence/P3/**`

Do not change the public site, P0–P2 files or evidence, the masterplan,
narrative files, tokens, fonts, logo assets or legacy previews.

### Execution subpackages

P3 remains one acceptance package, but Claude executes it in two serial,
non-overlapping subpackages so a long implementation cannot hide progress or
collide with its own test rig:

- **P3A · Rendered chrome:** owns only `design/golden-standard/system/chrome.css`,
  `design/golden-standard/system/chrome.js` and
  `preview/golden-standard/chrome/**`. It stops after static source/syntax
  checks and never grades its own rendering.
- **P3B · Acceptance rig:** starts only after Codex has inspected P3A source.
  It owns only `tests/test_p3_chrome.py`, `tools/capture_p3_evidence.py` and
  `evidence/P3/**`. It may not alter P3A files to make a test pass.
- **P3C · Integration:** Codex alone owns the status/acceptance record, the
  real-Chrome run, visual review, corrections sent back to the relevant
  subpackage, commit and clean post-commit reproduction.

The subpackages do not change the P3 gate. P4 remains blocked until all P3
requirements pass together in one immutable snapshot.

## 5. Information architecture contract

The production route map is:

| Label | Production path | P3 preview destination |
|---|---|---|
| Dagg logotype | `/` | `/preview/golden-standard/chrome/` |
| Transformation | `/transformation` | `/preview/golden-standard/chrome/routes/transformation/` |
| WorkGraph | `/workgraph` | `/preview/golden-standard/chrome/routes/workgraph/` |
| Build | `/build` | `/preview/golden-standard/chrome/routes/build/` |
| Impact | `/impact` | `/preview/golden-standard/chrome/routes/impact/` |
| Company | `/company` | `/preview/golden-standard/chrome/routes/company/` |
| Start an assessment | `/assessment` | `/preview/golden-standard/chrome/routes/assessment/` |
| Trust | `/trust` | `/preview/golden-standard/chrome/routes/trust/` |
| Privacy | `/privacy` | `/preview/golden-standard/chrome/routes/privacy/` |
| Terms | `/terms` | `/preview/golden-standard/chrome/routes/terms/` |

Every preview link must carry its production path in `data-production-href`.
Every preview destination must return 200 and render the same global chrome.
There are no `#`, `javascript:`, empty or unserved links.

The homepage remains the whole-company executive memo. `Transformation` is a
deep route, not the default landing page. WorkGraph remains top-level. Dagg
Factory, Operate and Trust do not become primary items; Factory and Operate
belong inside Build, while Trust is linked from the footer.

## 6. Visual contract

### Header

- Use the P2 1240 px field, gutters and Geist interface role.
- Render at 68 px high from 940 px upward and 60 px below 940 px.
- Use the real Dagg logotype, not text or a redrawn mark.
- Desktop composition: logotype left, the five primary depth routes as one
  calm sequence, assessment action right. It must not look like a dashboard,
  tab strip or pill row.
- Mobile composition: logotype left and one native disclosure right. The open
  menu is a full reading surface with generous vertical rhythm, not a cramped
  dropdown card.
- Default warm state uses Paper/Lift and Ink. Dark-state adaptation uses Ink
  and Paper. Coral is reserved for the assessment action and active human
  choice; Sage is not a navigation decoration.
- Use one-pixel semantic rules, 4 px control radius and no ornamental shadow,
  glass effect, gradient, fake icon or rounded container around the full nav.
- The header may be sticky. After 160 px it hides on sustained downward scroll
  and returns on upward scroll, focus entry, menu open or direction change.
- It must adopt the declared section ground before its contents lose contrast.
  Sections expose `data-header-theme="warm|ink"`; enhancement observes the
  ground at the header boundary. With JavaScript absent, the warm header stays
  legible and all content and routes remain available.

### Footer

- Use one full-width Ink ground with the real light logotype, not a set of
  cards. The descriptor is the editorial lead; link groups are supporting
  structure.
- Desktop uses one asymmetric 5/7 composition: brand/descriptor on the left,
  three link columns on the right. Mobile becomes one continuous reading
  sequence with rules and spacing, not boxed accordions.
- Footer text is at least 13 px; links use visible hover and focus treatments.
- Trust is visible but does not imply certifications or controls not yet
  evidenced. Privacy and Terms are routes only; P3 invents no legal copy.

## 7. Interaction and accessibility contract

- Desktop navigation appears at 940 px and above. Mobile disclosure appears
  below 940 px. The DOM reading order remains logotype → primary routes →
  assessment.
- Use a native `<details>/<summary>` disclosure as the no-JavaScript baseline.
  JavaScript may enhance it with Escape, outside-click close, focus return and
  body-scroll lock. Core navigation may not depend on JavaScript.
- Summary and every route meet the 44 × 44 px target. Keyboard focus is always
  visible on Paper and Ink.
- The open disclosure exposes `aria-expanded="true"` through its native state;
  the enhancement keeps the visible Menu/Close labels synchronized.
- Escape closes and restores focus to the summary. Choosing a route closes the
  disclosure. Resizing to desktop closes it and restores document scrolling.
- When the menu is open, keyboard focus stays within the header navigation
  surface until it closes. No hidden menu link may remain focusable when shut.
- Active route uses `aria-current="page"` and a typographic/rule treatment,
  not color alone.
- `prefers-reduced-motion: reduce` removes hide/reveal and disclosure motion
  without changing route order, reachability or resolved state.
- Hover-only information is forbidden. At 200% zoom, routes remain reachable
  and the document does not scroll horizontally.

## 8. P3 specimen

Build `/preview/golden-standard/chrome/index.html` as a long, neutral chrome
specimen using only P2 surfaces, type, real logo assets and supplied copy. It
must include:

1. a warm opening carrier;
2. one short Lift carrier;
3. one Ink carrier that forces the adaptive header state;
4. enough vertical distance to prove hide/reveal behavior;
5. the accepted editorial footer;
6. route shells for all nine non-root destinations.

The carriers are diagnostics, not homepage sections. They may print only the
route marker, route label, route note and the P2 specimen headings already
approved in P2. Do not insert imagery, product UI, diagrams or marketing copy.

## 9. Executable acceptance tests

Create `tests/test_p3_chrome.py` and drive the installed Google Chrome through
CDP. Reuse the P0R2 immutable server; do not use Playwright or another browser.

The suite must prove:

1. HTML, CSS, JavaScript, fonts and both logotypes carry one snapshot ID.
2. Every preview destination returns 200, declares the correct production
   path and renders one header and one footer.
3. Primary label order is exactly Transformation, WorkGraph, Build, Impact,
   Company, Start an assessment; the root is not Transformation.
4. No link is empty, hash-only, JavaScript or unserved; mail is the only
   non-HTTP route and is exactly `mailto:hello@dagg.ai`.
5. `document.scrollWidth === document.clientWidth` at 320, 360, 390, 768,
   1024 and 1440 px and at Chrome's 200% page zoom.
6. Every rendered text node is at least 12 px, every footer text node is at
   least 13 px, and every interactive target is at least 44 × 44 px.
7. Desktop and mobile controls switch at 940 px without changing primary DOM
   order. Hidden navigation is not focusable.
8. Keyboard Tab reaches all visible routes once in logical order. Focus rings
   are distinguishable on warm header, ink-adapted header and footer.
9. Mobile disclosure opens from keyboard, traps focus while open, closes on
   Escape and outside click, restores focus and unlocks body scroll.
10. Sustained down-scroll hides the closed header after 160 px; up-scroll,
    focus entry and menu open reveal it. The Ink carrier changes computed
    header foreground/background to the declared Ink pair.
11. `aria-current="page"` is correct on every route shell and absent on the
    root logo when a depth route is active.
12. With JavaScript disabled, the native disclosure still exposes every route
    and the footer remains complete.
13. Reduced motion removes non-essential transitions without changing layout,
    content, active route or focus order.
14. No request leaves `127.0.0.1`; zero console errors occur; only P3-owned
    files differ from the base commit and all public/legacy/P0–P2 files remain
    byte-identical.

## 10. Required evidence

Create `tools/capture_p3_evidence.py`. One immutable server process must
produce:

- `evidence/P3/result.json` using the masterplan schema and snapshot ID;
- full-page root screenshots at 1440, 390, 360 and 320 px;
- viewport screenshots of the compact desktop header at 940 and 1024 px;
- mobile menu closed, keyboard-open and focus-trapped screenshots at 390 px;
- warm, Ink-adapted, hidden-on-down-scroll and revealed-on-up-scroll header
  screenshots at 1440 px;
- one route-shell screenshot with its active state;
- no-JavaScript and reduced-motion screenshots at 390 px;
- DOM, route, focus, request, response-header and state-transition records;
- test output, exact coverage, deviations and unmeasured fields.

Capture a clean post-commit run that reproduces the accepted pre-commit
snapshot ID with `evidence/**` excluded exactly as P0R2 defines.

## 11. Performance budget

- Additional shared CSS ≤ 24 KB uncompressed.
- Shared JavaScript ≤ 12 KB uncompressed.
- No added font, image, icon or third-party dependency.
- Header enhancement initializes without measurable layout shift.
- No remote request.

## 12. Stop conditions

Stop before commit if:

- the primary topology changes;
- the homepage resolves to Transformation;
- WorkGraph is demoted or Factory/Operate is promoted to primary navigation;
- a preview or footer link is a placeholder;
- the header loses contrast over a declared ground;
- the mobile menu is a squeezed desktop row or requires JavaScript;
- keyboard focus can escape an open disclosure or reach a closed one;
- the footer becomes a card grid or claims unsupported Trust facts;
- P2 tokens, public files or legacy previews change;
- screenshots and state records do not prove the same immutable snapshot.

Do not begin P4.

## 13. Completion report

Return deviations first, then exact files and commit, route table, state
screenshots, keyboard/no-JavaScript/reduced-motion results, snapshot ID and
what is ready for Codex visual review. Do not call P3 accepted; Codex owns the
operating and visual gate.

## 14. Codex P3C acceptance record

Pre-commit candidate: `codex-visual-gate-r4`
Rendered base commit: `772ea9d875ac79fcfb1bef7c339150e81f66b516`
Snapshot ID: `96e0d67da3d6f522a42b5e63fb2aca403c935f073aaa8ec6477fb924e19247ba`

- 14/14 numbered Chrome tests pass; the completed result carries 15 true
  checks, 14 substantive measurements and eight served-asset coverage entries.
- Layout is verified at 320, 360, 390, 768, 1024 and 1440 px, the 939/940
  switch, compact-header screenshots at 940 and 1024 px and the 200% reflow
  proxy.
- Warm, Ink-adapted, hidden, revealed, active-route, mobile closed/open/trapped,
  no-JavaScript and reduced-motion states were visually inspected.
- Same-run Anthropic, OpenAI, Palantir and xAI reference captures were compared
  with the rendered P3 header and mobile menu. Dagg retains the references'
  restraint, route clarity and precision without copying their identities.
- Independent visual review rejected the first candidate because mobile footer
  metadata computed to 12 px and its groups lacked required rules. The accepted
  candidate renders footer text at a measured 13 px minimum, adds restrained
  mobile rules and makes both conditions executable gates.
- No public, legacy or P0-P2 file differs from the P3 base commit. No remote
  request or third-party dependency was added.

The final clean post-commit reproduction is recorded in
`evidence/P3/result.json`. The capture freezes the source snapshot before its
suite rewrites excluded evidence files, so `dirtyAtCapture` describes the
accepted source rather than the evidence run's own outputs.
