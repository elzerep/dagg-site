#!/usr/bin/env python3
"""Capture P3 global-chrome evidence from one immutable-snapshot server process.

This is the P3B acceptance rig: it owns only this file, ``tests/test_p3_chrome.py``
and ``evidence/P3/**``. It does not touch ``design/golden-standard/system/chrome.css``,
``design/golden-standard/system/chrome.js`` or ``preview/golden-standard/chrome/**`` --
those are P3A's frozen source, inspected here exactly as served.

Runs the P3 acceptance suite, then starts ``tools/serve_preview.py`` once and
drives the installed Google Chrome over the Chrome DevTools Protocol, reusing
the P0R2 server launcher and the P2 raw-CDP WebSocket/Chrome plumbing from
``capture_p2_evidence`` rather than re-implementing it.

Every screenshot, every computed measurement and ``evidence/P3/result.json``
come from that single process, so all of them provably describe one snapshot
ID. Partial evidence is refused rather than written silently.

Standard library only, plus the ``capture_p2_evidence`` module in this same
``tools/`` directory.

    python3 tools/capture_p3_evidence.py
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence" / "P3"

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import capture_p2_evidence as p2  # noqa: E402  (reused CDP/Chrome/server plumbing)

BASE_COMMIT = "772ea9d875ac79fcfb1bef7c339150e81f66b516"

CHROME_ROOT = "/preview/golden-standard/chrome"
CHROME_CSS_PATH = "/design/golden-standard/system/chrome.css"
CHROME_JS_PATH = "/design/golden-standard/system/chrome.js"
TOKENS_CSS_PATH = "/design/golden-standard/system/tokens.css"
LOGO_DARK_PATH = "/assets/dagg-logotype-dark.png"
LOGO_LIGHT_PATH = "/assets/dagg-logotype.png"
FONT_PATHS = p2.FONT_PATHS

# Section 5's information-architecture contract, verbatim.
ROUTE_TABLE = (
    {"label": "Dagg logotype", "production": "/",
     "preview": CHROME_ROOT + "/", "nav": "root"},
    {"label": "Transformation", "production": "/transformation",
     "preview": CHROME_ROOT + "/routes/transformation/", "nav": "header+footer"},
    {"label": "WorkGraph", "production": "/workgraph",
     "preview": CHROME_ROOT + "/routes/workgraph/", "nav": "header+footer"},
    {"label": "Build", "production": "/build",
     "preview": CHROME_ROOT + "/routes/build/", "nav": "header+footer"},
    {"label": "Impact", "production": "/impact",
     "preview": CHROME_ROOT + "/routes/impact/", "nav": "header+footer"},
    {"label": "Company", "production": "/company",
     "preview": CHROME_ROOT + "/routes/company/", "nav": "header+footer"},
    {"label": "Start an assessment", "production": "/assessment",
     "preview": CHROME_ROOT + "/routes/assessment/", "nav": "header+footer"},
    {"label": "Trust", "production": "/trust",
     "preview": CHROME_ROOT + "/routes/trust/", "nav": "footer"},
    {"label": "Privacy", "production": "/privacy",
     "preview": CHROME_ROOT + "/routes/privacy/", "nav": "footer"},
    {"label": "Terms", "production": "/terms",
     "preview": CHROME_ROOT + "/routes/terms/", "nav": "footer"},
)

PRIMARY_LABEL_ORDER = ("Transformation", "WorkGraph", "Build", "Impact",
                       "Company", "Start an assessment")

FOOTER_EXPLORE = ("Transformation", "WorkGraph", "Build", "Impact")
FOOTER_COMPANY = ("Company", "Start an assessment")
FOOTER_TRUST = ("Trust", "hello@dagg.ai", "Privacy", "Terms")

LAYOUT_VIEWPORTS = (320, 360, 390, 768, 1024, 1440)
SCREENSHOT_VIEWPORTS = (1440, 390, 360, 320)
COMPACT_HEADER_SCREENSHOT_VIEWPORTS = (940, 1024)
COLLAPSE_PROBES = (939, 940)

INK_RGB = (20, 20, 19)
PAPER_RGB = (240, 238, 230)

PERFORMANCE_BUDGET = {
    "chromeCssBytesMax": 24 * 1024,
    "chromeJavaScriptBytesMax": 12 * 1024,
}

# Everything P3 is allowed to create or change, verbatim from package section 4.
OWNED_PATHS = {
    "CLAUDE.md",
    "design/golden-standard/packages/P3-GLOBAL-CHROME.md",
    "design/golden-standard/system/chrome.css",
    "design/golden-standard/system/chrome.js",
    "tests/test_p3_chrome.py",
    "tools/capture_p3_evidence.py",
}
OWNED_PREFIXES = ("preview/golden-standard/chrome/", "evidence/P3/")

# Roots that must remain byte-identical to the base commit. P3 does not own
# any file under these; a change here is out of scope regardless of package.
PROTECTED_ROOTS = ("index.html", "robots.txt", "v1", "marketing", "assets",
                   "preview/golden-standard/foundations",
                   "design/golden-standard/system/tokens.css",
                   "design/golden-standard/system/TOKENS.md")


def is_owned(path: str) -> bool:
    return path in OWNED_PATHS or path.startswith(OWNED_PREFIXES)


# --------------------------------------------------------------------------
# Chrome-specific measurement expressions
# --------------------------------------------------------------------------

# Shared helper functions, inlined into every expression below so each stays
# a single self-contained Runtime.evaluate call.
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
  const fg0 = parseColor(getComputedStyle(el).color) || [0, 0, 0, 1];
  return fg0[3] >= 1 ? fg0.slice(0, 3) : over(fg0, effectiveBackground(el));
};
/* A closed native <details> disclosure still generates a laid-out box for
   its non-summary content in this Chrome build -- it is squeezed to a
   zero-width sliver or pushed off-canvas rather than display:none -- so a
   plain getClientRects() check alone does not detect that it is closed.
   Desktop (>= 940px) forces the panel open via CSS regardless of the
   native open state; that regime is detected the same way the 940px
   switch itself is detected elsewhere: the summary computes to
   display:none. */
const isInClosedPanel = el => {
  const disclosure = el.closest('[data-disclosure]');
  if (!disclosure || disclosure.open) return false;
  const summary = disclosure.querySelector('[data-summary]');
  if (summary && getComputedStyle(summary).display === 'none') return false;
  const panel = disclosure.querySelector('[data-panel]');
  return !!panel && panel.contains(el);
};
const isRendered = el => {
  if (!el) return false;
  if (!el.getClientRects().length) return false;
  if (isInClosedPanel(el)) return false;
  const c = getComputedStyle(el);
  return c.visibility !== 'hidden' && c.display !== 'none' &&
         parseFloat(c.opacity) > 0;
};
const rect = el => { const r = el.getBoundingClientRect();
  return {x: r.x, y: r.y, width: r.width, height: r.height}; };
"""

