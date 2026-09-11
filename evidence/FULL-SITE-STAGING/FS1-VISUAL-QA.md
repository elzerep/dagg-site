# FS1 visual QA — Impact internal staging route

Date: 2026-09-02
Route: `/preview/golden-standard/routes/impact/`
Scope: internal staging skeleton only; no publication approval and no claim that an Impact proof exists.

## Accepted screenshots

1. `visual-qa/01-impact-desktop-1440.png` — desktop, 1440 x 900 viewport
2. `visual-qa/02-impact-tablet-1024.png` — tablet, 1024 x 768 viewport
3. `visual-qa/03-impact-mobile-390.png` — mobile, 390 x 844 viewport
4. `visual-qa/04-impact-mobile-menu-open-390.png` — mobile navigation disclosure

Each file is the exact screenshot captured from the assembled route in the current browser run.

## Result

FS1 passes as a truthful, responsive internal skeleton.

- The H1, lead, proof types, evidence chain, withheld-proof state and next move form a coherent reading order on desktop, tablet and mobile.
- The route is visibly marked as internal staging and has static `noindex, nofollow` metadata in the assembled output.
- No horizontal page overflow was present at 390 or 1440. The 390 viewport produced a 375 px document client width and a matching 375 px document scroll width.
- Minimum sampled visible type size was 12 px on mobile and 13 px on desktop.
- No browser warnings or errors were recorded.
- The native mobile disclosure opens, changes its label to Close and exposes the full primary navigation plus the assessment action.

## Visible strengths

- The warm opening establishes editorial trust without reading as a generic case-study grid.
- The dark evidence chain gives the route one decisive technical proof moment and keeps provenance central.
- The mobile version preserves hierarchy and comfortable line lengths rather than shrinking the desktop composition.

## Known limits and deliberate omissions

- The route contains no published case because none is approved. Its 224 visible words are therefore below the future Impact budget, which assumes one complete proof.
- Impact remains absent from public navigation. It must not ship until a named or accurately anonymized proof passes the evidence and permission gate.
- Screenshot inspection does not prove full WCAG compliance. Keyboard focus order, screen-reader output and zoom beyond the sampled layouts remain part of the whole-site QA pass.
- The primary CTA wording is inherited from the locked content contract. In this internal state it lands on the explicit `Approved proof · none published` truth boundary; it is not a public conversion path.

## Decision

Accept FS1 for whole-site staging. Do not spend further visual polish on this route until a real proof exists. Proceed to FS2: convert the WorkGraph and Factory mechanisms from click-led demonstrations into scroll-led, zero-click-comprehensible sequences while preserving keyboard and direct-control access.
