# FS4A — Supporting-route corrections

Status: **HISTORICAL — WRITE SCOPE SUPERSEDED AND REVOKED BY FS5**  
Parent authority: `FS4-WHOLE-SITE-POLISH-AND-QA.md`  
Implementation owner: Claude Code  
Acceptance owner: Codex

The corrections below record the earlier FS4A pass. They grant no current file
ownership; the active FS5 Lane A/B/C packages control all further source work.

## Objective

Apply the six known supporting-route corrections below. This is a bounded
implementation package, not a redesign. Home, Transformation, shared chrome,
tokens, imagery, JavaScript carriers and authority documents remain read-only.

## Exact implementation map

### WorkGraph

- Move the existing `<nav class="workgraph-index">` from inside
  `.workgraph-hero` into a new `.workgraph-index-band` immediately after the
  Hero section.
- Keep all four links and labels unchanged.
- Remove the now-invalid desktop grid placement from `.workgraph-index` and
  style the new band for authored desktop, tablet and mobile flow.
- Do not change `[data-workgraph-lifecycle-carrier]`, any
  `[data-workgraph-step]`, `[data-workgraph-record-state]` or
  `workgraph/src/direction.js`.

Owned files:

- `preview/golden-standard/routes/workgraph/src/body.html`
- `preview/golden-standard/routes/workgraph/src/direction.css`

### Build

Make only these three copy cuts:

1. Remove `It builds only what the operating model justifies.` from
   `.build-lead`.
2. Remove the first sentence of `.build-modes__intro p` and change
   `It is whether…` to `Decide whether…`.
3. Remove the first sentence of the Automate card body.

The intended net cut is 46 words. Preserve both build modes, the permission
boundary and accountable owner. Do not change anything from
`.build-section--factory` onward and do not change `build/src/direction.js`.

Owned file:

- `preview/golden-standard/routes/build/src/body.html`

### Trust

- Move the complete existing `.trust-hero__instrument` node out of the Hero
  into a bounded post-Hero wrapper immediately after the Hero.
- Keep all wording and data attributes unchanged.
- Make `.trust-hero` copy-led and full-width.
- Recompose the moved three-step instrument horizontally at widths of 940px or
  more and vertically below that breakpoint.
- Remove the current 560px Hero minimum.
- Do not change `trust/src/direction.js`.

Owned files:

- `preview/golden-standard/routes/trust/src/body.html`
- `preview/golden-standard/routes/trust/src/direction.css`

### Company

- Keep the partnership-standard eyebrow and H2 visible.
- Add this exact visible summary:
  `Dagg names the decision, its boundary, the accountable owner and the evidence required before release.`
- Wrap the existing five-item `.company-standard__list` and
  `.company-standard__boundary`, unchanged, in native
  `<details class="company-standard__detail">`.
- Use summary label `Inspect the full partnership standard` with secondary
  text `Five commitments · diligence boundary`.
- Keep the Trust link outside the disclosure.
- Use no JavaScript for the disclosure.

Owned files:

- `preview/golden-standard/routes/company/src/body.html`
- `preview/golden-standard/routes/company/src/direction.css`

### Assessment

- Keep eyebrow, H1, lead, primary CTA and the compact scope text
  `One material path.` / `Not the whole company.` in the Hero.
- Move the existing four-item ordered list, unchanged, into a post-Hero
  `.assessment-scope-detail`.
- Move the secondary CTA `See what you leave with` into that same band.
- Remove the desktop 560px scope minimum and author the split for desktop,
  tablet and mobile.
- Preserve `#inquiry`, `#deliverable` and the truthful non-transmitting form.
- Do not change Assessment JavaScript.

Owned files:

- `preview/golden-standard/routes/assessment/src/body.html`
- `preview/golden-standard/routes/assessment/src/direction.css`

### Impact

- Change the Hero primary CTA from `Inspect the approved proof` /
  `#approved-proof` to `Inspect the evidence standard` / `#evidence-chain`.
- Keep the truthful empty proof slot and noindex staging status.

Owned file:

- `preview/golden-standard/routes/impact/src/body.html`

## Verification before handoff

- Do not run the write-mode assembler. It rewrites generated routes outside
  this package's ownership. Codex runs the shared assembler during integration.
- Source-check the six corrections and report that assembly remains pending.
- Confirm Home and Transformation source hashes are unchanged.
- Confirm the protected WorkGraph lifecycle and Build Factory carriers retain
  their original DOM order, data attributes and JavaScript.
- Confirm every moved local anchor still resolves.
- Inspect the assembled source for all exact copy and disclosure contracts.
- Do not deploy, publish, commit or promote canonical routes.

## Report

Write a failure-first report to:

`evidence/FULL-SITE-STAGING/FS4-IMPLEMENTATION-REPORT.md`

List every changed file, every command/test actually run and all unresolved
failures. Hand the source revision to Codex for assembly. Do not claim visual
or assembled acceptance; Codex owns integration and Browser acceptance on the
immutable snapshot.
