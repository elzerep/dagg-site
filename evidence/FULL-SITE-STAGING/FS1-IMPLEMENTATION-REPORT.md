# FS1 — Whole-site staging skeleton: implementation report

Package: `design/golden-standard/packages/FS1-WHOLE-SITE-STAGING-SKELETON.md`  
Parent authority: `design/golden-standard/packages/FS0-WHOLE-SITE-STAGING-AUTHORITY.md`  
Implementer: Claude Code (non-interactive session)  
Date: 2 September 2026  
Returned to: Codex, for integration review

No deployment or publication occurred. Nothing was pushed, served publicly,
committed or published. Impact was not added to shared navigation.

## 1. Failures and limitations (read first)

1. **Assembler not run.** `node tools/build_golden_standard_previews.mjs`
   and its `--check` form were both denied by the session permission layer
   ("This command requires approval"; non-interactive, no prompt possible).
   Consequently `preview/golden-standard/routes/impact/index.html` and an
   updated `evidence/HOME-DIRECTIONS/shared-substrate/build-manifest.json`
   do **not** exist yet. Codex must run the assembler once at integration.
   Discovery is a sorted walk for `*/src/body.html`, so no assembler edit is
   required; the Impact source will be found automatically.
2. **No browser or served render.** `python3 tools/serve_preview.py`,
   `playwright-cli` and Python Playwright were all denied. Verification item 7
   (console errors, rendered hidden content) is therefore **not covered** in
   this session. Static source checks stand in for it below and make no
   visual-acceptance claim (CLAUDE.md rule 5).
3. **Indexing prevention is not head-level in the assembled page.** The
   assembler's `meta.json` contract has no robots field and FS1 does not own
   `head.html`. The route is marked `routeState: internal-staging`,
   `publication: omitted-until-approved-proof` and `robots: noindex, nofollow`
   in `meta.json` (recorded, but inert to the current assembler), and
   `direction.js` applies `<meta name="robots" content="noindex, nofollow">`
   at runtime as progressive enhancement. A static noindex would require either
   a `head.html` partial or a meta.json `robots` field in the assembler, both
   outside FS1 ownership. Recommended FS2/FS4 follow-up.
4. **Copy density is below the contract band by design.** Page 5 gives a
   320-460 visible-word budget "with one approved proof". With no approved
   proof, the route carries roughly 230 visible words. This is the fallback
   state the contract requires, not a shortfall to fill.
5. **Hashing tool substitution.** `shasum`, `openssl dgst` and `cksum` were
   denied; `sha256sum` was permitted and used for every hash below.
6. `preview/golden-standard/routes/impact/src/body.html` already existed on
   disk at session start (untracked, mtime 2 September 2026 10:18, SHA-256
   `78b4c32e…a26a3325`). It is an FS1-owned file, matched Page 5 exactly and
   was retained unchanged rather than rewritten.

## 2. Files created or owned

| File | State |
| --- | --- |
| `preview/golden-standard/routes/impact/src/body.html` | pre-existing FS1 draft, retained byte-identical |
| `preview/golden-standard/routes/impact/src/direction.css` | created |
| `preview/golden-standard/routes/impact/src/direction.js` | created |
| `preview/golden-standard/routes/impact/src/meta.json` | created |
| `evidence/FULL-SITE-STAGING/FS1-IMPLEMENTATION-REPORT.md` | this file |
| `evidence/FULL-SITE-STAGING/FS1-ACCEPTANCE.json` | created |
| `preview/golden-standard/routes/impact/index.html` | **not generated** (see failure 1) |

No other file was written. Home, shared chrome, tokens, assembler, existing
route sources, image masters, authority documents, packages and `CLAUDE.md`
were not touched.

## 3. Copy source

Every public sentence, label and link text comes from
`design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`, Page 5 —
Impact, acts 1-5, in contract order: Position, Proof types, Evidence chain
(`id="evidence-chain"`), Lead proof slot (`id="approved-proof"`), Next move.
Title and description come from the Page 5 metadata row of the same contract.

Two route-state sentences are not contract copy and are the truthful
staging disclosure the package requires in §4:

- `Internal staging route · not published` (hero state line)
- `Approved proof · none published` plus `Publication requires an approved
  proof. A case appears here only when its company, Dagg's role, the
  evidence, the timeframe and permission to publish have passed review.`

Internal-only contract text (`Systems operated`, Aloi, "not public copy",
internal anchor/status/fallback rules, required case fields) does not appear
in the route.

Contextual links use the existing preview-route convention:
`#approved-proof`, `/preview/golden-standard/routes/assessment/` (twice),
`/preview/golden-standard/routes/transformation/`. Brand link is
`/preview/golden-standard/home/`. No `currentNavHref` is declared because
Impact is not in shared navigation.

## 4. Design and interaction

- Reuses the accepted route-kit grammar (`.page` / `.field`, `cl-eyebrow`,
  `h1`, `h2`, `cl-h3`, `lead`, `cl-body`, `cl-actions`, `cl-button`,
  `cl-link`, `on-ink`) and the Company/Build section rhythm and rule pattern.
