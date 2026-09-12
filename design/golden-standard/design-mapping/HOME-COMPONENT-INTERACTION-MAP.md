# Home Component and Interaction Map

Status: **historical shared-behaviour reference; not the current Home structure**  
Route: `/`  
Narrative authority: `narrative/FULL-SITE-CONTENT-CONTRACT.md`  
Design authority: approved Foundations, Image Language and Component and Interaction Library  
Scope: the five accepted Home beats plus the global navigation behavior they inherit

> P4R10 controls the current six-act A/B/C founder gate. Reuse the accessible
> adaptive-navigation and fallback principles below only where P4R10 does not
> supersede them. Do not implement this file's five-beat composition or copy.

## 1. Decision

Home should feel intelligent because it responds precisely to intent, not
because every section moves. V1 uses only two enhanced behaviors:

1. one adaptive `Build` navigation preview;
2. one reader-controlled operating-record progression.

A finite hero before/resolved control is an approved later enhancement only if
independently art-directed unresolved desktop and mobile frames are produced.
Until then the hero is an honest resolved still; code may not simulate missing
semantic image states.

Everything else is editorial, visible and still. The interaction load therefore
follows the narrative load: orientation in the header, one causal resolution in
the opening and one inspectable proof in the body. There is no carousel, card
grid, terminal, dashboard, ambient loop or hover-only explanation.

The five-beat reading order is fixed:

1. Position;
2. Consequence;
3. Technology;
4. Execution proof;
5. Identity and next move.

Enhancement may change the amount of detail in view. It may not change this
hierarchy, the claims, the destinations or the accountable end state.

## 2. Calm-load composition

| Beat | Ground and composition | Image-language role | Enhanced behavior | Deliberately static |
|---|---|---|---|---|
| 1. Position | Paper; asymmetric 7/5 editorial hero | Decision Field as the world; the resolved composition already carries the outcome | Still in V1; conditional finite before/resolved control only after approved start frames exist | Eyebrow, H1, lead, actions and visual meaning |
| 2. Consequence | Paper; short punctuation block | None | None | Entire beat |
| 3. Technology | Lift; two-part editorial capability index, not cards | None; named products and one shared synthetic-data boundary carry meaning | Link response only | Both propositions, one shared disclosure and both destinations |
| 4. Execution proof | Paper; one contained ink instrument with a narrow state rail | Coded evidence pattern, not an Operational Evidence image-family asset; restrained Machine Signal may mark reader-selected progression | Three finite reader-selected progression markers; all state bodies remain visible | Record identity, state labels, permission, owner, evidence, way back and destinations |
| 5. Identity and next move | Lift; quiet 5/7 close | None | Link and button response only | Entire argument and next move |

This sequence uses three page-ground changes at most: Paper to Lift for
Technology, back to Paper for the proof, then Lift for the close. The dark proof
is a contained instrument, not a page ground. No two image-heavy acts are
adjacent. Home uses zero decorative or feature icons; only familiar utility
icons may explain navigation controls.

## 3. Global chrome — adaptive navigation that reveals intent

### 3.1 Topology

The header remains visually warm and typographically quiet. Its direct routes
are `Transformation`, `WorkGraph`, `Build`, conditional `Impact` and `Company`,
with persistent `Start an assessment`. `Impact` is omitted atomically until the
route is enabled. It never appears as a disabled or empty destination.

All top-level labels remain real links. `Build` alone earns a separate adjacent
disclosure button because it has four real depths. The button uses a neutral
library chevron and owns the open state; the word `Build` still navigates to the
Build overview. Ordinary Dagg routes do not open new tabs.

### 3.2 Build preview

The flyout is one stable outer panel, approximately 620–680 px wide on a desktop
fine-pointer layout. Four destination rows change one contained proof inset:

| Destination | Preview transition | Persistent conclusion or boundary |
|---|---|---|
| Build overview | Strategic decision → bounded build brief | `One operating decision becomes a buildable, governed system.` |
| Dagg Factory | Requirement → product decision → evaluation | Context and decision remain attached to the build |
| Agents and software | Agent around an existing system ↔ rebuilt workflow layer | The intervention follows the operating decision |
| Trust and operation | Proposed action → governed boundary → accountable human decision | Authority stops at the named boundary |

The inset is a preview of meaning, not a miniature application. It may use a
single ink surface, concise real labels and at most one or two semantic marks
only if ownership, boundary or evidence would otherwise be ambiguous. The outer
panel, header height, route order and assessment action never change when the
preview state changes.

