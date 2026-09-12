# Dagg website — the plan from today's candidate to golden standard

**Author:** Claude Fable 5.1 (`claude-fable-5-1`), independent failure-first review under FS4B · **Date:** 2 September 2026
**Candidate reviewed:** immutable snapshot `6ef754faf00f234ba503ddbc83e8226759054a4b57929b9757561b3a6fdfdc50`, commit `f688c54`, served on `127.0.0.1:8933`. All 136 candidate files served are byte-identical to disk; the assembler check passes; the candidate did not change during review.
**Mode:** read-only. No source, asset, evidence or authority file was changed. Nothing here approves implementation. On approval the only write is a copy of this document to `evidence/FULL-SITE-STAGING/FS4B/FABLE-5.1-FULL-SITE-REVIEW-2026-09-02.md`.

**Contents.** 0 Ten-minute read · 1 Where the site is · 2 What 10/10 means, headline-only story · 3 Methods · 4 Protected decisions · 5 Design system by viewport and the global component table · 6 Scored peer comparison · 7 Credibility architecture per route · 8 Execution plan and package checklists · 9 Section-by-section specification for every route · 10 Gate matrix · 11 Launch blockers versus publication · 12 Decision log and activation verdict · 13 Risk register · Appendices A–D.

---

## 0. Ten-minute read

**Where the site is.** One coherent, warm, disciplined system with a founder-grade Home hero, contract-exact copy, working adaptive navigation and three genuine coded proofs. Not yet a release candidate: three P1 defects (one evidence-integrity, two truth-boundary) and one structural gap — execution is described more than witnessed, and five routes open with the same silhouette.

**Verdict on the current candidate:** REJECT as release candidate · ACCEPT-WITH-CHANGES on direction. Nothing in this plan reopens the brand, the selected Home hero, the six-act narrative or navigation.

**What golden means.** Eleven dimensions with measurable pass conditions on one immutable snapshot (§2). Estimated today 7.4/10 average with three dimensions below 7; target ≥9 on every dimension, no P0/P1/visible P2.

**How we get there.** Five steps, one writer, one assembler, no shared files (§8). Codex closes ten decisions and amends the authorities; Claude writes six routes to a section-by-section specification (§9); Codex assembles once, freezes one snapshot and runs a fail-closed evidence rig (§10); Fable accepts independently; publication work is separated (§11).

**Activation and gates (§12).** The ten open items are resolved defaults, R1–R10, owned and recorded by Codex. FS5 is activated for one bounded writer as soon as Codex records R1–R10 in the FS5 text and reconciles the authority files (content contract, Home founder reset, page maps) to §9. Founder gates are only a materially different design-world direction and final launch, publish or canonical promotion; everything else is Codex operating acceptance. No publish, deploy or canonical promotion happens without Christian's explicit launch approval.

**Time.** Immediate FS5 repair to a founder-reviewable candidate: 2–4 working days, with the evidence runner built in parallel from day one. Launch readiness is dependency-led (approved legal text, a real form endpoint, canonical routing, verified titles) and is not part of the immediate repair; no launch date is promised.

---

## 1. Where the site is today

### 1.1 What is already right

- One system: Paper world, contained ink instruments, coral only at judgment, sage only at boundary; Geist/Newsreader/JetBrains Mono roles hold; icons limited to chevrons and menu/close.
- Home hero preserves the founder reference's causal structure (torn operating material → one coral plane → sage boundary → coherent machine signal). At 1515 px the serif H1 is 92 px on two lines, the lead four lines, both actions single-line, the image band 413 px.
- Copy matches `FULL-SITE-CONTENT-CONTRACT.md` and `HOME-NARRATIVE-FOUNDER-RESET.md` on every route; the only non-contract public copy is the Trust hero instrument. No superlative, multiplier, headcount or "proprietary" anywhere.
- Shared chrome: keyboard path to the Build flyout, inset switching on focus, Escape with focus restore, closed-panel links unfocusable — verified live. Mobile sheet: `aria-expanded`, inert background, scroll lock, 48 px reveal controls, per-destination preview — verified live at 527 px.
- Coded proof: WorkGraph WG-034 record with sticky lifecycle carrier; Factory pass (idle → running within 2 s → `Governed review complete` at ≈6.3 s with two holds, Pause/Replay, reduced-motion Inspect) — verified live.
- Assessment: form appears only with JavaScript, validates all five fields, focuses the first error, announces the message, sends no request — verified live. Confirmation copy truthful.
- Zero console errors on all eight routes; no horizontal overflow at any measured width; every link and anchor resolves; Impact absent from navigation and footer while gated.
- Architecture: deterministic assembler, immutable snapshot server with revision meta, semantic HTML first, small deferred scripts. The right stack; no framework change recommended.

### 1.2 P1 — blocks founder review

| # | Defect | Location | Evidence | Repair owner |
|---|---|---|---|---|
| P1-1 | The evidence set does not prove the candidate. All 25 full-page captures under `evidence/FULL-SITE-STAGING/FS4B/rendered/` were written 15:17–15:33; repairs to Home (16:03), Transformation (16:00), Company body and v2 hero (16:08–16:09) and shared chrome (15:58) came later; the snapshot froze at 16:11:44. Company captures still show the rejected v1 hero. No capture carries a snapshot ID. Current captures are 22 first viewports only. FS4 §9's `FS4-VISUAL-QA.md`, `FS4-ACCESSIBILITY-RESILIENCE.md`, `FS4-PERFORMANCE.json` do not exist. | `evidence/FULL-SITE-STAGING/FS4B/` | file mtimes; directory listing | Codex (§10) |
| P1-2 | Transformation's local provenance `Illustrative operating reality map · constructed example` sits inside the closed `<details class="transformation-folio">`; hidden with and without JavaScript. Ledger acceptance gate fails. | `routes/transformation/src/body.html` line 71 inside 62–72 | live `checkVisibility()` = false at 1440 | Claude (§9.2) |
| P1-3 | Home Act 3 renders a constructed record (`Context record — WG-041`, four labels) before any disclosure; the only Home disclosure is inside the Act 4 instrument; the reset assigns no record object to Act 3; identity duplicated. Ledger: shared disclosure precedes the first constructed artifact. | `home/src/body.html` 63–74 vs 94 | DOM order; live render | Claude (§9.1) |

### 1.3 P2 — fixed in FS5 or FS6

Visible quality: Company closed partnership `<details>` stretches to 404 px (grid-row placement, `company/src/direction.css` 66–69) leaving ~340 px of empty ink and a stray rule · Trust's default "one exception/result" (`Invoice and receipt disagree`, `Release withheld`) is inside the closed record · Transformation actions float over the image pulled up by `margin-top:-120px`; folio default state is one line · Build hero bitmap is a dark CGI instrument whose causal event is not legible in two seconds · WorkGraph desktop first viewport has no action (actions at y≈1325 at 1440×723); record arrives after a full-screen image · Home Act 3 rail is labels without values; Replay↔Pause label swap reflows the instrument header 36 px · five route first screens share one silhouette; at 390 every route's mechanism is below the fold · Transformation H1 computes 63.36 px at 1440 (route override; 68 only ≥1545 px); Build and Assessment H1s wrap to four desktop lines.

Copy and contract: header flyout descriptions and fourth label differ from contract §4; footer lacks Privacy/Terms; `Menu`/`Close` vs contract labels; top-level `Build` is a `<summary>`, not a link · Trust hero instrument copy is not in the contract · WorkGraph default copy ≈450 words vs 320–430 band · Trust, Company, Assessment, Impact have no `data-copy-scope` hooks · all page maps predate FS2/FS4A; Home has no current map · WorkGraph lens live region is rewritten on load.

Motion and interaction: Home sequence lacks hover/focus suspension (FS0 §3.5); under reduced motion it still offers a timed `Replay sequence` · Transformation outcomes tap-only below 1180 px or with a coarse pointer · mobile-sheet Escape layering (first Escape closes the inner Build disclosure, second closes the sheet) undocumented.

Technical: every route loads the 78 KB specimen stylesheet and 31 KB specimen script · three unsubset variable fonts ≈399 KB (budget two files ≤160 KB) · absolute `/preview/golden-standard/…` hrefs everywhere · Impact `noindex` only via runtime JS · no hero preload · disk snapshot ID differs from served because of three non-candidate files (FS5 draft, `tests/test_preview_revision.py`, `tools/check_p1_copy.py`).

### 1.4 Verified live versus not verified

Verified live (tab visible): flyout keyboard path and hover open; Factory pass timing and controls; Home resolved state, Replay → running, Pause shown; Assessment validation; mobile sheet open state and Build reveal at 527 px; console and overflow on all routes; snapshot identity.
Not verified live (environment, Appendix C): reduced motion, true no-JS, 200 % zoom, exact 1440 and 390 runtime, flyout close-grace timing, carrier reversal timing, mobile-sheet Escape close with focus restore. Source logic exists for each; §10 proves them.

---

## 2. What 10/10 means

### 2.1 Scorecard (reviewer estimate today → target)

| Dimension | Pass condition at 10 | Today | Target |
|---|---|---|---|
| Strategic clarity | A first-time reader states what Dagg does and for whom after two Home screens; no product name before its business consequence | 8 | 9 |
| Visual distinction | Seven first screens distinguishable as grayscale thumbnails; one Decision Field world; coral/sage never decorative | 6 | 9 |
| Product concreteness | One constructed thread (WG-034, supplier payment exception) witnessed on Home, WorkGraph, Build and Trust, each route owning one layer | 6 | 9 |
| Execution credibility | Every material claim has an adjacent artifact, state or boundary; an action is seen prepared, withheld and returned to a named owner without a click | 7 | 9 |
| Executive accessibility | Home ≤520 default words, first screen ≤55, zero unexplained Dagg vocabulary above the fold | 9 | 9 |
| Technical credibility | Permission, stop condition, owner, evidence and way back are explicit text on WorkGraph, Build and Trust | 8 | 9 |
| Narrative flow | Each close asks the next chapter's question; every link and anchor resolves; no repeated proposition | 8 | 9 |
| Motion | Exactly three autonomous sequences; each finite, pausable, hover/focus-suspended, instant under reduced motion, complete without JavaScript | 7 | 9 |
| Mobile and accessibility | Defining mechanism begins in the first 320/360/390 viewport; 44/48 px targets; axe-core zero critical/serious; 200 % zoom reflows | 7 | 9 |
| Performance | Local LCP ≤2.0 s, CLS ≤0.05 at 1440 and 390; fonts subset; no specimen payload | 6 | 9 |
| Conversion | Every `Start an assessment` resolves; validation, focus, truthful confirmation by keyboard and touch; no data leaves the preview | 9 | 9 |

Process condition: every gate in §10 passes fail-closed from one command against one snapshot ID; independent Fable acceptance finds no P0/P1.

### 2.2 What would still make it merely polished

