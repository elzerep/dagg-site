# P4 design QA

Status: blocked pending correction round 1  
Reviewer: Codex  
Date: 30 August 2026

## Compared evidence

- source truth: `design/golden-standard/image-system/direction-a-decision-field/01-hero-decision-field.png`
- implementation: `preview/golden-standard/p4/selected/index.html`
- combined comparison: `/tmp/p4peek/comparison-hero-1440.png`
- inspected desktop render: `/tmp/p4peek/full-1440.png` at 1440 px
- inspected mobile render: `/tmp/p4peek/full-390.png` at 390 px
- section and navigation states: `/tmp/p4focus/`
- automated audit: `/tmp/p4audit.json`

The primary image asset and the rendered hero were inspected together at the
same desktop state. The implementation preserves the tactile paper field,
graphite structure, coral intervention and sage boundary of the selected image
direction. The following failures prevent operating acceptance.

## Blocking findings

1. **Reading ground becomes a dark chapter.** WorkGraph and Factory are two
   consecutive full-width Ink sections. P4 freezes Ink as a contained product
   instrument and the warm field as the reading ground. Keep their headings,
   explanation and closing lines on warm Paper or Lift; keep the interactive
   records themselves as contained Ink instruments.
2. **Hero measure does not meet the P1 contract.** The H1 renders on four lines
   at 1440 and 1280, and five lines at 1024 and 940. The accepted desktop limit
   is 2.5 lines. Correct composition or typography without changing the frozen
   sentence.
3. **Horizontal overflow at 940 px.** The audit measured a 952 px scroll width
   in a 940 px viewport. The right edge of `.chrome-header__cta` lands at
   952.30 px. Correct this in P4-owned CSS; do not edit the accepted P3 chrome.
4. **Mobile assessment list breaks its punctuation.** Separator dots can wrap
   as orphaned marks at 390 and 320. On mobile, remove those separators or
   recompose the deliverables as a stable list.

## Required verification after correction

- viewports: 1440x1000, 1280x800, 1024x768, 940x800, 768x1024,
  390x844 and 320x568;
- zero horizontal overflow at each exact width;
- all Decision, WorkGraph and Factory states remain distinct and operable;
- no-JavaScript and reduced-motion modes expose complete terminal meaning;
- no console errors or failed local assets;
- source and corrected hero screenshot compared together again;
- section anchors land below the sticky header and do not create clipped
  headings.

## Non-blocking follow-up

The sentence "Impact separates companies built from companies transformed"
is not publication-quality English. It is frozen P1R1 copy and therefore must
be corrected through a separate, explicit narrative amendment rather than by
P4 implementation improvisation.

## Initial audit facts

- minimum visible text size: 12 px or greater at all audited viewports;
- console errors: zero;
- no-JavaScript: complete Decision, WorkGraph, Factory and operating states
  remain available;
- reduced motion: terminal meaning remains visible;
- 200 percent zoom: no horizontal overflow;
- measured H1 lines: 4, 4, 5, 5, 3, 5 and 7 across the seven viewports.

## Result

Blocked. Do not freeze P4 and do not start P5-P9 implementation from this
revision.
