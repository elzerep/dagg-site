# evidence/COMPONENT-LIBRARY

Evidence for `design/golden-standard/packages/P4R5-COMPONENT-INTERACTION-SPECIMEN.md`.

Artefact under test: `preview/golden-standard/component-library/`
(`index.html`, `styles.css`, `script.js`).

## Contents

| File | What it is |
| --- | --- |
| `capture_component_library_evidence.py` | The whole rig. One command, one server snapshot, one Chrome process. |
| `check_class_coverage.py` | Static, browser-free check that every class used in `index.html` has at least one CSS rule. It exists because the failure mode this specimen actually hit was markup written against CSS that was never added, which renders unstyled while every machine check still passes. |
| `P4R5-REPAIR-RECORD.md` | The human-readable status of the P0 repair pass: what was fixed, what has and has not been rendered, and the interpretations that need a second reader. |
| `result.json` | Written by the rig. Revision, snapshot id, viewports actually measured, screenshot index, acceptance matrix, budgets, scope. |
| `states.json` | Written by the rig. The raw measurement of every interaction state it drove. |
| `acceptance-matrix.json` | Written by the rig. The machine-readable matrix P4R5 §8 requires. |
| `screenshots/` | Written by the rig. |
| `revision.json`, `server-stderr.txt` | Written by the rig. Provenance of the served snapshot. |

## Running it

```
python3 evidence/COMPONENT-LIBRARY/check_class_coverage.py
python3 evidence/COMPONENT-LIBRARY/capture_component_library_evidence.py
```

Exit code 0 means no matrix entry evaluated to `false`. It does **not** mean
the specimen passes — see the next section.

The rig lives here rather than in `tools/` because P4R5 §7 permits this
package to create files only under
`preview/golden-standard/component-library/`, `assets/vendor/lucide-dagg/`
and `evidence/COMPONENT-LIBRARY/`. It imports the existing P0R2 server
launcher and the P2 raw-CDP/Chrome plumbing from `tools/` rather than
duplicating either.

## What the rig will and will not decide

It measures. It does not grade its own rendering. CLAUDE.md rule 5 stands:
**machine tests do not overrule a visible rendering failure.**

Four deliberate properties:

0. **A missing control fails; it never crashes and never passes.** Every
   in-page read goes through `txt()`/`rect()`, which return `null` for an
   absent element instead of raising on `.textContent`, and every
   interaction step goes through `safe()`, which records the failure and its
   reason in `stepFailures` and fails the
   `everyInteractionStepActuallyRan` matrix row. The first implementation
   pass aborted the whole run on a null `textContent` when
   `[data-signal-carrier]` was on the hero figure while the status it looked
   for lived in the Machine Signal act; that class of abort is now a
   reported failure instead.

1. **A check is never asserted.** Every matrix entry carries the measurement
   it was derived from. Any check whose inputs are missing is written as
   `null` with a reason, never as a pass. `matrixUndecidedByMachine` lists
   them explicitly — currently the Factory pass duration and whether each
   protected hero crop preserves its coral decision and sage boundary. Those
   are for a human or for Codex to judge from the recorded timeline and the
   screenshots.

2. **Screenshot filenames carry the viewport Chrome reported**, from
   `window.innerWidth` × `window.innerHeight`, not the width that was
   requested. P4R5 §8 forbids labelling a larger capture as 390 px, so the
   requested and the measured width are both recorded per screenshot and a
   disagreement is visible in the filename itself.

3. **The no-JavaScript captures block the two exact local script URLs**
   (`script.js` and the shared `chrome.js`) with `Network.setBlockedURLs`
   rather than disabling the JS engine, so the rig's own `Runtime.evaluate`
   calls keep working and a real dispatched click can still open a native
   `<summary>`. The resulting failed loads are the intended condition, not
   page errors.

## States the rig drives

Viewports: 1440, 1024, 768, 390, 360, 320 — the exact set in P4R5 §5.

- default first-viewport and full-page capture at all six widths;
- Build flyout: closed, hover-intent open, mid close-grace, after
  close-grace, keyboard open, focus within, Escape with focus restoration;
- Build flyout proof inset: each of the four destinations driven by pointer
  hover, then the same four driven by real Tab traversal from the trigger,
  with the outer panel's rect compared across all eight states so a morphing
  inset cannot be confused with a moving panel;
- Build flyout on mobile: each of the four previews opened as a disclosure
  in the reading sheet, checked one-at-a-time;
- icons: every `.cl-ico` checked for being an `<img>` whose `src` is under
  `/assets/vendor/lucide-dagg/icons/`, with the document's inline `<svg>`,
  `<use>` and `<symbol>` counts all required to be zero;
- strategic continuum: each of the five outcomes;
- WorkGraph record: each of the four sources, plus roving tabindex under
  ArrowRight;
- Factory: the untriggered state, a twelve-sample timeline of one pass,
  mid-pass, paused, still-paused, resolved, replayed;
- two surfaces: both modes, with the persistent record's text compared
  across them;
- Machine Signal: the coarse before state, the one-shot control being run,
  the resolved state, and the resolved state re-measured 1.2 s later to
  prove it resolves once and stops — all as strata geometry (width,
  horizontal offset, thickness, opacity, colour), plus the protected hero
  image measured in the same pass so a filter, blur, overlay or blend mode
  standing in for the transition fails;
- keyboard: the full tab order at 1440 and 390, with every stop checked for
  inertness, hiddenness, rendering and a 2 px focus ring;
- mobile: menu closed, menu open, flyout open inside the menu, Escape;
- reduced motion at 1440 and 390;
- no JavaScript at 1440 and 390.

## Budgets checked

From P4R5 §5, verbatim: initial JavaScript ≤ 120 KB gzip, navigation ≤ 20 KB
gzip, CSS ≤ 45 KB gzip, initial mobile transfer ≤ 1.2 MB, hero asset ≤ 500 KB
desktop and ≤ 300 KB mobile. Gzip sizes are computed from the bytes the
snapshot server actually served; the hero figures are the bytes Chrome
actually selected from the `<picture>` at each viewport, re-fetched from the
same snapshot.
