# P2 · Foundations: tokens, type, grid and accessibility pairs

Status: accepted by Codex  
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Base commit: `cf9bdcdfa1e47ff75e193155feee00b0bda67e86`  
Gate type: operating acceptance by Codex

## Acceptance record

Accepted by Codex after independent rendered review at desktop and mobile and
an installed-Google-Chrome acceptance run. The authoritative snapshot ID,
commit state, measurements, screenshots, deviations and post-commit
reproduction live under `evidence/P2/`; the package does not duplicate the
snapshot ID so recording the result cannot mutate the content set it names.

The accepted heading correction uses Geist at weight 400 with normal wrapping.
The 2.5-line desktop H1 limit is measured as visual line-equivalent occupancy
(sum of the actual DOM text-line widths divided by the 1240 px field width),
with at most three physical lines and a final line no wider than half the field.
This preserves the exact P1 copy, the frozen 68 px endpoint and an honest,
executable measure instead of forcing an impossible two-line split.

## 1. Objective

Turn the accepted design constitution into one immutable, locally served foundation system and a rendered specimen. P2 freezes the palette roles, typography, grid, spacing, surfaces, focus treatment and responsive rules that every P4 direction must share. It does not design a homepage direction.

## 2. Final visible copy — use verbatim

**Document title**  
Dagg foundations — P2

**Page marker**  
Dagg / Foundations

**H1**  
Warm intelligence. Precise mechanism.

**Lead**  
The surrounding world is tactile, warm and editorial. The mechanism inside it is exact, dark and inspectable.

**Section titles**

- Palette with a job
- Type carries meaning
- One grid, different emphasis
- Rhythm, not slides
- Accessible by construction

**Palette captions**

- Paper — the default reading ground.
- Lift — a short editorial rise.
- Panel — material depth and division.
- Ink — precision, instruments and the final close.
- Ink 2 — body copy and secondary explanation.
- Coral — a human decision changes the path.
- Coral deep — accessible action and emphasis.
- Sage — a boundary, permission or stable state.

**Typography specimen copy**

- H1: We redesign how your company works — and build what its AI-native operating model requires.
- H2: The first AI decision is what should not be automated.
- H3: The map becomes part of the system.
- Lead: A machine works at machine speed. A company moves at the speed of its handoffs.
- Body: WorkGraph connects workflows, content, systems, decisions, exceptions and domain knowledge so the strategic decision and the build can draw on the same record.
- Metadata: REPRESENTATIVE RECORD · SYNTHETIC DATA

**Grid labels**  
12-column field · 7/5 strategic split · 45/55 product split · 560–620 px reading measure

**Rhythm captions**

- One long carrier.
- One short punctuation.
- One contained instrument.
- One proof split.
- One decisive close.

**Accessibility labels**

- Primary action
- Secondary action
- Text link
- Focus visible
- Coral is not small text.
- Sage is a boundary, not a label color.

No other visible explanatory copy may be invented. Numeric token values may be printed next to their labels.

## 3. Authoritative inputs

- `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`, Part III.
- `../narrative/HOMEPAGE-MESSAGE-ARCHITECTURE.md`.
- `../narrative/VERTICAL-SLICE-COPY.md`.
- `../reference-audits/ANTHROPIC-OPENAI-RECIPE.md`.
- `../reference-audits/PALANTIR-RECIPE.md`.
- `../reference-audits/xai-current/XAI-CURRENT-AUDIT.md`.
- Existing Dagg logo assets under `assets/`.
- Immutable preview server accepted in P0R2.

## 4. Files owned by P2

Only these paths may be created or changed:

- `design/golden-standard/packages/P2-FOUNDATIONS.md` — status and acceptance record only.
- `design/golden-standard/system/TOKENS.md`
- `design/golden-standard/system/tokens.css`
- `assets/fonts/golden-standard/**`
- `preview/golden-standard/foundations/index.html`
- `preview/golden-standard/foundations/foundations.css`
- `tests/test_p2_foundations.py`
- `tools/capture_p2_evidence.py`
- `evidence/P2/**`