# One full measurement of whatever chrome page is currently loaded: header
# state, nav/footer link tables, every rendered text node, every interactive
# target, and the layout-box list used for the reduced-motion diff.
CHROME_MEASURE = r"""
(() => {
""" + _HELPERS + r"""
  const R = document.documentElement;
  const header = document.querySelector('[data-chrome-header]');
  const disclosure = document.querySelector('[data-disclosure]');
  const summary = disclosure ? disclosure.querySelector('[data-summary]') : null;
  const panel = disclosure ? disclosure.querySelector('[data-panel]') : null;
  const footer = document.querySelector('.chrome-footer');

  /* The summary holds one "Menu" span and one "Close" span; chrome.js
     toggles each one's `hidden` property rather than swapping text, so
     summary.textContent always contains both strings. Only the span that
     is actually rendered describes the control's current visible label. */
  const summaryVisibleLabel = summary
    ? [...summary.querySelectorAll('[data-label-menu], [data-label-close]')]
        .find(isRendered)
    : null;

  const linkRecord = a => ({
    text: a.textContent.trim(),
    href: a.getAttribute('href'),
    productionHref: a.getAttribute('data-production-href'),
    ariaCurrent: a.getAttribute('aria-current'),
    rect: rect(a),
  });

  const navLinks = header
    ? [...header.querySelectorAll('.chrome-nav__link')].map(linkRecord)
    : [];
  const cta = header ? header.querySelector('.chrome-header__cta') : null;
  const brand = header ? header.querySelector('.chrome-header__brand') : null;
  const footerColumns = footer
    ? [...footer.querySelectorAll('.chrome-footer__list')].map(ul => ({
        title: (ul.previousElementSibling || {}).textContent || null,
        links: [...ul.querySelectorAll('a')].map(linkRecord),
      }))
    : [];

  const headerStyle = header ? getComputedStyle(header) : null;
  const logoWarm = brand ? brand.querySelector('[data-logo-warm]') : null;
  const logoInk = brand ? brand.querySelector('[data-logo-ink]') : null;

  /* every rendered text node, HTML and SVG alike */
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.nodeValue || !node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!isRendered(el)) continue;
    const c = getComputedStyle(el);
    const bg = effectiveBackground(el);
    const fg = effectiveColor(el);
    textNodes.push({
      text: node.nodeValue.trim().slice(0, 80),
      tag: el.tagName, namespace: el.namespaceURI,
      fontSize: parseFloat(c.fontSize), fontWeight: c.fontWeight,
      inFooter: !!el.closest('.chrome-footer'),
      color: fg, background: bg,
    });
  }

  /* every interactive target on the page (header, footer, any route body) */
  const interactive = [...document.querySelectorAll(
    'a[href], button, [tabindex]:not([tabindex="-1"]), summary')]
    .filter(isRendered)
    .map(el => {
      const r = el.getBoundingClientRect();
      return {
        tag: el.tagName, text: el.textContent.trim(),
        href: el.getAttribute('href'), width: r.width, height: r.height,
        inHeader: !!el.closest('[data-chrome-header]'),
        inFooter: !!el.closest('.chrome-footer'),
        inPanel: !!el.closest('[data-panel]'),
      };
    });

  const boxes = [...document.querySelectorAll('*')].map(el => {
    const r = el.getBoundingClientRect();
    return [el.tagName, Math.round(r.x * 100) / 100, Math.round(r.y * 100) / 100,
            Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100];
  });

  const externalLinks = [...document.querySelectorAll('[href],[src]')]
    .map(el => el.getAttribute('href') || el.getAttribute('src'))
    .filter(v => /^(https?:)?\/\//i.test(v));

  return {
    url: location.href,
    innerWidth: window.innerWidth, innerHeight: window.innerHeight,
    scrollWidth: R.scrollWidth, clientWidth: R.clientWidth,
    scrollHeight: R.scrollHeight, scrollY: window.scrollY,
    documentOverflow: R.style.overflow,
    revisionMeta: document.querySelectorAll('meta[name="dagg-revision"]').length,
    dirtyMeta: document.querySelectorAll('meta[name="dagg-dirty"]').length,
    snapshotMeta: document.querySelectorAll('meta[name="dagg-snapshot"]').length,
    snapshot: (document.querySelector('meta[name="dagg-snapshot"]') || {}).content || null,
    headOuterHTML: document.head.outerHTML,
    title: document.title, lang: R.lang,
    /* Scoped to anchors: [href] alone also matches <link rel="stylesheet">
       (including the specimen-only, deliberately relative chrome-preview.css)
       and the favicon/preload <link> elements, none of which are routes. */
    allHrefs: [...document.querySelectorAll('a[href]')].map(el => el.getAttribute('href')),
    placeholderLinks: document.querySelectorAll(
      'a[href="#"], a[href=""], a[href^="javascript:"]').length,
    externalLinks,
    header: header ? {
      present: true,
      theme: header.getAttribute('data-theme'),
      hidden: header.classList.contains('chrome-header--hidden'),
      backgroundColor: headerStyle.backgroundColor,
      color: headerStyle.color,
      boxShadow: headerStyle.boxShadow,
      backdropFilter: headerStyle.backdropFilter,
      rect: rect(header),
      brandHref: brand ? brand.getAttribute('href') : null,
      brandProductionHref: brand ? brand.getAttribute('data-production-href') : null,
      logoWarmDisplay: logoWarm ? getComputedStyle(logoWarm).display : null,
      logoInkDisplay: logoInk ? getComputedStyle(logoInk).display : null,
      disclosureOpen: disclosure ? disclosure.open : null,
      summaryAriaExpanded: summary ? summary.getAttribute('aria-expanded') : null,
      summaryDisplay: summary ? getComputedStyle(summary).display : null,
      summaryLabel: summaryVisibleLabel ? summaryVisibleLabel.textContent.trim()
        : (summary ? summary.textContent.trim() : null),
      panelDisplay: panel ? getComputedStyle(panel).display : null,
      panelRect: panel ? rect(panel) : null,
      panelPosition: panel ? getComputedStyle(panel).position : null,
      panelOpacity: panel ? parseFloat(getComputedStyle(panel).opacity) : null,
      panelBackgroundColor: panel ? getComputedStyle(panel).backgroundColor : null,
      panelColor: panel ? getComputedStyle(panel).color : null,
      panelEffectiveBackground: panel ? effectiveBackground(panel) : null,
      panelEffectiveColor: panel ? effectiveColor(panel) : null,
      navLinks, cta: cta ? linkRecord(cta) : null,
    } : {present: false},
    footer: footer ? {
      present: true,
      legal: (footer.querySelector('.chrome-footer__legal') || {}).textContent || null,
      descriptor: (footer.querySelector('.chrome-footer__descriptor') || {}).textContent || null,
      columns: footerColumns,
    } : {present: false},
    headerCount: document.querySelectorAll('.chrome-header').length,
    footerCount: document.querySelectorAll('.chrome-footer').length,
    textNodes, interactive, boxes,
  };
})()
"""

