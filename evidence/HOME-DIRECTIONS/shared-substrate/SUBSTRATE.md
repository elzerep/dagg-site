# P4R6 shared substrate acceptance

Status: **PASS for P4R6 route assembly**  
Accepted: 31 August 2026  
Scope: static assembly, exact shared imports and desktop interaction smoke test. This is not Home-direction visual acceptance.

## Resolution of the component-layer conflict

The first Claude extraction duplicated P4R5 flyout behavior inside `shared/chrome/chrome.js` while P4R6 also required every route to import the exact passed P4R5 component script. Loading both would have initialized the Build flyout twice.

The accepted contract is now explicit:

1. `shared/chrome/chrome.css` is byte-identical to the accepted P3 global chrome stylesheet.
2. `shared/chrome/chrome.js` is byte-identical to the accepted P3 global chrome behavior.
3. Every assembled route directly imports the exact passed P4R5 `component-library/styles.css` and `component-library/script.js` after the P3 layer.
4. Direction CSS/JS loads last and is mechanically forbidden from forking shared chrome behavior, tokens or component classes.
5. Header and footer DOM are inserted only by the deterministic build step and are complete before the first script, so no-JavaScript remains legible.

This preserves both authorities without double initialization: P3 owns global disclosure, sticky header, focus containment and theme adaptation; P4R5 owns the Build flyout, component behavior and finite semantic motion.

## Machine evidence

Commands:

```text
node tools/build_golden_standard_previews.mjs
node tools/build_golden_standard_previews.mjs --check
```

Fresh result: 7 of 7 assembly checks pass, with deterministic second-run equality.

- shared hash equality: pass;
- outputs current: pass;
- local references only: pass;
- no inline vector markup: pass;
- no text-symbol icons: pass;
- no-JavaScript static completeness: pass;
- no copied shared DOM: pass.

The authoritative hashes, source order and fixture output hash are recorded in `build-manifest.json` beside this file.

## Visual and interaction smoke test

Immutable local snapshot:

`69f682cbb83a2ba71c2f9c6da229a787afe9e22ae03863694f5f3e3c9ff9cc20`

The assembled fixture was opened in the in-app browser and inspected at its measured desktop viewport. Header, typography, page field, footer and warm/ink transition rendered correctly. Opening the Build disclosure produced the accepted two-column flyout with four real destinations and one proof inset; no duplicate reveal controls or duplicate state initialization appeared.

Exact mobile behavior remains part of the six-route P4R6 evidence run. The assembly layer itself imports the unchanged P3 and passed P4R5 mobile behavior rather than reimplementing it.

## Release boundary

This pass releases route construction only. A0/X1 acceptance still requires the full nine-act Home contract, frozen image manifests, equal six-route evidence, desktop/mobile/no-JS/reduced-motion coverage and visible peer comparison.
