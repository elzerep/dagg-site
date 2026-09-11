# Home responsive reading map

Status: **historical five-beat reference; superseded by P4R10 for Home**  
Route: `/`  
Content authority: `../narrative/HOME-NARRATIVE-FOUNDER-RESET.md`  
Visual authority: `../authority/Dagg-Design-System-Foundations.pdf`  
Responsive and QA authority: `../packages/P4R10-FIGMA-HOME-DIRECTION-GATE-AND-SHARED-IMPLEMENTATION-CONTRACT.md`  
Publication status: not approved for publication

> Do not implement this file's five-beat order, counts or hooks. P4R10 controls
> the current six-act founder gate. Reuse only resilience principles that do not
> conflict with P4R10; P4R11 will issue the selected direction's exact
> responsive map and hooks.

## 1. Purpose and authority

This map translates the accepted Home copy into one responsive reading system.
It fixes semantic order, viewport composition, line-length limits, progressive
disclosure, resilience states and the acceptance evidence required before Home
can be judged visually.

It does not change copy, select a hero asset, define a production route, compose
the page or reopen the image-language decision. If this map conflicts with the
current content contract, the content contract wins for copy and assignment. If
it conflicts with Foundations or P4R7, Foundations wins for the visual system
and P4R7 wins for Home responsive, interaction and QA requirements.

The prior 291/26/49 and 520/0/63 baselines are withdrawn. Both predate the
current founder-led narrative repair. The current source route measures 519
default-visible words, 0 progressive words and 59 words in the Position block
using the canonical count in section 11. The immutable acceptance run must
reproduce 519/0/59 and check those values against the content-contract range.

The stable structural baseline remains five narrative beats and a target of
4.5-6.0 screens including the footer at 1280 x 720. Copy budgets come from the
current content contract and are tested against the rendered page.

Counts exclude global navigation, footer, metadata and internal notes. They
include visible headings, actions, captions, the shared artifact disclosure and
artifact labels.
They must be re-measured from the rendered revision, not inferred from source
file length.

## 2. Non-negotiable reading invariants

1. There is one semantic sequence at every width:
   `Position -> Consequence -> Technology -> Execution proof -> Identity and next move`.
2. CSS `order`, duplicated desktop/mobile copy and alternate DOM trees may not
   change that sequence.
3. The executive conclusion precedes the mechanism. The mechanism precedes
   technical depth.
4. WorkGraph and Dagg Factory are both named before the end of the second
   viewport at every required viewport.
5. One contained proof carries the execution argument. Home may not become a
   component catalogue, terminal wall or sequence of equal cards.
6. Required copy is never reveal-on-scroll gated. A full-page capture made
   without scripted scrolling must contain the complete default reading path.
7. Progressive copy is additional inspection, not missing meaning. All four
   proof states remain in the default path; optional evidence detail alone may
   reveal progressively.
8. Mobile is recomposed around the same meaning. It is not a blindly stacked
   desktop grid and never uses a desktop image crop as mobile art direction.
9. The shared illustrative-data disclosure remains available before the reader
   can mistake any Home artifact for client or production evidence.
10. The conditional Impact link is absent until the content contract's proof
    gate passes. Hiding the route may not leave punctuation, separators or an
    empty layout slot.

## 3. Required semantic and test hooks

The implementation package must expose these stable hooks. Class names and
visual wrappers remain implementation-owned.

| Hook | Required semantic object |
|---|---|
| `[data-home]` | The single Home route root; it is the only child of the global `<main>` landmark |
| `[data-home-beat="position"]` | Home 1 |
| `[data-home-beat="consequence"]` | Home 2 |
| `[data-home-beat="technology"]` | Home 3 |
| `[data-home-beat="proof"]` | Home 4 |
| `[data-home-beat="identity"]` | Home 5 |
| `[data-home-h1]` | The single H1 |
| `[data-home-lead]` | Hero lead |
| `[data-home-hero-picture]` | Hero `<picture>` |
| `[data-home-hero-image]` | Hero `<img>` and intrinsic fallback |
| `[data-home-technology="workgraph"]` | WorkGraph proposition |
| `[data-home-technology="factory"]` | Dagg Factory proposition |
| `[data-home-proof]` | The one contained proof instrument |
| `[data-home-proof-state="0"]` | Operating reality; default |
| `[data-home-proof-state="1"]` | Decision retained; default |
| `[data-home-proof-state="2"]` | Governed execution; default |
| `[data-home-proof-state="3"]` | Evidence returns; default/resolved |
| `[data-home-progressive]` | Optional future evidence detail; absent when progressive copy is zero |
| `[data-home-primary-action]` | `Start an assessment` |
| `[data-copy-scope="default"]` | Counted primary-reading copy |
| `[data-copy-scope="progressive"]` | Counted progressive copy |
| `[data-narrative-anchor]` | Meaningful visual/reading anchors used by rhythm QA |

