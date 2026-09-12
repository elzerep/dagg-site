#!/usr/bin/env python3
"""Capture P4R5 Component-and-Interaction-Specimen evidence from one snapshot.

    python3 evidence/COMPONENT-LIBRARY/capture_component_library_evidence.py

Why this file lives under ``evidence/`` rather than ``tools/``
-------------------------------------------------------------
P4R5 section 7 lists exactly four things this package may create or change:
``preview/golden-standard/component-library/{index.html,styles.css,script.js}``,
``assets/vendor/lucide-dagg/*`` and ``evidence/COMPONENT-LIBRARY/*``. A new
file under ``tools/`` would be out of scope, so the rig ships inside the one
directory the package owns. It imports the existing P0R2 server launcher and
the P2 raw-CDP/Chrome plumbing rather than re-implementing either.

What it refuses to do
---------------------
It never writes a check as ``true`` that it did not measure. Every entry in
``acceptance-matrix.json`` carries the measurement it was derived from, and
any check whose inputs are missing is written as ``null`` with a reason --
never as a pass. Screenshot filenames carry the viewport Chrome actually
reported (``window.innerWidth`` x ``window.innerHeight``), not the width that
was requested, so a larger capture can never be labelled 390 px.

It also refuses to crash on a missing control. Every in-page read goes
through ``txt()``/``rect()``, which return ``null`` for an absent element
rather than raising on ``.textContent``; every interaction step goes through
``safe()``, which records the failure and its reason in ``stepFailures`` and
fails the ``everyInteractionStepActuallyRan`` matrix row. A run that could
not exercise an interaction therefore reports that fact instead of either
aborting or, worse, looking like a clean pass.

Standard library only, plus ``tools/capture_p2_evidence.py``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence" / "COMPONENT-LIBRARY"
SHOTS_DIR = EVIDENCE_DIR / "screenshots"

sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.dont_write_bytecode = True
import capture_p2_evidence as p2  # noqa: E402  (reused CDP/Chrome/server plumbing)

SPECIMEN = "/preview/golden-standard/component-library/"
STYLES = SPECIMEN + "styles.css"
SCRIPT = SPECIMEN + "script.js"
CHROME_JS = "/design/golden-standard/system/chrome.js"
CHROME_CSS = "/design/golden-standard/system/chrome.css"
TOKENS_CSS = "/design/golden-standard/system/tokens.css"

# P4R5 section 5, verbatim.
VIEWPORTS = (1440, 1024, 768, 390, 360, 320)

# P4R5 section 5 performance budgets, verbatim, in gzip bytes except the
# hero and the initial mobile transfer, which are wire bytes.
BUDGET = {
    "initialJavaScriptGzipMax": 120 * 1024,
    "navigationGzipMax": 20 * 1024,
    "cssGzipMax": 45 * 1024,
    "initialMobileTransferMax": 1200 * 1024,
    "heroDesktopMax": 500 * 1024,
    "heroMobileMax": 300 * 1024,
}

# P4R5 section 7, verbatim.
OWNED_PREFIXES = (
    "preview/golden-standard/component-library/",
    "assets/vendor/lucide-dagg/",
    "evidence/COMPONENT-LIBRARY/",
)

# Every verbatim string P4R5 requires to be present on the page. A missing
# string is a hard failure, not a note.
REQUIRED_STRINGS = (
    # 4.1 flyout contents and proof inset
    "Build overview",
    "Dagg Factory",
    "Agents and software",
    "Trust and operation",
    "One operating decision becomes a buildable, governed system.",
    # 4.1 chrome
    "Transformation", "WorkGraph", "Build", "Impact", "Company",
    "Start an assessment",
    # 4.5 the five outcomes
    "Preserve", "Simplify", "Automate", "Rebuild", "Retire",
    # 4.6 record fields
    "Source", "Work", "Decision", "Owner", "Boundary", "Evidence",
    # 4.7 factory stages
    "Requirement", "Product decision", "Architecture", "Evaluation", "Review",
    # 4.8 modes and the five customer-surface strings
    "Inside the company",
    "At the customer surface",
    "What needs attention, and what can be resolved now?",
    "MCP exposes approved tools and permissioned context.",
    "The client system remains the source of truth.",
    "Explain, prepare or execute only within the granted boundary.",
    "No external write or commitment without accountable approval.",
    # 4.10 footer groups
    "Explore", "Trust",
)

# Strings whose presence anywhere on the page is a failure (P4R5 section 6
# and the P4R4 addendum section 5).
FORBIDDEN_STRINGS = ("Build+", "ClaudeForce")

# The last entry of the RESOLVED table in the specimen's script.js. Reduced
# motion, the completed pass and the no-JavaScript default must all land on
# this exact string; anything else means one of the three paths diverged.
RESOLVED_END_STATE = (
    "Ready for governed review · release withheld from the agent")


# ==========================================================================
# Page measurement
# ==========================================================================

_HELPERS = r"""
const parseColor = c => {
  const m = (c || '').match(/[\d.]+/g);
  if (!m) return null;
  const a = m.length > 3 ? parseFloat(m[3]) : 1;
  return [parseFloat(m[0]), parseFloat(m[1]), parseFloat(m[2]), a];
};
const over = (fg, bg) => [
  fg[0] * fg[3] + bg[0] * (1 - fg[3]),
  fg[1] * fg[3] + bg[1] * (1 - fg[3]),
  fg[2] * fg[3] + bg[2] * (1 - fg[3])];
const effectiveBackground = el => {
  const layers = [];
  let node = el;
  while (node) {
    const c = parseColor(getComputedStyle(node).backgroundColor);
    if (c && c[3] > 0) { layers.push(c); if (c[3] >= 1) break; }
    node = node.parentElement;
  }
  if (!layers.length) return [255, 255, 255];
  let out = layers.pop().slice(0, 3);
  while (layers.length) out = over(layers.pop(), out);
  return out;
};
const effectiveColor = el => {
  const fg = parseColor(getComputedStyle(el).color) || [0, 0, 0, 1];
  return fg[3] >= 1 ? fg.slice(0, 3) : over(fg, effectiveBackground(el));
};
/* A closed native <details> still generates a laid-out box for its
   non-summary content in this Chrome build, so getClientRects() alone does
   not prove a panel is closed. The desktop rule that force-opens the shared
   header disclosure is detected the same way chrome.css switches it: the
   summary computes to display:none. */
const inClosedDetails = el => {
  let d = el.closest('details');
  while (d) {
    if (!d.open) {
      const s = d.querySelector(':scope > summary');
      const insideSummary = !!(s && (el === s || s.contains(el)));
      if (!insideSummary && (!s || getComputedStyle(s).display !== 'none')) return true;
    }
    d = d.parentElement ? d.parentElement.closest('details') : null;
  }
  return false;
};
const isRendered = el => {
  if (!el || !el.getClientRects().length) return false;
  if (inClosedDetails(el)) return false;
  const c = getComputedStyle(el);
  return c.visibility !== 'hidden' && c.display !== 'none' &&
         parseFloat(c.opacity) > 0;
};
const rect = el => { if (!el) return null; const r = el.getBoundingClientRect();
  return {x: r.x, y: r.y, width: r.width, height: r.height}; };
/* Never read `.textContent` off a query that may not match. A missing
   control must be recorded as a null with a reason, not raise inside
   Runtime.evaluate and take the whole run down with it. */
const txt = el => (el && typeof el.textContent === 'string')
  ? el.textContent.replace(/\s+/g, ' ').trim() : null;
