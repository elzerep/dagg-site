# FS4 implementation report — FS4A supporting-route corrections

Package: `FS4A-SUPPORTING-ROUTE-CORRECTIONS.md` (parent `FS4-WHOLE-SITE-POLISH-AND-QA.md`)  
Implementation owner: Claude Code, model identifier `claude-fable-5-1`  
Written: 2026-09-02T13:39+02:00  
Git commit at start and end: `f688c5431960bae3fda7dbe237c47cb0a95cf57c` (branch `design-language`)  
Working tree: dirty. `preview/golden-standard/routes/`, `preview/golden-standard/home/`,
`preview/golden-standard/shared/`, `evidence/FULL-SITE-STAGING/` and the FS packages are
all untracked in git; `CLAUDE.md` and three design documents were already modified before
this session. Nothing was committed, staged, assembled, deployed or published.

Status: **SOURCE COMPLETE — ASSEMBLY PENDING — NO VISUAL OR ASSEMBLED ACCEPTANCE CLAIMED.**
Codex owns the shared assembler run, the immutable snapshot and Browser acceptance.

---

## 1. Failures, gaps and deviations (read first)

### 1.1 SHA-256 verification of read-only files was NOT executed

The FS4A brief asks for confirmation that Home and Transformation source hashes and the
protected-carrier hashes in `FS4-INVARIANT-BASELINE.json` are unchanged. This session's
sandbox denied every hashing path: `shasum`, `openssl dgst`, `node -e`, `python3`, `perl`
and `awk` all returned "requires approval", and a read-only subagent had Bash denied
entirely. **No SHA-256 value in the baseline was recomputed.** Codex must re-run the
baseline hash commands before assembly.

Substitute evidence actually gathered (weaker than a hash, stated as such):

| Check | Method | Result |
|---|---|---|
| Home `src/body.html` unchanged | `diff body.html home/index.html \| grep -c '^<'` against the assembled page written 12:11:28 (before the 13:16 baseline) | `0` source lines missing from the assembled page |
| Transformation `src/body.html` unchanged | same method against `routes/transformation/index.html` | `0` |
| Home/Transformation `direction.css`, `direction.js`, `meta.json` | `ls -lT` mtimes | all dated 2026-09-01 or 2026-09-02 ≤ 12:16:14, i.e. before the 13:16:00 baseline capture; none touched this session |
| WorkGraph, Build, Trust, Company, Assessment, Impact `direction.js` | `ls -lT` mtimes | all ≤ 2026-09-02 11:20:36; none touched this session |
| Control of the method | edited WorkGraph body vs its pre-edit page | `7` mismatching lines, as expected for an edited file |

### 1.2 Protected carriers: byte-compared, not hashed

| Carrier | Baseline range | New range | Method | Result |
|---|---|---|---|---|
| WorkGraph lifecycle carrier | `body.html` 112–134 | **118–140** (shifted +6 by the index move above it) | `sed -n '118,140p' \| diff - workgraph/index.html \| grep -c '^<'` | `0` mismatches |
| Build Factory carrier | `body.html` 52–152 | 52–152, unchanged | covered by the suffix check below | — |
| Build protected suffix | `body.html` 52–EOF (196 lines) | 52–196, line count unchanged at 196 | `sed -n '52,196p' \| diff - build/index.html \| grep -c '^<'` | `0` mismatches |
| Build control | edited lines 12, 34, 40 | — | same method on those three lines | `3` mismatches, as expected |
| Build control | untouched lines 1–11 | — | same method | `0` |

The baseline hash `workgraphLifecycleHtmlLines112To134` will **not** reproduce at lines
112–134 any more; Codex should re-key it to 118–140. The Build suffix hash should
reproduce unchanged because lines 52–196 are byte-identical and the file still ends at
line 196; this is asserted from the ordered-diff result, not from a recomputed hash.

### 1.3 Assembler check-mode was not run

`node tools/build_golden_standard_previews.mjs --check` required approval and was not
executed. The write-mode assembler was deliberately not run per FS4A. Every
`preview/golden-standard/routes/*/index.html` is therefore still the pre-FS4A assembly
from 12:11:28 and will fail a check run until Codex re-assembles. **Assembly is pending.**

### 1.4 No rendered verification of any kind

No browser, viewport, reduced-motion, no-JavaScript, keyboard or contrast check was run.
Every composition statement below is a source-level intent. Viewports listed in FS4 §7
remain entirely untested by this pass.

### 1.5 Content-contract text now diverges from source (Codex to reconcile)

The corrections are authorized by FS4 §3 and FS4A, but three places in
`FULL-SITE-CONTENT-CONTRACT.md` still carry the pre-correction copy. Claude does not own
that file.

