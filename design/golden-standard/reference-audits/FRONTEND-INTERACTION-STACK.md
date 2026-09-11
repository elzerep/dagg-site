# Frontend and interaction system audit

Status: accepted research input for P4 and later implementation  
Audit date: 30 August 2026  
Authority: `../DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Scope: current public navigation behavior, implementation signals, Dagg stack recommendation and executable acceptance contract

## Executive decision

Dagg should use a modern Next.js App Router stack with most public content
server-rendered and a deliberately small interactive layer. The premium feeling
must come from adaptive behavior, material precision, real product evidence and
motion with meaning. It must not come from a generic marketing template or a
large hydrated component library.

The xAI-style adaptive flyout is the primary interaction reference. Dagg will
improve it with Anthropic's disclosure semantics, OpenAI's hierarchy and
external-link clarity, and Palantir's discipline of exposing proof only when
there is real proof to show.

The governing rule is:

> Modernity should be visible in behavior and restraint, not in how much
> JavaScript Dagg ships.

## Evidence policy

The matrix separates what was directly observed from what was inferred. A
framework name may inform implementation only when its use was visible in the
delivered site. An animation library, hosting provider or package version is
not treated as known merely because the interaction resembles one.

| Reference | Directly observed interaction | Verified implementation signal | Inferred or unknown |
|---|---|---|---|
| xAI / SpaceXAI | Hover flyouts on Products, Solutions, Developer and Company; Pricing and News are direct links. Panels resize and reposition by group. Products measured about `700 × 387`; Solutions `220 × 237`; Developer `220 × 196`; Company `220 × 160`. Opening was immediate in the sampled state. The panel remained open at least 80 ms after pointer exit and was closed by 260 ms. | Next.js assets under `/_next/static`, including a Turbopack runtime. Reduced-motion CSS is present. | Tailwind is a high-confidence inference from compiled utilities. Exact package version, motion library and hosting are unknown. |
| Anthropic | Warm compact flyouts. The sampled Research panel measured about `250 × 259`. Hover and Enter open; Escape closes and returns focus. `aria-controls`, `aria-haspopup` and `aria-expanded` are present. | Webflow page/CDN/runtime, jQuery and GSAP 3.15 with ScrollTrigger and SplitText. | Exact custom build pipeline and full reduced-motion implementation are unknown. |
| OpenAI | Full-width flyout below a 64 px header. The page behind dims and blurs. The panel uses strong section hierarchy. External links include accessible new-window language. | Next.js/Turbopack asset paths and Vercel Speed Insights. Reduced-motion CSS is present. | Tailwind-like classes are visible but the dependency and version are unverified. Keyboard opening was not confirmed in the sampled browser run. |
| Palantir | Click opens a full-viewport editorial navigation rather than a desktop hover flyout. The navigation combines products, current material, impact and offerings. `aria-expanded` updates. | Next.js Pages Router, `__NEXT_DATA__` and webpack chunks. Reduced-motion CSS is present. | Hosting, internal component library and animation library are unknown. |

Reference URLs:

- <https://x.ai/>
- <https://www.anthropic.com/>
- <https://openai.com/>
- <https://www.palantir.com/>

## What Dagg takes from each reference

### xAI / SpaceXAI

- adaptive flyout width and height rather than one fixed mega-menu;
- a warm elevated panel that reads like a precise editorial object;
- row-level hover and focus treatment;
- selective external-link arrows;
- short close grace so the pointer can travel into the panel;
- direct routes where no submenu is justified.

### Anthropic

- a true disclosure model with explicit expanded state;
- keyboard open, Escape close and focus return;
- compact panels whose size follows content;
- warm material without turning navigation into decoration.

### OpenAI

- strong hierarchy and legible grouping;
- unmistakable focus states;
- accessible naming for links that deliberately open another domain or tab;
- the page beneath may recede when a large information surface opens.

### Palantir

- current proof belongs in navigation only when there is enough real proof;
- product and impact material can be editorial rather than a grid of product
  names;
- navigation can become a content surface, but should not manufacture an
  enterprise-scale information architecture before the content exists.

## Dagg production stack

Use the current stable releases at implementation time, then lock exact
versions in the package lockfile.

- Next.js App Router, TypeScript and React Server Components.
- Static generation for public routes.
- Tailwind CSS 4 mapped to Dagg semantic CSS variables for layout and low-level
  utilities.
- Co-located CSS Modules for bespoke chrome, materials and interaction states.
- Motion for React only for adaptive navigation and meaning-bearing mechanism
  carriers. Use CSS transitions for simple hover, focus and opacity states.
- Typed local content or MDX first. Add a CMS only when a real multi-editor
  publishing workflow exists.
- Next Image for responsive sources, explicit dimensions and lazy loading.
- No generic visual component kit and no bought marketing template.

Official implementation references:

- <https://nextjs.org/docs/app>
- <https://nextjs.org/docs/app/getting-started/server-and-client-components>
- <https://nextjs.org/docs/app/getting-started/images>

### Server and client boundary

```text
SiteLayout.server
├── SiteHeader.server
│   ├── DesktopNavigation.client
│   │   ├── TopLevelLink
│   │   ├── DisclosureButton
│   │   └── AdaptiveFlyout
│   └── MobileNavigation.client
├── route pages and editorial content.server
├── MechanismCarrier.client
└── SiteFooter.server
```

Navigation data lives in one typed schema containing:

- label;
- destination;
- direct or disclosure behavior;
- compact or feature panel variant;
- internal or external destination;
- visible description;
- optional real preview artifact.

No page body becomes a Client Component merely because one child moves.

## Launch navigation topology

The accepted top-level navigation remains:

`Transformation · WorkGraph · Build · Company · Start an assessment`

At launch:

| Item | Behavior | Reason |
|---|---|---|
| Transformation | Direct link | One coherent strategic destination; no child route is yet needed. |
| WorkGraph | Direct link | Singular core technology and cross-lifecycle context layer. |
| Build | Native disclosure enhanced into an adaptive feature flyout in FS5 | Enough real depth exists to justify Build overview, Dagg Factory, Agents & custom software and Trust. The `<summary>` is named `Build`; the first child is the real overview link. |
| Impact | Absent at launch until proof gate passes | Enable only when a permissioned evidence-led proof and complete public route exist. |
| Company | Direct link | Keep direct until at least two substantial child destinations exist. |
| Start an assessment | Persistent direct CTA | Conversion action, never a disclosure. |

Build uses the feature-panel form, approximately 620–680 px wide. Links sit
on the left; one real Factory or build-record state sits on the right. It must
not contain invented customer evidence. A future Company flyout may use a
compact 240–300 px form if the route tree becomes real.

## Adaptive flyout contract

### Desktop with a fine pointer

- Open after 70–100 ms hover intent.
- Close 180–240 ms after leaving both trigger and panel.
- Provide a pointer corridor so the trigger-to-panel journey cannot fall into
  a closure gap.
- Switching disclosure groups morphs panel dimensions in 180–240 ms with no
  overshoot and no page reflow.
- Content crossfades in 100–140 ms.
- Row highlight moves in about 120 ms.
- The panel remains open while either it or its disclosure control is hovered
  or focused.
- Escape closes and returns focus to the disclosure control.
- Click outside closes.
- Keyboard focus on a direct link does not reveal unrelated content.

FS5 preserves the existing native `<details><summary>` named `Build`; its first
child is the real `/build` overview link, followed by `/build#factory`,
`/build#factory-modes` and `/trust`. FS6 migrates to a real top-level overview
link plus adjacent disclosure button after exact interaction parity is proven.
Use a normal navigation list and the WAI disclosure pattern; do not apply ARIA
`menu` or `menubar` roles to ordinary site navigation.

