# P4R4 — Claude design-partner review

Reviewer: Claude session (active)
Date: 2026-08-31
Scope: answers to P4R4-HOMEPAGE-RESET-BRIEF §7 + measured evidence report on the current
`preview/golden-standard/p4r4` rendering.
Files changed by this pass: this file only. No page, system, portfolio or masterplan file touched.

---

## Part 1 — Failures first (measured, current p4r4 revision)

Served from repo root at 1527×1909 and via same-origin iframes at 375 and 305 CSS px.

### F1 — BLOCKING. The hero shows 60% of the master. The protected chain is cut at both ends.

`home-hero-operating-model-v1.png` is 1586×992 (aspect 1.60). The rendered box is 498×520
(aspect 0.96) with `object-fit: cover; object-position: 51% 50%`.

Measured consequence: **324 px cropped from the left, 312 px from the right — 40% of the width gone.**

The protected event is: unresolved graphite paths → one coral decision → fewer exact ink paths →
translucent sage boundary. In the master, the wandering paths originate around x≈0–740, the coral
lozenge sits at x≈830 (sampled `#b7593d`), the resolved ink lines run x≈900–1050, and the sage
field occupies x≈1020–1586. The crop therefore removes the *origin* of the disorder and most of the
*governed field it resolves into*, leaving a middle fragment in which "fewer exact ink paths"
survives as roughly 30 px of horizontal space.

This directly violates SLICE §5: "Do not center-crop away any part of that chain."

The asset is not the problem — it is the strongest thing in the project and it reads without a
caption at full width. The container is the problem.

### F2 — BLOCKING. The hero caption carries the meaning the image is supposed to carry.

Rendered: `HUMAN JUDGMENT — redirects company context into a governed operating path.`
Rejected P4R3-A rendered: `A material decision redirects an exact system toward a governed state.`

Same crutch, reworded. Gate §10.2 says stop if the hero asset needs its caption to explain what
happened. Note the causal order: the caption is *needed* here only because F1 removed the evidence.
Fix F1 and the caption can become a provenance line rather than an explanation.

### F3 — H1 wraps to four lines at every viewport tested.

| Viewport | H1 size | Lines | Column |
| --- | --- | --- | --- |
| 1527 | 68 px | 4 | 459 px |
| 375 | 44 px | 4 | — |
| 305 | 40 px | 4 | — |

BRIEF §6 sets a maximum of two desktop lines; SLICE §7 sets 2.5. Desktop is a real fail: four
53-character lines in a 459 px measure reads as a stacked list, not a conclusion.

Mobile is a contract error rather than a render error — four lines of 44 px is correct on a phone.
Recommend §7 be reworded to bind desktop only.

### F4 — The hero is a slide floating in a frame.

Section height 1650 px containing roughly 380 px of content: ~330 px of empty ground above the
eyebrow, ~340 px below the buttons. It satisfies "0.85–0.95 viewport" (0.86) only because this
window is 1909 px tall — the ratio is being met by scaling emptiness, so on a 900 px laptop the
same rule produces a different composition. Recommend the hero be bound by content and a fixed
ceiling, not by viewport fraction.

### F5 — No art-directed mobile crop. At 390 the hero asset is destroyed.

Rendered box at 375 px: **335×1024, aspect 0.33.** A 1.60 landscape asset in a 0.33 portrait slot
shows roughly 21% of the master's width. It reads as a soft grey band with no legible event.
SLICE §7 requires an art-directed mobile crop; there is none — the same `cover` rule is simply
letting a portrait box eat a landscape image.

### F6 — Non-blocking, for Codex to confirm in P3 chrome (outside my write scope)

Four links inside the Build disclosure have live layout rects (y≈103–235) and `tabIndex >= 0` while
`innerText` is empty. This *may* violate SLICE §7 "Hidden states are not focusable." I could not
confirm it: three of my selectors into the shared chrome matched the wrong element, and §9 forbids
me changing that code. Treat as a lead requiring a keyboard-order check, not a confirmed defect.

---

## Part 2 — What passes