- The WG-034 thread is described on four routes but never seen withheld and returned → polished, not category-defining.
- First screens keep one template with a different photograph → a beautiful consultancy site.
- Impact empty at launch → honest, but the site sells trajectory only; one permissioned proof is a business decision no design package substitutes for.
- Phones meet a brochure because every mechanism starts below the first screen.
- Evidence stays screenshots without an immutable ID → nothing is proven.

### 2.3 The headline-only story (as rendered on the candidate)

Whole site, H1 sequence in route order — the argument a reader gets from headlines alone:

1. Build the company AI makes possible.
2. Decide how the company should work before choosing what to build.
3. The model can change. Company context should remain.
4. Turn the decision into a system that can act.
5. Control belongs inside the system.
6. The people who shape the direction stay accountable for what gets built.
7. The first engagement is a decision, not a project.
8. (internal, gated) What changed should be possible to prove.

Reads: possibility → judgment before tooling → durable context → execution → control → accountability → a bounded first move → proof. It holds. The two weak joints are Build → Trust (the reader has to infer that "act" needs "control") and Company → Assessment (accountability to commitment), both carried by the route closes rather than the H1s; §7 keeps those closes.

Per route (H1 then H2s, verbatim from the assembled pages):

- **Home** — Build the company AI makes possible. → AI-native changes who executes — and who decides. → Start with how the company really works. → The decision becomes a working system. → Every operating cycle makes the next one better. → One partner, from direction to accountable release. *Complete causal spine; no change.*
- **Transformation** — Decide how the company should work before choosing what to build. → Machine speed requires a different division of work. → See the whole path, not only the visible workflow. → The first decision is what not to automate. → Sequence the change while the company keeps running. → Keep the operating model adaptable as AI capability changes. → Retain the decision before the build begins. *Strongest supporting spine; no change.*
- **WorkGraph** — The model can change. Company context should remain. → Context begins with how work actually moves. → One retained record connects transformation, build and operation. → Start with the context the intervention requires. → Carry the decision into a working system. *Complete; the record must now appear under the H1 rather than after an image (§9.3).*
- **Build** — Turn the decision into a system that can act. → Automate what should stay. Rebuild what should change. → A build begins with a decision, not a prompt. → Nothing acts beyond its permission. → Decide who will run it before it ships. → Who stays accountable from direction through release? *Complete; the first screen must show the system acting (§9.4).*
- **Trust** — Control belongs inside the system. → Permission is attached to the action. → The exception is part of the product. → Keep the operating model governable beyond any one model. → A release needs a way back. *Complete; the first proof must show the exception (§9.5).*
- **Company** — The people who shape the direction stay accountable for what gets built. → Dagg exists to make the AI-native operating model real. → Judgment, company building, engineering and execution belong together. → The engagement is designed around named decisions and boundaries. → Accountability has names. → Begin with the decision that matters most. *Complete; opening composition changes (§9.6), headlines do not.*
- **Assessment** — The first engagement is a decision, not a project. → Start where consequence and ownership are clear. → Follow the path from evidence to choice. → You leave with a decision you can use. → Begin with one path that matters. (+ hidden confirmation H2 `The inquiry is ready for review.`) *No change.*
- **Impact (internal)** — What changed should be possible to prove. → Two forms of transformation. One evidence standard. → A result without provenance is a claim. → Begin with the decision that can become evidence. *No change; stays gated.*

---

## 3. Methods — the rigor this plan borrows, and what it refuses to import

**Sources actually read.** The three authority PDFs (every page image plus extracted text), the masterplan, the content contract, the founder reset, the evidence ledger, all packages FS0–FS5, all page maps, the five peer audits (`reference-audits/`), the legacy design language (`design/DESIGN-LANGUAGE.md`, the written rules behind the Arrowhead deck), the browser-measured peer notes (`design/MEASURED.md`, `design/TEMPLATE.md`), all route source, the shared chrome and component substrate, the assembler and snapshot server, all current rendered evidence, the live candidate, and — read directly and read-only on 2 September 2026 with `pdftotext -layout`, all pages — `/Users/christianperez/Downloads/About-Insight-Pitch-Deck-v1.pdf` (19 pages, 1440×810) and `/Users/christianperez/Downloads/About-Insight-Brand-Design-System-v0.1.pdf` (18 pages, A4). Page images of the two About Insight documents were not rendered; the observations below come from their complete extracted text.

**Direct observations from the About Insight documents that matter for Dagg (method only).**
- One conclusion per screen. Every deck slide carries one headline written as a sentence; the brand system states it as a rule ("One idea per slide, the headline as a sentence"; "Headlines are sentences, not labels").
- A headline-only narrative that holds by itself. Read as headlines alone the deck runs: accounting is becoming AI-native → the interface is moving → humans orchestrate, agents execute, legacy stays connected → autonomy you can audit → a firm that grows without growing its administration → right information → right control → right person → right decision → not another system, the layer between them → the 17 things you need to act on today, not the 500 that work → same people, same competence, a different day → the portal is the command centre, the chat is the cockpit → the answer comes from the layer with its source → legacy systems were built for a person with a screen → we build the way we work → velocity is the operating model → founded by a firm and a builder → fewer initiatives, done 0–100, baseline first → one platform, one playbook → three firms, then the alliance. Dagg applies the same test in §2.3 and gates it in §10.
- Claim followed by mechanism or proof. The mandate ladder (Observe · Prepare · Confirm · Delegate · Selective autonomy) with "Always a person" and "When unsure: abstain, escalate, never guess"; the six morning questions; the exception-row anatomy (state bar, title, one line of context with a provenance chip, due date in mono, a named owner). Dagg's equivalent is the WG-034 thread carried through Home, WorkGraph, Build and Trust (§7, §9).
- Provenance adjacent to claims. Every product value shows source and time (`Källa Business Central 08:14`, `Beräknad 08:15`, `AI-förslag 09:03`); slide footers name sources and dates; illustrative data is labelled as such. Dagg's equivalent is the disclosure-order rule, the provenance-visible-with-disclosures-closed gate and the P/R/V/C/X ledger status on every claim.
- Consistent rhythm. Three acts (the shift, the product, the company and the path); paper body slides, forest reserved for title, section breaks and close; evidence set in mono at the foot of each slide. Dagg keeps its own rhythm rules (Paper world, at most three ground changes, height variation by argument) and gates them in §10.
- Solution first, concrete over abstract. "Here are the 17 things you need to act on today" is preferred to "AI-powered exception management"; "Same people. Same competence. A different day." Dagg's equivalent is replacing generic execution states with the request, decision, withheld action and returned evidence of one supplier-payment exception.
- Plain, confident, unhurried language. Short sentences; no exclamation marks; no jargon without a translation (exception / avvikelse, mandate level / mandatnivå). Dagg's copy gate forbids superlatives and unexplained Dagg vocabulary above the fold; `Harness engineering` becomes `AI system engineering` for that reason.
- Numbers, dates and provenance carry the claims. "26 August 2026"; "37 prebuilt skills"; "around seventy recurring obligations per client per year"; "Day 0 … Day 15"; "82 user stories and 41 architecture decisions"; "$63"; "Delivery from 19 August". Dagg has no publishable customer numbers yet, so the honest translation is stricter, not looser: no number appears without a ledger status, every constructed artifact says so, and Impact stays gated until a permissioned proof exists.
- Two further rules worth keeping as method: "State is not decoration" (semantic colours kept apart from the brand accent; "Red means deviation. Nothing else is red.") mirrors Dagg's coral-as-judgment and sage-as-boundary discipline; and "we started from the product, not from a mood board" mirrors Dagg's rule that coded artifacts, not generated images, carry proof.

**Borrowed from Dagg's own deck-derived design language (`DESIGN-LANGUAGE.md`):**
- Confident understatement as the register: state, don't qualify; no adjectives about Dagg; no performed humility. Every §9 copy string is verbatim from an accepted authority; the writer adds no sentence.
- The hedging budget: a qualification survives only if its absence would create a false belief. Applied here as the disclosure rule — one constructed-example line per page, placed before the first synthetic identifier, never repeated, never hidden.
- Three registers on every screen (a header, a main argument, a band of supporting fact): applied as first-viewport contracts that require proposition, action and one inspectable object together.
- Conclusion-led headlines that could carry the story alone: applied as the headline-only test in §2.3 and as a gate.
- "Never empty, never crowded" and document scale over poster scale: applied as the 6:1 ceiling between H1 and meta (92 : 13 on Home is 7:1 and is the documented exception; 68 : 13 elsewhere is 5.2:1) and as the anchor-gap rule (no empty interval above 60 % of viewport height without a semantic object).

**Borrowed from the measured brand-system references (`MEASURED.md`, `TEMPLATE.md`, the five audits):**
- Measure, don't impress: every layout claim in §5 and §6 is a computed value or a browser measurement, and every acceptance line in §9 names the measurement that proves it.
- Section-height variation of 4–6× between shortest and tallest act, one carrying section per page, media rare and grouped, punctuation sections of 120–180 px: applied as rhythm checks in §10 and as the reason Build and WorkGraph move their proof into the first screen instead of adding a third image.
- Ground discipline: peers keep one ground per page and use height for variation; Foundations allows at most three ground changes. The plan keeps the Foundations rule (it is the binding authority) and adds the measured caution: variation must come from height and composition first, ground second.
- Proof architecture from Palantir (attributed statement → starting condition → mechanism → outcome → source) without its ontology jargon; product-first entrance from OpenAI without a prompt box; stable carriers with state change from xAI without terminals; warm material and editorial air from Anthropic without its collage.

**Refused — explicitly.** From About Insight: its brand and green palette (Forest `#17201b`, Pine `#024c35`, Leaf `#0b936b`, Paper `#f4f3ee`, Mist, Slate; Amber, Terracotta and Info state colours), its typefaces (Hedvig Letters Serif, Inter), its pill buttons and dark sidebar, its content (accounting, the 17 things, the year-wheel, the mandate ladder, About Value, the Swedish product copy, the Salesforce–Anthropic example) and its deck layout (1440×810 slides, forest title/section/close, evidence-in-mono footers, the three-act slide sequence). From Dagg's own earlier deck: the second colour (green), folios and per-section page rails, slide-ground alternation (near-white/ivory/night per slide), poster-scale display serif for running text, and any layout that reads as a deck or a pitch. The site keeps Paper as the one reading world, coral and sage as its only semantic signals, Geist/Newsreader/JetBrains Mono, and section rhythm that varies by argument.

**Scoring method.** §2.1 and §6 use a 1–10 scale where 10 means the pass condition is met with evidence on one immutable snapshot, 7 means the condition is met by design but not proven, and below 7 means a visible or structural gap. Peer scores use the measured figures in the audits and the reviewer's judgment of the live pages as sampled on 30 August–1 September 2026.

---

## 4. Protected decisions (immutable in every package)

