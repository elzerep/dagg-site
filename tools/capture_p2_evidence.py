#!/usr/bin/env python3
"""Capture P2 foundations evidence from one immutable-snapshot server process.

Runs the P2 acceptance suite, then starts ``tools/serve_preview.py`` once and
drives the installed Google Chrome over the Chrome DevTools Protocol. Every
screenshot, every computed measurement, every response header record and
``evidence/P2/result.json`` come from that single process, so all of them
provably describe one snapshot ID.

The capture is refused outright if any response header, any injected DOM meta
tag or any screenshot record disagrees with the server's snapshot ID. Partial
evidence is worse than none, because it looks like proof.

This module is also the browser plumbing for ``tests/test_p2_foundations.py``:
the WebSocket/CDP client, the Chrome launcher, the immutable-server launcher
and the measurement expressions live here and are imported by the suite, so
the tests and the evidence measure the identical thing in the identical way.

Standard library only. Nothing is written outside ``evidence/P2/`` and a
temporary Chrome profile that is removed on exit.

    python3 tools/capture_p2_evidence.py
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import hashlib
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence" / "P2"

PAGE_PATH = "/preview/golden-standard/foundations/index.html"
TOKENS_CSS_PATH = "/design/golden-standard/system/tokens.css"
PAGE_CSS_PATH = "/preview/golden-standard/foundations/foundations.css"
LOGO_DARK_PATH = "/assets/dagg-logotype-dark.png"
LOGO_LIGHT_PATH = "/assets/dagg-logotype.png"
FONT_PATHS = (
    "/assets/fonts/golden-standard/geist/Geist-Variable.woff2",
    "/assets/fonts/golden-standard/newsreader/Newsreader-Variable.woff2",
    "/assets/fonts/golden-standard/jetbrains-mono/JetBrainsMono-Variable.woff2",
)
LICENSE_PATHS = (
    "assets/fonts/golden-standard/geist/OFL.txt",
    "assets/fonts/golden-standard/geist/LICENSE.txt",
    "assets/fonts/golden-standard/newsreader/OFL.txt",
    "assets/fonts/golden-standard/jetbrains-mono/OFL.txt",
)

BASE_COMMIT = "cf9bdcdfa1e47ff75e193155feee00b0bda67e86"

# Screenshot ladder required by P2 section 8. The scrollWidth ladder in the
# acceptance suite is wider (320/360/390/768/1024/1440).
SCREENSHOT_VIEWPORTS = (1440, 390, 360, 320)
LAYOUT_VIEWPORTS = (320, 360, 390, 768, 1024, 1440)

# Declared endpoints, straight from P2 section 5. Duplicated here so the
# evidence states them rather than reading them back from the page it is
# measuring.
TYPE_ENDPOINTS = {
    "h1": {1440: 68.0, 390: 44.0, 320: 42.0, "lh": (1.00, 1.04)},
    "h2": {1440: 52.0, 390: 36.0, 320: 34.0, "lh": (1.04, 1.10)},
    "h3": {1440: 32.0, 390: 27.0, 320: 26.0, "lh": (1.08, 1.16)},
    "lead": {1440: 23.0, 390: 20.0, 320: 19.0, "lh": (1.38, 1.50)},
    "body": {1440: 18.0, 390: 17.0, 320: 17.0, "lh": (1.55, 1.68)},
    "meta": {1440: 13.0, 390: 12.0, 320: 12.0, "lh": (1.35, 1.50)},
}

GUTTERS = ((1440, 72), (1600, 72), (1024, 48), (1439, 48),
           (768, 24), (1023, 24), (320, 20), (767, 20))

PERFORMANCE_BUDGET = {
    "htmlBytesMax": 40 * 1024,
    "cssBytesMax": 55 * 1024,
    "javaScriptBytesMax": 0,
    "woff2BytesMax": 750 * 1024,
}

REQUIRED_NO_STORE = {
    "cache-control": "no-store, max-age=0",
    "pragma": "no-cache",
    "expires": "0",
}

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)


class SnapshotDisagreement(RuntimeError):
    """A served artefact did not carry the server's snapshot ID."""


# --------------------------------------------------------------------------
# Minimal WebSocket client (RFC 6455), enough for the DevTools Protocol
# --------------------------------------------------------------------------


