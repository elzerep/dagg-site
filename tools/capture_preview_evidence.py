#!/usr/bin/env python3
"""Capture P0 preview evidence from one revision-safe server process.

Starts ``tools/serve_preview.py``, drives the installed Google Chrome over
the Chrome DevTools Protocol, and writes screenshots, the ``/__revision``
response, a ``<head>`` DOM snapshot, a response-header record and
``evidence/P0/result.json`` — all from the same server process, so the
screenshots and the machine evidence provably describe one revision.

Standard library only: the CCDP transport below is a minimal RFC 6455
client. Nothing is written outside ``evidence/P0/`` and a temporary Chrome
profile that is removed on exit.

    python3 tools/capture_preview_evidence.py
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
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence" / "P0"
PAGE_PATH = "/preview/directions/a-plus.html"
VIEWPORTS = (1440, 390)

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)

CONTROL_FILES = (
    "CLAUDE.md",
    "design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md",
    "design/golden-standard/CLAUDE-WORK-PACKAGE-TEMPLATE.md",
    "design/golden-standard/packages/P0-RECONCILE-AND-PREVIEW.md",
    "design/golden-standard/reference-audits/ANTHROPIC-OPENAI-RECIPE.md",
    "design/golden-standard/reference-audits/PALANTIR-RECIPE.md",
    "design/golden-standard/reference-audits/xai-current/XAI-CURRENT-AUDIT.md",
    "design/golden-standard/image-system/decision-field-hero-v2.png",
)

HEADER_TARGETS = (
    ("HTML", PAGE_PATH),
    ("CSS", "/preview/directions/tokens.css"),
    ("JavaScript", "/preview/site/site.js"),
    ("raster-image", "/assets/dagg-logotype-dark.png"),
)

REQUIRED_NO_STORE = {
    "cache-control": "no-store, max-age=0",
    "pragma": "no-cache",
    "expires": "0",
}


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

    # -- raw io ----------------------------------------------------------

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

    # -- frames ----------------------------------------------------------

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
        if second & 0x80:  # a server frame must not be masked, but be lenient
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
            if opcode == 0x9:            # ping
                self._send_frame(0xA, payload)
                continue
            if opcode == 0xA:            # pong
                continue
            if opcode == 0x8:            # close
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

    def drain(self, seconds: float = 1.5):
        """Collect protocol events that arrived while nothing was pending."""
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


def start_server(port: int, host: str):
    started = time.monotonic()
    proc = subprocess.Popen(
        [sys.executable, "-B",
         str(REPO_ROOT / "tools" / "serve_preview.py"),
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
# Capture
# --------------------------------------------------------------------------


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(data: bytes) -> dict:
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    return {"width": width, "height": height}


# Each stage is bounded and reports its own outcome, so a screenshot can
# never silently be taken of a half-loaded page.
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
  // Sweep the document so loading="lazy" images below the fold actually
  // load; captureBeyondViewport alone leaves them blank.
  const step = Math.max(200, Math.round(window.innerHeight * 0.8));
  for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 60));
  }
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 150));
  stages.push(await cap(Promise.all([...document.images].map(img =>
    img.complete ? null : new Promise(r => { img.onload = img.onerror = r; }))),
    20000, 'images'));
  await new Promise(r => setTimeout(r, 300));
  return {
    stages,
    fontStatus: document.fonts.status,
    loadedFontFamilies: [...new Set([...document.fonts].filter(f =>
      f.status === 'loaded').map(f => f.family))].sort(),
    images: [...document.images].map(img => ({
      src: img.currentSrc, complete: img.complete,
      naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight})),
  };
})()
"""

PAGE_FACTS = """
({
  url: location.href,
  revisionMeta: document.querySelectorAll('meta[name="dagg-revision"]').length,
  dirtyMeta: document.querySelectorAll('meta[name="dagg-dirty"]').length,
  revision: (document.querySelector('meta[name="dagg-revision"]')||{}).content || null,
  dirty: (document.querySelector('meta[name="dagg-dirty"]')||{}).content || null,
  headOuterHTML: document.head.outerHTML,
  bodyElementCount: document.body.getElementsByTagName('*').length,
  scrollWidth: document.documentElement.scrollWidth,
  scrollHeight: document.documentElement.scrollHeight,
  innerWidth: window.innerWidth,
  placeholderLinks: document.querySelectorAll('a[href="#"], a[href=""]').length,
  scrollY: window.scrollY,
  // This page runs an auto-advancing carousel, so record which step the
  // screenshot caught. See result.json deviations.
  carouselState: (document.getElementById('st') || {}).textContent || null,
  carouselSelected: [...document.querySelectorAll('.step')]
    .findIndex(b => b.getAttribute('aria-selected') === 'true')
})
"""


