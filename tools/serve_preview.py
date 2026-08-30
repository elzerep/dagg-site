#!/usr/bin/env python3
"""Revision-safe local preview server for the Dagg site.

Every HTML, CSS, JavaScript, font, JSON and image response is sent with
no-store headers, so a browser can never mix current HTML with cached CSS.
The exact Git revision and dirty state are exposed at ``/__revision`` and
injected into every served HTML document as ``<meta name="dagg-revision">``
and ``<meta name="dagg-dirty">``. Source files are never modified.

Usage:

    python3 tools/serve_preview.py --port 8912

Standard library only. Development use only; this serves no production code.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import mimetypes
import re
import subprocess
import sys
import traceback
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_PORT = 8912
DEFAULT_HOST = "127.0.0.1"
REVISION_PATH = "/__revision"

NO_STORE_HEADERS = (
    ("Cache-Control", "no-store, max-age=0"),
    ("Pragma", "no-cache"),
    ("Expires", "0"),
)

EXTRA_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".txt": "text/plain; charset=utf-8",
    ".ico": "image/x-icon",
}

HTML_SUFFIXES = (".html", ".htm")


# --------------------------------------------------------------------------
# Git revision
# --------------------------------------------------------------------------


def _git(repo_root: Path, *args: str) -> str:
    """Run a read-only git command. ``--no-optional-locks`` keeps the index
    from being rewritten, so serving never mutates the working tree."""
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def find_repo_root(start: Path) -> Path:
    return Path(_git(start, "rev-parse", "--show-toplevel")).resolve()


def read_revision(repo_root: Path) -> dict:
    """Snapshot the served revision. Taken once, at server start."""
    full = _git(repo_root, "rev-parse", "HEAD")
    porcelain = _git(repo_root, "status", "--porcelain")
    return {
        "commit": full,
        "abbreviatedCommit": _git(repo_root, "rev-parse", "--short", "HEAD"),
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(porcelain),
        "dirtyEntryCount": len([l for l in porcelain.splitlines() if l.strip()]),
        "serverStartedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "repositoryRoot": str(repo_root),
    }


# --------------------------------------------------------------------------
# Path resolution
# --------------------------------------------------------------------------


def resolve_request_path(repo_root: Path, raw_path: str) -> Path | None:
    """Map a request target to a file below ``repo_root``.

    Query strings are discarded, percent-escapes (including spaces) are
    decoded, and any traversal that would leave the repository root returns
    ``None`` so the caller can refuse the request.
    """
    path = urllib.parse.urlsplit(raw_path).path
    path = urllib.parse.unquote(path, errors="replace")
    segments: list[str] = []
    # Reject "..", before any normalisation could quietly collapse it.
    for segment in path.replace("\\", "/").split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            return None
        segments.append(segment)
    candidate = repo_root.joinpath(*segments)
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    if resolved != repo_root and repo_root not in resolved.parents:
        return None
    return resolved


def guess_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in EXTRA_TYPES:
        return EXTRA_TYPES[suffix]
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


# --------------------------------------------------------------------------
# HTML metadata injection (in memory only)
# --------------------------------------------------------------------------


_HEAD_CLOSE = re.compile(r"</head\s*>", re.IGNORECASE)
_HEAD_OPEN = re.compile(r"<head[^>]*>", re.IGNORECASE)
_HTML_OPEN = re.compile(r"<html[^>]*>", re.IGNORECASE)


def revision_meta(revision: dict) -> str:
    return (
        '<meta name="dagg-revision" content="%s">\n'
        '<meta name="dagg-dirty" content="%s">\n'
        % (revision["commit"], "true" if revision["dirty"] else "false")
    )


def inject_revision_meta(raw: bytes, revision: dict) -> bytes:
    """Insert the revision metadata into ``<head>``.

    Metadata goes inside ``<head>`` only, so it can never produce a visible
    layout node. The file on disk is untouched.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    block = revision_meta(revision)
    match = _HEAD_CLOSE.search(text)
    if match:
        # Re-use the indentation of the closing tag so the only new lines in
        # the served document are the two meta tags themselves.
        line_start = text.rfind("\n", 0, match.start()) + 1
        indent = text[line_start : match.start()]
        if indent.strip():
            indent = ""
        block = block.replace("\n", "\n" + indent)
        return (text[: match.start()] + block + text[match.start() :]).encode("utf-8")
    match = _HEAD_OPEN.search(text)
    if match:
        return (text[: match.end()] + "\n" + block + text[match.end() :]).encode("utf-8")
    match = _HTML_OPEN.search(text)
    if match:
        head = "\n<head>\n" + block + "</head>\n"
        return (text[: match.end()] + head + text[match.end() :]).encode("utf-8")
    return (block + text).encode("utf-8")