Test hooks must not add visible labels or replace correct HTML semantics.

## 4. Canonical reading order and disclosure map

### Beat 1 - Position

Semantic order:

1. eyebrow;
2. H1;
3. lead;
4. primary action;
5. secondary action;
6. Decision Field picture with restrained Machine Signal.

The copy column precedes the picture in the DOM. Desktop may place them beside
one another. At 939 px and below, the composed order is copy, actions and mobile
picture. The picture never interrupts H1 and lead.

The H1 and lead remain the only proposition in the initial view. No autoplay
video, ambient product loop, fake prompt input or Operational Evidence surface
enters the hero. V1 uses the approved resolved still and one finite material-
settle entrance, then holds.

### Beat 2 - Consequence

Semantic order: H2, then body.

This is a punctuation beat, not a second hero and not a full thesis chapter.
Its typography may carry editorial emphasis, but it must remain an H2 in the
document outline. `human-speed` and `AI-native` may not break at their hyphens.
No additional image or card is introduced here.

### Beat 3 - Technology

Semantic order:

1. eyebrow;
2. H2;
3. intro;
4. shared synthetic-data disclosure;
5. one connected artifact with WorkGraph H3/body/link followed by Dagg Factory
   H3/body/link.

At 940 px and above, the two propositions may share one asymmetric field. They
must read as peer capabilities rather than equal feature cards. At 939 px and
below, WorkGraph is followed by Factory in one column, separated by a structural
rule or spacing rather than floating card chrome.

Both product names and their short propositions are default copy. One shared
synthetic-data disclosure appears before the connected product artifact and
qualifies every illustrative record on Home. The WorkGraph sentence uses the
current accepted wording `ongoing operating decisions`; older `later operating
decisions` wording is invalid.

### Beat 4 - Execution proof

Semantic order:

1. eyebrow and H2;
2. proof title and record ID;
3. State 1 - Operating reality;
4. State 2 - Decision retained;
5. State 3 - Governed execution;
6. State 4 - Evidence returns;
7. Trust link;
8. conditional Impact link when eligible.

The visual default must make States 1, 2 and 3 understandable without opening
detail. The DOM order remains 1-2-3. Enhanced controls may mark progression but
may not hide a causal state.

No-JavaScript exposes all four states as ordinary ordered document content.
Reduced motion retains all four complete states without a transition. Eligible
desktop may run one finite preview; mobile, tablet and reduced motion remain
manual-only. No control may hide a state.

This is the only dominant dark instrument on Home. It is contained, never a
full-page terminal, and preserves its labels, owner, boundary, evidence and way
back at every width.

### Beat 5 - Identity and next move

Semantic order: H2, body, primary assessment action, Transformation link.

This is the close, not a sitemap in prose. The footer follows as global shell.
The assessment action remains a direct link and never becomes a disclosure.

## 5. Viewport composition matrix

The content field is capped at 1240 px. The accepted grid has twelve columns.
At 940 px the strategic split is still active; at 939 px it is recomposed.

| Test viewport | Platform job | Gutter | Grid gap | Composition requirement |
|---|---|---:|---:|---|
| 1440 x 900 | Mac/PC wide desktop | 72 px | 32 px | Hero is one large full-width field with copy in authored quiet paper; H1 and the complete visual event are simultaneous. |
| 1366 x 768 | Common PC laptop | 48 px | 32 px | Same desktop order; no nav collision; consequence remains an obvious continuation rather than a second slide. |
| 1280 x 720 | Binding Home height benchmark | 48 px | 32 px | Complete page including footer is 3240-4320 px; one dominant idea per viewport; no empty viewport. |
| 1024 x 768 | iPad landscape / compact desktop | 48 px | 32 px | Desktop split remains; text measure wins over equal columns; chrome may compact only according to accepted P3 behavior. |
| 768 x 1024 | iPad portrait | 24 px | 24 px | One-column editorial composition; the portrait source may sit in a measured 16:9 tablet crop held at the protected event so all protected events enter the first screen; proof controls precede the ordered states they mark. |
| 390 x 844 | Mobile | 20 px | no track gap requirement | One-column mobile composition; copy and action precede hero art; no sideways product pan for the primary proof. |
| 360 x 800 | Mobile interpolation guard | 20 px | no track gap requirement | Same 390 hierarchy with no breakpoint-only omission or orphan separator. |
| 320 x 800 | Small mobile | 20 px | no track gap requirement | Full 280 px content width remains usable; no horizontal document scroll; all actions fit without clipped labels. |