| Check | Result |
| --- | --- |
| Document horizontal overflow | None at 1527, 375, 305 |
| Section height ratio | 1720 / 300 = **5.7** — matches measured Anthropic /company exactly |
| Visible Home word count | **406** (43·19·50·75·71·96·52) — inside the 350–500 gate |
| First-viewport words | 43 — inside the 50 gate |
| Grounds per page | One page ground `#F0EEE6` + two `#FAF9F5` lifts + one ink section |
| Body copy, mobile | **20 px** at 375 and 305 — clears the ≥17 px rule |
| Mobile navigation | Collapses to a working `Menu` disclosure; 11 visible links |
| Mobile reading order | Unchanged from desktop |
| Hero resolve animation | Runs once and cleans up: on a clean load the figure carries no state class and `filter: none` |
| Console errors | None observed |

Two corrections to my own first reading, recorded because they were wrong and could have wasted
Codex's time: I initially reported the hero resolve as stuck mid-transition (it is not — my own
replay probe had re-added the class), and I initially measured a 12 px hero lead (wrong element;
all real body copy is 20 px).

---

## Part 3 — Answers to BRIEF §7

### 1. The three deepest causes of P4R3's failure

**Cause 1 — the image languages were promoted from roles to identities.** A, B and C each inherited
a whole world from a single asset, so the asset chose the argument instead of serving it. B became a
dark machine company; C became a hardware brand. The correction in SLICE §2 is right, and it is the
only one of the three causes the package currently fixes.

**Cause 2 — every direction states a claim, shows a picture of the claim, then captions the
picture.** Three layers carrying identical information means none is load-bearing, and the reader
correctly reads the image as decoration. An image earns its place only by carrying something the
sentence beside it does not say. This cause is *not* yet fixed: F1 and F2 above are it, recurring.

**Cause 3 — no section was allowed to be the bearer.** Measured Anthropic /company puts 544 of
1015 words in one section — a 5.7 height ratio and deliberately unequal weight. All three P4R3
directions distribute weight evenly across panels, and evenly-weighted panels *are* what slides
are. A website earns its scroll by making one section obviously the argument and the rest its
approach and consequences. p4r4 now hits 5.7 on height, which is real progress, but its word
distribution is still flat: 43·19·50·75·71·96·52, where the largest section carries 24% of the
words. Anthropic's bearer carries 54%.

### 2. What Home should borrow from the peers, and what it should refuse

**Borrow one thing: Anthropic's single bearing section** — deliberately unequal weight, one section
carrying roughly half the page's words and height, everything else short. It is the specific
structural property that separates a page from a deck, and it is measurable, so it can be verified
rather than argued about.

**Borrow one more, from OpenAI: the mechanism arrives before the prose.** On openai.com/about the
reader meets behaviour with very little preamble. Dagg's equivalent is that WorkGraph and Factory
should be reachable and inspectable early, not introduced by a paragraph first.

**Refuse: the full-bleed atmospheric opening that all four peers use.** Dagg's hero asset is an
argument with a left-to-right causal reading order, not an atmosphere. A bleed or a square crop
destroys it — which is precisely F1. It needs a measured, wide column with its whole width intact.

**Refuse: xAI's rotating-word theatre and Palantir's cinematic darkness.** Both are brand mood
substituting for a claim. And refuse Anthropic's essay register: Dagg is offering a decision, not
publishing a paper.

### 3. Hero thesis — three candidates, one selection

**A (currently frozen): "Build the company AI makes possible."**
Six words, genuine aspiration. Two problems: the verb belongs to the client, so Dagg disappears
from its own headline; and it wraps to four lines at 68 px (F3).

**B: "Decide what the company becomes."**
Five words. Puts judgment first, which is what Dagg sells before any build. Crucially it is the only
candidate the hero asset *independently proves* — the coral lozenge is a decision, and the image's
whole event is a decision redirecting a path.

**C: "The operating model is the product."**
The sharpest thesis of the three, and closest to the real insight. But it is an essay title: it
states a belief instead of offering the reader a move, and it invites the reader to agree rather
than to act.

**Selection: B.** The tradeoff: B gives up A's emotional lift and C's intellectual flex, and it is
the least quotable of the three. It wins because its subject is Dagg's actual act and because the
hero image demonstrates it without a caption — which is the one property gate §10.2 tests, and the
one both P4R3-A and the current p4r4 fail. It also fits two lines at 68 px in the existing measure.

If the frozen copy stays as A, then A must be reset at 56–60 px or given a wider column so it
occupies two lines, and the caption must stop explaining the picture.

### 4. The seven Home macrosections