1. Logo and wordmark; Paper `#F0EEE6`, Lift `#FAF9F5`, Panel `#E8E6DC`, Ink `#141413`, Ink 2 `#33332F`, Coral `#R97757`, Coral deep `#9E4A2E`, Sage `#7C8471` and their roles; Geist, Newsreader, JetBrains Mono roles including the Home serif display exception (`home/src/direction.css` 114–121).
2. Primary navigation: Transformation · WorkGraph · Build (adaptive disclosure) · Company · `Start an assessment`; Impact withheld until a proof is permissioned.
3. Home: V4 hero pair (`home-hero-selected-desktop-v4.webp` 1983×793; `home-hero-selected-mobile-v4.webp` 1448×1086), full-width band under the editorial proposition, H1 `Build the company AI makes possible.`, first-screen lead and two actions, six-act order, every paragraph of Acts 1–3, 5 and 6.
4. The route headline spine (§2.3) and all contract copy not named in §9.
5. Transformation's five-outcome continuum and decide-before-build thesis; Assessment's asymmetric composition and truthful non-transmitting preview.
6. Image roles: Decision Field surrounds and explains; Operational Evidence proves; Machine Signal transitions and stops; one primary role per section, at most two.
7. Shared chrome behavior, tokens, assembler, snapshot server.
8. No invented client, metric, deployment, endpoint, certification or operating claim; no deploy, publish or canonical promotion without Christian's explicit gate.

---

## 5. Design system by viewport

### 5.1 Exact type and layout values (computed from `tokens.css` formulas; Home and Transformation H1 from their route overrides)

| Viewport | Gutter | Column gap | Field | Section lg / md | H1 | H2 | H3 | Lead | Body | Meta | Home H1 (serif) | Transformation H1 | Mode |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1536 | 72 | 32 | 1240 | 160 / 112 | 68.0 | 52.0 | 32.0 | 23.0 | 18.0 | 13.0 | 92.0 | 67.6 | desktop |
| 1440 | 72 | 32 | 1240 | 160 / 112 | 68.0 | 52.0 | 32.0 | 23.0 | 18.0 | 13.0 | 87.8 | 63.4 | desktop |
| 1366 | 48 | 32 | 1240 | 160 / 112 | 66.3 | 50.9 | 31.6 | 22.8 | 17.9 | 12.9 | 83.3 | 60.1 | desktop |
| 1280 | 48 | 32 | 1184 | 160 / 112 | 64.3 | 49.6 | 31.2 | 22.5 | 17.9 | 12.9 | 78.1 | 56.3 | desktop |
| 1180 | 48 | 32 | 1084 | 160 / 112 | 62.1 | 48.0 | 30.8 | 22.3 | 17.8 | 12.8 | 72.0 | 54.0 | desktop; sticky carriers begin |
| 1024 | 48 | 32 | 928 | 160 / 112 | 58.5 | 45.7 | 30.0 | 21.8 | 17.6 | 12.6 | 62.5 | 54.0 | desktop, compact nav |
| 940 | 24 | 24 | 892 | 112 / 88 | 56.6 | 44.4 | 29.6 | 21.6 | 17.5 | 12.5 | 57.3 | 54.0 | last desktop |
| 939 | 24 | 24 | 891 | 112 / 88 | 56.5 | 44.4 | 29.6 | 21.6 | 17.5 | 12.5 | 57.3 | 56.5 | first recomposed; mobile sheet |
| 768 | 24 | 24 | 720 | 112 / 88 | 52.6 | 41.8 | 28.8 | 21.1 | 17.4 | 12.4 | 54.0 | 52.6 | recomposed |
| 390 | 20 | 24 | 350 | 88 / 64 | 44.0 | 36.0 | 27.0 | 20.0 | 17.0 | 12.0 | 54.6 | 44.0 | recomposed |
| 360 | 20 | 24 | 320 | 88 / 64 | 43.1 | 35.1 | 26.6 | 19.6 | 17.0 | 12.0 | 50.4 | 43.1 | recomposed |
| 320 | 20 | 24 | 280 | 88 / 64 | 42.0 | 34.0 | 26.0 | 19.0 | 17.0 | 12.0 | 48.0 | 42.0 | recomposed |

Layout constants: field max 1240 px, twelve columns; strategic split 7/5 (Home hero 8/4, Build hero 5/7, closes 5/7); collapse at 940 px; hero images use `<picture>` with an independently authored portrait source below 940 (Home switches at 640); reading measure 560–620 px (Home 64ch, Transformation 66ch); radii 4 px controls, 10 px surfaces, 14 px instruments; focus ring 2 px with 2 px offset, Ink on warm and Paper on ink; targets ≥44 px, ≥48 px for navigation and Assessment; line-heights H1 1.02, H2 1.07, H3 1.12, lead 1.44, body 1.62, meta 1.42. Rule observed today and kept: Transformation's route override lands below the 68 px endpoint at 1440 (63.4); it is recorded as a P2 and left to Codex.

### 5.2 Global component and interaction table

| Component | Where | Rest | Pointer | Keyboard | Touch | Reduced motion | No-JS | Timing |
|---|---|---|---|---|---|---|---|---|
| Sticky header | all routes | Paper, 68 px (60 mobile), 1 px rule | hides on scroll-down past 160 px, reveals on scroll-up | reveals on focus within | same as pointer | no transition | static header | 240 ms transform, 180 ms colour |
| Adaptive ground | header over `[data-header-theme="ink"]` sections (footer) | Paper | swaps to Ink when the section reaches the header line | same | same | swap without reveal | Paper | 180 ms |
| Skip link | all | offscreen | — | visible on focus, jumps to `#main` | — | same | same | — |
| Primary nav links | ≥940 | Geist 18 px, `aria-current` underline | underline on hover | focus ring | tap | same | real links | 180 ms |
| Build flyout | ≥940 | `Build` summary + chevron | opens 85 ms after intent, closes 210 ms after leaving trigger and panel, hover bridge | Enter/Space toggles; focus on a destination selects its inset; Escape closes and restores focus; closed panel unfocusable | disabled (touch uses the sheet) | inset swaps with no height morph | first destination's inset painted; all four links real | panel morph 200 ms, crossfade 120 ms |
| Mobile sheet | <940 | `Menu` control 48 px | tap opens fixed Paper sheet under the header | Tab contained inside sheet; Escape closes and restores focus to `Menu` | same; backdrop and link tap close | no transition | authored-open in-flow list, never a viewport sheet | — |
| Build inside sheet | <940 | `Build` row 48 px + per-destination 48×48 reveal buttons (JS-created) | tap reveals one inset at a time | Enter on reveal; Escape closes inner disclosure first | same | same | four real links, no reveal buttons | 180 ms |
| Primary button | all | Coral deep on Paper / Coral on ink, 4 px radius, ≥44 px | Ink background | focus ring | ≥48 px on mobile | same | link | 180 ms |
| Secondary button | all | rule border | Lift fill, Ink border | focus ring | same | same | link | 180 ms |
| Text link | all | Coral deep underline | Ink | focus ring | same | same | link | 180 ms |
| Native disclosure (`<details>`) | Transformation folio and roadmap, WorkGraph record depth and diligence, Build boundary and surfaces, Trust record, Company standard | closed summary ≥48 px, text-only marker | click toggles | Enter/Space toggles | tap | native | native | native |
| Decision continuum | Transformation | five stations on one axis, `Preserve` checked; readout shows selected outcome | ≥1180 px fine pointer: sticky stage, scroll selects outcome; direct selection becomes authoritative | radiogroup, arrow keys move selection | tap selects; all five explanations visible (§9.2) | all five explanations, no runway | all five explanations in order | 240 ms readout fade |
| WorkGraph record lenses | WorkGraph | three `aria-pressed` buttons, JS-only | click emphasises fields from that source | Enter/Space | tap | same | hidden | 240 ms |
| Lifecycle carrier | WorkGraph | steps in flow; record-state card | ≥1180×720 sticky card beside steps; state = last step above the 45 % line; reverses on scroll-up | scrolling only; no control | compact sticky card above steps | resolved on `Learn` | all steps and labels in order | 320 ms |
| Home execution instrument | Home Act 4 | ink instrument, four states, signal line, status | starts once at ≥35 % visibility; hover over the state list pauses (FS5); Pause/Replay | Pause/Replay buttons; focus on an interactive descendant pauses (FS5) | starts on scroll; no hover pause | resolved final state; Replay hidden (FS5) | all four states and Request in order; controls hidden | 1.6 + 2.2 + 2.2 s |
| Factory pass | Build | six stages, status line, Pause/Replay/Inspect | starts when the sentinel enters the upper 60 % of the viewport; hover over stages pauses | Pause/Replay; focus pauses | starts on scroll | resolved on `Governed review`; `Inspect resolved progression` shown | ordered list resolved on stage six; controls hidden | 880 ms per stage, 950 ms holds (580/650 below 940) |
| Hero settle | Transformation, WorkGraph, Build, Company | resolved still | one settle from scale 1.022–1.025 to 1 on load | — | same | none | still | 1.45–1.5 s |
| Trust control path | Trust | three ruled steps + state | one-time staggered settle | — | same | none | resolved | 560/620 ms, delays 300/600 |
| Assessment form | Assessment | hidden until JS | click submit validates | Enter submits; first invalid field focused | tap | reveal 0 ms | `<noscript>` mail path | 450 ms preview reveal |
| Footer | all | Ink, 5/7 grid | link underline on hover | focus ring Paper | tap | same | static | — |

---

## 6. Scored peer comparison and measurable recipes

Scores 1–10 by the method in §3. Peer figures from `reference-audits/` and `design/MEASURED.md` (sampled 29 August–1 September 2026).