The exact boundary tests are 940 px and 939 px. At 940, the strategic split and
desktop navigation may remain. At 939, content is recomposed and the accepted
mobile navigation disclosure is present. DOM order is identical on both sides.

## 6. Type, measure and line requirements

### Frozen endpoints

| Role | 1440 px | 390 px | 320 px | Leading |
|---|---:|---:|---:|---:|
| H1 | 68 px | 44 px | 42 px | 1.02 |
| H2 | 52 px | 36 px | 34 px | 1.07 |
| H3 | 32 px | 27 px | 26 px | 1.12 |
| Lead | 23 px | 20 px | 19 px | 1.44 |
| Body | 18 px | 17 px | 17 px | 1.62 |
| Meta | 13 px | 12 px | 12 px | 1.42 |

Computed sizes between endpoints must be continuous. A one-pixel viewport
change around 940 or another breakpoint may change layout, but may not create a
type-size jump greater than 0.5 px.

### Line and measure gates

- H1: at most two lines at 1440, 1366 and 1280; at most three at 1024, 768 and
  390; at most four at 320. No clipping at 200% zoom.
- Hero lead: at most five lines on wide desktop, six at 1024/768, seven at 390
  and eight at 320. The type size and measure may not be compressed merely to
  meet the line gate.
- H2: at most three lines on desktop/tablet landscape. The long Consequence H2
  may use four balanced lines at 768/390 and five at 320; other Home H2s remain
  at three or fewer.
- H3: conclusion only; no category label is promoted to H3 to gain scale.
- Long prose at 940 px and above: 560-620 px maximum reading measure and never
  wider than 68 characters per line in its rendered font.
- Long prose below 940 px: full available measure up to 620 px; at 390/320 it
  uses the 20 px gutters and no artificial narrow column.
- Body paragraphs remain 20-45 words. Do not reduce font size or compress line
  height to make a paragraph fit a composition.
- JetBrains Mono is limited to the shared disclosure, record IDs, status and
  instrument labels. It never carries body copy.
- No visible text, including SVG text, may compute below 12 px.
- `hyphens: none` and normal word wrapping apply to headings. A line containing
  only punctuation, an arrow or a separator is a failure.

## 7. Rhythm and vertical continuity

- One warm Paper reading ground carries most of the page.
- At most three meaningful page-ground changes occur.
- Only one carrier may exceed 80svh and no two full-height acts are consecutive.
- Desktop large/medium/mobile section padding follows the accepted 160/112/88
  and 112/88/64 scales according to local argumentative weight; it is not one
  repeated global value.
- A punctuation gap may be 240-360 px on desktop only when the Consequence line
  itself occupies and justifies it.
- For every viewport, the empty vertical distance between consecutive
  `[data-narrative-anchor]` boxes is at most 60% of viewport height. A larger
  gap requires a visible semantic visual occupying that distance; whitespace
  alone fails.
- Home height is measured only against the binding 1280 x 720 target. Other
  viewport heights are evidence for rhythm and access, not proxy targets.

## 8. Progressive enhancement and state behavior

Default Home meaning is present in HTML before JavaScript runs. Enhancement may
change presentation, never ownership of meaning.

### Enhanced state

- default copy remains visible without scrolling or interaction prerequisites;
- all four proof states remain visible; a control may mark progression but may
  not close or replace a causal state;
- every hover state has equivalent focus and tap behavior;
- the proof control changes one focal state, announces the named end state and
  stops;
- opening progressive detail does not move focus unexpectedly or create a
  layout jump larger than the detail being revealed;
- Escape closes a modal-like disclosure and restores focus when such a pattern
  is used; ordinary inline `<details>` retains native behavior.

### Reduced motion

- `prefers-reduced-motion: reduce` produces no automatic state sequence;
- transition and animation durations for Home state changes compute to 0 ms;
- State 3 is available immediately and the same record identity, boundary and
  resolved meaning remain visible;
- no control label promises `play` when no motion will occur; use inspect/replay
  language appropriate to the resolved state;
- page geometry and reading order remain content-equivalent to normal motion.