| # | Conclusion-led heading | One supporting sentence | The one visual / mechanism job |
| --- | --- | --- | --- |
| 1 | Decide what the company becomes. | Dagg sets the operating direction, then builds the systems that carry it. | The hero asset at full width: disorder → one decision → fewer exact paths → governed field. Still, with one finite resolve. Proves the thesis without a caption. |
| 2 | The operating gap compounds. | Machines execute continuously; companies still slow wherever context and decisions are rebuilt by hand. | No image. Typographic punctuation only, 240–360 px. |
| 3 | Technology follows the operating decision. | We map how work moves, then decide what to preserve, simplify, automate, rebuild or retire. | The five outcomes as one interactive continuum — the reader operates the judgment rather than reading about it. No bitmap. |
| 4 | **Company context should outlast the model.** *(bearer)* | WorkGraph keeps workflows, decisions, ownership and evidence usable across strategy, build and operation. | A coded, inspectable record: selecting a source changes one record in place. This section should carry ~45–50% of the page's words and height. |
| 5 | The decision becomes a working system. | Factory turns the justified intervention into governed agents or software with the permissions and evaluations it needs. | A contained instrument, all stages present without JS. Operational Evidence framing may surround it; it may not pretend to be a live deployment. |
| 6 | AI-native changes the company inside and out. | Agents carry bounded internal execution; the same governed capability can meet customers where they already work. | One carrier, two user-selected states. No second bitmap. |
| 7 | Start with the decision, not the build. | Trace one material path and leave with a recommendation, an accountable owner, and the evidence that would change it. | Ink close. A small Decision Pack preview — the bill of materials and the threshold rule, never an amount. |

The one structural change I would make to the frozen set: **section 4 must become the bearer.**
Today all seven are roughly equal, which is cause 3 above.

### 5. Image-language placement matrix

| Section | Language | Max density | Moment type |
| --- | --- | --- | --- |
| 1 Hero | Decision Field only | one carrier, 6/12 columns, full 1.60 aspect preserved, 460–520 px tall | finite motion — one coarse→resolved pass ≤1.2 s, then hold permanently |
| 2 Stakes | none | zero bitmaps | still (type only) |
| 3 Transform | Decision Field *through interaction* | no bitmap in V1 | coded interaction, 240 ms response |
| 4 WorkGraph | Decision Field framing + Operational Evidence record, kept visually separate | frame ≤4/12; record ≤8/12 | coded interaction |
| 5 Factory | Operational Evidence, contained | instrument ≤8/12; no full-width dark world | finite resolution, then hold |
| 6 Two surfaces | Operational Evidence | ≤8/12, no additional bitmap | user-controlled state change only |
| 7 Assessment | none | zero bitmaps | micro response only |

Machine Signal appears **once**, and only as the resolve inside section 1's carrier. It is never a
page world and never a second section's language. No section uses more than two languages; no two
image-heavy sections sit in sequence; at most one dominant media object per viewport.

### 6. Production brief — hero asset

**My recommendation is not to regenerate the desktop master.** `home-hero-operating-model-v1.png`
is correct and it reads without a caption at full width. F1 is a container fault: change the box to
preserve the 1.60 aspect (6/12 columns at roughly 620×390) and the asset needs no reissue. Issuing
a new desktop master would hide a layout bug behind an image change.

**A new asset genuinely is required for mobile,** because no crop of a 1.60 landscape survives a
0.33 portrait slot (F5). Brief for that variant:

- Output 1200×1600 (3:4 portrait), same paper, same physical staging, same light.
- Recompose the identical causal chain **vertically, top to bottom**: four or five wandering,
  smudged graphite paths entering at the top edge; converging at a single terracotta lozenge
  (`#b7593d`) at roughly 45% height; emerging below as three or four clean, exact ink lines;
  passing beneath a translucent sage boundary that occupies the lower third and runs off the
  bottom edge.
- The disorder must be visibly *doubled and uncertain* — smudge, graphite dust, corrections — so
  that the resolution below it is legible as an improvement.
- Every link in the chain must be complete inside the frame. Nothing may depend on a crop.
- Forbidden, explicitly: circuit boards, tubes, glass vessels, cables, chips, screens, interfaces,
  dashboards, charts, arrows, glow, lens flare, neon, gradients, particle fields, generic AI waves,
  human hands, faces, people, logos, text, numerals, brand marks.
- Exactly two accent hues: the terracotta and the sage. Everything else is paper and graphite.
- Deliver as PNG, then `cwebp -q 82 -resize 1200 0` for the page.

