# P4R5 · repair record for the first implementation pass

Scope: the four verified P0 defects in the Component and Interaction
Specimen, plus the rig changes that make a fresh run able to report them.

Sources read in full before this repair, as CLAUDE.md requires:

- `/Users/christianperez/Downloads/Dagg-Image-Language-System.pdf` — all 14
  pages;
- `/Users/christianperez/Downloads/Dagg-Design-System-Foundations.pdf` — all
  15 pages;
- `design/golden-standard/packages/P4R2-THREE-WAY-DIRECTION-GATE.md`,
  including the exact derived page map in §2;
- `design/golden-standard/packages/P4R5-COMPONENT-INTERACTION-SPECIMEN.md`,
  `P4R4-CHRISTIAN-AUTHORITATIVE-ADDENDUM.md`,
  `P4R3-PRE-SLICE-COMPONENT-CONTRACT.md`,
  `design/golden-standard/image-system/IMAGE-PRODUCTION-PROTOCOL.md`.

## Status, failures first

**The repaired specimen has not been rendered in a browser in this session.**
Chrome could not be launched and neither the evidence rig nor any script
could be executed: this sandbox refused every attempt to run `python3
<script>`, `python3 -m py_compile`, `python3 -c` and `node --check`. No
screenshot, no acceptance matrix and no pass value in this directory has
been regenerated. Nothing below is a claim of browser acceptance. Codex must
run the rig outside the sandbox before any of this is treated as verified.

Consequences that follow honestly from that:

- the four Build preview states, the Machine Signal geometry and the icon
  swap are **implemented and statically reviewed, not seen rendered**;
- `result.json`, `states.json`, `acceptance-matrix.json`, `revision.json`
  and `screenshots/` in this directory are stale artefacts of the crashed
  first run, or absent. They have deliberately not been hand-written;
- the Python and JavaScript in this change have not been byte-compiled or
  syntax-checked by a tool. They have been read back and reviewed by hand.

## P0-1 · the Build flyout had no real preview states

Before: the header flyout's four destinations were nested `<details>`
disclosures with no CSS at all, and the standalone demo instance had a
single hard-coded proof card that never changed. That is the P4R5 §4.1 P0
("a permanently static right-hand inset is a P0 failure").

After, in both live instances:

- one left-hand list of four real destinations, each still an ordinary link
  to a real route;
- one right-hand proof inset with four states — Build overview (strategic
  decision → bounded build brief), Dagg Factory (requirement → product
  decision → evaluation), Agents and software (agent around an existing
  system ↔ rebuilt workflow layer), Trust and operation (proposed action →
  governed boundary → accountable human decision);
- the first state carries the conclusion `One operating decision becomes a
  buildable, governed system.`;
- `pointerenter` and `focus` on each destination select that destination's
  state, so hover and keyboard focus produce the same four states;
- 85 ms open intent, 210 ms close grace, 120 ms content crossfade, 200 ms
  height morph of the inset only. The outer panel is pinned by
  `min-height: calc(var(--fp-max-h) + 2 * var(--space-4))`, measured once
  from the tallest state, so the panel cannot jump, flicker or reposition
  while the inset morphs;
- the pointer corridor is unbroken: the panel is a descendant of the
  `<details>` and an `::after` bridge spans the 14 px gap, so moving from
  the trigger through the list into the inset never leaves the flyout;
- Escape closes and restores focus to the trigger (unchanged behaviour,
  still wired);
- reduced motion swaps state with no morph and no transition;
- below 940 px each item becomes a real per-destination disclosure in the
  reading sheet, with a 48 px tap control created by script.js so the
  no-JavaScript DOM contains no inert control.

The four states and the four mobile disclosures are the **same DOM**. At
desktop the list and its items are `display: contents`, so the links stack
down column 1 of the panel grid and all four states share the single
column-2 area; inactive states are `visibility: hidden`, which keeps them in
layout (so the panel height is stable) while removing them from the reading
order and the accessibility tree. Nothing is duplicated.

No chat UI, dashboard, typing effect, particle field or new visual language
was introduced: each state reuses the same meta / chain / pair / claim
components the rest of the page already uses, in the ink instrument
register at the 14 px instrument radius (Foundations p.10).

## P0-2 · the Machine Signal was wired to the wrong element

