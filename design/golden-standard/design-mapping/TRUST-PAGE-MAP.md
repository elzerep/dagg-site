# Trust page map

Status: binding implementation authority for `/trust`, amended for FS5.

## Decision and argument

FS5 places a coded control-path band immediately after the opening. It shows,
without opening the full record: `Action withheld — Invoice and receipt
disagree.`, `Permission — The agent may prepare, never release.`, `Accountable
owner — Finance owner decides; the manual path remains available.` and the
resolved state `Human decision recorded. Release withheld.` The provenance is
`Constructed control path`. These are default copy, not hidden detail.

Trust explains a control model without turning architecture principles into
unsupported security assurances:

`approved context -> explicit permission -> material exception -> accountable owner -> inspectable record -> way back`

The copy authority is `FULL-SITE-CONTENT-CONTRACT.md`, Page 7.

## Visual hierarchy

Trust uses Operational Evidence only. Position is a copy-led full-width opening.
The control path is a separate, immediate horizontal band below it, not a hero
sidecar. The main proof is constructed record OR-021. It is labelled as a
constructed example and cannot be presented as client or production evidence.
Coral marks the material exception; sage marks permission, withheld release and
a stable way back.

## Motion

The control-path band performs one finite 1.5 second settle in semantic order
after the band enters view and then holds. It may not finish invisibly during
page load. It does not loop or imply system activity. No-JavaScript and reduced
motion render the final state immediately. The operating record itself is still.

## Composition and responsive contract

1. Position - copy-led full-width opening.
2. Immediate control-path band - three horizontal lines and the resolved state;
   stacked on narrow screens. The complete band carries `[data-trust-control]`
   exactly once for first-viewport measurement.
3. Permission - explanation plus five control fields.
4. Record - the exception conclusion is primary; one full-field Ink Operational Evidence object opens progressively on request.
5. Models - harness principle and explicit boundary.
6. Reversibility - diligence route and governed-build link.

At 939 px and below every section follows DOM order. When opened, the record
changes from two columns to one without omitting a field. At 320 px there is no
horizontal overflow, field labels sit above values and controls remain at least
44 px.

## Acceptance

- exactly one H1 and no heading skips;
- no security, residency or production-deployment claim without evidence;
- permission, stop condition, owner, evidence and way back are explicit text;
- OR-021 provenance is adjacent and visible;
- finite band motion starts on entry, resolves and reduced motion is immediate;
- 1440, 1180, 1024, 940, 939, 390 and 320 remain legible without overflow;
- technical diligence is a real mail action and Build is a real route.
