# Dagg foundation tokens — P2

Status: implemented, **not yet accepted** — the rendered acceptance gates could not be executed in the implementation session. See section 10.
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`, Part III
Contract: `../packages/P2-FOUNDATIONS.md`, section 5
Base commit: `cf9bdcdfa1e47ff75e193155feee00b0bda67e86`
Implementation: `tokens.css`
Specimen: `/preview/golden-standard/foundations/index.html`

This file explains the frozen foundation. `tokens.css` is the single source of the values; anything below that disagrees with `tokens.css` is wrong and `tokens.css` wins.

Every P4 direction composes from these tokens. A direction may change composition, emphasis, sequence and imagery. It may not introduce a hue, a typeface, a breakpoint jump or a focus treatment that is not here.

---

## 1. Palette

Eight roles. No additional brand hue exists.

| Token | Value | Role | Rule |
|---|---|---|---|
| `--paper` | `#F0EEE6` | Main reading ground | Carries the majority of a page. |
| `--lift` | `#FAF9F5` | Short editorial lift | A raised act, not a card grid. |
| `--panel` | `#E8E6DC` | Material depth | Divisions and contained surfaces. |
| `--ink` | `#141413` | Precision, instruments, final close | Contained inside mechanisms; may become the last full-bleed act. |
| `--ink-2` | `#33332F` | Body text | Default reading colour on warm grounds. |
| `--coral` | `#D97757` | Human intervention | Large signal, graphic or an action on ink. Never small text on paper. |
| `--coral-deep` | `#9E4A2E` | Accessible action and emphasis | The action colour on paper, lift and panel. |
| `--sage` | `#7C8471` | Boundary, permission, stable state | A surface or boundary. Never a label colour on paper. |

Neutrals are derived only by putting alpha on Ink or on Paper. No grey is introduced as a ninth colour.

| Token | Value | Derived from |
|---|---|---|
| `--rule` | `rgb(20 20 19 / 0.14)` | Ink |
| `--rule-strong` | `rgb(20 20 19 / 0.30)` | Ink |
| `--ink-disabled` | `rgb(20 20 19 / 0.38)` | Ink |
| `--rule-on-ink` | `rgb(240 238 230 / 0.20)` | Paper |
| `--paper-disabled` | `rgb(240 238 230 / 0.38)` | Paper |

### Accepted pairs

Ratios are WCAG 2.1 relative-luminance contrast, computed from the frozen hex values. The specimen re-computes each one from the colours Chrome actually rendered and refuses to print a number it cannot reproduce.

| Foreground | Background | Ratio | Accepted for |
|---|---|---:|---|
| `--ink` | `--paper` | 15.87:1 | any size |
| `--ink` | `--lift` | 17.50:1 | any size |
| `--ink` | `--panel` | 14.73:1 | any size |
| `--ink-2` | `--paper` | 10.92:1 | any size |
| `--ink-2` | `--lift` | 12.04:1 | any size |
| `--ink-2` | `--panel` | 10.14:1 | any size |
| `--coral-deep` | `--paper` | 5.21:1 | any size |
| `--coral-deep` | `--lift` | 5.74:1 | any size |
| `--coral-deep` | `--panel` | 4.83:1 | any size |
| `--paper` | `--ink` | 15.87:1 | any size |
| `--lift` | `--ink` | 17.50:1 | any size |
| `--coral` | `--ink` | 5.90:1 | any size |
| `--ink` | `--sage` | 4.74:1 | any size |

### Rejected pairs

| Foreground | Background | Ratio | Why it is rejected |
|---|---|---:|---|
| `--coral` | `--paper` | 2.69:1 | Below 3:1, so it fails even as large text. Coral is a signal, an action on ink, or a graphic. |
| `--sage` | `--paper` | 3.35:1 | Passes 3:1 for graphics and boundaries only. It is never a readable label. |

`--paper` on `--sage` (3.35:1) and `--ink-2` on `--sage` (3.26:1) are rejected for the same reason. Text on a Sage surface uses `--ink`.

---

## 2. Type

Three families, vendored locally with their licenses under `assets/fonts/golden-standard/`. No remote font request is permitted anywhere in the golden-standard system.