### 3.3 Input and capability behavior

| Mode | Contract |
|---|---|
| Desktop, fine pointer | Open after 70–100 ms of intent. Keep trigger-to-panel travel inside a forgiving corridor. Close 180–240 ms after leaving both trigger and panel. Row emphasis responds in about 120 ms; content crossfades in 100–140 ms; the inset may morph in 180–240 ms without overshoot, reflow or outer-panel jump. |
| Keyboard | The separate disclosure button opens with Enter or Space. Normal Tab order reaches every real destination and produces the same four preview states as pointer focus. Escape closes and restores focus to the disclosure button. Hidden states are not focusable. Ordinary site navigation uses disclosure semantics, never `menu` or `menubar`. |
| iPad landscape or hybrid pointer/touch | Pointer may use the bounded flyout; touch opens the same four destinations as one-at-a-time disclosures. Capability detection, not width alone, chooses the behavior. |
| iPad portrait | Use the touch-first reading sheet. Build expands in place to the four destinations and one selected proof at a time. |
| Mobile and coarse pointer | Open a full-canvas reading sheet. Rows are 52–56 px; open and close targets are at least 48 × 48 px. The page beneath is inert, focus stays in the sheet, backdrop and Escape close it, and focus returns to the opener. The assessment action remains reachable after the final route. |
| Reduced motion | Remove position, scale and panel-size morph. Swap to the same selected proof state immediately, with at most a brief opacity change. |
| No JavaScript | Preserve every top-level link and all four Build destinations through native disclosure or a complete sitemap reading path. Remove inert enhancement controls. |

Hover never carries a destination, claim or instruction that is unavailable by
keyboard and touch.

## 4. Beat 1 — Position

### Component

`StrategicEditorialHero`: one large image-led field. The copy occupies the
authored quiet upper-left paper while the full source-to-judgment-to-governed
event spans the lower field. This is not a 7/5 split and the image is not a
rounded five-column illustration. Use the exact frozen Home pair from
`slot-manifests/home.json`:
`image-system/home/home-hero-decision-machine-desktop-v2.webp` and
`image-system/home/home-hero-decision-machine-mobile-v2.webp`, through one
responsive picture source. The mobile image is independently authored.

The resolved image must preserve imperfect context, the coral act of judgment
and the sage governed boundary. A start frame may simplify the same approved
scene, but it may not introduce a second motif or a new visual direction.

### Fixed narrative content

- Eyebrow: `AI-native transformation`
- H1: `Build the company AI makes possible.`
- Lead: `Dagg redesigns how existing companies work for an AI-native world and helps new companies begin that way. We map the operating reality, decide what should remain human, what can be automated and what must be rebuilt, then turn that direction into agents or software.`
- Primary action: `Start an assessment` → `/assessment`
- Secondary action: `See what must change` → `/transformation`

These elements remain visible and in this order. The hero uses zero icons.

### Interaction

V1 has no semantic hero control: it presents the approved resolved still. On
first load the field may settle once from 1.035 scale and 10 px displacement to
its authored position over 1.1-1.6 seconds, then hold. This is editorial
arrival, not an operating-state claim. There is no hover, scroll or looping
image motion.

If independently art-directed unresolved desktop and mobile frames are later
approved, the visual may offer two explicitly named states: `Operating reality`
and `Executable state`. That future pressed-state control changes only the
visual state; it does not replace the H1, lead, actions or disclosure. The
coarse-to-resolved Machine Signal transition runs once in 0.8–1.0 seconds and
then stops. Focus is visible, targets are at least 44 px on desktop and 48 px on
touch, and the selected state is programmatically exposed. Reduced motion swaps
immediately. Without JavaScript the resolved thesis image remains visible and
enhanced controls disappear.

### Responsive composition

At 1440 and 1280 px, keep copy and the full image event simultaneously legible.
At iPad landscape, preserve the full event without reducing the copy measure.
At iPad portrait and 390/360/320 px,
recompose in this order: eyebrow, H1, lead, actions, 4:5 visual, then the
conditional future state control if approved frames exist. Do not
shrink desktop type or allow the H1 to become a narrow stack beside the image.

## 5. Beat 2 — Consequence

### Component