- <https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/>
- <https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus>

### External destinations

- Use `↗` only when Dagg deliberately opens a separate product or domain in a
  new tab.
- Reveal it on hover and focus; keep it visible for touch.
- Add visually hidden “opens in a new tab” text.
- Do not open ordinary Dagg routes in new tabs.

Reference: <https://www.w3.org/WAI/WCAG22/Techniques/html/H83.html>

### Mobile and coarse pointer

- No hover dependency.
- Use a full-height reading sheet with 52–56 px rows and native accordion
  groups only where child destinations exist.
- Open and close controls are named and at least 48 × 48 px.
- The page beneath becomes inert; focus remains within the sheet.
- Escape and the backdrop close the sheet and return focus.
- The assessment action remains reachable and never covers the final links.
- Use pointer capability, not viewport width alone, for hybrid devices.

### No JavaScript

- Every direct top-level destination remains a real link. Build remains a native
  summary whose first child is the real overview link.
- All public copy, cases and artifacts remain server-rendered and readable.
- Mobile exposes the native Build `details/summary` disclosure and the complete
  four-link destination list.
- The adaptive flyout is progressive enhancement, not the only route to its
  child pages.

### Reduced motion

- Remove position, scale and panel-size morph.
- Snap panel dimensions and use at most a short opacity transition.
- Mechanism loops show their resolved explanatory state.
- Labels and meaning never disappear with motion.