| Token | Family | Job |
|---|---|---|
| `--font-sans` | Geist | Headings, navigation, actions, interface. Decisions and structure. |
| `--font-serif` | Newsreader | Leads, explanatory prose, captions, selective editorial emphasis. Judgment and reflection. |
| `--font-mono` | JetBrains Mono | Genuine metadata and instrument labels only. Never body copy. |

Provenance and hashes: `../../../assets/fonts/golden-standard/PROVENANCE.md`.

### The scale

Six roles. Three frozen endpoints each, at 320, 390 and 1440 px.

| Role | Token | 1440 px | 390 px | 320 px | Leading | Measure note |
|---|---|---:|---:|---:|---:|---|
| H1 | `--fs-h1` | 68 px | 44 px | 42 px | 1.02 | 17 words / 2.5 lines |
| H2 | `--fs-h2` | 52 px | 36 px | 34 px | 1.07 | 3 lines |
| H3 | `--fs-h3` | 32 px | 27 px | 26 px | 1.12 | conclusion only |
| Lead | `--fs-lead` | 23 px | 20 px | 19 px | 1.44 | 42 words |
| Body | `--fs-body` | 18 px | 17 px | 17 px | 1.62 | 560–620 px |
| Meta | `--fs-meta` | 13 px | 12 px | 12 px | 1.42 | never below 12 px |

### Why the curve is written the way it is

The three endpoints are not collinear. H1 rises 2 px between 320 and 390 (a slope of 0.0286 px per px) and 24 px between 390 and 1440 (0.0229 px per px). One straight line cannot pass through all three, and a breakpoint jump is forbidden.

Each role is therefore a **continuous piecewise-linear curve** with its knee exactly at 390 px:

```
--fs-h1: clamp(42px, min(32.857143px + 2.857143vw, 35.085714px + 2.285714vw), 68px);
                     └─ 320→390 segment ─┘  └─ 390→1440 segment ─┘
```

`min()` selects the lower of the two segments, which is the mobile segment below 390 px and the desktop segment above it; the two are equal at 390 px, so the curve is continuous and has no jump. `clamp()` pins both ends. Where the mobile segment is flat and the desktop segment rises — Body and Meta — the lower bound of `clamp()` does the same job and no `min()` is needed.

Consequence: the size is right at 320, 390 and 1440 by construction, and it moves smoothly at every width in between. There is no width at which type snaps.

### Line length

`--measure-min: 560px` and `--measure-max: 620px`. The `.measure` utility caps at `--measure-max`; below about 660 px of available width the measure is simply the available width, which is correct on a phone.

---

## 3. Spacing and shape

`--space-scale: 4 8 12 16 24 32 48 64 96 128 160`, exposed individually as `--space-1` … `--space-11`. Nothing in the system uses a value outside this scale.

| Section step | Mobile (<768) | Tablet (768–1023) | Desktop (≥1024) |
|---|---:|---:|---:|
| `--section-lg` | 88 px | 112 px | 160 px |
| `--section-md` | 64 px | 88 px | 112 px |

Radius is a three-step scale, applied by meaning rather than by habit:

| Token | Value | Applies to |
|---|---:|---|
| `--radius-control` | 4 px | Buttons, chips, small detail. |
| `--radius-surface` | 10 px | Contained surfaces and cards. |
| `--radius-instrument` | 14 px | Instruments and ink mechanisms. |

Not every surface is a rounded card. A section ground has no radius at all.

Short punctuation blocks are 240–360 px of total block height at desktop; on mobile the content decides the height.

---

## 4. Grid

| Token | Value |
|---|---|
| `--field-max` | 1240 px |
| `--columns` | 12 |
| `--col-gap` | 24 px below 1024, 32 px at 1024 and above |
| `--page-gutter` | 20 px below 768, 24 px at 768–1023, 48 px at 1024–1439, 72 px at 1440 and above |
| `--split-strategic` / `--split-strategic-counter` | 7 / 5 |
| `--split-product` / `--split-product-counter` | 45 / 55 |
| `--collapse` | 940 px |

The gutter and the column gap are the only stepped values in the system. The masterplan declares them as fixed values per range, not as a curve, so they change at 768, 1024 and 1440 px and nowhere else.