- Build 1 Lead (contract line ≈819) still ends `It builds only what the operating model justifies.`
- Build 2 Intro (≈836) still opens `Once a build is justified, the first decision is not which model to use. It is whether…`
- Build 2 Automate body (≈846) still opens `When the workflow is sound but people move information…`
- Impact 1 Primary action (≈1041) still reads `Inspect the approved proof`.

The Company summary sentence, the disclosure summary label and its secondary text
(`Inspect the full partnership standard` / `Five commitments · diligence boundary`) exist
only in FS4A; they are not yet in the contract.

### 1.6 Page-map deviations introduced by the package

- `ASSESSMENT-PAGE-MAP.md` §Composition 1 says `5/7 copy and one large scope object`.
  With the list moved out, the scope object is compact, so the Hero split was authored as
  **7/5** (copy dominant) at ≥940 px. This is a deliberate deviation for Codex to accept
  or reverse in `direction.css` line 79.
- `TRUST-PAGE-MAP.md` §Visual hierarchy says `The hero contains one large coded control
  path`. The path now sits in a band directly after the copy-led Hero, as FS4 §3 requires.
- `COMPANY-PAGE-MAP.md` §Composition 4 (`one Ink field with named decisions and
  boundaries`) is now mostly progressive; only the eyebrow, H2, one summary sentence and
  the Trust link are default-visible, as FS4 §3 requires.
- `WORKGRAPH-PAGE-MAP.md` §Local orientation says the index `follows the hero visual`. It
  now follows the whole Hero section (after the actions), which matches the page map's own
  mobile order (`actions and then the route index`) at every width.

### 1.7 Behavioral notes for Browser QA

- **Trust settle timing.** `trust/src/direction.js` (unchanged) sets `data-trust-ready`
  on the second animation frame, not on scroll. Now that the instrument sits below the
  Hero, the finite 1.5 s settle may complete before the instrument enters the viewport at
  short desktop heights (e.g. 1280×720, 1366×768). The resolved state is still correct;
  only the visibility of the settle changes. If Codex wants the settle to be seen, that is
  a JavaScript change outside FS4A ownership.
- **`--shadow-ink` is undeclared.** `trust`, `assessment` and `workgraph` direction CSS
  (pre-FS4A, unchanged by this pass in that respect) use `box-shadow: var(--shadow-ink)`,
  and no declaration of `--shadow-ink:` exists under `preview/golden-standard` or
  `design/golden-standard`. The declaration is therefore invalid and no shadow renders.
  Pre-existing; tokens are read-only; reported, not fixed.
- **Company disclosure indicator.** The native `<details>` summary is text-only with the
  marker hidden, mirroring the accepted Trust record disclosure and the sparse icon
  budget. It relies on the shared `summary:focus-visible` ring and the `.on-ink`
  `--focus-ring: var(--paper)` token for visible focus.

### 1.8 Default-visible word budgets not re-measured

Build lost 46 default-visible words; Company moved roughly 120 words from default to
progressive. Route budgets in the contract §4.1 were not re-measured on a rendered page.

---

## 2. Changed files (exactly these; all FS4A-owned)