### 7. Five conditions under which I stop rather than show Christian another weak slice

These are mine, and deliberately not restatements of §10:

1. **I have not looked at the rendered page at full size with my own eyes.** Every serious failure
   in this project came from reasoning about code instead of looking at output. A passing test suite
   is not a substitute for the screenshot.
2. **A claim in the copy is not demonstrated by the thing next to it.** If a sentence says Dagg
   builds working systems and the adjacent object is a picture rather than a mechanism, the page is
   asserting rather than proving, and the reader will discount everything else on it.
3. **An image needs a caption to be understood.** Then the image is not carrying information and
   should either be recomposed or removed. A caption may state provenance; it may not state meaning.
4. **The page's weight is evenly distributed.** Equal panels are the signature of slides. If no
   single section obviously carries the argument, no amount of typography will fix the impression.
5. **A number or amount has appeared anywhere on the page,** or a client, engagement or metric is
   identifiable. This is absolute and non-negotiable, and it is the one condition where I stop
   without discussion.

I would add a sixth in practice: **if I find myself tuning a percentage against a preview that does
not yet contain all seven sections,** I am optimising a proxy and should stop and build the missing
sections first.

---

## Part 4 — Evidence report (SLICE §11)

- **Revision reviewed:** working tree, `preview/golden-standard/p4r4/` untracked
  (index.html 21437 B, styles.css 18388 B, script.js 7408 B).
- **Files changed by me:** `evidence/P4R4/CLAUDE-REVIEW.md` only. p4r4 remains untouched — verified
  by `git status`.
- **Method:** served the repo root over HTTP so the absolute asset paths resolve (they 404 under
  `file://`); rendered in a real Chrome session; measured with `getComputedStyle`,
  `getBoundingClientRect`, and canvas pixel sampling of the hero master; tested 375 and 305 CSS px
  through same-origin iframes because macOS silently refuses window widths below ~485 px and reports
  success anyway.
- **Viewports:** 1527×1909, 375, 305. **Not yet tested: 1440, 1024, 768, 360.**
- **Interaction states tested:** hero resolve on clean load (runs once, cleans up); nav hit-testing
  (no interception); mobile nav disclosure (collapses to `Menu`, 11 links visible).
  **Not tested: Build flyout hover intent and Escape, decision continuum, WorkGraph source
  selection, Factory stages, impact modes, no-JS, reduced motion.**
- **Console:** no errors observed.
- **Overflow:** no document-level horizontal overflow at any viewport tested.
- **Copy counts:** 406 visible words; first viewport 43; H1 6 words; all section leads one sentence.
- **Peer comparison verdict:** height rhythm now matches Anthropic (5.7). Word distribution does
  not — Dagg's largest section carries 24% against Anthropic's 54%. Structurally this is the last
  thing standing between p4r4 and "not slides."
- **Recommendation:** do not show Christian this revision. F1 and F2 are one fix — give the hero
  asset its full width and the caption stops being load-bearing. F3 and F4 are layout. F5 needs the
  portrait asset in §6 above. None of these require another style direction.


---

## Part 5 — Addendum pass (P4R4-CHRISTIAN-AUTHORITATIVE-ADDENDUM, read after Parts 1–4)

I had not read the authoritative addendum when Parts 1–4 were written. It is binding and it adds
three findings and one confirmation.

### F7 — BLOCKING. The Build flyout trigger is literally a plus sign.

Measured in the DOM: the `<summary>` inside `[data-build-flyout]` has `innerText` **`"+"`**, box
32×44 px, sitting immediately right of the "Build" label.

Addendum §5 forbids this by name: the flyout "should feel deliberate and spatially responsive,
**never like a plus-sign utility control** or a purchased template." This is not an interpretation —
the control is the exact thing the addendum names.

It also explains the glyph collision visible in the rendered nav: "Build" followed by a cramped `+`
reads as an accordion widget, not as premium navigation.

### F8 — BLOCKING. The closed flyout is keyboard-focusable and laid out over the hero.

With `details.open === false`, the panel computes `display: grid`, `visibility: visible`,
`opacity: 1`, height 285 px at `top: 66px`. Its four links — `01 Build overview`, `02 Dagg Factory`,
`03 Agents and software`, `04 Trust and operations` — each have `tabIndex: 0` and a 44 px box.

