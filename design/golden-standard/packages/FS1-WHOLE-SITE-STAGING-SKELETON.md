# FS1 — Whole-site staging skeleton

Status: **ACTIVE**  
Parent authority: `FS0-WHOLE-SITE-STAGING-AUTHORITY.md`  
Implementation owner: Claude Code  
Integration and acceptance owner: Codex

## 1. Objective

Expose one coherent local staging site using the substantial route work that
already exists. Do not redesign accepted supporting pages and do not wait for a
final Home hero. Close the one material route gap by creating an honest internal
Impact route from the exact content contract.

## 2. Read first

1. `CLAUDE.md`
2. `design/golden-standard/packages/FS0-WHOLE-SITE-STAGING-AUTHORITY.md`
3. `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`, especially
   Page 5 — Impact
4. `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`
5. all three authority PDFs named in `CLAUDE.md`
6. existing route sources for Transformation, WorkGraph, Build, Company and
   Assessment, plus the shared fixture and chrome

## 3. Files owned by this package

Create and own only:

- `preview/golden-standard/routes/impact/src/body.html`
- `preview/golden-standard/routes/impact/src/direction.css`
- `preview/golden-standard/routes/impact/src/direction.js`
- `preview/golden-standard/routes/impact/src/meta.json`
- `evidence/FULL-SITE-STAGING/FS1-IMPLEMENTATION-REPORT.md`
- `evidence/FULL-SITE-STAGING/FS1-ACCEPTANCE.json`

If the existing assembler generates
`preview/golden-standard/routes/impact/index.html`, report it as generated
output. Do not hand-edit it. Do not accept modifications to any other generated
route output; restore none and overwrite none manually.

Everything else is read-only, including Home, shared chrome, tokens, existing
route source files, image masters, authority documents, package files and
`CLAUDE.md`.

## 4. Impact contract

Implement exactly the five Impact acts and exact public copy in Page 5 of
`FULL-SITE-CONTENT-CONTRACT.md`:

1. Position
2. Proof types
3. Evidence chain
4. Lead proof slot
5. Next move

Do not publish Aloi, invent a case, invent numbers, imply that Dagg operates a
system today, or expose internal instructions as public copy.

The lead proof area must be a truthful internal-staging state with
`id="approved-proof"` and a visibly calm disclosure that publication requires
an approved proof. It must not look like an empty case card, broken component or
marketing promise. Mark the route as internal staging in metadata and prevent
indexing.

Impact is not added to shared public navigation in FS1. It must still have
contextual links that work inside local staging using the existing preview-route
convention.

## 5. Design and interaction

- Reuse the accepted route kit, tokens, type, spacing and component grammar.
- Do not invent a new page world, hero language, icon family or motion system.
- The route is primarily editorial and evidence-led. No click is required to
  understand it.
- Use no decorative autoplay and no fake proof artifact.
- `direction.js` may be empty or limited to progressive enhancement that does
  not hide content.
- No-JS shows every public sentence in correct reading order.
- Reduced motion is complete and stable.

## 6. Verification

Before reporting completion:

1. Run the existing route assembler using its supported invocation.
2. Confirm the Impact source is discovered and the generated page resolves.
3. Confirm existing source files outside the package are byte-identical to the
   preflight snapshot.
4. Confirm all local references in Impact resolve.
5. Confirm the route contains exactly one H1 and anchors `evidence-chain` and
   `approved-proof` exactly once.
6. Confirm internal instructions, Aloi and `Systems operated` do not appear as
   public copy.
7. Confirm no hidden core content, no click-required comprehension and no
   console error in the browser environment available to you.
8. Record limitations honestly if the browser or port environment is not
   available.

## 7. Required report

Write failures first, then:

- files created;
- exact copy source used;
- assembler command and result;
- Impact route URL/path;
- source-preservation hashes for every pre-existing route source directory;
- checks run and exact coverage;
- remaining FS2/FS3 work;
- explicit statement that no deployment or publication occurred.

Do not ask Christian for approval. Return the completed package to Codex for
integration review.
