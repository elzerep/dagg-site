# Peer copy-density benchmark

Date: 1 September 2026  
Status: editorial calibration evidence; not a pixel or interaction audit  
Sites: Anthropic, OpenAI, SpaceXAI/xAI and Palantir  

## Method

- Official live pages only.
- Approximate main-content words; global navigation and footer excluded.
- For tabs, carousels and product worlds, count the initially visible state
  rather than every hidden sibling.
- Narrative words and active product/UI words are separated where the page
  structure makes that distinction possible.
- Major acts are editorial sections, not DOM containers.
- This pass did not capture a common desktop viewport or pixel screenshots.
  Therefore it supports copy-density and disclosure decisions only. It does not
  verify spacing, viewport height, hover behavior or visual prominence.
- Live pages can change. Re-sample before the final rendered density gate.

## Anthropic and OpenAI

| Official page | Approximate visible words | Major acts | H1 / lead | Proof and disclosure pattern |
|---|---:|---:|---|---|
| [Anthropic Home](https://www.anthropic.com/) | 100-120 | 4 | 10 / 24 | Institutional thesis and current artifact cards; depth routes outward. |
| [Anthropic Research](https://www.anthropic.com/research) | 380-410 | 5-6 | 1 / 27 | Research areas, featured items and publications form an index. |
| [Anthropic Company](https://www.anthropic.com/company) | 900-950 | 6 | 7 / 16 | Editorial institution story, values and governance. |
| [Anthropic Policy](https://www.anthropic.com/policy) | about 1,900 in DOM | 4 macro + 6 priorities | 1 / 25 | Panels and priority areas reduce initial burden versus total DOM copy. |
| [OpenAI Home](https://openai.com/) | 250-280 | 6-7 | product prompt / 5 | Product surface and story/research/business cards carry the page. |
| [OpenAI Research](https://openai.com/research/) | 470-520 | 5 | 7 / about 29 | Research clusters and artifact cards route to articles. |
| [OpenAI API Platform](https://openai.com/api/) | 540-600 | 7-8 | 7 / none | Model, modality and use-case states progressively reveal product depth. |
| [OpenAI Enterprise](https://openai.com/business/why-openai/enterprises/) | 380-420 | 8-9 | 7 / 15 | Value pillars, product proof, customer measures and case routes. |

## SpaceXAI/xAI and Palantir

| Official page | Approximate visible words | Major acts | H1 / lead | Proof and disclosure pattern |
|---|---:|---:|---|---|
| [SpaceXAI Home](https://x.ai/) | 240-320 including active UI | 5 | 7 / 12 | Five product mini-worlds, one API/code state and compact metrics. |
| [SpaceXAI Build](https://x.ai/build) | 300-380 narrative; 500-650 with active UI | 8 | 5 / 15 | Feature-specific product worlds carry the mechanism. |
| [SpaceXAI Business](https://x.ai/grok/business) | 400-520 narrative; 650-900 with UI | 5 macro | 4 / 18 | Capability modules, controls and pricing reveal depth progressively. |
| [SpaceXAI Company](https://x.ai/company) | 190-230 | 6 | 4 / 23 | Mission, evidence links, values and timeline/news. |
| [Palantir Home](https://www.palantir.com/) | 350-420 | 6 | 6 / no conventional lead | Platform index, analyst proof, bootcamp and differentiators. |
| [Palantir AIP](https://www.palantir.com/platforms/aip/) | 700-900 initially inspectable | 9 | 2 / 10 | Ontology mechanism, capabilities, awards and media. |
| [Palantir Offerings](https://www.palantir.com/offerings/) | 430-500 | 2 | 1 / about 21 | A concise taxonomy routes to more than 30 child solutions. |
| [Palantir Impact](https://www.palantir.com/impact/) | 700-950 | 5 | 6 / 9 | Quantitative lead cases, quotes and a deeper case library. |

## Interpretation

The strongest common pattern is not a single word count. It is a relationship:

`short conclusion -> named product or mechanism -> evidence-bearing object -> next layer`

Home pages are edited entrances, not compressed deep pages. Product and case
pages earn additional copy when an inspectable mechanism, UI state, source or
attribution boundary carries it. Hidden sibling states do not justify an
unbounded total.

The binding Dagg budgets, peer-to-route mapping and anti-proxy rules live in:
`design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`.

