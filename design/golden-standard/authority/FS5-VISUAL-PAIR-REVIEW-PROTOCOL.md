# FS5 visual pair review protocol

Status: binding post-implementation visual acceptance.

Use only the canonical desktop `1440×900`, tablet `1024×768` and mobile
`390×844` views for visual judgment. Capture the first viewport and full page
from one immutable snapshot. Geometry alone cannot pass a route: every pair
must pass caption-free causal recognition and the grayscale silhouette test.

## Breakpoint continuity — 12 pairs

For Home, Transformation, WorkGraph, Build, Trust and Company compare:

- `1440×900 ↔ 1024×768`
- `1024×768 ↔ 390×844`

Reject if hierarchy changes rather than recomposes, a required mechanism falls
below the fold, imagery becomes a token sliver, or whitespace appears where the
wider composition carried meaning.

## Route-silhouette distinction — 18 pairs

At each viewport compare grayscale, text-obscured thumbnails, downscaled to
approximately 180 px wide and randomized:

- Home ↔ Transformation
- Transformation ↔ WorkGraph
- WorkGraph ↔ Build
- Build ↔ Trust
- Trust ↔ Company
- Company ↔ Home

The reviewer must identify all six without copy or colour:

- Home: proposition above a dominant full-width image band.
- Transformation: 7/5 thesis beside a tall 4:5 field plus five-label strip.
- WorkGraph: proposition beside a coded retained record; no hero bitmap.
- Build: proposition beside a five-row vertical Factory stage.
- Trust: full-width opening followed by a horizontal control band.
- Company: proposition, small end-aligned 5:2 seam, then ruled rows.

Any confused pair stops acceptance.

## Asset and render fidelity

- Home: rendered hero region against the frozen FS4 lossless baseline at all
  three sizes; at most 0.5% differing pixels and correct desktop/mobile
  `currentSrc`.
- Transformation: rendered 4:5 carrier against assigned
  `transformation-hero-decision-field-mobile-v2` at all sizes; no CSS crop or
  16:10 fallback.
- WorkGraph: Context carrier against desktop source at 1440/1024 and portrait
  source at 390. Position versus Context must prove the bitmap exists only in
  Context.
- Company: rendered seam against source scaled to `640×256`, `640×256` and
  `350×140`; end-aligned and uncropped.
- Build: Position stage against later Factory instrument; both coded, with the
  retired bitmap absent from DOM and network.
- Trust: opening control band against expanded OR-021; both Operational
  Evidence, never image-led product theatre.

## Whitespace and rhythm — 18 pairs

For every route and viewport pair first viewport with full-page capture.
Reject:

- an empty vertical run exceeding 60% of viewport height without a semantic
  object;
- a stranded rule, label or CTA;
- a proof carrier pushed into the next viewport;
- Paper functioning only as an oversized gutter;
- adjacent Ink sections reading as one continuous dashboard.

Authored negative space inside Home or Company imagery does not count as empty
page space when the causal event remains legible.

## Two-second route checks

| Route | Must register | Immediate reject |
|---|---|---|
| Home | imperfect sources → coral judgment → sage boundary → precise signal | either side cropped, desktop crop on mobile, or a second hero |
| Transformation | heterogeneous inputs → one judgment → three changed-work carriers → ownership boundary | Home silhouette, dashboard/process diagram, or displaced labels |
| WorkGraph | one retained record with identity, state, owner and permission; Context image resolves sources into a governed record | bitmap in Position, cropped coral/sage event, or Machine Signal |
| Build | approved intervention → specification/permission → evaluation → governed review/evidence | bitmap, terminal/code wall, or dashboard tiles |
| Trust | action withheld → permission → accountable owner → release remains withheld | hero sidecar, generic security checklist, or merged control/record surfaces |
| Company | three fragments → coral judgment → one aligned Paper path inside an open sage boundary, followed by accountability rows | decorative stripe/process diagram, second hero, or clipped first two rows |