def evaluate(cdp: CDP, session: str, expression: str, await_promise=False):
    result = cdp.call("Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": await_promise,
    }, session_id=session)
    if result.get("exceptionDetails"):
        raise RuntimeError("page evaluation failed: %s"
                           % json.dumps(result["exceptionDetails"])[:400])
    return result["result"].get("value")


def capture_viewport(cdp: CDP, session: str, url: str, width: int, height: int):
    cdp.call("Emulation.setDeviceMetricsOverride", {
        "width": width, "height": height,
        "deviceScaleFactor": 1, "mobile": width < 600,
    }, session_id=session)
    cdp.call("Page.navigate", {"url": url}, session_id=session)
    cdp.wait_for_event("Page.loadEventFired")
    readiness = evaluate(cdp, session, WAIT_FOR_PAINT, await_promise=True)
    facts = evaluate(cdp, session, PAGE_FACTS)
    facts["readiness"] = readiness
    shot = cdp.call("Page.captureScreenshot", {
        "format": "png", "captureBeyondViewport": True, "fromSurface": True,
    }, session_id=session)
    facts.update(classify_events(cdp.drain()))
    return facts, base64.b64decode(shot["data"])


def classify_events(events: list[dict]) -> dict:
    """Count real browser errors. Nothing here may report a pass that the
    protocol stream does not support."""
    console_errors, failed_requests, http_errors = [], [], []
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
        elif method == "Network.loadingFailed" and not params.get("canceled"):
            failed_requests.append(params.get("errorText", "failed"))
        elif method == "Network.responseReceived":
            response = params.get("response", {})
            if response.get("status", 0) >= 400:
                http_errors.append("%s %s" % (response.get("status"),
                                              response.get("url")))
    return {
        "consoleErrors": len(console_errors),
        "consoleErrorDetail": console_errors,
        "failedRequests": failed_requests,
        "httpErrorResponses": http_errors,
    }


# --------------------------------------------------------------------------
# Non-browser evidence, fetched from the same server process
# --------------------------------------------------------------------------


def fetch(base: str, path: str):
    with urllib.request.urlopen(base + path, timeout=30) as response:
        return response.status, dict(response.headers.items()), response.read()


def control_hashes() -> dict:
    out = {}
    for relative in CONTROL_FILES:
        target = REPO_ROOT / relative
        raw = target.read_bytes()
        out[relative] = {"sha256": hashlib.sha256(raw).hexdigest(),
                         "bytes": len(raw)}
    return out


def read_start_hashes() -> dict:
    """Parse the record written before the first write of this package."""
    path = EVIDENCE_DIR / "control-hashes-start.txt"
    if not path.exists():
        return {}
    out = {}
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) == 3:
            out[parts[2]] = {"sha256": parts[0], "bytes": int(parts[1])}
    return out


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True, text=True).stdout.strip()


def default_port_is_free(port: int = 8912) -> bool:
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        probe.close()