| Dimension | Anthropic | OpenAI | Palantir | xAI/SpaceXAI | McKinsey | Dagg today | Dagg target | Measurable recipe Dagg keeps |
|---|---|---|---|---|---|---|---|---|
| Warm editorial materiality | 9 | 5 | 3 | 4 | 4 | 8 | 9 | Paper ground; one dark close; serif for judgment; ≤3 ground changes; 72/48/24/20 px gutters |
| Product proof in or just after the hero | 6 | 9 | 8 | 9 | 3 | 5 | 9 | Proof object inside the first viewport on WorkGraph and Build; Home proof within two screens; no prompt box |
| Conclusion-led hierarchy | 8 | 7 | 6 | 7 | 9 | 8 | 9 | H1 6–12 words, ≤2.5 lines desktop (Home exception 2 lines at 92 px); headline-only story passes |
| Operational credibility (mechanism, owner, boundary, way back) | 5 | 6 | 9 | 7 | 4 | 7 | 9 | Every constructed artifact shows permission, stop condition, owner, evidence, way back as text |
| Motion discipline | 8 | 8 | 5 | 8 | 8 | 7 | 9 | Three finite sequences; 180–240 ms micro; 0.8–1.2 s signal; 6–8 s pass; reduced motion instant |
| Navigation behavior | 7 | 8 | 6 | 9 | 6 | 8 | 9 | 70–100 ms intent, 180–240 ms grace, stable panel, keyboard parity, inert sheet |
| Trust architecture | 6 | 7 | 9 | 6 | 5 | 7 | 9 | Control fields as text, diligence as a real mail action, no badge wall, no unverified assurance |
| Mobile recomposition | 8 | 8 | 5 | 7 | 6 | 7 | 9 | 20 px gutters; authored portrait heroes; mechanism in the first 844 px; 44/48 px targets; no overflow |
| Density calibration | 9 | 7 | 5 | 6 | 5 | 8 | 9 | Route bands (Home 430–520, routes 260–600); progressive copy capped; artifact replaces prose |
| Conversion | 6 | 9 | 7 | 9 | 5 | 8 | 9 | One persistent action; validation, focus, truthful preview; two intents (assessment, dialogue) |
| Evidence and truth boundaries | 7 | 6 | 8 | 4 | 5 | 8 | 10 | P/R/V/C/X status on every claim; disclosure before first artifact; no invented number |
| Reproducible QA | — | — | — | — | — | 4 | 10 | One command, one snapshot ID, fail-closed gates (§10) |

### 6.1 How Dagg can exceed each peer

| Peer | Peer strength | Weakness Dagg refuses | Dagg intended advantage | Exact route/section mechanism that earns it | Evidence gate preventing self-congratulation |
|---|---|---|---|---|---|
| Anthropic | Warm editorial materiality; one tactile idea-object per chapter; institutional calm; sparse imagery; sans for structure, serif for judgment | Delivery stays invisible: abstraction with no inspectable B2B mechanism; no operational landing within the viewport | The same warmth resolves into a coded mechanism within one viewport, so the reader never has to trust an image alone | Home: hero Decision Field → Act 3 WG-034 identity with Owner and Permission → Act 4 four-state execution object (§9.1). WorkGraph: the retained record sits beside the thesis in the first screen (§9.3). Company: accountability chain instead of a second tactile hero (§9.6, R5) | Runner asserts that every Decision Field image has a coded artifact or contract copy within one viewport height at 1440 and 390 (§10 first-viewport contracts); copy gate forbids any sentence describing Dagg as warm, human or considered; Fable judges two-second legibility of each image without its caption |
| OpenAI | Product proof first; buyer-language information architecture; one dominant artifact with a narrow evidence rail; two conversion routes | Generic prompt box as hero; content-feed magazine; all-white sterility; logo theater without sourced stories | The proof is a governed operating record — request, decision, permission, withheld action, returned evidence — not a chat surface; conversion offers a bounded assessment and direct dialogue | Home Act 4 execution object with static `Request` row and four states (§9.1); Build hero Factory stage `Approved intervention → Specification → Evaluation → Review state → Evidence return` (§9.4); Assessment primary action plus `Start a dialogue` mailto on Company (§9.6) | Runner asserts no text input or prompt-like control exists outside the Assessment form; Home Act 4 and the Build stage must expose an accountable owner and a withheld action as DOM text in their resolved state; copy gate forbids `AI` superlatives and any claim of intelligence not tied to a state |
| xAI / SpaceXAI | Operational immediacy: a stable carrier changes state beside copy; adaptive flyout; 44 px controls; visible cadence | Terminal and code walls; monochrome black world; vanity scale metrics; 36 px mobile CTAs; unnamed menu control; 11,000 px mobile pages | State change on a warm ground with human judgment made explicit in coral, a verification hold in sage and a way back, inside three finite sequences | WorkGraph lifecycle carrier Connect → Decide → Build → Learn with invariant Owner and Permission (§9.3); Build Factory pass with judgment and verification holds (§9.4); Transformation continuum with all five explanations reachable on touch (§9.2) | Carrier gate: forward and reverse progression at labelled positions; Factory pass finite 6–8 s, never loops; copy gate forbids `LIVE`, `production` and any number without ledger status; targets ≥44 px and navigation ≥48 px; menu control has an accessible name; route heights recorded per viewport and judged by Fable |
| Palantir | Proof architecture: promise → named system → mechanism → measured proof → matched action; trust as an evidence-heavy destination; Impact first-class | Ontology jargon; node and circuit diagrams; black command-centre; 100 px display type; 15,000 px tours; mobile overflow; giant embedded forms | The same evidence chain in plain language on warm material, with the truth boundary stated before the claim; Trust reachable from every proof; Impact honest until a proof is permissioned | Trust control path with `Action withheld`, `Permission`, `Accountable owner` and recorded state, plus OR-021 (§9.5); Build trust rail (§9.4); Impact eight-field evidence chain and truthful empty slot (§9.7); ledger P/R/V/C/X on every claim | Copy gate: provenance visible with all disclosures closed on every route; no route exceeds three ground changes; Impact absent from navigation, footer and links until a C/V proof passes; every claim carries a ledger status in the contract audit; H1 capped at 68 px (Home 92 exception) |

Measured recipe lines carried into gates: Anthropic institutional hero ≈390 px below a 68 px nav with a 61/67 px H1 (Dagg: hero copy block + 413 px image band, H1 68–92 px); OpenAI 32 px gutters, 1201 px container, 895/282 proof-and-rail (Dagg: 1240 field, 7/5 and 5/7); Palantir 1365 px field, 783.8/435 columns, 100/115 px H1 rejected as poster scale (Dagg caps H1 at 68, Home 92); xAI 24/16 px margins, 60/36 px H1, 44 px controls, 7–8 s loops (Dagg 6–8 s finite pass, no loop); McKinsey conclusion-first structure adopted, self-description rejected. Peer weaknesses Dagg must not inherit: Palantir mobile overflow (`scrollWidth 383` vs 375) and 26.8 px anchor items; xAI 36 px mobile CTAs and unnamed menu control; OpenAI 40 px utility controls; Anthropic's delivery invisibility.

---

## 7. Credibility architecture per route

Each row: what the reader is asked to believe → the artifact that shows it → the provenance label that qualifies it → the boundary that limits it → the question the route hands to the next.

| Route | Claim | Artifact | Provenance | Boundary | Next question → route |
|---|---|---|---|---|---|
| Home | Dagg decides how a company should work with agents and software, then builds it | Hero causal image; Act 3 WG-034 identity with Owner and Permission; Act 4 four-state execution object | `Constructed example, not client data or a production deployment.` before the first WG-034 (once) | `A product pattern, not a named deployment or provider.` | What must change first? → Transformation; how is it controlled? → Trust |
| Transformation | Decide the operating model before choosing what to build | Division-of-work ledger; operating-reality folio; five-outcome continuum; six-step sequence | Page disclosure before the folio; `Illustrative operating reality map · constructed example` visible with folio closed | `Future capability is a planning scenario, not a promise about a model, date or outcome.` | How does the decision survive into implementation? → WorkGraph `#record` |
| WorkGraph | Company context can remain usable while models change | Record WG-034 (Decision, Owner, Permission default; Evidence, Operating state, Reason, Provenance, History progressive); lifecycle carrier with invariants | Page disclosure before the record; `Representative WorkGraph record · synthetic data` | `The depth of WorkGraph grows with the work it must govern.`; provider/residency/retention deferred to diligence | How does retained context become a working system? → Build `#factory` |
| Build | An approved decision becomes governed agents or software | Factory stage (intervention → specification → evaluation → review state → evidence return); two plans; finite pass; control rail | Page disclosure above the stage; `Illustrative Factory build plan · not a client deployment`; `Illustrative operating record · constructed example` | `Operating roles are defined per engagement…`; two-surfaces pattern `not a claim about a named customer deployment or a specific external provider` | Who stays accountable? → Company; how is action governed? → Trust `#permission` |
| Trust | Control belongs inside the system | Control path (action withheld, permission, accountable owner, recorded state); five control fields; OR-021 record | `Constructed control path`; page disclosure; `Illustrative operating record · constructed example` | `This is an architecture principle, not a promise of universal portability…` | How do we begin exact technical review? → mailto diligence; how do controls enter the build? → Build `#factory` |
| Company | The people who shape direction stay accountable for what is built | Accountability chain (Decision, Build, Escalation); four capabilities; named leadership | none needed for method statements (P); leadership titles V before publication | `…no residency, retention, encryption or isolation assurance is implied here.` | How would we work together? → Assessment; direct dialogue → mailto |
| Assessment | The first engagement is a decision, not a project | Scope card; four-item scope; process; Decision Pack; validated form with truthful preview | `This local preview has not sent any data…` | `The assessment is a decision instrument, not a commitment to build.` | Return → Home |
| Impact (gated) | What changed should be possible to prove | Evidence chain of eight fields; truthful empty proof slot | `Approved proof · none published`; `Internal staging route · not published` | Publication requires an approved proof | Begin with the decision that can become evidence → Assessment |

Rule enforced by §10: on every route the provenance label is visible with all disclosures closed, JS on and off, at 320–1536.

---

## 8. Execution plan and package checklists

### 8.1 Sequence, owners, gates

| Step | Package | Owner | Duration (est.) | Output | Gate to proceed |
|---|---|---|---|---|---|
| 0 | FS4B review (this document) | Fable | done | Stored beside FS4B evidence | Codex accepts P1s |
| 1 | FS5 pre-activation | Codex | day 1 (runner build starts in parallel and continues through step 2) | Amended contract and reset; R1–R10 resolved defaults recorded; maps re-baselined; hooks added; runner dry-run | Activation condition: R1–R10 recorded and authority files reconciled to §9; Fable reconciliation read of the final FS5 text (same day) |
| 2 | FS5 writing | Claude Code, one writer | days 1–3 | Source edits in owned files only; `FS5-IMPLEMENTATION-REPORT.md`; assembler check mode only | Writer's failure-first report; protected hashes unchanged |
| 3 | FS5 assembly and evidence | Codex | day 3–4 | One assembly; one snapshot equal to disk for candidate files; atomic evidence package | All §10 gates pass |
| 4 | FS5 founder-review acceptance | Fable | day 4 | Verdict beside the runner package | No P0/P1 |
| 5 | FS6 publication | Codex + Claude (bounded) | dependency-led; not estimated | Canonical routing, legal routes, endpoint, fonts, CSS split, robots, titles | Christian's launch gate |

Steps 1–4 total 2–4 working days to a founder-reviewable candidate and deploy nothing. Step 5 depends on approved legal text and a real endpoint, is not part of the immediate repair, and carries no promised date.

### 8.2 File ownership (no overlap)