References:

- <https://motion.dev/docs/react-use-reduced-motion>
- <https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion>

## Performance and asset budgets

The peer sites demonstrate interaction quality, not acceptable Dagg payloads.
Dagg keeps the following hard budgets:

| Surface | Target | Hard failure |
|---|---:|---:|
| Initial client JavaScript | ≤120 KB gzip | >150 KB gzip |
| Navigation client bundle | ≤20 KB gzip excluding shared React | >20 KB gzip |
| Initial CSS | ≤45 KB gzip | >45 KB gzip |
| Initial fonts | two WOFF2, ≤160 KB combined | more than two or >160 KB |
| Mobile initial transfer | ≤1.2 MB | >1.2 MB |
| Hero/LCP visual | ≤300 KB mobile; ≤500 KB desktop | larger without accepted exception |

Additional rules:

- no autoplay video in the initial viewport;
- below-fold imagery is lazy loaded with explicit dimensions and `sizes`;
- nonessential analytics loads after consent or idle;
- no advertising pixels;
- field p75 targets: LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1;
- internal targets: LCP ≤2.0 s and CLS ≤0.05.

Core Web Vitals reference:
<https://web.dev/articles/defining-core-web-vitals-thresholds>

## Executable acceptance contract

The navigation and shared runtime are not review-ready until one exact
revision passes all of the following:

1. Viewports: `1440×900`, `1280×800`, `1024×768`, `940×800`, `768×1024`,
   `390×844` and `320×568`.
2. Input: fine-pointer hover, mouse click, keyboard only and coarse-pointer
   touch.
3. Hover opens the correct panel within 120 ms.
4. Pointer movement from disclosure to panel cannot close it.
5. Leaving both closes in 180–280 ms.
6. Feature and compact panels morph without page reflow or cumulative layout
   shift.
7. Enter and Space toggle disclosure buttons; Escape closes and restores
   focus.
8. Tab reaches every visible submenu link exactly once and never enters a
   hidden panel.
9. `aria-expanded`, `aria-controls`, current route and external-link naming
   are correct.
10. External arrows appear on hover and keyboard focus.
11. Mobile traps focus, locks page scroll, closes by Escape and backdrop, and
    contains no clipped destination.
12. `prefers-reduced-motion` shows the resolved state without spatial morph.
13. A JavaScript-disabled run retains top-level navigation and readable public
    content.
14. `document.scrollWidth === document.clientWidth` at every target viewport.
15. Zero browser errors, broken routes or dead controls.
16. Automated accessibility testing has zero critical or serious findings;
    manual keyboard and screen-reader smoke tests also pass.
17. Lighthouse CI mobile scores at least 95 for Accessibility, SEO and Best
    Practices, and at least 90 for Performance.
18. Evidence contains desktop and mobile screenshots for closed navigation,
    every disclosure group, keyboard focus, the mobile sheet, reduced motion
    and no JavaScript.

## Rejection conditions

Reject the implementation if any of these are true:

- it uses a bought template or a generic visual component kit;
- it exposes flyouts for empty or invented child routes;
- its premium effect depends on glass, large shadows or ornamental motion;
- a submenu is hover-only or inaccessible from the keyboard;
- a false product screenshot appears in the feature panel;
- no-JavaScript navigation loses destinations;
- motion disappears without leaving a resolved semantic state;
- the client bundle exceeds the budget merely to animate marketing content;
- the result resembles an enterprise dashboard, circuit board or slide deck.
