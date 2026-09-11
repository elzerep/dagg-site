# FS5 post-lane source freeze

Date: 3 September 2026  
State: source frozen before the single controlled assembly  
Publication: not authorised and not attempted

This is the controlling post-lane handoff. It supersedes Lane A report §1.1
and Lane B report §1.2 only:

- Company now uses the breakpoint-specific R5 contract recorded in
  `FS5-CONTROLLER-RECONCILIATION.md` and the current Company page map.
- WorkGraph now has exactly one route root: both `data-workgraph` and
  `data-workgraph-page` are emitted on `<main>` from `meta.json`; the duplicate
  wrapper hook is removed.

All three lane reports remain valid historical implementation evidence for the
work they describe. Final source identity is the hash set below.

## Final route source hashes

| Route / file | SHA-256 |
|---|---|
| `home/src/body.html` | `bdc49a3211447cf8021cb139d82accae41c0a17dd6653aa7130af5328b12f404` |
| `home/src/direction.css` | `56d312c513a80d9c759792662a2bc8104cf43b7950fdad8b6791e6aaae92b069` |
| `home/src/direction.js` | `ffc710df6f912e51b13c67f91b7b649e0cc9e246866ed6a9732931ac385a35ee` |
| `home/src/meta.json` | `b7540d457ffd6f36f397c2ad1ff4081752abd481d5bd122b8682fd9c38f322a5` |
| `transformation/src/body.html` | `26ef492baa55a1df345c6ab7c5740a98cd009556148664878c175bda99d6040f` |
| `transformation/src/direction.css` | `9cfbbad44dcf0d5aa8cbd23c95e9daf493aabb34349a2e4586a218d7c4d176f3` |
| `transformation/src/direction.js` | `12ff6ab165dc58c73e0c135decc3d9607681d1495da099a92f16faa40361803b` |
| `transformation/src/meta.json` | `066896168859ad0c2b4e6225bde2cc85a4c6603785ef42f7e5f67cd24d29d2c0` |
| `company/src/body.html` | `0c0f8302ffeae7510e5b74b76778fe5e63a85e64b29bf243e6105671df32dab2` |
| `company/src/direction.css` | `e5d76fb8f84666201cd23e0ead59716c456ba9f61f2b800f8216671c0039d40f` |
| `company/src/direction.js` | `a03df84cf2fbcc0838c4a93c8326acb10c838586b5269a7950a43df9ab338b38` |
| `company/src/meta.json` | `cb0459d2c098ad953210d6b457839bbf5cf5ee4ed0028a11a2167262cc1a0b70` |
| `workgraph/src/body.html` | `65f1a390183971f93bd6b3788ed6cc715e9e0f41b8f1269096351df73cd61294` |
| `workgraph/src/direction.css` | `61754f99a41267f3c894d3342d8a0ebe7a89192b97bfe0940fae2bc2318ad868` |
| `workgraph/src/direction.js` | `92f84d0640b52148ead79e259fa5e7f24095de0b5ddff861d9472aee3e76e09f` |
| `workgraph/src/meta.json` | `3f75bc24e290850cd92e0f111c0a78f9c88cb7e59078c0270bd96180657b6cc3` |
| `build/src/body.html` | `b7561c4d09b5043eda1333c45b7f68fa17be21c81524cf80dbc42bb19af80fd1` |
| `build/src/direction.css` | `ade4244b3144df2402f6ded73009354da3741bd7cb86d1cc01d4301289257653` |
| `build/src/direction.js` | `21dccd80543e21e2598d4b460607be4ebd9dfe58b79932811170c7ff9f4fa1c8` |
| `build/src/meta.json` | `e5360d3efc84e968953fa77ae2cac4ee24af500168271dff79ccceacd13a3ee4` |
| `trust/src/body.html` | `cd42fd3ea7abc06b934b3319cb359caddc10ec316fe3469a995969711fd6f0b5` |
| `trust/src/direction.css` | `36a9abace024373d80415cf68f6ddf0f4f6f24b519f6c760420736feab02b643` |
| `trust/src/direction.js` | `850b0e4f351ae0c1a83c2a35782b40ed9fee4c1258c78aee527e7b3cd1d6d876` |
| `trust/src/meta.json` | `f33e9c5e00c9dc2c6f7ad27e6fa8f76e554ccd67c58c38faaf4f46eb479264c8` |
| `assessment/src/body.html` | `f235fdddff0daec24429fbf7ad4b8f6c8251d9d662f28f3f0ac41bee6b266eed` |
| `assessment/src/direction.css` | `db17ee83b0c7055f8289e71579e7e875374553fc830a80590eb3f159d77e1fcc` |
| `assessment/src/direction.js` | `0432c7d19c767d29190576510c59dd824b78996cdf4bfc5450ef41fc7faf54c5` |
| `assessment/src/meta.json` | `e86a3a31bf2f4d1a2a72dcf8c726aefbdc6fcd7896fbf8fa789c8bfa9f572ed2` |
| `impact/src/body.html` | `202703bb3e76571719e1cd4516888ebf9746b71be5a32314f482a4b4ddc6f151` |
| `impact/src/direction.css` | `7e349a5c06c5b5ad23c067ac83a76028efbafe6b5072f870e152e59b4f6398e4` |
| `impact/src/direction.js` | `93473828b9fe6fa9090f468c86056de03937214079853cb95be799f6221a1d75` |
| `impact/src/meta.json` | `11221222a4759e2680a81f477ce06ac893d4b1a1b06182a0c021ef04a76faaac` |