Claude Code (FS5) may edit only:
`preview/golden-standard/home/src/{body.html,direction.css,direction.js}` · `routes/transformation/src/{body.html,direction.css,direction.js}` · `routes/workgraph/src/{body.html,direction.css,direction.js}` · `routes/build/src/{body.html,direction.css,direction.js}` · `routes/trust/src/{body.html,direction.css}` · `routes/company/src/{body.html,direction.css}` · `evidence/FULL-SITE-STAGING/FS5-IMPLEMENTATION-REPORT.md`. (`transformation/src/direction.js` is added to the FS5 draft list; §9.2 needs it.)

Codex owns everything else: `shared/chrome/*`, `tokens.css`, `component-library/*`, `assets/*`, images and crops, `tools/*`, `tests/*`, all generated `index.html`, Assessment and Impact sources, narrative and mapping documents, all evidence.

### 8.3 Checklist — Codex pre-activation (step 1)

- [ ] Record R1–R10 — RESOLVED DEFAULTS (§12) in the FS5 text as binding.
- [ ] Amend `FULL-SITE-CONTENT-CONTRACT.md`: WorkGraph 1 record-in-hero and row assignment (§9.3); Build 1 first-screen object with the two FS5 lines (§9.4); Trust 1 instrument copy and state (§9.5); Company 3 label; header/footer/menu wording per R9; budgets restated with the §10.4 method.
- [ ] Amend `HOME-NARRATIVE-FOUNDER-RESET.md` Acts 3–4 with §9.1 copy (R1).
- [ ] Re-baseline `design-mapping/`: new Home map; WorkGraph, Build, Trust, Company maps to §9; mark superseded sections.
- [ ] Add `data-copy-scope` hooks to `routes/assessment/src/body.html` and `routes/impact/src/body.html`.
- [ ] Image lane: Transformation 4:5 desktop-side use of the mobile asset if R3 = A; Company seam crop if R5 = A; register in `ASSET-REGISTRY.json` and slot manifests with hashes.
- [ ] Write `tools/capture_fs5_evidence.py` and `tests/test_fs5_candidate.py`; dry-run against `6ef754faf00f`; the dry run must fail on P1-2 and P1-3 and pass the rest.
- [ ] Move `FS4B/rendered/*` to `FS4B/superseded/rendered-pre-repair/`.
- [ ] Re-freeze a snapshot so served ID equals disk.
- Definition of done: FS5 text final; every §9 copy string present in the contract or reset; runner proven fail-closed; Fable reconciliation returns no open item.

### 8.4 Checklist — Claude writer (step 2)

- [ ] Read §4, §9 and the amended contract and reset; confirm every string in §9 exists there.
- [ ] Edit only the files in §8.2; keep every existing `data-*` hook; add `data-copy-scope` to every new visible node.
- [ ] Keep DOM order identical at every width; no CSS `order`; no new hue, family, radius, icon, breakpoint or remote reference.
- [ ] Run `node tools/build_golden_standard_previews.mjs --check` only; never write mode, commit, assembly, deploy or publish.
- [ ] Confirm protected hashes unchanged against the re-keyed `FS4-INVARIANT-BASELINE.json`.
- [ ] Report: failures first; changed files with reasons; measured default/progressive/first-section per route using §10.4; every deviation from §9; statement that nothing was assembled or published.
- Definition of done: all §9 acceptance lines self-checked at source level; report filed.

### 8.5 Checklist — Codex assembly and evidence (step 3)

- [ ] Assemble once; verify byte-identical outputs on a second check run.
- [ ] Freeze one immutable snapshot; confirm ID equals disk for every candidate path.
- [ ] Run the §10 rig; promote atomically only on full pass; keep failed packages under `.failed-<snapshot>-<timestamp>`.
- [ ] Publish `report.md` with failures first and the snapshot ID in every artifact.
- Definition of done: every §10 row passes; package promoted; no evidence from another snapshot present.

### 8.6 Checklist — Fable acceptance (step 4)

- [ ] Read-only against the promoted package and the same snapshot ID.
- [ ] Judge every route screenshot at every viewport and every state capture; re-run the headline-only test; grayscale-thumbnail the seven first screens.
- [ ] Verdict stored beside the package; any P0/P1 rejects FS5 without editing runner evidence.

### 8.7 Checklist — FS6 publication (step 5)

- [ ] Base-path substitution in the assembler; canonical routes; sitemap; canonical and social metadata per route.
- [ ] Privacy and Terms routes with approved legal text; footer links.
- [ ] Assessment endpoint, delivery, error state, spam protection, retention, privacy copy; contract success/error copy.
- [ ] Fonts subset or static instances within two files ≤160 KB; hero image preload.
- [ ] Split shared substrate from the specimen stylesheet and script.
- [ ] Static robots meta for Impact via `src/head.html`.
- [ ] Header and menu wording per R9 recorded in the contract.
- [ ] Leadership names and titles verified.
- [ ] Production performance gates and platform smoke tests (macOS Safari and Chrome, Windows Edge, iPad Safari both orientations, iPhone Safari, 320 px touch).
- [ ] Christian's launch gate on the exact production revision.

---

## 9. Section-by-section specification for every route

The amended authority files — `FULL-SITE-CONTENT-CONTRACT.md`, `HOME-NARRATIVE-FOUNDER-RESET.md` and the page maps — carry every string in these tables verbatim, including all retained copy marked "unchanged", so the writer sources from the authorities, never from this plan.

Columns: **Copy** — exact source or exact string (verbatim from the contract, the reset or FS5; the writer adds nothing) · **Image** — role and asset · **Component · interaction** — what it is and what it does · **Input** — pointer · keyboard · touch · **RM / no-JS** — reduced motion and no-JavaScript behavior · **Credibility** — provenance and boundary · **Owner** — file(s) · **Acceptance** — the measurement that proves it. "unchanged" means the current candidate already meets the specification and must not be altered.

### 9.1 Home (`home/src/body.html`, `direction.css`, `direction.js`)

First-viewport contract, unchanged: 1440×900 and 1536×1024 — eyebrow, H1, lead, both actions, full-width image band; 1024×768 — same in the 8/4 split; 390×844 — eyebrow, H1, lead, stacked actions, top of the mobile image. Hero pixel-diff ≤0.5 % against the frozen FS4 baselines.

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| Act 1 Position (hero) | Reset Act 1 verbatim; unchanged | Decision Field + restrained Machine Signal: V4 pair via `<picture>`, mobile source <640 | Editorial 8/4 hero; full-width image band `clamp(300px,27vw,430px)` (mobile `clamp(250px,72vw,330px)`); no motion on the image | Buttons: hover Ink, focus ring, 48 px on mobile | Identical; identical | None needed (P copy) | none (protected) | Pixel-diff ≤0.5 %; `currentSrc` desktop ≥640, mobile <640; H1 2 lines desktop; both actions single-line at 1440 and 1536 |
| Act 2 Operating shift | Reset Act 2 verbatim; unchanged | none (typographic) | 7/5 editorial turn with coral dash | Text link hover Ink | Identical; identical | none | none | `See what must change` → `/routes/transformation/` resolves |
| Act 3 Map and retain — copy | Reset Act 3 verbatim; unchanged | none | 7/5, copy left | Link | Identical; identical | none | none | Link → `/routes/workgraph/#record` |
| Act 3 — record aside (replaces lines 63–74) | In order: `Constructed example, not client data or a production deployment.` · `Context record — WG-034` · `One governed exception, carried through` · `Owner` — `Finance owner.` · `Permission` — `Prepare only. Never release.` | none (coded identity) | `home-record` surface: disclosure in mono meta ≥12 px `--ink-2`; identity; two-row `<dl>` 64 px rows; sage inline-start rule on Permission; no label list | none (static) | Identical; identical | Disclosure is the page's single constructed-example line and precedes the first synthetic identifier | `body.html`, `direction.css` | Disclosure `checkVisibility()` true at 320–1536; `WG-041` absent from Home; disclosure text occurs once on Home |
| Act 4 Build and expose — copy | Reset Act 4 verbatim incl. boundary; unchanged | none | 4/8 on ink at ≥1100 | On-ink link hover Paper | Identical; identical | `A product pattern, not a named deployment or provider.` | none | Link → `/routes/build/#factory` |
| Act 4 — execution instrument | `Context record — WG-034` · `One governed exception, carried through` · static `Request` — `Prepare this supplier payment exception for review.` · states: `Operating reality` / `The invoice and receipt disagree.` · `Decision retained` / `Automate preparation. Keep human approval for release.` · `Governed execution` / `The agent prepares the draft. It cannot release payment.` · `Evidence returns` / `The finance owner decides; the result and evidence update the same record.` · initial status `Ready to inspect the operating change` · completion `Human decision recorded. Release remains withheld.` · controls `Pause sequence` / `Resume sequence` / `Replay sequence`; the current disclosure line at 94 is removed | Operational Evidence (coded) + Machine Signal signal line (coral → paper → sage) | Ink instrument; starts once at ≥35 % visibility; 1.6 + 2.2 + 2.2 s; stops on state 4; pauses offscreen and on document hidden; **new:** pause on pointer over the state list (non-touch) and on focus of an interactive descendant; explicit Pause authoritative; controls fixed `min-width` so the identity row height never changes | Pointer hover pauses; Pause/Replay buttons; keyboard: Tab reaches Pause/Replay only (no `tabindex` on states); touch: no hover pause | RM: resolved final state immediately, `Replay` hidden; no-JS: Request and four states in order, controls hidden | Provenance carried by the Act 3 disclosure above | `body.html`, `direction.css`, `direction.js` | Four states in DOM order after Request; `data-home-sequence` reaches `complete` once; hover on states → `paused`, leave → `running`; identity row height constant across ready/running/paused/complete; `aria-live` polite only at completion |
| Act 5 Operate and compound | Reset Act 5 verbatim; unchanged | none | 7/5 lead paragraph | Link | Identical; identical | none | none | `Inspect the control model` → `/routes/trust/#permission` |
| Act 6 Partner and next move | Reset Act 6 verbatim; unchanged | none | 7/5 with two actions | Buttons | Identical; identical | none | none | Primary → `/routes/assessment/`; secondary → `/routes/company/` |

Word budget: today 497 (493 scoped + 4 unscoped labels); expected ≈503 (−4 labels, +8 invariants, +7 Request, −5 net state text, disclosure moved). Hard ceiling 520 (contract); target ≤500 per R6.

### 9.2 Transformation (`transformation/src/body.html`, `direction.css`, `direction.js`)