`PunctuationBlock`: one editorial conclusion followed by one short explanatory
paragraph. It spans enough columns to feel institution-level but keeps a
60–620 px readable measure. No image, icon, metric, ticker or animated accent is
added to make the space feel occupied.

### Fixed narrative content

- H2: `AI-native changes who executes - and who decides.`
- Body 1: `An AI-native company is not the same company with more AI tools. People set direction, requirements and boundaries; agents and software carry more of the continuous execution. As AI capability advances, the gap compounds between companies limited by human-speed handoffs and companies designed to operate at machine speed.`
- Body 2: `We follow work across people, systems, documents, decisions and exceptions, including the handoffs that formal processes miss. Each path is tested against five outcomes: preserve, simplify, automate, rebuild or retire. Building is one possible result, never the premise.`

### Interaction

None. The beat is the page's visual breath and strategic consequence. It does
not reveal word-by-word, pin to scroll or animate into view. Hover, focus,
reduced motion and no-JavaScript all present the same complete reading state.

On mobile the headline may use the full content field; the body follows beneath
it rather than becoming a side column. Section spacing, not a divider card,
creates the pause.

## 6. Beat 3 — Technology

### Component

`PairedCapabilityIndex`: one shared eyebrow and H2 followed by two editorial
capability entries. This is not a feature-card row. WorkGraph appears first as
the retained context layer; Dagg Factory follows as the mechanism that can turn
an approved intervention and retained context into a governed build. The Home
artifact itself remains pre-decision: it shows what is known and what still has
to be decided, so Beat 4 retains the causal resolution. A fine rule, shared
baseline or directional type cue may show that the same record carries through
both entries, but it may not become a flowchart.

### Fixed narrative content

- Eyebrow: `WorkGraph + Dagg Factory`
- H2: `Strategy and execution share the same company context.`
- Intro: `Strategy often loses meaning when handed to engineering. Dagg keeps the decision, evidence, owner and boundaries connected to what gets built.`
- Shared identity: `WG-041 - Company-specific record`; `One operating decision, carried from strategy into build.`
- Shared disclosure: `Illustrative system record; not client work or a production deployment.`
- WorkGraph: `WorkGraph retains how work happens and should change: workflows, evidence, decisions, owners and boundaries. That context remains usable through transformation, Dagg Factory and operations.`
- WorkGraph fields: `Evidence - Cross-system handoffs`; `Owner - Service owner`; `Boundary - Material judgment remains human`.
- WorkGraph link: `See how company context is retained` → `/workgraph#record`
- Dagg Factory: `Once a change is approved, Dagg Factory carries its context through design, architecture, build and evaluation. It produces the justified agent, automation or software with permissions, human judgment and a way back defined before release.`
- Dagg Factory fields: `Input - WG-041`; `Evaluation - Basis visible before action`; `Permission - Service-owner approval required`.
- Factory link: `See how context becomes a build` → `/build#factory`

Both propositions, the one shared disclosure and both links are always visible.
The disclosure uses the metadata type role; it is not reduced to an icon or
tooltip.

### Interaction

There is no tab switch, hover reveal or embedded mechanism here. Pointer and
focus may move a short link rule or directional cue in the 120–180 ms micro
range. That response confirms action but reveals no new meaning. The section is
identical under reduced motion and no JavaScript.

Desktop may use a restrained two-part split within one shared field. At iPad
portrait and mobile, preserve the semantic order WorkGraph → Factory and stack
the entries with one clear spacing interval. Do not horizontally scroll or
compress the two entries into cards.

## 7. Beat 4 — Execution proof

### Component

`PersistentOperatingRecord`: Home's only dominant proof instrument. One stable
contained ink carrier holds the proof title and record identity `WG-041`. A
narrow rail marks four ordered states while all four remain readable in the
default path. The carrier may not multiply into cards, terminal panes,
dashboard widgets or a node graph.

This is an inspectable coded product artifact, not an Operational Evidence
image-family asset. It does not add a third generated image grammar to Home.

All four states remain legible in the default reading path. Enhanced controls
may mark progression but may not hide what began, what changed, who decided,
what evidence returned or whether a way back exists.

### Fixed narrative states

1. `Operating reality` — `The request crosses systems and specialist judgment.`
2. `Decision retained` — `The evidence, boundary and accountable owner stay together.`
3. `Governed execution` — `Agents prepare a permitted action; material uncertainty stays with the service owner.`
4. `Evidence returns` — `The owner decides; evidence returns and the previous path remains available.`

Persistent links:

