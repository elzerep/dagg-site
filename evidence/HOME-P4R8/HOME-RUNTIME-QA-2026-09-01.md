# Home runtime QA — 1 September 2026

Status: **SUPERSEDED**. This file records the pre-narrative-repair Home
composition and is not acceptance evidence for the current route. Its PASS
statements are historical only; a new immutable run is required after the
content contract, three Home maps and rendered page agree.

Route: `/preview/golden-standard/home/`  
Source revision: P4R8R1 plus measured tablet art direction  
Reviewer: Codex  
Historical verdict: `PASS-RESPONSIVE-VISUAL` for the superseded revision;
motion and independent final Claude visual acceptance were not completed.

## What this verdict proves

- The current Home is visually coherent and usable at the tested desktop,
  iPad and phone widths.
- The first screen is strategically led, contains the named technology path,
  and uses the frozen calm Decision Field hero without terminal, dashboard,
  circuit-board or slide-deck framing.
- The complete Home narrative remains legible in one DOM order.
- Navigation, the adaptive Build flyout, the Home proof state control and the
  primary CTA paths work in the tested browser.
- The build is local only. This evidence does not authorize publishing.

## Rendered evidence

| Viewport | Evidence | Result |
|---|---|---|
| 1280 x 720 | `dagg-home-r1-1280-first.png`, `dagg-home-r1-1280-full.png`, `peer-comparison.html` | PASS. H1 two lines; 4112 px page height; no horizontal overflow; first screen credible beside the captured Anthropic, xAI and OpenAI references. |
| 1024 x 768 | `dagg-home-r1-1024-first.png` | PASS. Desktop split and landscape source retained; H1 three lines; no nav collision. |
| 768 x 1024 | `dagg-home-r3-768-first.png`, `dagg-home-r3-768-full.png` | PASS after visible repair. Portrait source remains authoritative; a measured 16:9 carrier held at 58% removes only quiet paper and keeps all protected events in the first screen. H1 two lines; 5206 px page height; no overflow. |
| 390 x 844 | `dagg-home-r1-390-first.png`, `dagg-home-r1-390-full.png` | PASS. Full portrait composition, single-column order, no horizontal overflow. |
| 320 x 800 | `dagg-home-r1-320-first.png` | PASS. 305 px client and scroll width; H1 four lines; minimum measured interactive target 44 px. |

The exact 940/939 boundary also passed:

- 940 px: desktop navigation, two-column hero and desktop image source.
- 939 px: mobile navigation, one-column hero and portrait image source.
- No document-level horizontal overflow on either side.

## Runtime interaction evidence

### Global navigation

- Desktop Build opens after pointer intent and defaults to `overview`.
- Hovering Dagg Factory and Agents and software updates both selected entry and
  proof inset without navigating.
- Escape closes the desktop flyout and restores focus to Build.
- Mobile Menu opens a full reading sheet, sets `aria-expanded=true`, locks page
  scroll and exposes all primary routes.
- Mobile Build opens the same four-destination DOM as stacked disclosures.
- Dagg Factory preview changes the single expanded preview state.
- Escape closes the mobile menu, clears the scroll lock and restores focus to
  Menu.

### Home proof

- Strategic decision, Governed execution and Accountable result are all
  default-visible.
- Each control updates the pressed state and the live status text.
- The ownership boundary and way back are never hidden by the interaction.
- No console errors or warnings were produced during the tested transitions.

### CTA paths

All six tested paths navigated to a real local route without a 404:

1. Start an assessment -> `/routes/assessment/`
2. See what must change -> `/chrome/routes/transformation/`
3. See how company context is retained -> `/chrome/routes/workgraph/#record`
4. See how context becomes a build -> `/chrome/routes/build/#factory`
5. Inspect the control model -> `/chrome/routes/trust/#permission`
6. See how Dagg takes responsibility -> `/chrome/routes/company/`

## Assembly evidence

`node tools/build_golden_standard_previews.mjs` and its `--check` mode pass all
seven assembly checks: shared hashes, current outputs, local references,
vector/icon policy, no-JavaScript completeness and no copied shared DOM.

## Copy state in the render

Historical note: this superseded P4R8R1 render carried 351 default-visible
words and zero progressive words under the then-current counting method. That
measurement and its former 280-360 budget are not evidence for the repaired
Home.

## Gates still open

1. Run the same route with real `prefers-reduced-motion: reduce` emulation and
   verify that no non-essential motion survives and no meaning disappears.
2. Obtain independent final Claude visual acceptance of the exact current
   screenshots. Claude already accepted the copy and implemented the source
   repair, but the final screenshot payload has not been sent externally in
   this pass.
3. Repeat the responsive and interaction audit in Safari/iPadOS and Edge before
   any production handoff.