## Shared-source hashes

| File | SHA-256 |
|---|---|
| `shared/chrome/header.html` | `077054be7636781944b0520524b229fc8e20fb27cfa5d942ec2462652967d666` |
| `shared/chrome/footer.html` | `2a3c56cd9162b8c7b93b3522bb3c1419ba543fd2cd11d712c607dd12e41c401d` |
| `shared/chrome/chrome.css` | `aaeaea97b67d26e320594370f73f6c35a5e14b0dbad41ab40d54267efbd15761` |
| `shared/chrome/chrome.js` | `4d15db4cbd6999a68a5b3ad64691b8f9394be7f914566f6ce147951efafce72e` |
| `component-library/styles.css` | `0f9cc27324c306f181dd2f60e4d7ecd265bbc415d656ea6cc150dc728f4bc674` |
| `component-library/script.js` | `3c6c09707975eae870221f757c5ab125a95147d3156bd421fb9f7850195cbeb0` |
| `system/tokens.css` | `acc9fc8367455f23740735e9be7a0d4597c7bcab1fef3b18edcfb494fe8705cd` |

## Controller and narrative authority hashes

| File | SHA-256 |
|---|---|
| `FABLE-5.1-WHOLE-SITE-GOLDEN-STANDARD-PLAN.md` | `84a8014ed3fbc1e4e9744932024bf9c08f5ebff6533f81fef945e533ab0b62bb` |
| `design-mapping/COMPANY-PAGE-MAP.md` | `003c6406f9e9b2bc5d2f27030529964c948a4c59e37c5f3a8ad3afce99b4cca2` |
| `packages/FS5-LANE-A-CLAUDE-WRITER.md` | `2866245cd64c2abf763d377a289510b4bddb1e233ac35ed859d4d852807feb62` |
| `tools/capture_fs5_evidence.py` | `67a7e64827a9cbe3afd36974ad2951e54e2a54d9a8817a17b87d0a54b16d4ed6` |
| `narrative/COPY-UNIT-MANIFEST.json` | `a7d8b0baabdda5a1807a74f1ea3c73c50ad5342bdd39bcee4bfaddec5a80d801` |
| `narrative/FULL-SITE-CONTENT-CONTRACT.md` | `c7068104a28fa6a2e6f104daecbdec8410ec5c719fcf00f55f47432ed03a07dc` |

## Pre-assembly checks

- Pure FS5 suite: 47 tests; 37 pass; ten evidence-package tests skip as
  designed before assembly; zero failures.
- JavaScript syntax: pass on all route and shared scripts.
- CSS `order`: absent from all six writer-lane route stylesheets.
- Copy manifest and current authority hashes: internally consistent.
- Assembler check: six structural checks pass; only expected stale generated
  output remains.

The next write to generated route output must be the controlled assembler. Any
change to the frozen source above invalidates this handoff and requires a new
hash set before browser evidence.