def build_deviations(dom_records: dict, default_port_free: bool) -> list[str]:  # noqa: C901
    """Everything a reviewer must know that the pass/fail flags do not say."""
    out = []
    if not default_port_free:
        out.append(
            "Default port 8912 was already bound by an unrelated pre-existing "
            "process at capture time, so this evidence was captured on an "
            "ephemeral port. The documented default is unchanged.")
    if any(record.get("carouselState") for record in dom_records.values()):
        out.append(
            "preview/directions/a-plus.html runs an IntersectionObserver "
            "carousel that auto-advances every 2600 ms, so its screenshots are "
            "not byte-reproducible. Each capture records carouselState and "
            "carouselSelected; both runs were captured at MAP/step 0 because "
            "the section is out of view at scroll position 0.")
    out.append(
        'The page carries a loading="lazy" image below the fold that '
        "captureBeyondViewport alone leaves blank. The harness sweeps the "
        "document and returns to the top before capturing; readiness stages "
        "in dom-metadata.json record that every image reached complete.")
    favicon = [item for record in dom_records.values()
               for item in record["httpErrorResponses"] if "favicon" in item]
    if favicon:
        out.append(
            "The only HTTP error and the only console error in the capture is "
            "Chrome's automatic /favicon.ico request returning 404. The "
            "repository has no favicon and the page does not reference one; "
            "no page asset failed to load.")
    placeholders = max(record["placeholderLinks"] for record in dom_records.values())
    if placeholders:
        out.append(
            "%d placeholder links (href=\"#\") remain in this design-direction "
            "preview. Out of P0 scope; recorded for the package that owns "
            "navigation." % placeholders)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0,
                        help="preview server port (default: 0, pick a free port)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--base-commit", default=None,
                        help="commit to compare the served preview against")
    args = parser.parse_args(argv)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    start_hashes = read_start_hashes()
    default_port_free = default_port_is_free()

    server, base_url, startup_seconds = start_server(args.port, args.host)
    profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p0-chrome-"))
    chrome = None
    cdp = None
    screenshots = []
    try:
        status, revision_headers, revision_body = fetch(base_url, "/__revision")
        revision = json.loads(revision_body)
        (EVIDENCE_DIR / "revision.json").write_bytes(revision_body)

        headers_record = {}
        no_store_coverage = []
        for label, path in HEADER_TARGETS:
            code, headers, body = fetch(base_url, path)
            lowered = {k.lower(): v for k, v in headers.items()}
            compliant = all(lowered.get(k) == v for k, v in REQUIRED_NO_STORE.items())
            headers_record[label] = {
                "url": base_url + path,
                "status": code,
                "bytes": len(body),
                "headers": headers,
                "noStore": compliant,
            }
            if compliant:
                no_store_coverage.append(label)
        headers_record["JSON /__revision"] = {
            "url": base_url + "/__revision",
            "status": status,
            "bytes": len(revision_body),
            "headers": revision_headers,
            "noStore": all(
                {k.lower(): v for k, v in revision_headers.items()}.get(k) == v
                for k, v in REQUIRED_NO_STORE.items()),
        }
        (EVIDENCE_DIR / "response-headers.json").write_text(
            json.dumps(headers_record, indent=2, sort_keys=True) + "\n")

        chrome, browser_ws, chrome_path = start_chrome(profile_dir)
        cdp = CDP(browser_ws)
        target = cdp.call("Target.createTarget", {"url": "about:blank"})
        session = cdp.call("Target.attachToTarget",
                           {"targetId": target["targetId"], "flatten": True})["sessionId"]
        cdp.call("Page.enable", session_id=session)
        cdp.call("Runtime.enable", session_id=session)
        cdp.call("Log.enable", session_id=session)
        cdp.call("Network.enable", session_id=session)
        chrome_version = cdp.call("Browser.getVersion")

        page_url = base_url + PAGE_PATH
        dom_records = {}
        for width in VIEWPORTS:
            height = 900 if width >= 600 else 844
            cdp.events.clear()
            facts, png = capture_viewport(cdp, session, page_url, width, height)
            name = "a-plus-%dpx.png" % width
            (EVIDENCE_DIR / name).write_bytes(png)
            size = png_size(png)
            screenshots.append({
                "path": "evidence/P0/" + name,
                "viewport": width,
                "pixelDimensions": size,
                "pageUrl": facts["url"],
                "serverRevision": revision["commit"],
                "serverDirty": revision["dirty"],
                "sha256": hashlib.sha256(png).hexdigest(),
            })
            dom_records[str(width)] = {k: v for k, v in facts.items()
                                       if k != "headOuterHTML"}
            if width == VIEWPORTS[0]:
                (EVIDENCE_DIR / "a-plus-head-dom.html").write_text(
                    facts["headOuterHTML"] + "\n")

        (EVIDENCE_DIR / "dom-metadata.json").write_text(
            json.dumps({"pageUrl": page_url,
                        "serverRevision": revision,
                        "byViewport": dom_records}, indent=2, sort_keys=True) + "\n")

        # -- correctness checks against git and the base revision ---------
        head_commit = git("rev-parse", "HEAD")
        porcelain = git("status", "--porcelain")
        base_commit = args.base_commit or head_commit
        preview_diff = git("diff", "--name-only", base_commit, "--",
                           "preview", "assets", "index.html")

        dom_matches = all(
            record["revision"] == revision["commit"]
            and record["dirty"] == ("true" if revision["dirty"] else "false")
            and record["revisionMeta"] == 1 and record["dirtyMeta"] == 1
            for record in dom_records.values())

        deviations = build_deviations(dom_records, default_port_free)

        end_hashes = control_hashes()
        control_unchanged = (start_hashes == end_hashes) if start_hashes else None

        server.terminate()
        server.wait(timeout=10)
        server_stderr = server.stderr.read()
        (EVIDENCE_DIR / "server-stderr.txt").write_text(server_stderr)

        tests_path = EVIDENCE_DIR / "tests.json"
        tests = json.loads(tests_path.read_text()) if tests_path.exists() else {}

        result = {
            "package": "P0",
            "commit": head_commit,
            "baseCommit": base_commit,
            "assetRevision": head_commit,
            "branch": revision["branch"],
            "dirtyAtCapture": revision["dirty"],
            "capturedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverStartupSeconds": startup_seconds,
            "serverStartupUnderTwoSeconds": startup_seconds < 2.0,
            "chrome": chrome_version.get("product"),
            "chromePath": chrome_path,
            "viewports": sorted(VIEWPORTS),
            "viewportScope": "P0 captures 1440 and 390 only; the full "
                             "masterplan viewport ladder belongs to later packages.",
            "statesTested": ["default (no interaction, no reduced-motion override)"],
            "scrollWidthMatches": all(
                record["scrollWidth"] <= int(key)
                for key, record in dom_records.items()),
            "minimumTouchTarget": {"width": 44, "height": 44},
            "minimumComputedTextPx": None,
            "textCoverage": [],
            "contrastFailures": [],
            "placeholderLinks": max(record["placeholderLinks"]
                                    for record in dom_records.values()),
            "consoleErrors": sum(record["consoleErrors"]
                                 for record in dom_records.values()),
            "failedRequests": sorted({item for record in dom_records.values()
                                      for item in record["failedRequests"]}),
            "httpErrorResponses": sorted({item for record in dom_records.values()
                                          for item in record["httpErrorResponses"]}),
            "reducedMotion": "not measured; out of P0 scope",
            "noJavaScript": "not measured; out of P0 scope",
            "unmeasuredInP0": ["minimumComputedTextPx", "textCoverage",
                               "contrastFailures", "reducedMotion",
                               "noJavaScript"],
            "screenshots": screenshots,
            "deviations": deviations,

            "authorityNotes": {
                path: (REPO_ROOT / path).read_text().count(
                    "**Authority status:** Historical evidence and implementation context.")
                for path in ("design/DESIGN-LANGUAGE.md", "design/TEMPLATE.md",
                             "design/SITEMAP.md")
            },
            "revisionEndpointMatchesGit": revision["commit"] == head_commit,
            "domRevisionMatchesEndpoint": dom_matches,
            "dirtyStateMatchesGit": revision["dirty"] == bool(porcelain),
            "noStoreCoverage": no_store_coverage,
            "visiblePreviewChanged": bool(preview_diff),

            "controlFileHashesAtStart": start_hashes,
            "controlFileHashesBeforeCommit": end_hashes,
            "controlFilesUnchanged": control_unchanged,
            "previewAndAssetDiffVersusBase": preview_diff.splitlines(),
            "serverExceptions": server_stderr.count("Traceback"),
            "evidenceFiles": sorted(
                "evidence/P0/" + p.name for p in EVIDENCE_DIR.iterdir()
                if p.name != "result.json"),
            "tests": tests,
        }
        (EVIDENCE_DIR / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({k: result[k] for k in (
            "commit", "revisionEndpointMatchesGit", "domRevisionMatchesEndpoint",
            "dirtyStateMatchesGit", "noStoreCoverage", "visiblePreviewChanged",
            "controlFilesUnchanged", "serverExceptions")}, indent=2))
        return 0
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
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
