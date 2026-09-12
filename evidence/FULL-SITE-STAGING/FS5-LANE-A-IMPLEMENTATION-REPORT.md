# FS5 Lane A implementation report — Home, Transformation, Company

Date: 3 September 2026  
Writer: Claude Fable 5.1 (`claude-fable-5-1`), FS5 Lane A under
`design/golden-standard/packages/FS5-LANE-A-CLAUDE-WRITER.md`  
State: source complete in the nine owned files; nothing assembled, committed,
pushed, deployed or published. `node tools/build_golden_standard_previews.mjs
--check` was run in check mode only.

Authority read in full before editing: `CLAUDE.md`; the Fable golden-standard
plan (§4, 5, 7, 8.2, 8.4, 9.1, 9.2, 9.6, 10, 12 and the rest); the FS5 route
specificity package; the full-site content contract; the Home founder reset;
`COPY-UNIT-MANIFEST.json` (all 205 units); the evidence ledger; the Home,
Transformation and Company page maps; `IMAGE-LIBRARY-CATALOG.md`;
`ASSET-REGISTRY.json`; the three frozen slot manifests; the three authority
PDFs (`Dagg-Image-Language-System.pdf`, `Dagg-Design-System-Foundations.pdf`,
`Dagg-Component-and-Interaction-Library.pdf`, every page); P4R5B; the P4R4
addendum; the image production protocol; the masterplan; the FS5 runner
(`tools/capture_fs5_evidence.py`) and validator (`tests/test_fs5_candidate.py`)
so that every hook and state string matches what the rig asserts.

## 1. Failures, deviations and holds first

