#!/usr/bin/env python3
"""Immutable-snapshot preview tests.

Proves that one preview process serves exactly one workspace moment. HTML,
CSS, JavaScript, raster image and JSON all carry the same snapshot ID as
``/__revision``; the snapshot ID is independently recomputed here from the
framed algorithm declared in P0R1; and changing, deleting or creating source
files while a server runs cannot alter a single served byte. Restarting
after those changes is proved to be the only way to see them, and to produce
a different snapshot ID.

Coverage: HTML, CSS, JavaScript, raster image (PNG), JSON, directory
indexes, traversal refusal, percent-encoded spaces, query strings,
clean/dirty reporting, post-startup mutation, restart behaviour, evidence
exclusion, startup time, owned-file scope and server exceptions. The Dagg
worktree is never mutated: every mutation test runs in a throwaway Git
repository under a temporary directory. Standard library only.

    python3 -B -m unittest discover -s tests -v
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.dont_write_bytecode = True  # keep __pycache__ out of the working tree
sys.path.insert(0, str(TOOLS))

import serve_preview  # noqa: E402  (path set above)

BASE_COMMIT = "972700bf95641bb6615a72d859fdd037329cbc86"

HTML_PATH = "/preview/directions/a-plus.html"
CSS_PATH = "/preview/directions/tokens.css"
JS_PATH = "/preview/site/site.js"
IMAGE_PATH = "/assets/dagg-logotype-dark.png"

REQUIRED_NO_STORE = {
    "cache-control": "no-store, max-age=0",
    "pragma": "no-cache",
    "expires": "0",
}

# Everything P0R1 is allowed to create or change. Anything else in the diff
# or in the working tree is a scope failure, not a detail.
OWNED_PATHS = {
    "README.md",
    "design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md",
    "design/golden-standard/packages/P0-RECONCILE-AND-PREVIEW.md",
    "design/golden-standard/packages/P0R1-IMMUTABLE-PREVIEW-SNAPSHOT.md",
    "tools/serve_preview.py",
    "tools/capture_preview_evidence.py",
    "tests/test_preview_revision.py",
    "evidence/P0/REJECTED-BY-CODEX.md",
}
OWNED_PREFIXES = ("evidence/P0R1/",)

PUBLIC_PREFIXES = ("preview/", "assets/", "marketing/", "v1/")
PUBLIC_FILES = {"index.html", "robots.txt"}

# Filled in as tests run, written out when DAGG_P0R1_TEST_JSON is set.
RESULTS: dict = {"checks": {}, "coverage": [], "notes": []}


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return git_raw(*args, cwd=cwd).strip()


def git_raw(*args: str, cwd: Path = REPO_ROOT) -> str:
    """Unstripped output. ``git status --porcelain`` encodes the status in
    the first two columns, so stripping the result would silently eat the
    leading space of an unstaged-only entry and corrupt every path."""
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(cwd), *args],
        check=True, capture_output=True, text=True).stdout


def is_owned(path: str) -> bool:
    return path in OWNED_PATHS or path.startswith(OWNED_PREFIXES)


def is_public(path: str) -> bool:
    return path.startswith(PUBLIC_PREFIXES) or path in PUBLIC_FILES


# --------------------------------------------------------------------------
# An independent implementation of the P0R1 snapshot algorithm
# --------------------------------------------------------------------------


def independent_snapshot_id(repo_root: Path) -> tuple[str, int, int]:
    """Recompute the snapshot ID straight from the package text, without
    reusing the server's helpers, so a bug in the server cannot hide behind
    a matching bug in the test."""
    raw = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo_root), "ls-files",
         "--cached", "--others", "--exclude-standard", "-z"],
        check=True, capture_output=True).stdout
    paths = set()
    for chunk in raw.split(b"\0"):
        if not chunk:
            continue
        name = chunk.decode("utf-8", errors="surrogateescape")
        segments = name.split("/")
        if segments[0] in (".git", "evidence"):
            continue
        if "__pycache__" in segments[:-1] or name.endswith(".pyc"):
            continue
        if segments[-1] == ".DS_Store":
            continue
        paths.add(name)

    digest = hashlib.sha256()
    count = 0
    total = 0
    for name in sorted(paths, key=lambda p: p.encode("utf-8")):
        target = repo_root / name
        if not target.exists():
            continue
        content = target.read_bytes()
        path_bytes = name.encode("utf-8", errors="surrogateescape")
        digest.update(struct.pack(">Q", len(path_bytes)))
        digest.update(path_bytes)
        digest.update(struct.pack(">Q", len(content)))
        digest.update(content)
        count += 1
        total += len(content)
    return digest.hexdigest(), count, total


# --------------------------------------------------------------------------
# Server processes
# --------------------------------------------------------------------------


class ServerProcess:
    """The real CLI, started on an available local port."""

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.started = time.monotonic()
        command = [sys.executable, "-B", str(TOOLS / "serve_preview.py"),
                   "--port", "0", "--quiet"]
        if repo_root != REPO_ROOT:
            command += ["--repo-root", str(repo_root)]
        self.proc = subprocess.Popen(
            command, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True)
        line = self.proc.stdout.readline().strip()
        if not line.startswith("LISTENING "):
            raise RuntimeError("server did not announce a port: %r %s"
                               % (line, self.proc.stderr.read()))
        self.startup_seconds = round(time.monotonic() - self.started, 3)
        _, host, port = line.split()
        self.host, self.port = host, int(port)
        self.base = "http://%s:%s" % (host, port)

    def get(self, path: str):
        request = urllib.request.Request(self.base + path)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, dict(response.headers.items()), response.read()
        except urllib.error.HTTPError as err:
            with err:
                return err.code, dict(err.headers.items()), err.read()

    def revision(self) -> dict:
        status, _, body = self.get("/__revision")
        assert status == 200, status
        return json.loads(body)

    def stop(self) -> str:
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=10)
        stderr = self.proc.stderr.read()
        self.proc.stdout.close()
        self.proc.stderr.close()
        return stderr


def make_throwaway_repo(root: Path, dirty: bool = False) -> Path:
    """A small committed repository that mutation tests may destroy freely."""
    root.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "probe", cwd=root)
    git("config", "user.email", "p0r1@example.invalid", cwd=root)
    git("config", "user.name", "P0R1", cwd=root)
    (root / "index.html").write_text(
        "<!doctype html><html><head><title>probe</title>"
        '<link rel="stylesheet" href="style.css"></head>'
        "<body><p>one</p></body></html>")
    (root / "style.css").write_text("body{color:#111}\n")
    (root / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    (root / "data.json").write_text('{"n": 1}\n')
    git("add", "-A", cwd=root)
    git("commit", "-q", "-m", "probe", cwd=root)
    if dirty:
        (root / "style.css").write_text("body{color:#222}\n")
    return root


# --------------------------------------------------------------------------
# Tests against the real Dagg repository (read-only)
# --------------------------------------------------------------------------


class SnapshotContractTest(unittest.TestCase):
    """Acceptance points 1-5, 11-14 on the live repository. Read-only."""

    server: ServerProcess

    @classmethod
    def setUpClass(cls):
        cls.server = ServerProcess()
        cls.head_commit = git("rev-parse", "HEAD")
        cls.porcelain = git("status", "--porcelain")
        status, headers, body = cls.server.get("/__revision")
        assert status == 200, status
        cls.revision = json.loads(body)
        cls.revision_headers = headers

    @classmethod
    def tearDownClass(cls):
        stderr = cls.server.stop()
        RESULTS["serverStderr"] = stderr
        RESULTS["checks"]["zeroServerExceptions"] = "Traceback" not in stderr

    # -- helpers ---------------------------------------------------------

    def assert_no_store(self, headers: dict, label: str):
        lowered = {k.lower(): v for k, v in headers.items()}
        for name, expected in REQUIRED_NO_STORE.items():
            self.assertIn(name, lowered, "%s missing %s" % (label, name))
            self.assertEqual(lowered[name], expected,
                             "%s has wrong %s" % (label, name))
        self.assertNotIn("etag", lowered, "%s must not send a validator" % label)
        self.assertNotIn("last-modified", lowered,
                         "%s must not send a validator" % label)
        if label not in RESULTS["coverage"]:
            RESULTS["coverage"].append(label)

    def assert_snapshot_headers(self, headers: dict, label: str):
        lowered = {k.lower(): v for k, v in headers.items()}
        self.assertEqual(lowered.get("x-dagg-snapshot"),
                         self.revision["snapshotId"],
                         "%s carries a different snapshot" % label)
        self.assertEqual(lowered.get("x-dagg-revision"), self.revision["commit"])
        self.assertEqual(lowered.get("x-dagg-dirty"),
                         "true" if self.revision["dirty"] else "false")

    # -- 1. revision endpoint fields -------------------------------------

    def test_01_revision_endpoint_has_every_required_field(self):
        for field in ("commit", "abbreviatedCommit", "branch", "dirty",
                      "serverStartedAt", "repositoryRoot", "snapshotId",
                      "snapshotFileCount", "snapshotByteCount"):
            self.assertIn(field, self.revision, "missing %s" % field)
        self.assertIsInstance(self.revision["dirty"], bool)
        self.assertEqual(self.revision["repositoryRoot"], str(REPO_ROOT))
        self.assertEqual(self.revision["commit"], self.head_commit)
        self.assertEqual(self.revision["dirty"], bool(self.porcelain))
        self.assertTrue(self.revision["commit"].startswith(
            self.revision["abbreviatedCommit"]))
        self.assertRegex(self.revision["snapshotId"], r"^[0-9a-f]{64}$")
        self.assertGreater(self.revision["snapshotFileCount"], 0)
        self.assertGreater(self.revision["snapshotByteCount"], 0)
        RESULTS["commit"] = self.head_commit
        RESULTS["dirty"] = self.revision["dirty"]
        RESULTS["snapshotId"] = self.revision["snapshotId"]
        RESULTS["snapshotFileCount"] = self.revision["snapshotFileCount"]
        RESULTS["snapshotByteCount"] = self.revision["snapshotByteCount"]
        RESULTS["checks"]["revisionEndpointFields"] = True
        RESULTS["checks"]["revisionEndpointMatchesGit"] = True
        RESULTS["checks"]["dirtyStateMatchesGit"] = True

    # -- 2. one snapshot across every content type -----------------------

    def test_02_every_content_type_carries_one_snapshot_id(self):
        for label, path in (("HTML", HTML_PATH), ("CSS", CSS_PATH),
                            ("JavaScript", JS_PATH), ("raster-image", IMAGE_PATH),
                            ("JSON", "/__revision")):
            status, headers, body = self.server.get(path)
            self.assertEqual(status, 200, "%s not served" % label)
            self.assertGreater(len(body), 0, "%s served empty" % label)
            self.assert_snapshot_headers(headers, label)
        RESULTS["checks"]["oneSnapshotAcrossContentTypes"] = True

    # -- 3. exactly one of each meta, inside <head> ----------------------

    def test_03_html_has_exactly_one_of_each_meta_inside_head(self):
        _, _, body = self.server.get(HTML_PATH)
        text = body.decode("utf-8")
        revisions = re.findall(
            r'<meta name="dagg-revision" content="([0-9a-f]{40})">', text)
        dirties = re.findall(
            r'<meta name="dagg-dirty" content="(true|false)">', text)
        snapshots = re.findall(
            r'<meta name="dagg-snapshot" content="([0-9a-f]{64})">', text)
        self.assertEqual(len(revisions), 1, "expected exactly one dagg-revision")
        self.assertEqual(len(dirties), 1, "expected exactly one dagg-dirty")
        self.assertEqual(len(snapshots), 1, "expected exactly one dagg-snapshot")
        self.assertEqual(revisions[0], self.revision["commit"])
        self.assertEqual(dirties[0], "true" if self.revision["dirty"] else "false")
        self.assertEqual(snapshots[0], self.revision["snapshotId"])

        head_end = re.search(r"</head\s*>", text, re.IGNORECASE).start()
        for name in ("dagg-revision", "dagg-dirty", "dagg-snapshot"):
            self.assertLess(text.index('name="%s"' % name), head_end,
                            "%s must sit inside <head>, not in the body" % name)
        RESULTS["checks"]["domSnapshotMatchesEndpoint"] = True
        RESULTS["checks"]["metaInsideHeadOnly"] = True

    # -- 4. served HTML is the snapshot plus three meta tags -------------

    def test_04_stripping_the_meta_tags_restores_the_snapshot_bytes(self):
        source = (REPO_ROOT / HTML_PATH.lstrip("/")).read_bytes()
        committed = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "show",
             "HEAD:" + HTML_PATH.lstrip("/")],
            check=True, capture_output=True).stdout
        self.assertEqual(source, committed, "preview source must be unchanged")

        _, _, served = self.server.get(HTML_PATH)
        stripped = re.sub(
            r'<meta name="dagg-(?:revision|dirty|snapshot)"[^>]*>\n[ \t]*',
            "", served.decode("utf-8"))
        self.assertEqual(stripped, source.decode("utf-8"),
                         "served HTML differs from the snapshot beyond the metas")
        self.assertEqual(len(served) - len(source),
                         len(serve_preview.revision_meta(self.revision).encode()))
        RESULTS["checks"]["servedHtmlIsSnapshotPlusMetaOnly"] = True
        RESULTS["checks"]["visiblePreviewChanged"] = False

    # -- 5. the snapshot ID is reproducible from the declared algorithm --

    def test_05_snapshot_id_recomputes_from_the_declared_algorithm(self):
        digest, count, total = independent_snapshot_id(REPO_ROOT)
        self.assertEqual(digest, self.revision["snapshotId"],
                         "independently framed digest disagrees with the server")
        self.assertEqual(count, self.revision["snapshotFileCount"])
        self.assertEqual(total, self.revision["snapshotByteCount"])
        RESULTS["checks"]["snapshotIdIndependentlyRecomputed"] = True

    # -- 11. no-store on every content type ------------------------------

    def test_11_no_store_headers_on_every_content_type(self):
        for label, path in (("HTML", HTML_PATH), ("CSS", CSS_PATH),
                            ("JavaScript", JS_PATH), ("raster-image", IMAGE_PATH)):
            status, headers, body = self.server.get(path)
            self.assertEqual(status, 200)
            self.assert_no_store(headers, label)
        self.assert_no_store(self.revision_headers, "JSON")

        _, headers, body = self.server.get(CSS_PATH)
        self.assertIn("text/css", headers["Content-Type"])
        _, headers, _ = self.server.get(JS_PATH)
        self.assertIn("javascript", headers["Content-Type"])
        _, headers, body = self.server.get(IMAGE_PATH)
        self.assertEqual(headers["Content-Type"], "image/png")
        self.assertEqual(body[:8], b"\x89PNG\r\n\x1a\n", "not a real PNG payload")

        # The stylesheet actually linked by the page is the one measured.
        _, _, html = self.server.get(HTML_PATH)
        hrefs = re.findall(r'<link[^>]+href="([^"]+)"', html.decode("utf-8"))
        relative = [h for h in hrefs
                    if not h.startswith(("http:", "https:", "//", "#"))]
        self.assertTrue(relative, "no same-origin stylesheet found in the HTML")
        linked = urllib.parse.urlsplit(
            urllib.parse.urljoin("http://x" + HTML_PATH, relative[0])).path
        self.assertEqual(linked, CSS_PATH, "linked stylesheet is not the tested one")
        RESULTS["linkedCss"] = linked

    # -- 12. traversal, spaces, query strings, directory indexes ---------

    def test_12_traversal_spaces_queries_and_directory_indexes(self):
        for attempt in ("/../etc/passwd", "/preview/../../etc/passwd",
                        "/%2e%2e/%2e%2e/etc/passwd", "/preview/directions/../../../"):
            status, headers, _ = self.server.get(attempt)
            self.assertIn(status, (403, 404), "traversal %s returned %d"
                          % (attempt, status))
            self.assert_snapshot_headers(headers, "traversal refusal")
        self.assertIsNone(serve_preview.resolve_request_path("/../secrets.txt"))
        self.assertEqual(
            serve_preview.resolve_request_path(
                "/design/a%20file%20with%20spaces.md?v=2"),
            "design/a file with spaces.md")

        status, headers, body = self.server.get(HTML_PATH + "?v=cache-bust&x=1")
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "HTML")
        self.assertIn(b"dagg-snapshot", body)

        status, _, _ = self.server.get("/design/a%20file%20with%20spaces.md")
        self.assertEqual(status, 404)

        # A directory index is built from the frozen map, so it can only
        # list paths that are in the snapshot.
        status, headers, body = self.server.get("/assets/")
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "HTML")
        self.assert_snapshot_headers(headers, "directory index")
        listed = re.findall(r'<a href="([^"]+)"', body.decode("utf-8"))
        self.assertIn("img/", listed)
        self.assertIn("dagg-logotype-dark.png", listed)
        for name in listed:
            candidate = "assets/" + name.rstrip("/")
            self.assertTrue(
                candidate in serve_preview.list_candidate_paths(REPO_ROOT)
                or any(p.startswith(candidate + "/")
                       for p in serve_preview.list_candidate_paths(REPO_ROOT)),
                "directory index listed %s, which is not in the snapshot" % name)

        # Evidence is outside the served set by definition.
        status, _, _ = self.server.get("/evidence/P0/result.json")
        self.assertEqual(status, 404, "evidence must not be served")
        RESULTS["checks"]["traversalRefused"] = True
        RESULTS["checks"]["spacesAndQueryStrings"] = True
        RESULTS["checks"]["directoryIndexFromSnapshot"] = True
        RESULTS["checks"]["evidenceNotServed"] = True

    # -- 13. no server exceptions ----------------------------------------

    def test_13_server_raises_no_exceptions(self):
        """Drive success, refusal, 404, HEAD and directory paths through a
        dedicated process, then read its stderr. A handler traceback is a
        failure even when the client still received a response."""
        server = ServerProcess()
        try:
            probes = (HTML_PATH, CSS_PATH, JS_PATH, IMAGE_PATH, "/__revision",
                      "/assets/", "/", "/preview/", "/missing.html",
                      "/../etc/passwd", "/%2e%2e/etc/passwd",
                      HTML_PATH + "?v=1", "/design/a%20file%20with%20spaces.md",
                      "/evidence/P0/result.json", "/assets/img/")
            for path in probes:
                status, headers, _ = server.get(path)
                self.assertNotEqual(status, 500, "%s produced a 500" % path)
                self.assertIn("X-Dagg-Snapshot", headers,
                              "%s answered without a snapshot header" % path)
            request = urllib.request.Request(server.base + HTML_PATH, method="HEAD")
            with urllib.request.urlopen(request, timeout=20) as response:
                self.assertEqual(response.status, 200)
                self.assertIn("X-Dagg-Snapshot", dict(response.headers.items()))
        finally:
            stderr = server.stop()
        self.assertNotIn("Traceback", stderr, "server raised: %s" % stderr)
        RESULTS["checks"]["zeroServerExceptions"] = True
        RESULTS["probedPaths"] = list(probes) + ["HEAD " + HTML_PATH]

    # -- 14. startup time -------------------------------------------------

    def test_14_startup_is_under_two_seconds(self):
        self.assertLess(self.server.startup_seconds, 2.0,
                        "startup took %.3fs" % self.server.startup_seconds)
        RESULTS["startupSeconds"] = self.server.startup_seconds
        RESULTS["checks"]["startupUnderTwoSeconds"] = True


# --------------------------------------------------------------------------
# Mutation tests, all in throwaway repositories
# --------------------------------------------------------------------------


class ImmutabilityTest(unittest.TestCase):
    """Acceptance points 6-10. Never touches the Dagg worktree."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dagg-p0r1-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    # -- 6, 7. mutation during one server lifetime -----------------------

    def test_06_and_07_post_startup_mutation_cannot_reach_the_client(self):
        root = make_throwaway_repo(self.tmp / "probe")
        server = ServerProcess(root)
        try:
            first = server.revision()
            _, css_headers, css_before = server.get("/style.css")
            _, _, image_before = server.get("/logo.png")
            self.assertEqual(css_headers["X-Dagg-Snapshot"], first["snapshotId"])

            # Change a served CSS file, delete a snapshotted image and create
            # a new file, all while the server runs.
            (root / "style.css").write_text("body{color:#f00}\n")
            (root / "logo.png").unlink()
            (root / "late.html").write_text("<html><head></head><body>late</body></html>")

            _, headers_after, css_after = server.get("/style.css")
            self.assertEqual(css_after, css_before,
                             "a changed source file altered the response bytes")
            self.assertEqual(headers_after["X-Dagg-Snapshot"], first["snapshotId"])

            status, _, image_after = server.get("/logo.png")
            self.assertEqual(status, 200, "a deleted file stopped being served")
            self.assertEqual(image_after, image_before)

            status, headers, _ = server.get("/late.html")
            self.assertEqual(status, 404,
                             "a file created after startup became available")
            self.assertEqual(headers["X-Dagg-Snapshot"], first["snapshotId"])

            second = server.revision()
            self.assertEqual(second["snapshotId"], first["snapshotId"],
                             "the snapshot ID changed inside one process")
            self.assertEqual(second["snapshotFileCount"], first["snapshotFileCount"])
            self.assertEqual(second["snapshotByteCount"], first["snapshotByteCount"])
            self.snapshot_before_restart = first["snapshotId"]
        finally:
            stderr = server.stop()
        self.assertNotIn("Traceback", stderr)
        RESULTS["checks"]["changedFileCannotChangeResponse"] = True
        RESULTS["checks"]["deletedFileKeepsServing"] = True
        RESULTS["checks"]["createdFileIsNotServed"] = True

    # -- 8. restart is the only way to see changes -----------------------

    def test_08_restart_serves_the_new_snapshot(self):
        root = make_throwaway_repo(self.tmp / "probe")
        server = ServerProcess(root)
        try:
            before = server.revision()
            _, _, css_before = server.get("/style.css")
        finally:
            server.stop()

        (root / "style.css").write_text("body{color:#f00}\n")
        (root / "logo.png").unlink()
        (root / "late.html").write_text("<html><head></head><body>late</body></html>")

        server = ServerProcess(root)
        try:
            after = server.revision()
            _, _, css_after = server.get("/style.css")
            self.assertNotEqual(css_after, css_before,
                                "restart did not pick up the changed CSS")
            self.assertEqual(css_after, b"body{color:#f00}\n")

            status, _, _ = server.get("/logo.png")
            self.assertEqual(status, 404, "a deleted file survived restart")

            status, _, body = server.get("/late.html")
            self.assertEqual(status, 200, "a new file is still missing after restart")
            self.assertIn(b"late", body)

            self.assertNotEqual(after["snapshotId"], before["snapshotId"],
                                "a changed served set produced the same snapshot ID")
            self.assertIn("logo.png", after.get("snapshotSkippedPaths", []))
        finally:
            stderr = server.stop()
        self.assertNotIn("Traceback", stderr)
        RESULTS["checks"]["restartProducesNewSnapshot"] = True

    # -- 9. evidence is outside the snapshot -----------------------------

    def test_09_evidence_files_do_not_change_the_snapshot_id(self):
        root = make_throwaway_repo(self.tmp / "probe")
        server = ServerProcess(root)
        try:
            before = server.revision()["snapshotId"]
        finally:
            server.stop()

        evidence = root / "evidence" / "P0R1"
        evidence.mkdir(parents=True)
        (evidence / "result.json").write_text('{"written": "after startup"}\n')
        (evidence / "shot.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x01" * 128)

        server = ServerProcess(root)
        try:
            after = server.revision()
            self.assertEqual(after["snapshotId"], before,
                             "evidence files entered the served set")
            status, _, _ = server.get("/evidence/P0R1/result.json")
            self.assertEqual(status, 404, "evidence must not be served")
        finally:
            server.stop()
        RESULTS["checks"]["evidenceExcludedFromSnapshot"] = True

    # -- 10. truthful dirty state ----------------------------------------

    def test_10_dirty_state_is_truthful_at_snapshot_start(self):
        clean_root = make_throwaway_repo(self.tmp / "clean")
        server = ServerProcess(clean_root)
        try:
            clean = server.revision()
        finally:
            server.stop()
        self.assertFalse(clean["dirty"], "a clean repository reported dirty")
        self.assertEqual(clean["commit"], git("rev-parse", "HEAD", cwd=clean_root))

        dirty_root = make_throwaway_repo(self.tmp / "dirty", dirty=True)
        server = ServerProcess(dirty_root)
        try:
            dirty = server.revision()
        finally:
            server.stop()
        self.assertTrue(dirty["dirty"], "a dirty repository reported clean")
        self.assertEqual(dirty["commit"], git("rev-parse", "HEAD", cwd=dirty_root))
        self.assertNotEqual(dirty["snapshotId"], clean["snapshotId"],
                            "a dirty tree produced the clean snapshot ID")
        RESULTS["checks"]["dirtyReportingHonest"] = True


