# Current xAI / SpaceXAI design and narrative audit

Audit date: 2026-08-30  
Source: current official `https://x.ai/` experience, which identifies the company as **SpaceXAI** in the captured state.  
Mode: read-only combined design, UX, responsive, motion and accessibility-risk audit.

## Audit scope

Pages captured and inspected:

1. [Homepage](https://x.ai/)
2. [Grok](https://x.ai/grok)
3. [Grok Build](https://x.ai/build)
4. [API](https://x.ai/api)
5. [Business](https://x.ai/grok/business)
6. Mobile homepage, Business, API and open navigation at a requested 390 x 844 viewport. The browser exposed 375 CSS pixels on the homepage and Business captures, so measurements below distinguish the requested viewport from the page client width.

The audit is based only on screenshots and DOM/computed-style evidence collected during this run. Forms and outbound CTAs were not submitted. Reduced-motion CSS was inspected, but the pages were not re-rendered under an emulated reduced-motion operating-system preference.

## Evidence set

### 1. Homepage hero and product matrix — healthy

![Homepage desktop hero](01-home-viewport.png)

The hero is one sentence, one supporting line, two actions, then immediate product proof. The headline is not made futuristic with imagery. A changing final word and a small three-second shimmer underline create controlled anticipation. The product matrix below makes breadth tangible before the page explains the API.

### 2. Homepage full narrative — healthy, but sparse on customer proof

![Homepage full page](02-home-full.png)

Narrative order:

1. New-model signal.
2. Stable platform proposition.
3. Self-serve and documentation actions.
4. Five live-looking product surfaces.
5. Unified API explanation.
6. Scale and infrastructure proof.
7. Fresh release/news cadence.
8. Self-serve versus supported buying choice.

The weakness is proof quality for an enterprise transformation buyer. `400M+`, `200K GPUs`, and fresh releases establish scale and velocity, but the audited homepage does not show client outcomes or implementation evidence.

### 3. Grok product page — healthy product explanation, weak differentiation for a strategic buyer

![Grok product hero](03-grok-viewport.png)

The broad promise is followed by a linear feature walk: Chat, Multi-agent, Search, Imagine, then additional capabilities, onboarding, and a bridge to API access. Each feature pairs short explanatory copy with a simulated product state.

The pattern is excellent for explaining one product. The phrase `useful for everyone` is intentionally broad and would be too generic for Dagg.

### 4. Grok Build — very strong productization

![Grok Build operational feature](19-build-feature.png)

Build is the strongest xAI reference for Dagg's Factory and human-control story. It does not describe abstract “agentic workflows.” It shows a working artifact: a plan, a status, an approval point and a terminal. The page's feature carrier contains five sequential capabilities — Skills, Plan, Plugins, Q&A and Subagents — in roughly 1,993 desktop pixels.

The pattern to translate is **claim beside inspectable work**, not the black terminal styling.

### 5. API page — excellent self-serve/enterprise ladder

![API desktop hero](08-api-viewport.png)

The API hero puts the proposition and production code at equal visual weight. The page then progresses from API key to pricing, playground, capability map, enterprise controls, console, buying choice, cloud availability, releases and FAQ. It is unusually complete without losing the primary action.

For Dagg, the equivalent is not code in the hero. It is a real WorkGraph-derived decision or operating record that an executive can understand without an engineer.

### 6. Business enterprise proof — strong product demonstrations, weak client outcome proof

![Business enterprise proof cards](16-business-features.png)

Three 390 x 480 pixel modules make the enterprise promise concrete:

- Data isolation is shown as a key inside a tenant grid.
- Connected knowledge is shown through recognizable tools.
- Production output is shown as a real spreadsheet surface.

![Business scroll-led workflow](17-business-connect-tools.png)

The use-case carrier advances down the page. Copy on the left and a stable application surface on the right change together. The active step is full contrast; adjacent steps fade. This is scroll-led explanation, not a slideshow.

![Business spreadsheet workflow](18-business-spreadsheet.png)

The strongest moment is familiar work changing in place. A spreadsheet does not become a sci-fi interface; values update, the state resolves, and the viewer understands the consequence.

### 7. Mobile behavior — structurally strong, with accessibility risks

![Homepage mobile](12-home-mobile-viewport.png)

At the sampled mobile breakpoint:

- Outer margin is 16 px and content width is 343 px.
- H1 becomes 36 px with about 38–40 px line height.
- Hero CTAs stack vertically.
- Product cards become a single 343 x 220 px column with 12 px gaps.
- Copy precedes product UI; the API's large desktop code visual is deferred below the first viewport.
- No horizontal overflow was present on the sampled homepage, Business or API pages.

![Mobile navigation open](21-mobile-menu-open.png)

The mobile navigation is a full-height sheet with four accordion groups, Pricing and News, and one fixed-priority action at the bottom. The 48 x 48 menu control is visually adequate, but the captured button had no accessible name in the DOM. Several Business mobile CTAs measured only 36 px high. Those are risks to avoid rather than patterns to copy.

## Measured design recipe

All values are direct measurements or bounded estimates from the captured state.

| Element | Desktop | Mobile |
|---|---:|---:|
| Browser/client width | 1,265 px content viewport inside 1,280 px browser | 375 px client width from requested 390 px viewport |
| Page outer margin | 24 px | 16 px |
| Full content width | about 1,217 px | 343 px |
| Homepage/Grok/Build H1 | 60 / 60 px, 500 weight | 36 / 37.8–39.6 px, 500 weight |
| Centered hero copy width | 672–768 px | 343 px |
| Business split hero | 568.5 px text + 80 px gap + 568.5 px product surface | stacked; product surface removed from first viewport |
| Global desktop header | about 64 px | about 80 px |
| Primary hero control height | 44 px | 44 px on homepage/API; some Business actions only 36 px |
| Homepage product cards | 3 x 397.7 px then 2 x 602.5 px; 280 px high | 343 x 220 px, one per row |
| Homepage card gap/radius | 12 px / 16 px | 12 px / 16 px |
| Business proof cards | 3 x 389.7 px; 480 px high | stacked |
| Business proof gap/radius | 24 px / 24 px | stacked with large vertical rhythm |
| Homepage length | 3,938 px | 6,992 px |
| Grok length | 4,461 px | not fully measured in this run |
| Build length | 4,693 px | not fully measured in this run |
| API length | 8,088 px | 12,551 px |
| Business length | 7,031 px | 11,037 px |

### Type

- Display: `universalSansDisplay`.
- Body/interface: `universalSans`.
- Large pages are entirely sans-serif. Hierarchy comes from scale, opacity and whitespace rather than contrasting type families.
- Dagg should translate the clarity, not the font system. Dagg's grotesk + editorial serif combination is better suited to “strategic judgment meets machine execution.”

### Palette and material

Observed core colors:

- Primary ink: approximately `#0A0A0A`.
- Page: `#FFFFFF`.
- Warm product-card surface: `#F9F8F6`.
- Hairline: `rgba(10,10,10,0.06)`.
- Secondary copy commonly uses 40–60% black.
- Micro-accent: orange around `#FF6308`, with occasional violet/blue in generated-image/API artwork.

There are almost no shadows. Separation is made with warm surface shifts, one-pixel borders, radius and whitespace.

For Dagg, retain the approved warm paper/ink/coral/sage system. xAI validates the principle that the accent should be small and semantic; it does not validate replacing Dagg's warmth with black, white and blue.

## Information architecture recipe

The global navigation is organized by buyer intent:

1. **Products** — Grok, Business, Government, Bot and downloads.
2. **Solutions** — use cases and functional/regulated contexts.
3. **Developer** — API, documentation and Build.
4. **Company** — company and infrastructure.
5. **Pricing** — commercial clarity.
6. **News** — proof of cadence.
7. Persistent enterprise action: **Contact Sales**.
8. Persistent self-serve action: **Try for free**.

This gives xAI two concurrent funnels: explore/build independently or talk to the company.

### Dagg translation

Use the same intent clarity with Dagg's actual operating model:

1. **WorkGraph** — how hidden work is mapped and decisions are made.
2. **Factory** — agents and custom software built from that map.
3. **Operations** — systems Dagg operates and governs for the customer.
4. **Impact** — evidence, operating records and client outcomes.
5. **Company** — point of view, partnership and people.
6. Persistent primary action: **Start an assessment**.

Do not add a generic `Solutions` mega-menu until there are enough distinct, evidence-backed solution pages. Do not place `AI-native` in the top navigation as a vague thought-leadership category; it belongs in the narrative and insight layer.

## Narrative recipe

xAI repeatedly uses the same sequence:

1. **One stable proposition.** Six to twelve words, no methodology preamble.
2. **One sentence of scope.** The modalities or work covered.
3. **Immediate action.** Product access plus a secondary learning/sales route.
4. **Inspectable product proof.** A UI state, code, data or artifact.
5. **Sequential capability walk.** Each step is short copy paired with a changing, stable product surface.
6. **Trust and scale.** Infrastructure, security, compliance or distribution.
7. **Commercial fork.** Self-serve versus support.
8. **Freshness.** Version badge, changelog or dated releases.

The Dagg equivalent should be:

1. Consequence-led hero about hidden work and the operating system that replaces it.
2. A single WorkGraph-derived decision field, not a network diagram.
3. The sequence **Map → Decide → Build → Govern → Operate** demonstrated inside one carrier.
4. One strategic thesis explaining what should *not* be automated.
5. Factory proof through a real agent/software artifact.
6. Operations proof through an exception, human decision and resulting system action.
7. Impact proof with a falsifiable outcome and evidence boundary.
8. Assessment as the conversion path.

## Productization and motion recipe

The site contains no video elements in the inspected pages. Energy comes from coded product simulations, canvases and small transitions:

- Homepage: 15 images and two canvases.
- Grok: four images and one canvas.
- Build: four images and one canvas.
- API: 11 images and two canvases.
- Business: four images and one canvas.

Observed timing:

- Hero underline shimmer: 3 seconds.
- Caret: 1 second, stepped, infinite.
- Thinking dots: 1.4 seconds.
- Document reveal: 0.4 seconds; state swap: 0.3 seconds after a 2.2-second delay.
- Spreadsheet/finance stories: 7–8 second loops.
- Most interface transitions: 150–500 ms.
- Reduced-motion CSS explicitly removes or resolves the principal tenant, spreadsheet, document, chat and finance animations to a static final state.

### Dagg translation

- Use **one stable carrier surface** per page. Copy changes; the surface persists.
- The homepage carrier should tell an 8–12 second operational story: hidden work appears, a decision is made, Factory produces a system, governance catches an exception, a human resolves it, and Operations proceeds.
- Motion must change meaning or state. No floating nodes, tracing lines, particle fields, circuit-board pulses or decorative parallax.
- Use 180–450 ms micro-transitions and 7–10 second inspectable loops.
- Pause or reduce nonessential motion off-screen.
- Reduced motion must show the resolved state and preserve every explanatory label.
- Keep the dark instrument localized. Surround it with Dagg's warm editorial field and abstract concept images.

## How xAI creates urgency without fearmongering

The site does not say “adopt AI or die.” It makes the future feel present through:

- A visible new-version badge.
- A working install command.
- Live-looking progress, cursors, plan approvals and state transitions.
- Present-tense words: `real-time`, `now`, `in seconds`, `ship`.
- A current release/news feed.
- Large-scale proof close to the product.
- Familiar work changing in place.

For Dagg, urgency should be produced by visible operational velocity:

- Show a decision becoming a running system, not a countdown clock.
- Show the cost of hidden work as a present operating constraint, not a catastrophe claim.
- Use release/operating evidence only when it is real: date, state, owner, exception and outcome.
- Let the reader infer speed from the mechanism and proof.
- Never use `10x/100x/1000x`, existential threats, generic `future is here`, or unverifiable transformation statistics as hero copy.

## Proof and conversion recipe

### What works

- Global actions stay visible at all times.
- Context-specific CTAs match the page: API key, Grok, install/docs, Business or sales.
- The API page repeats the action only after adding new decision information.
- Business pairs security signals with product behavior rather than isolating trust in a legal footer.
- The mobile menu makes one primary action unavoidable without crowding the top bar.

### What Dagg needs beyond xAI

xAI's audited pages are weak on customer cases and implementation outcomes. Dagg cannot rely on scale metrics or model breadth. Dagg needs:

- An anonymized but inspectable operating record.
- An impact study with baseline, intervention, observed result and what would invalidate the claim.
- A clear boundary between assessment, build and operated service.
- Evidence of human control, data isolation and governance at the moment those questions arise.
- A single primary conversion: `Start an assessment`, with `See how WorkGraph works` as the learning alternative.

## What Dagg should translate

1. Product proof immediately after the promise.
2. A dual executive/self-serve-style funnel translated into assessment versus method exploration.
3. One stable visual carrier whose state changes with the narrative.
4. Familiar artifacts — decisions, operating records, specs and systems — not abstract diagrams.
5. A visible cadence of change.
6. Warm near-white surfaces, hairlines and restrained radii.
7. Precise responsive reordering: copy and action first, artifact second.
8. Motion as state change.
9. Trust integrated into the product story.
10. A conversion fork only after enough evidence exists to make the choice.

## What Dagg should avoid

1. xAI's monochrome/cold palette as Dagg's identity.
2. Repeated black terminal panels.
3. A hero install command or engineering-first vocabulary.
4. Generic phrases such as `superpowers`, `AI for everyone` or `the future of work`.
5. Five or more equally weighted product tiles before the Dagg method is understood.
6. Very long pages by default; Business is about 11,037 px on mobile and API about 12,551 px.
7. Small 36 px mobile CTAs.
8. An unnamed mobile menu control.
9. Low-contrast gray as the primary body-copy treatment.
10. Infrastructure vanity metrics without customer consequence.

## Accessibility evidence and limits

Confirmed from the captured state:

- Sampled mobile pages reflowed without horizontal overflow.
- Main homepage/API hero controls measured 44 px high.
- The mobile menu control measured 48 x 48 px.
- Reduced-motion CSS exists and covers the principal looping product animations.

Risks:

- The mobile menu button had no accessible name in the captured DOM.
- Several Business mobile CTAs measured 36 px high.
- Much secondary copy uses roughly 40–60% black on white; exact WCAG contrast requires color-by-color testing.
- Scroll-faded inactive copy can become extremely low contrast.
- Full accessibility cannot be established from screenshots and DOM sampling alone; keyboard order, focus visibility, screen-reader announcements and actual reduced-motion rendering remain unverified.

## Bottom line for Dagg

Borrow xAI's **operational immediacy**, not its look. The Dagg golden-standard composition is:

- Anthropic for tactile abstract imagery and editorial warmth.
- McKinsey for conclusion-led structure and disciplined evidence.
- Palantir for the operating model, implementation credibility and trust.
- xAI/SpaceXAI for visible product states, release velocity and a future that is already functioning.

The xAI-specific rule is simple: **never draw “technology.” Show work changing state.**
