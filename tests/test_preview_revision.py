#!/usr/bin/env python3
"""Exact-revision preview tests.

Proves that the revision-safe preview server cannot serve a mixed-revision
page: HTML, CSS, JavaScript and a raster image all arrive with no-store
headers from one server process, and the revision reported by
``/__revision``, by the injected DOM metadata and by ``git rev-parse HEAD``
is the same commit.

Coverage: HTML, CSS, JavaScript, raster image (PNG), directory traversal,
percent-encoded spaces, query strings, clean/dirty revision reporting and
server exceptions. Standard library only.

    python3 -B -m unittest discover -s tests -v
"""

from __future__ import annotations

import atexit
import json
import os
import re
import subprocess
import sys
import tempfile
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

HTML_PATH = "/preview/directions/a-plus.html"
JS_PATH = "/preview/site/site.js"
IMAGE_PATH = "/assets/dagg-logotype-dark.png"

REQUIRED_NO_STORE = {
    "cache-control": "no-store, max-age=0",
    "pragma": "no-cache",
    "expires": "0",
}

# Filled in as tests run, written out when DAGG_P0_TEST_JSON is set.
RESULTS: dict = {"checks": {}, "coverage": [], "notes": []}


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(cwd), *args],
        check=True, capture_output=True, text=True).stdout.strip()


class ServerProcess:
    """The real CLI, started on an available local port."""

    def __init__(self):
        self.proc = subprocess.Popen(
            [sys.executable, "-B", str(TOOLS / "serve_preview.py"),
             "--port", "0", "--quiet"],
            cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True)
        line = self.proc.stdout.readline().strip()
        if not line.startswith("LISTENING "):
            raise RuntimeError("server did not announce a port: %r" % line)
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