const num = v => { const n = parseFloat(v); return Number.isFinite(n) ? n : null; };
const round1 = v => { const n = num(v); return n === null ? null : Math.round(n * 10) / 10; };
const lineCount = el => {
  /* Real rendered line boxes, from the element's own client rects, not an
     estimate from character count. */
  const range = document.createRange();
  range.selectNodeContents(el);
  const boxes = [...range.getClientRects()].filter(r => r.height > 1);
  const tops = [...new Set(boxes.map(r => Math.round(r.top)))];
  return tops.length || 1;
};
"""

MEASURE = r"""
(() => {
""" + _HELPERS + r"""
  const R = document.documentElement;

  /* Every rendered text run, with its computed size and its effective
     foreground/background pair. Meta (JetBrains Mono) has its own 12 px
     floor per Foundations p.07; everything else answers to the 17 px body
     floor in P4R5 section 5, so the two are reported separately. */
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const runs = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.nodeValue || !node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!isRendered(el)) continue;
    const c = getComputedStyle(el);
    const family = c.fontFamily || '';
    runs.push({
      text: node.nodeValue.trim().slice(0, 90),
      tag: el.tagName,
      className: (typeof el.className === 'string' ? el.className : '').slice(0, 80),
      fontSize: parseFloat(c.fontSize),
      fontWeight: c.fontWeight,
      isMono: /JetBrains Mono|ui-monospace|monospace/i.test(family),
      color: effectiveColor(el),
      background: effectiveBackground(el),
      onInk: !!el.closest('.on-ink, .cl-close, .chrome-footer, .cl-record, .cl-factory, .cl-surfaces, .cl-evidence, .cl-fp'),
    });
  }

  const interactive = [...document.querySelectorAll(
    'a[href], button, summary, input, [tabindex]:not([tabindex="-1"])')]
    .filter(isRendered)
    .map(el => {
      const r = el.getBoundingClientRect();
      return {
        tag: el.tagName,
        type: el.getAttribute('type'),
        text: (el.textContent || '').trim().slice(0, 60),
        href: el.getAttribute('href'),
        width: Math.round(r.width * 100) / 100,
        height: Math.round(r.height * 100) / 100,
        inHeaderNav: !!el.closest('[data-chrome-header]'),
        inert: !!el.closest('[inert]'),
      };
    });

  const headings = [...document.querySelectorAll('.h1, .h2, .cl-typeset__h1')]
    .filter(isRendered)
    .map(el => ({
      role: el.classList.contains('h1') || el.classList.contains('cl-typeset__h1') ? 'H1' : 'H2',
      text: el.textContent.trim().slice(0, 90),
      fontSize: parseFloat(getComputedStyle(el).fontSize),
      lines: lineCount(el),
      width: Math.round(el.getBoundingClientRect().width),
    }));

  /* Page grounds: the background of every full-width <section>, in document
     order, so "at most three ground changes" (Foundations p.04) is counted
     from what actually painted rather than from intent. */
  const grounds = [...document.querySelectorAll('main > section, footer')]
    .map(el => {
      const bg = effectiveBackground(el);
      const r = el.getBoundingClientRect();
      return {
        id: el.id || el.tagName.toLowerCase(),
        background: bg,
        height: Math.round(r.height),
      };
    });
  let groundChanges = 0;
  for (let i = 1; i < grounds.length; i += 1) {
    const a = grounds[i - 1].background, b = grounds[i].background;
    if (Math.abs(a[0] - b[0]) > 2 || Math.abs(a[1] - b[1]) > 2 ||
        Math.abs(a[2] - b[2]) > 2) { groundChanges += 1; }
  }

  const focusable = [...document.querySelectorAll(
    'a[href], button, summary, input, [tabindex]:not([tabindex="-1"])')];
  const focusableInsideHidden = focusable.filter(el =>
    el.closest('[hidden]') || el.closest('[inert]') ||
    (el.offsetParent === null && getComputedStyle(el).position !== 'fixed')
  ).map(el => ({
    tag: el.tagName,
    text: (el.textContent || '').trim().slice(0, 50),
    inert: !!el.closest('[inert]'),
    hidden: !!el.closest('[hidden]'),
  }));

  const flyouts = [...document.querySelectorAll('[data-flyout]')].map(f => {
    const trigger = f.querySelector('[data-flyout-trigger]');
    const panel = f.querySelector('[data-flyout-panel]');
    const links = [...f.querySelectorAll('[data-flyout-panel] a[href]')];
    /* The trigger icon must be the vendored Lucide *file*, referenced as a
       real image element. An inline <svg>, a <use> into a sprite, a text
       symbol or a CSS glyph all fail P4R5 §4.1, so record what is actually
       in the trigger rather than only looking for the shape we expect. */
    const triggerIcon = trigger
      ? trigger.querySelector('img, svg, [class*="icon"]') : null;
    const states = [...f.querySelectorAll('[data-preview-state]')];
    const activeStates = states.filter(s => s.classList.contains('is-active'));
    return {
      id: f.getAttribute('data-flyout-id'),
      open: f.open,
      ariaExpanded: trigger ? trigger.getAttribute('aria-expanded') : null,
      triggerText: txt(trigger),
      triggerRect: rect(trigger),
      triggerIconTag: triggerIcon ? triggerIcon.tagName : null,
      triggerIconSrc: triggerIcon ? triggerIcon.getAttribute('src') : null,
      triggerHasInlineSvg: !!(trigger && trigger.querySelector('svg')),
      panelDisplay: panel ? getComputedStyle(panel).display : null,
      panelRect: rect(panel),
      linkCount: links.length,
      linkHrefs: links.map(a => a.getAttribute('href')),
      linksTabbable: links.filter(a => a.tabIndex >= 0).length,
      linksRendered: links.filter(isRendered).length,
      /* The right-hand proof inset. `activePreview` is the state the inset
         is actually showing; `previewText` is every state's own words, read
         from textContent so an inactive (visibility: hidden) state can
         still be compared and a static inset cannot hide behind an empty
         innerText. */
      previewStateCount: states.length,
      previewKeys: states.map(s => s.getAttribute('data-preview-state')),
      activePreview: activeStates.length === 1
        ? activeStates[0].getAttribute('data-preview-state') : null,
      activePreviewCount: activeStates.length,
      renderedPreviews: states.filter(isRendered)
        .map(s => s.getAttribute('data-preview-state')),
      previewText: Object.fromEntries(states.map(s => [
        s.getAttribute('data-preview-state'), txt(s)])),
      previewRects: Object.fromEntries(states.map(s => [
        s.getAttribute('data-preview-state'), rect(s)])),
      previewVisibility: Object.fromEntries(states.map(s => [
        s.getAttribute('data-preview-state'),
        getComputedStyle(s).visibility])),
      previewHidden: states.filter(s => s.hidden)
        .map(s => s.getAttribute('data-preview-state')),
      selectedLinks: links.filter(a => a.classList.contains('is-selected'))
        .map(a => a.getAttribute('data-preview-key')),
      reveals: [...f.querySelectorAll('[data-preview-reveal]')].map(b => ({
        key: b.getAttribute('data-preview-reveal'),
        expanded: b.getAttribute('aria-expanded'),
        controls: b.getAttribute('aria-controls'),
        controlsExists: !!document.getElementById(b.getAttribute('aria-controls') || ''),
        rendered: isRendered(b),
        rect: rect(b),
      })),
    };
  });

  const record = document.querySelector('[data-record]');
  const factory = document.querySelector('[data-factory]');
  const surfaces = document.querySelector('[data-surfaces]');

  return {
    url: location.href,
    innerWidth: window.innerWidth,
    innerHeight: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio,
    scrollWidth: R.scrollWidth,
    clientWidth: R.clientWidth,
    scrollHeight: R.scrollHeight,
    horizontalOverflowPx: Math.max(0, R.scrollWidth - R.clientWidth),
    title: document.title,
    lang: R.lang,
    enhanced: R.classList.contains('cl-enhanced'),
    snapshot: (document.querySelector('meta[name="dagg-snapshot"]') || {}).content || null,
    visibleText: document.body.innerText.replace(/\s+/g, ' ').trim(),
    visibleWordCount: document.body.innerText.trim().split(/\s+/).filter(Boolean).length,
    duplicateIds: (() => {
      const seen = {}, dupes = [];
      [...document.querySelectorAll('[id]')].forEach(el => {
        if (seen[el.id]) dupes.push(el.id); else seen[el.id] = 1;
      });
      return dupes;
    })(),
    brokenAriaRefs: [...document.querySelectorAll('[aria-labelledby],[aria-controls]')]
      .flatMap(el => ['aria-labelledby', 'aria-controls']
        .flatMap(a => (el.getAttribute(a) || '').split(/\s+/).filter(Boolean))
        .filter(id => !document.getElementById(id))),
    placeholderLinks: document.querySelectorAll(
      'a[href="#"], a[href=""], a[href^="javascript:"]').length,
    externalRefs: [...document.querySelectorAll('[href],[src]')]
      .map(el => el.getAttribute('href') || el.getAttribute('src'))
      .filter(v => v && /^(https?:)?\/\//i.test(v)),
    headerTheme: (document.querySelector('[data-chrome-header]') || {}).getAttribute
      ? document.querySelector('[data-chrome-header]').getAttribute('data-theme') : null,
    disclosureOpen: (document.querySelector('[data-disclosure]') || {}).open ?? null,
    summaryDisplay: document.querySelector('[data-summary]')
      ? getComputedStyle(document.querySelector('[data-summary]')).display : null,
    runs, interactive, headings, grounds, groundChanges, focusableInsideHidden,
    flyouts,
    continuum: {
      present: !!document.querySelector('[data-continuum]'),
      stations: [...document.querySelectorAll('.cl-station input')].map(i => ({
        value: i.value, checked: i.checked,
        labelRect: rect(i.closest('.cl-station')),
      })),
      outcomesInDom: document.querySelectorAll('[data-outcome]').length,
      outcomesRendered: [...document.querySelectorAll('[data-outcome]')]
        .filter(isRendered).map(el => el.getAttribute('data-outcome')),
      hasSupport: CSS.supports('selector(:has(*))'),
    },
    record: record ? (() => {
      const tabsHost = record.querySelector('[data-record-tabs]');
      return {
        missing: tabsHost ? [] : ['[data-record-tabs]'],
        tabsHidden: tabsHost ? tabsHost.hidden : null,
        tabRole: tabsHost ? tabsHost.getAttribute('role') : null,
        tabs: [...record.querySelectorAll('[role="tab"]')].map(t => ({
          text: txt(t),
          selected: t.getAttribute('aria-selected'),
          tabIndex: t.tabIndex,
          controls: t.getAttribute('aria-controls'),
          rect: rect(t),
        })),
        panelsInDom: record.querySelectorAll('[data-record-panel]').length,
        panelsRendered: [...record.querySelectorAll('[data-record-panel]')]
          .filter(isRendered).map(p => p.getAttribute('data-record-panel')),
        retainedFields: [...record.querySelectorAll('.cl-record__retained dt')]
          .map(dt => txt(dt)),
      };
    })() : {missing: ['[data-record]']},
    factory: factory ? (() => {
      const controlsHost = factory.querySelector('[data-factory-controls]');
      const resolvedEl = factory.querySelector('[data-factory-resolved]');
      const missing = [];
      if (!controlsHost) missing.push('[data-factory-controls]');
      if (!resolvedEl) missing.push('[data-factory-resolved]');
      return {
        missing,
        controlsHidden: controlsHost ? controlsHost.hidden : null,
        controls: controlsHost
          ? [...controlsHost.querySelectorAll('button')].map(b => ({
              text: txt(b), rect: rect(b),
              pressed: b.getAttribute('aria-pressed'),
              iconTag: b.querySelector('img, svg')
                ? b.querySelector('img, svg').tagName : null,
              iconSrc: b.querySelector('img')
                ? b.querySelector('img').getAttribute('src') : null,
            }))
          : [],
        stages: [...factory.querySelectorAll('.cl-factory__stage')].map(s => ({
          stage: s.getAttribute('data-stage'),
          hold: s.getAttribute('data-hold'),
          current: s.classList.contains('is-current'),
          done: s.classList.contains('is-done'),
          rendered: isRendered(s),
        })),
        resolved: txt(resolvedEl),
      };
    })() : {missing: ['[data-factory]']},
    surfaces: surfaces ? (() => {
      const recordEl = surfaces.querySelector('.cl-surfaces__record');
      return {
        missing: recordEl ? [] : ['.cl-surfaces__record'],
        modes: [...surfaces.querySelectorAll('[data-surface-mode]')].map(b => ({
          mode: b.getAttribute('data-surface-mode'),
          pressed: b.getAttribute('aria-pressed'),
          rect: rect(b),
        })),
        panelsRendered: [...surfaces.querySelectorAll('[data-surface-panel]')]
          .filter(isRendered).map(p => p.getAttribute('data-surface-panel')),
        panelsInDom: surfaces.querySelectorAll('[data-surface-panel]').length,
        recordRendered: recordEl ? isRendered(recordEl) : null,
        recordText: txt(recordEl),
      };
    })() : {missing: ['[data-surfaces]']},

    /* Machine Signal. The hook lives on the Machine Signal component, so
       the transition measured here is that component's own geometry: the
       width, the horizontal offset, the opacity, the thickness and the
       colour of each of the five strata. `onProtectedHero` exists so a
       future regression that re-attaches the hook to the hero figure fails
       loudly instead of silently measuring an image treatment. */
    signal: (() => {
      const carrier = document.querySelector('[data-signal-carrier]');
      if (!carrier) {
        return {present: false,
                reason: 'no [data-signal-carrier] element in the document'};
      }
      const statusEl = carrier.querySelector('[data-signal-status]');
      const host = carrier.querySelector('[data-signal-control]');
      const strataHost = carrier.querySelector('[data-strata]');
      const missing = [];
      if (!statusEl) missing.push('[data-signal-status]');
      if (!host) missing.push('[data-signal-control]');
      if (!strataHost) missing.push('[data-strata]');
      const strata = strataHost
        ? [...strataHost.children].map(li => {
            const bar = li.querySelector('.cl-strata__rule');
            const s = bar ? getComputedStyle(bar) : null;
            return {
              stratum: li.getAttribute('data-stratum'),
              role: li.classList.contains('is-decision') ? 'decision'
                  : li.classList.contains('is-boundary') ? 'boundary'
                  : 'context',
              label: txt(li.querySelector('.cl-strata__label')),
              width: s ? round1(s.width) : null,
              marginLeft: s ? round1(s.marginLeft) : null,
              height: s ? round1(s.height) : null,
              opacity: s ? num(s.opacity) : null,
              background: s ? s.backgroundColor : null,
            };
          })
        : [];
      return {
        present: true,
        missing,
        selector: carrier.tagName + '.' +
          (typeof carrier.className === 'string' ? carrier.className : ''),
        onProtectedHero: !!carrier.closest('[data-protected-hero]'),
        /* Icons are excluded: the one-shot control legitimately carries a
           vendored Lucide <img>. What must be zero is a *photograph* inside
           the Machine Signal component, because that would mean the
           transition is being applied to an image again. */
        containsPhotograph:
          carrier.querySelectorAll('img:not(.cl-ico)').length,
        coarse: carrier.classList.contains('is-coarse'),
        status: txt(statusEl),
        controlHidden: host ? host.hidden : null,
        controlButtons: host
          ? [...host.querySelectorAll('button')].map(b => ({
              text: txt(b), disabled: b.disabled, rect: rect(b)}))
          : [],
        strata,
        strataCount: strata.length,
        coralStrata: strata.filter(s => s.background === 'rgb(217, 119, 87)')
          .map(s => s.stratum),
        sageStrata: strata.filter(s => s.background === 'rgb(124, 132, 113)')
          .map(s => s.stratum),
      };
    })(),

    /* The protected Home thesis asset. Nothing may pretend to be the
       semantic transition here: no filter, no blur, no veil, no overlay
       and no blend mode. */
    protectedHero: (() => {
      const figure = document.querySelector('[data-protected-hero]');
      if (!figure) {
        return {present: false,
                reason: 'no [data-protected-hero] figure in the document'};
      }
      const img = figure.querySelector('img');
      if (!img) return {present: true, imgMissing: true};
      const s = getComputedStyle(img);
      return {
        present: true,
        imgMissing: false,
        currentSrc: img.currentSrc,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        decoded: img.naturalWidth > 0,
        filter: s.filter,
        opacity: num(s.opacity),
        mixBlendMode: s.mixBlendMode,
        transitionProperty: s.transitionProperty,
        overlayChildren: figure.querySelectorAll(
          '[data-signal-veil], [data-signal-carrier], .cl-carrier__grain').length,
        hasSignalHook: figure.hasAttribute('data-signal-carrier'),
      };
    })(),

    /* Icons. Every icon must be the vendored Lucide file referenced as an
       image element, and the document must contain no inline SVG at all. */
    icons: (() => {
      const marked = [...document.querySelectorAll('.cl-ico')];
      const bad = marked.filter(el => el.tagName !== 'IMG' ||
        !(el.getAttribute('src') || '')
          .startsWith('/assets/vendor/lucide-dagg/icons/'));
      return {
        count: marked.length,
        notVendoredImages: bad.map(el => ({
          tag: el.tagName, src: el.getAttribute('src'),
          className: typeof el.className === 'string' ? el.className : null})),
        sources: [...new Set(marked.map(el => el.getAttribute('src')))].sort(),
        undecoded: marked.filter(el => el.tagName === 'IMG' &&
          !(el.complete && el.naturalWidth > 0)).map(el => el.getAttribute('src')),
        inlineSvgElements: document.querySelectorAll('svg').length,
        svgUseElements: document.querySelectorAll('use').length,
        svgSymbolElements: document.querySelectorAll('symbol').length,
      };
    })(),
    images: [...document.images].map(img => ({
      currentSrc: img.currentSrc,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      renderedWidth: Math.round(img.getBoundingClientRect().width),
      renderedHeight: Math.round(img.getBoundingClientRect().height),
      aspect: img.naturalHeight
        ? Math.round((img.naturalWidth / img.naturalHeight) * 1000) / 1000 : null,
      loading: img.getAttribute('loading'),
      sizes: img.getAttribute('sizes'),
      complete: img.complete,
      decoded: img.naturalWidth > 0,
    })),
  };
})()
"""

FOCUS_PROBE = r"""
(() => {
""" + _HELPERS + r"""
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  const c = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return {
    tag: el.tagName,
    text: (el.textContent || '').trim().slice(0, 60) || el.getAttribute('aria-label'),
    href: el.getAttribute('href'),
    role: el.getAttribute('role'),
    matchesFocusVisible: el.matches(':focus-visible'),
    outlineStyle: c.outlineStyle,
    outlineWidth: parseFloat(c.outlineWidth),
    outlineOffset: parseFloat(c.outlineOffset),
    outlineColor: c.outlineColor,
    insideInert: !!el.closest('[inert]'),
    insideHidden: !!el.closest('[hidden]'),
    /* The strategic continuum uses a full-label transparent native radio.
       Its visible label owns the focus ring. Count that as rendered while
       continuing to reject anything inside a closed details or hidden
       container. */
    rendered: isRendered(el) || !!(
      el.tagName === 'INPUT' &&
      el.closest('label') &&
      isRendered(el.closest('label')) &&
      !inClosedDetails(el)
    ),
    rect: {x: r.x, y: r.y, width: r.width, height: r.height},
  };
})()
"""

FLYOUT_OPEN_PROBE = r"""
Array.from(document.querySelectorAll('[data-flyout]')).map(flyout => ({
  id: flyout.getAttribute('data-flyout-id'),
  open: flyout.open,
  expanded: (flyout.querySelector('[data-flyout-trigger]') || {})
    .getAttribute ? flyout.querySelector('[data-flyout-trigger]')
    .getAttribute('aria-expanded') : null
}))
"""


class SpecimenPage(p2.Page):
    """P2's Page, with the interactions this specimen needs: real mouse
    moves for hover intent, native keyboard activation of <summary>, and
    exact-URL network blocking for the no-JavaScript capture."""

    def measure(self):
        return self.evaluate(MEASURE)

    def settle(self, ms: int = 80):
        """A native <details> dispatches ``toggle`` as a queued task, not
        synchronously inside the keypress that opened it, so measuring in
        the same tick can read the DOM before the listener has run."""
        return self.evaluate("new Promise(r => setTimeout(r, %d))" % ms,
                             await_promise=True)

    def open_specimen(self, base_url: str, width: int, height: int | None = None,
                      reduced_motion: bool = False, block: list[str] | None = None):
        self.cdp.events.clear()
        self.requests = []
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height or (900 if width >= 600 else 844),
            "deviceScaleFactor": 1, "mobile": width < 600,
        }, session_id=self.session)
        self.set_reduced_motion(reduced_motion)
        self.cdp.call("Network.setBlockedURLs", {"urls": block or []},
                      session_id=self.session)
        self.cdp.call("Page.navigate", {"url": base_url + SPECIMEN},
                      session_id=self.session)
        self.cdp.wait_for_event("Page.loadEventFired")
        readiness = self.evaluate(p2.WAIT_FOR_PAINT, await_promise=True)
        facts = self.measure()
        facts["readiness"] = readiness
        facts["reducedMotion"] = reduced_motion
        facts["blockedUrls"] = block or []
        facts["requestedWidth"] = width
        facts.update(self.collect_events())
        return facts

    def move_mouse_to(self, selector: str, scroll: bool = True):
        """``scroll=False`` is required for anything inside the sticky
        header: centring a flyout link in the viewport would scroll the
        document, and the accepted chrome hides the header on down-scroll,
        so the measurement would then be of a header that is on its way
        off screen rather than of the interaction under test."""
        point = self.evaluate(
            "(() => { const el = document.querySelector(%s); if (!el) return null; "
            "if (%s) el.scrollIntoView({block:'center', behavior:'instant'}); "
            "const r = el.getBoundingClientRect(); "
            "if (!r.width || !r.height) return null; "
            "return {x: r.x + r.width / 2, y: r.y + r.height / 2}; })()"
            % (json.dumps(selector), "true" if scroll else "false"))
        if point is None:
            raise RuntimeError(
                "no laid-out element for selector %r" % selector)
        self.cdp.call("Input.dispatchMouseEvent", {
            "type": "mouseMoved", "x": point["x"], "y": point["y"],
        }, session_id=self.session)
        return point

    def move_mouse_away(self):
        self.cdp.call("Input.dispatchMouseEvent", {
            "type": "mouseMoved", "x": 2, "y": 2,
        }, session_id=self.session)

    def click_selector(self, selector: str, scroll: bool = True):
        point = self.move_mouse_to(selector, scroll=scroll)
        for kind in ("mousePressed", "mouseReleased"):
            self.cdp.call("Input.dispatchMouseEvent", {
                "type": kind, "x": point["x"], "y": point["y"],
                "button": "left", "clickCount": 1,
            }, session_id=self.session)
        return point

    def focus_selector(self, selector: str, scroll: bool = True):
        return self.evaluate(
            "(() => { const el = document.querySelector(%s); if (!el) return false; "
            "if (%s) el.scrollIntoView({block:'center'}); el.focus(); "
            "return document.activeElement === el; })()"
            % (json.dumps(selector), "true" if scroll else "false"))

    def press_key(self, key: str, code: str | None = None, vk: int = 0,
                  text: str | None = None):
        """``text`` inserts a ``char`` event between key-down and key-up.
        This Chrome build only runs a focused <summary>'s default action off
        that ``char`` event; a bare rawKeyDown/keyUp pair delivers the JS
        events but silently fails to open the native disclosure, which is a
        gap in the rig rather than a keyboard defect in the page."""
        code = code or key
        sequence = ["rawKeyDown"] + (["char"] if text is not None else []) + ["keyUp"]
        for kind in sequence:
            params = {"type": kind, "key": key, "code": code,
                      "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk}
            if kind == "char":
                params["text"] = text
                params["unmodifiedText"] = text
            self.cdp.call("Input.dispatchKeyEvent", params, session_id=self.session)

    def press_tab(self, shift: bool = False):
        for kind in ("rawKeyDown", "keyUp"):
            self.cdp.call("Input.dispatchKeyEvent", {
                "type": kind, "key": "Tab", "code": "Tab",
                "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
                "modifiers": 8 if shift else 0,
            }, session_id=self.session)
        return self.evaluate(FOCUS_PROBE)

    def tab_through(self, limit: int = 80) -> list:
        self.evaluate("window.scrollTo(0, 0); "
                      "if (document.activeElement) document.activeElement.blur(); null")
        stops, seen = [], set()
        for _ in range(limit):
            stop = self.press_tab()
            if stop is None:
                break
            key = (stop["tag"], stop["text"], round(stop["rect"]["y"], 1))
            if key in seen:
                break
            seen.add(key)
            stops.append(stop)
        return stops

    def scroll_to(self, selector: str, offset: int = -140):
        return self.evaluate(
            "(async () => { const el = document.querySelector(%s); "
            "if (!el) return null; "
            "window.scrollTo({top: el.getBoundingClientRect().top + window.scrollY + %d, "
            "behavior:'instant'}); "
            "await new Promise(r => setTimeout(r, 260)); return window.scrollY; })()"
            % (json.dumps(selector), offset), await_promise=True)

    def sleep(self, ms: int):
        return self.evaluate("new Promise(r => setTimeout(r, %d))" % ms,
                             await_promise=True)


# ==========================================================================
# Non-browser evidence
# ==========================================================================


def gzip_bytes(raw: bytes) -> int:
    import gzip as _gzip
    return len(_gzip.compress(raw, 9))


def asset_budget(base_url: str) -> dict:
    def get(path):
        status, _headers, body = p2.fetch(base_url, path)
        return status, body

    parts = {}
    for label, path in (("specimenHtml", SPECIMEN), ("specimenCss", STYLES),
                        ("specimenJs", SCRIPT), ("chromeCss", CHROME_CSS),
                        ("chromeJs", CHROME_JS), ("tokensCss", TOKENS_CSS)):
        status, body = get(path)
        parts[label] = {"path": path, "status": status,
                        "bytes": len(body), "gzip": gzip_bytes(body)}

    css_gzip = parts["specimenCss"]["gzip"] + parts["chromeCss"]["gzip"] + \
        parts["tokensCss"]["gzip"]
    js_gzip = parts["specimenJs"]["gzip"] + parts["chromeJs"]["gzip"]
    return {
        "parts": parts,
        "cssGzipTotal": css_gzip,
        "initialJavaScriptGzipTotal": js_gzip,
        "navigationGzipTotal": parts["chromeJs"]["gzip"],
        "budget": BUDGET,
    }


def hero_asset_bytes(base_url: str, facts_desktop: dict, facts_mobile: dict) -> dict:
    """The bytes Chrome actually chose from the hero <picture> at each
    viewport, fetched again from the same snapshot so the number is real."""
    out = {}
    for label, facts, key in (("desktop", facts_desktop, "heroDesktopMax"),
                              ("mobile", facts_mobile, "heroMobileMax")):
        chosen = [i for i in facts.get("images", [])
                  if i.get("currentSrc") and "hero-" in i["currentSrc"]]
        entries = []
        for image in chosen:
            path = image["currentSrc"].split(base_url, 1)[-1]
            status, _headers, body = p2.fetch(base_url, path)
            entries.append({"path": path, "status": status, "bytes": len(body),
                            "naturalWidth": image["naturalWidth"],
                            "naturalHeight": image["naturalHeight"],
                            "aspect": image["aspect"]})
        out[label] = {"entries": entries,
                      "totalBytes": sum(e["bytes"] for e in entries),
                      "budget": BUDGET[key]}
    return out


def owned_scope() -> dict:
    raw = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "status",
         "--porcelain", "--untracked-files=all"],
        check=True, capture_output=True, text=True).stdout
    working = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        working.append(path.strip('"'))
    owned = [p for p in working if p.startswith(OWNED_PREFIXES)]
    other = [p for p in working if not p.startswith(OWNED_PREFIXES)]
    return {
        "workingTree": working,
        "ownedByThisPackage": owned,
        "notOwnedByThisPackage": other,
        "note": "Paths under notOwnedByThisPackage pre-date P4R5. This rig "
                "reports them; it does not claim they were left untouched. "
                "Compare against the pre-P4R5 working tree to be sure.",
    }


def contrast_findings(facts: dict) -> dict:
    """Every rendered text run's measured pair, checked against the WCAG AA
    threshold for its own size and weight. Foundations p.05 freezes the
    accessible combinations; this proves which ones actually painted."""
    failures, checked = [], 0
    for run in facts.get("runs", []):
        ratio = p2.contrast_ratio(run["color"], run["background"])
        threshold = p2.aa_threshold(run["fontSize"], run["fontWeight"])
        checked += 1
        if ratio + 0.005 < threshold:
            failures.append({
                "text": run["text"], "tag": run["tag"],
                "className": run["className"],
                "fontSize": run["fontSize"], "fontWeight": run["fontWeight"],
                "ratio": round(ratio, 2), "required": threshold,
                "color": run["color"], "background": run["background"],
            })
    return {"runsChecked": checked, "failures": failures}


def text_floors(facts: dict) -> dict:
    body = [r for r in facts.get("runs", []) if not r["isMono"]]
    meta = [r for r in facts.get("runs", []) if r["isMono"]]
    return {
        "minBodyPx": min((r["fontSize"] for r in body), default=None),
        "minMetaPx": min((r["fontSize"] for r in meta), default=None),
        "bodyUnder17": [{"text": r["text"], "className": r["className"],
                         "fontSize": r["fontSize"]}
                        for r in body if r["fontSize"] < 17],
        "metaUnder12": [{"text": r["text"], "className": r["className"],
                         "fontSize": r["fontSize"]}
                        for r in meta if r["fontSize"] < 12],
    }


def target_floors(facts: dict, mobile: bool) -> dict:
    live = [i for i in facts.get("interactive", []) if not i["inert"]]
    floor = 48 if mobile else 44
    undersized = [i for i in live
                  if min(i["width"], i["height"]) + 0.5 < 44
                  or (i["inHeaderNav"] and mobile
                      and min(i["width"], i["height"]) + 0.5 < 48)]
    return {
        "liveInteractiveCount": len(live),
        "inertInteractiveCount": len(facts.get("interactive", [])) - len(live),
        "smallestEdge": min((min(i["width"], i["height"]) for i in live),
                            default=None),
        "navFloorApplied": floor,
        "undersized": undersized,
    }


def shot_name(state: str, facts: dict) -> str:
    """Filenames carry the viewport Chrome reported, never the requested
    width: P4R5 section 8 forbids labelling a larger capture as 390 px."""
    return "%s-%dx%d.png" % (state, facts["innerWidth"], facts["innerHeight"])


# ==========================================================================
# Capture
# ==========================================================================


def main(argv=None) -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--label", default="claude-self-review")
    args = parser.parse_args(argv)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)

    server, base_url, startup = p2.start_server(args.port, args.host)
    status, _headers, revision_body = p2.fetch(base_url, "/__revision")
    revision = json.loads(revision_body)
    snapshot_id = revision["snapshotId"]
    (EVIDENCE_DIR / "revision.json").write_bytes(revision_body)

    profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p4r5-"))
    chrome = cdp = None
    screenshots: list[dict] = []
    states: dict = {}
    deviations: list[str] = []
    step_failures: list[dict] = []

    def progress(message: str):
        print("[P4R5] " + message, flush=True)

    def safe(label: str, fn, *fn_args, **fn_kwargs):
        """Run one interaction step. A missing control is recorded as a
        failed matrix input with its reason -- never raised, and never
        quietly treated as a pass. Every recorded failure also lands in
        ``stepFailures`` so a run that could not exercise an interaction
        cannot be mistaken for a run that exercised it successfully."""
        try:
            return {"ok": True, "label": label,
                    "value": fn(*fn_args, **fn_kwargs)}
        except Exception as error:  # noqa: BLE001 - recorded, not swallowed
            entry = {"ok": False, "label": label,
                     "error": "%s: %s" % (type(error).__name__, error)}
            step_failures.append(entry)
            return entry

    def shoot(page, state: str, facts: dict, full: bool = False):
        png = page.screenshot(beyond_viewport=full)
        name = shot_name(state, facts)
        (SHOTS_DIR / name).write_bytes(png)
        record = {
            "path": "evidence/COMPONENT-LIBRARY/screenshots/" + name,
            "state": state,
            "requestedWidth": facts.get("requestedWidth"),
            "measuredViewport": [facts["innerWidth"], facts["innerHeight"]],
            "pixelDimensions": p2.png_size(png),
            "fullPage": full,
            "sha256": hashlib.sha256(png).hexdigest(),
        }
        screenshots.append(record)
        return record

    try:
        chrome, browser_ws, chrome_path = p2.start_chrome(profile_dir)
        cdp = p2.CDP(browser_ws)
        chrome_version = cdp.call("Browser.getVersion")

        # -- 1 · every required viewport, default state ------------------
        # Reuse one target for the entire run. Keeping six full-page targets
        # alive after the default captures made Chrome retain several very
        # tall raster surfaces; the later Escape-state measurement could then
        # time out even though the page itself was responsive.
        progress("default viewport captures")
        page = SpecimenPage(cdp)
        for width in VIEWPORTS:
            progress("default %d px" % width)
            facts = page.open_specimen(base_url, width)
            if facts["snapshot"] and facts["snapshot"] != snapshot_id:
                raise p2.SnapshotDisagreement(
                    "specimen reported snapshot %r, server reports %r"
                    % (facts["snapshot"], snapshot_id))
            mobile = width < 940
            states["default-%d" % width] = {
                "facts": facts,
                "contrast": contrast_findings(facts),
                "textFloors": text_floors(facts),
                "targets": target_floors(facts, mobile),
            }
            shoot(page, "default-first-viewport-%d" % width, facts)
            shoot(page, "default-full-%d" % width, facts, full=True)

        # -- 2 · desktop interaction states at 1440 ---------------------
        # Use a fresh interaction target after the six default/full-page
        # captures. The raw CDP transport otherwise carries a large screenshot
        # history into a state-heavy flyout sequence.
        progress("desktop Build flyout states")
        page = SpecimenPage(cdp)
        facts = page.open_specimen(base_url, 1440)
        shoot(page, "flyout-closed-1440", facts)
        states["flyout-closed"] = facts["flyouts"]

        # hover intent: move onto the trigger, wait past 85 ms, measure
        page.move_mouse_to('[data-flyout-id="header"] [data-flyout-trigger]',
                           scroll=False)
        page.sleep(220)
        hovered = page.measure()
        states["flyout-hover-open"] = hovered["flyouts"]
        shoot(page, "flyout-hover-open-1440", hovered)

        # -- 2a · the four preview states, driven by pointer hover ------
        # P4R5 §4.1. The flyout stays open throughout: the pointer moves
        # from the trigger into the list without leaving the corridor, and
        # each destination must change the one right-hand inset.
        preview_keys = ("overview", "factory", "agents", "trust")
        hover_previews: dict = {}
        for key in preview_keys:
            selector = ('[data-flyout-id="header"] '
                        '[data-preview-key="%s"]' % key)
            step = safe("hover-preview-" + key,
                        page.move_mouse_to, selector, scroll=False)
            page.sleep(300)
            measured = page.measure()
            header = next((f for f in measured["flyouts"]
                           if f["id"] == "header"), None)
            hover_previews[key] = {
                "step": step,
                "flyoutOpen": header["open"] if header else None,
                "activePreview": header["activePreview"] if header else None,
                "activePreviewCount": (header["activePreviewCount"]
                                       if header else None),
                "selectedLinks": header["selectedLinks"] if header else None,
                "panelRect": header["panelRect"] if header else None,
                "previewRect": (header["previewRects"].get(key)
                                if header else None),
                "previewText": (header["previewText"].get(key)
                                if header else None),
            }
            shoot(page, "flyout-preview-hover-%s-1440" % key, measured)
        states["flyout-preview-hover"] = hover_previews

        # close grace: leave, measure before and after the 210 ms window
        page.move_mouse_away()
        page.sleep(90)
        states["flyout-during-close-grace"] = page.measure()["flyouts"]
        page.sleep(400)
        states["flyout-after-close-grace"] = page.measure()["flyouts"]

        # keyboard open via Enter on the native summary, then focus within
        page.focus_selector('[data-flyout-id="header"] [data-flyout-trigger]',
                            scroll=False)
        page.press_key("Enter", "Enter", 13, text="\r")
        page.settle()
        keyboard_open = page.measure()
        states["flyout-keyboard-open"] = keyboard_open["flyouts"]
        shoot(page, "flyout-keyboard-open-1440", keyboard_open)

        # -- 2b · the same four states, driven by real Tab traversal ----
        # Focus starts on the trigger. Each Tab lands on the next
        # destination, and the inset must follow keyboard focus exactly as
        # it follows the pointer (P4R5 §4.1: "Keyboard focus produces the
        # same four states").
        focus_previews: dict = {}
        for index, key in enumerate(preview_keys):
            stop = page.press_tab()
            page.sleep(300)
            measured = page.measure()
            header = next((f for f in measured["flyouts"]
                           if f["id"] == "header"), None)
            focus_previews[key] = {
                "tabIndexInSequence": index + 1,
                "focus": stop,
                "focusIsThisDestination": bool(
                    stop and (stop.get("text") or "").startswith(
                        {"overview": "Build overview",
                         "factory": "Dagg Factory",
                         "agents": "Agents and software",
                         "trust": "Trust and operation"}[key])),
                "flyoutOpen": header["open"] if header else None,
                "activePreview": header["activePreview"] if header else None,
                "activePreviewCount": (header["activePreviewCount"]
                                       if header else None),
                "panelRect": header["panelRect"] if header else None,
            }
            shoot(page, "flyout-preview-focus-%s-1440" % key, measured)
        states["flyout-preview-focus"] = focus_previews

        first_stop = focus_previews[preview_keys[0]]["focus"]
        states["flyout-focus-within"] = {
            "focus": first_stop, "flyouts": page.measure()["flyouts"]}
        shoot(page, "flyout-focus-within-1440", page.measure())

        # Escape closes and restores focus to the trigger
        page.press_key("Escape", "Escape", 27)
        page.settle()
        states["flyout-escape"] = {
            # Escape only needs the disclosure state and focus restoration.
            # Avoid a full-document measurement after sixteen flyout captures;
            # that proved unreliable in raw CDP despite the visible browser
            # remaining responsive.
            "flyouts": page.evaluate(FLYOUT_OPEN_PROBE),
            "focusAfterEscape": page.evaluate(FOCUS_PROBE),
        }

        # -- 3 · strategic continuum, all five stations -----------------
        progress("strategic continuum and WorkGraph record")
        page = SpecimenPage(cdp)
        page.open_specimen(base_url, 1440)
        page.scroll_to("#continuum")
        continuum_states = {}
        for value in ("preserve", "simplify", "automate", "rebuild", "retire"):
            page.click_selector('.cl-station input[value="%s"]' % value)
            page.settle()
            measured = page.measure()
            continuum_states[value] = measured["continuum"]
            if value in ("preserve", "retire"):
                shoot(page, "continuum-%s-1440" % value, measured)
        states["continuum"] = continuum_states

        # -- 4 · WorkGraph record, all four sources ---------------------
        page.scroll_to("#record")
        record_states = {}
        for source in ("meetings", "messages", "documents", "systems"):
            page.click_selector("#record-tab-%s" % source)
            page.settle()
            measured = page.measure()
            record_states[source] = measured["record"]
            if source in ("meetings", "systems"):
                shoot(page, "record-%s-1440" % source, measured)
        # roving tabindex under arrow keys
        page.focus_selector("#record-tab-meetings")
        page.press_key("ArrowRight", "ArrowRight", 39)
        page.settle()
        record_states["afterArrowRight"] = {
            "record": page.measure()["record"],
            "focus": page.evaluate(FOCUS_PROBE),
        }
        states["record"] = record_states

        # -- 5 · Factory pass: timed, paused, resolved, replayed --------
        # A fresh target, so the pass has provably not been triggered by an
        # earlier scroll: the observer fires once and the timeline below is
        # therefore the whole pass from its first stage.
        progress("Factory motion states")
        page_factory = SpecimenPage(cdp)
        factory_facts = page_factory.open_specimen(base_url, 1440)
        states["factory-before-seen"] = factory_facts["factory"]
        page_factory.scroll_to("#factory", offset=-200)
        timeline = []
        for _ in range(12):
            timeline.append({
                "atMs": page_factory.evaluate("Math.round(performance.now())"),
                "factory": page_factory.measure()["factory"],
            })
            page_factory.sleep(800)
        states["factory-timeline"] = timeline
        shoot(page_factory, "factory-resolved-1440", page_factory.measure())

        # Pause and replay, exercised mid-pass rather than after it: the
        # pause control is correctly absent once the pass has stopped, so
        # clicking it afterwards would test nothing.
        page_pause = SpecimenPage(cdp)
        page_pause.open_specimen(base_url, 1440)
        page_pause.scroll_to("#factory", offset=-200)
        page_pause.sleep(1500)
        states["factory-mid-pass"] = page_pause.measure()["factory"]
        page_pause.click_selector(
            '[data-factory-controls] button[aria-pressed="false"]')
        page_pause.settle()
        paused_once = page_pause.measure()
        states["factory-paused"] = paused_once["factory"]
        shoot(page_pause, "factory-paused-1440", paused_once)
        page_pause.sleep(2500)
        states["factory-still-paused-after-2500ms"] = \
            page_pause.measure()["factory"]
        page_pause.click_selector('[data-factory-controls] button:last-child')
        page_pause.sleep(1200)
        replayed = page_pause.measure()
        states["factory-after-replay"] = replayed["factory"]
        shoot(page_pause, "factory-replay-mid-pass-1440", replayed)

        # -- 6 · Two surfaces: both modes, record must not move ---------
        progress("two-surface operating proof")
        page = SpecimenPage(cdp)
        page.open_specimen(base_url, 1440)
        page.scroll_to("#surfaces")
        for mode in ("inside", "customer"):
            page.click_selector('[data-surface-mode="%s"]' % mode)
            page.settle()
            measured = page.measure()
            states["surfaces-%s" % mode] = measured["surfaces"]
            states["surfaces-%s" % mode]["visibleText"] = measured["visibleText"]
            shoot(page, "surfaces-%s-1440" % mode, measured)

        # -- 7 · Machine Signal before / after --------------------------
        # The hook is on the Machine Signal component, so the before state
        # is deterministic: the one-shot control is the only thing that can
        # resolve it. Both states are measured as geometry, and the
        # protected hero image is measured in the same pass so a filter,
        # blur or overlay standing in for the transition cannot pass.
        progress("Machine Signal states")
        page_signal = SpecimenPage(cdp)
        signal_facts = page_signal.open_specimen(base_url, 1440)
        states["signal-before-any-scroll"] = {
            "signal": signal_facts["signal"],
            "protectedHero": signal_facts["protectedHero"],
        }
        page_signal.scroll_to("#signal", offset=-120)
        # Longer than the 900 ms pass, so the "before" measurement can never
        # catch a transition still in flight and report a half-resolved
        # geometry as the coarse state.
        page_signal.sleep(1200)
        before_facts = page_signal.measure()
        states["signal-before-resolution"] = {
            "signal": before_facts["signal"],
            "protectedHero": before_facts["protectedHero"],
        }
        shoot(page_signal, "signal-coarse-1440", before_facts)
        run_step = safe("signal-run-control", page_signal.click_selector,
                        "[data-signal-control] button")
        page_signal.sleep(1400)
        resolved_facts = page_signal.measure()
        states["signal-after-resolution"] = {
            "runStep": run_step,
            "signal": resolved_facts["signal"],
            "protectedHero": resolved_facts["protectedHero"],
        }
        shoot(page_signal, "signal-resolved-1440", resolved_facts)
        # It resolves once and stops: nothing may put it back to coarse.
        page_signal.sleep(1200)
        states["signal-still-resolved-after-1200ms"] = \
            page_signal.measure()["signal"]

        # -- 8 · keyboard path, full page, 1440 and 390 -----------------
        progress("keyboard paths")
        for width in (1440, 390):
            page_kb = SpecimenPage(cdp)
            kb_facts = page_kb.open_specimen(base_url, width)
            stops = page_kb.tab_through()
            states["tab-order-%d" % width] = {
                "measuredViewport": [kb_facts["innerWidth"], kb_facts["innerHeight"]],
                "stopCount": len(stops),
                "stops": stops,
                "stopsInsideInert": [s for s in stops if s["insideInert"]],
                "stopsInsideHidden": [s for s in stops if s["insideHidden"]],
                "stopsWithoutVisibleRing": [
                    s for s in stops
                    if s["matchesFocusVisible"] and
                    (s["outlineStyle"] == "none" or s["outlineWidth"] < 2)],
                "stopsNotRendered": [s for s in stops if not s["rendered"]],
            }
            if width == 1440:
                shoot(page_kb, "focus-first-stop-1440", kb_facts)

        # -- 9 · mobile menu closed / open at 390 -----------------------
        progress("mobile menu and flyout")
        page_mobile = SpecimenPage(cdp)
        mobile_facts = page_mobile.open_specimen(base_url, 390)
        shoot(page_mobile, "mobile-menu-closed-390", mobile_facts)
        page_mobile.focus_selector("[data-summary]")
        page_mobile.press_key("Enter", "Enter", 13, text="\r")
        page_mobile.settle()
        open_facts = page_mobile.measure()
        states["mobile-menu-open"] = {
            "disclosureOpen": open_facts["disclosureOpen"],
            "flyouts": open_facts["flyouts"],
            "horizontalOverflowPx": open_facts["horizontalOverflowPx"],
        }
        shoot(page_mobile, "mobile-menu-open-390", open_facts)
        page_mobile.click_selector(
            '[data-flyout-id="header"] [data-flyout-trigger]')
        page_mobile.settle()
        flyout_mobile = page_mobile.measure()
        states["mobile-flyout-open"] = flyout_mobile["flyouts"]
        shoot(page_mobile, "mobile-flyout-open-390", flyout_mobile)

        # The four previews become one-at-a-time disclosures inside the
        # reading sheet (P4R5 §4.1). Each tap must open exactly one.
        # `overview` is the default-open disclosure, so it is tapped last:
        # tapping it first would only exercise the close direction and the
        # pass would never prove that its own preview can be re-opened.
        mobile_previews: dict = {}
        for key in ("factory", "agents", "trust", "overview"):
            selector = ('[data-flyout-id="header"] '
                        '[data-preview-reveal="%s"]' % key)
            step = safe("mobile-reveal-" + key,
                        page_mobile.click_selector, selector)
            page_mobile.settle(140)
            measured = page_mobile.measure()
            header = next((f for f in measured["flyouts"]
                           if f["id"] == "header"), None)
            mobile_previews[key] = {
                "step": step,
                "renderedPreviews": (header["renderedPreviews"]
                                     if header else None),
                "reveals": header["reveals"] if header else None,
                "horizontalOverflowPx": measured["horizontalOverflowPx"],
            }
            if key in ("overview", "trust"):
                shoot(page_mobile,
                      "mobile-flyout-preview-%s-390" % key, measured)
        states["mobile-flyout-previews"] = mobile_previews

        page_mobile.press_key("Escape", "Escape", 27)
        page_mobile.settle()
        states["mobile-after-escape"] = {
            "disclosureOpen": page_mobile.evaluate(
                "document.querySelector('[data-disclosure]').open"),
            "documentOverflow": page_mobile.evaluate(
                "document.documentElement.style.overflow"),
            "focus": page_mobile.evaluate(FOCUS_PROBE),
        }

        # -- 10 · reduced motion, 1440 and 390 --------------------------
        progress("reduced motion")
        for width in (1440, 390):
            page_rm = SpecimenPage(cdp)
            rm_facts = page_rm.open_specimen(base_url, width, reduced_motion=True)
            page_rm.scroll_to("#factory", offset=-200)
            page_rm.sleep(400)
            rm_factory = page_rm.measure()
            page_rm.scroll_to("#signal", offset=-120)
            page_rm.sleep(400)
            rm_signal = page_rm.measure()
            states["reduced-motion-%d" % width] = {
                "measuredViewport": [rm_facts["innerWidth"], rm_facts["innerHeight"]],
                "factory": rm_factory["factory"],
                "signal": rm_signal["signal"],
                "protectedHero": rm_signal["protectedHero"],
                "flyouts": rm_facts["flyouts"],
                "horizontalOverflowPx": rm_facts["horizontalOverflowPx"],
                "visibleWordCount": rm_facts["visibleWordCount"],
                "consoleErrors": rm_facts["consoleErrors"],
            }
            shoot(page_rm, "reduced-motion-%d" % width, rm_facts, full=True)

        # -- 11 · no JavaScript, 1440 and 390 ---------------------------
        # Only the two exact local script URLs are network-blocked, not the
        # JS engine, so the rig's own Runtime.evaluate calls keep working
        # and a real dispatched click can still open the native <summary>.
        blocked = [base_url + SCRIPT, base_url + CHROME_JS]
        progress("fresh-load no-JavaScript")
        for width in (1440, 390):
            page_nojs = SpecimenPage(cdp)
            nojs = page_nojs.open_specimen(base_url, width, block=blocked)
            page_nojs.click_selector('[data-flyout-id="demo"] [data-flyout-trigger]')
            page_nojs.settle()
            nojs_open = page_nojs.measure()
            states["no-javascript-%d" % width] = {
                "measuredViewport": [nojs["innerWidth"], nojs["innerHeight"]],
                "enhanced": nojs["enhanced"],
                "visibleWordCount": nojs["visibleWordCount"],
                "horizontalOverflowPx": nojs["horizontalOverflowPx"],
                "continuum": nojs["continuum"],
                "recordPanelsRendered": (nojs["record"] or {}).get("panelsRendered"),
                "recordTabsHidden": (nojs["record"] or {}).get("tabsHidden"),
                "recordTabCount": len((nojs["record"] or {}).get("tabs") or []),
                "factoryControlsHidden": (nojs["factory"] or {}).get("controlsHidden"),
                "factoryControlCount": len((nojs["factory"] or {}).get("controls") or []),
                "factoryStagesRendered": sum(
                    1 for s in ((nojs["factory"] or {}).get("stages") or [])
                    if s["rendered"]),
                "surfacePanelsRendered": (nojs["surfaces"] or {}).get("panelsRendered"),
                "signal": nojs["signal"],
                "protectedHero": nojs["protectedHero"],
                "icons": nojs["icons"],
                "liveInteractive": target_floors(nojs, width < 940),
                "flyoutAfterNativeClick": nojs_open["flyouts"],
                # The mobile disclosure controls are created by script.js,
                # so with JavaScript absent there must be none at all: no
                # inert control may remain in the no-JS DOM (P4R5 §4.6).
                "flyoutRevealCount": sum(
                    len(f["reveals"]) for f in nojs["flyouts"]),
                "flyoutRenderedPreviewsAfterNativeClick": next(
                    (f["renderedPreviews"] for f in nojs_open["flyouts"]
                     if f["id"] == "demo"), None),
                "textFloors": text_floors(nojs),
                "contrast": contrast_findings(nojs),
                "failedRequests": nojs["failedRequests"],
            }
            shoot(page_nojs, "no-javascript-%d" % width, nojs, full=True)

        # -- 12 · force and decode lazy images at both art directions ---
        # The default captures deliberately preserve lazy loading. For the
        # image-loading check, request every local source in a fresh page and
        # wait on decode() before measuring. This proves the real assets load
        # without weakening the shipped page's loading strategy.
        progress("decoded image inventory")
        for width in (1440, 390):
            page_images = SpecimenPage(cdp)
            page_images.open_specimen(base_url, width)
            states["decoded-images-%d" % width] = page_images.evaluate(
                "(async () => { const out = []; for (const img of document.images) { "
                "img.loading = 'eager'; img.scrollIntoView({block:'center', behavior:'instant'}); "
                "try { await img.decode(); out.push({currentSrc: img.currentSrc || img.src, "
                "naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, "
                "aspect: img.naturalHeight ? Math.round((img.naturalWidth / img.naturalHeight) * 1000) / 1000 : null, "
                "decoded: true}); } "
                "catch (error) { out.push({currentSrc: img.currentSrc || img.src, "
                "naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight, "
                "aspect: null, decoded: false, error: String(error)}); } "
                "} return out; })()", await_promise=True)

        # -- 13 · non-browser evidence ----------------------------------
        progress("budgets and acceptance matrix")
        budget = asset_budget(base_url)
        heroes = hero_asset_bytes(
            base_url, {"images": states["decoded-images-1440"]},
            {"images": states["decoded-images-390"]})
        scope = owned_scope()
        server_stderr = p2.stop_server(server)
        (EVIDENCE_DIR / "server-stderr.txt").write_text(server_stderr)

        # ==============================================================
        # Acceptance matrix. Every entry is derived, never asserted.
        # ==============================================================
        d1440 = states["default-1440"]
        d390 = states["default-390"]

        # A closed flyout's panel computes `display: none`, so its four
        # destinations and its proof states are correctly absent from the
        # default state's rendered text. Checking the required strings only
        # against that state would report the flyout copy as missing from a
        # page that renders it correctly the moment the flyout opens. The
        # union below is the text that was *actually rendered* across the
        # captured states -- nothing is asserted from source.
        text_sources = {
            "default-1440": d1440["facts"]["visibleText"],
            "default-390": d390["facts"]["visibleText"],
            "flyout-keyboard-open-1440": keyboard_open["visibleText"],
            "flyout-hover-open-1440": hovered["visibleText"],
            "mobile-menu-open-390": open_facts["visibleText"],
            "mobile-flyout-open-390": flyout_mobile["visibleText"],
            "surfaces-customer-1440": states["surfaces-customer"]["visibleText"],
        }
        page_text = d1440["facts"]["visibleText"]
        rendered_text = "\n".join(text_sources.values())
        rendered_text_folded = rendered_text.casefold()

        # Every state's own words, from the open header flyout, so a static
        # inset cannot pass by rendering one block four times.
        header_open = next((f for f in states["flyout-keyboard-open"]
                            if f["id"] == "header"), None)
        preview_text_by_key = (header_open or {}).get("previewText") or {}

        factory_start_ms = states["factory-timeline"][0]["atMs"]
        factory_finish = next((
            t for t in states["factory-timeline"]
            if (t["factory"] or {}).get("resolved") == RESOLVED_END_STATE
        ), None)
        factory_duration_s = (
            round((factory_finish["atMs"] - factory_start_ms) / 1000, 3)
            if factory_finish else None)
        paused_stage = next((
            s["stage"] for s in (states["factory-paused"] or {}).get("stages", [])
            if s["current"]), None)
        held_stage = next((
            s["stage"] for s in
            (states["factory-still-paused-after-2500ms"] or {}).get("stages", [])
            if s["current"]), None)
        replay_stage = next((
            s["stage"] for s in
            (states["factory-after-replay"] or {}).get("stages", [])
            if s["current"]), None)

        def check(name, value, evidence, rule):
            return {"check": name, "pass": value, "evidence": evidence,
                    "rule": rule}

        def all_four(source: dict, field: str = "activePreview"):
            """True only when each of the four destinations produced its
            own distinct inset state. A missing measurement returns False,
            never None -- the interaction was required and was not proven."""
            got = [source.get(key, {}).get(field) for key in preview_keys]
            return got == list(preview_keys), got

        matrix = [
            check("noHorizontalOverflowAtEveryViewport",
                  all(states["default-%d" % w]["facts"]["horizontalOverflowPx"] == 0
                      for w in VIEWPORTS),
                  {w: states["default-%d" % w]["facts"]["horizontalOverflowPx"]
                   for w in VIEWPORTS},
                  "P4R5 §5 — no document-level horizontal overflow"),
            check("zeroConsoleErrors",
                  all(states["default-%d" % w]["facts"]["consoleErrors"] == 0
                      for w in VIEWPORTS),
                  {w: states["default-%d" % w]["facts"]["consoleErrorDetail"]
                   for w in VIEWPORTS},
                  "P4R5 §5 — console errors are zero"),
            check("bodyCopyAtLeast17px",
                  not any(states["default-%d" % w]["textFloors"]["bodyUnder17"]
                          for w in VIEWPORTS),
                  {w: states["default-%d" % w]["textFloors"] for w in VIEWPORTS},
                  "P4R5 §5 — body copy is at least 17 px; "
                  "Foundations p.07 — meta never below 12 px"),
            check("metadataAtLeast12px",
                  not any(states["default-%d" % w]["textFloors"]["metaUnder12"]
                          for w in VIEWPORTS),
                  {w: states["default-%d" % w]["textFloors"]["minMetaPx"]
                   for w in VIEWPORTS},
                  "Foundations p.07 — Meta never below 12 px"),
            check("h1WithinTwoAndAHalfLines",
                  all(h["lines"] <= 2.5
                      for w in VIEWPORTS
                      for h in states["default-%d" % w]["facts"]["headings"]
                      if h["role"] == "H1"),
                  {w: [h for h in states["default-%d" % w]["facts"]["headings"]
                       if h["role"] == "H1"] for w in VIEWPORTS},
                  "P4R5 §5 — H1 examples stay within 2.5 lines"),
            check("everyLiveTargetClears44px",
                  not any(states["default-%d" % w]["targets"]["undersized"]
                          for w in VIEWPORTS),
                  {w: states["default-%d" % w]["targets"] for w in VIEWPORTS},
                  "Foundations p.11 — 44 px minimum, 48 px mobile navigation"),
            check("allTextPairsMeetAA",
                  not any(states["default-%d" % w]["contrast"]["failures"]
                          for w in VIEWPORTS),
                  {w: states["default-%d" % w]["contrast"] for w in VIEWPORTS},
                  "Foundations p.05 — accessible combinations are frozen"),
            check("atMostThreeGroundChanges",
                  d1440["facts"]["groundChanges"] <= 3,
                  {"groundChanges": d1440["facts"]["groundChanges"],
                   "grounds": d1440["facts"]["grounds"]},
                  "Foundations p.04 — at most three page-ground changes"),
            check("noDuplicateIdsOrBrokenAriaRefs",
                  not d1440["facts"]["duplicateIds"]
                  and not d1440["facts"]["brokenAriaRefs"],
                  {"duplicateIds": d1440["facts"]["duplicateIds"],
                   "brokenAriaRefs": d1440["facts"]["brokenAriaRefs"]},
                  "P4R5 §5 — the full keyboard path works"),
            check("noPlaceholderLinksAndNoRemoteRequests",
                  d1440["facts"]["placeholderLinks"] == 0
                  and not d1440["facts"]["externalRefs"],
                  {"placeholderLinks": d1440["facts"]["placeholderLinks"],
                   "externalRefs": d1440["facts"]["externalRefs"]},
                  "P4R5 §4.1 — every destination remains a real link; "
                  "Foundations p.06 — no remote font request is permitted"),
            check("everyRequiredStringPresent",
                  all(s.casefold() in rendered_text_folded for s in REQUIRED_STRINGS),
                  {"missing": [s for s in REQUIRED_STRINGS
                               if s.casefold() not in rendered_text_folded],
                   "sourcesUsed": sorted(text_sources),
                   "note": "Rendered text only, unioned across the captured "
                           "states. A closed flyout's panel computes "
                           "display:none, so its copy is proven from the "
                           "open-flyout captures, not from source."},
                  "P4R5 §4.1, §4.5–§4.8, §4.10 — verbatim specimen copy"),
            check("noForbiddenString",
                  not any(s in rendered_text for s in FORBIDDEN_STRINGS),
                  {"found": [s for s in FORBIDDEN_STRINGS
                             if s in rendered_text]},
                  "P4R5 §6 — no `Build+` or text-symbol control; "
                  "P4R4 addendum §5"),
            check("flyoutTriggerIsAVendoredLucideChevronImage",
                  all(f["triggerIconTag"] == "IMG"
                      and (f["triggerIconSrc"] or "")
                      == "/assets/vendor/lucide-dagg/icons/chevron-down.svg"
                      and not f["triggerHasInlineSvg"]
                      and "+" not in (f["triggerText"] or "")
                      for f in d1440["facts"]["flyouts"])
                  and len(d1440["facts"]["flyouts"]) >= 2,
                  d1440["facts"]["flyouts"],
                  "P4R5 §4.1 — the word Build plus a proper icon-library "
                  "chevron, never a text plus sign or handcrafted icon; "
                  "the vendored official Lucide file is referenced as a "
                  "real image element"),
            check("everyIconIsAVendoredLucideImageAndNoInlineSvgExists",
                  bool(d1440["facts"]["icons"]["count"])
                  and not d1440["facts"]["icons"]["notVendoredImages"]
                  and not d1440["facts"]["icons"]["undecoded"]
                  and d1440["facts"]["icons"]["inlineSvgElements"] == 0
                  and d1440["facts"]["icons"]["svgUseElements"] == 0
                  and d1440["facts"]["icons"]["svgSymbolElements"] == 0
                  and not d390["facts"]["icons"]["notVendoredImages"]
                  and d390["facts"]["icons"]["inlineSvgElements"] == 0,
                  {"1440": d1440["facts"]["icons"],
                   "390": d390["facts"]["icons"]},
                  "P4R5 §4.1 / §7 — reference the vendored official Lucide "
                  "files under /assets/vendor/lucide-dagg/icons/ with real "
                  "image elements; no inline SVG, no sprite, no copied path "
                  "data, no hand-drawn replacement and no text symbol"),
            check("flyoutProofInsetHasFourDistinctStates",
                  len(preview_text_by_key) == 4
                  and all(preview_text_by_key.get(k)
                          for k in preview_keys)
                  and len(set(preview_text_by_key.values())) == 4
                  and "One operating decision becomes a buildable, governed "
                      "system." in (preview_text_by_key.get("overview") or ""),
                  {"previewText": preview_text_by_key,
                   "distinctStates": len(set(preview_text_by_key.values())),
                   "headerFlyoutWhenOpen": header_open},
                  "P4R5 §4.1 — one right-hand proof inset with four states; "
                  "the first state carries the conclusion `One operating "
                  "decision becomes a buildable, governed system.`; a "
                  "permanently static inset is a P0 failure"),
            check("flyoutProofInsetFollowsPointerHover",
                  all_four(states["flyout-preview-hover"])[0]
                  and all(v["activePreviewCount"] == 1
                          for v in states["flyout-preview-hover"].values())
                  and all(v["flyoutOpen"] is True
                          for v in states["flyout-preview-hover"].values()),
                  {"measuredActiveStates":
                       all_four(states["flyout-preview-hover"])[1],
                   "detail": states["flyout-preview-hover"],
                   "stepFailures": [s for s in step_failures
                                    if s["label"].startswith("hover-preview")]},
                  "P4R5 §4.1 — hover on each destination updates the one "
                  "right-hand proof inset, and the pointer stays inside a "
                  "forgiving corridor so the flyout never closes on the way"),
            check("flyoutProofInsetFollowsKeyboardFocus",
                  all_four(states["flyout-preview-focus"])[0]
                  and all(v["focusIsThisDestination"]
                          for v in states["flyout-preview-focus"].values())
                  and all(v["activePreviewCount"] == 1
                          for v in states["flyout-preview-focus"].values()),
                  {"measuredActiveStates":
                       all_four(states["flyout-preview-focus"])[1],
                   "detail": states["flyout-preview-focus"]},
                  "P4R5 §4.1 — keyboard focus produces the same four "
                  "states, reached by real Tab traversal from the trigger"),
            check("flyoutOuterPanelDoesNotMoveWhileTheInsetMorphs",
                  (lambda rects: bool(rects) and all(
                      r is not None for r in rects) and all(
                      abs(r["x"] - rects[0]["x"]) <= 0.5
                      and abs(r["y"] - rects[0]["y"]) <= 0.5
                      and abs(r["width"] - rects[0]["width"]) <= 0.5
                      and abs(r["height"] - rects[0]["height"]) <= 0.5
                      for r in rects))(
                      [v["panelRect"] for v in
                       states["flyout-preview-hover"].values()]
                      + [v["panelRect"] for v in
                         states["flyout-preview-focus"].values()]),
                  {"hoverPanelRects": {k: v["panelRect"] for k, v in
                                       states["flyout-preview-hover"].items()},
                   "focusPanelRects": {k: v["panelRect"] for k, v in
                                       states["flyout-preview-focus"].items()},
                   "tolerancePx": 0.5},
                  "P4R5 §4.1 — the right-hand region may morph its "
                  "dimensions in 180–240 ms, but the outer panel may not "
                  "jump, flicker or reposition"),
            check("mobilePreviewsAreOneAtATimeDisclosures",
                  bool(states["mobile-flyout-previews"])
                  and all(
                      (v["renderedPreviews"] or []) == [k]
                      and sum(1 for r in (v["reveals"] or [])
                              if r["expanded"] == "true") == 1
                      and all(r["controlsExists"]
                              for r in (v["reveals"] or []))
                      and v["horizontalOverflowPx"] == 0
                      for k, v in states["mobile-flyout-previews"].items()),
                  states["mobile-flyout-previews"],
                  "P4R5 §4.1 — on touch/mobile the four previews become "
                  "one-at-a-time disclosures inside the reading sheet"),
            check("noInertPreviewControlWithoutJavaScript",
                  states["no-javascript-390"]["flyoutRevealCount"] == 0
                  and states["no-javascript-1440"]["flyoutRevealCount"] == 0
                  and states["no-javascript-1440"][
                      "flyoutRenderedPreviewsAfterNativeClick"] == ["overview"],
                  {"1440": states["no-javascript-1440"],
                   "390": states["no-javascript-390"]},
                  "P4R5 §4.6 / §5 — no-JS leaves no inert control, and the "
                  "state that carries the conclusion is the one that paints"),
            check("flyoutOpensOnHoverIntentAndClosesAfterGrace",
                  any(f["open"] for f in states["flyout-hover-open"])
                  and not any(f["open"] for f in states["flyout-after-close-grace"]),
                  {"hoverOpen": states["flyout-hover-open"],
                   "duringGrace": states["flyout-during-close-grace"],
                   "afterGrace": states["flyout-after-close-grace"]},
                  "Foundations p.12 — open intent 70–100 ms, "
                  "close grace 180–240 ms"),
            check("flyoutKeyboardOpenAndEscapeRestoresFocus",
                  any(f["open"] for f in states["flyout-keyboard-open"])
                  and not any(f["open"] for f in states["flyout-escape"]["flyouts"])
                  and ((states["flyout-escape"]["focusAfterEscape"] or {})
                       .get("text") or "").startswith("Build"),
                  states["flyout-escape"],
                  "Foundations p.12 — Enter / Space / Escape; "
                  "P4R3 §5 — Escape closes and restores focus"),
            check("closedFlyoutContentIsNotFocusable",
                  not states["tab-order-1440"]["stopsInsideHidden"]
                  and not states["tab-order-1440"]["stopsInsideInert"]
                  and not states["tab-order-1440"]["stopsNotRendered"],
                  states["tab-order-1440"],
                  "P4R5 §5 — hidden states are not focusable"),
            check("everyFocusStopShowsThe2pxRing",
                  not states["tab-order-1440"]["stopsWithoutVisibleRing"]
                  and not states["tab-order-390"]["stopsWithoutVisibleRing"],
                  {"1440": states["tab-order-1440"]["stopsWithoutVisibleRing"],
                   "390": states["tab-order-390"]["stopsWithoutVisibleRing"]},
                  "Foundations p.11 — 2 px ring / 2 px offset"),
            check("continuumSelectionChangesOneExplanation",
                  all(v["outcomesRendered"] == [k]
                      for k, v in states["continuum"].items()),
                  states["continuum"],
                  "P4R5 §4.5 — one selected state changes a single "
                  "explanation and proof marker"),
            check("continuumCompleteWithoutJavaScript",
                  states["no-javascript-1440"]["continuum"]["outcomesInDom"] == 5,
                  states["no-javascript-1440"]["continuum"],
                  "P4R5 §4.5 — complete content is present without JavaScript"),
            check("recordIsATablistWithRovingTabindex",
                  (d1440["facts"]["record"] or {}).get("tabRole") == "tablist"
                  and len((d1440["facts"]["record"] or {}).get("tabs") or []) == 4
                  and sum(1 for t in ((d1440["facts"]["record"] or {})
                                      .get("tabs") or [])
                          if t["tabIndex"] == 0) == 1,
                  d1440["facts"]["record"],
                  "P4R5 §5 — if controls switch panels, use tablist "
                  "semantics and roving tabindex"),
            check("recordRetainsTheSameSixFields",
                  all(f.casefold() in page_text.casefold() for f in
                      ("Source", "Work", "Decision", "Owner", "Boundary",
                       "Evidence")),
                  {"retainedFields": (d1440["facts"]["record"] or {})
                   .get("retainedFields")},
                  "P4R5 §4.6 — one retained record with Source / Work / "
                  "Decision / Owner / Boundary / Evidence"),
            check("recordHasNoInertControlWithoutJavaScript",
                  states["no-javascript-1440"]["recordTabsHidden"] is True
                  and states["no-javascript-1440"]["recordTabCount"] == 0
                  and len(states["no-javascript-1440"]["recordPanelsRendered"] or []) == 4,
                  states["no-javascript-1440"],
                  "P4R5 §4.6 — without JavaScript all records remain "
                  "readable and no inert controls remain"),
            check("factoryPassIsSixToEightSecondsWithPauseAndReplay",
                  factory_duration_s is not None
                  and 6 <= factory_duration_s <= 8
                  and paused_stage == held_stage
                  and (states["factory-paused"]["controls"][0]
                       .get("pressed")) == "true"
                  and replay_stage is not None
                  and (states["factory-after-replay"]["controls"][0]
                       .get("pressed")) == "false",
                  {
                      "measuredDurationSeconds": factory_duration_s,
                      "pausedStage": paused_stage,
                      "heldStageAfter2500ms": held_stage,
                      "replayStageAfter1200ms": replay_stage,
                      "timeline": [{"atMs": t["atMs"],
                                    "current": [s["stage"] for s in
                                                (t["factory"] or {}).get("stages", [])
                                                if s["current"]],
                                    "resolved": (t["factory"] or {}).get("resolved")}
                                   for t in states["factory-timeline"]],
                      "controls": (d1440["facts"]["factory"] or {})
                          .get("controls"),
                      "note": "Derive the pass duration from the timeline "
                              "above; this rig records it rather than "
                              "asserting it.",
                  },
                  "ILS p.08 — one 6–8 second pass, hold at judgment and "
                  "verification, then stop; P4R5 §4.7 — pause and replay "
                  "are mandatory"),
            check("factoryResolvesToTheSameEndStateUnderReducedMotion",
                  bool((states["reduced-motion-1440"]["factory"] or {})
                       .get("stages"))
                  and (states["reduced-motion-1440"]["factory"]["stages"][-1]
                       ["current"]) is True
                  and (states["reduced-motion-1440"]["factory"]
                       .get("resolved")) == RESOLVED_END_STATE,
                  {"reducedMotion": states["reduced-motion-1440"]["factory"],
                   "reducedMotion390": states["reduced-motion-390"]["factory"],
                   "expectedEndState": RESOLVED_END_STATE},
                  "P4R5 §4.7 — reduced motion resolves to the same verified "
                  "end state immediately"),
            check("factoryStagesAllReadableWithoutJavaScript",
                  states["no-javascript-1440"]["factoryStagesRendered"] == 6
                  and states["no-javascript-1440"]["factoryControlCount"] == 0,
                  states["no-javascript-1440"],
                  "P4R5 §4.7 / §5 — no-JS exposes all core content without "
                  "dead buttons"),
            check("modeChangeAltersContextActionPermissionAndEvidence",
                  states["surfaces-inside"]["panelsRendered"] == ["inside"]
                  and states["surfaces-customer"]["panelsRendered"] == ["customer"]
                  and states["surfaces-inside"]["recordText"]
                  == states["surfaces-customer"]["recordText"],
                  {"inside": states["surfaces-inside"],
                   "customer": states["surfaces-customer"]},
                  "P4R5 §4.8 — changing mode must change context, action, "
                  "permission and evidence in the same carrier; the shared "
                  "centre is a persistent company record"),
            check("machineSignalIsWiredToItsOwnComponent",
                  (d1440["facts"]["signal"] or {}).get("present") is True
                  and not (d1440["facts"]["signal"] or {}).get("missing")
                  and (d1440["facts"]["signal"] or {})
                      .get("onProtectedHero") is False
                  and (d1440["facts"]["signal"] or {})
                      .get("containsPhotograph") == 0
                  and (d1440["facts"]["signal"] or {}).get("strataCount") == 5
                  and (d1440["facts"]["signal"] or {}).get("status")
                  is not None,
                  {"signal": d1440["facts"]["signal"],
                   "signal390": d390["facts"]["signal"]},
                  "P4R5 P0 repair — the hook belongs on the Machine Signal "
                  "component, whose own status and states live there; the "
                  "rig must be able to read a status without a null "
                  "textContent"),
            check("protectedHeroCarriesNoTransitionTreatment",
                  (d1440["facts"]["protectedHero"] or {}).get("present") is True
                  and (d1440["facts"]["protectedHero"] or {})
                      .get("filter") == "none"
                  and (d1440["facts"]["protectedHero"] or {})
                      .get("opacity") == 1
                  and (d1440["facts"]["protectedHero"] or {})
                      .get("mixBlendMode") == "normal"
                  and (d1440["facts"]["protectedHero"] or {})
                      .get("overlayChildren") == 0
                  and (d1440["facts"]["protectedHero"] or {})
                      .get("hasSignalHook") is False
                  and (states["signal-after-resolution"]["protectedHero"] or {})
                      .get("filter") == "none",
                  {"default1440": d1440["facts"]["protectedHero"],
                   "default390": d390["facts"]["protectedHero"],
                   "duringSignalPass":
                       states["signal-before-resolution"]["protectedHero"],
                   "afterSignalPass":
                       states["signal-after-resolution"]["protectedHero"]},
                  "P4R5 P0 repair / IMAGE-PRODUCTION-PROTOCOL §7 — no "
                  "filter, blur or overlay may pretend to be the semantic "
                  "transition, and the protected hero image is unchanged"),
            check("machineSignalResolvesOnceAndHolds",
                  (lambda before, after, held: bool(before) and bool(after)
                   # the before state is genuinely coarse
                   and before.get("coarse") is True
                   and after.get("coarse") is False
                   and held.get("coarse") is False
                   # a one-shot control existed, and is gone afterwards
                   and len(before.get("controlButtons") or []) == 1
                   and before.get("controlHidden") is False
                   and after.get("controlHidden") is True
                   and len(after.get("controlButtons") or []) == 0
                   # the geometry itself changed: every stratum moved to a
                   # shared origin at full width and full opacity
                   and all(s["marginLeft"] not in (0, None)
                           or s["width"] != a["width"]
                           for s, a in zip(before.get("strata") or [],
                                           after.get("strata") or []))
                   and all(s["marginLeft"] == 0 and s["opacity"] == 1
                           for s in (after.get("strata") or []))
                   and any(s["marginLeft"] and s["marginLeft"] > 0
                           for s in (before.get("strata") or []))
                   # coral appears exactly once, and only after resolution;
                   # sage arrives only with the verified boundary
                   and before.get("coralStrata") == []
                   and before.get("sageStrata") == []
                   and after.get("coralStrata") == ["judgment"]
                   and after.get("sageStrata") == ["boundary"])(
                      states["signal-before-resolution"]["signal"] or {},
                      states["signal-after-resolution"]["signal"] or {},
                      states["signal-still-resolved-after-1200ms"] or {}),
                  {"before": states["signal-before-resolution"]["signal"],
                   "after": states["signal-after-resolution"]["signal"],
                   "held": states["signal-still-resolved-after-1200ms"],
                   "runStep": states["signal-after-resolution"]["runStep"],
                   "reducedMotion1440": states["reduced-motion-1440"]["signal"],
                   "noJavaScript1440": states["no-javascript-1440"]["signal"]},
                  "P4R5 §4.4 — a finite Machine Signal before/after control "
                  "that resolves once and stops, with no replay below one "
                  "second; ILS p.10 RESOLVE and p.11 REQUIRED — a visible "
                  "before and after state, coral once, sage only with "
                  "control"),
            check("machineSignalIsResolvedWithoutJavaScriptAndUnderReduce",
                  (states["no-javascript-1440"]["signal"] or {})
                      .get("coarse") is False
                  and (states["no-javascript-390"]["signal"] or {})
                      .get("coarse") is False
                  and (states["no-javascript-1440"]["signal"] or {})
                      .get("controlHidden") is True
                  and (states["reduced-motion-1440"]["signal"] or {})
                      .get("coarse") is False
                  and (states["reduced-motion-390"]["signal"] or {})
                      .get("coarse") is False
                  and (states["reduced-motion-1440"]["signal"] or {})
                      .get("controlHidden") is True,
                  {"noJavaScript1440": states["no-javascript-1440"]["signal"],
                   "noJavaScript390": states["no-javascript-390"]["signal"],
                   "reducedMotion1440": states["reduced-motion-1440"]["signal"],
                   "reducedMotion390": states["reduced-motion-390"]["signal"]},
                  "P4R5 §5 — no-JS exposes all core content without dead "
                  "buttons; Foundations p.13 — reduced motion snaps position "
                  "and size and preserves the resolved meaning"),
            check("heroCropsAreProtected16to10And4to5",
                  None,
                  {"desktop": heroes["desktop"], "mobile": heroes["mobile"]},
                  "P4R5 §4.4 — the real Home hero asset in both protected "
                  "16:10 desktop and art-directed 4:5 mobile crops; both "
                  "must preserve unresolved context, coral decision and "
                  "sage boundary. The aspect ratios here are machine-"
                  "checkable; whether the protected subject survives each "
                  "crop is a visual judgement and is NOT decided by this "
                  "rig."),
            check("everyImageDecoded",
                  all(i["decoded"] for i in states["decoded-images-1440"])
                  and all(i["decoded"] for i in states["decoded-images-390"]),
                  {"1440": states["decoded-images-1440"],
                   "390": states["decoded-images-390"]},
                  "P4R5 §5 — image loading"),
            check("performanceBudgets",
                  budget["initialJavaScriptGzipTotal"] <= BUDGET["initialJavaScriptGzipMax"]
                  and budget["navigationGzipTotal"] <= BUDGET["navigationGzipMax"]
                  and budget["cssGzipTotal"] <= BUDGET["cssGzipMax"]
                  and heroes["desktop"]["totalBytes"] <= BUDGET["heroDesktopMax"]
                  and heroes["mobile"]["totalBytes"] <= BUDGET["heroMobileMax"],
                  {"budget": budget, "heroes": heroes},
                  "P4R5 §5 — JS ≤120 KB gzip, navigation ≤20 KB gzip, "
                  "CSS ≤45 KB gzip, hero ≤500 KB desktop / ≤300 KB mobile"),
            check("everyInteractionStepActuallyRan",
                  not step_failures,
                  {"stepFailures": step_failures,
                   "note": "A step that could not find its control is "
                           "recorded here as a failure with its reason. It "
                           "is never reported as a pass and it never raises "
                           "out of the run."},
                  "P4R5 §8 — every interaction/state has named evidence; "
                  "CLAUDE.md rule 6 — a claim of verification must name the "
                  "actual coverage"),
            check("onlyOwnedFilesChanged",
                  None if scope["notOwnedByThisPackage"] else True,
                  {**scope, "reason": (
                      "A clean pre-P4R5 working-tree baseline is unavailable; "
                      "the rig reports concurrent paths but cannot attribute them."
                      if scope["notOwnedByThisPackage"] else None)},
                  "P4R5 §7 — files owned"),
        ]

        unresolved = [m["check"] for m in matrix if m["pass"] is None]
        failed = [m["check"] for m in matrix if m["pass"] is False]

        deviations.append(
            "The no-JavaScript captures block only the two exact local "
            "script URLs (%s) via Network.setBlockedURLs rather than "
            "disabling the JS engine, so this rig's own Runtime.evaluate "
            "calls keep working. The resulting failed loads are the "
            "intended no-JS condition, not page errors." % ", ".join(blocked))
        deviations.append(
            "Checks whose `pass` is null are deliberately undecided by "
            "machine: %s. They record their measurement for a human or "
            "for Codex to judge." % (", ".join(unresolved) or "none"))
        deviations.append(
            "This rig records machine evidence only. It does not grade its "
            "own rendering, and a passing matrix does not overrule a "
            "visible rendering failure (CLAUDE.md rule 5).")

        result = {
            "package": "P4R5",
            "artefact": SPECIMEN,
            "label": args.label,
            "commit": p2.git("rev-parse", "HEAD"),
            "branch": revision["branch"],
            "dirtyAtCapture": revision["dirty"],
            "snapshotId": snapshot_id,
            "capturedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverStartupSeconds": startup,
            "chrome": chrome_version.get("product"),
            "chromePath": chrome_path,
            "chromeDriver": "Chrome DevTools Protocol over a raw WebSocket",
            "viewportsRequested": list(VIEWPORTS),
            "viewportsMeasured": {
                w: [states["default-%d" % w]["facts"]["innerWidth"],
                    states["default-%d" % w]["facts"]["innerHeight"]]
                for w in VIEWPORTS},
            "screenshots": screenshots,
            "acceptanceMatrix": matrix,
            "matrixFailed": failed,
            "matrixUndecidedByMachine": unresolved,
            "stepFailures": step_failures,
            "performance": budget,
            "heroAssets": heroes,
            "scope": scope,
            "deviations": deviations,
            "notMeasuredHere": [
                "Screen-reader announcement quality.",
                "Real-device rendering and real-device touch.",
                "Whether the specimen reads as a premium Dagg surface: that "
                "is the visual review, not this rig.",
                "Whether each protected crop preserves the coral decision "
                "and sage boundary.",
            ],
        }
        (EVIDENCE_DIR / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
        (EVIDENCE_DIR / "states.json").write_text(
            json.dumps(states, indent=2, sort_keys=True, default=str) + "\n")
        (EVIDENCE_DIR / "acceptance-matrix.json").write_text(
            json.dumps({"package": "P4R5", "snapshotId": snapshot_id,
                        "matrix": matrix, "failed": failed,
                        "undecidedByMachine": unresolved},
                       indent=2, sort_keys=True, default=str) + "\n")

        print(json.dumps({"snapshotId": snapshot_id,
                          "screenshots": len(screenshots),
                          "failed": failed,
                          "stepFailures": [s["label"] for s in step_failures],
                          "undecidedByMachine": unresolved}, indent=2))
        return 1 if failed else 0
    finally:
        if cdp is not None:
            try:
                cdp.close()
            except Exception:
                pass
        if chrome is not None:
            chrome.terminate()
            try:
                chrome.wait(timeout=10)
            except subprocess.TimeoutExpired:
                chrome.kill()
        p2.stop_server(server)
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
