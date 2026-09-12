# P4R3 · Pre-slice component and interaction contract

Status: binding input to the three browser slices  
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Inputs: `P2-FOUNDATIONS.md`, `P3-GLOBAL-CHROME.md`,
`P4R2-THREE-WAY-DIRECTION-GATE.md`, the approved Foundations PDF and the
approved Image Language PDF

## 1. Sequence and ownership

The component and interaction system is defined before the slice, validated
through the slice, and frozen into the final library after Christian accepts a
slice.

This document is the pre-slice contract. It prevents each direction from
inventing its own controls, radii, motion, typography or responsive behavior.
The final Component and Interaction Library is a reconciled record of the
accepted implementation, including code references, variants and verified
states. It is not permission to improvise during P4R3.

## 2. Frozen primitives

All directions inherit without variation:

- palette, typography, grid, spacing, radii, focus and motion tokens from
  `system/tokens.css`;
- the global header, mobile disclosure, Build flyout and assessment action
  from P3;
- one warm page ground, no more than three meaningful ground changes and one
  contained ink instrument at a time;
- a 1240 px field, 12 columns, 7/5 strategic split, optional 45/55 product
  split and a 940 px collapse;
- Geist for headings, controls and interface; Newsreader for explanation and
  judgment; JetBrains Mono only for genuine metadata;
- 44 px minimum actions, 48 px mobile navigation controls and the frozen 2 px
  focus treatment.

## 3. Allowed composition primitives

The three slices may compose only these primitives:

1. **Executive opening** — conclusion-led H1, one short lead and two actions.
   It may be typographic, 7/5 or 45/55; it may not become a full-screen image.
2. **Decision Field moment** — one bounded real image asset with an explicit
   idea, caption or adjacent mechanism. It is never a decorative background.
3. **Editorial punctuation** — one short conclusion in a 240–360 px act.
4. **Decision continuum** — the five outcomes Preserve, Simplify, Automate,
   Rebuild and Retire. Native content remains complete without JavaScript.
5. **Operational instrument** — one inspectable WorkGraph, Factory or operating
   record. It is a coded interface, not a generated product screenshot.
6. **State rail** — a small set of real controls changing one carrier in place;
   no carousel of decorative panels.
7. **Evidence caption** — provenance, boundary and what the artifact proves.
8. **Text link and primary action** — direct destination and accurate label.

No card grid, decorative dashboard, terminal wall, feature inventory, generic
network graph or image-per-section pattern is available to a direction.

## 4. Component states

Every interactive component supplied to Christian must include:

| Component | Required states |
| --- | --- |
| Header | warm, ink, desktop, compact desktop, mobile closed, mobile open |
| Build flyout | closed, hover-intent open, keyboard open, focus within, delayed close |
| Action | rest, hover, focus-visible, active, disabled only when truthful |
| Decision continuum | complete no-JS record, collapsed choices, one open choice, keyboard focus |
| State rail | complete no-JS sequence, selected state, changed carrier, resolved state |
| Instrument | loading is not shown; default, human-decision, governed and exception states |
| Motion | initial, causal transition, resolved, paused/replay when one-pass exceeds 1 s |

Hidden content must not remain focusable. A control may not imply a route or
state that does not work.

## 5. Interaction grammar

- Hover intent opens the Build flyout after 70–100 ms; leaving both trigger
  and panel closes it after 180–240 ms.
- Enter and Space activate disclosures; Escape closes and restores focus.
- Micro response is 180 ms; component/state response is 240 ms. There is no
  spring, overshoot or ambient loop.
- Machine Signal is a finite state change inside a bounded carrier. It is not a
  page theme, background animation or decorative pulse.
- One moving focal point is permitted in a viewport.
- `prefers-reduced-motion: reduce` snaps position and size to the same resolved
  meaning. It does not delete labels, proof or the final state.
- Without JavaScript, all core content, routes and the resolved causal record
  remain legible.

## 6. Image slots

Image language governs a slot after layout has assigned its job. It never
determines section height.

| Slot | Permitted language | Constraint |
| --- | --- | --- |
| Home hero | Decision Field + finite Machine Signal | One bounded carrier; no full-bleed generated art; Operational Evidence is separate. |
| Strategic act | Decision Field | One idea and one caption; may be absent when type carries the act. |
| Product proof | Operational Evidence | Coded, inspectable and contained; generated material may only frame it. |
| Transition | Machine Signal | Finite before/decision/after behavior; resolved frame works alone. |

The 70/25/5 hierarchy describes the distribution of governed image-language
moments across the system. It is not a target for viewport area, section height
or the amount of generated imagery.

## 7. Responsive contract

- Desktop targets: 1440 and 1024. Mobile/tablet targets: 768, 390, 360 and 320.
- Mobile is recomposed; it is not a desktop grid stacked without judgment.
- Semantic reading order is identical across breakpoints.
- No document-level horizontal overflow.
- Product panning, if unavoidable, is contained in a labelled focusable region.
- Navigation and CTA never cover content or become unreachable.
- H1 remains within the frozen line-count rule and body copy remains at least
  17 px.

## 8. What the three directions may vary

Only these variables may differ at the direction gate:

- commercial entry point and final copy;
- opening composition: typographic, 7/5 or 45/55;
- which accepted component carries the primary proof;
- the order and relative height of the same bounded acts;
- the interaction model inside the proof: decision continuum, retained context
  or before/decision/after state.

Palette, type roles, navigation, focus, motion grammar, semantic colors,
component anatomy and truth boundaries do not vary.

## 9. Pre-slice acceptance gate

No direction is reviewable until:

1. every visible element maps to a component in this contract;
2. all copy is final-quality and within the copy ceilings;
3. all image assets occupy declared slots;
4. desktop and mobile are both authored;
5. no-JS and reduced-motion states preserve the complete meaning;
6. navigation, flyout, controls and both CTA paths work;
7. the direction has been compared with fresh peer screenshots at the same
   viewport and does not read as a slide, design studio, terminal or template.

## 10. Post-selection library

After Christian accepts one slice, reconcile this contract against the exact
implementation. Remove unused theoretical variants, add any verified variant
that the accepted composition genuinely required, link every item to code and
test evidence, then publish the final Component and Interaction Library PDF.