| File | Change |
|---|---|
| `preview/golden-standard/routes/workgraph/src/body.html` | Removed `<nav class="workgraph-index">` from `.workgraph-hero`; added `.workgraph-index-band` wrapper immediately after the Hero `<section>` holding the identical nav (four links, labels, `aria-label`, `data-copy-scope` unchanged). 167 → 173 lines. |
| `preview/golden-standard/routes/workgraph/src/direction.css` | Hero `padding-block` now `var(--space-8)` both sides; new `.workgraph-index-band` rules for desktop/tablet/mobile; removed the invalid `grid-column/grid-row/align-self` placement of `.workgraph-index` from the ≥940 px block; mobile spacing at ≤600 px. |
| `preview/golden-standard/routes/build/src/body.html` | Three in-place copy cuts on lines 12, 34, 40 only. Lines 1–11, 13–33, 35–39, 41–196 byte-identical. |
| `preview/golden-standard/routes/trust/src/body.html` | Removed `.trust-hero__instrument` from `.trust-hero`; added `.trust-control-path` wrapper immediately after the Hero `<section>` containing the identical instrument node (wording, `data-trust-instrument`, `data-trust-node`, `data-trust-state`, `aria-live` unchanged). 108 → 115 lines. |
| `preview/golden-standard/routes/trust/src/direction.css` | Hero copy-led and full-width (no ≥940 px two-column grid; `.trust-hero__copy` max 1080 px; H1 14ch; lead 62ch); removed `min-height: 560px`; instrument `<ol>` becomes three columns at ≥940 px and stays vertical below; band padding; ≤600 px padding and stretched actions. |
| `preview/golden-standard/routes/company/src/body.html` | Added `<p class="company-standard__summary">` with the exact FS4A sentence inside `.company-standard__intro`; wrapped the unchanged five-item `.company-standard__list` and `.company-standard__boundary` in `<details class="company-standard__detail">` with `<summary><span>Inspect the full partnership standard</span><small>Five commitments · diligence boundary</small></summary>`; Trust link remains outside the disclosure. No script. 90 → 96 lines. |
| `preview/golden-standard/routes/company/src/direction.css` | Summary paragraph, native disclosure and summary styling on ink; ≥940 px grid now places intro in column 1 and details + link in column 2; ≤600 px summary stacks. |
| `preview/golden-standard/routes/assessment/src/body.html` | Hero keeps eyebrow, H1, lead, primary CTA and the compact scope aside (`Assessment scope` / `One material path.` / `Not the whole company.`); the unchanged four-item `<ol>` and the secondary CTA `See what you leave with` (`#deliverable`) moved into a new `.assessment-scope-detail` band immediately after the Hero. `#inquiry`, `#deliverable`, form and noscript untouched. 107 → 116 lines. |
| `preview/golden-standard/routes/assessment/src/direction.css` | Removed `min-height: 560px`; compact scope spacing; `.assessment-scope-detail` band styles; list one column <600 px, two columns ≥600 px; ≥940 px band split 7/5 with list left and action right; Hero split authored 7/5 (see §1.6). |
| `preview/golden-standard/routes/impact/src/body.html` | Hero primary CTA changed from `#approved-proof` / `Inspect the approved proof` to `#evidence-chain` / `Inspect the evidence standard`. Empty `#approved-proof` slot, `Approved proof · none published` and `Internal staging route · not published` retained; `meta.json` (noindex) untouched. |
| `evidence/FULL-SITE-STAGING/FS4-IMPLEMENTATION-REPORT.md` | This report. |

Not touched: Home (`preview/golden-standard/home/`), Transformation, `company/src/direction.js`
(listed as FS4-owned but FS4A requires no script for the disclosure), every other
`direction.js`, every `meta.json`, every generated `index.html`, shared chrome, tokens,
component library, assembler, manifests, imagery, authority documents, content contract.

---

## 3. Build word cut (target 46)

| Cut | Text removed / changed | Words |
|---|---|---|
| 1 `.build-lead` | `It builds only what the operating model justifies.` | −8 |
| 2 `.build-modes__intro p` | removed `Once a build is justified, the first decision is not which model to use.` (−14); `It is whether` → `Decide whether` (−1) | −15 |
| 3 Automate card body | `When the workflow is sound but people move information between disconnected systems, Dagg builds a bounded agent or automation layer around what remains.` | −23 |
| **Net** | | **−46** |

Preserved: both mode H3/body blocks, `Prepare only. Never release.` (line 97),
`Release owner` / `Finance owner.` (99), `Service owner.` (111), `Accountable owner` /
`Finance owner.` (165). Nothing from `.build-section--factory` (line 52) onward changed.

---

## 4. Source checks actually run (all read-only; commands verbatim)

