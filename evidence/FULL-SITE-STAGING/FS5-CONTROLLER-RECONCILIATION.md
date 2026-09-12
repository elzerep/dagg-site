# FS5 controller reconciliation

Date: 3 September 2026

## Decisions after Lane A and Lane B

### R5 — Company opening

Lane A proved that the previous first-viewport rule was internally impossible
at 390×844 without shrinking exact copy or the registered 5:2 seam. The rule is
now breakpoint-specific:

- 1440×900: 640×256 seam and the Decision and Build rows fully in view.
- 1024×768: the seam fills the responsive seven-column carrier at intrinsic
  5:2, capped at 640 px and never cropped; Decision and Build remain fully in
  view.
- 390×844: 350×140 seam; the accountability chain and at least the first 44 px
  of the Decision row begin in view. The remaining rows continue in DOM order.

This keeps the proposition readable, the image subordinate and the mobile
composition honest. It does not hide copy, reduce type, crop the image or use
CSS reordering. The Company map, Fable plan, Lane A package, runner contract
and route CSS were amended together.

### WorkGraph route root

The binding WorkGraph map requires one `<main>` carrying both
`data-workgraph` and `data-workgraph-page`. The route meta now emits both hooks
and the duplicate wrapper hook is removed. This resolves the sole Lane B
deviation without changing copy, order or behavior.

## Status

Source reconciliation only. The assembled output and all visual, responsive,
motion, reduced-motion, no-JavaScript, navigation and CTA claims remain
unproven until the immutable FS5 browser run.

Post-amendment authority hashes:

- Fable plan: `84a8014ed3fbc1e4e9744932024bf9c08f5ebff6533f81fef945e533ab0b62bb`
- Copy-unit manifest: `a7d8b0baabdda5a1807a74f1ea3c73c50ad5342bdd39bcee4bfaddec5a80d801`
- Content contract (unchanged): `c7068104a28fa6a2e6f104daecbdec8410ec5c719fcf00f55f47432ed03a07dc`

The pure FS5 contract suite passes 37 tests with ten evidence-package tests
correctly skipped before assembly.