class PreviewRevisionTest(unittest.TestCase):
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

    # -- revision endpoint ----------------------------------------------

    def test_01_revision_endpoint_fields(self):
        for field in ("commit", "abbreviatedCommit", "branch", "dirty",
                      "serverStartedAt", "repositoryRoot"):
            self.assertIn(field, self.revision)
        self.assertIsInstance(self.revision["dirty"], bool)
        self.assertEqual(self.revision["repositoryRoot"], str(REPO_ROOT))
        self.assertTrue(self.revision["commit"].startswith(
            self.revision["abbreviatedCommit"]))
        RESULTS["checks"]["revisionEndpointFields"] = True

    def test_02_revision_matches_git_head(self):
        self.assertEqual(self.revision["commit"], self.head_commit)
        RESULTS["checks"]["revisionEndpointMatchesGit"] = True
        RESULTS["commit"] = self.head_commit

    def test_03_dirty_state_matches_git(self):
        self.assertEqual(self.revision["dirty"], bool(self.porcelain))
        RESULTS["checks"]["dirtyStateMatchesGit"] = True
        RESULTS["dirty"] = self.revision["dirty"]

    def test_04_revision_reporting_is_honest_on_a_clean_tree(self):
        """A clean checkout must report dirty=false and a dirty one true.

        Uses a throwaway repository in a temporary directory; this
        repository is never mutated.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "probe"
            root.mkdir()
            git("init", "-q", "-b", "probe", cwd=root)
            git("config", "user.email", "p0@example.invalid", cwd=root)
            git("config", "user.name", "P0", cwd=root)
            (root / "a.txt").write_text("one\n")
            git("add", "a.txt", cwd=root)
            git("commit", "-q", "-m", "one", cwd=root)

            clean = serve_preview.read_revision(root.resolve())
            self.assertFalse(clean["dirty"])
            self.assertEqual(clean["commit"], git("rev-parse", "HEAD", cwd=root))

            (root / "a.txt").write_text("two\n")
            dirty = serve_preview.read_revision(root.resolve())
            self.assertTrue(dirty["dirty"])
            self.assertEqual(dirty["commit"], clean["commit"])
        RESULTS["checks"]["dirtyReportingHonest"] = True

    # -- HTML + injected metadata ---------------------------------------

    def test_05_html_no_store_and_single_meta_pair(self):
        status, headers, body = self.server.get(HTML_PATH)
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "HTML")
        text = body.decode("utf-8")

        revisions = re.findall(
            r'<meta name="dagg-revision" content="([0-9a-f]{40})">', text)
        dirties = re.findall(
            r'<meta name="dagg-dirty" content="(true|false)">', text)
        self.assertEqual(len(revisions), 1, "expected exactly one dagg-revision meta")
        self.assertEqual(len(dirties), 1, "expected exactly one dagg-dirty meta")

        self.assertEqual(revisions[0], self.revision["commit"])
        self.assertEqual(dirties[0], "true" if self.revision["dirty"] else "false")
        RESULTS["checks"]["domRevisionMatchesEndpoint"] = True

    def test_06_meta_is_inside_head_only(self):
        _, _, body = self.server.get(HTML_PATH)
        text = body.decode("utf-8")
        head_end = re.search(r"</head\s*>", text, re.IGNORECASE).start()
        for name in ("dagg-revision", "dagg-dirty"):
            index = text.index('name="%s"' % name)
            self.assertLess(index, head_end,
                            "%s must sit inside <head>, not in the body" % name)
        RESULTS["checks"]["metaInsideHeadOnly"] = True

    def test_07_source_html_is_not_modified(self):
        """Injection happens in memory: on disk the file still matches HEAD,
        and the served bytes differ only by the two meta lines."""
        source = (REPO_ROOT / HTML_PATH.lstrip("/")).read_bytes()
        committed = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(REPO_ROOT), "show",
             "HEAD:" + HTML_PATH.lstrip("/")],
            check=True, capture_output=True).stdout
        self.assertEqual(source, committed, "preview source must be unchanged")

        _, _, served = self.server.get(HTML_PATH)
        # Removing the two injected meta tags must restore the source byte
        # for byte: nothing else in the document was touched.
        stripped = re.sub(r'<meta name="dagg-(?:revision|dirty)"[^>]*>\n[ \t]*',
                          "", served.decode("utf-8"))
        self.assertEqual(stripped, source.decode("utf-8"),
                         "served HTML differs from source beyond the meta pair")
        self.assertEqual(len(served) - len(source),
                         len(serve_preview.revision_meta(self.revision).encode()))
        RESULTS["checks"]["servedHtmlIsSourcePlusMetaOnly"] = True
        RESULTS["checks"]["visiblePreviewChanged"] = False

    # -- linked CSS, JS, image ------------------------------------------

    def test_08_linked_css_is_fetched_from_the_same_server(self):
        _, _, body = self.server.get(HTML_PATH)
        hrefs = re.findall(r'<link[^>]+href="([^"]+)"', body.decode("utf-8"))
        relative = [h for h in hrefs if not h.startswith(("http:", "https:", "//", "#"))]
        self.assertTrue(relative, "no same-origin stylesheet found in the HTML")

        base = urllib.parse.urljoin("http://x" + HTML_PATH, relative[0])
        css_path = urllib.parse.urlsplit(base).path
        self.assertTrue(css_path.endswith("tokens.css"), css_path)

        status, headers, css = self.server.get(css_path)
        self.assertEqual(status, 200, "linked CSS %s not served" % css_path)
        self.assert_no_store(headers, "CSS")
        self.assertIn("text/css", headers["Content-Type"])
        self.assertGreater(len(css), 0)
        RESULTS["linkedCss"] = css_path

    def test_09_javascript_no_store(self):
        status, headers, body = self.server.get(JS_PATH)
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "JavaScript")
        self.assertIn("javascript", headers["Content-Type"])
        self.assertGreater(len(body), 0)

    def test_10_raster_image_no_store(self):
        status, headers, body = self.server.get(IMAGE_PATH)
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "raster-image")
        self.assertEqual(headers["Content-Type"], "image/png")
        self.assertEqual(body[:8], b"\x89PNG\r\n\x1a\n", "not a real PNG payload")

    def test_11_revision_endpoint_no_store(self):
        self.assert_no_store(self.revision_headers, "JSON")

    # -- path handling ---------------------------------------------------

    def test_12_path_traversal_is_refused(self):
        for attempt in ("/../etc/passwd", "/preview/../../etc/passwd",
                        "/%2e%2e/%2e%2e/etc/passwd", "/preview/directions/../../../"):
            status, _, _ = self.server.get(attempt)
            self.assertIn(status, (403, 404), "traversal %s returned %d"
                          % (attempt, status))
        self.assertIsNone(
            serve_preview.resolve_request_path(REPO_ROOT, "/../secrets.txt"))
        RESULTS["checks"]["traversalRefused"] = True

    def test_13_query_strings_and_spaces(self):
        status, headers, body = self.server.get(HTML_PATH + "?v=cache-bust&x=1")
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "HTML")
        self.assertIn(b"dagg-revision", body)

        # A percent-encoded space resolves to the intended name, and a
        # missing file is a clean 404 rather than an exception.
        resolved = serve_preview.resolve_request_path(
            REPO_ROOT, "/design/a%20file%20with%20spaces.md?v=2")
        self.assertEqual(resolved, REPO_ROOT / "design" / "a file with spaces.md")
        status, _, _ = self.server.get("/design/a%20file%20with%20spaces.md")
        self.assertEqual(status, 404)
        RESULTS["checks"]["spacesAndQueryStrings"] = True

    def test_14_fresh_bytes_after_a_local_change(self):
        """A changed file is re-read on the next request; nothing is cached."""
        probe = REPO_ROOT / "evidence" / "P0" / "_freshness-probe.html"
        probe.parent.mkdir(parents=True, exist_ok=True)
        try:
            probe.write_text("<html><head><title>one</title></head><body>one</body></html>")
            _, _, first = self.server.get("/evidence/P0/_freshness-probe.html")
            self.assertIn(b"one", first)
            probe.write_text("<html><head><title>two</title></head><body>two</body></html>")
            _, _, second = self.server.get("/evidence/P0/_freshness-probe.html")
            self.assertIn(b"two", second)
            self.assertNotIn(b">one<", second)
            self.assertIn(b"dagg-revision", second)
        finally:
            probe.unlink(missing_ok=True)
        RESULTS["checks"]["freshBytesAfterChange"] = True

    def test_15_directory_index_is_served_with_no_store(self):
        status, headers, body = self.server.get("/preview/directions/")
        self.assertEqual(status, 200)
        self.assert_no_store(headers, "HTML")
        self.assertIn(b"dagg-revision", body)


def _write_results():
    target = os.environ.get("DAGG_P0_TEST_JSON")
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
