# Vendored fonts — Dagg golden standard (P2)

All three families are open source under the SIL Open Font License 1.1. Each
license file is stored beside the font it covers. Nothing here is fetched at
runtime: `design/golden-standard/system/tokens.css` references these files by
absolute local path and the golden-standard specimen makes no remote request.

Downloaded 2026-08-30.

---

## Geist

| | |
|---|---|
| Family | Geist |
| Upstream | https://github.com/vercel/geist-font |
| File taken | `packages/next/dist/fonts/geist-sans/Geist-Variable.woff2` |
| Upstream commit for that path | `a0a06a3d916dcf92fe96f12051a124f89056b36a` (2026-04-02) |
| Vendored as | `geist/Geist-Variable.woff2` |
| SHA-256 | `2ffebe993e969069a9789d15164b7715d42491b5835516c5e3b935d5f81b05f1` |
| Bytes | 69,760 |
| Axes | `wght` 100–900 (default 400) |
| Modification | none — the upstream WOFF2 byte for byte |
| License | `geist/OFL.txt` (SHA-256 `c683bfbcc7e087f5d37a54ef628f10387c451a83ddc459b151403a164ac46c90`), copied from the repository root at commit `c40c1aec7e72b9ebdce65a4fccd03cb3950a359b`. `geist/LICENSE.txt` (SHA-256 `930853ee1daa68554d9e35c8a9175affb74f699fad9a5da6ee5ebe76379d9137`) is the same repository's `LICENSE.txt`, which names Vercel and basement.studio. |

## JetBrains Mono

| | |
|---|---|
| Family | JetBrains Mono |
| Upstream | https://github.com/JetBrains/JetBrainsMono |
| File taken | `fonts/webfonts/JetBrainsMono[wght].woff2` |
| Upstream commit for that path | `02bb50b082dad9ef8a0f33ac393839202b760223` (2024-08-08) |
| Vendored as | `jetbrains-mono/JetBrainsMono-Variable.woff2` |
| SHA-256 | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| Bytes | 113,672 |
| Axes | `wght` 100–800 (default 400) |
| Modification | renamed only. The brackets in the upstream filename need percent-encoding in a CSS `url()`, so the file was renamed to `JetBrainsMono-Variable.woff2`. The bytes are unchanged. |
| License | `jetbrains-mono/OFL.txt` (SHA-256 `a76abf002c49097d146e86740a3105a5d00450b1592e820a1109a8c5680cd697`), from the repository root at commit `61cf0cedc2d9d29efcab968e97707d6899133e68`. |

## Newsreader

| | |
|---|---|
| Family | Newsreader |
| Designer/upstream project | Production Type — https://github.com/productiontype/Newsreader |
| Distribution taken from | https://github.com/google/fonts, `ofl/newsreader/` |
| File taken | `ofl/newsreader/Newsreader[opsz,wght].ttf` |
| Upstream commit for that path | `991ce1de6075188e6b8977a5aa9fcd3610a4e946` (2020-12-09) |
| Source SHA-256 | `8a08d13f8a6c0d51be379a60af84f945f65369a67e509ee3c3bdcc421254d7c1` (451,664 bytes) |
| Vendored as | `newsreader/Newsreader-Variable.woff2` |
| SHA-256 | `f25206ca663fd7dcf9c5305a2fa9767acfe354b284238232dce9a4a0383ff9ac` |
| Bytes | 215,264 |
| Axes | `wght` 200–800 (default 400), `opsz` 6–72 (default 18) |
| Modification | container format only. Google Fonts publishes Newsreader as TTF; it was recompressed to WOFF2 with no subsetting, no axis pinning and no outline change. Glyph coverage, axes and name table are the upstream ones. |
| License | `newsreader/OFL.txt` (SHA-256 `fdfad38143ec470553cae82a1e45320bdd1b9ec70415d37bd0171051d8a4ded8`), from the same directory and commit. |

### The Newsreader conversion, exactly

```
python3 -m venv /tmp/dagg-p2-fonts
/tmp/dagg-p2-fonts/bin/pip install "fonttools[woff]"     # fonttools 4.63.0 + brotli
/tmp/dagg-p2-fonts/bin/python - <<'PY'
from fontTools.ttLib import TTFont
f = TTFont("Newsreader[opsz,wght].ttf")
f.flavor = "woff2"
f.save("Newsreader-Variable.woff2")
PY
```

Re-running this on the source TTF named above reproduces the vendored file's
glyph set and axes. WOFF2 is a Brotli container, so a byte-identical result
also depends on the fontTools and Brotli versions; the SHA-256 above records
what was actually vendored.

---

## Totals against the P2 budget

| | Bytes |
|---|---:|
| Geist | 69,760 |
| JetBrains Mono | 113,672 |
| Newsreader | 215,264 |
| **Combined WOFF2** | **398,696** |
| P2 budget | 768,000 (750 KB) |

No italic is vendored. The foundation uses no italic, and `font-synthesis`
is left at its default, so no synthetic oblique is drawn either. If P4 needs
Newsreader Italic, it comes from `ofl/newsreader/Newsreader-Italic[opsz,wght].ttf`
in the same upstream directory and adds roughly 190 KB.