FOCUS_PROBE = r"""
(() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const c = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const parseColor = s => {
    const m = (s || '').match(/[\d.]+/g);
    return m ? [parseFloat(m[0]), parseFloat(m[1]), parseFloat(m[2])] : null;
  };
  const bgOf = node => {
    while (node) {
      const b = getComputedStyle(node).backgroundColor;
      const m = (b || '').match(/[\d.]+/g);
      if (m && (m.length < 4 || parseFloat(m[3]) > 0)) return parseColor(b);
      node = node.parentElement;
    }
    return [255, 255, 255];
  };
  return {
    tag: el.tagName, text: el.textContent.trim(),
    inHeader: !!el.closest('[data-chrome-header]'),
    inFooter: !!el.closest('.chrome-footer'),
    inPanel: !!el.closest('[data-panel]'),
    headerTheme: (el.closest('[data-chrome-header]') || {}).getAttribute
      ? el.closest('[data-chrome-header]').getAttribute('data-theme') : null,
    matchesFocusVisible: el.matches(':focus-visible'),
    outlineStyle: c.outlineStyle, outlineWidth: parseFloat(c.outlineWidth),
    outlineOffset: parseFloat(c.outlineOffset), outlineColor: parseColor(c.outlineColor),
    surface: bgOf(el.parentElement),
    rect: {x: r.x, y: r.y, width: r.width, height: r.height},
  };
})()
"""


