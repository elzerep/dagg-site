#!/usr/bin/env python3
"""Immutable-snapshot local preview server for the Dagg site.

One running process serves exactly one workspace moment. Before the socket
is bound and before ``LISTENING`` is announced, every served HTML, CSS,
JavaScript, font, JSON and image byte is frozen into an in-memory
path-and-byte map and reduced to a deterministic SHA-256 ``snapshotId``. A
running server never reads a served source path again, so HTML from one
workspace moment can never be combined with CSS, JavaScript or images from
another -- not even while the working tree is dirty.

Source changes become reviewable only after a restart, which produces a new
snapshot ID. The commit, dirty state and snapshot ID are exposed at
``/__revision``, on every response header and in invisible ``<head>``
metadata of every served HTML document. Source files are never modified.

Usage:

    python3 tools/serve_preview.py --port 8912

Standard library only. Development use only; this serves no production code.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import mimetypes
import re
import struct
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

# Excluded from the served set. ``evidence`` is excluded so a capture run
# cannot reference itself and so the post-commit clean run reproduces the
# pre-commit snapshot ID; the rest is Git plumbing and build litter that is
# not website content.
EXCLUDED_TOP_DIRS = (".git", "evidence")
EXCLUDED_DIR_NAMES = ("__pycache__",)
EXCLUDED_SUFFIXES = (".pyc",)
EXCLUDED_BASENAMES = (".DS_Store",)


class SnapshotError(RuntimeError):
    """Raised when the served set cannot be frozen safely. Fatal at startup."""


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
    """Read commit and dirty state. Taken once, at snapshot start."""
    porcelain = _git(repo_root, "status", "--porcelain")
    return {
        "commit": _git(repo_root, "rev-parse", "HEAD"),
        "abbreviatedCommit": _git(repo_root, "rev-parse", "--short", "HEAD"),
        "branch": _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD"),
        "dirty": bool(porcelain),
        "dirtyEntryCount": len([l for l in porcelain.splitlines() if l.strip()]),
        "serverStartedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "repositoryRoot": str(repo_root),
    }


# --------------------------------------------------------------------------
# The immutable snapshot
# --------------------------------------------------------------------------


def is_excluded(relative: str) -> bool:
    segments = relative.split("/")
    if segments[0] in EXCLUDED_TOP_DIRS:
        return True
    if any(segment in EXCLUDED_DIR_NAMES for segment in segments[:-1]):
        return True
    if segments[-1] in EXCLUDED_BASENAMES:
        return True
    return relative.endswith(EXCLUDED_SUFFIXES)


def list_candidate_paths(repo_root: Path) -> list[str]:
    """Every tracked and every untracked-but-not-ignored path, sorted by its
    UTF-8 byte sequence, with the excluded set removed."""
    raw = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo_root),
         "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True, capture_output=True,
    ).stdout
    seen: set[str] = set()
    for chunk in raw.split(b"\0"):
        if not chunk:
            continue
        relative = chunk.decode("utf-8", errors="surrogateescape")
        relative = relative.replace("\\", "/").strip("/")
        if not relative or is_excluded(relative):
            continue
        seen.add(relative)
    return sorted(seen, key=lambda p: p.encode("utf-8"))


def _snapshot_read(repo_root: Path, relative: str) -> bytes | None:
    """Read one candidate path, refusing anything that escapes the repository.

    Returns ``None`` when the path is listed by Git but absent from the
    working tree (a staged deletion, or a file removed before this server
    started). Such a path is simply not part of the snapshot and answers 404.
    """
    if ".." in relative.split("/") or relative.startswith("/"):
        raise SnapshotError("path escapes the repository: %s" % relative)
    full = repo_root / relative
    try:
        resolved = full.resolve()
    except OSError as err:
        raise SnapshotError("cannot resolve %s: %s" % (relative, err)) from err
    if resolved != repo_root and repo_root not in resolved.parents:
        raise SnapshotError("path escapes the repository: %s -> %s"
                            % (relative, resolved))
    if full.is_symlink():
        # A symlink is snapshotted only when it points at a regular file that
        # is itself inside the repository; anything else is refused loudly
        # rather than served from an unknown workspace.
        if not resolved.is_file():
            raise SnapshotError(
                "symlink %s does not resolve to a regular file inside the "
                "repository" % relative)
    if not full.exists():
        return None
    if not full.is_file():
        raise SnapshotError("%s is not a regular file" % relative)
    return full.read_bytes()


def frame(relative: str, content: bytes) -> bytes:
    """Unambiguous framing for the snapshot digest: eight-byte big-endian
    path length, UTF-8 path bytes, eight-byte big-endian content length,
    content bytes. Length prefixes make ``a/b`` + ``c`` indistinguishable
    from ``a`` + ``b/c`` impossible."""
    path_bytes = relative.encode("utf-8", errors="surrogateescape")
    return (struct.pack(">Q", len(path_bytes)) + path_bytes
            + struct.pack(">Q", len(content)) + content)


def compute_snapshot_id(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(files, key=lambda p: p.encode("utf-8")):
        digest.update(frame(relative, files[relative]))
    return digest.hexdigest()


class Snapshot:
    """One immutable path-and-byte view of the workspace.

    Every byte is read in ``__init__``. Nothing here reopens a source path
    afterwards, so the served set cannot drift while the server runs.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.files: dict[str, bytes] = {}
        self.skipped: list[str] = []
        for relative in list_candidate_paths(repo_root):
            content = _snapshot_read(repo_root, relative)
            if content is None:
                self.skipped.append(relative)
                continue
            self.files[relative] = content
        self.paths = sorted(self.files, key=lambda p: p.encode("utf-8"))
        self.snapshot_id = compute_snapshot_id(self.files)
        self.byte_count = sum(len(v) for v in self.files.values())
        self.directories = self._build_directories()

    def _build_directories(self) -> dict[str, set[str]]:
        """Directory listings derived from the frozen path map, never from
        the live filesystem."""
        tree: dict[str, set[str]] = {"": set()}
        for relative in self.paths:
            segments = relative.split("/")
            for depth in range(len(segments)):
                parent = "/".join(segments[:depth])
                child = segments[depth] + ("/" if depth < len(segments) - 1 else "")
                tree.setdefault(parent, set()).add(child)
        return tree

    def get(self, relative: str) -> bytes | None:
        return self.files.get(relative)

    def is_directory(self, relative: str) -> bool:
        return relative in self.directories

    def entries(self, relative: str) -> list[str]:
        return sorted(self.directories.get(relative, ()),
                      key=lambda name: (not name.endswith("/"), name))