- `Inspect the control model` → `/trust#permission`
- `Inspect the evidence standard` → `/impact#evidence-chain`, omitted atomically until Impact is enabled

### Interaction

The four selectors are a pressed-button group for four temporal states of one
record, not navigation tabs. Each selection changes one coherent state object:
context and proposed action, permission and accountable owner, evidence and way
back. The outer carrier, title, `WG-041` and destinations do not
move. The selected state is exposed programmatically; user-triggered changes may
be announced politely without replaying the entire record.

A state change keeps the outer geometry stable; no column grows and no state
copy disappears. On eligible desktop the four phases may advance once after
the carrier has remained 60% visible for 800 ms, then stop on `Evidence
returns`. It never loops. Pointer presence, focus, document visibility and
explicit pause stop the sequence; a direct state choice cancels automatic
ownership. Run, pause and replay controls remain available. Mobile, tablet and
reduced-motion paths are manual-only. There is no synthetic terminal typing or
scroll-driven progression.

Current-state emphasis is neutral Paper on Ink. Coral is reserved for
`Decision retained`, where accountable human judgment enters the record. Sage
is reserved for `Evidence returns`, where the governed result is stable. The
preview may not turn every traversed phase coral as a generic progress color.

With reduced motion, selection swaps immediately to the complete same state.
Without JavaScript, all four states render as one ordered record and enhanced
selectors disappear. No critical meaning depends on color: labels, selected
state, owner, withheld action, returned evidence and previous operating path remain
textually explicit.

### Responsive composition

At desktop and iPad landscape with sufficient width, use one stable 2 x 2
four-state grid. At iPad portrait and mobile, place the four selectors above the ordered bodies; targets are at
least 48 px and every state fits without horizontal scrolling. The record
identity precedes the controls. Do not squeeze the rail beside the proof at
390/360/320 px.

## 8. Beat 5 — Identity and next move

### Component

`EditorialAssessmentClose`: a quiet 5/7 close on Lift. The H2 and body form the
argument; the action group supplies one primary assessment button and one clear
Transformation link. It is not a conversion card, founder profile, logo wall or second
dark finale.

### Fixed narrative content

- H2: `Each operating decision makes the next one stronger.`
- Body 1: `Because context survives, transformation does not restart with every project. New evidence sharpens the next decision; reusable tools and evaluation improve the next justified build.`
- Body 2: `Dagg combines strategic judgment, company-building and engineering in one engagement. An assessment follows one material path to a clear decision and accountable next move. We build only when that decision justifies it.`
- Primary action: `Start an assessment` → `/assessment`
- Text link: `See what should change first` → `/transformation`

### Interaction

Only standard action feedback is allowed: visible hover, focus and active states
within the 120–180 ms micro range. No form, modal, reveal, count-up, animated
background or image is introduced on Home. Reduced motion and no-JavaScript
retain the same actions and destinations.

On mobile the complete argument precedes both actions. The primary action may
span the content width, but it must not become sticky or obscure the company
link.

## 9. State and meaning rules

| Element | Rest | Hover | Focus | Selected/open | Reduced motion | No JavaScript |
|---|---|---|---|---|---|---|
| Build disclosure | Direct Build link plus closed chevron button | Intent delay, then one stable panel | Equivalent panel and preview states | Four real routes; one proof inset | Immediate proof swap | All routes in native disclosure or sitemap |
| Hero visual | Approved resolved still; no V1 control | No state change | Conditional future control only | Conditional finite resolution after approved start frames exist | Resolved still | Resolved still plus complete caption |
| Technology entries | Complete propositions and one shared disclosure | Link cue only | Visible link focus | Real route navigation | Same | Same |
| Operating record | Persistent title, ID and all four ordered state bodies | No state change | Visible ring on progression controls | Progress marker changes; no state body is hidden | Immediate marker change | All four states in order |
| Close | Complete argument and actions | Action response only | Visible action focus | Real route navigation | Same | Same |

The following facts may never become transient or hover-only:

- the five-beat narrative order;
- the exact H1, lead, H2s, propositions and close;
- the one shared constructed-example boundary;
- `WG-041` and `Complex customer request`;
- the permission stop, accountable owner, returned evidence and previous operating path;
- every real destination and conditional Impact rule;
- the assessment action;
- the header height and outer flyout geometry while open;
- the hero's unresolved-to-resolved meaning.

## 10. Responsive truth table

