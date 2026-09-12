#!/usr/bin/env node
/* Dagg golden standard — shared preview assembler
 *
 * Contract: design/golden-standard/packages/P4R6-DUAL-CUT-HOME-DIRECTIONS.md §9.
 *
 * ------------------------------------------------------------------------
 * WHAT THIS TOOL IS FOR
 * ------------------------------------------------------------------------
 * P4R6 §9 requires that the accepted global chrome be promoted into ONE
 * canonical assembly contract, that the build step assemble header,
 * composition and footer into every static output so the delivered page is
 * complete with JavaScript disabled, and that NO DIRECTION HAND-COPY header
 * or footer DOM. This tool is that build step.
 *
 * It is deliberately not a framework. It concatenates the accepted shared
 * files with one direction's own source files, writes a static `index.html`,
 * and then refuses to succeed unless the result passes every static check
 * the package names.
 *
 * ------------------------------------------------------------------------
 * DIRECTION SOURCE CONTRACT
 * ------------------------------------------------------------------------
 * A direction is any directory under `preview/golden-standard/` that
 * contains a `src/` subdirectory holding `body.html`. Discovery is a sorted
 * walk, so adding a route requires no edit to this file.
 *
 *   <route>/src/body.html      REQUIRED. The composition only — everything
 *                              that belongs between <main id="main"> and
 *                              </main>. It may not contain <main>, <html>,
 *                              <head>, <body>, the skip link, or any shared
 *                              chrome class or data attribute. Those are
 *                              rejected, which is how "composition code
 *                              without copied shared DOM" is enforced.
 *   <route>/src/direction.css  OPTIONAL. Loaded after chrome.css. May not
 *                              restyle the chrome or redeclare a token.
 *   <route>/src/direction.js   OPTIONAL. Deferred, loaded after chrome.js.
 *   <route>/src/head.html      OPTIONAL. Extra <head> lines, local refs only.
 *   <route>/src/meta.json      OPTIONAL. { title, description, lang,
 *                              brandHref, currentNavHref, css: [...],
 *                              js: [...] }.
 *
 * Output is `<route>/index.html`. Source files stay under `<route>/src/` and
 * are referenced by root-absolute URL, so nothing is copied and there is one
 * place to edit each file.
 *
 * ------------------------------------------------------------------------
 * DETERMINISM
 * ------------------------------------------------------------------------
 * The output contains no timestamp, no random value, no absolute filesystem
 * path and no build counter. Discovery and every recorded list are sorted.
 * Running the tool twice over unchanged sources produces byte-identical
 * outputs and a byte-identical manifest. `--check` proves it without writing.
 *
 * ------------------------------------------------------------------------
 * USAGE
 * ------------------------------------------------------------------------
 *   node tools/build_golden_standard_previews.mjs
 *   node tools/build_golden_standard_previews.mjs --check
 *
 * Default: assemble, write outputs and the evidence manifest, run every
 * static check. `--check`: assemble in memory, run every static check, and
 * fail if any output or the manifest on disk differs from a fresh assembly.
 *
 * Exit code 0 only when there are no failures. Failures print before
 * successes (CLAUDE.md rule 4). A machine check never overrules a visible
 * rendering failure (CLAUDE.md rule 5): this tool measures assembly only and
 * makes no visual-acceptance claim.
 *
 * ------------------------------------------------------------------------
 * A NOTE ON HOW THE CHECKS READ SOURCE
 * ------------------------------------------------------------------------
 * Several checks look for markup or code that must not exist. Every one of
 * them strips comments first, because these files document the very rules
 * they are checked against — the header partial's own comment explains that
 * it contains no inline `<svg>`, and a naive substring search would fail on
 * that sentence. A comment cannot render an icon or fetch a URL, so
 * stripping is correct rather than lenient.
 * ==================================================================== */

import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve, posix } from "node:path";
import { fileURLToPath } from "node:url";

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const SHARED_DIR = "preview/golden-standard/shared/chrome";
const SCAN_ROOT = "preview/golden-standard";
const SCAN_MAX_DEPTH = 4;