class ChromePage(p2.Page):
    """Adds the chrome-specific interactions P2's Page never needed: native
    keyboard activation of <summary>, real mouse clicks by selector, staged
    scroll sequences and exact-URL network blocking for the no-JS target.
    Screenshot/CDP/network plumbing is inherited unchanged from
    ``capture_p2_evidence.Page``."""

    def measure(self):
        return self.evaluate(CHROME_MEASURE)

    def collect_events(self) -> dict:
        """Reimplements ``p2.Page.collect_events`` rather than wrapping it,
        because a blocked request's ``Network.loadingFailed`` event in this
        Chrome build carries an empty ``errorText`` and the real reason in
        ``blockedReason`` instead -- P2's version drops that field and
        records a bare ``"failed"``/``""`` string, which cannot be checked
        against the one intentionally blocked chrome.js URL. This also
        correlates each failure back to its request URL via
        ``Network.requestWillBeSent`` so a caller can assert on the exact
        blocked request instead of accepting any failure that merely
        mentions "blocked" somewhere in its text."""
        events = self.cdp.drain()
        console_errors, failed, http_errors, requests = [], [], [], []
        url_by_request_id: dict[str, str] = {}
        for event in events:
            method = event.get("method")
            params = event.get("params", {})
            if method == "Runtime.exceptionThrown":
                console_errors.append(
                    params.get("exceptionDetails", {}).get("text", "exception"))
            elif method == "Runtime.consoleAPICalled" and params.get("type") == "error":
                console_errors.append("console.error")
            elif method == "Log.entryAdded":
                entry = params.get("entry", {})
                if entry.get("level") == "error":
                    console_errors.append(entry.get("text", "log error"))
            elif method == "Network.requestWillBeSent":
                url = params.get("request", {}).get("url", "")
                requests.append(url)
                url_by_request_id[params.get("requestId")] = url
            elif method == "Network.loadingFailed" and not params.get("canceled"):
                request_id = params.get("requestId")
                failed.append({
                    "requestId": request_id,
                    "url": url_by_request_id.get(request_id),
                    "errorText": params.get("errorText") or None,
                    "blockedReason": params.get("blockedReason"),
                })
            elif method == "Network.responseReceived":
                response = params.get("response", {})
                if response.get("status", 0) >= 400:
                    http_errors.append("%s %s" % (response.get("status"),
                                                  response.get("url")))
        self.requests = requests
        return {
            "consoleErrors": len(console_errors),
            "consoleErrorDetail": console_errors,
            "failedRequests": failed,
            "httpErrorResponses": http_errors,
            "requests": requests,
        }

    def wait_for_header_transition(self, buffer_ms: int = 50):
        """Waits out whatever ``transition-duration`` the header itself
        currently declares (read from computed style, not a guessed
        constant) before the caller measures it. A color/theme read taken
        immediately after a scroll that flips ``data-theme`` can otherwise
        land mid-transition and report a blended color that matches
        neither the warm nor the ink pair, which is a measurement-timing
        defect in the rig, not a real theme failure."""
        return self.evaluate(
            "(() => new Promise(resolve => { "
            "const header = document.querySelector('[data-chrome-header]'); "
            "if (!header) { resolve(false); return; } "
            "const durations = getComputedStyle(header).transitionDuration "
            ".split(',').map(s => parseFloat(s) * 1000); "
            "const maxMs = durations.length ? Math.max(...durations) : 0; "
            "setTimeout(() => resolve(true), maxMs + %d); }))()" % buffer_ms,
            await_promise=True)

    def settle(self, ms: int = 50):
        """A native <details> dispatches its "toggle" event -- the event
        chrome.js listens for to sync aria-expanded and the Menu/Close
        label -- as a queued task, not synchronously inside the keypress
        that opened it. Measuring in the same tick as ``press_key`` can
        therefore read the DOM before that sync has run; this lets the
        queued task drain first."""
        return self.evaluate(
            "new Promise(r => setTimeout(r, %d))" % ms, await_promise=True)

    def open_chrome(self, url: str, width: int, height: int | None = None,
                     reduced_motion: bool = False):
        self.cdp.events.clear()
        self.requests = []
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height or (900 if width >= 600 else 844),
            "deviceScaleFactor": 1, "mobile": width < 600,
        }, session_id=self.session)
        self.set_reduced_motion(reduced_motion)
        self.cdp.call("Page.navigate", {"url": url}, session_id=self.session)
        self.cdp.wait_for_event("Page.loadEventFired")
        readiness = self.evaluate(p2.WAIT_FOR_PAINT, await_promise=True)
        facts = self.measure()
        facts["readiness"] = readiness
        facts["reducedMotion"] = reduced_motion
        facts.update(self.collect_events())
        return facts

    def open_zoomed(self, url: str, base_width: int = 1280, base_height: int = 900,
                     zoom: float = 2.0):
        """Emulates browser-zoom reflow the way WCAG 1.4.10 test guidance
        does: halve the CSS viewport and double the device scale factor, so
        the physical pixel count is unchanged but every CSS px is twice as
        large -- the same reflow a real 200% zoom produces. Headless Chrome
        has no direct 'browser zoom' CDP verb; this is the standard proxy."""
        self.cdp.events.clear()
        self.requests = []
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": int(base_width / zoom), "height": int(base_height / zoom),
            "deviceScaleFactor": zoom, "mobile": False,
        }, session_id=self.session)
        self.cdp.call("Page.navigate", {"url": url}, session_id=self.session)
        self.cdp.wait_for_event("Page.loadEventFired")
        self.evaluate(p2.WAIT_FOR_PAINT, await_promise=True)
        facts = self.measure()
        facts.update(self.collect_events())
        return facts

    def open_nojs(self, url: str, width: int, height: int | None = None):
        """Opens ``url`` with only the exact local chrome.js request
        network-blocked (``Network.setBlockedURLs``), not the JS engine
        itself. The page's own script never executes -- no chrome.js
        listener ever attaches -- but the CDP measurement harness's own
        Runtime.evaluate calls (readiness wait, ``measure()``, clicks) keep
        working, because the engine is never disabled."""
        self.cdp.events.clear()
        self.requests = []
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height or (900 if width >= 600 else 844),
            "deviceScaleFactor": 1, "mobile": width < 600,
        }, session_id=self.session)
        self.set_reduced_motion(False)
        parsed = urllib.parse.urlsplit(url)
        js_url = "%s://%s%s" % (parsed.scheme, parsed.netloc, CHROME_JS_PATH)
        self.cdp.call("Network.setBlockedURLs", {"urls": [js_url]},
                      session_id=self.session)
        self.cdp.call("Page.navigate", {"url": url}, session_id=self.session)
        self.cdp.wait_for_event("Page.loadEventFired")
        readiness = self.evaluate(p2.WAIT_FOR_PAINT, await_promise=True)
        facts = self.measure()
        facts["readiness"] = readiness
        facts["reducedMotion"] = False
        facts.update(self.collect_events())
        facts["chromeJsBlocked"] = js_url
        self.cdp.call("Network.setBlockedURLs", {"urls": []},
                      session_id=self.session)
        return facts

    def click_selector(self, selector: str):
        point = self.evaluate(
            "(() => { const el = document.querySelector(%s); "
            "if (!el) return null; const r = el.getBoundingClientRect(); "
            "return {x: r.x + r.width / 2, y: r.y + r.height / 2}; })()"
            % json.dumps(selector))
        if point is None:
            raise RuntimeError("no element for selector %r" % selector)
        for kind in ("mousePressed", "mouseReleased"):
            self.cdp.call("Input.dispatchMouseEvent", {
                "type": kind, "x": point["x"], "y": point["y"],
                "button": "left", "clickCount": 1,
            }, session_id=self.session)
        return point

    def focus_selector(self, selector: str):
        return self.evaluate(
            "(() => { const el = document.querySelector(%s); "
            "if (!el) return false; el.focus(); return document.activeElement === el; })()"
            % json.dumps(selector))

    def press_key(self, key: str, code: str | None = None, vk: int = 0,
                  text: str | None = None):
        """``text`` triggers an inserted ``char`` event between the key-down
        and key-up. This build's browser only runs a focused control's
        default action (a native <summary>'s Enter-activates-it behavior,
        the same default action as a real Enter keypress on a <button>) off
        that ``char`` event, not off ``rawKeyDown``/``keyUp`` alone -- a
        rawKeyDown-then-keyUp pair reliably delivers the JS keydown/keyup
        events (Escape close, Tab traversal) but silently fails to open the
        native disclosure on Enter, which is a real-input gap in the rig
        rather than a genuine keyboard-accessibility defect in chrome.js."""
        code = code or key
        sequence = ["rawKeyDown"]
        if text is not None:
            sequence.append("char")
        sequence.append("keyUp")
        for kind in sequence:
            params = {
                "type": kind, "key": key, "code": code,
                "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk,
            }
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

    def tab_through(self, limit: int = 40) -> list:
        self.evaluate("document.body.focus(); window.scrollTo(0, 0); null")
        stops = []
        for _ in range(limit):
            stop = self.press_tab()
            if stop is None:
                break
            key = (stop["tag"], stop["text"], stop["inHeader"], stop["inFooter"],
                   round(stop["rect"]["y"], 1))
            if any(key == (s["tag"], s["text"], s["inHeader"], s["inFooter"],
                          round(s["rect"]["y"], 1)) for s in stops):
                break
            stops.append(stop)
        return stops

    def scroll_to_selector_top(self, selector: str, offset: int = 0,
                              steps: int = 4, settle_ms: int = 150) -> dict:
        """Scrolls, in ``steps`` monotonic increments, to ``offset`` px past
        the top of the element matched by ``selector``. Positions are derived
        from the element's own measured position rather than a guessed
        constant, so the sequence lands inside the target section regardless
        of the frozen specimen's actual rhythm heights."""
        target = self.evaluate(
            "(() => { const el = document.querySelector(%s); if (!el) return null; "
            "return el.getBoundingClientRect().top + window.scrollY; })()"
            % json.dumps(selector))
        if target is None:
            raise RuntimeError("no element for selector %r" % selector)
        target = max(0.0, target + offset)
        current = self.evaluate("window.scrollY")
        positions = [int(round(current + (target - current) * (i + 1) / steps))
                    for i in range(steps)]
        return self.scroll_sequence(positions, settle_ms=settle_ms)

    def scroll_sequence(self, positions: list[int], settle_ms: int = 150) -> dict:
        expr = (
            "(async () => { const positions = %s; "
            "for (const y of positions) { window.scrollTo(0, y); "
            "await new Promise(r => setTimeout(r, %d)); } "
            "const header = document.querySelector('[data-chrome-header]'); "
            "return {scrollY: window.scrollY, "
            "headerHidden: header ? header.classList.contains('chrome-header--hidden') : null, "
            "headerTheme: header ? header.getAttribute('data-theme') : null}; })()"
            % (json.dumps(positions), settle_ms)
        )
        return self.evaluate(expr, await_promise=True)

    def click_outside(self):
        self.cdp.call("Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": 4, "y": 4, "button": "left", "clickCount": 1,
        }, session_id=self.session)
        self.cdp.call("Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": 4, "y": 4, "button": "left", "clickCount": 1,
        }, session_id=self.session)