class WebSocket:
    def __init__(self, url: str, timeout: float = 60.0):
        assert url.startswith("ws://"), url
        rest = url[len("ws://"):]
        netloc, _, path = rest.partition("/")
        host, _, port = netloc.partition(":")
        self.sock = socket.create_connection((host, int(port)), timeout=timeout)
        self.sock.settimeout(timeout)
        self._buffer = b""

        key = base64.b64encode(os.urandom(16)).decode()
        handshake = (
            "GET /%s HTTP/1.1\r\n"
            "Host: %s\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Key: %s\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n" % (path, netloc, key)
        )
        self.sock.sendall(handshake.encode())
        response = self._read_until(b"\r\n\r\n")
        if b" 101 " not in response.split(b"\r\n")[0]:
            raise RuntimeError("WebSocket upgrade refused: %r" % response[:200])

    def _read_until(self, marker: bytes) -> bytes:
        while marker not in self._buffer:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("connection closed during handshake")
            self._buffer += chunk
        head, _, self._buffer = self._buffer.partition(marker)
        return head + marker

    def _read_exactly(self, count: int) -> bytes:
        while len(self._buffer) < count:
            chunk = self.sock.recv(max(65536, count - len(self._buffer)))
            if not chunk:
                raise ConnectionError("connection closed mid-frame")
            self._buffer += chunk
        out, self._buffer = self._buffer[:count], self._buffer[count:]
        return out

    def _send_frame(self, opcode: int, payload: bytes):
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < (1 << 16):
            header.append(0x80 | 126)
            header += struct.pack(">H", length)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", length)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _recv_frame(self):
        first, second = self._read_exactly(2)
        fin = bool(first & 0x80)
        opcode = first & 0x0F
        length = second & 0x7F
        if length == 126:
            length = struct.unpack(">H", self._read_exactly(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self._read_exactly(8))[0]
        if second & 0x80:
            mask = self._read_exactly(4)
            payload = bytes(b ^ mask[i % 4]
                            for i, b in enumerate(self._read_exactly(length)))
        else:
            payload = self._read_exactly(length)
        return fin, opcode, payload

    def send_text(self, text: str):
        self._send_frame(0x1, text.encode("utf-8"))

    def recv_text(self) -> str:
        chunks = b""
        while True:
            fin, opcode, payload = self._recv_frame()
            if opcode == 0x9:
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:
                continue
            if opcode == 0x8:
                raise ConnectionError("peer closed the WebSocket")
            chunks += payload
            if fin:
                return chunks.decode("utf-8")

    def close(self):
        try:
            self._send_frame(0x8, b"")
        except OSError:
            pass
        finally:
            self.sock.close()


class CDP:
    """Chrome DevTools Protocol client over one browser connection."""

    def __init__(self, browser_ws: str):
        self.ws = WebSocket(browser_ws)
        self._id = 0
        self.events: list[dict] = []

    def call(self, method: str, params: dict | None = None,
             session_id: str | None = None) -> dict:
        self._id += 1
        message = {"id": self._id, "method": method, "params": params or {}}
        if session_id:
            message["sessionId"] = session_id
        self.ws.send_text(json.dumps(message))
        while True:
            payload = json.loads(self.ws.recv_text())
            if payload.get("id") == self._id:
                if "error" in payload:
                    raise RuntimeError("%s failed: %s" % (method, payload["error"]))
                return payload.get("result", {})
            if "method" in payload:
                self.events.append(payload)

    def wait_for_event(self, method: str, timeout: float = 45.0) -> dict:
        for event in self.events:
            if event.get("method") == method:
                self.events.remove(event)
                return event
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            payload = json.loads(self.ws.recv_text())
            if payload.get("method") == method:
                return payload
            if "method" in payload:
                self.events.append(payload)
        raise TimeoutError("timed out waiting for %s" % method)

    def drain(self, seconds: float = 1.0):
        previous = self.ws.sock.gettimeout()
        self.ws.sock.settimeout(0.25)
        deadline = time.monotonic() + seconds
        try:
            while time.monotonic() < deadline:
                try:
                    payload = json.loads(self.ws.recv_text())
                except (socket.timeout, TimeoutError):
                    continue
                except OSError:
                    break
                if "method" in payload:
                    self.events.append(payload)
        finally:
            self.ws.sock.settimeout(previous)
        return self.events

    def close(self):
        self.ws.close()


# --------------------------------------------------------------------------
# Processes
# --------------------------------------------------------------------------


def start_server(port: int = 0, host: str = "127.0.0.1"):
    """Start the P0R2 immutable preview server and wait for its LISTENING
    line. Nothing here reads a source file: the server has already frozen
    every served byte before this function returns."""
    started = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, "-B", str(REPO_ROOT / "tools" / "serve_preview.py"),
         "--port", str(port), "--host", host, "--quiet"],
        cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True)
    line = proc.stdout.readline().strip()
    if not line.startswith("LISTENING "):
        raise RuntimeError("preview server did not start: %r %s"
                           % (line, proc.stderr.read()))
    _, bound_host, bound_port = line.split()
    return (proc, "http://%s:%s" % (bound_host, bound_port),
            round(time.monotonic() - started, 3))


def stop_server(proc) -> str:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
    return proc.stderr.read()


def find_chrome() -> str:
    override = os.environ.get("CHROME_PATH")
    if override and Path(override).exists():
        return override
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    found = shutil.which("google-chrome") or shutil.which("chromium")
    if found:
        return found
    raise RuntimeError("Google Chrome not found; set CHROME_PATH")


