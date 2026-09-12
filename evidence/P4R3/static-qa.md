# P4R3 static QA

Date: 2026-08-31  
Scope: pre-browser structural checks only  
Visual status: not reviewed; Chrome control unavailable and no fallback browser
was used without Christian's approval

## Served artifacts

Immutable preview snapshot `9c3172984314` served all three direction URLs with
HTTP 200 before the final 840 ms motion adjustment. The server must be restarted
before browser review so the immutable snapshot includes that adjustment.

## Structural checks

| Gate | A | B | C |
| --- | ---: | ---: | ---: |
| Exactly one H1 | pass | pass | pass |
| H1 words, maximum 10 | 5 | 6 | 7 |
| Hero lead words, maximum 26 | 22 | 20 | 17 |
| Finite Machine Signal carrier | 1 | 1 | 1 |
| Contained interactive proof | 1 | 1 | 1 |
| Assessment action in chrome + hero | 2 | 2 | 2 |
| Referenced local assets exist | pass | pass | pass |

`node --check preview/golden-standard/p4r3/shared.js` passed.  
`git diff --check` passed.  
No referenced local source or image path was missing.

## Required browser evidence still missing

Static checks do not prove visual quality, interaction state, viewport overflow,
keyboard behavior, reduced motion or no-JavaScript composition. Before Christian
sees a direction, browser review must cover 1440, 1024, 768, 390, 360 and 320 px,
all proof states, Build flyout, mobile disclosure, both CTA routes, no-JS and
`prefers-reduced-motion: reduce`. Reference and prototype screenshots must be
compared in the same viewport.