Do not change `index.html`, `robots.txt`, `v1/`, `marketing/`, legacy `preview/` files, legacy direction tokens, logo assets, the masterplan, the four narrative files, P0–P1 evidence or the preview server.

## 5. Frozen token contract

### Palette

Use these exact base values and no additional brand hues:

| CSS token | Value | Role |
|---|---|---|
| `--paper` | `#F0EEE6` | Main reading ground |
| `--lift` | `#FAF9F5` | Short editorial lift |
| `--panel` | `#E8E6DC` | Material depth |
| `--ink` | `#141413` | Precision and dark surfaces |
| `--ink-2` | `#33332F` | Body text |
| `--coral` | `#D97757` | Human intervention; large signal only |
| `--coral-deep` | `#9E4A2E` | Accessible action text on paper/lift |
| `--sage` | `#7C8471` | Governance surface/boundary |

Neutral rules may be derived only by applying alpha to Ink or Paper. Coral and Sage may not become decorative section colors.

### Type

Vendor the exact open-source font files and their licenses locally. No Google Fonts request or other remote font request is permitted in the rendered specimen.

- Geist: headings, navigation, actions and interface.
- Newsreader: leads, explanatory prose, captions and selective editorial emphasis.
- JetBrains Mono: genuine metadata and instrument labels only.

Required computed endpoints:

| Role | 1440 px | 390 px | 320 px | Line height | Max measure |
|---|---:|---:|---:|---:|---:|
| H1 | 68 px | 44 px | 42 px | 1.00–1.04 | 17 words / 2.5 lines |
| H2 | 52 px | 36 px | 34 px | 1.04–1.10 | 3 lines |
| H3 | 32 px | 27 px | 26 px | 1.08–1.16 | conclusion only |
| Lead | 23 px | 20 px | 19 px | 1.38–1.50 | 42 words |
| Body | 18 px | 17 px | 17 px | 1.55–1.68 | 560–620 px |
| Meta/mono | 13 px | 12 px | 12 px | 1.35–1.50 | never below 12 px |

Use a continuous fluid scale between endpoints. Do not add arbitrary breakpoint jumps.

### Spacing and shape

- Base spacing scale in px: `4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 160`.
- Section large: 160 px desktop, 112 px tablet, 88 px mobile.
- Section medium: 112 px desktop, 88 px tablet, 64 px mobile.
- Short punctuation block: 240–360 px total block height at desktop; content determines mobile height.
- Radius scale: 4 px controls/detail, 10 px contained surfaces, 14 px instruments. Do not make every surface a rounded card.
- Minimum interactive target: 44 × 44 px.
- Focus ring: at least 2 px, at least 2 px offset, visible against both warm and ink grounds.

### Grid

- Maximum content width: 1240 px.
- Twelve columns.
- Column gap: 32 px at 1024+, 24 px below 1024.
- Page gutter: 72 px at 1440+, 48 px at 1024–1439, 24 px at 768–1023, 20 px below 768.
- Strategic split: 7/5.
- Product split: 45/55.
- Reading measure: 560–620 px.
- Collapse two-column carriers between 900 and 960 px. Use 940 px for the frozen implementation.
- No document-level horizontal scroll at 320, 360, 390, 768, 1024 or 1440 px.

### Surface and action semantics

- Warm paper carries the majority of a page.
- Lift and Panel create hierarchy without card grids.
- Ink is contained inside mechanisms and may become the final full-bleed close.
- Coral marks only a human decision or accessible action.
- Sage marks only a boundary, permission or stable state.
- Buttons are compact, not pills; text links remain visibly links.
- Only verified contrast pairs may be presented as accepted.

## 6. Foundation specimen contract

Build `/preview/golden-standard/foundations/index.html` as a documentation specimen, not a homepage concept.

It must render:

1. All eight palette roles with numeric values and allowed-use captions.
2. Accepted foreground/background pairs plus explicitly rejected Coral-small-text and Sage-small-text pairs.
3. The complete type scale using the exact specimen copy at desktop and mobile endpoints.
4. A visible twelve-column ruler and real 7/5, 45/55 and reading-measure examples.
5. A non-repeating rhythm specimen showing a long carrier, punctuation, contained instrument, proof split and close without placeholder boxes, fake product UI or invented imagery.
6. Primary, secondary and text-link states: default, hover, focus-visible and disabled where applicable.
7. The Dagg logotype from the existing real asset.
8. A short semantic-token reference generated from `tokens.css`, with no conflicting duplicate values.

The page may use text, real logo assets, color surfaces and layout diagnostics. It may not use CSS/SVG/div art pretending to be imagery, a product screenshot or a WorkGraph mechanism.

## 7. Executable acceptance tests

Create `tests/test_p2_foundations.py` and drive the installed Google Chrome through CDP. Reuse the P0R2 immutable server; do not use Playwright or another browser.

The suite must prove:

1. HTML, CSS, every WOFF2 and the Dagg logo carry the same snapshot ID as `/__revision`.
2. `document.scrollWidth === document.clientWidth` at 320, 360, 390, 768, 1024 and 1440 px.
3. Every rendered HTML and SVG text node is at least 12 px; coverage is not limited to selected classes.
4. H1, H2, H3, Lead, Body and Meta computed sizes match the table at 1440, 390 and 320 within 0.5 px.
5. Measured gutters equal 72, 48, 24 and 20 px in their stated ranges; the content field never exceeds 1240 px.
6. The desktop grid exposes twelve equal tracks and collapses at 940 px without changing DOM reading order.
7. Every rendered interactive target is at least 44 × 44 px.
8. Keyboard Tab reaches every interactive specimen once in logical order and its focus indicator is visually distinguishable on warm and ink surfaces.
9. All accepted text/background pairs meet WCAG AA for their actual size; Coral and Sage small-text specimens are explicitly marked rejected and are not used as readable labels.
10. `document.fonts.check()` passes for Geist, Newsreader and JetBrains Mono; all font requests are local and their licenses exist.
11. No request leaves `127.0.0.1`; zero console errors occur.
12. `prefers-reduced-motion: reduce` removes all non-essential transitions without changing content or layout.
13. Only P2-owned files differ from base commit; all public site and legacy preview files are byte-identical.

## 8. Required evidence

Create `tools/capture_p2_evidence.py`. One immutable server process must produce:

- `evidence/P2/result.json` using the masterplan schema and snapshot ID;
- full-page screenshots at 1440, 390, 360 and 320;
- focused primary action on paper and focused secondary action on ink;
- reduced-motion 390 screenshot;
- DOM snapshot containing computed token/type/grid facts;
- request log proving local-only assets;
- response headers for HTML, CSS, WOFF2 and PNG;
- unit-test output and exact coverage statement;
- deviations and unmeasured fields.

Capture a clean post-commit run that reproduces the same snapshot ID as the accepted pre-commit content set, excluding evidence paths exactly as P0R2 defines.

## 9. Performance budget

- HTML ≤ 40 KB uncompressed.
- Combined CSS ≤ 55 KB uncompressed.
- JavaScript on the specimen page: 0 bytes.
- Combined WOFF2 ≤ 750 KB.
- CLS = 0 after local fonts resolve.
- No remote dependency.

## 10. Stop conditions

Stop before commit if:

- a new hue or typeface is introduced;
- a font remains remotely hosted;
- a proxy selector scan replaces full rendered-text coverage;
- Coral or Sage is accepted as small text on warm paper;
- the mobile layout is merely a squeezed desktop grid;
- a visible asset is faked with CSS, SVG or placeholder boxes;
- the specimen starts to become a homepage direction;
- a public or legacy preview file changes;
- the exact immutable snapshot cannot be proven.

Do not begin P3 or P4.

## 11. Completion report

Return deviations first, then:

1. exact commit and owned files;
2. locally vendored font provenance and licenses;
3. snapshot ID and evidence paths;
4. screenshots;
5. tests and what every test actually covers;
6. what is ready for Codex review.

Do not use “verified,” “complete” or “production-ready” unless every gate has authoritative evidence.