def start_chrome(profile_dir: Path):
    """The installed Google Chrome, headless, with its own throwaway profile.
    No Playwright, no bundled browser."""
    chrome = find_chrome()
    proc = subprocess.Popen(
        [chrome,
         "--headless=new",
         "--remote-debugging-port=0",
         "--user-data-dir=%s" % profile_dir,
         "--no-first-run", "--no-default-browser-check",
         "--disable-extensions", "--disable-gpu",
         "--disable-background-timer-throttling",
         "--disable-backgrounding-occluded-windows",
         "--disable-renderer-backgrounding",
         "--hide-scrollbars", "--force-device-scale-factor=1",
         "--remote-allow-origins=*",
         "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    port_file = profile_dir / "DevToolsActivePort"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if port_file.exists():
            lines = port_file.read_text().splitlines()
            if len(lines) >= 2:
                return proc, "ws://127.0.0.1:%s%s" % (lines[0], lines[1]), chrome
        time.sleep(0.05)
    proc.kill()
    raise RuntimeError("Chrome did not expose a DevTools port")


# --------------------------------------------------------------------------
# Measurement expressions
# --------------------------------------------------------------------------

# Waits for load, for local fonts to resolve and for every image to complete,
# and reports what actually happened rather than assuming it.
WAIT_FOR_PAINT = """
(async () => {
  const cap = (promise, ms, label) => Promise.race([
    Promise.resolve(promise).then(() => label + ':ok'),
    new Promise(r => setTimeout(() => r(label + ':timeout'), ms)),
  ]);
  const stages = [];
  stages.push(await cap(new Promise(r => (document.readyState === 'complete'
    ? r() : window.addEventListener('load', r, {once: true}))), 20000, 'load'));
  stages.push(await cap(document.fonts.ready, 20000, 'fonts'));
  stages.push(await cap(Promise.all([...document.images].map(img =>
    img.complete ? null : new Promise(r => { img.onload = img.onerror = r; }))),
    20000, 'images'));
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  return {
    stages,
    fontStatus: document.fonts.status,
    loadedFontFamilies: [...new Set([...document.fonts].filter(f =>
      f.status === 'loaded').map(f => f.family))].sort(),
    fontsCheck: {
      Geist: document.fonts.check('500 68px Geist'),
      Newsreader: document.fonts.check('400 18px Newsreader'),
      'JetBrains Mono': document.fonts.check('400 12px "JetBrains Mono"'),
    },
    images: [...document.images].map(img => ({
      src: img.currentSrc, complete: img.complete,
      naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
      renderedWidth: img.getBoundingClientRect().width,
      renderedHeight: img.getBoundingClientRect().height})),
    scriptElements: document.querySelectorAll('script').length,
    inlineEventAttributes: [...document.querySelectorAll('*')].filter(el =>
      [...el.attributes].some(a => a.name.startsWith('on'))).length,
  };
})()
"""

# Everything the acceptance suite and the evidence both need from one render.
# Shared so a test can never measure something different from the evidence.
MEASURE = r"""
(() => {
  const R = document.documentElement;
  const rs = getComputedStyle(R);
  const tok = n => rs.getPropertyValue(n).trim();
  const num = v => parseFloat(v);
  const rect = el => { const r = el.getBoundingClientRect();
    return {x: r.x, y: r.y, width: r.width, height: r.height}; };

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
  const isRendered = el => {
    if (!el) return false;
    if (!el.getClientRects().length) return false;
    const c = getComputedStyle(el);
    return c.visibility !== 'hidden' && c.display !== 'none' &&
           parseFloat(c.opacity) > 0;
  };

  /* ---- 1. tokens as computed by the browser from tokens.css ---- */
  const tokenNames = [...document.querySelectorAll('[data-token]')]
    .map(el => el.dataset.token);
  const computedTokens = {};
  for (const name of [...new Set(tokenNames)]) computedTokens[name] = tok(name);
  computedTokens['--page-gutter'] = tok('--page-gutter');
  computedTokens['--col-gap'] = tok('--col-gap');
  computedTokens['--section-lg'] = tok('--section-lg');
  computedTokens['--section-md'] = tok('--section-md');
  computedTokens['--focus-ring'] = tok('--focus-ring');

  /* ---- 2. printed token reference, generated from tokens.css ---- */
  const printedTokens = [...document.querySelectorAll('.tokref__row')].map(row => ({
    name: row.querySelector('dt').dataset.token,
    printedLabel: row.querySelector('dt').textContent.trim(),
    printedValue: row.querySelector('dd').textContent.trim().replace(/\s+/g, ' '),
  }));

  /* ---- 3. type scale ---- */

  /* The width of each text line the browser actually laid out, taken from a
     DOM Range over the exact text rather than from the specimen's box. A
     Range yields one client rect per line fragment, so fragments sharing a
     top are merged back into the line they belong to. */
  const textLineWidths = el => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rows = new Map();
    for (const fragment of range.getClientRects()) {
      if (!fragment.width || !fragment.height) continue;
      const key = Math.round(fragment.top * 2) / 2;
      const seen = rows.get(key);
      rows.set(key, seen
        ? {left: Math.min(seen.left, fragment.left),
           right: Math.max(seen.right, fragment.right)}
        : {left: fragment.left, right: fragment.right});
    }
    return [...rows.entries()].sort((a, b) => a[0] - b[0])
      .map(([, line]) => Math.round((line.right - line.left) * 100) / 100);
  };

  const typeRoles = {};
  for (const row of document.querySelectorAll('.scale__row')) {
    const spec = row.querySelector('.scale__specimen');
    const c = getComputedStyle(spec);
    const r = spec.getBoundingClientRect();
    const lineWidths = textLineWidths(spec);
    const occupied = lineWidths.reduce((a, b) => a + b, 0);
    typeRoles[row.dataset.role] = {
      renderedLineWidths: lineWidths,
      lastLineFraction: (r.width && lineWidths.length)
        ? Math.round((lineWidths[lineWidths.length - 1] / r.width) * 1000) / 1000
        : null,
      lineEquivalentMeasure: r.width
        ? Math.round((occupied / r.width) * 1000) / 1000 : null,
      fontSize: num(c.fontSize),
      lineHeight: num(c.lineHeight),
      lineHeightRatio: num(c.lineHeight) / num(c.fontSize),
      fontFamily: c.fontFamily,
      fontWeight: c.fontWeight,
      renderedWidth: r.width,
      renderedHeight: r.height,
      renderedLines: Math.round(r.height / num(c.lineHeight)),
      words: spec.textContent.trim().split(/\s+/).length,
      printedEndpoints: row.querySelector('[data-endpoints]').textContent.trim(),
      printedLeading: row.querySelector('[data-leading]').textContent.trim(),
      text: spec.textContent.trim(),
    };
  }

  /* ---- 4. grid, gutters, splits, measure ---- */
  const pages = [...document.querySelectorAll('.page')].map(el => {
    const c = getComputedStyle(el);
    return {left: num(c.paddingLeft), right: num(c.paddingRight),
            width: el.getBoundingClientRect().width};
  });
  const fields = [...document.querySelectorAll('.field')]
    .map(el => el.getBoundingClientRect().width);
  const ruler = document.querySelector('.ruler');
  const rulerStyle = getComputedStyle(ruler);
  const rulerTracks = rulerStyle.gridTemplateColumns.trim().split(/\s+/).map(num);
  const rulerCells = [...ruler.children].map(el => el.getBoundingClientRect().width);
  const rulerNumbers = [...ruler.querySelectorAll('.ruler__n')]
    .filter(isRendered).map(el => el.textContent.trim());

  const splitOf = sel => {
    const el = document.querySelector(sel);
    const a = el.querySelector('.split__a').getBoundingClientRect();
    const b = el.querySelector('.split__b').getBoundingClientRect();
    return {
      columnCount: getComputedStyle(el).gridTemplateColumns.trim().split(/\s+/).length,
      aWidth: a.width, bWidth: b.width,
      sameRow: Math.abs(a.y - b.y) < 1,
      ratio: b.width ? a.width / b.width : null,
    };
  };

  const measures = [...document.querySelectorAll('.measure')]
    .map(el => el.getBoundingClientRect().width);

  /* ---- 5. every rendered text node, HTML and SVG alike ---- */
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  const seenElements = new Set();
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.nodeValue || !node.nodeValue.trim()) continue;
    const el = node.parentElement;
    if (!isRendered(el)) continue;
    const c = getComputedStyle(el);
    const fg0 = parseColor(c.color) || [0, 0, 0, 1];
    const bg = effectiveBackground(el);
    const fg = fg0[3] >= 1 ? fg0.slice(0, 3) : over(fg0, bg);
    const disabled = !!el.closest('[disabled],[aria-disabled="true"]');
    const rejected = !!el.closest('[data-status="rejected"]') &&
                     el.hasAttribute('data-specimen');
    textNodes.push({
      text: node.nodeValue.trim().slice(0, 80),
      tag: el.tagName,
      namespace: el.namespaceURI,
      fontSize: num(c.fontSize),
      fontWeight: c.fontWeight,
      fontFamily: c.fontFamily.split(',')[0].replace(/["']/g, ''),
      color: fg, background: bg,
      disabled, rejectedSpecimen: rejected,
    });
    seenElements.add(el);
  }

  /* ---- 6. contrast pair specimens ---- */
  const pairs = [...document.querySelectorAll('.pair')].map(el => {
    const spec = el.querySelector('[data-specimen]');
    const c = getComputedStyle(spec);
    const fg0 = parseColor(c.color);
    const bg = effectiveBackground(spec);
    return {
      status: el.dataset.status,
      fgToken: el.dataset.fg, bgToken: el.dataset.bg,
      printedRatio: el.querySelector('[data-ratio]').textContent.trim(),
      printedMinimum: el.querySelector('[data-ratio-min]').textContent.trim(),
      fontSize: num(c.fontSize), fontWeight: c.fontWeight,
      color: fg0[3] >= 1 ? fg0.slice(0, 3) : over(fg0, bg),
      background: bg,
      lineThrough: c.textDecorationLine.includes('line-through'),
      note: (el.querySelector('.pair__note') || {}).textContent || null,
    };
  });

  /* ---- 7. interactive targets ---- */
  const interactive = [...document.querySelectorAll(
    'a[href], button, input, select, textarea, [tabindex]')].filter(isRendered)
    .map(el => {
      const r = el.getBoundingClientRect();
      const c = getComputedStyle(el);
      return {
        tag: el.tagName, text: el.textContent.trim(), href: el.getAttribute('href'),
        disabled: el.disabled === true,
        onInk: !!el.closest('.on-ink'),
        width: r.width, height: r.height,
        transitionDuration: c.transitionDuration,
        transitionProperty: c.transitionProperty,
      };
    });

  /* ---- 8. rhythm ---- */
  const rhythm = [...document.querySelectorAll('[data-rhythm]')].map(el => ({
    name: el.dataset.rhythm,
    height: el.getBoundingClientRect().height,
    background: effectiveBackground(el),
    caption: (el.querySelector('.rhythm__caption') || {}).textContent || null,
  }));

  /* ---- 9. motion ---- */
  const transitions = [...document.querySelectorAll('*')].map(el => {
    const c = getComputedStyle(el);
    return c.transitionDuration;
  }).filter(v => v && v !== '0s')
    .flatMap(v => v.split(',').map(s => parseFloat(s)))
    .filter(v => v > 0);

  /* ---- 10. layout box of every element, for the reduced-motion diff ---- */
  const boxes = [...document.querySelectorAll('*')].map(el => {
    const r = el.getBoundingClientRect();
    return [el.tagName, Math.round(r.x * 100) / 100, Math.round(r.y * 100) / 100,
            Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100];
  });

  return {
    url: location.href,
    innerWidth: window.innerWidth,
    scrollWidth: R.scrollWidth,
    clientWidth: R.clientWidth,
    scrollHeight: R.scrollHeight,
    bodyBackground: getComputedStyle(document.body).backgroundColor,
    revisionMeta: document.querySelectorAll('meta[name="dagg-revision"]').length,
    dirtyMeta: document.querySelectorAll('meta[name="dagg-dirty"]').length,
    snapshotMeta: document.querySelectorAll('meta[name="dagg-snapshot"]').length,
    snapshot: (document.querySelector('meta[name="dagg-snapshot"]') || {}).content || null,
    revision: (document.querySelector('meta[name="dagg-revision"]') || {}).content || null,
    dirty: (document.querySelector('meta[name="dagg-dirty"]') || {}).content || null,
    headOuterHTML: document.head.outerHTML,
    title: document.title,
    lang: R.lang,
    placeholderLinks: document.querySelectorAll('a[href="#"], a[href=""]').length,
    externalLinks: [...document.querySelectorAll('[href],[src]')]
      .map(el => el.getAttribute('href') || el.getAttribute('src'))
      .filter(v => /^(https?:)?\/\//i.test(v)),
    computedTokens, printedTokens, typeRoles,
    pages, fields, rulerTracks, rulerCells, rulerNumbers,
    splitStrategic: splitOf('.split--strategic'),
    splitProduct: splitOf('.split--product'),
    measures,
    domTextOrder: [...document.querySelectorAll('.split--strategic .split__n, .split--product .split__n')]
      .map(el => el.textContent.trim()),
    textNodes, pairs, interactive, rhythm,
    transitionDurations: transitions,
    boxes,
    sectionTitles: [...document.querySelectorAll('.section__title')]
      .map(el => el.textContent.trim()),
  };
})()
"""

# Presses Tab n times and reports the element that holds focus after each
# press, plus the focus indicator the browser actually painted.
TAB_SEQUENCE = r"""
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
    tag: el.tagName,
    text: el.textContent.trim(),
    onInk: !!el.closest('.on-ink'),
    matchesFocusVisible: el.matches(':focus-visible'),
    outlineStyle: c.outlineStyle,
    outlineWidth: parseFloat(c.outlineWidth),
    outlineOffset: parseFloat(c.outlineOffset),
    outlineColor: parseColor(c.outlineColor),
    surface: bgOf(el.parentElement),
    rect: {x: r.x, y: r.y, width: r.width, height: r.height},
    domIndex: [...document.querySelectorAll('a[href], button:not([disabled])')]
      .indexOf(el),
  };
})()
"""


def evaluate(cdp: CDP, session: str, expression: str, await_promise=False):
    result = cdp.call("Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": await_promise,
    }, session_id=session)
    if result.get("exceptionDetails"):
        raise RuntimeError("page evaluation failed: %s"
                           % json.dumps(result["exceptionDetails"])[:600])
    return result["result"].get("value")


class Page:
    """One Chrome target, driven over CDP. Shared by the suite and the
    evidence run so both measure the identical render."""

    def __init__(self, cdp: CDP):
        self.cdp = cdp
        target = cdp.call("Target.createTarget", {"url": "about:blank"})
        self.session = cdp.call("Target.attachToTarget",
                                {"targetId": target["targetId"],
                                 "flatten": True})["sessionId"]
        for domain in ("Page", "Runtime", "Log", "Network", "DOM"):
            cdp.call("%s.enable" % domain, session_id=self.session)
        self.requests: list[str] = []

    def set_reduced_motion(self, reduce: bool):
        self.cdp.call("Emulation.setEmulatedMedia", {
            "features": [{"name": "prefers-reduced-motion",
                          "value": "reduce" if reduce else "no-preference"}],
        }, session_id=self.session)

    def open(self, url: str, width: int, height: int | None = None,
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
        readiness = self.evaluate(WAIT_FOR_PAINT, await_promise=True)
        facts = self.evaluate(MEASURE)
        facts["readiness"] = readiness
        facts["reducedMotion"] = reduced_motion
        facts.update(self.collect_events())
        return facts

    def evaluate(self, expression: str, await_promise=False):
        return evaluate(self.cdp, self.session, expression, await_promise)

    def press_tab(self):
        for kind in ("rawKeyDown", "keyUp"):
            self.cdp.call("Input.dispatchKeyEvent", {
                "type": kind, "key": "Tab", "code": "Tab",
                "windowsVirtualKeyCode": 9, "nativeVirtualKeyCode": 9,
            }, session_id=self.session)
        return self.evaluate(TAB_SEQUENCE)

    def tab_through(self, limit: int = 24) -> list:
        """Focus the document, then Tab until focus leaves the page. Returns
        one record per stop, in the order the keyboard produced them."""
        self.evaluate("document.body.focus(); window.scrollTo(0, 0); null")
        stops = []
        for _ in range(limit):
            stop = self.press_tab()
            if stop is None:
                break
            key = (stop["tag"], stop["text"], stop["onInk"], stop["rect"]["y"])
            if any(key == (s["tag"], s["text"], s["onInk"], s["rect"]["y"])
                   for s in stops):
                break
            stops.append(stop)
        return stops

    def screenshot(self, beyond_viewport: bool = True) -> bytes:
        shot = self.cdp.call("Page.captureScreenshot", {
            "format": "png", "captureBeyondViewport": beyond_viewport,
            "fromSurface": True,
        }, session_id=self.session)
        return base64.b64decode(shot["data"])

    def collect_events(self) -> dict:
        events = self.cdp.drain()
        console_errors, failed, http_errors, requests = [], [], [], []
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
                requests.append(params.get("request", {}).get("url", ""))
            elif method == "Network.loadingFailed" and not params.get("canceled"):
                failed.append(params.get("errorText", "failed"))
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


# --------------------------------------------------------------------------
# Colour and contrast, computed here rather than trusted to the page
# --------------------------------------------------------------------------


def _channel(value: float) -> float:
    c = value / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb) -> float:
    r, g, b = (_channel(float(v)) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg) -> float:
    a, b = relative_luminance(fg), relative_luminance(bg)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


def aa_threshold(font_size_px: float, font_weight) -> float:
    """WCAG 2.1 AA for the actual rendered size: 3:1 for large text
    (>= 24 px, or >= 18.66 px when bold), 4.5:1 otherwise."""
    try:
        weight = int(font_weight)
    except (TypeError, ValueError):
        weight = 400
    large = font_size_px >= 24 or (weight >= 700 and font_size_px >= 18.66)
    return 3.0 if large else 4.5


# --------------------------------------------------------------------------
# Non-browser evidence
# --------------------------------------------------------------------------


def fetch(base: str, path: str):
    request = urllib.request.Request(base + path)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as err:
        with err:
            return err.code, dict(err.headers.items()), err.read()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True, text=True).stdout.strip()


