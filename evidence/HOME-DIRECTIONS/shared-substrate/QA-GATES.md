# Shared Home direction QA gates

Date: 2026-09-01  
Surface: A/B/C Home directions and shared assessment conversion path  
Browser: Codex in-app Browser

## Scope note

This file preserves the earlier X0 shared-substrate check. The authoritative
resolved A1/B1/C1 direction-gate evidence is now
`../resolved/QA.md`. No direction has been promoted to production and nothing
has been published.

## Captured flow

1. **Direction A, mobile start — healthy.** The primary assessment action is
   visible before the image and its target is the shared assessment route.
   Evidence: `01-a-mobile-start.png`.
2. **Assessment landing, mobile — healthy.** The hero arrives at
   `Start with one material decision.`, preserves the Dagg chrome, presents one
   primary contact action and states the truth boundary before the assessment
   brief. Evidence: `02-assessment-mobile.png`.
3. **Mobile navigation open — healthy.** All five primary destinations and the
   assessment action remain visible in one full-height disclosure; the page is
   not visible underneath. Evidence: `03-mobile-menu-open.png`.

## CTA proof

The hero `Start an assessment` action was driven from each then-current X0
direction:

- A: `/preview/golden-standard/directions/a0-claude/`
- B: `/preview/golden-standard/directions/b0-codex/`
- C: `/preview/golden-standard/directions/c0-codex/`

All three landed on
`/preview/golden-standard/routes/assessment/` with the H1
`Start with one material decision.`. The old P3 placeholder assessment page is
not in the conversion path.

## Keyboard and focus proof

- The mobile disclosure uses native `<details>/<summary>` semantics.
- With the menu open, `Tab` from the final assessment link wraps to
  `Dagg — Home`.
- `Shift+Tab` from `Dagg — Home` wraps back to the final assessment link.
- `Escape` closes the menu, restores `aria-expanded="false"` and returns focus
  to the Menu summary.
- The accepted open state shows a visible focus treatment around Close.

The in-app Browser keyboard adapter did not execute the browser's native
default toggle for Enter/Space on `<summary>` during this run. The control is a
native summary and no script cancels Enter/Space, but this single activation
path should still receive a physical-device smoke test before publication.

## Reduced-motion proof and limit

Source inspection confirms that the shared chrome, component library and the
selected directions all branch on `prefers-reduced-motion`. Transitions snap,
scrolling becomes immediate and finite Machine Signal states resolve without
ambient motion. The in-app Browser does not expose a media-feature emulator,
so this run does not claim a rendered reduced-motion environment. A real OS
reduced-motion smoke test remains a pre-publication gate, not an A/B/C
direction blocker.

## Image hashes

```text
df8fb860266a5c993b9fb0d9df4f716b2eaa0778610ebb7e6ba759cd2709dddd  01-a-mobile-start.png
7e3c6cbcb0661c539c81553962afbdf73c488fe0579c6f95d3a715397d75a449  02-assessment-mobile.png
1ce52183fa53cc5efa44d467d9c5f283439d38d8ef6709f2479d6fc7d2661e9f  03-mobile-menu-open.png
```