Before: `[data-signal-carrier]` sat on the Home hero `<figure>` while
`[data-signal-status]`, `[data-strata]` and `[data-signal-control]` lived in
the separate Machine Signal act. The rig's `carrier.querySelector(
'[data-signal-status]').textContent` therefore raised on `null` and took the
whole run down, and the visible "transition" that remained in CSS was
`filter: blur(5px) saturate(.62) contrast(.88)` on the protected hero
photograph plus a scan-line overlay — an image treatment standing in for a
semantic state change.

After:

- the hook is on the Machine Signal component. The hero figure carries
  `data-protected-hero` and nothing else;
- the blur/saturate/contrast filter, the `.cl-carrier__grain` overlay and
  the dead `.cl-signal__state`/`__arrow`/`__spec` rules are deleted;
- the transition is real geometry on five strata: horizontal offset
  (`margin-left`), width, opacity and thickness. Coarse means short, offset
  from the shared origin and faint, with no coral and no sage anywhere.
  Resolved means aligned on one origin at full width and full opacity, with
  coral appearing exactly once at the judgment stratum and sage arriving
  only as the boundary verifies (ILS p.10 RESOLVE, p.11 REQUIRED);
- one 900 ms pass, run by a one-shot control that is removed once the pass
  resolves. Because the pass is under one second, P4R5 §4.4 and ILS p.11
  give it no replay, and no dead control remains;
- reduced motion resolves immediately with the control hidden; with
  JavaScript absent the resolved state is the document default and the
  control host keeps its `hidden` attribute, so no inert control exists.

**Interpretation to flag:** §4.4 says "a finite Machine Signal before/after
control that resolves once and stops; provide replay only if the transition
exceeds one second." Read literally, the *control* is the thing that
resolves once, and the replay clause only makes sense if there is a control
to press. It is therefore implemented as a user-operated one-shot rather
than an on-scroll autoplay. The trade-off is that a reader who never presses
it sees only the coarse state; the resolved state is still the no-JS and
reduced-motion default, and the labels are identical in both states. If
Codex reads §4.4 the other way, the change is one branch in `initSignal`.

## P0-3 · the asset rule was violated by an inline SVG sprite

Before: `index.html` carried a `<symbol>` sprite with Lucide path data
copied verbatim into the document, every icon was an inline `<svg><use>`,
and `script.js` built icons with `innerHTML = '<svg …><use …></svg>'`.

After: every icon is the vendored official file referenced as a real image
element — `<img src="/assets/vendor/lucide-dagg/icons/<name>.svg">` — in both
the document and `script.js`, which now creates icons with
`document.createElement("img")` and never writes markup. The sprite, every
inline `<svg>`, every `<use>` and the `.cl-sprite` rule are gone.

Warm/ink contrast is preserved without redrawing anything: an `<img>` cannot
inherit `currentColor`, so the vendored black stroke paints as-is on the
warm ground, and ink grounds apply `filter: invert(1)` — an exact tonal
inversion of a monochrome stroke, so Paper-on-Ink equals Ink-on-Paper. Muted
registers use opacity rather than a second asset.

Icons actually referenced: `chevron-down`, `menu`, `x`, `arrow-up-right`,
`play`, `pause`, `rotate-ccw`. `external-link.svg` is vendored but unused.
P4R5 §7 permits "only the required icons plus upstream license", so it is
either out of scope or a pending requirement; it pre-dates this repair and
has been left in place rather than deleted unilaterally. Flagging it for
Codex.

**Known consequence, stated rather than hidden:** the small inline arrow
beside a coral text link now paints ink rather than coral, because an
`<img>` cannot take the link's colour. This is a direct cost of the asset
rule. The alternative — a hand-tuned `filter` chain approximating coral — is
a redrawn icon in all but name, so it was not used.

## P0-4 · the Home thesis pair

Unchanged and still wired: `home-hero-operating-model-v1.webp` (desktop,
1586 × 992) and `home-hero-operating-model-v1-mobile.webp` (art-directed
4:5, 960 × 1200), each delivered through its own `<picture>` with explicit
dimensions and `sizes`. The PNGs remain source masters and are not
referenced. The figure now also carries `data-protected-hero` so the rig can
prove no treatment is applied to it.

## P0-5 · the rig can no longer crash, and now tests the repairs

- every in-page read goes through `txt()` / `rect()`, which return `null`
  for a missing element instead of raising on `.textContent`; `record`,
  `factory`, `surfaces` and `signal` each report a `missing` list naming the
  selectors that were not found;
- every interaction step goes through `safe()`, which records the failure
  and its reason in `stepFailures` and fails the new
  `everyInteractionStepActuallyRan` row. A step that could not run is never
  reported as a pass;
- icon checks were rewritten for vendored `<img>` assets: every `.cl-ico`
  must be an `IMG` whose `src` is under `/assets/vendor/lucide-dagg/icons/`
  and must have decoded, and the document's inline `<svg>`, `<use>` and
  `<symbol>` counts must all be zero;
- new rows: `flyoutProofInsetHasFourDistinctStates`,
  `flyoutProofInsetFollowsPointerHover`,
  `flyoutProofInsetFollowsKeyboardFocus` (driven by real Tab traversal from
  the trigger, not by a scripted `.focus()`),
  `flyoutOuterPanelDoesNotMoveWhileTheInsetMorphs`,
  `mobilePreviewsAreOneAtATimeDisclosures`,
  `noInertPreviewControlWithoutJavaScript`,
  `machineSignalIsWiredToItsOwnComponent`,
  `protectedHeroCarriesNoTransitionTreatment`,
  `machineSignalIsResolvedWithoutJavaScriptAndUnderReduce`,
  `everyIconIsAVendoredLucideImageAndNoInlineSvgExists`,
  `everyInteractionStepActuallyRan`;
- `machineSignalResolvesOnceAndHolds` was rewritten from "the class is gone
  and the image filter is none" to a geometry comparison: coarse offsets and
  widths before, one shared origin at full width and full opacity after, no
  coral or sage before, coral only at `judgment` and sage only at
  `boundary` after, the control present before and gone after, and the
  resolved state re-measured 1.2 s later to prove it stops;
- `everyRequiredStringPresent` now checks the union of text **actually
  rendered** across the captured states rather than the default state alone.
  A closed flyout's panel computes `display: none`, so the previous check
  would have reported the flyout's own copy as missing from a page that
  renders it correctly the moment the flyout opens. No string is asserted
  from source;
- no existing check was removed, relaxed or given a wider tolerance.

## Also repaired, because it would have been a visible rendering failure

The first pass shipped markup for which no CSS had been written:
`.cl-preview*` (the header flyout's four nested disclosures), `.cl-strata*`,
`.cl-signal__head`, `.cl-signal__control`, `.cl-evidence*`,
`.cl-section--medium`, `.cl-head--rail` and `.cl-carrier--wide`. Meanwhile
`.cl-oe*` styles remained for markup that no longer existed. Every one of
those blocks would have rendered unstyled while every machine check passed.
All are now styled, the dead `.cl-oe*` rules are removed, and
`check_class_coverage.py` is a browser-free guard against the same class of
regression.

The specimen also no longer animates itself on load: `html.cl-booting`
suppresses transitions for the first two frames while enhancement writes its
initial states, so setting up the coarse Machine Signal geometry does not
read as a state change.

## Files changed by this repair

- `preview/golden-standard/component-library/index.html`
- `preview/golden-standard/component-library/styles.css`
- `preview/golden-standard/component-library/script.js`
- `evidence/COMPONENT-LIBRARY/capture_component_library_evidence.py`
- `evidence/COMPONENT-LIBRARY/check_class_coverage.py` (new)
- `evidence/COMPONENT-LIBRARY/README.md`
- `evidence/COMPONENT-LIBRARY/P4R5-REPAIR-RECORD.md` (this file)

All are inside P4R5 §7 file ownership. No P4R4 file, Home slice, shared
token, shared chrome file, PDF, image portfolio, masterplan, route stub or
deployment configuration was touched.

## Page-map rows this repair is accountable to

From the exact derived page map in `P4R2-THREE-WAY-DIRECTION-GATE.md` §2 and
`Dagg-Image-Language-System.pdf` p.13:

| Row | Primary | Support | Bearing on this repair |
| --- | --- | --- | --- |
| Home hero | Decision Field | Machine Signal | The protected hero is Decision Field and is now free of any treatment; the Machine Signal support is a separate, finite, geometric act — never a filter on the A image. Operational Evidence is still absent from the hero, as the row requires. |
| Build | Operational Evidence | Machine Signal | The Build flyout's proof inset is contained Operational Evidence in the ink register; it proves that a requirement resolves into a governed, verified build, and it does not import Decision Field imagery. |

Whether the rendered page passes those rows is a visual judgement on
rendered states. **This repair cannot claim it**, because no state was
rendered in this session.