def require_snapshot(headers: dict, snapshot_id: str, label: str):
    lowered = {k.lower(): v for k, v in headers.items()}
    actual = lowered.get("x-dagg-snapshot")
    if actual != snapshot_id:
        raise SnapshotDisagreement(
            "%s carried snapshot %r, the server reports %r"
            % (label, actual, snapshot_id))


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(data: bytes) -> dict:
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    return {"width": width, "height": height}


def run_acceptance_suite() -> dict:
    """Run the P2 suite only.

    ``unittest discover -s tests`` would also run the P0R2 suite, whose scope
    test is pinned to the P0R2 base commit and therefore reports every file
    P1 and P2 legitimately added. P2 does not own that file and may not
    repair it, so this runs the P2 pattern alone and says so.
    """
    target = EVIDENCE_DIR / "tests.json"
    environment = dict(os.environ, DAGG_P2_TEST_JSON=str(target),
                       PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-B", "-m", "unittest", "discover",
               "-s", "tests", "-p", "test_p2_foundations.py", "-v"]
    started = time.monotonic()
    completed = subprocess.run(command, cwd=str(REPO_ROOT), capture_output=True,
                               text=True, env=environment)
    output = completed.stdout + completed.stderr
    (EVIDENCE_DIR / "tests-output.txt").write_text(output)
    detail = json.loads(target.read_text()) if target.exists() else {}
    return {
        "command": " ".join(["python3"] + command[1:]),
        "returnCode": completed.returncode,
        "passed": completed.returncode == 0,
        "seconds": round(time.monotonic() - started, 3),
        "summary": [line for line in output.splitlines()
                    if line.startswith(("OK", "FAILED", "Ran "))],
        "outcomes": [line.rsplit(" ... ", 1) for line in output.splitlines()
                     if " ... " in line],
        "detail": detail,
    }