So the closed menu's contents sit invisibly on top of the hero and a keyboard user tabs straight
into them. SLICE §7: "Hidden states are not focusable." Violated. This confirms F6, which was
correctly left as an unconfirmed lead in Part 1.

### F9 — The customer edge does not carry the addendum's actual thesis.

Section 6 is otherwise the best-built section on the page: one carrier, two states, real buttons
with `aria-pressed`, no fake vendor chat UI, and a chain that nearly matches addendum §3.

Two gaps:

1. **The MCP surface is never present.** Addendum §3 says the company's product "is no longer
   confined to its own interface" and names an MCP integration surfaced in Claude, ChatGPT or
   Codex. The rendered edge state says only "a source-linked recommendation **inside the customer
   interface**" — which a reader will most naturally take to mean Dagg's own interface. The single
   most differentiating claim in the thesis is currently rendered as a generic phrase.
   The fix cannot be a branded chat window (§3 forbids it, and forbids implying dependence on any
   single frontier model). It should name the surface *class* without vendor chrome — the capability
   reached through the assistant and tools the customer already uses, shown as a governed connection
   in the mechanism itself.
2. **The edge chain never closes the evidence loop.** Addendum §3 requires: request → resolves
   against company-specific context → recommendation or bounded action → crosses an explicit
   permission boundary → **returns evidence**. The inside state does return a record
   ("Decision and evidence return to company context"); the edge state stops at Boundary. The two
   surfaces must both close, or they do not read as two surfaces of one governed capability.

### Confirmation — peer structure re-verified live (addendum §1)

Addendum §1 requires re-verifying the peers rather than trusting stored measurements. Re-measured
anthropic.com/company today at 1542 px, and it reproduces the stored figures exactly:

| Section | Height | Words |
| --- | --- | --- |
| Making AI systems you can rely on | 258 | 25 |
| Our Purpose | 569 | 184 |
| The Team | 1004 | 168 |
| **What we value and how we act** | **1473** | **544** |
| Governance | 424 | 82 |
| Want to help us build the future | 472 | 12 |

Total 1015 words. **Bearer share 54%. Height ratio 5.7. Ground `#FAF9F5`.**

P4R4 matches the height ratio (5.7) and misses the weight distribution badly: its largest section
carries **24%**. That gap is the remaining structural reason the page still reads closer to a deck
than to a company page, and it is now backed by same-day measurement rather than recall.

Not re-verified this pass: OpenAI, xAI and Palantir. My claims about them in Part 3 rest on earlier
measurement and should be treated as such until re-run.

### Revised recommendation

Five blocking items, not four, and they cluster into three fixes:

1. **Hero container** — restore the full 1.60 aspect (F1); the caption then stops being
   load-bearing (F2) and the H1 gets room to sit on two lines (F3, F4).
2. **Global chrome** — replace the `+` trigger and stop the closed panel from rendering and taking
   focus (F7, F8). This is in P3 chrome, outside my write scope under §9, so it is Codex's.
3. **Customer edge and mobile asset** — name the MCP surface without vendor chrome, close the edge
   evidence loop (F9), and produce the portrait hero variant (F5).

None of these requires another style direction. The page's bones are sound; it is being let down by
one container, one nav control and one unfinished claim.

---

## Part 6 — Implementation pass (files owned by me under SLICE §9)

Christian authorised proceeding. I implemented the items inside my write scope and left F7/F8
(global chrome) to Codex. Verified with an own CDP client driving headless Chrome, because the
browser extension froze the renderer twice on this page (see "Open questions" below).

### Root cause found — one missing declaration caused both hero failures

`styles.css:15` was `img { display: block; max-width: 100%; }` with **no `height: auto`**.

Without it, the HTML `height` attribute acts as the used height, so `aspect-ratio` was ignored on
every image on the page. That is why the desktop hero clamped to `max-height: 520px` (giving the
0.96 box) and why the mobile hero stretched to the raw attribute height of 1024 (giving 0.33). The
declared `aspect-ratio: 4 / 5` never applied anywhere. F1 and F5 were the same bug seen from two
viewports, not two separate layout mistakes.

### Changes

`preview/golden-standard/p4r4/styles.css` — 5 edits:

1. `img { … height: auto; }` — the root-cause fix.
2. `.h1 { max-width: 10ch → 16ch }` — 10ch computed to 459 px at 68 px, forcing four lines.
3. `.hero { min-height: calc(90svh - 68px) → min(calc(90svh - 68px), 760px) }` — caps dead space on
   tall displays so the hero is bound by content, not by viewport fraction.
