# Dagg website — versions

Two versions live side by side. **Version 1 is preserved and untouched.**

| Version | URL | Notes |
|---------|-----|-------|
| **V1** (approved baseline) | https://elzerep.github.io/dagg-site/ | The current approved design + content. Unchanged. |
| **V2** (content/structure iteration) | https://elzerep.github.io/dagg-site/v2/ | Same design system, expanded strategic content. |

To roll back: V2 lives only in `/v2/`. Deleting that folder leaves V1 exactly as-is.

---

## What changed in V2 (content / structure / copy only — NOT a redesign)

The visual system is identical to V1: same dark green / purple palette, icons,
typography, spacing, gradients, animations (self-assembling WorkGraph, factory
flow, looping compounding curve), scrollspy tabs on desktop, hamburger + one-
section-per-screen snapping on iPad/mobile.

**Strategic clarity**
- New **two-mode transformation model** in the Factory section:
  *"Automate what should stay. Rebuild what should change."* — three cards:
  Map the work · Automate existing workflows · Rebuild broken workflows.
  Makes explicit that Dagg does **both** agentic automation on top of existing
  systems **and** custom AI-native software when the workflow layer is broken.
- New **"Works with the stack you already have"** card (no rip-and-replace, but
  new software where the old layer is broken).
- New **"Production-grade, not prototype-grade"** card (governed, monitored,
  rollback, measurable before/after).

**Technology section rewrite**
- "DIS / KRAG — your knowledge…" → **"The Intelligence Layer — your company
  context, made operable by agents."**
- Four sub-blocks: Capture · Model · Recall & Act · Govern.
- DIS/KRAG are no longer customer-facing names; KRAG is referenced only lightly
  as a proprietary method (knowledge graph + retrieval + workflow context).

**New sections**
- **Proof of the thesis — "From workflows to ventures"** with an **Aloi** card
  (logo + "Institutional knowledge, activated.", link to https://aloi.law/).
- **About — "Built by founders, engineers and operators."**

**Navigation**
- Tabs/menu updated to: Premise · WorkGraph · Factory · Technology · Proof · About.
- Long-scroll storytelling preserved; smooth anchor nav + active-section state kept.

**Cleanup**
- Removed all external links to **getdis.ai** and the old **dagg.ai** (this site
  becomes the new dagg.ai). Footer/menu now use `hello@dagg.ai`.
- Primary CTA standardized to **"Book a WorkGraph Strategy Assessment"** throughout;
  secondary CTA "Explore the platform" / "See how the factory works".

**Removed**
- The generic "What you get / Operating advantage" value-grid section (folded;
  its substance now lives across Premise, Factory and Compounding).