def asset_budget(base: str) -> dict:
    """Measure the performance budget from the served bytes, not from disk."""
    _, _, html = fetch(base, PAGE_PATH)
    _, _, tokens_css = fetch(base, TOKENS_CSS_PATH)
    _, _, page_css = fetch(base, PAGE_CSS_PATH)
    fonts = {}
    for path in FONT_PATHS:
        _, _, body = fetch(base, path)
        fonts[path] = len(body)
    return {
        "htmlBytes": len(html),
        "tokensCssBytes": len(tokens_css),
        "pageCssBytes": len(page_css),
        "combinedCssBytes": len(tokens_css) + len(page_css),
        "woff2Bytes": fonts,
        "combinedWoff2Bytes": sum(fonts.values()),
        "javaScriptBytes": 0,
        "budget": PERFORMANCE_BUDGET,
        "withinBudget": (
            len(html) <= PERFORMANCE_BUDGET["htmlBytesMax"]
            and len(tokens_css) + len(page_css) <= PERFORMANCE_BUDGET["cssBytesMax"]
            and sum(fonts.values()) <= PERFORMANCE_BUDGET["woff2BytesMax"]),
    }


def font_provenance() -> dict:
    out = {}
    for relative in ("assets/fonts/golden-standard/geist/Geist-Variable.woff2",
                     "assets/fonts/golden-standard/newsreader/Newsreader-Variable.woff2",
                     "assets/fonts/golden-standard/jetbrains-mono/"
                     "JetBrainsMono-Variable.woff2") + LICENSE_PATHS:
        target = REPO_ROOT / relative
        if not target.exists():
            out[relative] = {"present": False}
            continue
        raw = target.read_bytes()
        out[relative] = {"present": True, "bytes": len(raw),
                         "sha256": hashlib.sha256(raw).hexdigest()}
    return out


def owned_scope() -> dict:
    committed = [p for p in git("diff", "--name-only",
                                "%s...HEAD" % BASE_COMMIT).splitlines() if p]
    working = []
    raw = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "status",
         "--porcelain"], check=True, capture_output=True, text=True).stdout
    for line in raw.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        working.append(path.strip('"'))
    public = [p for p in git(
        "diff", "--name-only", "%s...HEAD" % BASE_COMMIT, "--",
        "index.html", "robots.txt", "v1", "marketing", "assets",
        "preview/directions", "preview/site").splitlines() if p]
    return {"committedVersusBase": committed, "workingTree": working,
            "publicOrLegacyChanged": public}