4. `.hero-art img` — `aspect-ratio: 4 / 5 → 1586 / 992` (the asset's true ratio),
   `max-height: 520px → none`, `object-position: 51% center → center`.
5. Removed the `max-width: 639.98px` override that re-imposed `aspect-ratio: 4 / 5` on phones.

`preview/golden-standard/p4r4/index.html` — 4 edits:

1. Hero `img` intrinsic attributes `1536×1024 → 1586×992` (they did not match the file; the
   WorkGraph image's 1536×1024 is correct and was left alone).
2. Caption `"Human judgment redirects company context into a governed operating path."` →
   `"Decision field — Original composition. Not a client system."` Provenance, not explanation, and
   consistent with the confidentiality rule.
3. Added a `Surface` row to the customer-edge state (addendum §3).
4. Added a `Record` row to the customer-edge state, closing the evidence loop.

Frozen copy was not altered. Slice §4 permits additional disclosed fields provided the stated
conclusions are not replaced; the two new rows add fields only.

### Verified after the change

| Check | Before | After |
| --- | --- | --- |
| Hero: share of master width shown, 1440 | 60% | **100%** |
| Hero: share of master width shown, 390 | ~21% | **100%** |
| Hero image aspect vs natural (1.60) | 0.96 desktop / 0.33 mobile | **1.60 at 1440, 768, 390, 320** |
| H1 lines, 1440 | 4 | **2** |
| H1 lines, 768 | — | **2** |
| Hero section height @ ~813 px viewport | 1650 | **664** |
| Document horizontal overflow | none | **none** at 1440, 768, 390, 320 |
| Smallest body-copy size | 20 px | **20 px @390, 19 px @320** |
| Console errors | none | **none** |
| Customer-edge chain | Request → Context → Response → Boundary | **Request → Surface → Context → Response → Boundary → Record** |
| `aria-pressed` toggling, one state visible | ok | **ok** |
| Visible word count | 406 | **404 default; 65 in the edge state when selected** |

Screenshots: `after-hero-1440.png`, `after-hero-390.png`, `after-full-1440.png`,
`after-full-390.png`.

I looked at the rendered result at full size rather than inferring it from the numbers. The hero now
reads its own argument — wandering smudged graphite on the left, the terracotta decision, four exact
lines continuing under the sage boundary — without the caption doing any of the work.

### Deviations I chose, stated rather than hidden

**Hero carrier is ~350 px, not the 460–520 px band in SLICE §5.** At the frozen 7/5 grid the art
column is 5/12 ≈ 498 px, and at the asset's true 1.60 ratio that yields 311 px of image plus the
caption. The band and the no-crop rule cannot both hold at 5 columns. I kept the frozen grid and the
whole chain, and gave up the height band, because §5 and addendum §5 both state the crop rule
explicitly while the band is a composition guideline. If Codex prefers the band, the fix is to widen
the art to 6 columns — but that narrows the copy column and risks returning the H1 to three lines,
so it should be measured, not assumed.

**H1 remains four lines on mobile** (44 px @390, 40 px @320). Four lines is correct typography at
that width; the "at most 2.5 headline lines" rule in §7 reads as a desktop constraint and should be
reworded to bind desktop only. I did not shrink the type to satisfy a number at the cost of the
rendering.

### Still open, not mine to fix

- **F7** — the Build flyout trigger is literally `+`. Addendum §5 forbids it by name.
- **F8** — the closed flyout's four links remain laid out and `tabIndex: 0` over the hero.
- **F5 (remainder)** — the landscape asset is now complete but small on a phone (350×219 at 390 px).
  A purpose-composed portrait variant, briefed in Part 3 §6, would serve mobile better. Creating it
  writes into `design/golden-standard/image-system/`, which §9 does not grant me.
- **Bearer share is still 24%** against Anthropic's measured 54%. Unchanged by this pass, because it
  is a content-architecture decision, not a layout fix.

### Open questions

The browser extension froze the renderer twice on this page — once immediately after a hover over
the nav, once on a plain evaluate. The first freeze predates all my edits, so it is not caused by
them, and headless Chrome renders the same page without errors. It may be the extension rather than
the page, but a hover-triggered renderer freeze is worth Codex reproducing independently before the
slice is accepted.
