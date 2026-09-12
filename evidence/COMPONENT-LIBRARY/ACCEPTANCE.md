# P4R5 acceptance

Status: **PASS**  
Accepted by: Codex program/design direction  
Accepted: 31 August 2026  
Rendered snapshot: `39ce287cfde694eb8b8d998fe09cde436d0c050e292a81cbfaced81880f57696`

## Machine evidence

The final run `p4r5-final-codex-r6` captured 45 named states across 1440,
1024, 768, 390, 360 and 320 CSS-pixel viewports. It covered pointer and
keyboard flyout states, mobile navigation, all five strategic outcomes, all
four WorkGraph sources, Factory pause/replay/resolution, both operating
surfaces, Machine Signal before/after, reduced motion, fresh-load no-JavaScript,
image decoding, asset budgets, accessibility floors and route integrity.

- 40 machine checks: pass
- 0 machine checks: fail
- 0 interaction steps: failed to run
- Factory pass: 6.652 seconds; pause held `decision` for 2.5 seconds; replay
  restarted correctly
- Two checks intentionally remained machine-undecided and were resolved below

Authoritative outputs are `result.json`, `states.json`,
`acceptance-matrix.json` and `screenshots/` in this directory.

## Manual resolution: protected hero crops

**PASS.** Desktop is 1.599 (approximately 16:10); mobile is 0.800 (4:5).
Both visibly preserve the complete semantic sequence: unresolved graphite
paths, one coral judgment, exact machine lines and the sage governed boundary.
The portrait asset is a genuine re-staging for the mobile frame rather than a
centre crop of the desktop composition.

## Manual resolution: package ownership

**Accepted with a recorded provenance limitation.** No out-of-scope P4R5 edit
was identified from the repair record and current change provenance. P4R5 work
is confined to the component-library files, vendored Lucide icons and licence,
the three explicitly approved hero outputs, and this evidence directory.

The shared worktree was already dirty and also contains concurrent program
orchestration. A clean pre-P4R5 baseline is unavailable, so retrospective
machine attribution would be dishonest. The acceptance-matrix ownership row
therefore remains `null`; it is not rewritten as a machine pass.

## Release decision

There is no remaining P0 or P1. P4R5 releases the shared component and
interaction system to P4R6. This acceptance does not approve any Home direction
and does not authorize publication or deployment.