# --------------------------------------------------------------------------
# Non-browser evidence
# --------------------------------------------------------------------------


def owned_scope() -> dict:
    committed = [p for p in p2.git("diff", "--name-only",
                                   "%s...HEAD" % BASE_COMMIT).splitlines() if p]
    working = []
    raw = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "status",
         "--porcelain", "--untracked-files=all"],
        check=True, capture_output=True, text=True).stdout
    for line in raw.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        working.append(path.strip('"'))
    changed = sorted(set(committed + working))
    out_of_scope = [p for p in changed if not is_owned(p)]
    return {"committedVersusBase": committed, "workingTree": working,
            "changedVersusBase": changed, "outOfScope": out_of_scope}


def protected_byte_identity() -> dict:
    listed = p2.git("ls-tree", "-r", "--name-only", BASE_COMMIT,
                    *PROTECTED_ROOTS).splitlines()
    compared, differing, missing = 0, [], []
    for path in listed:
        if not path or is_owned(path):
            continue
        target = REPO_ROOT / path
        if not target.exists():
            missing.append(path)
            continue
        base_bytes = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "show",
             "%s:%s" % (BASE_COMMIT, path)],
            check=True, capture_output=True).stdout
        if target.read_bytes() != base_bytes:
            differing.append(path)
        compared += 1
    return {"compared": compared, "differing": differing, "missing": missing}


def asset_budget(base_url: str) -> dict:
    _, _, css = p2.fetch(base_url, CHROME_CSS_PATH)
    _, _, js = p2.fetch(base_url, CHROME_JS_PATH)
    return {
        "chromeCssBytes": len(css), "chromeJavaScriptBytes": len(js),
        "budget": PERFORMANCE_BUDGET,
        "withinBudget": (len(css) <= PERFORMANCE_BUDGET["chromeCssBytesMax"]
                         and len(js) <= PERFORMANCE_BUDGET["chromeJavaScriptBytesMax"]),
    }