- No image, no icon, no autoplay, no fake proof artifact, no new motion
  system. `direction.css` declares no transition or animation, so reduced
  motion is the resolved state by construction.
- The approved-proof slot is a bordered editorial note with a mono status
  line and one serif disclosure sentence, not a card grid or placeholder
  tile.
- `direction.js` only injects the robots meta tag and sets a ready attribute
  that no CSS depends on. No content is hidden, reordered or revealed by
  script; the no-JS reading order printed from source is complete.

## 5. Assembler command and result

```
node tools/build_golden_standard_previews.mjs --check   → denied (requires approval)
node tools/build_golden_standard_previews.mjs           → denied (requires approval)
```

Result: not run. Expected output when Codex runs it:
`preview/golden-standard/routes/impact/index.html` (generated; do not
hand-edit) and an updated shared-substrate `build-manifest.json`.

Impact route path once assembled: `/preview/golden-standard/routes/impact/`.

## 6. Source-preservation hashes (SHA-256, `sha256sum`)

Preflight was taken before any write; postflight after all writes. Every
pre-existing hash is identical. The manifest and every generated `index.html`
are also unchanged because the assembler did not run.

```
5bcbf7db5bc85e9d975cb58a9367930272c304286fd41e63dfc3fb7f5a10ff6e  routes/assessment/src/body.html
35a71d0becb920fad2cb1688163a3911a00abf72ed857bdb148b0a6a4adca406  routes/assessment/src/direction.css
daf5b1338619255bad1289ec5c48b15030b4048845bd844898cde3707614dc81  routes/assessment/src/direction.js
4df28705ab69830b5f123596ddb8d22912a657fab889c400a0f32b120a197913  routes/assessment/src/meta.json
20ad8d03f1e093724b27342d22901361afbce5e27c5c16ad17f398d3d1819fbc  routes/build/src/body.html
343db3274d54330523daff41994f08906d10b1c73b88bf18408f3844d2c43b93  routes/build/src/direction.css
73d2d7a370668dae62e5a9e1ef517eaf259190d3481048b0c91ac3ec6afa2fea  routes/build/src/direction.js
e5360d3efc84e968953fa77ae2cac4ee24af500168271dff79ccceacd13a3ee4  routes/build/src/meta.json
c9c8480456b84c8c35d2e6b0c13af24111888584dceb97f9b1810b20a018e6ed  routes/company/src/body.html
05ad37cfee0f2d131efd9fca91ff580643074af78c1ed11e6740311230430058  routes/company/src/direction.css
a03df84cf2fbcc0838c4a93c8326acb10c838586b5269a7950a43df9ab338b38  routes/company/src/direction.js
ecaa69dedb1e4a1b49fc37be76d54a714168b7ff8af9b45ca6d4a54decd49c1b  routes/company/src/meta.json
b14c16ff08e4b7924858b35ff3e67caf54797bd6475a73e278e8b59d68d36032  routes/transformation/src/body.html
a43c2f1794cdf7185fb0675d4621d8d694f39588eeb43720c59cb1270767b088  routes/transformation/src/direction.css
7273412684f776ba3353fdb1b806c2756ce50182e9c3646eccce33679e7b0040  routes/transformation/src/direction.js
066896168859ad0c2b4e6225bde2cc85a4c6603785ef42f7e5f67cd24d29d2c0  routes/transformation/src/meta.json
6b53765205ad1d3a771e0978d6abb0b01d52e0eb8a1029e2a29babcc8246bcb8  routes/trust/src/body.html
d1bc74be826fc0b66f0afc3f21d6b14acef94740385b15e627c410ab3e60640d  routes/trust/src/direction.css
ebcf9d5748a033265e6da0794eb51c0fb6592d0e19bc6b9ba48508fb5f7534b3  routes/trust/src/direction.js
036006a1fe61610dc1544ea4e7dd54388f6d6e37ff12375fdd162f2c880daa74  routes/trust/src/meta.json
32fef135916f24f8cbf42f261f597cc0a4e0c6c618e2dbe267e260d76ccbaf4c  routes/workgraph/src/body.html
3444233c707ee6e4aa7b5fef64e9ee56a851df4e6b2afefd93888ee398d2e90e  routes/workgraph/src/direction.css
765ba2718c3a6dfe864146c736e4f807d69a5bf1c4aa492c5c0fbb97fa6afe25  routes/workgraph/src/direction.js
aea01d7ce5e0d276c17ffa6ae69f30677f76545cc045a26e95a8ed63ac3e6bb0  routes/workgraph/src/meta.json
92a57d55fad3bfe48d6f1d3ff92e981940aaf731c8cde44b15d0bf68990fc325  home/src/body.html
8499460a3a205e56ee4b38eab9f8886d4e444039aaa1e7bbf7ce3abd1c723eec  home/src/direction.css
59c2f3066f906cb853d65bf649da31ca8d2c7dcf6403dd1aa81a679194890f94  home/src/direction.js
a4f261e139e5c40a4b6e359634dc103a6bdab92b52af342b90d30b6967859ba7  home/src/meta.json
4909454a75dde120d2968a245957735197e7281dcb15b9c7f24e0d186ace53df  shared/chrome/chrome.css
544e590b4c2b19d81c967625eea4ea409f9b71c68a355e46e9c750d97125e3b0  shared/chrome/chrome.js
070c5e66f6b605936066a4bb29d0d82d34924fcbc3b15028785b6bd77756db2a  shared/chrome/footer.html
dd827a94208e5c3c3366d87db0b17d108d446d756b58bc74611371fe932475bb  shared/chrome/header.html
c5cdc077b7e1810e1a27448c821e4d12868f570e6137128416c02a1bd3a2f563  shared/fixture/src/body.html
91f394c385b9b2e35fe6bbbeeaa6488a0f49d4ad362e1988abf0e916842431d3  shared/fixture/src/direction.css
4cd6c94daca7f7207b026f7d9dc44559b1ab4215f408115cf4e387cd5b8bff9c  shared/fixture/src/direction.js
892737daeb67fb25ca779f8f3ae48510cef85185600bc0b9abed1313541fd7b1  shared/fixture/src/meta.json
5abe1da6c5d18a9c0f2d37ea61f7e0db58ad0f465eb65970079cc7ee15c88d87  shared/fixture/index.html
a40a83a067306dba57217aea2dff3ce97242f434f2a1cfc8f82f3d0bf4e4b964  home/index.html
6d33f02c4886e313d5be4a934b3133ff2b572fbd245bdc050aea591b269429e7  routes/assessment/index.html
167fa72665e8580ac259b956bd6092806e0e0920fd0fb3edb73502c9f2729fec  routes/build/index.html
ee18cbb4a425f9f2296f3b93b8f43990c91bebe756aeb64ca99cf2874b87db34  routes/company/index.html
19215cf36855fc9201cd80587d64b4898a18eec3f11c6a60400288a777b6c58a  routes/transformation/index.html
533296e9dbdd6bca9eaf1622758bd76a8de53686ef1924e19a56b896be00d305  routes/trust/index.html
19b685ba1b193925d4ead57c4dfc87fb3f4789fb739d9dc2cc165f43988dfc81  routes/workgraph/index.html
81201a6a00d0d01143415efeb4703ca477869ed39e9a16a2c573237cea9706c5  evidence/HOME-DIRECTIONS/shared-substrate/build-manifest.json
```