```
git rev-parse HEAD
git status --short
git status --short -- preview/golden-standard/home preview/golden-standard/shared design/golden-standard/system tools
wc -l preview/golden-standard/routes/{workgraph,build,trust,company,assessment,impact}/src/body.html
grep -c "" preview/golden-standard/routes/{workgraph,trust,company,assessment}/src/direction.css
grep -n "workgraph-index|workgraph-section--hero|id=\"record\"|id=\"lifecycle\"|id=\"control\"|id=\"learning\"|data-workgraph-lifecycle-carrier" workgraph/src/body.html
sed -n '118p;140p' workgraph/src/body.html
grep -n "operating model justifies|Once a build is justified|It is whether|Decide whether|When the workflow is sound|explicit before execution|build-section--factory|Prepare only. Never release|Release owner|Finance owner" build/src/body.html
sed -n '52p;118p;123p;152p;196p' build/src/body.html
grep -n "trust-hero__instrument|trust-control-path|data-trust-instrument|data-trust-node|data-trust-state|id=\"permission\"|trust-section--hero|min-height: 560" trust/src/body.html trust/src/direction.css
grep -n "company-standard__summary|company-standard__detail|<summary>|</details>|company-standard__list|company-standard__boundary|company-standard__link|Dagg names the decision|Inspect the full partnership standard|Five commitments" company/src/body.html
grep -n "assessment-hero__scope|assessment-scope-detail|One material path|Not the whole company|See what you leave with|Send one path for review|id=\"inquiry\"|id=\"deliverable\"|Accountable next move|data-assessment-form|min-height: 560" assessment/src/body.html assessment/src/direction.css
grep -n "evidence-chain|approved-proof|Inspect the evidence standard|Inspect the approved proof|none published|Internal staging route" impact/src/body.html impact/src/meta.json
grep -n ":root|@font-face|.chrome-|.cl-flyout|.cl-fp|.cl-ico|.cl-meta|.cl-sr|.skip-link" {workgraph,trust,company,assessment}/src/direction.css   # no hits
grep -c "It builds only what the operating model justifies" build/index.html   # 1 → assembled page is pre-edit
sed -n '52,196p' build/src/body.html | diff - build/index.html | grep -c '^<'          # 0
sed -n '118,140p' workgraph/src/body.html | diff - workgraph/index.html | grep -c '^<' # 0
sed -n '23,31p' trust/src/body.html | diff - trust/index.html | grep -c '^<'           # 0 (moved instrument byte-identical)
sed -n '62,69p' company/src/body.html | diff -w - company/index.html | grep -c '^<'    # 0 (list + boundary identical, indentation aside)
sed -n '27,32p' assessment/src/body.html | diff -w - assessment/index.html | grep -c '^<' # 0 (list identical, indentation aside)
sed -n '1,11p' build/src/body.html | diff - build/index.html | grep -c '^<'            # 0 control
sed -n '12p;34p;40p' build/src/body.html | diff - build/index.html | grep -c '^<'      # 3 control
diff preview/golden-standard/home/src/body.html preview/golden-standard/home/index.html | grep -c '^<'                 # 0
diff routes/transformation/src/body.html routes/transformation/index.html | grep -c '^<'                               # 0
diff routes/workgraph/src/body.html routes/workgraph/index.html | grep -c '^<'                                         # 7 control
ls -lT <read-only src files, assembled index.html files, FS4-INVARIANT-BASELINE.json>
grep -rl "shadow-ink:" preview/golden-standard design/golden-standard   # no hits
```

Commands attempted and denied by the sandbox (not run): `shasum -a 256`, `openssl dgst
-sha256`, `node -e`, `node tools/build_golden_standard_previews.mjs --check`,
`python3 -c`, `perl -MDigest::SHA`, `awk`, `git hash-object`, `cksum -a sha256`, output
redirection to `/tmp`.

### Anchor resolution (source level)

| Link | Target present in the same route source |
|---|---|
| WorkGraph index `#record`, `#lifecycle`, `#control`, `#learning` | lines 46, 105, 145, 123 |
| Assessment `#inquiry`, `#deliverable` | lines 85, 67 |
| Impact `#evidence-chain` | line 41; `#approved-proof` slot retained at line 63 |
| Company → `/preview/golden-standard/routes/trust/#permission` | trust `body.html` line 35 |

### Assembler-rule pre-check

Edited `direction.css` files contain none of `:root`, `@font-face`, `.chrome-`,
`.cl-flyout`, `.cl-fp`, `.cl-ico`, `.cl-meta`, `.cl-sr`, `.skip-link`. Edited bodies add
no header, footer, `<main>` or flyout markup. The `·` in `Five commitments · diligence
boundary` sits inside a sentence and does not stand alone as a control label.

---

## 5. Composition intent per correction (unrendered)

- **WorkGraph.** Hero: eyebrow, H1, lead, Decision Field still, actions. Index band: one
  top rule, four plain anchors (48 px min targets) wrapping in order; band bottom padding
  `--section-md` (mobile `--space-8`), `--section-lg` at ≥940 px. Carrier untouched.
- **Build.** Copy only. No layout change.
- **Trust.** Hero: eyebrow, H1 (14ch), lead (62ch), two actions, full width. Control-path
  band: the ink instrument; at ≥940 px the three steps sit in three columns, each on its
  own rule (permission coral, owner sage), `Authority resolved` below; below 940 px the
  steps stack as before. Settle and reduced-motion rules unchanged.
- **Company.** Standard section: intro column with eyebrow, H2, summary sentence;
  disclosure column with a 64 px summary row, then the five-item list and boundary when
  open; Trust link below the disclosure. Single column in DOM order below 940 px.
- **Assessment.** Hero 7/5 at ≥940 px: copy and primary CTA left, compact ink scope object
  right. Scope-detail band: list (two columns from 600 px) and the secondary CTA
  (right column at ≥940 px, below the list otherwise).
- **Impact.** CTA label and target only.

---

## 6. Handoff

Source revision handed to Codex for assembly: working tree of commit `f688c543…` with the
ten FS4A source files above modified. Codex should (1) recompute every hash in
`FS4-INVARIANT-BASELINE.json`, re-keying the WorkGraph carrier to lines 118–140; (2) run
the shared assembler; (3) reconcile the content contract per §1.5; (4) judge §1.6 and
§1.7 in Browser QA on the immutable snapshot. Nothing in this report claims visual,
responsive, accessibility or assembled acceptance.
