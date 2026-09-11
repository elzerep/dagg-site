# P4R7 — Homepage convergence

Status: **historical; superseded by P4R10 for Home direction and implementation**  
Publication status: local preview only  
Decision owner: Christian Perez  
Execution owners: Codex and Claude Code

> Do not implement this five-beat convergence. Christian subsequently required
> three genuinely different six-act Home directions. P4R10 and
> `HOME-NARRATIVE-FOUNDER-RESET.md` are the current gate and copy authority.

## 1. Why P4R6 is superseded

Christian's rendered review rejected A1/B1/C1 as a homepage gate. This is a
visible-quality failure even though the assembly and interaction checks passed.

Measured at the same 1280 × 720 browser viewport on 1 September 2026:

| Page | Height | Main words | Major sections |
|---|---:|---:|---:|
| Dagg A1 | 10.9 screens | 415 | 9 |
| Dagg B1 | 10.0 screens | 365 | 9 |
| Dagg C1 | 11.8 screens | 410 | 10 |
| Anthropic | 4.4 screens | 453* | 6 |
| xAI | 5.5 screens | 542* | 4 |
| OpenAI | 8.3 screens | 557* | content index |
| Palantir | 9.3 screens | 2,610* | cinematic/product index |

\* Peer word counts include navigation, release/news cards and footer content.
They are not copy targets. The relevant peer pattern is a sparse, headline-led
primary reading path with optional detail carried by product cards and onward
links.

P4R6 failed because it treated the nine-part site story as a requirement for
the Home page. It also repeated similar system panels across all three
directions. A1 has an additional visible defect: its full-page capture leaves a
large blank region after the hero because essential content is reveal-gated.

## 2. Chosen worldview

The convergence direction is **strategically led and product-proven**.

Keep:

> Build the company AI makes possible.

This is the strongest opening because it holds existing-company transformation
and new-company creation in the same sentence. `Build` is not a claim that Dagg
only starts companies; it states that Dagg makes the future operating model
real.

The technology must appear early. Dagg may not read as a strategy consultancy
with engineering added later, and may not read as a software vendor whose
product precedes the decision.

## 3. Binding Home story

Home has five beats. The footer is not a sixth narrative beat.

### Beat 1 — Position

**H1**  
Build the company AI makes possible.

**Lead**  
Dagg turns strategic direction into an AI-native operating model — then builds
the context, agents and software that make it work.

One primary action: `Start an assessment`. One quiet secondary action may point
to Transformation.

The hero uses Decision Field with restrained Machine Signal. It must suggest an
operating model resolving into executable structure, not show a generic folded
material, a dashboard, a terminal or a literal flowchart.

### Beat 2 — Stakes and transition

One conclusion-led sentence, not a full explanatory section:

> The gap between human-speed companies and AI-native companies compounds.

Its job is to make the transition consequential and lead into Dagg's mechanism.
It does not explain the whole AI-native thesis.

### Beat 3 — Dagg's technology

WorkGraph and Dagg Factory are named peer-level capabilities, not buried
implementation details.

**WorkGraph**  
Turns how the company works — its context, decisions, rules and boundaries —
into a retained record that agents and people can use.

**Dagg Factory**  
Turns strategic requirements and company context into governed agents and
software, with evaluation and human judgment built into the build.

Each gets one short value proposition, one visual state and one onward link.
This is the Home equivalent of a concise product index, not two mini product
pages.

### Beat 4 — One execution proof

Show one bounded transformation from company context to working system:

`strategic decision → retained context → governed build → verified state`

The proof may be interactive, but it has one start state, one meaningful
transition and one resolved state. It must not look like a terminal collection
or expose six simultaneous panels. This is a contained WorkGraph or Factory
instrument in Operational Evidence mode. One restrained Machine Signal makes
the state change legible and then stops. Decision Field does not enter this
proof section.

The proof is explicitly illustrative. It cannot imply a client deployment or a
measured outcome that Dagg cannot substantiate.

### Beat 5 — Onward choice

End with a compact route into:

- Transformation — decide what must change;
- WorkGraph — retain the company context;
- Build — turn the decision into agents and software;
- Impact — inspect named evidence when publishable;
- Start an assessment — begin with one material decision.

Do not restate the full site architecture in prose.

## 4. What moves off Home

| Material | Destination |
|---|---|
| Preserve / Simplify / Automate / Rebuild / Retire continuum | Transformation |
| Detailed AI-native operating-model thesis | Transformation |
| Source ingestion, retained records, RAG/graph architecture and boundaries | WorkGraph |
| Full Factory stages, ADRs, evaluation and agent/software pipeline | Build |
| Internal vs customer-facing surfaces and MCP explanation | Build or a later product proof |
| Evidence provenance, cases and truth boundaries | Impact |
| Ambition, company-building experience and people | Company |
| Detailed assessment deliverables | Assessment route |

Home may tease these ideas but may not teach all of them.

## 5. Composition contract

- Target total height at 1280 × 720: **4.5–6.0 screens including footer**.
- Target primary Home copy: **180–260 words excluding navigation and footer**.
- First screen: one H1, one lead, no more than two actions and no more than
  about 55 readable words.
- Technology is visibly named before the end of the second viewport.
- At most one dominant dark proof surface on Home.
- Home may use all three governed roles across the full page, but never all
  three in one section: Decision Field establishes the world; a contained
  Operational Evidence instrument proves the mechanism; one finite Machine
  Signal makes the consequence legible. The Home hero itself remains strictly
  Decision Field plus restrained Machine Signal.
- No nine-act template, repeated terminal panels or component catalogue.
- No required content may be hidden until scroll. A full-page screenshot taken
  without scripted scrolling must show the complete page.
- Large type and whitespace create hierarchy, but no empty viewport exists
  without a narrative or visual purpose.
- Every visual must perform the local narrative job defined by the Image
  Language System; library examples are direction, not a fixed set of assets.

## 6. Responsive and interaction contract

The same five-beat story must work at:

- desktop 1440 × 900 and 1280 × 720;
- iPad landscape 1024 × 768;
- iPad portrait 768 × 1024;
- mobile 390 × 844;
- small mobile 320 × 800.

Required:

- no horizontal overflow;
- no clipped or hidden essential copy;
- real mobile art direction for the hero and proof, not a desktop crop;
- menu, primary CTA and all onward links work;
- hover has an equivalent focus/tap state;
- motion explains state change and stops after resolution;
- reduced motion shows the resolved state immediately;
- zero console errors in tested states.

## 7. Collaboration and gate

Codex owns narrative hierarchy, peer comparison, acceptance and final visible
judgment. Claude Code independently pressure-tests the hierarchy and visual
execution. Both review the same rendered evidence. Neither may declare success
from source metrics alone.

The next Christian-facing gate is **one coherent A2 page**. At most two focused
hero alternatives may be shown if headline or first-screen composition remains
a genuine unresolved choice. Three more full homepages are prohibited unless a
future decision truly requires three different worldviews.
