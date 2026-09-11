# FS6 — production migration and publication package

Status: required after FS5 visual acceptance and before Christian's launch gate  
Owner: Codex integration; bounded Fable 5.1 implementation and review lanes  
Publication: forbidden until every gate below passes and Christian approves the
exact immutable production revision

## 1. Decision

FS5 is an intentionally deterministic static HTML/CSS/JavaScript staging system.
It is the visual, narrative, responsive and interaction truth used to make the
site correct. It is not the permanent production architecture.

FS6 migrates the accepted FS5 candidate to the production stack already selected
in `reference-audits/FRONTEND-INTERACTION-STACK.md`:

- current stable Next.js App Router, TypeScript and React Server Components;
- static generation for public routes;
- Tailwind CSS 4 mapped to the existing Dagg semantic variables for utilities;
- co-located CSS Modules for bespoke composition, material and chrome;
- Motion for React only for meaning-bearing carriers and adaptive navigation;
- typed local content or MDX; no CMS until a real multi-editor need exists;
- Next Image with explicit dimensions, responsive sources and route-specific
  loading priority;
- no bought template, generic visual kit or client-rendered page body.

Versions are selected from current stable releases at migration time, recorded
in the lockfile and held constant through publication QA.

## 2. Migration authority and ownership

1. Freeze the accepted FS5 assembly, snapshot ID, route matrix, screenshots and
   exact copy manifest.
2. Create the Next.js application in a new production directory. Do not mutate
   the accepted FS5 sources into a framework piecemeal.
3. Migrate shared tokens, fonts, logo and image assets first; preserve hashes for
   unchanged source assets.
4. Migrate server-rendered route structure and exact copy before enhancements.
5. Migrate adaptive navigation and each meaning-bearing carrier as isolated
   Client Components.
6. Run parity route by route against the same viewport, state and source
   reference. FS5 remains the visual and semantic oracle until parity passes.
7. Cut over only after the production build passes every FS5 gate plus the FS6
   gates below. No route is promoted individually.

One writer owns each migrated route or shared component. Fable 5.1 is the
primary design/copy/interaction implementer inside those bounded scopes. Codex
owns integration, parity evidence, infrastructure, security boundaries and the
single release candidate. Two writers never edit the same file concurrently.

## 3. Required production topology

```text
app/
  layout.tsx
  page.tsx
  transformation/page.tsx
  workgraph/page.tsx
  build/page.tsx
  company/page.tsx
  trust/page.tsx
  assessment/page.tsx
  impact/page.tsx                 # generated only when the proof gate passes
  privacy/page.tsx
  terms/page.tsx
  not-found.tsx
components/
  chrome/
    SiteHeader.tsx                # server shell
    DesktopNavigation.client.tsx
    MobileNavigation.client.tsx
    AdaptiveBuildPreview.client.tsx
    SiteFooter.tsx
  mechanisms/                     # isolated client carriers only
content/                           # typed route copy and metadata
styles/                            # tokens plus route CSS Modules
public/                            # vendored fonts, logo, responsive assets
```

Pages remain Server Components. Interactive islands receive typed serializable
state and do not duplicate public copy in JavaScript.

## 4. Navigation and routing migration

The launch navigation is `Transformation · WorkGraph · Build · Company · Start
an assessment`. Impact remains atomically absent until its proof gate passes.

FS5 preserves the native Build `<details><summary>` substrate. FS6 implements the
final split control:

- a real `/build` overview link;
- an adjacent named disclosure button with `aria-expanded` and `aria-controls`;
- destinations `/build`, `/build#factory`, `/build#factory-modes` and `/trust`;
- a stable feature panel whose bounded proof inset changes without outer-layout
  jump;
- 70–100 ms pointer intent, 180–240 ms close grace and an unbroken pointer
  corridor;
- Enter/Space, Escape with focus restoration, complete Tab order and no ARIA
  menu roles;
- a full-height mobile reading sheet with 48 px controls, focus containment,
  background inertness, scroll lock and equivalent content;
- native/static no-JavaScript access to every destination.

Replace staging base paths with canonical internal routes through one typed
navigation schema. Ordinary Dagg routes remain in the same tab. External-window
indication is used only for genuine external destinations.