1. **Company first-viewport contract cannot be met at 1024×768 or 390×844 with
   the frozen seam — R5 returned to Codex (P1, composition).** The runner
   requires `[data-company-seam]`, the `decision` row and the `build` row to be
   fully inside the first viewport at all three sizes. Source-level budgets
   (sticky header 68/60 px, frozen type scale, exact copy, seam at the
   manifest's 640×256 / 350×140):
   - 1440×900, lead beside the end-aligned seam (implemented ≥1280 px):
     68 + 48 + 29 (eyebrow) + 139 (H1, 2 lines) + 32 + 256 (seam row) + 32 +
     ~106 + ~106 (two rows) ≈ **816 px — fits**.
   - 1024×768, stacked (the seam must stay 640 wide, so it cannot share a row
     with a readable lead in a 928 px field): 68 + 40 + 29 + 179 (H1, 3 lines)
     + 20 + 126 (lead) + 24 + 256 + 24 + ~90 + ~90 ≈ **946 px — the Build row
     and most of the Decision row fall below 768**.
   - 390×844, stacked: 60 + 32 + 33 + 224 (H1, 5 lines) + 24 + 173 (lead, 6
     lines) + 24 + 140 + 24 + ~140 + ~140 ≈ **1014 px — both rows fall below
     844**.
   Per the Company map stop gate ("if the seam … pushes either of the first two
   accountability rows below the first viewport, implementation stops and
   returns R5 to Codex"), I did not hide copy, shrink the seam below the
   manifest size or reorder the DOM to force a fit. The composition is
   implemented as specified (proposition → end-aligned seam → three rows) and
   fits at 1440×900 by arithmetic only. Codex must decide R5: relax the
   1024/390 row contract to `start44` for the chain, or allow the seam to fill
   a 5-column carrier at 1024 (`min(100%, 40rem)` inside the right column,
   which breaks the ±2 px 640×256 expectation), or accept another remedy.
2. **`outputs-stale` from the assembler check is expected and reported.** All
   19 outputs differ because Lane A, Lane B and Lane C edit source without
   assembling. Every other assembler check passes (shared hashes equal, local
   refs only, no inline SVG, no symbol icons, no-JS completeness, no copied
   shared DOM).
3. **Rendered behaviour is unproven before assembly.** No browser was launched.
   Hero pixel-diff (≤0.5 %), H1 line counts, first-viewport geometry, the
   1.6 + 2.2 + 2.2 s cadence, hover/focus suspension, reduced-motion,
   true-no-JS and axe are source-checked only and must be proved by the Codex
   runner against one immutable snapshot.
4. **Home default copy is 504 words**: inside the hard 0–520 band, above the
   ≤500 R6 target. The count is fixed by the exact manifest; no trim is
   possible without deleting exact copy.
5. **Concurrent edits were observed on owned files.** Between my initial read
   and my writes, `routes/transformation/src/body.html`,
   `routes/transformation/src/direction.js` and
   `routes/company/src/body.html` changed on disk (a parallel Lane A run is
   listed in `ps`). I re-read them and overwrote with the reconciled versions
   below so that body, CSS and JS class names are coherent. Final SHA-256 of
   every owned file is listed in §7; if the runner sees different hashes, the
   files were changed after this report.
6. **Home hero geometry parity is asserted, not measured.** The draft hero CSS
   reproduces the accepted FS4 8/4 composition with `display: contents` on the
   narrative owner and an explicit `1fr auto` row pair (bottom-aligned copy
   and lead/actions in both regimes). The FS4B lossless baselines were read
   for reference; only the runner's pixel diff can confirm ≤0.5 %.
7. The Company `direction.js` is not in Lane A ownership and was left
   untouched; `meta.json` still loads it. It only writes `data-company-ready`,
   which no Company CSS rule uses any more, so it is inert.
8. Inherited, unchanged: `[data-home-primary-action]` occurs twice on Home
   (hero and Act 6), as in the accepted FS4 candidate; the runner scopes the
   first-viewport check to `.home-hero`.

No other deviation from the package, the maps or the manifest is known.

## 2. Exact changed files and reasons

| File | Change |
|---|---|
| `preview/golden-standard/home/src/body.html` | Kept the reconciled FS5 draft after verification against the manifest: six acts, disclosure before the first `WG-034` identifier, Act 3 identity with Owner/Permission, Act 4 identity → static Request → signal line → four states → status. Stale labels `Illustrative WorkGraph continuity` and `Retained company context` and `WG-041` are absent. Protected hero markup, sources, alt, H1, lead and actions unchanged. |
| `preview/golden-standard/home/src/direction.css` | Kept the draft composition; added an enhanced-only pending-state weight rule. No `order`, no new hue/family/radius/breakpoint. |
| `preview/golden-standard/home/src/direction.js` | Rewritten: finite, pausable runtime with `phase` + `{viewport, visibility, hover, focus}` suspension sources + `userPaused`; remaining-interval hold; hover suspension for non-touch pointers on the state list only; focus suspension only for interactive descendants of the list; explicit Pause authoritative until explicit Resume; exact four status states written with `data-copy-state`; Pause/Resume label states; reduced motion or missing `IntersectionObserver` resolve immediately and hide Replay (R8); `aria-live` polite only at completion. |
| `preview/golden-standard/routes/transformation/src/body.html` | Rewritten to the exact manifest: keyed `data-copy-ref/kind/scope` on every unit; 7/5 thesis with the five-label strip (`[data-transformation-outcome-strip]`, five `[data-transformation-index-label]` anchors to `#decide`) before the single 4:5 T-DF-01 carrier; lowercase role definitions; numbered folio removed in favour of exact fields; provenance moved outside and after the closed `<details>`; continuum rebuilt as one fieldset (aria-label legend unit) with five outcome blocks each owning heading + explanation, radios inside the heading labels; roadmap narrative kept as one contiguous unit with the sequence and action as siblings. |
| `preview/golden-standard/routes/transformation/src/direction.css` | Rewritten: grid placement for copy/image/strip (no `order`), `margin-top:-120px` removed, image at intrinsic 4:5 with the finite settle, strip as mono anchors on one rule (48 px targets, vertical below 360 px), continuum manual/scroll modes, sticky runway at ≥1180 fine pointer with motion, provenance styling, tighter 1024 rhythm. |
| `preview/golden-standard/routes/transformation/src/direction.js` | Hero settle retained; continuum mode attribute (`scroll`/`manual`); scroll-led forward/reverse selection until a direct choice; reduced motion, missing `:has()` or rAF resolve to manual with `data-transformation-resolved`. |
| `preview/golden-standard/routes/company/src/body.html` | Rewritten to the exact manifest: keyed units on every node; hero image pair removed; proposition → end-aligned 5:2 seam (`[data-company-seam]`, C-DF-SEAM-01) → `<dl>` chain (`[data-company-accountability]`, rows `decision`/`build`/`escalation`); `AI system engineering`; eyebrows and numerals without manifest units removed; capabilities as a ruled ledger; partnership `<details>` with exact summary/meta and progressive body; close narrative contiguous, leadership group (`role="group"`, `aria-label="Dagg leadership"`) as sibling; three close actions including `hello@dagg.ai`. |
| `preview/golden-standard/routes/company/src/direction.css` | Rewritten: seam `inline-size: min(100%, 40rem); aspect-ratio: 5/2; object-fit: contain`, end-aligned; lead beside the seam at ≥1280; ruled chain rows; partnership details `align-self:start` with a 62–64 px closed summary; close as 5/7 with leadership and actions in the right column. |
| `evidence/FULL-SITE-STAGING/FS5-LANE-A-IMPLEMENTATION-REPORT.md` | This report. |

## 3. Source-level checks run

Commands: `node --check` on both scripts (pass); `node
tools/build_golden_standard_previews.mjs --check` (only `outputs-stale`);
a Python source reconciliation of each `body.html` against
`COPY-UNIT-MANIFEST.json` using the runner's rules (nearest `data-copy-ref`
owner, NFC/whitespace normalisation, text-node join, kind/scope/section
match, multiplicity, accessible-attribute ownership, nesting rule, no
uncovered text), plus the §10.4 word count, hook counts and asset hashes.

Results, all three routes: **zero manifest problems** (no missing, extra,
mismatched, nested or uncovered units; no uncovered accessible strings).

| Route | Default words | Band | Progressive | Ceiling | First section | Band |
|---|---:|---|---:|---:|---:|---|
| Home | 504 | 0–520 (target ≤500) | 0 | 100 | 40 | 35–55 |
| Transformation | 538 | 450–600 | 71 | 220 | 53 | 35–55 |
| Company | 350 | 260–360 | 0 (detail closed) | 160 | 84 | 75–95 |

Counting follows §10.4: closed `<details>` content is excluded, so the Company
partnership body (~110 words) and the Transformation folio fields and sequence
count only when opened; the Transformation progressive figure is the four
visible manual-mode explanations.

Hooks verified in source: Home `data-home` ×1, `data-home-hero-image`,
`data-home-execution`, `-states`, `-status`, `-pause`, `-replay` ×1 each,
four `data-home-execution-state` rows, acts
`position,shift,record,build,compound,partner`, disclosure unit precedes
`home.record.identity` which precedes `home.build.execution-identity`,
`WG-041` absent, stale labels absent. Transformation sections exactly
`thesis,division,map,decision,roadmap,horizon,next`; one strip, five index
labels, provenance not inside `<details>`, `#map/#decide/#roadmap` present
once, only `transformation-hero-decision-field-mobile-v2.webp` loaded
(SHA-256 `6624d6a0…3ac936` matches the registry), strip precedes image,
`preserve` checked. Company sections `position,view,capabilities,standard,
close`; one seam, one chain, rows `decision,build,escalation`, seam before
chain, only `company-accountability-seam-01-v1.webp` loaded (SHA-256
`05abef05…c73da` matches), `Harness engineering` absent. One H1 and no
duplicate id per route. No CSS `order`, no `:root`/`@font-face`, no remote
URL in any owned stylesheet.

Protected invariants: all six `homeHero.copy` strings from
`FS5-PROTECTED-INVARIANT-BASELINE.json` are present verbatim in
`home/src/body.html`; the four selected asset files hash to the baseline
values (`49f87d83…`, `fa231e00…`, `b740f0f5…`, `d1f9ea85…`) and the two
`<picture>` sources plus the PNG fallback are unchanged.

## 4. Viewport, motion and resilience behaviour that source can prove

- **DOM order = reading order at every width** on all three routes; layout
  changes use grid placement only.
- **Home no-JS**: status text is statically `Human decision recorded. Release
  remains withheld.` with `data-copy-state="resolved"`; Pause/Replay and their
  container carry `hidden`; Request and the four states are in source order.
- **Home enhanced**: initial status `Ready to inspect the operating change`
  (`initial`); running/paused/resolved strings exact; Pause label states
  `pause`/`resume`; sequence attribute `ready|running|paused|complete`;
  `data-home-state-index` 0–3; no `a`, `button` or `tabindex` inside the
  state list (no junk tab stop); intervals 1600/2200/2200 ms with hold/resume
  preserving remaining time; hover suspension excludes touch pointers;
  explicit Pause cannot be cleared by hover or visibility.
- **Home reduced motion / missing observer**: resolved immediately, Replay and
  the controls container hidden.
- **Transformation no-JS**: radios `display:none`; all five outcomes and the
  strip in order; provenance visible outside the closed folio; hero is a still.
  Runner tokens `Preserve…Retire` occur in order (strip first).
- **Transformation <1180 px / coarse / reduced motion**: `manual` mode keeps
  all five `[data-transformation-outcome]` blocks rendered and selectable;
  reduced motion also sets `data-transformation-resolved`.
- **Transformation ≥1180 fine pointer**: five stations on one rule, one
  readout, sticky runway; scroll to stage bottom selects `retire`, back to top
  selects `preserve` until a direct selection owns the page view.
- **Transformation first viewport, computed**: 1440×900 image 498×622 fully
  inside (bottom ≈738 px), strip bottom ≈818 px; 1024×768 image 368×460
  (bottom ≈576), copy ≈475 px, strip bottom ≈671; 390×844 copy + strip end
  ≈705 px, image starts ≈737 px with ≥44 px visible (start44). H1 line
  estimates 3/4/4 at 1440/1024/390 against ceilings 3/4/4 (4 lines at 1024
  assumes ≥19 characters per 528 px line; if it wraps to 5, the strip still
  ends ≈735 px).
- **Company**: seam is a still image with no motion at any state; details
  closed row 62–64 px; see §1.1 for the first-viewport hold.
- Reduced-motion blocks zero all route-specific transitions on all three
  routes.

## 5. Copy and claim boundaries

Every public string is a verbatim manifest unit. Home uses the single
disclosure `Constructed example, not client data or a production
deployment.` once, before `WG-034`; Transformation carries the shared page
disclosure before the folio and the local provenance `Illustrative operating
reality map · constructed example`; Company carries P method statements and
the V leadership lines only. No `proprietary`, `LIVE`, `production`,
multiplier, headcount or `Harness engineering` appears.

## 6. Not done, by rule

Not assembled, not committed, not pushed, not deployed, not published, no
subagents, no file outside the nine owned paths touched, no browser run.

## 7. Final owned-file hashes (SHA-256)

- `home/src/body.html` `bdc49a3211447cf8021cb139d82accae41c0a17dd6653aa7130af5328b12f404`
- `home/src/direction.css` `56d312c513a80d9c759792662a2bc8104cf43b7950fdad8b6791e6aaae92b069`
- `home/src/direction.js` `ffc710df6f912e51b13c67f91b7b649e0cc9e246866ed6a9732931ac385a35ee`
- `routes/transformation/src/body.html` `26ef492baa55a1df345c6ab7c5740a98cd009556148664878c175bda99d6040f`
- `routes/transformation/src/direction.css` `9cfbbad44dcf0d5aa8cbd23c95e9daf493aabb34349a2e4586a218d7c4d176f3`
- `routes/transformation/src/direction.js` `12ff6ab165dc58c73e0c135decc3d9607681d1495da099a92f16faa40361803b`
- `routes/company/src/body.html` `0c0f8302ffeae7510e5b74b76778fe5e63a85e64b29bf243e6105671df32dab2`
- `routes/company/src/direction.css` `e3372bcbeb733086c3b0b66ae828194d0f26ac7de4806ad2b2566ec3f3da6820`

## 8. Required continuation (Codex)

1. Decide R5 for the Company 1024×768 and 390×844 first-viewport row
   contract (§1.1) before assembly.
2. Assemble once, freeze one snapshot, run the FS5 runner and validator; the
   Home pixel-diff, cadence, suspension, Transformation geometry and all
   no-JS/reduced-motion lanes are proven there, not here.