First-viewport contract: 1440×900 and 1024×768 — eyebrow, H1, lead, two actions, five-label strip; image beside (R3 = A) or below (R3 = B). 390×844 — eyebrow, H1, lead, actions, strip; image after the strip.

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| 1 Thesis hero | Contract Transformation 1 verbatim; **new strip labels** `Preserve` · `Simplify` · `Automate` · `Rebuild` · `Retire` (anchors to `#decide`) | Decision Field only: T-DF-01. R3 = A: mobile 4:5 asset in a 4:5 box beside the copy (7/5); R3 = B: desktop 2:1 below copy. `margin-top:-120px` removed | Copy, actions, index strip styled like `.workgraph-index` (mono meta, 48 px targets, one rule); one hero settle 1.5 s | Strip links focusable; buttons | RM: still; no-JS: still and strip | none (P copy) | `body.html`, `direction.css` | Five labels inside the first viewport at 1440×900 and 1024×768; no node overlaps the image; strip precedes image at 390 |
| 2 Division of work | Contract 2 verbatim; unchanged | none | 7/5 prose + `<dl>` ledger, coral term on `People` | none | Identical; identical | none | none | Four ledger rows readable |
| 3 Map operating reality | Contract 3 verbatim; unchanged | none | Copy + page disclosure + `<details>` folio (summary `Current path and accountable owner`, five fields progressive) + **provenance moved outside the details** | Details toggles by click, Enter/Space, tap | RM native; no-JS native (closed) — provenance visible regardless | Page disclosure before folio; `Illustrative operating reality map · constructed example` visible with folio closed | `body.html` (move line 71 after line 72) | Provenance `checkVisibility()` true with folio closed, JS on and off, 320–1536 |
| 4 Choose the intervention | Contract 4 verbatim; unchanged | none | Radiogroup continuum, sticky runway ≥1180 px fine pointer (`max(1040px,175svh)`), readout on Lift; closing line with sage rule | Pointer: scroll selects until a direct choice; keyboard: arrows; touch: tap | RM: all five explanations, no runway; no-JS: all five in order; **new:** below 1180 or coarse pointer, all five explanations rendered in order with the group still selectable | none | `direction.js`, `direction.css` | Forward Preserve → Retire and reverse at labelled positions on desktop; all five explanations visible at 390 and 768 without a tap |
| 5 Sequence the transition | Contract 5 verbatim; unchanged | none | H2 + body, `<details>` `Transition sequence` (six steps progressive), link, clarification | Details | Native; native | none | none | Link → `/routes/build/#factory-modes` |
| 6 Design for changing capability | Contract 6 verbatim; unchanged | none | 5/7 with sage boundary panel | none | Identical | `Future capability is a planning scenario…` default-visible | none | Boundary visible at all widths |
| 7 Next move | Contract 7 verbatim; unchanged | none | 5/7 close, primary button + text link | Buttons | Identical | none | none | Primary → `/routes/workgraph/#record`; link → `/routes/assessment/` |

### 9.3 WorkGraph (`workgraph/src/body.html`, `direction.css`, `direction.js`)

First-viewport contract: 1440×900 — eyebrow, H1, lead, both actions, page disclosure, record showing `WG-034 · Supplier payment exception`, `Decision retained` and at least `Owner — Finance owner.`; 1024×768 — same stacked or 5/7; 390×844 — eyebrow, H1, lead, disclosure, record identity and status inside 844 px, actions after the record.

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| 1 Position hero (recomposed) | Contract WorkGraph 1 verbatim; page disclosure `All artifacts on this page are constructed examples, not client data or production deployments.` moved here; record object copy per contract 2 (title `WG-034 · Supplier payment exception`, status `Decision retained`, provenance `Representative WorkGraph record · synthetic data`; default rows `Decision — Automate preparation. Preserve human approval for release.`, `Owner — Finance owner.`, `Permission — Prepare only. Never release.`; progressive rows `Evidence — Invoice and receipt disagree.`, `Operating state — Draft prepared; release withheld.`, `Reason…`, `Provenance…`, `History…` inside `Provenance and history`) | none in hero (image moves to §2) | 5/7: copy left, ink record right; lens controls JS-only (`aria-pressed`) | Lenses click/Enter/tap; record depth details | RM identical; no-JS: record complete, lenses hidden | Disclosure precedes the record; provenance line on the record | `body.html`, `direction.css`, `direction.js` (lens status only after click) | First-viewport contract at three widths; `Evidence`/`Operating state` not visible by default; lens status not written before interaction |
| Index band | `Context` · `Factory connection` · `Control` · `Learning` (contract local orientation); unchanged | none | Four anchors, 48 px targets | Links | Identical | none | none | Anchors resolve |
| 2 Context (record section) | Contract 2 H2 and two paragraphs verbatim; unchanged | Decision Field: WG-DF-OE-01 desktop/mobile pair moved here; one settle 1.45 s | 7/5 copy left, image right at ≥1280; stacked below | none | RM: still; no-JS: still | none | `body.html`, `direction.css` | Image `currentSrc` desktop ≥940, portrait <940; no crop loses the coral registration contact or sage field |
| 3 Lifecycle | Contract 3 verbatim (intro paragraphs default today; R7 may move paragraph 1 to progressive) | none | Steps in flow; record-state card sticky at ≥1180×720 beside steps, compact sticky above steps below; state = last step above the 45 % line; invariants `Owner — Finance owner.`, `Permission — Prepare only. Never release.` | Scroll only | RM and no-IO: resolved on `Learn`; no-JS: all four steps and labels | Record identity persists across states | none (protected FS2 carrier) | Connect → Decide → Build → Learn forward and reverse at labelled scroll positions |
| 4 Control and proportionality | Contract 4 verbatim; unchanged (`Technical diligence` details progressive) | none | 7/5 copy + sage boundary | Details; link | Native | Boundary `The depth of WorkGraph grows with the work it must govern.` default | none | Link → `/routes/trust/#permission` |
| 5 Next move | Contract 5 verbatim; unchanged | none | 5/7 close | Buttons | Identical | none | none | Primary → `/routes/build/#factory` |

Word budget: today ≈450; after moving two rows ≈438; R7 closes the last 8+ words to reach ≤430.

### 9.4 Build (`build/src/body.html`, `direction.css`, `direction.js`)

First-viewport contract: 1440×900 — eyebrow, H1, lead, action, page disclosure, stage rows `Approved intervention`, `Permission`, `Review state`; 1024×768 — same, stage may follow copy; 390×844 — eyebrow, H1, lead, action, disclosure, stage's first two rows inside the viewport.

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| 1 Position hero (recomposed) | Contract Build 1 verbatim; page disclosure moved above the stage; **Factory stage rows:** `Illustrative Factory build plan · not a client deployment` · `Approved intervention` — `Prepare the payment draft; preserve human approval for release.` · `Specification` — `Context — WorkGraph WG-034 and its approved-source set.` · `Tools — Read approved sources; prepare draft.` · `Release owner — Finance owner.` · `Permission` — `Prepare only. Never release.` · `Evaluation` — `Withhold when source records disagree.` · `Review state` — `Draft preparation passed evaluation; payment release remains prohibited.` · `Evidence return` — `Evidence returns to WG-034; the Finance owner retains release authority.` | Operational Evidence (coded stage); B-OE-MS-01 per R4 (omitted, or ≤⅓-height band above the rows) | 5/7: copy left; ink stage (14 px radius) right; coral rule on Approved intervention, sage rule on Review state; static | none | Identical; identical | Disclosure above the stage; provenance row | `body.html`, `direction.css` | First-viewport contract at three widths; disclosure precedes stage; stage static |
| 2 Two intervention modes | Contract 2 verbatim (post-FS4A); unchanged | none | Two-lane editorial field 5/7, rule divider | Link | Identical | none | none | Link → `/routes/workgraph/#record` |
| 3 Factory | Contract 3 verbatim; **paragraph 1 moves into** `Technical and reuse boundary` details; provenance `Illustrative Factory build plan · not a client deployment`, title `Factory modes · two constructed examples`, status `Ready for governed review`; plan rows and both resolved states unchanged | Operational Evidence (coded) + Machine Signal in the pass | Ink instrument: plan summaries with `Inspect automate plan` / `Inspect rebuild plan` (JS), plan detail, six-stage pass, `One governed capability, two surfaces` details | Plan buttons; Pause/Replay/Inspect; hover and focus pause | RM: resolved, `Inspect resolved progression`; no-JS: both plans, all rows, stages resolved, controls hidden | Provenance on the instrument; boundary `This is a product and architecture pattern…` | `body.html` | Pass: idle → running on sentinel; holds at Intervention and Evaluation; `Governed review complete`; Replay shown; hover pauses |
| 4 Trust rail | Contract 4 verbatim; unchanged | none | Light 5/7 rail on Lift | Link | Identical | `Illustrative operating record · constructed example` | none | Link → `/routes/trust/#permission` |
| 5 Operating choice and close | Contract 5 verbatim; conditional Impact link omitted; unchanged | none | Two typographic options; boundary; 5/7 close | Buttons | Identical | `Operating roles are defined per engagement…` | none | Primary → `/routes/company/`; link → `/routes/assessment/` |

Word budget: today 470; after −35 paragraph and +≈62 stage ≈497 (ceiling 500).

### 9.5 Trust (`trust/src/body.html`, `direction.css`)

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| 1 Position hero | Contract Trust 1 verbatim; unchanged | none | Copy-led full-width hero; two actions (`Inspect the control model` → `#permission`; `Start technical diligence` → mailto) | Buttons | Identical | none | none | mailto subject `Dagg technical diligence` |
| Control path band | `Constructed control path` · `01 Action withheld` — `Invoice and receipt disagree.` · `02 Permission` — `The agent may prepare, never release.` · `03 Accountable owner` — `Finance owner decides; the manual path remains available.` · state `Human decision recorded. Release withheld.` | Operational Evidence (coded) | Ink band, three columns ≥940, stacked below; coral rule under 01, sage under 03; one staggered settle | none | RM: resolved; no-JS: resolved | Provenance `Constructed control path` | `body.html`, `direction.css` | `Release withheld` and `Finance owner` visible without opening the record at 320–1536 |
| 2 Permission | Contract 2 verbatim; unchanged | none | 5/7 copy + five control fields | none | Identical | none | none | Five fields readable |
| 3 Evaluation and record | Contract 3 verbatim; unchanged (record inside `Inspect the full operating record` details) | none | Intro + page disclosure + details + OR-021 ink record | Details | Native | Page disclosure default; `Illustrative operating record · constructed example` on the record | `body.html` (hooks only) | Record opens with all eleven fields; provenance present |
| 4 Models and company control | Contract 4 verbatim; unchanged | none | 5/7 with sage boundary | none | Identical | Boundary default | none | Boundary visible |
| 5 Reversibility and diligence | Contract 5 verbatim; unchanged | none | 5/7 close; primary mailto; link → Build | Buttons | Identical | none | none | Link → `/routes/build/#factory` |

Add `data-copy-scope` to every visible Trust node (record contents progressive).

### 9.6 Company (`company/src/body.html`, `direction.css`)