# --------------------------------------------------------------------------
# Scope
# --------------------------------------------------------------------------


class ScopeTest(unittest.TestCase):
    """Acceptance point 15. Proves P0R1 touched only what it owns."""

    def test_15_only_owned_files_differ_from_the_base_commit(self):
        committed = [p for p in git("diff", "--name-only",
                                    "%s...HEAD" % BASE_COMMIT).splitlines() if p]
        working = []
        for line in git_raw("status", "--porcelain").splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            working.append(path.strip('"'))

        for path in committed + working:
            self.assertTrue(is_owned(path), "out-of-scope file changed: %s" % path)
            self.assertFalse(is_public(path),
                             "public source file changed: %s" % path)

        public_diff = [p for p in git(
            "diff", "--name-only", "%s...HEAD" % BASE_COMMIT, "--",
            "preview", "assets", "marketing", "v1", "index.html",
            "robots.txt").splitlines() if p]
        self.assertEqual(public_diff, [], "public source differs from the base")

        RESULTS["committedDiffVersusBase"] = committed
        RESULTS["workingTreeChanges"] = working
        RESULTS["checks"]["onlyOwnedFilesChanged"] = True
        RESULTS["checks"]["noPublicSourceChanged"] = True


def _write_results():
    target = os.environ.get("DAGG_P0R1_TEST_JSON")
    if not target:
        return
    RESULTS["coverage"] = sorted(RESULTS["coverage"])
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_text(json.dumps(RESULTS, indent=2, sort_keys=True) + "\n")


# Registered at import so the summary is written under `unittest discover`
# as well as under direct execution.
atexit.register(_write_results)


if __name__ == "__main__":
    unittest.main(verbosity=2)
