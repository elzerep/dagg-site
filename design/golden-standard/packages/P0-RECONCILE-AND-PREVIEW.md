# P0 · Reconcile authority and create an exact-revision preview

Status: ready · control set frozen after IA sign-off  
Authority: `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Base commit: `1e939b5d3acc46f77b53830b25901c8e6a36dadf`  
Gate type: operating acceptance by Codex

## 1. Objective

Make the masterplan the unambiguous repository authority and make every local preview provably belong to one exact Git revision. This package changes no public design, copy, interaction or IA.

P0 is accepted only when:

- legacy design documents cannot override the masterplan;
- the preview server prevents mixed-revision HTML/CSS/JS/image rendering;
- an automated check can read the served revision and dirty state;
- the preview itself exposes the same revision in DOM metadata;
- normal preview screenshots remain visually unchanged.

## 2. Final visible copy — use verbatim

No public-facing copy changes.

Repository authority note to insert at the top of each legacy design document named below:

> **Authority status:** Historical evidence and implementation context. If this file conflicts with `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`, the masterplan wins. Do not implement a new visual, narrative, IA, motion or component decision from this file alone.

README preview heading:

> Golden-standard preview

README explanation:

> Run the revision-safe preview command below. It serves every HTML, CSS, JavaScript and image response with no-store headers, exposes the exact Git revision and dirty state at `/__revision`, and injects the same revision into each served HTML document as `<meta name="dagg-revision">`. Do not review the site through another static server.

## 3. Authoritative inputs

- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
- `design/golden-standard/CLAUDE-WORK-PACKAGE-TEMPLATE.md`
- This package file.
- Repository state at exact full hash `1e939b5d3acc46f77b53830b25901c8e6a36dadf`.

The control set is frozen when execution starts. Before the first write, record SHA-256 and byte size for every supplied control file listed in section 4. Recompute them before commit and include both sets in `evidence/P0/result.json`. The values must match. Do not edit this package header during execution.

## 4. Files owned by this package

Only these paths may be created or changed:

- `CLAUDE.md` — include the supplied execution authority unchanged.
- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
- `design/golden-standard/CLAUDE-WORK-PACKAGE-TEMPLATE.md`
- `design/golden-standard/packages/P0-RECONCILE-AND-PREVIEW.md`
- `design/golden-standard/reference-audits/ANTHROPIC-OPENAI-RECIPE.md` — include unchanged.
- `design/golden-standard/reference-audits/PALANTIR-RECIPE.md` — include unchanged.
- `design/golden-standard/reference-audits/xai-current/XAI-CURRENT-AUDIT.md` — include unchanged.
- `design/golden-standard/image-system/decision-field-hero-v2.png` — include unchanged.
- `design/DESIGN-LANGUAGE.md` — authority note only.
- `design/TEMPLATE.md` — authority note only.
- `design/SITEMAP.md` — authority note only.
- `README.md` — revision-safe preview instructions only.
- `tools/serve_preview.py` — new revision-safe local preview server.
- `tools/capture_preview_evidence.py` — new stdlib-only Chrome DevTools Protocol capture harness.
- `tests/test_preview_revision.py` — new exact-revision preview test.
- `evidence/P0/result.json`
- `evidence/P0/` screenshot and DOM evidence files.

If any other file is required, stop and report the dependency. Do not widen scope silently.

## 5. Immutable files and decisions

Do not change:

- any file under `preview/`;
- any file under `assets/`;
- public copy, image assets, CSS, HTML, JavaScript or interaction behavior;
- the branch name;
- navigation, palette, type, grid, spacing, motion or image grammar;
- Git history or earlier commits;
- the masterplan, package-template or P0 contents supplied by Codex;
- the supplied reference-audit and Decision Field reference bytes.

Do not start P1.

## 6. Deliverables

1. Confirm the supplied masterplan, package template, reference audits, Decision Field reference and P0 file are present under `design/golden-standard/`; record their starting hashes, preserve their bytes, record matching ending hashes and include the control tree in the P0 commit.
2. Insert the exact authority note into the three legacy documents without rewriting their historical content.
3. Add one documented command that starts the revision-safe server on a configurable port, defaulting to `8912`.
4. Add `GET /__revision` returning JSON with at least:
   - full commit hash;
   - abbreviated hash;
   - branch;
   - dirty boolean;
   - server start timestamp;
   - repository root.
5. Serve every HTML, CSS, JavaScript, font, JSON and image response with `Cache-Control: no-store, max-age=0`, `Pragma: no-cache` and `Expires: 0`.
6. Inject `<meta name="dagg-revision" content="FULL_HASH">` and `<meta name="dagg-dirty" content="true|false">` into served HTML in memory. Do not edit source HTML.
7. Add an automated test that starts the server on an available local port, fetches one HTML file and its linked CSS, and proves that:
   - both responses have no-store headers;
   - `/__revision` reports the same commit as `git rev-parse HEAD`;
   - HTML metadata matches `/__revision`;
   - dirty state matches `git status --porcelain`;
   - the linked CSS response is fetched from the same server during the test.
8. Add a reproducible stdlib-only evidence capture harness at `tools/capture_preview_evidence.py`. It may drive the installed Google Chrome through the Chrome DevTools Protocol, but it may not introduce a package dependency or write outside `evidence/P0/` and an automatically cleaned temporary directory.
9. Capture fresh screenshots of `preview/directions/a-plus.html` at 1440 px and 390 px, plus a DOM metadata record, from the same revision-safe server process.
10. Write `evidence/P0/result.json` using the masterplan schema plus package-specific checks.

## 7. Behavior and technical contract

- The server binds to loopback by default.
- It must refuse path traversal and may serve only files below the repository root.
- It must not require a new third-party dependency.
- It must not mutate the working tree during serving.
- It must handle spaces and query strings in requested paths.
- A dirty working tree is permitted for development but must be reported as dirty; it may not be disguised as a clean revision.
- The preview review protocol always records both full hash and dirty state.
- The injected metadata must not create any visible layout node.
- Existing preview behavior must remain unchanged.
- The capture harness must launch Chrome with a temporary isolated profile, wait for fonts and document load, capture the full document at the requested viewport width, save the exact page URL and server revision, then close Chrome and clean its temporary profile.

## 8. Executable acceptance tests

Claude must provide the exact command and test output for:

1. `git diff --name-only 1e939b5d3acc46f77b53830b25901c8e6a36dadf...HEAD` contains only owned files.
2. The three legacy documents contain the authority note exactly once.
3. SHA-256 and byte size for every supplied control file are identical at execution start and immediately before commit; both sets are present in the evidence JSON.
4. `/__revision` full hash equals `git rev-parse HEAD` from the served repository.
5. `/__revision.dirty` equals the Boolean result of `git status --porcelain` at server start.
6. Served HTML contains exactly one `meta[name="dagg-revision"]` and one `meta[name="dagg-dirty"]`.
7. HTML, `tokens.css`, a JavaScript file where present, and one image all return the required no-store headers.
8. A fresh request after a local source change returns the changed bytes and dirty state is truthfully represented after server restart.
9. `preview/directions/a-plus.html` has the same screenshot dimensions and no new visible nodes compared with the base revision.
10. Zero server exceptions for the automated request set.

Coverage must include HTML, CSS, JavaScript and one raster image. A test that fetches only HTML is insufficient.

## 9. Required visual and machine evidence

- Full-page screenshot at 1440 px from the revision-safe server.
- Full-page screenshot at 390 px from the same server run.
- Saved `/__revision` response.
- Saved relevant HTML `<head>` DOM snapshot.
- Response-header record for HTML, CSS, JavaScript and image.
- `evidence/P0/result.json` with exact paths.

The screenshots must come from the same server process as the revision and header evidence.

## 10. Performance budget

The server is development-only. It must add no production bundle bytes and no production runtime code. HTML injection overhead is not a public performance concern, but server startup should complete in under two seconds on the current machine.

## 11. P0 evidence JSON additions

In addition to the masterplan fields, include:

```json
{
  "authorityNotes": {
    "design/DESIGN-LANGUAGE.md": 1,
    "design/TEMPLATE.md": 1,
    "design/SITEMAP.md": 1
  },
  "revisionEndpointMatchesGit": true,
  "domRevisionMatchesEndpoint": true,
  "dirtyStateMatchesGit": true,
  "noStoreCoverage": ["HTML", "CSS", "JavaScript", "raster-image"],
  "visiblePreviewChanged": false
}
```

## 12. Stop conditions

Stop and report before changing code if:

- the base commit is not the expected current `design-language` HEAD;
- the working tree contains any pre-existing change outside the supplied untracked `CLAUDE.md` and `design/golden-standard/` control files;
- an owned legacy document contains uncommitted user edits;
- exact revision injection would require editing public preview source files;
- the server cannot be implemented without a new third-party dependency;
- any test requires a destructive Git operation.
- the supplied control set changes after its starting hashes are recorded.

Do not continue to P1.

## 13. Required completion report

Return in this order:

1. Deviations or failures first.
2. Exact full commit and files changed.
3. Evidence JSON path.
4. Screenshot and header/DOM evidence paths.
5. Tests run and what each test covers.
6. What is ready for Codex operating acceptance.

Do not call P0 complete until the revision endpoint, DOM metadata, no-store coverage and visual non-change all have evidence.