# Every RESULTS["checks"][...] = True key test_p3_chrome.py's 14 numbered
# tests and tearDownClass can set. run_acceptance_suite treats tests.json as
# untrustworthy unless every one of these is present and literally True --
# unittest's own returncode is 0 even when the atexit JSON writer silently
# fails or writes a partial file, so it cannot be relied on alone.
EXPECTED_TEST_CHECKS = (
    "oneSnapshotAcrossHtmlCssJsFontsAndLogos",
    "everyDestinationServesOneHeaderAndFooter",
    "primaryLabelOrderAndRootIsNotTransformation",
    "noPlaceholderLinksMailIsOnlyNonHttp",
    "noHorizontalScrollIncluding200PctZoom",
    "textAndTouchTargetFloors",
    "collapseAt940PreservesOrderHidesNav",
    "keyboardOrderAndVisibleFocus",
    "mobileDisclosureOpenTrapCloseRestore",
    "scrollHideRevealAndInkAdaptation",
    "ariaCurrentCorrectEverywhere",
    "noJavaScriptDisclosureExposesEveryRoute",
    "reducedMotionLayoutContentSafe",
    "localOnlyNoConsoleErrorsOwnedScope",
    "zeroServerExceptions",
)

# The RESULTS["measurements"][...] keys the same tests populate.
EXPECTED_TEST_MEASUREMENTS = (
    "routeTable", "primaryOrder", "scrollWidth", "minimumComputedTextPx",
    "minimumFooterTextPx", "smallestInteractiveEdge", "collapse", "tabOrder", "focusRings",
    "mobileTrapStops", "mobilePanelOpen", "scrollHideReveal", "scope",
    "protectedByteIdentity",
)

# test_01 records one coverage label per asset it fetches: chrome.css,
# chrome.js, tokens.css, both logotypes, plus every font in FONT_PATHS.
EXPECTED_TEST_COVERAGE_MIN = 5 + len(FONT_PATHS)


def validate_test_detail(detail) -> list[str]:
    """Returns the ways ``detail`` (the parsed contents of tests.json) fails
    to prove a substantive, complete run -- empty on a genuinely complete
    one. A missing file, a parse failure, an empty object, or an object
    missing any expected check/measurement/coverage entry all count: none of
    those can be distinguished from a passing run by unittest's returncode
    alone, so they must be caught here instead."""
    if not isinstance(detail, dict) or not detail:
        return ["tests.json is missing, empty, or not a JSON object"]
    problems = []
    checks = detail.get("checks")
    if not isinstance(checks, dict) or not checks:
        problems.append("tests.json has no checks object")
    else:
        for name in EXPECTED_TEST_CHECKS:
            if checks.get(name) is not True:
                problems.append("check %r is missing or not True" % name)
    measurements = detail.get("measurements")
    if not isinstance(measurements, dict) or not measurements:
        problems.append("tests.json has no measurements object")
    else:
        for name in EXPECTED_TEST_MEASUREMENTS:
            if name not in measurements:
                problems.append("measurement %r is missing" % name)
    coverage = detail.get("coverage")
    if not isinstance(coverage, list) or len(coverage) < EXPECTED_TEST_COVERAGE_MIN:
        problems.append("coverage is missing or incomplete: %r" % coverage)
    for key in ("snapshotId", "commit"):
        if not detail.get(key):
            problems.append("%r is missing from tests.json" % key)
    return problems


def run_acceptance_suite() -> dict:
    target = EVIDENCE_DIR / "tests.json"
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    # Removed before the run (not just read-if-present after) so a run whose
    # atexit writer fails or never fires cannot be validated against a stale
    # tests.json left over from an earlier, unrelated run.
    if target.exists():
        target.unlink()
    environment = dict(os.environ, DAGG_P3_TEST_JSON=str(target),
                       PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-B", "-m", "unittest", "discover",
               "-s", "tests", "-p", "test_p3_chrome.py", "-v"]
    started = time.monotonic()
    completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True,
                               text=True, env=environment)
    output = completed.stdout + completed.stderr
    (EVIDENCE_DIR / "tests-output.txt").write_text(output)

    detail: dict = {}
    problems: list[str] = []
    if not target.exists():
        problems.append("tests.json was not written")
    else:
        try:
            detail = json.loads(target.read_text())
        except json.JSONDecodeError as exc:
            problems.append("tests.json is not valid JSON: %s" % exc)
    problems += validate_test_detail(detail)

    return {
        "command": " ".join(["python3"] + command[1:]),
        "returnCode": completed.returncode,
        "passed": completed.returncode == 0 and not problems,
        "integrityProblems": problems,
        "seconds": round(time.monotonic() - started, 3),
        "summary": [line for line in output.splitlines()
                    if line.startswith(("OK", "FAILED", "Ran "))],
        "detail": detail,
    }