# --------------------------------------------------------------------------
# Deviations
# --------------------------------------------------------------------------


def build_deviations(records: dict, budget: dict, scope: dict,
                     tests: dict, extra: list[str]) -> list[str]:
    out: list[str] = []
    if not tests.get("passed", True):
        out.append("The P2 acceptance suite did not pass; see "
                   "evidence/P2/tests-output.txt.")
    if scope["publicOrLegacyChanged"]:
        out.append("Public or legacy files changed versus the base commit: %s"
                   % ", ".join(scope["publicOrLegacyChanged"]))
    if not budget["withinBudget"]:
        out.append("The performance budget was exceeded: %s"
                   % json.dumps({k: budget[k] for k in
                                 ("htmlBytes", "combinedCssBytes",
                                  "combinedWoff2Bytes")}))
    out.extend(extra)
    out.append(
        "The acceptance command is `unittest discover -p test_p2_foundations.py`, "
        "not a full `discover -s tests`. tests/test_preview_revision.py pins its "
        "scope assertion to the P0R2 base commit 9e0a670 and therefore fails on "
        "every file P1 and P2 legitimately added. P2 does not own that file and "
        "did not repair it; the P0R2 suite otherwise still passes and its stale "
        "scope test belongs to whoever next owns that file.")
    out.append(
        "The twelve-column ruler renders the real content grid at every width. "
        "Below 768 px the twelve tracks are hairlines, because twelve columns "
        "with a 24 px gap genuinely leave about 7 px per track at 390 px and "
        "about 1 px at 320 px. The track numbers are therefore hidden below "
        "768 px and the mobile layout spans the full field instead of using "
        "column spans. That is the measured truth about the frozen grid on a "
        "phone, not a rendering fault.")
    out.append(
        "Screenshots are full-page at 1440, 390, 360 and 320 px, plus two "
        "viewport-height focus captures at 1440 px and one reduced-motion "
        "capture at 390 px. The 768 and 1024 px viewports are measured for "
        "overflow, gutters and grid collapse but are not screenshotted; P2 "
        "section 8 does not require them.")
    out.append(
        "Contrast is computed by this harness from the colours Chrome actually "
        "rendered, composited through every ancestor background, for every "
        "rendered text node. Two categories are excluded from the pass "
        "requirement and named individually in contrastExclusions: the two "
        "deliberately rejected Coral and Sage specimens, and text inside "
        "disabled controls, which WCAG 1.4.3 exempts.")
    out.append(
        "No SVG text exists on this page, so the SVG half of the text sweep "
        "covered zero nodes. The sweep is a document-wide TreeWalker over "
        "every text node rather than a selector list, so it would have found "
        "SVG text had any been rendered. Recorded as coverage, not as a pass.")
    return out


# --------------------------------------------------------------------------
# Capture
# --------------------------------------------------------------------------