| Section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| 1 Position hero | Contract Company 1 verbatim. R5 = A adds an accountability chain from three contract commitments verbatim: `Decision` — `Name what changes, what deliberately does not, who owns the outcome and what evidence would change the recommendation.` · `Build` — `Name the required context, tools, permissions, evaluations, approval and way back before release.` · `Escalation` — `Return material exceptions to an accountable owner.` | R5 = A: one narrow Decision Field seam (Codex 1:4 crop of the v2 asset) crossing the chain once; R5 = B: current v2 pair unchanged | R5 = A: three ruled rows on Paper; no cards, no icons; R5 = B: current hero | none | RM: still; no-JS: same | none (P method statements) | `body.html`, `direction.css` | R5 = A: first two chain roles inside 390×844; R5 = B: unchanged |
| 2 Point of view | Contract 2 verbatim; unchanged | none | 4/8 on Lift | Link | Identical | none | none | Link → `/routes/transformation/` |
| 3 What Dagg brings | Contract 3 verbatim with `Harness engineering` → `AI system engineering` (R2) | none | 2×2 ruled ledger, no cards | Links | Identical | none | `body.html` | Label changed; two links resolve |
| 4 Partnership standard | Contract 4 verbatim; summary and details labels unchanged; if R5 = A the details keeps `Confidentiality`, `Non-negotiable` and the boundary | none | Ink 5/7; `<details>` with `align-self:start`; closed row 64 px with its rule on the summary | Details | Native | Boundary `…no residency, retention, encryption or isolation assurance is implied here.` | `direction.css`, `body.html` | Closed details height 64 ± 4 px at 1440; link `Inspect the permission model` → `/routes/trust/#permission` |
| 5 Accountability and close | Contract 5 verbatim; unchanged | none | Leadership rows; close with primary and mailto | Buttons | Identical | Titles V before publication | none | Names unchanged; mailto subject `Dagg partnership` |

### 9.7 Assessment (unchanged in FS5; Codex adds hooks) and Impact (unchanged; robots meta in FS6)

| Route · section | Copy | Image | Component · interaction | Input | RM / no-JS | Credibility | Owner | Acceptance |
|---|---|---|---|---|---|---|---|---|
| Assessment 1 hero + scope card | Contract Assessment 1 verbatim | Operational Evidence coded scope card | 7/5, ink card `One consequential path.` / `Not the whole company.` | Button → `#inquiry` | Identical | none | Codex (hooks) | Card in first viewport at 1440 and 390 |
| Assessment scope band | four items + `See what you leave with` → `#deliverable` | none | 7/5 band | Button | Identical | none | Codex | Anchor resolves |
| Assessment 2 Fit | Contract 2 verbatim | none | 5/7 lists on Lift | none | Identical | none | Codex | — |
| Assessment 3 Process | Contract 3 verbatim | none | five-column sequence ≥768, vertical below; sage boundary | none | Identical | `Do not send confidential information in the first inquiry.` | Codex | — |
| Assessment 4 Deliverable | Contract 4 verbatim | none | Ink 5/7 Decision Pack | none | Identical | `The assessment is a decision instrument, not a commitment to build.` | Codex | — |
| Assessment 5 Inquiry | Contract 5 verbatim incl. consent, validation messages, success and error copy | none | Form hidden until JS; validation; 450 ms preview reveal; `<noscript>` mail path | Enter/click submit; first invalid field focused | RM: 0 ms reveal; no-JS: form hidden, noscript visible | `This local preview has not sent any data…` | Codex | All five `aria-invalid`; status text; zero outbound requests |
| Impact 1–5 | Contract Impact verbatim | none | Editorial; ink evidence chain; truthful empty slot | Buttons | Identical | `Approved proof · none published`; `Internal staging route · not published` | Codex | Absent from nav and footer; noindex |

### 9.8 Shared chrome (Codex)

Header, footer and skip link are assembled from `shared/chrome/*` and remain unchanged in FS5 except wording per R9 (FS6). Behavior table in §5.2. Acceptance in §10 (flyout, sheet, links, `aria-current`).

---

## 10. Fail-closed acceptance gates (Codex runner, then Fable)

**Commands.**
```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B tools/capture_fs5_evidence.py --output evidence/FULL-SITE-STAGING/FS5 --port 0
DAGG_FS5_EVIDENCE_DIR=evidence/FULL-SITE-STAGING/FS5 PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_fs5_candidate.py' -v
```
The runner writes to a temporary sibling, validates completeness and hashes, and promotes atomically. A failed or partial run is preserved as `.failed-<snapshot>-<timestamp>` and never replaces a passing package. Any missing capability, mixed snapshot, throttled timer, hidden document, unsupported input mode, missing screenshot or lost browser event is a rig failure, not a warning. Each route/mode opens in a fresh browser target.

| Gate | Method | Threshold | Output |
|---|---|---|---|
| Snapshot identity | `/__revision`, page meta, response headers, byte comparison of every candidate path served vs disk | one ID everywhere; 0 differing files | `revision.json` |
| Rig preconditions | `document.visibilityState`, a 200 ms timer, `devicePixelRatio`, CSS viewport size | visible; timer ≤250 ms; requested CSS viewport exactly achieved | `environment.json` |
| Visual regression | Home hero region at 1440×900, 1024×768, 390×844, 1536×1024 vs frozen FS4 first-viewport captures and the founder reference | ≤0.5 % differing pixels | `screenshots-manifest.json` |
| Viewports | Full-page and first-viewport captures for 8 routes at 320×720, 360×800, 390×844, 768×1024, 1024×768, 1280×720, 1366×768, 1440×900, 1536×1024 | `scrollWidth === clientWidth`; every capture stamped with the snapshot ID | `route-matrix.json`, screenshots |
| First-viewport contracts | DOM geometry of the §9 nodes at 1440×900, 1024×768, 390×844 | every listed node fully inside the viewport | `route-matrix.json` |
| Type and layout | computed font sizes, gutters, field width, splits at each viewport vs §5.1 | within ±0.5 px; H1 ≤2.5 lines desktop except Build (≤4 by map) and Home (2 at 92 px) | `route-matrix.json` |
| Rhythm | section heights per route; anchor gaps | tallest/shortest ≥2.5×; no empty gap >60 % viewport without a semantic object; ≤3 ground changes | `route-matrix.json` |
| Structure | one header/main/footer; one H1; no heading skip; no duplicate ID; landmarks named | zero violations | `route-matrix.json` |
| Links and anchors | every `href` and fragment; every visible `Start an assessment`; no Impact link while gated; `aria-current` | all resolve; zero placeholders | `anchors.json` |
| Desktop flyout | pointer intent open, leave close, Enter/Space, Tab through four destinations with inset change, Escape with focus restore, closed panel unfocusable | open ≤120 ms after 70–100 ms intent; close 180–280 ms; states as listed | `interactions.json` |
| Mobile sheet | real touch at 390×844 and 768×1024: open/close, `aria-expanded`, inert main and footer, scroll lock, focus containment, Escape layering, focus restore to the menu control | all true | `interactions.json` |
| Copy | §10.4 method per route; every visible sentence matches the amended contract or reset; forbidden terms absent; disclosure precedes first synthetic identifier; headline-only story unchanged | bands met; 0 unmatched sentences; 0 forbidden terms | `route-matrix.json` |
| Accessibility | axe-core per route and per state (menu open, flyout open, record open); targets; focus rings; min font; contrast pairs | 0 critical/serious; ≥44 px (48 nav/Assessment); ring visible; ≥12 px | `resilience.json` |
| 200 % zoom | 1280×900 physical with verified 640×450 CSS viewport | no overflow; H1, primary CTA, navigation, footer, route controls, Assessment fields and confirmation reachable | screenshots + `resilience.json` |
| Keyboard and touch traversal | full Tab traversal and touch traversal per route | every control reached once; hidden states never focusable | `interactions.json` |
| Home motion | start on ≥35 % visibility; 1.6+2.2+2.2 s; stop on state 4; hover and focus suspension; explicit Pause authoritative; Replay after completion only; no hover pause on touch | timings within ±150 ms | `interactions.json` |
| Factory pass | finite 6–8 s; two holds; Pause/Replay; hover and focus suspension; Inspect under reduced motion | as listed | `interactions.json` |
| Carriers | WorkGraph and Transformation forward and reverse at labelled scroll positions; Transformation all five explanations visible below 1180 and on coarse pointer | as listed | viewport-sized captures + `interactions.json` |
| Reduced motion | emulated `prefers-reduced-motion: reduce`, fresh target | every route resolved immediately; no timed control offered; no hero settle | `resilience.json` |
| True no-JS | scripting disabled, fresh target; DOM snapshot, accessibility tree, screenshot, `<noscript>` content | all copy and states in source order; no inert controls; routes reachable; Assessment mail path visible | `resilience.json` |
| Missing-enhancement script | block `component-library/script.js` and each `direction.js` separately | page complete and legible | `resilience.json` |
| Form truthfulness | empty submit; valid synthetic submit inside the runner | all fields `aria-invalid`; first message announced; focus on first field; confirmation appears; zero outbound requests during the whole flow | `assessment.json` |
| Console and network | request-ID ledger to network idle; console API, exceptions, log entries | 0 exceptions; 0 errors; 0 failed or ≥400 responses; 0 remote requests | `failures.json` |
| Performance | per route: transfer size, `currentSrc`, intrinsic dimensions, LCP, CLS at 1440 and 390 | hero ≤300 KB mobile / ≤500 KB desktop; LCP and CLS reported in FS5, gated in FS6 | `performance.json` |
| Silhouette distinctness | grayscale first-viewport thumbnails of seven routes at 1440 and 390 | Fable judges all seven distinguishable | Fable verdict |
| Independent acceptance | Fable reviews the promoted package against the same snapshot ID; verdict beside, never inside | no P0/P1 | `FS5/FABLE-ACCEPTANCE-<date>.md` |

### 10.4 Copy counting method

Count words in text nodes whose nearest ancestor with `data-copy-scope` is `default` or `progressive`; nested scopes count once at the outermost; exclude `hidden`, `aria-hidden="true"`, visually-hidden utility classes, `<script>`, `<style>` and the shared header/footer; hyphenated terms count as one word; the first-section figure counts default copy inside the first `<section>`. Report default, progressive and first-section per route with the snapshot ID.

---

## 11. Launch blockers versus later publication items

**Launch blockers (inside FS5 and its evidence).** P1-1, P1-2, P1-3 · Home hover/focus suspension and reduced-motion Replay · Trust default exception/result · Company details stretch · WorkGraph and Build first-screen proof · Transformation provenance and touch reach · all eight routes measurable and within band · every §10 gate on one snapshot · Fable acceptance.