Paths above are relative to `preview/golden-standard/` except the manifest.
FS1-owned source hashes are recorded in `FS1-ACCEPTANCE.json`.

## 7. Checks run and exact coverage

All checks are static, on source files, via `grep`/`ls`/`sha256sum`. No
rendered revision, viewport or browser state was covered.

| Package §6 item | Result | Coverage |
| --- | --- | --- |
| 1 Run assembler | **NOT RUN** | denied by permission layer |
| 2 Impact discovered, page resolves | **NOT VERIFIED** | depends on 1; discovery rule read and satisfied by `impact/src/body.html` |
| 3 Pre-existing sources byte-identical | PASS | 46 files, SHA-256 preflight = postflight |
| 4 Local references resolve | PASS (source-level) | 4 hrefs; both route targets have `index.html`; `#approved-proof` exists |
| 5 Exactly one H1; anchors once each | PASS | `<h1` ×1, `id="evidence-chain"` ×1, `id="approved-proof"` ×1 |
| 6 No Aloi / Systems operated / internal text | PASS | case-insensitive grep over body: 0 hits |
| 7 No hidden content, no click-required comprehension, no console error | PARTIAL | source has no `hidden`, `display:none`, `visibility` or `<svg>`; reading order printed complete from source; console **not covered** |
| 8 Limitations recorded | PASS | §1 above |

Assembler static rules checked by hand against source: no forbidden shared
DOM in `body.html`; no `.chrome-`, `.cl-meta`, `.cl-sr`, `:root`,
`@font-face` or `url(` in `direction.css`; no `cl-enhanced`/`cl-booting`
write, remote URL or SVG construction in `direction.js`. The `·` glyph appears
only inside sentences, never as a whole element label.

## 8. Remaining FS2/FS3 work and Codex integration steps

Integration (Codex, FS1 acceptance):

1. Run `node tools/build_golden_standard_previews.mjs`; confirm
   `routes/impact/index.html` is emitted and the manifest lists seven routes
   plus home and fixture.
2. Serve with `python3 tools/serve_preview.py --port 8912` and check
   `/preview/golden-standard/routes/impact/` at 320, 390, 768, 1024 and 1440
   for console errors, anchor scroll-margin under the sticky header, and the
   on-ink evidence chain contrast.
3. Decide whether a static `noindex` belongs in the assembler meta contract
   or a `head.html` partial (failure 3).

FS2: convert WorkGraph and Factory to the scroll-led interaction contract.
FS3: integrate final Home composition and the selected Decision Field hero.
FS4: one-pass responsive, accessibility, performance and route QA, which is
also where Impact's rendered review should land.

No deploy or publication occurred, and none is authorized by this report.
