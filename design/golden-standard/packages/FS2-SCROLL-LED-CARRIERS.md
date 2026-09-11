# FS2 — Scroll-led WorkGraph and Factory carriers

Status: **ACCEPTED FOR FS3 — 2026-09-02**  
Parent authority: `FS0-WHOLE-SITE-STAGING-AUTHORITY.md`  
Implementation owner: Claude Code  
Integration and acceptance owner: Codex

## 1. Objective

Give the supporting site its two primary intelligent-system moments without
turning either page into a demo that must be clicked.

- WorkGraph changes state as the reader moves through the retained-record
  lifecycle.
- Dagg Factory runs one finite causal pass when it enters view.
- Navigation, CTAs and optional inspection controls remain clickable.
- The core proposition is fully understandable before any click.

This is a trigger and composition revision, not a copy rewrite, image-language
reset or route redesign.

## 2. Read first

1. `CLAUDE.md`
2. `design/golden-standard/packages/FS0-WHOLE-SITE-STAGING-AUTHORITY.md`
3. `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`
4. `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
5. the three authority PDFs named and hashed in `CLAUDE.md`
6. `design/golden-standard/packages/P4R5B-COMPONENT-INTELLIGENCE-REVISION.md`
7. current WorkGraph and Build source files
8. `evidence/FULL-SITE-STAGING/FS1-VISUAL-QA.md`

## 3. Files owned by this package

Claude Code may edit only:

- `preview/golden-standard/routes/workgraph/src/body.html`
- `preview/golden-standard/routes/workgraph/src/direction.css`
- `preview/golden-standard/routes/workgraph/src/direction.js`
- `preview/golden-standard/routes/build/src/body.html`
- `preview/golden-standard/routes/build/src/direction.css`
- `preview/golden-standard/routes/build/src/direction.js`
- `evidence/FULL-SITE-STAGING/FS2-IMPLEMENTATION-REPORT.md`

The assembler may regenerate assembled pages. Do not hand-edit generated HTML.
Everything else is read-only, including shared chrome, tokens, images, Home,
Impact, metadata, content contracts and authority documents.

Codex independently owns `FS2-ACCEPTANCE.json`, screenshots and visual QA.
Claude must not write or pre-author its own acceptance result.

## 4. Binding interaction hierarchy

1. **Scroll carries the story.** A visitor who only scrolls sees the complete
   causal sequence.
2. **Autonomous motion is finite.** It runs once, shows cause then consequence,
   stops, and never loops by itself.
3. **Click is intentional.** It remains for navigation, CTAs, native details,
   optional source/plan inspection, Pause and Replay. It is never required to
   understand the mechanism.
4. **The page remains a website.** Do not create a terminal, fake app, canvas
   spectacle, circuit-board graph or dashboard wall.
5. **Only one focal system moves at a time.** Ambient image drift may not
   compete with the active carrier.

## 5. WorkGraph carrier

Use the existing lifecycle and retained-record material. Do not invent a new
record, source, claim or vocabulary.

### Required causal sequence

The same record identity persists through four states:

1. `OBSERVED / CONNECT` — approved work and sources become usable context.
2. `DECIDED / DECIDE` — intervention, reason, boundary and owner are retained.
3. `BUILT / BUILD` — Dagg Factory reads approved context rather than recreating
   the workflow.
4. `EVIDENCED / LEARN` — review or operating evidence returns to the same
   record and sharpens the next decision.

### Wide-desktop behavior (1180 px and wider, minimum viewport height 720 px)

- Recompose the existing lifecycle section into a readable sequence plus one
  persistent carrier.
- The narrative steps move normally with the page. The carrier may remain
  sticky within that section only.
- As each real narrative step crosses the viewport focus line, update one
  active state on the persistent carrier and the matching step.
- Preserve the same record identity, owner and permission boundary while state
  changes. This continuity is the point of the component.
- The last state remains resolved after the section is passed; scrolling back
  reverses the state deterministically.

At 940–1179 px, including typical 1024 px iPad landscape, use the ordered
inline sequence. Do not force the sticky carrier into a viewport that cannot
show the complete relationship comfortably.

### Tablet and mobile

- Do not use a tall sticky carrier below 1180 px or below 720 px viewport
  height.
- Present the four states as an ordered vertical sequence; a short highlight
  may follow the viewport, but every state and explanation remains visible.
- No horizontal scrolling, clipped labels or reduced type is permitted.

### Optional controls

- The existing Meeting / Document / System state source lenses may remain as
  optional inspection.
- All record fields are visible before using a lens. The lens may emphasize;
  it may not reveal otherwise hidden core meaning.
- Native details remain optional depth.

## 6. Dagg Factory carrier

Use the existing two build modes, plans and six-stage Factory progression.
Do not invent a third mode, extra product, client deployment or terminal UI.

### Required behavior

- Add a small dedicated sequence sentinel at the beginning of the Factory
  progression. Start one finite pass when that sentinel crosses the viewport
  focus line. Do not use a percentage of the whole tall progression as the
  trigger; it may be impossible to satisfy on a short viewport. `Run Factory
  pass` must not be the default entry condition.
- Advance in order:
  `Intervention → Specification → Architecture → Build → Evaluation → Governed review`.
- Use approximately 700–950 ms per stage on desktop and no more than 650 ms per
  stage on narrow screens. The exact timing may be tuned once in-browser, but
  the complete pass must feel deliberate rather than sluggish.
- The sequence stops on `Governed review` and never restarts itself.
- Preserve visible judgment holds at Intervention and Evaluation in coral.
  Only the final Governed review state uses sage.
- Pause when the carrier leaves the viewport, when pointer hover begins or when
  keyboard focus enters. Resume after the temporary interruption unless the
  user explicitly paused it.
- Pause while `document.hidden` is true and resume only under the same temporary
  interruption rule.
- Keep Pause and Replay as optional controls. Replay is available only after
  completion. A user-selected plan overrides the default demonstration and is
  not silently reset.

### No-JS and reduced motion

- No-JS exposes both plan summaries, both plan bodies and all six progression
  stages in semantic reading order. Nothing essential may depend on a class
  added by JavaScript.
- `prefers-reduced-motion: reduce` shows the resolved final Factory state
  immediately, with no timed sequence.
- If `IntersectionObserver` is unavailable, resolve immediately to the final
  state. Unsupported enhancement must never leave a blank, idle or half-run
  mechanism.
- On mobile the sequence is compact and non-sticky.

## 7. Copy and visual constraints

- Do not rewrite public copy. Existing lifecycle explanations may be moved out
  of an optional disclosure so they can carry the scroll sequence; wording must
  remain exact.
- Status text and ARIA labels may be added only to describe the current state.
- Reuse the current palette, typography, radii, borders, controls and media.
- Decision is coral, governed boundary is sage, machine precision is ink.
- Do not create new raster imagery, icons, illustrations or image composites.
- Do not change the Hero image or image-language mapping on either route.

## 8. Executable acceptance

Report actual values, not impressions.

### Zero-click comprehension

- A fresh route load followed only by scroll reaches all four WorkGraph states
  and all six Factory stages.
- No click is issued before those state changes are observed.
- All causal copy remains in the DOM and readable with JavaScript disabled.

### WorkGraph state mapping

- Crossing each of the four narrative steps produces exactly one matching
  active carrier state.
- Scrolling upward restores the prior matching state.
- Exactly one state is active at a time; the record ID and boundary remain
  unchanged.

### Factory state mapping

- The Factory starts once on first qualifying viewport entry.
- Stage order is exact and completion occurs once.
- The resolved state remains unchanged for at least five seconds after
  completion.
- Offscreen, hover and focus pauses are verified.
- Document-hidden pause and the no-`IntersectionObserver` resolved fallback are
  verified.
- Replay runs one new pass; explicit Pause does not auto-resume.

### Responsive and fallback matrix

- Verify 320, 360, 390, 768, 1024 and 1440 px.
- `scrollWidth` equals document client width at every viewport.
- No core text is below 11 px and no required target is below 44 px.
- Reduced motion resolves both carriers immediately; an unsupported observer
  does the same.
- No-JS reading order contains every public sentence and every state label.
- No console error is present.

### Preservation

- Run the existing assembler.
- Record hashes for every source file outside this package before and after.
- No shared chrome, Home, Impact, image, metadata or authority source may
  change.

## 9. Required report

Write failures first, then:

- exact files changed;
- the state and trigger implementation used;
- browser/viewports/states actually tested;
- zero-click, reduced-motion and no-JS results;
- source-preservation hashes;
- remaining FS3 and whole-site work;
- explicit statement that no deployment or publication occurred.

Return the package to Codex for visual integration review. Do not ask Christian
for approval and do not continue into Home.

## 10. Acceptance record

Codex accepted FS2 after responsive and interaction QA. The accepted browser
matrix, limitations and screenshots are recorded in:

- `evidence/FULL-SITE-STAGING/FS2-ACCEPTANCE.json`
- `evidence/FULL-SITE-STAGING/FS2-VISUAL-QA.md`
- `evidence/FULL-SITE-STAGING/FS2-CODEX-INTEGRATION.md`

Claude Code completed the owned source changes but reached its service usage
boundary before writing its implementation report. The separate Codex note
keeps that authorship boundary explicit.