**Gutter and field are two different things.** `--page-gutter` is the minimum padding between the viewport edge and the content field. `--field-max` is the ceiling on the field itself. At 1440 px the gutter leaves 1296 px available, the field caps at 1240 px, and the remaining 56 px is split by centring. The declared gutter is therefore the measured padding of `.page`, not the visual distance from the edge to the text at very wide viewports. Both constraints hold at once; neither overrides the other.

Two-column carriers collapse below 940 px, the frozen point inside the masterplan's 900–960 px band. Collapsing changes the visual arrangement only; the DOM reading order is identical above and below it.

The twelve-column ruler in the specimen renders the real content grid at every width. Below 768 px the tracks are hairlines, because twelve columns with a 24 px gap genuinely leave about 7 px per track at 390 px. That is why mobile content spans the full field rather than using column spans: mobile is composed, not stacked.

---

## 5. Surfaces and action semantics

- Warm paper carries the majority of a page.
- Lift and Panel create hierarchy without a card grid.
- Ink is contained inside a mechanism, and may become the final full-bleed close.
- A page changes ground at most three times.
- Coral marks a human decision or an accessible action. It is never a decorative stripe and never a section colour.
- Sage marks a boundary, a permission or a stable operating state. It is never a label colour.
- Buttons are compact, `--radius-control`, never pills.
- Text links stay visibly links: they keep an underline and they use `--coral-deep` on warm grounds, `--coral` on ink.

| Control | Warm ground | Ink ground |
|---|---|---|
| Primary | `--coral-deep` surface, `--paper` label (5.21:1) | `--coral` surface, `--ink` label (5.90:1) |
| Secondary | transparent, `--ink` label, `--rule-strong` border (15.87:1) | transparent, `--paper` label (15.87:1) |
| Text link | `--coral-deep`, underlined (5.21:1) | `--coral`, underlined (5.90:1) |
| Disabled | `--paper` surface, `--ink-disabled` label | inherits the same treatment |

Disabled controls are deliberately below AA. WCAG 1.4.3 exempts them, and the specimen records them as an explicit exclusion rather than silently skipping them.

---

## 6. Targets, focus and motion

| Token | Value |
|---|---|
| `--target-min` | 44 px |
| `--focus-width` | 2 px |
| `--focus-offset` | 2 px |
| `--focus-ring` | `--ink` on warm grounds, `--paper` inside `.on-ink` |

The focus ring is a single treatment that re-points its colour per ground, rather than two different focus systems. It is 15.87:1 against both Paper and Ink, so it is unambiguous on the warmest and the darkest surface in the palette.

Every interactive target is at least 44 × 44 px including its padding, at every width.

Motion tokens are `--motion-micro: 180ms`, `--motion-response: 240ms` and `--motion-ease`. Under `prefers-reduced-motion: reduce` every transition and animation is reduced to effectively zero. No motion on the foundation carries meaning, so removing it changes no content and no layout.

---

## 7. `.on-ink`

`.on-ink` is the only contextual class in `tokens.css`. It re-points `--focus-ring` to Paper and `--rule` to the Paper-derived hairline. It exists so that an ink instrument inside a warm page keeps one focus system and one hairline system rather than inventing a dark-mode variant.

---

## 8. What this file does not decide

Composition, sequence, imagery, motion choreography, navigation and page structure are not decided here. P2 froze the material; it did not design a page.

---

## 9. Performance budget

| Item | Budget | Measured |
|---|---:|---:|
| Specimen HTML | ≤ 40 KB | see `evidence/P2/result.json` |
| Combined CSS (`tokens.css` + `foundations.css`) | ≤ 55 KB | see `evidence/P2/result.json` |
| Page JavaScript | 0 bytes | 0 bytes, 0 `<script>` elements |
| Combined WOFF2 | ≤ 750 KB | 398,696 bytes |

`font-display: block` plus `width`/`height` attributes and `aspect-ratio` on both logotypes are how CLS is held at zero. That argument is not the same as a measured layout-shift score, and the evidence says so.

---

## 10. Acceptance state

The token system, the specimen, the acceptance suite and the evidence harness are implemented. The rendered gates — every measurement in sections 1–6 above, all screenshots and `evidence/P2/result.json` — have **not** been executed, because Google Chrome could not be launched in the implementation session. Nothing in this file may be treated as verified until `tools/capture_p2_evidence.py` has run and produced `evidence/P2/result.json`.