### No JavaScript

- exactly five beats, one H1 and the complete default copy remain;
- all four proof states remain available in order;
- no inert tabs, play buttons, empty panels or `aria-hidden` content remain;
- navigation and every onward route remain ordinary links;
- a native disclosure is allowed, but its summary must identify the detail and
  it must open without JavaScript;
- the Hero and proof retain meaningful static states and intrinsic dimensions.

## 9. Accessibility contract

- Landmarks occur once and in order: header, main, footer.
- There is exactly one H1. Heading levels never skip and the visual hierarchy
  agrees with the semantic outline.
- Keyboard traversal reaches every interactive element once in DOM order.
- Focus is a 2 px ring with 2 px offset; Ink is used on warm ground and Paper on
  Ink ground.
- Every interactive target is at least 44 x 44 px; the mobile navigation
  control is at least 48 x 48 px.
- Color contrast is measured from computed foreground and composited ancestor
  background for every rendered HTML and SVG text node. Coral/Paper and
  Sage/Paper remain graphic-only pairs.
- Proof state changes have an accessible name and a polite status announcement;
  the announcement does not repeat the whole panel.
- Picture alt treatment is decided by information role. If the adjacent copy
  fully carries the Decision Field meaning, use empty alt. If the picture adds
  a distinct causal fact, use one concise semantic alternative, not an art
  description.
- At 200% desktop zoom, and independently at 320 px CSS width, content reflows
  without loss, overlap or two-dimensional document scrolling.
- Focus, selected, expanded and resolved states may not be communicated by
  color alone.

## 10. Image crop integrity

Hero art direction is a `<picture>`, not CSS background art. It has a desktop
composition and an independently authored portrait/mobile composition.

Machine gates:

1. `currentSrc` at 1440/1280/1024 differs from `currentSrc` at 768/390/320.
2. The desktop source has a landscape natural ratio between 1.45 and 1.75.
3. The mobile source has a portrait natural ratio between 0.72 and 0.90.
4. The rendered image has non-zero intrinsic width/height before load settles,
   preventing layout shift.
5. No required semantic image is fetched from a remote origin.
6. The proof uses a real responsive coded composition or a separately art-
   directed mobile asset; `object-position` on the desktop hero is not accepted
   as mobile art direction.

Visual gates at every capture:

- the coral judgment event remains visible;
- the path from imperfect operating reality toward an executable state remains
  legible;
- any sage boundary remains attached to the resolved side, not cropped into a
  decorative patch;
- the crop introduces no biological, tube, circuit, military, terminal or
  generic-AI ambiguity;
- the image does not dominate the page so completely that Dagg reads as a
  design studio;
- any Machine Signal is finite and subordinate to Decision Field.

These visual gates require screenshot review; DOM geometry cannot overrule a
bad crop.

## 11. Exact acceptance runner contract

The Home implementation package must add a runner at
`tools/capture_home_responsive_evidence.py`. This mapping does not implement it.
The runner must reuse `tools/serve_preview.py` and the accepted raw-CDP plumbing
from `tools/capture_p2_evidence.py` so every capture belongs to one immutable
snapshot.

The canonical copy count is computed from the rendered `[data-home]` route
root. Count the visible text of top-level `[data-copy-scope]` nodes only, so a
nested scoped node is not counted twice. Exclude `.cl-sr`, `aria-hidden`,
`hidden`, non-rendered and symbol-only text. Global header/footer, source
comments and metadata remain outside the route root. Record separate totals for
`default`, `progressive` and the Position beat.

Required command:

```sh
python3 -B tools/capture_home_responsive_evidence.py \
  --route / \
  --output evidence/HOME-RESPONSIVE
```

Required browser matrix:

```text
Chromium: 1440x900, 1366x768, 1280x720, 1024x768, 768x1024,
          390x844, 360x800, 320x800, 940x800, 939x800
Reduced motion: 390x844 and 1280x720
No JavaScript: 390x844 and 1280x720
200% zoom/reflow proxy: 1440x900 with 720px CSS viewport and 2x scale
```

The command exits non-zero unless every automated assertion below passes:

1. one snapshot ID appears in headers and HTML metadata for HTML, CSS, JS,
   fonts and images;
2. exactly one `[data-home]`, one H1 and five ordered beat hooks exist;
3. the ordered beat values are exactly
   `position,consequence,technology,proof,identity` at every viewport;
4. `document.documentElement.scrollWidth ===
   document.documentElement.clientWidth` in every state and viewport;
