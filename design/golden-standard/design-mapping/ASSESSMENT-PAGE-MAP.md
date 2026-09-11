# Assessment page map

Status: binding implementation authority for `/assessment`, amended for FS5 evidence hooks.

## Decision and argument

The route converts interest into one bounded first engagement:

`one material path -> evidence -> operating map -> decision or refusal -> accountable next move`

The copy authority is `FULL-SITE-CONTENT-CONTRACT.md`, Page 8.

## Visual hierarchy

Assessment is evidence-led. The hero uses one large coded scope object, not a
decorative dashboard: one path, evidence, decision, boundary and accountable
next move. The Decision Pack is a single Ink Operational Evidence field. No
generated client interface, chat shell, terminal, metric tile or fake result.

## Interaction

The inquiry form validates every required field, focuses the first error,
announces validation, and reveals an explicitly labelled local-preview state.
The preview deliberately does not transmit data or claim receipt; a real
endpoint, privacy copy and error response remain publication requirements. No
confidential information is requested. Without JavaScript the inert form stays
hidden while all explanatory content and the direct email path remain readable.
The transient local state is exactly `Checking the path locally…`; it must not
say `Sending`. Every visible node receives a `data-copy-scope` hook owned by
Codex so the FS5 runner can distinguish default, progressive and system copy.

## Composition

1. Position - 5/7 copy and one large scope object.
2. Fit - good/not-a-fit editorial comparison.
3. Process - five stages in one sequence, not five cards.
4. Deliverable - one coherent Decision Pack field.
5. Inquiry - explanatory copy beside the form and explicit local state.

At 939 px and below every section follows DOM order. At 320 px fields are one
column, labels remain above controls, touch targets are at least 48 px and no
horizontal overflow is allowed.

## Required semantic and test hooks

- The single route root carries `[data-assessment]`.
- The opening H1 and lead retain `.assessment-h1` and `.assessment-lead`.
- The `Send one path for review` action carries
  `[data-assessment-primary-action]`.
- The opening scope object retains `.assessment-hero__scope`.
- The submit button and polite live region carry the exact manifest-backed
  `data-copy-state` value for `idle`, each validation state, `submitting`,
  `duplicate` and `error`.

## Publication blockers

- connect a reviewed form endpoint;
- replace preview success/error behavior with backend truth;
- approve Privacy text and legal link;
- verify spam protection, retention and access controls;
- retain Christian's explicit publication gate.