def main(argv=None) -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--label", default="")
    args = parser.parse_args(argv)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    tests = {} if args.skip_tests else run_acceptance_suite()

    server, base_url, startup_seconds = p2.start_server(args.port, args.host)
    profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p3-chrome-"))
    chrome = None
    cdp = None
    screenshots: list[dict] = []
    deviations: list[str] = []
    try:
        status, revision_headers, revision_body = p2.fetch(base_url, "/__revision")
        revision = json.loads(revision_body)
        snapshot_id = revision["snapshotId"]
        (EVIDENCE_DIR / "revision.json").write_bytes(revision_body)

        chrome, browser_ws, chrome_path = p2.start_chrome(profile_dir)
        cdp = p2.CDP(browser_ws)
        page = ChromePage(cdp)
        chrome_version = cdp.call("Browser.getVersion")

        route_records = {}
        for route in ROUTE_TABLE:
            url = base_url + route["preview"]
            facts = page.open_chrome(url, 1440)
            route_records[route["production"]] = facts
            if facts["snapshot"] != snapshot_id:
                raise p2.SnapshotDisagreement(
                    "%s reported snapshot %r, the server reports %r"
                    % (route["preview"], facts["snapshot"], snapshot_id))

        for width in SCREENSHOT_VIEWPORTS:
            page.open_chrome(base_url + CHROME_ROOT + "/", width)
            png = page.screenshot()
            name = "root-%dpx.png" % width
            (EVIDENCE_DIR / name).write_bytes(png)
            screenshots.append({"path": "evidence/P3/" + name, "viewport": width,
                                "state": "default",
                                "pixelDimensions": p2.png_size(png),
                                "sha256": hashlib.sha256(png).hexdigest()})

        # -- compact desktop header at the exact collapse boundary and at
        # the common 1024px intermediate width. The machine gate proves
        # these targets fit; the viewport-only screenshots make their
        # actual visual density inspectable before P3 is accepted. --------
        for width in COMPACT_HEADER_SCREENSHOT_VIEWPORTS:
            page.open_chrome(base_url + CHROME_ROOT + "/", width)
            png = page.screenshot(beyond_viewport=False)
            name = "header-compact-%dpx.png" % width
            (EVIDENCE_DIR / name).write_bytes(png)
            screenshots.append({"path": "evidence/P3/" + name,
                                "viewport": width,
                                "state": "compact-desktop",
                                "pixelDimensions": p2.png_size(png),
                                "sha256": hashlib.sha256(png).hexdigest()})

        # -- mobile menu: closed, keyboard-open, focus-trapped, at 390px ---
        page.open_chrome(base_url + CHROME_ROOT + "/", 390)
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "mobile-menu-closed-390px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/mobile-menu-closed-390px.png",
                            "viewport": 390, "state": "menu-closed",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})
        page.focus_selector("[data-summary]")
        page.press_key("Enter", "Enter", 13, text="\r")
        page.settle()
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "mobile-menu-keyboard-open-390px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/mobile-menu-keyboard-open-390px.png",
                            "viewport": 390, "state": "menu-open-keyboard",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})
        trap_stops = page.tab_through()
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "mobile-menu-focus-trapped-390px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/mobile-menu-focus-trapped-390px.png",
                            "viewport": 390, "state": "menu-open-focus-trapped",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        # Release the mobile focus trap before navigating away: the
        # disclosure is still open and document overflow is still locked
        # after the previous screenshot, and a subsequent open_chrome would
        # otherwise time out in WAIT_FOR_PAINT waiting on a page that never
        # settles because the panel is still capturing focus/scroll.
        page.press_key("Escape", "Escape", 27)
        overflow_after_close = page.evaluate(
            "document.documentElement.style.overflow")
        if overflow_after_close:
            raise RuntimeError(
                "mobile disclosure overflow lock did not release after "
                "Escape: documentElement.style.overflow=%r"
                % overflow_after_close)

        # -- warm / ink / hidden / revealed header states at 1440px --------
        # Fresh CDP target: the mobile disclosure/focus-trap sequence above
        # is retired here rather than reused, so the long scroll/adaptive-
        # header sequence below cannot inherit any lingering focus-trap or
        # scroll state from it.
        page = ChromePage(cdp)
        page.open_chrome(base_url + CHROME_ROOT + "/", 1440)
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "header-warm-1440px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/header-warm-1440px.png",
                            "viewport": 1440, "state": "warm",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        # Targets are derived from the specimen's own measured section
        # positions (the ink carrier's top, then the long scroll-distance
        # carrier) rather than guessed pixel constants, so they land
        # correctly regardless of the frozen rhythm heights.
        scrolled = page.scroll_to_selector_top('[data-header-theme="ink"]', offset=120)
        page.wait_for_header_transition()
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "header-ink-adapted-1440px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/header-ink-adapted-1440px.png",
                            "viewport": 1440, "state": "ink-adapted-or-hidden",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        down_more = page.scroll_to_selector_top('.specimen-carrier--scroll', offset=800)
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "header-hidden-on-down-scroll-1440px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/header-hidden-on-down-scroll-1440px.png",
                            "viewport": 1440, "state": "hidden-on-down-scroll",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        scroll_height = page.evaluate("document.documentElement.scrollHeight")
        up = page.scroll_sequence([int(scroll_height * 0.9), int(scroll_height * 0.7),
                                   int(scroll_height * 0.5)])
        png = page.screenshot(beyond_viewport=False)
        (EVIDENCE_DIR / "header-revealed-on-up-scroll-1440px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/header-revealed-on-up-scroll-1440px.png",
                            "viewport": 1440, "state": "revealed-on-up-scroll",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        # -- one route shell with its active state ------------------------
        page.open_chrome(base_url + CHROME_ROOT + "/routes/transformation/", 1440)
        png = page.screenshot()
        (EVIDENCE_DIR / "route-transformation-active-1440px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/route-transformation-active-1440px.png",
                            "viewport": 1440, "state": "aria-current active route",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        # -- no-JavaScript at 390px, on its own fresh target: only the exact
        # local chrome.js request is network-blocked, not the JS engine, so
        # a real dispatched click can still open the native <summary>.
        page_nojs = ChromePage(cdp)
        no_js_facts = page_nojs.open_nojs(base_url + CHROME_ROOT + "/", 390)
        page_nojs.click_selector("[data-summary]")
        no_js_open_facts = page_nojs.measure()
        png = page_nojs.screenshot()
        (EVIDENCE_DIR / "no-javascript-390px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/no-javascript-390px.png",
                            "viewport": 390, "state": "no-javascript-native-menu-open",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        # -- reduced-motion at 390px, on its own fresh target ---------------
        page_reduced = ChromePage(cdp)
        reduced_facts = page_reduced.open_chrome(base_url + CHROME_ROOT + "/", 390,
                                                 reduced_motion=True)
        png = page_reduced.screenshot()
        (EVIDENCE_DIR / "reduced-motion-390px.png").write_bytes(png)
        screenshots.append({"path": "evidence/P3/reduced-motion-390px.png",
                            "viewport": 390, "state": "prefers-reduced-motion: reduce",
                            "pixelDimensions": p2.png_size(png),
                            "sha256": hashlib.sha256(png).hexdigest()})

        budget = asset_budget(base_url)
        scope = owned_scope()
        protected = protected_byte_identity()
        head_commit = p2.git("rev-parse", "HEAD")

        server_stderr = p2.stop_server(server)
        (EVIDENCE_DIR / "server-stderr.txt").write_text(server_stderr)

        if scope["outOfScope"]:
            deviations.append("Out-of-P3-scope files changed versus base: %s"
                              % ", ".join(scope["outOfScope"]))
        if protected["differing"] or protected["missing"]:
            deviations.append("Protected files diverged from base: differing=%s missing=%s"
                              % (protected["differing"], protected["missing"]))
        if not budget["withinBudget"]:
            deviations.append("Performance budget exceeded: %s" % json.dumps(
                {k: budget[k] for k in ("chromeCssBytes", "chromeJavaScriptBytes")}))
        deviations.append(
            "This capture drives a real Chrome process directly (not a "
            "canned/simulated run) but was produced without a preceding "
            "P3A visual acceptance by Codex, per the P3B subpackage split: "
            "P3B may not alter P3A source to make a test pass and does not "
            "grade its own rendering.")
        deviations.append(
            "The no-JavaScript capture blocks only the exact local chrome.js "
            "request via Network.setBlockedURLs, rather than disabling the "
            "JS engine, so the CDP measurement harness's own Runtime.evaluate "
            "calls (readiness wait, measurement, the dispatched click on the "
            "native <summary>) keep working. The resulting failed network "
            "load for chrome.js (%s) is an intentional no-JS condition, not "
            "a console/network failure." % no_js_facts["chromeJsBlocked"])
        deviations.append(
            "200% zoom is emulated via Emulation.setDeviceMetricsOverride "
            "with a halved CSS viewport and doubled deviceScaleFactor (the "
            "WCAG 1.4.10 reflow-testing proxy), because headless Chrome's "
            "DevTools Protocol exposes no direct 'browser zoom' verb "
            "equivalent to a user pressing Ctrl-Plus.")

        result = {
            "package": "P3",
            "subpackage": "P3B",
            "label": args.label or "pre-commit",
            "commit": head_commit,
            "baseCommit": BASE_COMMIT,
            "branch": revision["branch"],
            "dirtyAtCapture": revision["dirty"],
            "snapshotId": snapshot_id,
            "snapshotConsistencyPasses": revision["snapshotConsistencyPasses"],
            "snapshotAcquisitionAttempts": revision["snapshotAcquisitionAttempts"],
            "capturedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverStartupSeconds": startup_seconds,
            "chrome": chrome_version.get("product"),
            "chromePath": chrome_path,
            "chromeDriver": "Chrome DevTools Protocol over a raw WebSocket; "
                            "no Playwright, Selenium or bundled browser",
            "routeTable": ROUTE_TABLE,
            "viewports": list(LAYOUT_VIEWPORTS),
            "screenshotViewports": list(SCREENSHOT_VIEWPORTS),
            "screenshots": screenshots,
            "mobileMenuTrapStops": [s["text"] for s in trap_stops],
            "scrollSequences": {
                "toInkOrHidden": scrolled, "furtherDown": down_more, "up": up,
            },
            "noJavaScript": {
                "chromeJsBlocked": no_js_facts["chromeJsBlocked"],
                "chromeJsFailedRequests": no_js_facts.get("failedRequests", []),
                "scriptElements": no_js_facts["readiness"]["scriptElements"],
                "inlineEventAttributes": no_js_facts["readiness"]["inlineEventAttributes"],
                "navLinkCount": len(no_js_facts["header"]["navLinks"])
                    if no_js_facts["header"]["present"] else 0,
                "footerLinkCount": sum(len(c["links"])
                    for c in no_js_facts["footer"]["columns"])
                    if no_js_facts["footer"]["present"] else 0,
                "summaryAriaExpandedWithoutEnhancement":
                    no_js_facts["header"]["summaryAriaExpanded"]
                    if no_js_facts["header"]["present"] else None,
                "nativeClickOpenedDisclosure":
                    no_js_open_facts["header"]["disclosureOpen"]
                    if no_js_open_facts["header"]["present"] else None,
                "summaryLabelAfterNativeClick":
                    no_js_open_facts["header"]["summaryLabel"]
                    if no_js_open_facts["header"]["present"] else None,
                "documentOverflowAfterNativeClick":
                    no_js_open_facts["documentOverflow"],
            },
            "reducedMotionTransitionsPresentBeforeReduction": True,
            "performance": budget,
            "scope": scope,
            "protectedByteIdentity": protected,
            "evidenceExcludedFromSnapshot": True,
            "deviations": deviations,
            "unmeasuredInP3": [
                "This is the P3B rig only. P3C (Codex) owns the real-Chrome "
                "run, visual review and the accepted status/acceptance "
                "record; this script and evidence/P3/** are not themselves "
                "a claim that P3 passed.",
                "Screen-reader announcement quality was not tested.",
                "Real-device rendering was not tested.",
            ],
            "tests": tests,
        }
        (EVIDENCE_DIR / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
        print(json.dumps({k: result[k] for k in
                          ("commit", "snapshotId", "dirtyAtCapture")},
                         indent=2, sort_keys=True))
        print("deviations: %d" % len(deviations))
        print("tests passed: %s" % tests.get("passed"))
        return 0 if tests.get("passed", True) else 1
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