## 5. Customer-edge two-surface proof

FS6 implements the stateful proof deferred from FS5. Start from the accepted
P4R5 two-surface component contract; do not design a new grammar.

One governed carrier demonstrates that the same capability can serve:

1. the company internally, where agents execute within owned context and human
   decision rights; and
2. the customer edge, where a permissioned request can reach the product from an
   interface the customer already uses.

The carrier must expose company context, proposed or completed action,
permission boundary, accountable owner and returned evidence. It must not mimic
Claude, ChatGPT or another provider; show a named customer, fabricated result or
live deployment; explain MCP as the headline; or become a generic prompt box.
Reduced motion renders every conclusion immediately. No JavaScript preserves the
complete explanatory argument.

## 6. Assessment production path

Replace the FS5 truthful non-transmitting preview with one approved production
endpoint. Evidence must cover:

- initial, client/server validation, submitting, success, error and duplicate
  states;
- keyboard and touch completion, first-error focus and polite status;
- CSRF/spam protection, rate limiting and duplicate suppression;
- a durable delivery destination and operational owner;
- consent, privacy, retention and deletion copy approved for launch;
- a resilient no-JavaScript path or an explicit truthful dependency;
- test submissions only during QA; no accidental real enquiry.

## 7. Publication dependencies

- Approved Privacy and Terms copy and reachable footer links.
- Correct title, description, canonical, Open Graph and social image per route.
- Static robots directives, sitemap and structured data matching the exact
  public route inventory.
- Impact absent from navigation, metadata, sitemap and build until one
  permissioned proof passes the evidence ledger. Aloi is not automatically
  publishable because its name is known.
- Christian Pérez and Simon Lundmark names, accents and titles verified before
  publication.
- Dash and quotation normalization without changing approved meaning.
- A truthful Trust route and diligence contact; no unsupported certifications,
  residency, encryption, isolation or managed-operation claims.
- One branded 404 with working recovery routes.

## 8. Fonts, images and performance

- Vendor the complete approved Geist, Newsreader and JetBrains Mono subsets
  required by the public copy; no Google Fonts or runtime font request.
- Keep total critical font transfer within the accepted budget; preload only the
  faces needed above the fold.
- Preload the selected Home hero desktop or mobile source by media condition;
  never preload both.
- Preserve intrinsic dimensions and independent mobile/tablet compositions.
- Use AVIF/WebP where visually lossless enough; preserve originals and
  provenance outside the public transfer path.
- Lazy-load below-fold imagery and non-critical mechanisms.
- Keep meaning-bearing client JavaScript inside the route and shared budgets;
  no analytics, consent or motion dependency may block first paint.
- Production targets: LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1 at field-equivalent
  p75; Lighthouse mobile ≥90 Performance and ≥95 Accessibility, Best Practices
  and SEO.

## 9. Parity and platform matrix

The production candidate must reproduce the accepted FS5 semantic order, copy,
visual hierarchy and states at all FS5 viewports, including `834×1194`. Add:

- macOS Safari and Chrome;
- Windows Edge;
- iPad Safari portrait and landscape;
- iPhone Safari-class touch;
- a 320 px touch/emulation pass;
- fine, coarse and hybrid pointer transitions, including resize/orientation
  changes while a disclosure or mechanism is open;
- reduced motion, 200 percent zoom, keyboard-only, screen-reader smoke and true
  no-JavaScript states;
- slow-image, failed-image and font-fallback behavior;
- production base path, canonical URL and hard-refresh routing.

Every capture, trace, assertion and performance result belongs to one immutable
production snapshot. Mixed-revision evidence is invalid.

## 10. Cutover and launch gate

FS6 is complete only when:

1. every public route has exact source-to-production parity or an approved,
   documented production-only correction;
2. all links, fragments, navigation states and Assessment outcomes work;
3. the full accessibility, responsive, motion, performance, metadata and
   platform matrix passes;
4. Codex and Fable 5.1 independently return no P0/P1 against the same frozen
   candidate;
5. the complete evidence bundle and immutable revision are presented to
   Christian; and
6. Christian explicitly approves publication of that exact revision.

No approval is inferred from FS5 acceptance, a Home choice, a successful build,
an available domain or a previous instruction to keep working.