const TOKENS_CSS = "/design/golden-standard/system/tokens.css";
const CHROME_CSS = `/${SHARED_DIR}/chrome.css`;
const CHROME_JS = `/${SHARED_DIR}/chrome.js`;
const COMPONENT_CSS = "/preview/golden-standard/component-library/styles.css";
const COMPONENT_JS = "/preview/golden-standard/component-library/script.js";

const SHARED_NAMES = ["header.html", "footer.html", "chrome.css", "chrome.js"];
const HASHED_NAMES = [
  ...SHARED_NAMES,
  "tokens.css",
  "component.css",
  "component.js",
];

const MANIFEST_PATH =
  "evidence/HOME-DIRECTIONS/shared-substrate/build-manifest.json";

/* Markup a direction may not contain, because the shared chrome owns it.
   This is the mechanical form of P4R6 §9's "no direction may hand-copy
   header or footer DOM". */
const FORBIDDEN_IN_BODY = [
  "<html", "</html", "<head", "</head", "<body", "</body",
  "<main", "</main", "<!doctype",
  "chrome-header", "chrome-footer", "chrome-disclosure", "chrome-nav__",
  "data-chrome-header", "data-disclosure", "data-header-theme",
  "data-flyout", "cl-flyout", "cl-fp", "skip-link",
];

/* Selectors and declarations a direction stylesheet may not contain. The
   chrome is styled once, in one file, and tokens are declared once, in
   tokens.css. */
const FORBIDDEN_IN_DIRECTION_CSS = [
  ".chrome-", ".cl-flyout", ".cl-fp", ".cl-ico", ".cl-meta", ".cl-sr",
  ".skip-link", ":root", "@font-face",
];

/* Glyphs that may not stand alone as a control's label — the `Build+`
   failure mode P4R5 §6 rejects. `→` and `↔` are deliberately absent: they
   occur inside real accepted prose in the flyout proof states, and the rule
   only fires when a glyph IS the entire text of an element, never when it
   sits inside a sentence. */
const SYMBOL_GLYPHS = "+\\-−–—×✕✖✗✓✔▸▾▶▼›»‹«↑↓⤴↗↘⌃⌄\\^\\*·•≡⋮⋯";

/* Pictographs whose default presentation is text, not emoji. These are
   legitimate typography and appear in the accepted footer. */
const TEXT_PICTOGRAPHS = new Set(["©", "®", "™", "↔"]);

const failures = [];
const successes = [];

function fail(id, detail) {
  failures.push({ id, detail });
}
function pass(id, detail) {
  successes.push({ id, detail });
}

const sha256 = (buf) => createHash("sha256").update(buf).digest("hex");
const readBytes = (rel) => readFileSync(join(REPO_ROOT, rel));
const readText = (rel) => readBytes(rel).toString("utf8");
const exists = (rel) => {
  try {
    statSync(join(REPO_ROOT, rel));
    return true;
  } catch {
    return false;
  }
};
const isDir = (rel) => {
  try {
    return statSync(join(REPO_ROOT, rel)).isDirectory();
  } catch {
    return false;
  }
};

const stripHtmlComments = (s) => s.replace(/<!--[\s\S]*?-->/g, "");
const stripBlockComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, "");
const stripRefSuffix = (s) => s.split("#")[0].split("?")[0];

/* ==================================================================== *
 * Discovery                                                             *
 * ==================================================================== */

function discoverRoutes() {
  const found = [];
  const walk = (rel, depth) => {
    if (depth > SCAN_MAX_DEPTH) return;
    let entries;
    try {
      entries = readdirSync(join(REPO_ROOT, rel), { withFileTypes: true });
    } catch {
      return;
    }
    const dirs = entries.filter((e) => e.isDirectory()).map((e) => e.name).sort();
    if (dirs.includes("src") && exists(posix.join(rel, "src", "body.html"))) {
      found.push(rel);
    }
    for (const name of dirs) {
      if (name === "src") continue;
      walk(posix.join(rel, name), depth + 1);
    }
  };
  walk(SCAN_ROOT, 0);
  return found.sort();
}

