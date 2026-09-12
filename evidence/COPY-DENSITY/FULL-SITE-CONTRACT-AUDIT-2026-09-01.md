# Full-site content contract density audit

Date: 1 September 2026  
Source: `design/golden-standard/narrative/FULL-SITE-CONTENT-CONTRACT.md`  
State: accepted narrative contract 1.0 after Codex and Claude cross-review  

## Counting method

- Exclude route metadata, page-job notes, internal status/fallback rules, anchor
  IDs, visual jobs and global shell.
- Include visible headings, CTA labels, captions, artifact labels and active
  record values.
- `Default-visible` follows the contract's explicit per-route assignment.
- `Progressive/system` includes permitted detail, alternate states and UI
  success/error copy.
- First-screen count includes all public copy ordered inside section 1.
- Hyphenated terms count as one word.
- Conditional Impact links are counted separately because the publication build
  omits them until a proof passes V/C review.

## Result

| Route | Default-visible | Progressive/system | First screen | Result |
|---|---:|---:|---:|---|
| Home | 351; 355 with Impact enabled | 0 | 49 | PASS |
| Transformation | 474 | 180 | 48 | PASS |
| WorkGraph | 351 | 122 | 48 | PASS |
| Build | 468; 472 with Impact enabled | 277 | 53 | PASS |
| Impact | 127 | 62 | 40 | STAGED; no approved proof |
| Company | 281 | 105 | 47 | PASS |
| Trust | 305 | 103 | 44 | PASS |
| Assessment | 335 | 131 | 39 | PASS |

Impact is not underfilled public copy. It is intentionally ineligible for the
publication build until a sourced case supplies the approved conclusion,
bounded Dagg role, result/timeframe and provenance.

Progressive copy below a cap is not a defect and must not be padded.

The Home figure records render-assignment addendum 1.1. P4R8R1 proved that the
intermediate state carries the ownership boundary that withholds commitment;
all three accepted proof states are therefore default-visible. No sentence or
claim was added, and 351 remains inside Home's 280-360 default-visible band.
