# P4R6 resolved Home directions — browser QA

Date: 2026-09-01  
Browser: Codex in-app Browser  
Routes: A1, B1 and C1  
Publication status: local preview only

## Verdict — superseded

**This eligibility verdict was invalidated by Christian's rendered review on
1 September 2026.** The machine and interaction results below remain historical
evidence; they did not protect against the visible failure. The three resolved
directions are not eligible for Christian's worldview choice.

The original verdict was:

The three resolved directions were considered eligible for Christian's worldview choice.
They are complete nine-act homepage slices with different hierarchy, copy,
imagery and interaction emphasis, not three cosmetic reskins. No direction has
been promoted to production and nothing has been published.

## Binding source and assembly gates

- `node tools/check_p4r6_sources.mjs --resolved`: PASS, three of three routes.
- Visible copy budgets: A1 498 words, B1 376 words, C1 466 words.
- Required act order: hero, stakes, transformation, WorkGraph, Factory,
  surfaces, operate/trust, Impact and assessment.
- `node tools/build_golden_standard_previews.mjs`: PASS.
- `node tools/build_golden_standard_previews.mjs --check`: PASS; all twelve
  outputs byte-identical to a fresh assembly.
- Shared hashes, local references, no inline vector markup, no text-symbol
  icons, complete no-JS markup and shared-DOM ownership all pass.

## Responsive render matrix

Each route was driven and measured at:

- desktop 1440 × 900;
- iPad landscape 1024 × 768;
- iPad portrait 768 × 1024;
- mobile 390 × 844;
- small mobile 320 × 800.

Across all fifteen route/viewport combinations:

- no horizontal overflow;
- zero broken images;
- the correct 1586 × 992 desktop or 1122 × 1402 mobile hero source loaded;
- H1 and lead remained legible without clipping;
- no visible text rendered below 11 px;
- no visible interactive target rendered below 24 px.

The captured desktop, iPad, mobile and full-page states are stored beside this
file. `peer-comparison.html` and `peer-comparison.png` place the current peer
captures and A1/B1/C1 in the same first-screen comparison. The comparison
confirms that the Dagg directions carry peer-level first-screen restraint,
hierarchy and visual authority while remaining recognisably Dagg.

## Interaction proof

### Shared chrome

- Desktop Build opens after hover intent.
- Hovering `Agents and software` changes both selected destination and proof
  inset to `agents`.
- Escape closes the flyout and restores `aria-expanded="false"`.
- Mobile Menu opens as a full disclosure, locks underlying page scrolling,
  and Escape closes it and restores focus to the Menu summary.
- Browser console: no warnings or errors in the inspected states.

### A1

- Selecting `Retire` checks the retained decision and resolves to `Stop work
  that changes nothing.`
- `At the customer edge` becomes the active surface and hides the internal
  surface.
- `Inspect the governed exception` opens the accountability detail.
- Hero CTA lands on the assessment H1 `Start with one material decision.`

### B1

- Selecting `Retire` changes both the decision output and the same Factory
  plan to `Archive the requirement.`
- `Customer surface` becomes the active surface.
- `Governed exception` becomes the only visible exception state.
- Hero CTA lands on the shared assessment route and expected H1.

### C1

- Decision continuum is operable through its labelled stations.
- Selecting the `Documents` source tab makes only the Documents panel visible.
- `At the customer surface` becomes the active surface.
- `Show material exception` changes the state to `exception`, reports
  `aria-pressed="true"` and changes its return label.
- Hero CTA lands on the shared assessment route and expected H1.

## Reduced motion and native disclosure limitation

The shared chrome, component library and direction-local CSS/JS all include
`prefers-reduced-motion` branches. In reduced motion, scrolling becomes
immediate, transitions snap and the finite Machine Signal resolves without
ambient motion. The in-app Browser does not expose OS media-feature emulation,
so an OS-level reduced-motion smoke test remains a pre-publication check.

The in-app Browser keyboard adapter did not execute the browser's native
Enter/Space default for any tested `<summary>`, including the unrelated native
A1 exception disclosure. Click, Escape and focus restoration work. Because the
failure is common to native summaries rather than specific to the Dagg Menu,
physical-device Enter/Space remains a pre-publication smoke test rather than an
A/B/C-direction blocker.

## Captured evidence hashes

```text
da1bb5c46433748ea91a5d4ee33b7779167477c04656e28df317cb9beb816c39  a1-desktop-1440x900.png
b9f23d6a96643b9c75975c95839435033a96c917d3242351a11ead36233bb04e  a1-ipad-768x1024.png
1f4b99b7d9d7742ee292207718b678acf1769d58846fd477fed10ac70bb82032  a1-mobile-390x844.png
2757f7f4944c02235642f6f24fdb05f2d717eedd11a6221ef441eb0508759da9  b1-desktop-1440x900.png
75f76895728e4ec05d9e355de82adf06cbc93ae8e7c119bac9fa8ec0d5a6913c  b1-ipad-768x1024.png
670b5306dc0810bfa4dbd64c5a559b26983b9bdb5950efc88015f678c942a191  b1-mobile-390x844.png
265f819097e69b18ba5fec7095ac47719c03fea5dd927f0fe5c4a7baf842f144  c1-desktop-1440x900.png
63e5d586edbdd119ff9396028026e4c58af20f3294da18beba8ff8355fb401bd  c1-ipad-768x1024.png
8ea41ae19b2fbc39c9137566125f19010ba7ad24b431f389009d4e5d1fd0b064  c1-mobile-390x844.png
a4744b6184f60c36a1160b5d378675090cd9b1181d84507c177d9d8f40b20850  peer-comparison.png
```
