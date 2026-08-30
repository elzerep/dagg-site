#!/usr/bin/env python3
"""Immutable-snapshot preview tests.

Proves that one preview process serves exactly one workspace moment. HTML,
CSS, JavaScript, raster image and JSON all carry the same snapshot ID as
``/__revision``; the snapshot ID is independently recomputed here from the
framed algorithm declared in P0R1; and changing, deleting or creating source
files while a server runs cannot alter a single served byte. Restarting
after those changes is proved to be the only way to see them, and to produce
a different snapshot ID.

P0R2 adds the acquisition half of the same guarantee: the workspace must be
read twice with identical results before a socket exists. A repository that
changes between the two passes is rejected, a repository that stops changing
is accepted on a later pair, and a repository that never stops is refused
with no listening port at all. Those races are driven through the
``acquire`` seam of ``acquire_consistent``, never through sleeps, so they
fail or pass for one reason only.

Coverage: HTML, CSS, JavaScript, raster image (PNG), JSON, directory
indexes, traversal refusal, percent-encoded spaces, query strings,
clean/dirty reporting, two-pass acquisition agreement, mid-acquisition byte
change, mid-acquisition status change, continuous-change refusal,
post-startup mutation, restart behaviour, evidence exclusion, startup time,
owned-file scope and server exceptions. The Dagg worktree is never mutated:
every mutation test runs in a throwaway Git repository under a temporary
directory. Standard library only.

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

BASE_COMMIT = "9e0a670a9689a16ce4641c86b5e92a320da0e9f6"

HTML_PATH = "/preview/directions/a-plus.html"
CSS_PATH = "/preview/directions/tokens.css"
JS_PATH = "/preview/site/site.js"
IMAGE_PATH = "/assets/dagg-logotype-dark.png"

REQUIRED_NO_STORE = {
    "cache-control": "no-store, max-age=0",
    "pragma": "no-cache",
    "expires": "0",
}

# Everything P0R2 is allowed to create or change, taken verbatim from the
# package. Anything else in the diff or in the working tree is a scope
# failure, not a detail.
OWNED_PATHS = {
    "README.md",
    "design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md",
    "design/golden-standard/packages/P0R1-IMMUTABLE-PREVIEW-SNAPSHOT.md",
    "design/golden-standard/packages/P0R2-CONSISTENT-SNAPSHOT-ACQUISITION.md",
    "tools/serve_preview.py",
    "tools/capture_preview_evidence.py",
    "tests/test_preview_revision.py",
    "evidence/P0R1/REJECTED-BY-CODEX.md",
}
OWNED_PREFIXES = ("evidence/P0R2/",)

PUBLIC_PREFIXES = ("preview/", "assets/", "marketing/", "v1/")
PUBLIC_FILES = {"index.html", "robots.txt"}

# Filled in as tests run, written out when DAGG_P0R2_TEST_JSON is set.
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
        """Measured on the running CLI, so the second acquisition pass is
        inside the number."""
        self.assertLess(self.server.startup_seconds, 2.0,
                        "startup took %.3fs" % self.server.startup_seconds)
        RESULTS["startupSeconds"] = self.server.startup_seconds
        RESULTS["checks"]["startupUnderTwoSeconds"] = True

    # -- 16. the accepted snapshot is declared as two agreeing passes ------

    def test_16_accepted_snapshot_declares_its_consistency(self):
        """P0R2 point 7 on the live repository: the endpoint, every response
        header and the HTML meta all carry the one accepted snapshot ID, and
        the endpoint says how that snapshot was accepted."""
        self.assertEqual(self.revision["snapshotConsistencyPasses"], 2)
        self.assertEqual(self.revision["snapshotAcquisitionStable"], True)
        self.assertIsInstance(self.revision["snapshotAcquisitionAttempts"], int)
        self.assertGreaterEqual(self.revision["snapshotAcquisitionAttempts"], 1)
        self.assertLessEqual(self.revision["snapshotAcquisitionAttempts"],
                             serve_preview.MAX_ACQUISITION_ATTEMPTS)

        for label, path in (("HTML", HTML_PATH), ("CSS", CSS_PATH),
                            ("JavaScript", JS_PATH), ("raster-image", IMAGE_PATH),
                            ("JSON", "/__revision"), ("directory", "/assets/"),
                            ("missing", "/missing.html")):
            _, headers, _ = self.server.get(path)
            self.assertEqual({k.lower(): v for k, v in headers.items()}
                             ["x-dagg-snapshot"], self.revision["snapshotId"],
                             "%s left the accepted snapshot" % label)
        _, _, html = self.server.get(HTML_PATH)
        self.assertIn('content="%s"' % self.revision["snapshotId"],
                      html.decode("utf-8"))

        RESULTS["snapshotConsistencyPasses"] = \
            self.revision["snapshotConsistencyPasses"]
        RESULTS["snapshotAcquisitionAttempts"] = \
            self.revision["snapshotAcquisitionAttempts"]
        RESULTS["snapshotAcquisitionStable"] = \
            self.revision["snapshotAcquisitionStable"]
        RESULTS["checks"]["acceptedSnapshotDeclaresTwoPasses"] = True
        RESULTS["checks"]["oneAcceptedSnapshotAcrossEverySurface"] = True


# --------------------------------------------------------------------------
# Mutation tests, all in throwaway repositories
# --------------------------------------------------------------------------


class ImmutabilityTest(unittest.TestCase):
    """Acceptance points 6-10. Never touches the Dagg worktree."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dagg-p0r2-"))
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
# Consistent acquisition, all in throwaway repositories
# --------------------------------------------------------------------------


