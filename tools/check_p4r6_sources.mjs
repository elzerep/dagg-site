#!/usr/bin/env node
/* Static P4R6 first-cut eligibility. Browser and visual acceptance are separate. */

import { readFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(join(root, rel), "utf8");
const matrix = JSON.parse(read("design/golden-standard/packages/P4R6-ACCEPTANCE-MATRIX.json"));
const registry = JSON.parse(read(matrix.sharedSources.registry));
const assets = new Map(registry.assets.map((asset) => [asset.id, asset]));
const availableOnly = process.argv.includes("--available");
const resolvedOnly = process.argv.includes("--resolved");
const routesToCheck = resolvedOnly ? (matrix.resolvedRoutes ?? []) : matrix.routes;

const failures = [];
const results = [];
const fail = (route, id, detail) => failures.push({ route, id, detail });
const stripComments = (value) => value
  .replace(/<!--[\s\S]*?-->/g, " ")
  .replace(/\/\*[\s\S]*?\*\//g, " ");
const decode = (value) => value
  .replace(/&amp;/g, "&")
  .replace(/&lt;/g, "<")
  .replace(/&gt;/g, ">")
  .replace(/&quot;/g, '"')
  .replace(/&#39;|&apos;/g, "'")
  .replace(/&mdash;|&#8212;/g, "—")
  .replace(/&ndash;|&#8211;/g, "–")
  .replace(/&nbsp;/g, " ");
const textOnly = (html) => decode(stripComments(html)
  .replace(/<script\b[\s\S]*?<\/script>/gi, " ")
  .replace(/<style\b[\s\S]*?<\/style>/gi, " ")
  .replace(/<[^>]+>/g, " "))
  .replace(/\s+/g, " ")
  .trim();
const words = (text) => text.match(/[\p{L}\p{N}][\p{L}\p{N}'’-]*/gu) ?? [];

for (const route of routesToCheck) {
  const rel = route.path;
  const src = `${rel}/src`;
  const required = ["body.html", "direction.css", "direction.js", "meta.json"];
  const missing = required.filter((name) => !existsSync(join(root, src, name)));
  if (missing.length) {
    if (!availableOnly) fail(rel, "missing-source", missing.join(", "));
    continue;
  }

  const body = read(`${src}/body.html`);
  const css = read(`${src}/direction.css`);
  const js = read(`${src}/direction.js`);
  let meta = {};
  try { meta = JSON.parse(read(`${src}/meta.json`)); }
  catch (error) { fail(rel, "bad-meta", error.message); }

  const contract = {
    ...matrix.directions[route.direction],
    ...(route.leadOverride ? { lead: route.leadOverride } : {}),
  };
  const cleanBody = stripComments(body);
  const visibleText = textOnly(body);
  const wordCount = words(visibleText).length;

  const actOrder = [...cleanBody.matchAll(/\bdata-act\s*=\s*["']([^"']+)["']/gi)]
    .map((match) => match[1]);
  if (JSON.stringify(actOrder) !== JSON.stringify(matrix.nineActs)) {
    fail(rel, "nine-act-order", `expected ${matrix.nineActs.join(" > ")}; got ${actOrder.join(" > ")}`);
  }

  const h1 = cleanBody.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i);
  const h1Text = h1 ? textOnly(h1[1]) : "";
  if (h1Text !== contract.h1) fail(rel, "opening-h1", `expected "${contract.h1}"; got "${h1Text}"`);
  if (!visibleText.includes(contract.lead)) fail(rel, "opening-lead", "exact direction lead is missing");

  if (wordCount < contract.visibleWordMin || wordCount > contract.visibleWordMax) {
    fail(rel, "copy-budget", `${wordCount} DOM-visible words; expected ${contract.visibleWordMin}-${contract.visibleWordMax}`);
  }

  const selected = [contract.selectedDesktopAsset, contract.selectedMobileAsset]
    .map((id) => assets.get(id));
  selected.forEach((asset, index) => {
    if (!asset) {
      fail(rel, "unknown-selected-asset", index ? contract.selectedMobileAsset : contract.selectedDesktopAsset);
    } else if (!cleanBody.includes(`/${asset.path}`)) {
      fail(rel, "selected-asset-missing", `${asset.id} -> /${asset.path}`);
    }
  });
  if (!/<picture\b/i.test(cleanBody)) fail(rel, "responsive-picture", "no <picture> element");

  const forbiddenMarkup = ["<header", "<footer", "<main", "<svg", "<style", "<script"]
    .filter((needle) => cleanBody.toLowerCase().includes(needle));
  if (forbiddenMarkup.length) fail(rel, "owned-markup-overreach", forbiddenMarkup.join(", "));

  const remoteRefs = [...cleanBody.matchAll(/(?:src|href)\s*=\s*["']([^"']+)["']/gi)]
    .map((match) => match[1])
    .filter((ref) => /^(?:https?:)?\/\//i.test(ref));
  if (remoteRefs.length) fail(rel, "remote-reference", [...new Set(remoteRefs)].join(", "));

  for (const term of matrix.forbiddenPublicCopy) {
    if (new RegExp(`\\b${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(visibleText)) {
      fail(rel, "forbidden-public-copy", term);
    }
  }

  if (resolvedOnly && /\bhuman release\b/i.test(`${visibleText} ${js}`)) {
    fail(rel, "p1r2-release-wording",
      'P1R2 requires "human approval for release"; "human release" remains.');
  }
  if (resolvedOnly && route.direction === "A") {
    const disclosure = "All artifacts on this page are constructed examples, not client data or production deployments.";
    if (!visibleText.includes(disclosure)) {
      fail(rel, "page-provenance-disclosure", `missing exact disclosure: ${disclosure}`);
    }
  }
  if (resolvedOnly && route.direction === "B") {
    const fieldCaption = cleanBody.match(
      /<figcaption\b[^>]*class=["'][^"']*b-field-caption[^"']*["'][^>]*>([\s\S]*?)<\/figcaption>/i
    );
    if (!fieldCaption || !/Decision Field/i.test(textOnly(fieldCaption[1]))) {
      fail(rel, "image-role-label",
        "B04 must be captioned as Decision Field; its adjacent operating record is a separate HTML mechanism.");
    }
    if (fieldCaption && /Operating record WG-034/i.test(textOnly(fieldCaption[1]))) {
      fail(rel, "image-role-mislabel",
        "B04 is Decision Field with restrained Machine Signal, not an operating-record screenshot.");
    }
  }

  const ids = [...cleanBody.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi)].map((match) => match[1]);
  const duplicateIds = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
  if (duplicateIds.length) fail(rel, "duplicate-id", duplicateIds.join(", "));

  const cssClean = stripComments(css);
  const cssOverreach = [":root", "@font-face", ".chrome-", ".cl-flyout", ".cl-fp", ".skip-link"]
    .filter((needle) => cssClean.includes(needle));
  if (cssOverreach.length) fail(rel, "css-overreach", cssOverreach.join(", "));
  if (/url\(\s*["']?(?:https?:)?\/\//i.test(cssClean)) fail(rel, "remote-css", "remote url() reference");

  const jsClean = stripComments(js);
  if (/createElementNS|<svg|data:image\/svg/i.test(jsClean)) fail(rel, "script-vector", "inline vector construction");
  if (/https?:\/\//i.test(jsClean)) fail(rel, "remote-script", "remote URL literal");
  if (/classList\s*\.\s*(?:add|remove|toggle)\s*\(\s*["'](?:cl-enhanced|cl-booting)["']/i.test(jsClean)) {
    fail(rel, "script-overreach", "direction script writes shared enhancement classes");
  }

  if (meta.css && JSON.stringify(meta.css) !== JSON.stringify(["direction.css"])) {
    fail(rel, "meta-css", `expected ["direction.css"]`);
  }
  if (meta.js && JSON.stringify(meta.js) !== JSON.stringify(["direction.js"])) {
    fail(rel, "meta-js", `expected ["direction.js"]`);
  }

  if (resolvedOnly) {
    const review = `evidence/HOME-DIRECTIONS/cross-review-${route.direction.toLowerCase()}.json`;
    if (!existsSync(join(root, review))) fail(rel, "missing-cross-review", review);
  }

  results.push({ route: rel, direction: route.direction, builder: route.builder, wordCount, actOrder });
}

console.log(JSON.stringify({
  mode: resolvedOnly ? "resolved" : "first-cuts",
  status: failures.length ? "FAIL" : (results.length === routesToCheck.length ? "PASS" : "PARTIAL"),
  checked: results.length,
  expected: routesToCheck.length,
  failures,
  routes: results,
}, null, 2));

process.exit(failures.length ? 1 : 0);