# --------------------------------------------------------------------------
# Request handler
# --------------------------------------------------------------------------


class PreviewHandler(BaseHTTPRequestHandler):
    server_version = "DaggPreview/1.0"
    protocol_version = "HTTP/1.1"

    # Set by ``build_server``.
    repo_root: Path
    revision: dict
    quiet: bool = False

    # -- helpers ---------------------------------------------------------

    def _send(self, status, content_type: str, body: bytes, head_only=False):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in NO_STORE_HEADERS:
            self.send_header(name, value)
        self.send_header("X-Dagg-Revision", self.revision["commit"])
        self.send_header("X-Dagg-Dirty", "true" if self.revision["dirty"] else "false")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _error(self, status, message: str, head_only=False):
        body = ("<!doctype html><title>%d</title><h1>%d %s</h1>" % (
            status.value, status.value, message)).encode("utf-8")
        self._send(status, "text/html; charset=utf-8", body, head_only)

    def _directory_listing(self, target: Path) -> bytes:
        rel = target.relative_to(self.repo_root).as_posix() or "."
        rows = []
        for entry in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name)):
            name = entry.name + ("/" if entry.is_dir() else "")
            rows.append('<li><a href="%s">%s</a></li>'
                        % (urllib.parse.quote(name), name))
        return ("<!doctype html><html><head><meta charset=\"utf-8\">"
                "<title>%s</title></head><body><h1>%s</h1><ul>%s</ul></body></html>"
                % (rel, rel, "".join(rows))).encode("utf-8")

    # -- verbs -----------------------------------------------------------

    def do_GET(self):
        self._handle(head_only=False)

    def do_HEAD(self):
        self._handle(head_only=True)

    def _handle(self, head_only: bool):
        try:
            self._dispatch(head_only)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self.server.exception_count += 1
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            try:
                self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "Server Error", head_only)
            except Exception:
                pass

    def _dispatch(self, head_only: bool):
        request_path = urllib.parse.urlsplit(self.path).path

        if request_path == REVISION_PATH:
            body = json.dumps(self.revision, indent=2, sort_keys=True).encode("utf-8")
            self._send(HTTPStatus.OK, "application/json; charset=utf-8", body, head_only)
            return

        target = resolve_request_path(self.repo_root, self.path)
        if target is None:
            self._error(HTTPStatus.FORBIDDEN, "Forbidden", head_only)
            return

        if target.is_dir():
            index = target / "index.html"
            if index.is_file():
                target = index
            else:
                self._send(HTTPStatus.OK, "text/html; charset=utf-8",
                           self._directory_listing(target), head_only)
                return

        if not target.is_file():
            self._error(HTTPStatus.NOT_FOUND, "Not Found", head_only)
            return

        body = target.read_bytes()
        if target.suffix.lower() in HTML_SUFFIXES:
            body = inject_revision_meta(body, self.revision)
        self._send(HTTPStatus.OK, guess_type(target), body, head_only)

    def log_message(self, fmt, *args):
        if not self.quiet:
            super().log_message(fmt, *args)


class PreviewServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    exception_count = 0


def build_server(repo_root: Path, host: str, port: int, quiet: bool) -> PreviewServer:
    revision = read_revision(repo_root)
    handler = type("BoundPreviewHandler", (PreviewHandler,), {
        "repo_root": repo_root,
        "revision": revision,
        "quiet": quiet,
    })
    return PreviewServer((host, port), handler)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="port to bind (default: %d; 0 picks a free port)" % DEFAULT_PORT)
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help="interface to bind (default: %s)" % DEFAULT_HOST)
    parser.add_argument("--quiet", action="store_true", help="suppress request logging")
    args = parser.parse_args(argv)

    repo_root = find_repo_root(Path(__file__).resolve().parent)
    server = build_server(repo_root, args.host, args.port, args.quiet)
    host, port = server.server_address[:2]
    revision = server.RequestHandlerClass.revision

    # Machine-readable startup line, consumed by the evidence harness.
    print("LISTENING %s %d" % (host, port), flush=True)
    print("Dagg revision-safe preview  http://%s:%d/" % (host, port), file=sys.stderr)
    print("  revision %s (%s) dirty=%s"
          % (revision["abbreviatedCommit"], revision["branch"],
             str(revision["dirty"]).lower()), file=sys.stderr, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