# --------------------------------------------------------------------------
# Path resolution (map-only; the filesystem is never consulted)
# --------------------------------------------------------------------------


def resolve_request_path(raw_path: str) -> str | None:
    """Map a request target to a repository-relative POSIX path.

    Query strings are discarded, percent-escapes (including spaces) are
    decoded, and any traversal segment returns ``None`` so the caller can
    refuse the request.
    """
    path = urllib.parse.urlsplit(raw_path).path
    path = urllib.parse.unquote(path, errors="replace")
    segments: list[str] = []
    for segment in path.replace("\\", "/").split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            return None
        segments.append(segment)
    return "/".join(segments)


def guess_type(relative: str) -> str:
    name = relative.rsplit("/", 1)[-1]
    suffix = ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""
    if suffix in EXTRA_TYPES:
        return EXTRA_TYPES[suffix]
    guessed, _ = mimetypes.guess_type(name)
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
        '<meta name="dagg-snapshot" content="%s">\n'
        % (revision["commit"],
           "true" if revision["dirty"] else "false",
           revision["snapshotId"])
    )


def inject_revision_meta(raw: bytes, revision: dict) -> bytes:
    """Insert the revision metadata into ``<head>``.

    Metadata goes inside ``<head>`` only, so it can never produce a visible
    layout node. The snapshotted bytes are not mutated; a fresh buffer is
    returned and the file on disk is untouched.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    block = revision_meta(revision)
    match = _HEAD_CLOSE.search(text)
    if match:
        # Re-use the indentation of the closing tag so the only new lines in
        # the served document are the three meta tags themselves.
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
    server_version = "DaggPreview/2.0"
    protocol_version = "HTTP/1.1"

    # Set by ``build_server``.
    snapshot: Snapshot
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
        self.send_header("X-Dagg-Snapshot", self.revision["snapshotId"])
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _error(self, status, message: str, head_only=False):
        body = ("<!doctype html><title>%d</title><h1>%d %s</h1>" % (
            status.value, status.value, message)).encode("utf-8")
        self._send(status, "text/html; charset=utf-8", body, head_only)

    def _directory_listing(self, relative: str) -> bytes:
        label = relative or "."
        rows = []
        for name in self.snapshot.entries(relative):
            rows.append('<li><a href="%s">%s</a></li>'
                        % (urllib.parse.quote(name), name))
        return ("<!doctype html><html><head><meta charset=\"utf-8\">"
                "<title>%s</title></head><body><h1>%s</h1><ul>%s</ul></body></html>"
                % (label, label, "".join(rows))).encode("utf-8")

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

        relative = resolve_request_path(self.path)
        if relative is None:
            self._error(HTTPStatus.FORBIDDEN, "Forbidden", head_only)
            return

        body = self.snapshot.get(relative)
        if body is None and self.snapshot.is_directory(relative):
            index = (relative + "/index.html").lstrip("/")
            indexed = self.snapshot.get(index)
            if indexed is not None:
                relative, body = index, indexed
            else:
                self._send(HTTPStatus.OK, "text/html; charset=utf-8",
                           self._directory_listing(relative), head_only)
                return

        if body is None:
            self._error(HTTPStatus.NOT_FOUND, "Not Found", head_only)
            return

        if relative.lower().endswith(HTML_SUFFIXES):
            body = inject_revision_meta(body, self.revision)
        self._send(HTTPStatus.OK, guess_type(relative), body, head_only)

    def log_message(self, fmt, *args):
        if not self.quiet:
            super().log_message(fmt, *args)


class PreviewServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    exception_count = 0


def build_server(repo_root: Path, host: str, port: int, quiet: bool) -> PreviewServer:
    """Freeze first, bind second. Nothing is served before the snapshot is
    complete, so no request can observe a partially read workspace."""
    revision = read_revision(repo_root)
    snapshot = Snapshot(repo_root)
    revision["snapshotId"] = snapshot.snapshot_id
    revision["abbreviatedSnapshotId"] = snapshot.snapshot_id[:12]
    revision["snapshotFileCount"] = len(snapshot.paths)
    revision["snapshotByteCount"] = snapshot.byte_count
    revision["snapshotSkippedPaths"] = snapshot.skipped
    handler = type("BoundPreviewHandler", (PreviewHandler,), {
        "snapshot": snapshot,
        "revision": revision,
        "quiet": quiet,
    })
    server = PreviewServer((host, port), handler)
    server.snapshot = snapshot
    server.revision = revision
    return server


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="port to bind (default: %d; 0 picks a free port)" % DEFAULT_PORT)
    parser.add_argument("--host", default=DEFAULT_HOST,
                        help="interface to bind (default: %s)" % DEFAULT_HOST)
    parser.add_argument("--repo-root", default=None,
                        help="repository to snapshot (default: the repository "
                             "containing this script)")
    parser.add_argument("--quiet", action="store_true", help="suppress request logging")
    args = parser.parse_args(argv)

    start = Path(args.repo_root).resolve() if args.repo_root \
        else Path(__file__).resolve().parent
    try:
        repo_root = find_repo_root(start)
    except subprocess.CalledProcessError:
        print("not a Git repository: %s" % start, file=sys.stderr)
        return 2
    try:
        server = build_server(repo_root, args.host, args.port, args.quiet)
    except SnapshotError as err:
        print("snapshot refused: %s" % err, file=sys.stderr, flush=True)
        return 2
    host, port = server.server_address[:2]
    revision = server.revision

    # Machine-readable startup line, consumed by the evidence harness. It is
    # printed only after every served byte is already frozen in memory.
    print("LISTENING %s %d" % (host, port), flush=True)
    print("Dagg immutable preview  http://%s:%d/" % (host, port), file=sys.stderr)
    print("  revision %s (%s) dirty=%s"
          % (revision["abbreviatedCommit"], revision["branch"],
             str(revision["dirty"]).lower()), file=sys.stderr)
    print("  snapshot %s  %d files  %d bytes"
          % (revision["abbreviatedSnapshotId"], revision["snapshotFileCount"],
             revision["snapshotByteCount"]), file=sys.stderr)
    print("  snapshotId %s" % revision["snapshotId"], file=sys.stderr, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
