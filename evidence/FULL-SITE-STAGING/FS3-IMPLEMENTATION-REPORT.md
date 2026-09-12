# FS3 Home implementation report

Status: returned to Codex for independent Browser QA and visual acceptance  
Implementation date: 2026-09-02  
Package: `design/golden-standard/packages/FS3-HOME-INTEGRATION.md`

## Failures and unverified items first

1. Browser acceptance was not run by this implementation lane. There are no screenshots or measured rendered slots in this report; Codex owns Browser QA at 320, 360, 390, 768, 1024 and 1440 px.
2. The provisional Hero is a desktop working asset. Tablet and mobile are recomposed with CSS from the same raster; a separately art-directed mobile asset has not been supplied or accepted.
3. Visual claims including two-second Hero comprehension, crop quality, contrast, overflow, clipping, focus visibility, touch behavior and five-second post-sequence stability remain unverified in this implementation lane until Codex re-runs the assembled page in Browser.

## Files changed

- `preview/golden-standard/home/src/body.html`
- `preview/golden-standard/home/src/direction.css`
- `preview/golden-standard/home/src/direction.js`
- `evidence/FULL-SITE-STAGING/FS3-IMPLEMENTATION-REPORT.md`

No package, authority, asset, shared-chrome, token, component-library or supporting-route file was edited by this implementation lane.

## Authority used

Public copy is verbatim from the sole Home authority:

- `design/golden-standard/narrative/HOME-NARRATIVE-FOUNDER-RESET.md`

The six public acts are present in the required order. Supporting interface labels only identify the illustrative retained record and its four execution states.

The following visual-system authorities were read in full and their rendered pages inspected before implementation:

- `Dagg-Image-Language-System.pdf`
- `Dagg-Design-System-Foundations.pdf`
- `Dagg-Component-and-Interaction-Library.pdf`

Package, masterplan, FS0, FS2 invariants, component-intelligence revision, founder addendum, image protocol and image-library catalog were also used as source authority.

## Image asset and authored slots

Working Hero asset:

- path: `design/golden-standard/image-system/home/home-hero-decision-field-provisional-v3.png`
- intrinsic dimensions: 1672 x 941 px
- SHA-256: `094f9ed09f04448881c50aef9b2919b05198c8c17ef8c144063c10b9e146f6b5`
- status: provisional composition placeholder, not final visual acceptance

Authored CSS slots, pending Browser measurement:

- desktop: full-bleed Hero, `min-height: min(840px, calc(100svh - 68px))`, cover crop
- tablet: Hero visual recomposed into the lower 47 percent of the opening scene
- mobile: 780 px opening scene with the visual in the lower 38 percent

The Hero contains one Decision Field image only. Operational Evidence and Machine Signal are excluded from the Hero.

## State and trigger implementation

- Four semantic states are present in source order: Operating reality, Decision retained, Governed execution, Evidence returns.
- A dedicated nonvisual sentinel starts one causal sequence when the execution artifact enters the viewport (`IntersectionObserver` threshold 0).
- Three 300 ms state transitions give a 0.9 second complete transition.
- The sequence stops on the resolved state and does not loop.
- Full-artifact viewport exit and document visibility pause an active sequence; pointer and keyboard users control Pause/Resume explicitly.
- Pause/Resume and Replay are optional enhanced controls; neither is required to understand the story.
- The Home source root carries `data-home`, so the behavior initializes both as a source fragment and after assembly.

## Source and interaction checks

- `node --check preview/golden-standard/home/src/direction.js`: PASS.
- Six H1/H2 story headings found in required causal order: PASS.
- Four execution-state nodes found: PASS.
- One Hero image reference found: PASS.
- Remote asset references, inline SVG, data images and route-owned shared chrome found in Home source: none.
- Assembler static contracts: seven PASS, including byte-current generated outputs.
- Browser/viewports/interactions: NOT RUN in this lane; explicitly handed to Codex.

## Word counts

Source-level count, excluding hidden enhanced controls:

- default-visible Home copy: 499 words
- first viewport: 40 words

The first viewport is within the corrected 35-55 word band and contains only eyebrow, H1, lead and two actions. During the sequence, the two-word control replaces two words removed by the shorter live status, keeping the visible total within the 430-500 band.

## Fallbacks

- No JavaScript: all six acts and all four execution states remain in semantic reading order; optional controls remain hidden.
- Reduced motion: the execution artifact resolves immediately to Evidence returns.
- Missing `IntersectionObserver`: the execution artifact resolves immediately.
- CSS explicitly preserves the `hidden` state of the control wrapper and individual control buttons.

These fallbacks are source-verified only; Browser execution remains for Codex.

## Preservation hashes recorded after implementation

Shared substrate, unchanged by this package:

- header: `dd827a94208e5c3c3366d87db0b17d108d446d756b58bc74611371fe932475bb`
- footer: `070c5e66f6b605936066a4bb29d0d82d34924fcbc3b15028785b6bd77756db2a`
- chrome CSS: `4909454a75dde120d2968a245957735197e7281dcb15b9c7f24e0d186ace53df`
- chrome JS: `544e590b4c2b19d81c967625eea4ea409f9b71c68a355e46e9c750d97125e3b0`
- tokens: `68005110f62bf2f476a4e842497ae8423bd6e8cb8add75c43d99a70f6268803e`
- component CSS: `759818148af7ec0d751b4348023dda4444d6b09f286313a18efb18b41cedf31c`
- component JS: `165ea42d7ca2d4daa15224e0c442430c7c3c8661102591f0be56c86228e2b2ac`

The assembler source check confirms identical shared hashes across all 19 assembled pages. Supporting route sources were not modified by this package.

## Remaining whole-site work

1. Re-run Codex Browser QA at all six required widths, including the repaired pointer/keyboard controls, reduced-motion, no-observer, no-JS, overflow, link and console checks.
2. Judge the provisional Hero for comprehension, cropping and calm confidence; replace or art-direct a mobile asset if needed.
3. Run the independent visual red-team against the FS3 rejection criteria.
4. Continue only through the next active whole-site staging package after FS3 acceptance.

Nothing was deployed or published. Nothing was committed or pushed.

## P1 repair after initial Browser QA rejection

Codex rejected the first FS3 assembly for two exact mobile defects. Both were repaired without changing the composition:

1. At 390 x 844, the closing secondary CTA escaped the 350 px action row and produced a 732 px document width. The mobile `.home-actions` contract is now an explicit one-column grid, and every action button is constrained to `width: 100%` and `max-width: 100%`.
2. The execution artifact was taller than the mobile viewport, so a 55 percent intersection ratio was unreachable. A dedicated nonvisual sentinel now starts the zero-click sequence as its leading edge enters the viewport. A separate observer watches the full artifact only for fully-offscreen pause and visible-again resume.

The finite duration remains 0.9 seconds. Reduced-motion, missing-observer and no-JavaScript fallbacks remain unchanged. Browser re-acceptance remains with Codex.

## P1 repair after control interaction rejection

Browser QA found that card-level hover/focus pausing could immediately override an explicit Resume action while the activated control retained focus or pointer occupancy. Ambient card hover/focus pausing has been removed. Pause/Resume and Replay now own their explicit control state without interference. Full-artifact offscreen pause/resume and document visibility pause/resume are preserved, as are the 0.9 second duration and all capability fallbacks.