/* ==================================================================== *
 * Reference collection and classification                               *
 * ==================================================================== */

function collectHtmlRefs(html) {
  const refs = [];
  const re = /(?:href|src)\s*=\s*"([^"]*)"/g;
  let m;
  while ((m = re.exec(stripHtmlComments(html))) !== null) refs.push(m[1]);
  return refs;
}

function collectCssRefs(css) {
  const refs = [];
  const re = /url\(\s*(?:"([^"]*)"|'([^']*)'|([^)'"\s]+))\s*\)/g;
  let m;
  while ((m = re.exec(stripBlockComments(css))) !== null) {
    refs.push(m[1] ?? m[2] ?? m[3]);
  }
  return refs;
}

function isRemote(ref) {
  if (/^(?:mailto:|tel:|data:)/i.test(ref)) return false;
  return /^(?:[a-z][a-z0-9+.-]*:)?\/\//i.test(ref) || /^[a-z][a-z0-9+.-]*:/i.test(ref);
}

function checkNoRemoteRefs(label, refs) {
  const remote = [...new Set(refs.filter(isRemote))];
  if (remote.length) {
    fail("remote-reference",
      `${label} references non-local URLs, which the specimen contract forbids: ${remote.join(", ")}`);
  }
}

/* A local ref must resolve to a real file; a directory ref must resolve to a
   directory holding index.html. `plannedOutputs` holds the outputs this same
   build produces, so a route linking to a sibling route it is emitting in
   the same run is not a false 404 on a first build. */
function checkLocalRefsResolve(label, refs, baseDirRel, plannedOutputs) {
  const missing = [];
  for (const ref of [...new Set(refs)]) {
    if (!ref || isRemote(ref) || ref.startsWith("#") || /^(?:mailto:|tel:|data:)/i.test(ref)) {
      continue;
    }
    const path = ref.split("#")[0].split("?")[0];
    if (!path) continue;
    const rel = path.startsWith("/")
      ? path.slice(1)
      : posix.normalize(posix.join(baseDirRel, path));
    const candidate = rel.endsWith("/") ? posix.join(rel, "index.html") : rel;
    if (plannedOutputs.has(candidate)) continue;
    if (exists(candidate) && !isDir(candidate)) continue;
    if (isDir(rel)) {
      const index = posix.join(rel, "index.html");
      if (plannedOutputs.has(index) || exists(index)) continue;
    }
    missing.push(`${ref} -> ${candidate}`);
  }
  if (missing.length) {
    fail("unresolved-local-reference",
      `${label} references files that do not exist, so the browser would 404: ${missing.join("; ")}`);
  }
}

/* ==================================================================== *
 * Static content checks                                                 *
 * ==================================================================== */

function checkNoInlineSvg(label, html) {
  const stripped = stripHtmlComments(html);
  const lower = stripped.toLowerCase();
  const hits = ["<svg", "<use", "<symbol", "<image "].filter((t) => lower.includes(t));
  if (stripped.includes("data:image/svg")) hits.push("data:image/svg");
  if (hits.length) {
    fail("inline-svg",
      `${label} contains inline vector markup, which P4R5 §4.1 forbids: ${hits.join(", ")}. ` +
      `Icons must be vendored Lucide files referenced as <img>.`);
  }
}

function checkNoTextSymbolIcons(label, html) {
  const stripped = stripHtmlComments(html);
  const hits = [];

  const picto = [...new Set(
    [...stripped.matchAll(/\p{Extended_Pictographic}/gu)]
      .map((m) => m[0])
      .filter((c) => !TEXT_PICTOGRAPHS.has(c))
  )];
  if (picto.length) hits.push(`emoji or pictograph: ${picto.join(" ")}`);
  if (stripped.includes("️")) {
    hits.push("U+FE0F emoji variation selector");
  }

  const runRe = new RegExp(`>\\s*([${SYMBOL_GLYPHS}]+)\\s*<`, "gu");
  let m;
  while ((m = runRe.exec(stripped)) !== null) {
    hits.push(`text symbol used as a control label: "${m[1]}"`);
  }

  if (hits.length) {
    fail("text-symbol-icon",
      `${label} uses symbols where a real icon is required (P4R5 §6): ${hits.join("; ")}`);
  }
}

