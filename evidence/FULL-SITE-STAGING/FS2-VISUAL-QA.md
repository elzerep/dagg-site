# FS2 visual QA — scroll-led WorkGraph and Factory carriers

Date: 2026-09-02  
Routes: `/preview/golden-standard/routes/workgraph/`, `/preview/golden-standard/routes/build/`  
Decision: accepted for FS3 Home integration; no deployment or publication occurred.

## Failures and limits first

1. Claude Code completed the six owned source files, then reached its service
   usage boundary before it could write the package's implementation report.
   Codex integrated the byte-identical source files and owns this acceptance;
   this document does not misattribute a missing Claude report.
2. Pointer-hover, keyboard-focus, `document.hidden`, reduced-motion and missing
   `IntersectionObserver` logic were inspected in source. Explicit Pause,
   Resume and Replay were exercised in the browser. Synthetic runtime coverage
   for the remaining fallback paths is deferred to final cross-route QA.
3. The WorkGraph and Build heroes remain intentionally outside FS2. WorkGraph
   still opens with more empty space than the final site should carry. Route
   pacing and hero refinement belong to the later whole-site polish pass.
4. Screenshot inspection does not prove full WCAG compliance. Screen-reader
   output, high zoom and the complete keyboard order remain final-QA work.

## Accepted screenshots

1. `visual-qa/06-workgraph-fs2-learn-1440.png` — WorkGraph desktop, resolved
   Learn state and persistent `WG-034` record.
2. `visual-qa/07-build-fs2-evaluation-1440.png` — Factory desktop, coral
   Evaluation judgment hold.
3. `visual-qa/08-build-fs2-review-1440.png` — Factory desktop, sage governed
   review and stable completion.
4. `visual-qa/09-workgraph-fs2-inline-390.png` — mobile ordered WorkGraph
   sequence with no sticky mechanism.
5. `visual-qa/10-build-fs2-review-390.png` — mobile Factory progression with
   Replay after completion.

Each file is the exact screenshot captured from the assembled FS2 revision in
the current in-app Browser run.

## Visible and interaction result

FS2 passes its purpose: scrolling now carries the core story, while click is
reserved for optional inspection and direct control.

- WorkGraph advances `Connect → Decide → Build → Learn`; scrolling upward
  restores the matching previous state. `WG-034`, its owner and `Prepare only.
  Never release.` remain continuous.
- At 1440 x 900 the record is sticky inside the lifecycle only. At 1024 px and
  below the complete ordered sequence is inline and readable.
- Factory starts one finite pass on entry, advances through all six stages and
  stops on Governed review. The resolved state remained unchanged for more
  than five seconds.
- Judgment holds remain coral at Intervention and Evaluation; only the final
  governed state is sage.
- Pause, Resume and Replay work. Selecting `Rebuild what should change`
  persists through Replay and completion instead of silently returning to the
  default plan.
- Browser logs contained no errors.

## Responsive matrix

| Viewport | WorkGraph | Factory | Overflow | Required controls |
| --- | --- | --- | --- | --- |
| 320 x 720 | ordered inline | finite sequence | none | 44 px or larger |
| 360 x 800 | ordered inline | finite sequence | none | 44 px or larger |
| 390 x 844 | ordered inline | finite sequence | none | 44 px or larger |
| 768 x 1024 | ordered inline | finite sequence | none | 44 px or larger |
| 1024 x 768 | ordered inline | finite sequence | none | 44 px or larger |
| 1440 x 900 | sticky carrier | finite sequence | none | 44 px or larger |

At 768 px the automated centering helper initially left Learn nine pixels
before the focus line; a normal additional 40 px scroll activated it. The
interaction passed. The first observation was a test-harness centering issue,
not a missing state.

## Static fallback and preservation result

- Both route scripts resolve immediately when reduced motion is active or
  `IntersectionObserver` is unavailable.
- The Factory pauses on focus entry, pointer entry and document visibility
  changes and distinguishes temporary suspension from explicit pause.
- With JavaScript disabled, both plans, all six Factory stages and all four
  WorkGraph states remain in semantic reading order.
- The assembler passed: 19 assembled pages, 20 files written; no inline SVG,
  text-symbol icons, shared DOM copies or broken local references.
- Home, Impact, Assessment, Transformation, Company, Trust and shared chrome
  source hashes remain identical to the FS1 baseline.

## Decision

Accept FS2 and activate FS3. The two carriers are strong enough to summarize on
Home without importing their full deep-page UI. Home must now use the six-act
founder reset, a Decision Field-only hero, one connected WorkGraph-to-Factory
record and a separate finite Machine Signal passage.