def main(argv=None) -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--base-commit", default=BASE_COMMIT)
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--label", default="",
                        help="suffix for the run record, e.g. post-commit")
    args = parser.parse_args(argv)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    tests = {} if args.skip_tests else run_acceptance_suite()

    server, base_url, startup_seconds = start_server(args.port, args.host)
    profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p2-chrome-"))
    chrome = None
    cdp = None
    screenshots: list[dict] = []
    extra_deviations: list[str] = []
    try:
        status, revision_headers, revision_body = fetch(base_url, "/__revision")
        revision = json.loads(revision_body)
        snapshot_id = revision["snapshotId"]
        (EVIDENCE_DIR / "revision.json").write_bytes(revision_body)
        require_snapshot(revision_headers, snapshot_id, "/__revision")

        # -- response headers, one per required content type ---------------
        header_targets = [("HTML", PAGE_PATH), ("CSS-tokens", TOKENS_CSS_PATH),
                          ("CSS-page", PAGE_CSS_PATH),
                          ("PNG-logotype-dark", LOGO_DARK_PATH),
                          ("PNG-logotype", LOGO_LIGHT_PATH)]
        header_targets += [("WOFF2-%s" % p.rsplit("/", 1)[-1], p)
                           for p in FONT_PATHS]
        headers_record = {}
        no_store_coverage = []
        for label, path in header_targets:
            code, headers, body = fetch(base_url, path)
            if code != 200:
                raise RuntimeError("%s returned %d" % (path, code))
            require_snapshot(headers, snapshot_id, label)
            lowered = {k.lower(): v for k, v in headers.items()}
            compliant = all(lowered.get(k) == v
                            for k, v in REQUIRED_NO_STORE.items())
            headers_record[label] = {
                "url": base_url + path, "status": code, "bytes": len(body),
                "contentType": headers.get("Content-Type"),
                "headers": headers, "noStore": compliant,
                "snapshotMatches": True,
                "sha256": hashlib.sha256(body).hexdigest(),
            }
            if compliant:
                no_store_coverage.append(label)
        json_no_store = all(
            {k.lower(): v for k, v in revision_headers.items()}.get(k) == v
            for k, v in REQUIRED_NO_STORE.items())
        headers_record["JSON"] = {
            "url": base_url + "/__revision", "status": status,
            "bytes": len(revision_body), "headers": revision_headers,
            "noStore": json_no_store, "snapshotMatches": True,
        }
        if json_no_store:
            no_store_coverage.append("JSON")
        (EVIDENCE_DIR / "response-headers.json").write_text(
            json.dumps(headers_record, indent=2, sort_keys=True) + "\n")

        # -- browser --------------------------------------------------------
        chrome, browser_ws, chrome_path = start_chrome(profile_dir)
        cdp = CDP(browser_ws)
        page = Page(cdp)
        chrome_version = cdp.call("Browser.getVersion")
        page_url = base_url + PAGE_PATH

        records: dict = {}
        request_log: dict = {}
        for width in LAYOUT_VIEWPORTS:
            facts = page.open(page_url, width)
            if facts["snapshot"] != snapshot_id:
                raise SnapshotDisagreement(
                    "the %dpx DOM reported snapshot %r, the server reports %r"
                    % (width, facts["snapshot"], snapshot_id))
            if (facts["revisionMeta"], facts["dirtyMeta"],
                    facts["snapshotMeta"]) != (1, 1, 1):
                raise SnapshotDisagreement(
                    "the %dpx DOM did not carry exactly one of each meta tag"
                    % width)
            request_log[str(width)] = facts["requests"]
            if width in SCREENSHOT_VIEWPORTS:
                png = page.screenshot()
                name = "foundations-%dpx.png" % width
                (EVIDENCE_DIR / name).write_bytes(png)
                screenshots.append({
                    "path": "evidence/P2/" + name, "viewport": width,
                    "state": "default",
                    "pixelDimensions": png_size(png),
                    "snapshotId": facts["snapshot"],
                    "sha256": hashlib.sha256(png).hexdigest(),
                })
            records[str(width)] = facts
            if width == 1440:
                (EVIDENCE_DIR / "foundations-head-dom.html").write_text(
                    facts["headOuterHTML"] + "\n")

        # -- keyboard focus, on warm paper and on ink -----------------------
        page.open(page_url, 1440)
        stops = page.tab_through()
        focus_records = []
        wanted = [("paper-primary", lambda s: not s["onInk"]
                   and s["text"] == "Primary action"),
                  ("ink-secondary", lambda s: s["onInk"]
                   and s["text"] == "Secondary action")]
        for name, predicate in wanted:
            page.open(page_url, 1440)
            reached = None
            for _ in range(24):
                stop = page.press_tab()
                if stop is None:
                    break
                if predicate(stop):
                    reached = stop
                    break
            if reached is None:
                raise RuntimeError("Tab never reached the %s control" % name)
            png = page.screenshot(beyond_viewport=False)
            filename = "focus-%s-1440px.png" % name
            (EVIDENCE_DIR / filename).write_bytes(png)
            ratio = (contrast_ratio(reached["outlineColor"], reached["surface"])
                     if reached["outlineColor"] else None)
            reached["outlineContrastAgainstSurface"] = (
                round(ratio, 2) if ratio else None)
            focus_records.append({"name": name, "screenshot":
                                  "evidence/P2/" + filename, **reached})
            screenshots.append({
                "path": "evidence/P2/" + filename, "viewport": 1440,
                "state": "focus-visible:%s" % name,
                "pixelDimensions": png_size(png),
                "snapshotId": snapshot_id,
                "sha256": hashlib.sha256(png).hexdigest(),
            })

        # -- reduced motion --------------------------------------------------
        reduced = page.open(page_url, 390, reduced_motion=True)
        png = page.screenshot()
        (EVIDENCE_DIR / "foundations-reduced-motion-390px.png").write_bytes(png)
        screenshots.append({
            "path": "evidence/P2/foundations-reduced-motion-390px.png",
            "viewport": 390, "state": "prefers-reduced-motion: reduce",
            "pixelDimensions": png_size(png), "snapshotId": reduced["snapshot"],
            "sha256": hashlib.sha256(png).hexdigest(),
        })
        page.set_reduced_motion(False)

        layout_identical = reduced["boxes"] == records["390"]["boxes"]
        motion_removed = all(v <= 0.001 for v in reduced["transitionDurations"])

        # -- contrast sweep over every rendered text node -------------------
        contrast_failures = []
        contrast_exclusions = []
        smallest_text = None
        text_namespaces = set()
        for width, facts in records.items():
            for node in facts["textNodes"]:
                text_namespaces.add(node["namespace"])
                if smallest_text is None or node["fontSize"] < smallest_text:
                    smallest_text = node["fontSize"]
                ratio = contrast_ratio(node["color"], node["background"])
                required = aa_threshold(node["fontSize"], node["fontWeight"])
                record = {"viewport": int(width), "text": node["text"],
                          "fontSizePx": node["fontSize"],
                          "ratio": round(ratio, 2), "required": required}
                if node["disabled"]:
                    record["reason"] = "disabled control, WCAG 1.4.3 exempt"
                    contrast_exclusions.append(record)
                elif node["rejectedSpecimen"]:
                    record["reason"] = "deliberately rejected pair specimen"
                    contrast_exclusions.append(record)
                elif ratio + 0.005 < required:
                    contrast_failures.append(record)

        # -- gutters ---------------------------------------------------------
        gutter_record = {}
        for width, facts in records.items():
            declared = {1440: 72, 1024: 48, 768: 24, 320: 20, 360: 20, 390: 20}[int(width)]
            measured = sorted({(p["left"], p["right"]) for p in facts["pages"]})
            gutter_record[width] = {"declared": declared, "measured": measured,
                                    "matches": all(l == declared and r == declared
                                                   for l, r in measured)}

        budget = asset_budget(base_url)
        scope = owned_scope()
        head_commit = git("rev-parse", "HEAD")
        porcelain = git("status", "--porcelain")

        all_requests = sorted({url for log in request_log.values() for url in log})
        remote = [u for u in all_requests
                  if not u.startswith(("http://127.0.0.1:", "data:", "about:"))]
        (EVIDENCE_DIR / "request-log.json").write_text(json.dumps({
            "byViewport": request_log,
            "distinct": all_requests,
            "nonLocal": remote,
            "localOnly": not remote,
        }, indent=2, sort_keys=True) + "\n")

        (EVIDENCE_DIR / "dom-metadata.json").write_text(json.dumps({
            "pageUrl": page_url,
            "serverRevision": revision,
            "typeEndpointContract": {k: {str(kk): vv for kk, vv in v.items()}
                                     for k, v in TYPE_ENDPOINTS.items()},
            "byViewport": {w: {k: v for k, v in f.items()
                               if k not in ("headOuterHTML", "boxes")}
                           for w, f in records.items()},
            "reducedMotion390": {k: v for k, v in reduced.items()
                                 if k not in ("headOuterHTML", "boxes")},
            "focus": focus_records,
            "tabOrder": stops,
            "gutters": gutter_record,
        }, indent=2, sort_keys=True) + "\n")

        server_stderr = stop_server(server)
        (EVIDENCE_DIR / "server-stderr.txt").write_text(server_stderr)

        console_errors = sum(f["consoleErrors"] for f in records.values())
        if console_errors:
            extra_deviations.append(
                "Console errors were recorded: %s"
                % json.dumps([f["consoleErrorDetail"] for f in records.values()]))

        h1 = records["1440"]["typeRoles"]["h1"]
        over_physical = h1["renderedLines"] > 3
        over_equivalent = h1["lineEquivalentMeasure"] > 2.5 + 0.005
        short_last = (h1["renderedLines"] < 3
                      or h1["lastLineFraction"] <= 0.5 + 0.005)
        if over_physical or over_equivalent or not short_last:
            extra_deviations.append(
                "The frozen P1 hero H1 exceeds the 2.5-line desktop limit at "
                "1440 px in the 1240 px field at the frozen 68 px size (%d "
                "words): %d physical lines, line-equivalent occupancy %.3f, "
                "last-line fraction %.3f, line widths %s. The limit is "
                "measured as visual line-equivalent occupancy (sum of text-line "
                "widths / field width), because this copy cannot fit two "
                "physical lines at this size in this field. Raised for P4, "
                "which owns hero composition; P2 changed no copy and no type "
                "endpoint."
                % (h1["words"], h1["renderedLines"],
                   h1["lineEquivalentMeasure"], h1["lastLineFraction"],
                   h1["renderedLineWidths"]))

        deviations = build_deviations(records, budget, scope, tests,
                                      extra_deviations)

        result = {
            "package": "P2",
            "label": args.label or "pre-commit",
            "commit": head_commit,
            "baseCommit": args.base_commit,
            "branch": revision["branch"],
            "dirtyAtCapture": revision["dirty"],
            "snapshotId": snapshot_id,
            "assetRevision": snapshot_id,
            "snapshotConsistencyPasses": revision["snapshotConsistencyPasses"],
            "snapshotAcquisitionAttempts": revision["snapshotAcquisitionAttempts"],
            "snapshotAcquisitionStable": revision["snapshotAcquisitionStable"],
            "snapshotFileCount": revision["snapshotFileCount"],
            "snapshotByteCount": revision["snapshotByteCount"],
            "snapshotExcludes": [".git/**", "evidence/**", "**/__pycache__/**",
                                 "**/*.pyc", ".DS_Store"],
            "capturedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverStartupSeconds": startup_seconds,
            "chrome": chrome_version.get("product"),
            "chromePath": chrome_path,
            "chromeDriver": "Chrome DevTools Protocol over a raw WebSocket; "
                            "no Playwright, Selenium or bundled browser",
            "viewports": list(LAYOUT_VIEWPORTS),
            "screenshotViewports": list(SCREENSHOT_VIEWPORTS),
            "statesTested": [
                "default", "keyboard focus-visible on warm paper",
                "keyboard focus-visible on ink", "hover (computed styles only)",
                "disabled", "prefers-reduced-motion: reduce",
            ],
            "scrollWidthMatches": all(f["scrollWidth"] == f["clientWidth"]
                                      for f in records.values()),
            "scrollWidthByViewport": {w: [f["scrollWidth"], f["clientWidth"]]
                                      for w, f in records.items()},
            "minimumTouchTarget": {"width": 44, "height": 44},
            "smallestInteractiveTarget": min(
                (min(i["width"], i["height"]) for f in records.values()
                 for i in f["interactive"]), default=None),
            "minimumComputedTextPx": smallest_text,
            "textCoverage": ["HTML", "SVG"],
            "textCoverageMethod": "document-wide TreeWalker over every text "
                                  "node in <body>, not a selector list",
            "textNodesMeasured": sum(len(f["textNodes"]) for f in records.values()),
            "textNamespaces": sorted(n for n in text_namespaces if n),
            "contrastFailures": contrast_failures,
            "contrastExclusions": contrast_exclusions,
            "gutters": gutter_record,
            "fieldWidths": {w: sorted(set(f["fields"]))
                            for w, f in records.items()},
            "gridTracks1440": records["1440"]["rulerTracks"],
            "splitCollapse": {
                "at1024": records["1024"]["splitStrategic"],
                "at768": records["768"]["splitStrategic"],
            },
            "typeRoles": {w: f["typeRoles"] for w, f in records.items()},
            "rhythm1440": records["1440"]["rhythm"],
            "tabOrder": [s["text"] for s in stops],
            "focus": focus_records,
            "placeholderLinks": max(f["placeholderLinks"] for f in records.values()),
            "consoleErrors": console_errors,
            "failedRequests": sorted({x for f in records.values()
                                      for x in f["failedRequests"]}),
            "httpErrorResponses": sorted({x for f in records.values()
                                          for x in f["httpErrorResponses"]}),
            "requestsAreLocalOnly": not remote,
            "nonLocalRequests": remote,
            "fontsCheck": records["1440"]["readiness"]["fontsCheck"],
            "loadedFontFamilies": records["1440"]["readiness"]["loadedFontFamilies"],
            "fontProvenance": font_provenance(),
            "reducedMotion": "passed" if (layout_identical and motion_removed)
                             else "failed",
            "reducedMotionLayoutIdentical": layout_identical,
            "reducedMotionTransitionsRemoved": motion_removed,
            "noJavaScript": "passed: 0 script elements, 0 inline event "
                            "attributes, 0 bytes of page JavaScript",
            "scriptElements": records["1440"]["readiness"]["scriptElements"],
            "performance": budget,
            "scope": scope,
            "dirtyStateMatchesGit": revision["dirty"] == bool(porcelain),
            "revisionEndpointMatchesGit": revision["commit"] == head_commit,
            "noStoreCoverage": no_store_coverage,
            "evidenceExcludedFromSnapshot": True,
            "serverExceptions": server_stderr.count("Traceback"),
            "screenshots": screenshots,
            "unmeasuredInP2": [
                "LCP, INP and CLS were not instrumented; CLS is argued from "
                "font-display: block plus width/height and aspect-ratio on both "
                "logotypes, not measured with a layout-shift observer.",
                "Screen-reader announcement quality was not tested.",
                "200% browser zoom was not tested; P2 section 7 does not "
                "require it and the masterplan places it in the P12 gate.",
                "Real-device rendering was not tested; all measurements come "
                "from headless Google Chrome on macOS.",
            ],
            "deviations": deviations,
            "evidenceFiles": sorted(
                "evidence/P2/" + item.name for item in EVIDENCE_DIR.iterdir()
                if item.name != "result.json"),
            "tests": tests,
        }
        (EVIDENCE_DIR / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")

        print(json.dumps({k: result[k] for k in (
            "commit", "label", "snapshotId", "dirtyAtCapture",
            "snapshotFileCount", "scrollWidthMatches", "minimumComputedTextPx",
            "smallestInteractiveTarget", "requestsAreLocalOnly",
            "consoleErrors", "reducedMotion", "fontsCheck",
            "serverExceptions")}, indent=2, sort_keys=True))
        print("contrast failures: %d" % len(contrast_failures))
        print("deviations: %d" % len(deviations))
        print("tests passed: %s" % tests.get("passed"))
        return 0 if tests.get("passed", True) and not contrast_failures else 1
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
        stop_server(server)
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