# Runs the real CLI with one seam replaced, so the refusal path is proved on
# a real process rather than on an in-process call. The seam changes the
# throwaway repository after every complete pass, which makes the outcome a
# property of the code and not of how fast the machine happens to be.
CONTINUOUS_CHANGE_DRIVER = (
    "import sys\n"
    "sys.dont_write_bytecode = True\n"
    "sys.path.insert(0, %r)\n"
    "from pathlib import Path\n"
    "import serve_preview\n"
    "_complete_pass = serve_preview.acquire_once\n"
    "_writes = [0]\n"
    "def always_changing(repo_root):\n"
    "    result = _complete_pass(repo_root)\n"
    "    _writes[0] += 1\n"
    "    (Path(repo_root) / 'style.css').write_text(\n"
    "        'body{color:#111}/*' + str(_writes[0]) + '*/\\n')\n"
    "    return result\n"
    "serve_preview.acquire_once = always_changing\n"
    "raise SystemExit(serve_preview.main(sys.argv[1:]))\n"
) % str(TOOLS)


class AcquisitionConsistencyTest(unittest.TestCase):
    """P0R2 points 1-5. The workspace must be read twice with identical
    results before anything can be served, and the race is driven through
    the ``acquire`` seam so no test depends on elapsed time."""

    # These tests call the acquisition functions directly instead of going
    # through the CLI, so they must resolve the throwaway root themselves.
    # ``find_repo_root`` does that for every real start, which is why the
    # macOS ``/var`` symlink never reaches production.
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="dagg-p0r2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    # -- 17. a stable repository is accepted on the first pair ------------

    def test_17_stable_repository_is_accepted_on_the_first_pair(self):
        root = make_throwaway_repo(self.tmp / "probe")
        server = ServerProcess(root)
        try:
            revision = server.revision()
        finally:
            stderr = server.stop()
        self.assertEqual(revision["snapshotConsistencyPasses"], 2)
        self.assertEqual(revision["snapshotAcquisitionAttempts"], 1)
        self.assertIs(revision["snapshotAcquisitionStable"], True)
        self.assertEqual(revision["snapshotRejectedPairs"], [])
        self.assertIn("stable after 1 attempt(s)", stderr)
        self.assertNotIn("Traceback", stderr)
        RESULTS["checks"]["stableRepositoryAcceptedOnFirstPair"] = True

    # -- 18. bytes that change between the passes are rejected ------------

    def test_18_bytes_changing_between_passes_are_rejected_then_settle(self):
        """One write lands between pass A and pass B. That pair must die,
        and the pair after it must carry only the final bytes."""
        root = make_throwaway_repo(self.tmp / "probe").resolve()
        final_css = b"body{color:#0f0}\n"
        passes: list = []

        def write_between_the_passes(repo_root: Path):
            completed = serve_preview.acquire_once(repo_root)
            passes.append(completed)
            if len(passes) == 1:
                (repo_root / "style.css").write_bytes(final_css)
            return completed

        accepted, attempts, per_attempt = serve_preview.acquire_consistent(
            root, acquire=write_between_the_passes)

        self.assertEqual(attempts, 2, "the changed pair was not retried")
        self.assertEqual(len(passes), 4, "an attempt is not two complete passes")
        # The replacement CSS is the same length as the original, so the
        # byte count cannot catch this edit. The digest and the direct byte
        # comparison have to, and the status has to move with them.
        self.assertEqual(len(final_css), len(passes[0].files["style.css"]))
        self.assertEqual(per_attempt[0],
                         ["status", "dirtyEntryCount", "snapshotId",
                          "frozenBytes"])
        self.assertEqual(per_attempt[1], [], "the accepted pair disagreed")

        # Nothing from the discarded pair survives into the accepted value.
        self.assertEqual(accepted.files["style.css"], final_css)
        self.assertEqual(accepted.snapshot_id, passes[3].snapshot_id)
        self.assertNotEqual(accepted.snapshot_id, passes[0].snapshot_id)
        self.assertTrue(accepted.dirty, "the accepted pass hid the edit")
        self.assertEqual(accepted.status_raw, passes[3].status_raw)
        RESULTS["checks"]["midAcquisitionByteChangeRejected"] = True
        RESULTS["checks"]["retryAcceptsOnlyFinalBytes"] = True

    # -- 19. status that changes between the passes is rejected -----------

    def test_19_status_changing_between_passes_is_rejected(self):
        """Staging an already-modified file leaves every served byte and the
        snapshot ID untouched and moves only the porcelain columns. The pair
        must still die, or status and bytes could come from different reads."""
        root = make_throwaway_repo(self.tmp / "probe", dirty=True).resolve()
        passes: list = []

        def stage_between_the_passes(repo_root: Path):
            completed = serve_preview.acquire_once(repo_root)
            passes.append(completed)
            if len(passes) == 1:
                git("add", "style.css", cwd=repo_root)
            return completed

        accepted, attempts, per_attempt = serve_preview.acquire_consistent(
            root, acquire=stage_between_the_passes)

        self.assertEqual(per_attempt[0], ["status"],
                         "the rejection was not attributed to raw status alone")
        self.assertEqual(passes[0].snapshot_id, passes[1].snapshot_id,
                         "this test only proves its point if the bytes match")
        self.assertEqual(dict(passes[0].files), dict(passes[1].files))
        self.assertEqual(attempts, 2)
        self.assertEqual(accepted.status_raw, passes[3].status_raw)
        self.assertTrue(accepted.status_raw.startswith(b"M "),
                        "expected the staged status, got %r" % accepted.status_raw)
        RESULTS["checks"]["midAcquisitionStatusChangeRejected"] = True

    # -- 20. continuous change is refused, with no socket at all ----------

    def test_20_continuous_change_refuses_before_any_socket_exists(self):
        root = make_throwaway_repo(self.tmp / "probe").resolve()
        writes = [0]

        def always_changing(repo_root: Path):
            completed = serve_preview.acquire_once(repo_root)
            writes[0] += 1
            (repo_root / "style.css").write_bytes(
                b"body{color:#111}/*%d*/\n" % writes[0])
            return completed

        # A tripwire in place of the server class: if acquisition ever gives
        # up and binds, the test fails on construction rather than on a
        # missing assertion later.
        created: list = []

        class Tripwire(serve_preview.PreviewServer):
            def __init__(self, *args, **kwargs):
                created.append(args)
                raise AssertionError("a socket was created for a changing "
                                     "workspace")

        original = serve_preview.PreviewServer
        serve_preview.PreviewServer = Tripwire
        try:
            with self.assertRaises(serve_preview.SnapshotError) as raised:
                serve_preview.build_server(root, "127.0.0.1", 0, True,
                                           acquire=always_changing)
        finally:
            serve_preview.PreviewServer = original

        self.assertEqual(created, [], "a socket was created before refusing")
        self.assertEqual(writes[0], serve_preview.MAX_ACQUISITION_ATTEMPTS * 2,
                         "the bound on pair attempts is not three")
        self.assertIn("changed while it was being read", str(raised.exception))

        # The same refusal through the real CLI, one process, one seam.
        driver = self.tmp / "continuous_change_driver.py"
        driver.write_text(CONTINUOUS_CHANGE_DRIVER)
        completed = subprocess.run(
            [sys.executable, "-B", str(driver), "--port", "0", "--quiet",
             "--repo-root", str(root)],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=120)
        self.assertEqual(completed.returncode, 2,
                         "the CLI did not exit non-zero: %s" % completed.stderr)
        self.assertNotIn("LISTENING", completed.stdout,
                         "the CLI announced a port for a changing workspace")
        self.assertEqual(completed.stdout.strip(), "")
        self.assertIn("snapshot refused", completed.stderr)
        self.assertIn("changed while it was being read", completed.stderr)
        RESULTS["checks"]["continuousChangeRefused"] = True
        RESULTS["checks"]["noSocketOnRefusal"] = True
        RESULTS["checks"]["noListeningLineOnRefusal"] = True
        RESULTS["acquisitionRefusalStderr"] = completed.stderr.strip()

    # -- 21. the accepted pass is independently reproducible --------------

    def test_21_accepted_pass_is_independently_recomputed(self):
        root = make_throwaway_repo(self.tmp / "probe", dirty=True).resolve()
        accepted, attempts, _ = serve_preview.acquire_consistent(root)
        digest, count, total = independent_snapshot_id(root)
        self.assertEqual(digest, accepted.snapshot_id)
        self.assertEqual(count, accepted.file_count)
        self.assertEqual(total, accepted.byte_count)
        for relative, content in accepted.files.items():
            self.assertEqual(content, (root / relative).read_bytes(),
                             "accepted bytes differ from disk for %s" % relative)
        self.assertEqual(attempts, 1)
        self.assertEqual(accepted.status_raw,
                         git_raw("status", "--porcelain", cwd=root).encode("utf-8"))
        RESULTS["checks"]["acceptedPassIndependentlyRecomputed"] = True

    # -- 22. two passes still start in well under two seconds -------------

    def test_22_two_pass_acquisition_of_the_real_repository_is_fast(self):
        """Point 8, measured on the real 20-25 MB repository rather than on
        a throwaway one."""
        started = time.monotonic()
        accepted, attempts, _ = serve_preview.acquire_consistent(REPO_ROOT)
        seconds = round(time.monotonic() - started, 3)
        self.assertLess(seconds, 2.0,
                        "two-pass acquisition took %.3fs" % seconds)
        self.assertGreater(accepted.byte_count, 0)
        RESULTS["twoPassAcquisitionSeconds"] = seconds
        RESULTS["twoPassAcquisitionAttempts"] = attempts
        RESULTS["checks"]["twoPassAcquisitionUnderTwoSeconds"] = True


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
    target = os.environ.get("DAGG_P0R2_TEST_JSON")
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