5. gutters, field cap, type endpoints, 940/939 collapse and line-count limits
   match this map;
6. the canonical default/progressive/Position count is exactly 519/0/59; it is
   within the 420-520, 0-100 and 55-90 content-contract ranges and the immutable
   run records the exact three values;
7. both technology hooks begin above `2 * innerHeight` at every required
   viewport;
8. every default-copy node has a non-zero rendered box in the full-page static
   state and is not hidden by a scroll-reveal class, opacity or clipping;
9. proof states are ordered 0-1-2-3 and all four are default-visible;
10. every visible text node, including SVG, is at least 12 px and passes its
    required computed contrast;
11. every target is at least 44 x 44 px and the mobile Menu is at least 48 x
    48 px;
12. keyboard order follows DOM order, focus is visible, Escape/focus return
    works where applicable, and hover/focus/tap reach equivalent states;
13. reduced motion schedules no automatic proof sequence, has zero Home
    transition/animation duration and exposes State 3 immediately;
14. no-JavaScript retains all five beats, all four proof states and every real
    route without inert enhanced controls;
15. desktop/mobile hero sources differ and pass the natural-ratio and intrinsic-
    size checks in section 10;
16. page height at 1280 x 720 is 3240-4320 px including footer;
17. no consecutive narrative-anchor gap violates section 7;
18. zero console errors, failed local assets, remote requests, duplicate IDs or
    placeholder links occur.

Required outputs from the same immutable run:

- `result.json` with every assertion, measured line counts, word counts,
  scroll/client widths, anchor gaps, current image sources and snapshot ID;
- full-page PNGs at all eight named product viewports;
- first-screen PNGs at 1440 x 900, 1280 x 720, 1024 x 768, 768 x 1024,
  390 x 844 and 320 x 800;
- normal, progression-focus, keyboard-focus, reduced-motion and no-JavaScript
  proof captures;
- a crop contact sheet pairing desktop and mobile Hero crops;
- captured accessibility outline and tab order;
- `tests-output.txt`, request log, console log and exact revision metadata.

### Platform smoke tests before visual acceptance

Automation is necessary but does not establish Mac/PC or touch truth alone.
The same snapshot must also pass:

- macOS Safari and Chrome at 1440 x 900;
- Windows Edge at 1366 x 768 and 1280 x 720;
- iPad Safari at 1024 x 768 and 768 x 1024, including rotation without reload;
- iPhone Safari-class touch at 390 x 844;
- a 320 px touch/emulation pass for smallest composition.

Each smoke test covers navigation, primary assessment action, proof interaction,
focus/tap parity, text selection, orientation/resize, image source, no overflow
and console/network health. Browser name, version, OS, viewport, snapshot ID and
result must be recorded. A platform that is not actually run is reported as
`not tested`, never inferred from Chromium.

## 12. Copy re-measure triggers

Run the complete copy and responsive suite again when any of the following
changes:

- H1, lead, body, CTA, link, disclosure, artifact label, proof state, header or
  footer wording;
- the conditional Impact route becomes enabled or disabled;
- default/progressive assignment or the initial proof state;
- font file, family, weight, size, line height, tracking, text transform or
  font loading behavior;
- content measure, gutter, grid gap, column split, collapse breakpoint or
  section padding;
- image aspect ratio, source selection, intrinsic dimensions, caption or crop;
- an icon gains visible or accessible text;
- a disclosure, tab, carousel, menu, form or state-control label changes;
- localization or punctuation normalization;
- a browser fix changes wrapping, font metrics, viewport units or intrinsic
  image sizing.

The re-measurement gate is not passed by preserving the same total word count.
It must re-check first-screen burden, line counts, reading order, technology
position, page height, disclosure assignment, crop integrity, keyboard/touch,
reduced motion and no-JavaScript.

## 13. Human visible-quality gate

After machine acceptance, Codex and Claude review the same exact-snapshot
desktop, iPad and mobile evidence. Reject Home if any view reads as:

- a consulting deck with repeated slide sections;
- a design studio led by abstract art rather than Dagg's business;
- a terminal, circuit, dashboard wall or generic AI template;
- a long explanatory essay despite passing the word budget;
- a sparse page whose hierarchy depends on empty space;
- a desktop page squeezed into mobile;
- a claim whose adjacent artifact does not prove or bound it.

Accept only when the sequence feels like one premium company system: warm
strategic authority, early named technology, one inspectable execution proof
and a bounded next move. Machine passes cannot overrule visible failure.