**FS6 publication package (before Christian's launch gate).** Base-path substitution and canonical routes, sitemap, canonical and social metadata · Privacy and Terms with approved legal text and footer links · Assessment endpoint, delivery, error state, spam protection, retention, privacy copy · fonts subset within two files ≤160 KB · specimen CSS/JS split · static robots meta for Impact · hero preload · header and menu wording per R9 · leadership titles verified · production performance gates and platform smoke tests · Impact publication gated on one permissioned proof (business decision).

---

## 12. R1–R10 — RESOLVED DEFAULTS, and the activation verdict

**Gate ownership.** Christian has delegated safe copy, terminology, layout and acceptance decisions. The only founder gates are a materially different design-world direction and final launch, publish or canonical promotion. Every item below is therefore a resolved default owned by Codex: Codex records it in the FS5 text and executes it; no approval is requested.

**Verdict.** FS5 as drafted is not sufficient; FS5 as specified in §9 is. Activation condition: Codex records R1–R10 in the FS5 text and reconciles the authority files — `FULL-SITE-CONTENT-CONTRACT.md`, `HOME-NARRATIVE-FOUNDER-RESET.md` and the page maps — to §9. When both are done, FS5 is active for one bounded writer with the file list in §8.2 and the rules in §8.4. Publication, deployment and canonical promotion remain forbidden without Christian's explicit launch approval.

**R1–R2 — copy and terminology (binding)**

| # | Item | Resolved default | Why |
|---|---|---|---|
| R1 | Home Acts 3–4: amend `HOME-NARRATIVE-FOUNDER-RESET.md` with the exact WG-034 copy and the disclosure-order rule in §9.1 | Approved | Closes P1-3 and makes Home's proof concrete; the reset remains the sole Home copy authority once amended |
| R2 | Public label `AI system engineering` replacing `Harness engineering` | Approved | Removes unexplained Dagg vocabulary from the Company capability list |

**R3–R10 — composition, budget and rig (binding)**

| # | Item | Options | Resolved default |
|---|---|---|---|
| R3 | Transformation first viewport | A: 7/5 hero with 4:5 image and five-label strip · B: full-field image plus strip | A |
| R4 | Build hero image | A: omit from first screen · B: ≤⅓ framing band above the coded stage | A |
| R5 | Company opening | A: accountability chain from three contract commitments plus narrow seam crop · B: keep hero, fix details and label only | A |
| R6 | Home default-word ceiling | A: enforce ≤500 and name the trim · B: accept contract ceiling 520 | B for FS5, A revisited in FS6 |
| R7 | WorkGraph trims beyond the two record rows | A: move lifecycle intro paragraph 1 into a native disclosure with a contract-approved label · B: accept ≈438 and amend the band to 320–440 | A, label supplied by Codex |
| R8 | Home reduced-motion control | A: hide Replay · B: relabel to an instant inspect control | A |
| R9 | Header wording | A: change flyout descriptions, fourth label and menu labels to the contract · B: amend the contract to the header as built | B (the built copy is stronger), record in the contract |
| R10 | Runner scope | Adopt §10 including the 1536×1024 frame, rig preconditions, served-vs-disk assertion, Escape layering expectation, silhouette gate | Adopt |

Sequence: Codex records R1–R10 → Codex amends the contract, the reset and the maps to §9 → Fable reconciliation read (one pass) → FS5 active for one bounded writer → §8.5–8.6 evidence and acceptance → FS6 → Christian's launch gate. Nothing before the launch gate publishes, deploys or promotes canonical routes.

---

## 13. Risk register

| Risk | Signal | Mitigation |
|---|---|---|
| Writer invents copy or design to fill a gap | any sentence not in §9 | §8.4 rule; runner copy gate fails closed |
| Word bands exceeded by the new objects | ledger over band | R6/R7 recorded before writing; writer reports counts |
| Evidence rig passes on a hidden or throttled tab | `visibilityState` or timer check | rig precondition gate |
| Snapshot drift between disk and served | ID mismatch | served-vs-disk byte assertion; re-freeze before capture |
| Home hero regresses while other routes change | pixel diff >0.5 % | visual regression gate against frozen baselines |
| Reduced-motion or no-JS regressions unseen | emulation missing | fresh-target emulation gates; missing capability = rig failure |
| Company chain or Transformation split creates a new template | grayscale thumbnails converge | silhouette gate; Fable judges explicitly |
| Impact stays empty at launch | no permissioned proof | business decision tracked outside design; site remains truthful |

---

## Appendix A — Contract divergences found (authority ↔ source)

| Authority | Source | Divergence |
|---|---|---|
| Evidence ledger required labels; Transformation map §7 | `routes/transformation/src/body.html` 62–72 | Provenance inside closed disclosure (P1-2) |
| Home reset Acts 3–4; ledger disclosure order | `home/src/body.html` 63–74 vs 94 | Record before disclosure; identity duplicated (P1-3) |
| Contract §4 Build disclosure (128–140) | `shared/chrome/header.html` 75–76, 90–91, 105–106, 119–120 | Four descriptions and the fourth label differ |
| Contract §4 footer groups (154–155) | `shared/chrome/footer.html` 41–46 | Privacy and Terms absent |
| Contract menu controls (1571–1576) | `header.html` 44–45 | `Menu`/`Close` |
| Contract link table (Build → /build) | `header.html` 66–70 | Build is a `<summary>` |
| Contract Trust 1 (1265–1280) | `routes/trust/src/body.html` 24–30 | Non-contract instrument copy |
| Contract §4.1 Trust default | `trust/src/body.html` 60–81 | Exception and result progressive only |
| Contract §4.1 WorkGraph budget | `routes/workgraph/src/body.html` | ≈450 default words |
| Contract motion control `Pause animation` | `home/src/body.html` 99; `build/src/body.html` 135 | `Pause sequence` |
| Foundations p.07 H1 68 px at 1440 | `transformation/src/direction.css` 88–91 | 63.36 px at 1440 |
| FS0 §3.5 hover/focus pause | `home/src/direction.js` | Absent |
| WorkGraph, Build, Trust, Company, Home maps | current sources | Maps predate FS2/FS4A; no current Home map |
| FS4 §3 `One material path.` | `assessment/src/body.html` 17 | Source follows the contract `One consequential path.`; FS4 text is wrong |

## Appendix B — Sources and evidence inspected

Authority: `CLAUDE.md`; masterplan (all 1303 lines); FS0, FS1, FS2, FS3, FS4, FS4A, FS4B, FS5 draft; FS3 and FS4 implementation reports; FS3 visual QA; GOAL-COMPLETION-MATRIX; FULL-SITE-CONTENT-CONTRACT; HOME-NARRATIVE-FOUNDER-RESET; EVIDENCE-LEDGER; PEER-BENCHMARK, FULL-SITE-CONTRACT-AUDIT, both CLAUDE narrative reviews; P4R2, P4R4 addendum, P4R5B; IMAGE-PRODUCTION-PROTOCOL; IMAGE-LIBRARY-CATALOG; HOME-HERO-SELECTED-V4-PROMPT; FS3 founder visual reference; all ten page maps; ANTHROPIC-OPENAI, PALANTIR, FRONTEND-INTERACTION-STACK, INTERACTIVE-PRODUCT-WORLDS, XAI-CURRENT audits; `design/DESIGN-LANGUAGE.md`, `design/MEASURED.md`, `design/TEMPLATE.md`, `design/VELOCITY.md`. Visual authority: extracted texts plus every page image — Foundations 1–15, Image Language 1–14, Component Library 1–17. Read directly, read-only, on 2 September 2026 with `pdftotext -layout` (all pages; page images not rendered): `/Users/christianperez/Downloads/About-Insight-Pitch-Deck-v1.pdf` (19 pages) and `/Users/christianperez/Downloads/About-Insight-Brand-Design-System-v0.1.pdf` (18 pages).

Source: all `src/body.html`, `direction.css`, `direction.js`, `meta.json` for home and the seven routes; `shared/chrome/{header.html,footer.html,chrome.css,chrome.js}`; `component-library/{styles.css,script.js}`; `tokens.css`; `tools/build_golden_standard_previews.mjs`; `tools/serve_preview.py` acquisition.

Rendered evidence: `FS4B/reference/home-founder-selected-1536x1024.png`; `FS4B/home-selected-hero-1440x900.png`; `FS4B/rendered/desktop/{assessment,build,company,flyout-factory,flyout-overview,transformation,trust,workgraph}-1440x900.png`, `home-1440x900.jpg`, `home-first-viewport-1536x1024.png`; `rendered/tablet/{assessment,build,company,transformation,trust,workgraph}-1024x768.png`, `home-1024x768.jpg`; `rendered/mobile/{assessment,build,company,mobile-menu-open,transformation,trust,workgraph}-390x844.png`, `home-390x844.jpg`; `snapshot-6ef754faf00f/{desktop,tablet,mobile}/*-first-*.jpg` (21), `states/transformation-rebuild-after-scroll-1440x900.jpg`, both contact sheets.

Live runtime on `127.0.0.1:8933`: Home, Transformation, WorkGraph, Build, Assessment, Company, Trust, Impact.

## Appendix C — Test-environment artifacts versus site defects

Artifacts, not defects: the automation tab reported `document.visibilityState === "hidden"` for much of the session, which pauses `requestAnimationFrame` and IntersectionObserver delivery and throttles timers — hence the Home sequence staying `ready` after scrolling, lagging carrier reads and untimeable hover close-grace; `resize_window` did not honor 1440×900 or 390×844 (viewports came back 1483–1530 wide, 527 at narrowest), so exact 1440 and 390 runtime values come from the frozen captures and `FS4-ROUTE-MATRIX.json`; Chrome starts Tab navigation from the last click point, which invalidated the first keyboard run; mobile-sheet steps used scripted clicks. Confirmed independent of environment: P1-2 and the Trust hidden exception (`checkVisibility`), P1-3 (DOM order), Company details stretch (geometry), Home control-swap reflow (two screenshots), type sizes (computed style), copy and contract items (static text), P1-1 (file mtimes), fonts and CSS payload (file sizes), snapshot identity (hash comparison).

## Appendix D — Type formulas (from `design/golden-standard/system/tokens.css`)

`--fs-h1: clamp(42px, min(32.857143px + 2.857143vw, 35.085714px + 2.285714vw), 68px)` · `--fs-h2: clamp(34px, min(24.857143px + 2.857143vw, 30.057143px + 1.523810vw), 52px)` · `--fs-h3: clamp(26px, min(21.428571px + 1.428571vw, 25.142857px + 0.476190vw), 32px)` · `--fs-lead: clamp(19px, min(14.428571px + 1.428571vw, 18.885714px + 0.285714vw), 23px)` · `--fs-body: clamp(17px, 16.628571px + 0.095238vw, 18px)` · `--fs-meta: clamp(12px, 11.628571px + 0.095238vw, 13px)`. Home H1 override: `clamp(54px, 6.1vw, 92px)` (≥640) and `clamp(48px, 14vw, 62px)` (<640). Transformation H1 override ≥940: `clamp(54px, 4.4vw, 68px)`. Gutters 20/24/48/72 at <768/768/1024/1440; column gap 24/32 at <1024/≥1024; section rhythm 88·64 / 112·88 / 160·112 at <768/768/≥1024.
