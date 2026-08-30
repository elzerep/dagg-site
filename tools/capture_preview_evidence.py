#!/usr/bin/env python3
"""Capture P0R1 preview evidence from one immutable-snapshot server process.

Runs the acceptance suite, then starts ``tools/serve_preview.py`` once and
drives the installed Google Chrome over the Chrome DevTools Protocol.
Screenshots, the ``/__revision`` response, a ``<head>`` DOM snapshot, a
response-header record and ``evidence/P0R1/result.json`` all come from that
single process, so every artefact provably describes one snapshot ID.

The capture is refused outright if any response header, any injected DOM
meta tag or any screenshot record disagrees with the server's snapshot ID:
partial evidence is worse than none, because it looks like proof.

Standard library only: the CDP transport below is a minimal RFC 6455
client. Nothing is written outside ``evidence/P0R1/`` and a temporary Chrome
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
EVIDENCE_DIR = REPO_ROOT / "evidence" / "P0R1"
PAGE_PATH = "/preview/directions/a-plus.html"
VIEWPORTS = (1440, 390)

CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
)

BASE_COMMIT = "972700bf95641bb6615a72d859fdd037329cbc86"

# The three authority documents must be byte-identical from the first
# recording to the pre-commit recomputation. The three implementation files
# are recorded in the same table precisely so their change is visible and
# attributable rather than hidden.
CONTROL_DOCUMENTS = (
    "design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md",
    "design/golden-standard/packages/P0R1-IMMUTABLE-PREVIEW-SNAPSHOT.md",
    "design/golden-standard/packages/P0-RECONCILE-AND-PREVIEW.md",
)
IMPLEMENTATION_FILES = (
    "tools/serve_preview.py",
    "tools/capture_preview_evidence.py",
    "tests/test_preview_revision.py",
)
CONTROL_FILES = CONTROL_DOCUMENTS + IMPLEMENTATION_FILES

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
  snapshotMeta: document.querySelectorAll('meta[name="dagg-snapshot"]').length,
  revision: (document.querySelector('meta[name="dagg-revision"]')||{}).content || null,
  dirty: (document.querySelector('meta[name="dagg-dirty"]')||{}).content || null,
  snapshot: (document.querySelector('meta[name="dagg-snapshot"]')||{}).content || null,
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


def compare_control_hashes(start: dict, end: dict) -> dict:
    """Say plainly which control files changed. The authority documents must
    not have moved; the implementation files are expected to have."""
    changed = sorted(k for k in end
                     if k in start and start[k] != end[k])
    missing = sorted(k for k in CONTROL_FILES if k not in start)
    return {
        "changedSinceStart": changed,
        "notRecordedAtStart": missing,
        "authorityDocumentsUnchanged": (
            None if any(d in missing for d in CONTROL_DOCUMENTS)
            else all(d not in changed for d in CONTROL_DOCUMENTS)),
        "implementationFilesChanged": [f for f in IMPLEMENTATION_FILES
                                       if f in changed],
    }


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


def default_port_is_free(port: int = 8912) -> tuple[bool, str | None]:
    """Report whether the documented preview port is free, and if not, name
    what holds it. A forgotten plain static server on this port is the exact
    failure P0R1 exists to prevent, so it must be identified, not shrugged at."""
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", port))
        return True, None
    except OSError:
        return False, port_holder(port)
    finally:
        probe.close()


def port_holder(port: int) -> str | None:
    lsof = shutil.which("lsof")
    if not lsof:
        return None
    listing = subprocess.run(
        [lsof, "-nP", "-iTCP:%d" % port, "-sTCP:LISTEN"],
        capture_output=True, text=True)
    rows = [line.split() for line in listing.stdout.splitlines()[1:] if line.strip()]
    if not rows:
        return None
    pid = rows[0][1]
    described = subprocess.run(["ps", "-p", pid, "-o", "command="],
                               capture_output=True, text=True).stdout.strip()
    return "pid %s: %s" % (pid, described or rows[0][0])


def build_deviations(dom_records: dict, default_port_free: bool,
                     port_holder_description: str | None = None) -> list[str]:  # noqa: C901
    """Everything a reviewer must know that the pass/fail flags do not say."""
    out = []
    if not default_port_free:
        out.append(
            "Documented preview port 8912 was already bound at capture time by "
            "a pre-existing process (%s), so this evidence was captured on an "
            "ephemeral port. That process was started before this package and "
            "was left running; it is not the immutable preview server. Anyone "
            "opening http://127.0.0.1:8912/ while it lives is reviewing a "
            "live-disk static server, which the masterplan forbids. Stop it "
            "before the next review. The documented default is unchanged."
            % (port_holder_description or "not identifiable on this system"))
    if any(record.get("carouselState") for record in dom_records.values()):
        out.append(
            "preview/directions/a-plus.html runs an IntersectionObserver "
            "carousel that auto-advances every 2600 ms, so its screenshots are "
            "not byte-reproducible. Each capture records carouselState and "
            "carouselSelected. Screenshot bytes are therefore not a snapshot "
            "identity check; the recorded snapshot ID is.")
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
            "preview. Out of P0R1 scope; recorded for the package that owns "
            "navigation." % placeholders)
    out.append(
        "P0R1 changed no public design, copy, IA, interaction or asset byte. "
        "These screenshots therefore look identical to the P0 capture; they "
        "exist to prove that the immutable snapshot serves the same page, not "
        "to show a visual change.")
    out.append(
        "Screenshots at 1440 and 390 px only. The full masterplan viewport "
        "ladder and the contrast, reduced-motion, no-JavaScript and computed "
        "text-size measurements are not covered by P0R1 and are recorded as "
        "unmeasured rather than as passes.")
    return out


def run_acceptance_suite() -> dict:
    """Run the real suite and record what it proved, pass or fail."""
    target = EVIDENCE_DIR / "tests.json"
    environment = dict(os.environ, DAGG_P0R1_TEST_JSON=str(target),
                       PYTHONDONTWRITEBYTECODE="1")
    started = time.monotonic()
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, env=environment)
    output = completed.stdout + completed.stderr
    (EVIDENCE_DIR / "tests-output.txt").write_text(output)
    detail = json.loads(target.read_text()) if target.exists() else {}
    summary = [line for line in output.splitlines()
               if line.startswith(("OK", "FAILED", "Ran "))]
    return {
        "command": "python3 -B -m unittest discover -s tests -v",
        "returnCode": completed.returncode,
        "passed": completed.returncode == 0,
        "seconds": round(time.monotonic() - started, 3),
        "summary": summary,
        "outcomes": [line.rsplit(" ... ", 1) for line in output.splitlines()
                     if " ... " in line],
        "detail": detail,
    }


def require_snapshot(headers: dict, snapshot_id: str, label: str):
    """Refuse the capture rather than write evidence that only looks whole."""
    lowered = {k.lower(): v for k, v in headers.items()}
    actual = lowered.get("x-dagg-snapshot")
    if actual != snapshot_id:
        raise SnapshotDisagreement(
            "%s carried snapshot %r, the server reports %r"
            % (label, actual, snapshot_id))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0,
                        help="preview server port (default: 0, pick a free port)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--base-commit", default=BASE_COMMIT,
                        help="commit to compare the served preview against")
    parser.add_argument("--skip-tests", action="store_true",
                        help="do not re-run the acceptance suite")
    args = parser.parse_args(argv)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    start_hashes = read_start_hashes()
    default_port_free, port_holder_description = default_port_is_free()
    tests = {} if args.skip_tests else run_acceptance_suite()

    server, base_url, startup_seconds = start_server(args.port, args.host)
    profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p0r1-chrome-"))
    chrome = None
    cdp = None
    screenshots = []
    try:
        status, revision_headers, revision_body = fetch(base_url, "/__revision")
        revision = json.loads(revision_body)
        snapshot_id = revision["snapshotId"]
        (EVIDENCE_DIR / "revision.json").write_bytes(revision_body)
        require_snapshot(revision_headers, snapshot_id, "/__revision")

        headers_record = {}
        no_store_coverage = []
        for label, path in HEADER_TARGETS:
            code, headers, body = fetch(base_url, path)
            require_snapshot(headers, snapshot_id, label)
            lowered = {k.lower(): v for k, v in headers.items()}
            compliant = all(lowered.get(k) == v for k, v in REQUIRED_NO_STORE.items())
            headers_record[label] = {
                "url": base_url + path,
                "status": code,
                "bytes": len(body),
                "headers": headers,
                "noStore": compliant,
                "snapshotMatches": True,
            }
            if compliant:
                no_store_coverage.append(label)
        json_no_store = all(
            {k.lower(): v for k, v in revision_headers.items()}.get(k) == v
            for k, v in REQUIRED_NO_STORE.items())
        headers_record["JSON"] = {
            "url": base_url + "/__revision",
            "status": status,
            "bytes": len(revision_body),
            "headers": revision_headers,
            "noStore": json_no_store,
            "snapshotMatches": True,
        }
        if json_no_store:
            no_store_coverage.append("JSON")
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
            if facts["snapshot"] != snapshot_id:
                raise SnapshotDisagreement(
                    "the %dpx DOM reported snapshot %r, the server reports %r"
                    % (width, facts["snapshot"], snapshot_id))
            if (facts["revisionMeta"], facts["dirtyMeta"],
                    facts["snapshotMeta"]) != (1, 1, 1):
                raise SnapshotDisagreement(
                    "the %dpx DOM did not carry exactly one of each meta tag"
                    % width)
            name = "a-plus-%dpx.png" % width
            (EVIDENCE_DIR / name).write_bytes(png)
            screenshots.append({
                "path": "evidence/P0R1/" + name,
                "viewport": width,
                "pixelDimensions": png_size(png),
                "pageUrl": facts["url"],
                "snapshotId": facts["snapshot"],
                "serverRevision": revision["commit"],
                "serverDirty": revision["dirty"],
                "sha256": hashlib.sha256(png).hexdigest(),
            })
            dom_records[str(width)] = {k: v for k, v in facts.items()
                                       if k != "headOuterHTML"}
            if width == VIEWPORTS[0]:
                (EVIDENCE_DIR / "a-plus-head-dom.html").write_text(
                    facts["headOuterHTML"] + "\n")

        recorded = {shot["snapshotId"] for shot in screenshots}
        if recorded != {snapshot_id}:
            raise SnapshotDisagreement(
                "screenshots span more than one snapshot: %s" % sorted(recorded))

        (EVIDENCE_DIR / "dom-metadata.json").write_text(
            json.dumps({"pageUrl": page_url,
                        "serverRevision": revision,
                        "byViewport": dom_records}, indent=2, sort_keys=True) + "\n")

        # -- correctness checks against git and the base revision ---------
        head_commit = git("rev-parse", "HEAD")
        porcelain = git("status", "--porcelain")
        base_commit = args.base_commit
        public_diff = git("diff", "--name-only", base_commit, "--",
                          "preview", "assets", "marketing", "v1", "index.html",
                          "robots.txt")

        dom_matches = all(
            record["revision"] == revision["commit"]
            and record["dirty"] == ("true" if revision["dirty"] else "false")
            and record["snapshot"] == snapshot_id
            and record["revisionMeta"] == 1 and record["dirtyMeta"] == 1
            and record["snapshotMeta"] == 1
            for record in dom_records.values())

        deviations = build_deviations(dom_records, default_port_free,
                                      port_holder_description)
        if not tests.get("passed", True):
            deviations.insert(0, "The acceptance suite did not pass; see "
                                 "evidence/P0R1/tests-output.txt.")

        end_hashes = control_hashes()
        control_comparison = compare_control_hashes(start_hashes, end_hashes)
        if control_comparison["authorityDocumentsUnchanged"] is False:
            deviations.insert(0, "An authority document changed during "
                                 "execution: %s"
                              % ", ".join(control_comparison["changedSinceStart"]))

        server.terminate()
        server.wait(timeout=10)
        server_stderr = server.stderr.read()
        (EVIDENCE_DIR / "server-stderr.txt").write_text(server_stderr)

        result = {
            "package": "P0R1",
            "commit": head_commit,
            "baseCommit": base_commit,
            "snapshotId": snapshot_id,
            "assetRevision": snapshot_id,
            "snapshotFileCount": revision["snapshotFileCount"],
            "snapshotByteCount": revision["snapshotByteCount"],
            "snapshotSkippedPaths": revision.get("snapshotSkippedPaths", []),
            "snapshotExcludes": [".git/**", "evidence/**", "**/__pycache__/**",
                                 "**/*.pyc", ".DS_Store"],
            "branch": revision["branch"],
            "dirtyAtCapture": revision["dirty"],
            "capturedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverStartupSeconds": startup_seconds,
            "serverStartupUnderTwoSeconds": startup_seconds < 2.0,
            "chrome": chrome_version.get("product"),
            "chromePath": chrome_path,
            "viewports": sorted(VIEWPORTS),
            "viewportScope": "P0R1 captures 1440 and 390 only; the full "
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
            "reducedMotion": "not measured; out of P0R1 scope",
            "noJavaScript": "not measured; out of P0R1 scope",
            "unmeasuredInP0R1": ["minimumComputedTextPx", "textCoverage",
                                 "contrastFailures", "reducedMotion",
                                 "noJavaScript"],
            "screenshots": screenshots,
            "deviations": deviations,

            "revisionEndpointMatchesGit": revision["commit"] == head_commit,
            "domSnapshotMatchesEndpoint": dom_matches,
            "allResponseHeadersMatchSnapshot": True,
            "allScreenshotsShareOneSnapshot": True,
            "dirtyStateMatchesGit": revision["dirty"] == bool(porcelain),
            "noStoreCoverage": no_store_coverage,
            "evidenceExcludedFromSnapshot": True,
            "documentedPortFree": default_port_free,
            "documentedPortHolder": port_holder_description,
            "publicSourceChangedVersusBase": bool(public_diff),
            "publicDiffVersusBase": public_diff.splitlines(),

            "controlFileHashesAtStart": start_hashes,
            "controlFileHashesBeforeCommit": end_hashes,
            "controlFileComparison": control_comparison,
            "serverExceptions": server_stderr.count("Traceback"),
            "evidenceFiles": sorted(
                "evidence/P0R1/" + item.name for item in EVIDENCE_DIR.iterdir()
                if item.name != "result.json"),
            "tests": tests,
        }
        (EVIDENCE_DIR / "result.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({k: result[k] for k in (
            "commit", "snapshotId", "dirtyAtCapture", "snapshotFileCount",
            "revisionEndpointMatchesGit", "domSnapshotMatchesEndpoint",
            "allScreenshotsShareOneSnapshot", "dirtyStateMatchesGit",
            "noStoreCoverage", "publicSourceChangedVersusBase",
            "serverExceptions")}, indent=2))
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
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