| Verification width | Navigation mode | Hero | Technology | Execution proof |
|---|---|---|---|---|
| 1440 / 1280 | Full navigation; pointer and keyboard flyout | 7/5 | Two-part editorial field | Narrow rail + stable carrier |
| 1366 / 1180 / 1024 landscape | Full or compact navigation; bounded flyout for fine pointer, touch disclosure for coarse pointer | Split while both measures remain useful | Two-part or roomy stacked field | Rail + carrier where width permits |
| 1024 / 820 / 768 portrait | Touch-first reading sheet | Authored editorial reflow | WorkGraph then Factory | Controls above carrier |
| 390 / 360 / 320 | Full-canvas navigation | Copy and actions, then art-directed 4:5 visual | Stacked, no cards | Identity, controls and all states; no horizontal overflow |

Breakpoint choice does not override pointer capability. Reading order, route
availability and accountable meaning remain identical in every mode. Body copy
stays at least 17 px, focus rings are 2 px, minimum targets are 44 px and mobile
navigation/state targets are 48 px or larger. The 1240 px field, 12-column grid
and 940 px collapse remain the shared substrate.

## 11. Implementation boundary

This map does not prescribe code, but the implementation must preserve the
accepted progressive-enhancement architecture:

- all Home copy, the shared disclosure, artifacts and destinations are server-readable;
- client behavior is limited to the adaptive navigation and an optional
  operating-record progression marker;
- simple hover and focus feedback remains CSS-level behavior;
- no generic component kit, whole-page client boundary or remote media is
  introduced;
- initial client JavaScript, navigation JavaScript, CSS and font budgets from
  the frontend interaction stack remain hard gates;
- `prefers-reduced-motion`, 200% zoom, keyboard-only, touch-only and
  JavaScript-disabled paths are separate acceptance proofs.

## 12. Acceptance tests

Home is ready to implement only if all of the following can be verified:

1. The five beats render in the exact accepted order with no duplicate summary
   section or missing proposition.
2. Default-visible Home copy remains within the content contract's current
   420–520-word range, progressive copy within 100 words and the Position block
   within 55–90 words. The exact baseline is measured from the rendered route.
3. The hero uses the approved desktop and independent mobile sources; the
   browser loads only the appropriate source. It uses zero icons.
4. The V1 hero is the approved resolved still with one finite material-settle
   arrival, no control, loop or scroll dependency.
5. The header exposes every enabled route as a real link. `Build` has a separate
   disclosure button, four meaningful preview states and a stable outer panel.
6. Pointer, keyboard and touch reach equivalent Build destinations and proof
   states. Escape restores focus; mobile focus is contained; no hidden state is
   focusable.
7. Technology remains an editorial two-part index, not a card grid or hidden
   tab system. Both propositions and the one shared disclosure remain visible.
8. The operating record preserves `WG-041`, four named default-visible states,
   permission, owner, evidence and way back. A progression marker may cause one
   focal change without hiding copy or causing a layout jump.
9. JavaScript-disabled Home retains the complete ordered argument and every real
   destination; inert controls are absent.
10. Reduced motion resolves to the same semantic states immediately. No meaning
    is communicated by motion or color alone.
11. Desktop, iPad landscape, iPad portrait and 390/360/320 mobile pass without
    horizontal overflow, mechanical desktop stacking, clipped focus or text
    smaller than the accepted minimums.
12. Home contains at most one dominant dark instrument, at most three page-ground
    changes, no adjacent image-heavy acts, no remote media and no terminal,
    dashboard, circuit or generic-AI spectacle.
13. The conditional Impact route, navigation item and Home evidence link appear
    or disappear as one atomic state.

## 13. Authority used

- `narrative/FULL-SITE-CONTENT-CONTRACT.md`
- `authority/Dagg-Component-and-Interaction-Library.pdf`
- `authority/Dagg-Design-System-Foundations.pdf`
- `packages/P4R5-COMPONENT-INTERACTION-SPECIMEN.md`
- `packages/P4R5B-COMPONENT-INTELLIGENCE-REVISION.md`
- `reference-audits/xai-current/XAI-CURRENT-AUDIT.md`
- `reference-audits/FRONTEND-INTERACTION-STACK.md`

The xAI audit informs operational immediacy, stable state carriers and adaptive
navigation quality. It does not authorize terminal density, repeated dark
panels, engineering-first vocabulary or interaction for its own sake.