function checkNoCopiedSharedDom(label, body) {
  const lower = stripHtmlComments(body).toLowerCase();
  const hits = FORBIDDEN_IN_BODY.filter((t) => lower.includes(t));
  if (hits.length) {
    fail("copied-shared-dom",
      `${label} contains markup the shared chrome owns (P4R6 §9): ${hits.join(", ")}. ` +
      `Remove it — the build tool inserts the header, <main id="main"> and the footer.`);
  }
}

function checkDirectionCss(label, css) {
  const stripped = stripBlockComments(css);
  const hits = FORBIDDEN_IN_DIRECTION_CSS.filter((t) => stripped.includes(t));
  if (hits.length) {
    fail("direction-css-overreach",
      `${label} declares things only the shared layer may declare: ${hits.join(", ")}. ` +
      `The chrome is styled once in chrome.css and tokens are declared once in tokens.css.`);
  }
}

/* Asset rules that apply to every script the page loads, chrome.js included. */
function checkScriptAssets(label, js) {
  const stripped = stripBlockComments(js);
  if (/["'`]\s*https?:\/\//.test(stripped)) {
    fail("remote-reference", `${label} contains a remote URL literal.`);
  }
  if (/createElementNS/.test(stripped) || /["'`][^"'`]{0,60}<svg/.test(stripped)) {
    fail("inline-svg", `${label} constructs SVG in script, which P4R5 §4.1 forbids.`);
  }
}

/* Ownership rules that apply only to a direction script. chrome.js legitimately
   writes cl-enhanced and cl-booting; it owns them. */
function checkDirectionJs(label, js) {
  checkScriptAssets(label, js);
  const stripped = stripBlockComments(js);
  if (/classList\s*\.\s*(?:add|remove|toggle)\s*\(\s*["'](?:cl-enhanced|cl-booting)["']/.test(stripped)) {
    fail("direction-js-overreach",
      `${label} writes cl-enhanced or cl-booting. chrome.js owns both classes (see its header comment).`);
  }
}

/* No-JS completeness, measured on the emitted bytes rather than asserted:
   the header, its nav routes, the flyout destinations, the CTA and the whole
   footer must be present as static markup, and no <script> may sit above the
   footer's closing tag. */
function checkNoJsCompleteness(label, html) {
  const required = [
    ['<header class="chrome-header"', "header element"],
    ['class="skip-link"', "skip link"],
    ['<main id="main"', "main landmark"],
    ['href="/preview/golden-standard/routes/transformation/"', "Transformation route"],
    ['href="/preview/golden-standard/routes/workgraph/"', "WorkGraph route"],
    ['href="/preview/golden-standard/routes/build/"', "Build flyout destinations"],
    ['href="/preview/golden-standard/routes/trust/"', "Trust destination"],
    /* Impact is intentionally not a shell requirement. The accepted content
       contract omits the route and every shell/contextual link atomically
       until at least one proof passes the V/C publication gate. */
    ['href="/preview/golden-standard/routes/company/"', "Company route"],
    ['class="chrome-header__cta"', "persistent assessment action"],
    ["One operating decision becomes a buildable, governed system.",
      "first flyout proof state, which carries the conclusion"],
    ['<footer class="chrome-footer on-ink"', "footer element"],
    ['href="mailto:hello@dagg.ai"', "footer contact route"],
  ];
  const missing = required.filter(([needle]) => !html.includes(needle)).map(([, name]) => name);
  if (missing.length) {
    fail("no-js-incomplete",
      `${label} would be incomplete with JavaScript disabled; no static markup for: ${missing.join(", ")}`);
  }
  const footerClose = html.indexOf("</footer>");
  const firstScript = html.indexOf("<script");
  if (firstScript !== -1 && footerClose !== -1 && firstScript < footerClose) {
    fail("script-above-footer",
      `${label} loads a script before the footer closes, so the static page is not self-sufficient.`);
  }
}

/* ==================================================================== *
 * Assembly                                                              *
 * ==================================================================== */

function loadShared() {
  const shared = {};
  for (const name of SHARED_NAMES) {
    const rel = posix.join(SHARED_DIR, name);
    if (!exists(rel)) {
      fail("missing-shared-partial", `Required shared file is absent: ${rel}`);
      return null;
    }
    const bytes = readBytes(rel);
    shared[name] = { rel, bytes, text: bytes.toString("utf8"), sha256: sha256(bytes) };
  }
  const tokensRel = TOKENS_CSS.slice(1);
  if (!exists(tokensRel)) {
    fail("missing-shared-partial", `Required token file is absent: ${tokensRel}`);
    return null;
  }
  const tokenBytes = readBytes(tokensRel);
  shared["tokens.css"] = {
    rel: tokensRel,
    bytes: tokenBytes,
    text: tokenBytes.toString("utf8"),
    sha256: sha256(tokenBytes),
  };

  const componentFiles = [
    ["component.css", COMPONENT_CSS.slice(1)],
    ["component.js", COMPONENT_JS.slice(1)],
  ];
  for (const [key, rel] of componentFiles) {
    if (!exists(rel)) {
      fail("missing-shared-partial", `Required passed P4R5 component file is absent: ${rel}`);
      return null;
    }
    const bytes = readBytes(rel);
    shared[key] = { rel, bytes, text: bytes.toString("utf8"), sha256: sha256(bytes) };
  }
  return shared;
}

function loadMeta(routeRel) {
  const rel = posix.join(routeRel, "src", "meta.json");
  if (!exists(rel)) return {};
  try {
    return JSON.parse(readText(rel));
  } catch (error) {
    fail("bad-meta-json", `${rel} is not valid JSON: ${error.message}`);
    return {};
  }
}

function assemble(routeRel, shared) {
  const srcRel = posix.join(routeRel, "src");
  const meta = loadMeta(routeRel);

  const body = readText(posix.join(srcRel, "body.html")).replace(/\s+$/, "");
  checkNoCopiedSharedDom(`${srcRel}/body.html`, body);

  const declaredCss = meta.css
    ?? (exists(posix.join(srcRel, "direction.css")) ? ["direction.css"] : []);
  const declaredJs = meta.js
    ?? (exists(posix.join(srcRel, "direction.js")) ? ["direction.js"] : []);
  const cssFiles = declaredCss.slice().sort();
  const jsFiles = declaredJs.slice().sort();

  for (const name of [...cssFiles, ...jsFiles]) {
    const rel = posix.join(srcRel, stripRefSuffix(name));
    if (!exists(rel)) {
      fail("missing-direction-file", `${routeRel} declares ${name} but ${rel} does not exist.`);
    }
  }

  for (const name of cssFiles) {
    const rel = posix.join(srcRel, stripRefSuffix(name));
    if (exists(rel)) checkDirectionCss(rel, readText(rel));
  }
  for (const name of jsFiles) {
    const rel = posix.join(srcRel, stripRefSuffix(name));
    if (exists(rel)) checkDirectionJs(rel, readText(rel));
  }

  const headExtraRel = posix.join(srcRel, "head.html");
  const headExtra = exists(headExtraRel) ? readText(headExtraRel).replace(/\s+$/, "") : "";

  const lang = meta.lang ?? "en";
  const title = meta.title ?? "Dagg";
  const description = meta.description ?? "";
  const brandHref = meta.brandHref ?? `/${routeRel}/`;
  const mainDataHooks = meta.mainDataHooks ?? [];
  if (!Array.isArray(mainDataHooks) || mainDataHooks.some((hook) =>
    typeof hook !== "string" || !/^data-[a-z0-9-]+$/.test(hook))) {
    fail("invalid-main-data-hook",
      `${routeRel} mainDataHooks must be an array of lowercase data-* attribute names.`);
  }
  const mainHookText = mainDataHooks.map((hook) => ` ${hook}`).join("");

  let header = shared["header.html"].text
    .replace(/\{\{BRAND_HREF\}\}/g, brandHref)
    .replace(/\s+$/, "");
  let footer = shared["footer.html"].text.replace(/\s+$/, "");

  const currentNavHref = meta.currentNavHref ?? "";
  if (currentNavHref) {
    const needle = `href="${currentNavHref}"`;
    if (!header.includes(needle)) {
      fail("missing-current-nav-target",
        `${routeRel} declares currentNavHref ${currentNavHref}, but the shared header has no exact matching link.`);
    } else {
      header = header.split(needle).join(`${needle} aria-current="page"`);
      if (footer.includes(needle)) {
        footer = footer.split(needle).join(`${needle} aria-current="page"`);
      }
    }
  }

  if (/\{\{[A-Z_]+\}\}/.test(header) || /\{\{[A-Z_]+\}\}/.test(footer)) {
    fail("unresolved-token",
      `A shared partial still contains an unresolved {{TOKEN}} after assembling ${routeRel}.`);
  }

  const lines = [];
  lines.push("<!doctype html>");
  lines.push(`<html lang="${lang}">`);
  lines.push("<head>");
  lines.push('  <meta charset="utf-8">');
  lines.push('  <meta name="viewport" content="width=device-width, initial-scale=1">');
  lines.push(`  <title>${title}</title>`);
  lines.push(`  <meta name="description" content="${description}">`);
  lines.push('  <link rel="icon" href="/assets/dagg-symbol.png">');
  lines.push('  <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/golden-standard/geist/Geist-Variable.woff2" crossorigin>');
  lines.push('  <link rel="preload" as="font" type="font/woff2" href="/assets/fonts/golden-standard/newsreader/Newsreader-Variable.woff2" crossorigin>');
  lines.push(`  <link rel="stylesheet" href="${TOKENS_CSS}">`);
  lines.push(`  <link rel="stylesheet" href="${CHROME_CSS}">`);
  lines.push(`  <link rel="stylesheet" href="${COMPONENT_CSS}">`);
  for (const name of cssFiles) {
    lines.push(`  <link rel="stylesheet" href="/${posix.join(srcRel, name)}">`);
  }
  if (headExtra) lines.push(headExtra);
  lines.push("</head>");
  lines.push("<body>");
  lines.push("  <!-- Shared chrome, assembled by tools/build_golden_standard_previews.mjs");
  lines.push(`       from ${SHARED_DIR}/header.html. Do not edit here; edit the partial. -->`);
  lines.push(header);
  lines.push("");
  lines.push(`  <main id="main"${mainHookText}>`);
  lines.push(body);
  lines.push("  </main>");
  lines.push("");
  lines.push(`  <!-- Shared chrome, from ${SHARED_DIR}/footer.html. -->`);
  lines.push(footer);
  lines.push("");
  lines.push(`  <script src="${CHROME_JS}" defer></script>`);
  lines.push(`  <script src="${COMPONENT_JS}" defer></script>`);
  for (const name of jsFiles) {
    lines.push(`  <script src="/${posix.join(srcRel, name)}" defer></script>`);
  }
  lines.push("</body>");
  lines.push("</html>");

  const html = lines.join("\n") + "\n";
  const outRel = posix.join(routeRel, "index.html");

  checkNoInlineSvg(outRel, html);
  checkNoTextSymbolIcons(outRel, html);
  checkNoJsCompleteness(outRel, html);

  /* Reference resolution is deferred until after the write step, so a route
     linking to another route this same build emits is not a false 404. */
  const refJobs = [{ label: outRel, refs: collectHtmlRefs(html), base: routeRel }];
  if (headExtra) {
    refJobs.push({ label: headExtraRel, refs: collectHtmlRefs(headExtra), base: routeRel });
  }
  const cssRels = [
    shared["tokens.css"].rel,
    shared["chrome.css"].rel,
    shared["component.css"].rel,
    ...cssFiles.map((n) => posix.join(srcRel, stripRefSuffix(n))),
  ];
  for (const cssRel of cssRels) {
    if (!exists(cssRel)) continue;
    refJobs.push({
      label: cssRel,
      refs: collectCssRefs(readText(cssRel)),
      base: posix.dirname(cssRel),
    });
  }

  checkScriptAssets(shared["chrome.js"].rel, shared["chrome.js"].text);
  checkScriptAssets(shared["component.js"].rel, shared["component.js"].text);

  return {
    route: routeRel,
    output: outRel,
    html,
    sha256: sha256(Buffer.from(html, "utf8")),
    bytes: Buffer.byteLength(html, "utf8"),
    brandHref,
    currentNavHref,
    directionCss: cssFiles.map((n) => posix.join(srcRel, stripRefSuffix(n))),
    directionJs: jsFiles.map((n) => posix.join(srcRel, stripRefSuffix(n))),
    refJobs,
    sharedHashes: Object.fromEntries(HASHED_NAMES.map((n) => [n, shared[n].sha256])),
  };
}

/* ==================================================================== *
 * Main                                                                  *
 * ==================================================================== */

const checkOnly = process.argv.includes("--check");

const shared = loadShared();
const routes = shared ? discoverRoutes() : [];
const pages = [];

if (shared) {
  if (!routes.length) {
    fail("no-routes",
      `No direction sources found. Expected at least one ${SCAN_ROOT}/**/src/body.html.`);
  }
  for (const routeRel of routes) pages.push(assemble(routeRel, shared));
}

/* P4R6 §9: unequal shared hashes across pages is a P0 failure. */
if (pages.length) {
  const reference = JSON.stringify(pages[0].sharedHashes);
  const divergent = pages.filter((p) => JSON.stringify(p.sharedHashes) !== reference);
  if (divergent.length) {
    fail("shared-hash-inequality",
      `P0. These pages did not assemble from identical shared files: ${divergent.map((p) => p.output).join(", ")}`);
  } else {
    pass("shared-hash-equality",
      `All ${pages.length} assembled page(s) record identical shared-file hashes.`);
  }
}

const manifest = shared && pages.length
  ? {
      contract: "design/golden-standard/packages/P4R6-DUAL-CUT-HOME-DIRECTIONS.md#9",
      tool: "tools/build_golden_standard_previews.mjs",
      deterministic: true,
      note: "No timestamp is recorded. Two runs over unchanged sources must produce this file byte-identically.",
      shared: Object.fromEntries(HASHED_NAMES.map((n) => [
        n, { path: shared[n].rel, sha256: shared[n].sha256, bytes: shared[n].bytes.length },
      ])),
      headContract: {
        stylesheetOrder: [TOKENS_CSS, CHROME_CSS, COMPONENT_CSS, "<route>/src/direction.css"],
        scriptOrder: [CHROME_JS, COMPONENT_JS, "<route>/src/direction.js"],
        mainLandmark: '<main id="main"',
      },
      pages: pages.map((p) => ({
        route: p.route,
        output: p.output,
        sha256: p.sha256,
        bytes: p.bytes,
        brandHref: p.brandHref,
        currentNavHref: p.currentNavHref,
        directionCss: p.directionCss,
        directionJs: p.directionJs,
        sharedHashes: p.sharedHashes,
      })),
    }
  : null;

const manifestText = manifest ? JSON.stringify(manifest, null, 2) + "\n" : null;

const targets = manifestText
  ? [...pages.map((p) => ({ rel: p.output, text: p.html })),
     { rel: MANIFEST_PATH, text: manifestText }]
  : [];
const plannedOutputs = new Set(targets.map((t) => t.rel));

if (targets.length) {
  if (checkOnly) {
    const stale = [];
    for (const t of targets) {
      if (!exists(t.rel)) { stale.push(`${t.rel} (absent)`); continue; }
      if (readText(t.rel) !== t.text) stale.push(`${t.rel} (differs)`);
    }
    if (stale.length) {
      fail("outputs-stale",
        `--check: on-disk outputs do not match a fresh assembly: ${stale.join(", ")}`);
    } else {
      pass("outputs-current",
        `--check: all ${targets.length} output(s) on disk are byte-identical to a fresh assembly.`);
    }
  } else {
    for (const t of targets) {
      mkdirSync(join(REPO_ROOT, posix.dirname(t.rel)), { recursive: true });
      writeFileSync(join(REPO_ROOT, t.rel), t.text, "utf8");
    }
    pass("outputs-written", `Wrote ${targets.length} file(s).`);
  }
}

/* Reference resolution, now that every output exists or is accounted for. */
for (const page of pages) {
  for (const job of page.refJobs) {
    checkNoRemoteRefs(job.label, job.refs);
    checkLocalRefsResolve(job.label, job.refs, job.base, plannedOutputs);
  }
}
if (pages.length && !failures.some((f) =>
  f.id === "remote-reference" || f.id === "unresolved-local-reference")) {
  pass("local-refs-only",
    "Every stylesheet, script, font, icon and route reference is local and resolves to a real file.");
}
if (pages.length && !failures.some((f) => f.id === "inline-svg")) {
  pass("no-inline-vector-markup",
    "No inline <svg>, <use>, <symbol> or data:image/svg in any emitted page or shared script.");
}
if (pages.length && !failures.some((f) => f.id === "text-symbol-icon")) {
  pass("no-text-symbol-icons",
    "No emoji, and no symbol glyph standing alone as a control label, in any emitted page.");
}
if (pages.length && !failures.some((f) => f.id === "no-js-incomplete" || f.id === "script-above-footer")) {
  pass("no-js-complete",
    "Every emitted page carries complete static header, nav, flyout, CTA and footer markup above its first script.");
}
if (pages.length && !failures.some((f) => f.id === "copied-shared-dom")) {
  pass("no-copied-shared-dom",
    "No direction body.html contains shared header, footer, main or flyout markup.");
}

/* ==================================================================== *
 * Report. Failures first (CLAUDE.md rule 4).                            *
 * ==================================================================== */

console.log(`build_golden_standard_previews — mode: ${checkOnly ? "check" : "build"}`);
console.log(`repo root: ${relative(process.cwd(), REPO_ROOT) || "."}`);
console.log("");

if (failures.length) {
  console.log(`FAILURES (${failures.length})`);
  for (const f of failures) console.log(`  [${f.id}] ${f.detail}`);
  console.log("");
}

if (shared) {
  console.log("SHARED FILES (sha256, bytes, path)");
  for (const name of HASHED_NAMES) {
    console.log(`  ${shared[name].sha256}  ${String(shared[name].bytes.length).padStart(7)}  ${shared[name].rel}`);
  }
  console.log("");
}

if (pages.length) {
  console.log(`ASSEMBLED PAGES (${pages.length})`);
  for (const p of pages) {
    console.log(`  ${p.sha256}  ${String(p.bytes).padStart(7)}  ${p.output}`);
  }
  console.log("");
}

if (successes.length) {
  console.log(`CHECKS PASSED (${successes.length})`);
  for (const s of successes) console.log(`  [${s.id}] ${s.detail}`);
  console.log("");
}

console.log(
  failures.length
    ? `RESULT: FAIL — ${failures.length} failure(s).`
    : "RESULT: PASS — assembly checks only."
);
console.log(
  "This tool measures assembly. It renders nothing and makes no visual-acceptance claim (CLAUDE.md rule 5)."
);

process.exit(failures.length ? 1 : 0);
