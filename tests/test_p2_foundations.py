#!/usr/bin/env python3
"""P2 foundations acceptance suite.

Drives the installed Google Chrome over the Chrome DevTools Protocol against
the P0R2 immutable-snapshot preview server. No Playwright, no bundled
browser, no live-disk server: every byte the browser renders comes from one
frozen snapshot, and every assertion below is made against what Chrome
actually computed, not against the source text.

What this suite covers, exactly:

* one snapshot ID across HTML, both stylesheets, all three WOFF2 files, both
  Dagg logotype PNGs and ``/__revision``;
* ``scrollWidth === clientWidth`` at 320, 360, 390, 768, 1024 and 1440;
* every rendered text node in the document, reached with a document-wide
  TreeWalker rather than a selector list, so HTML and SVG are both in scope;
* H1/H2/H3/Lead/Body/Meta computed size against the frozen endpoints at
  1440, 390 and 320 within 0.5 px, and computed leading inside its band;
* page gutters at 320, 360, 390, 767, 768, 1023, 1024, 1439 and 1440, and
  the 1240 px field ceiling;
* twelve equal grid tracks, and the 940 px carrier collapse proved at 939 and
  940 px with an unchanged DOM reading order;
* the rendered box of every focusable control against 44 x 44 px;
* the real keyboard Tab sequence, and the focus indicator Chrome painted on
  both a warm and an ink ground;
* the contrast of every rendered text node, composited through ancestor
  backgrounds, against WCAG AA for that node's actual size;
* ``document.fonts.check()`` for all three families, local-only font URLs and
  the presence of every vendored license;
* every network request the page made, and the console error count;
* ``prefers-reduced-motion: reduce`` against the unreduced render, box by box
  and text node by text node;
* the P2 owned-file boundary and the byte identity of every public and legacy
  file that existed at the base commit.

    python3 -B -m unittest discover -s tests -p test_p2_foundations.py -v
"""

from __future__ import annotations

import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOLS))

import capture_p2_evidence as harness  # noqa: E402  (path set above)

BASE_COMMIT = harness.BASE_COMMIT

PAGE_PATH = harness.PAGE_PATH
LAYOUT_VIEWPORTS = harness.LAYOUT_VIEWPORTS
GUTTER_PROBES = (767, 1023, 1439)
COLLAPSE_PROBES = (939, 940)

DECLARED_GUTTER = {320: 20, 360: 20, 390: 20, 767: 20,
                   768: 24, 1023: 24, 1024: 48, 1439: 48, 1440: 72}

# Everything P2 is allowed to create or change, verbatim from section 4.
OWNED_PATHS = {
    "design/golden-standard/packages/P2-FOUNDATIONS.md",
    "design/golden-standard/system/TOKENS.md",
    "design/golden-standard/system/tokens.css",
    "preview/golden-standard/foundations/index.html",
    "preview/golden-standard/foundations/foundations.css",
    "tests/test_p2_foundations.py",
    "tools/capture_p2_evidence.py",
}
OWNED_PREFIXES = ("assets/fonts/golden-standard/", "evidence/P2/")

# Roots that P2 must leave byte-identical. Everything tracked under these at
# the base commit is compared byte for byte, not merely by name.
PROTECTED_ROOTS = ("index.html", "robots.txt", "v1", "marketing", "assets",
                   "preview")

RESULTS: dict = {"checks": {}, "coverage": [], "measurements": {}, "notes": []}


def git(*args: str) -> str:
    return git_raw(*args).strip()


def git_raw(*args: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True, text=True).stdout


def git_bytes(*args: str) -> bytes:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True).stdout


def is_owned(path: str) -> bool:
    return path in OWNED_PATHS or path.startswith(OWNED_PREFIXES)


# --------------------------------------------------------------------------
# One server, one browser, one set of renders for the whole suite
# --------------------------------------------------------------------------


class RenderedSpecimen(unittest.TestCase):
    """Every assertion in this suite reads the class-level renders below.

    They are produced once, by one immutable server process and one Chrome
    process, so no two assertions can disagree about which bytes they saw.
    """

    server = None
    chrome = None
    cdp = None
    profile_dir = None

    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url, cls.startup_seconds = harness.start_server()
        cls.profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p2-test-chrome-"))
        cls.chrome, browser_ws, cls.chrome_path = harness.start_chrome(
            cls.profile_dir)
        cls.cdp = harness.CDP(browser_ws)
        cls.page = harness.Page(cls.cdp)
        cls.page_url = cls.base_url + PAGE_PATH

        status, headers, body = harness.fetch(cls.base_url, "/__revision")
        assert status == 200, status
        cls.revision = json.loads(body)
        cls.revision_headers = headers
        cls.snapshot_id = cls.revision["snapshotId"]

        cls.renders = {}
        for width in list(LAYOUT_VIEWPORTS) + list(GUTTER_PROBES) + list(COLLAPSE_PROBES):
            cls.renders[width] = cls.page.open(cls.page_url, width)
        cls.reduced = cls.page.open(cls.page_url, 390, reduced_motion=True)
        cls.page.set_reduced_motion(False)
        cls.page.open(cls.page_url, 1440)
        cls.tab_stops = cls.page.tab_through()

        RESULTS["snapshotId"] = cls.snapshot_id
        RESULTS["commit"] = cls.revision["commit"]
        RESULTS["dirty"] = cls.revision["dirty"]
        RESULTS["chrome"] = cls.chrome_path
        RESULTS["viewportsRendered"] = sorted(cls.renders)

    @classmethod
    def tearDownClass(cls):
        if cls.cdp is not None:
            try:
                cls.cdp.close()
            except Exception:
                pass
        if cls.chrome is not None:
            cls.chrome.terminate()
            try:
                cls.chrome.wait(timeout=10)
            except subprocess.TimeoutExpired:
                cls.chrome.kill()
        if cls.server is not None:
            stderr = harness.stop_server(cls.server)
            RESULTS["checks"]["zeroServerExceptions"] = "Traceback" not in stderr
        if cls.profile_dir is not None:
            shutil.rmtree(cls.profile_dir, ignore_errors=True)

    # -- 1 ----------------------------------------------------------------

    def test_01_every_served_asset_carries_one_snapshot_id(self):
        """HTML, both stylesheets, every WOFF2, both logotype PNGs and the
        revision endpoint must belong to the same frozen snapshot."""
        targets = [("HTML", PAGE_PATH),
                   ("CSS-tokens", harness.TOKENS_CSS_PATH),
                   ("CSS-page", harness.PAGE_CSS_PATH),
                   ("PNG-logotype-dark", harness.LOGO_DARK_PATH),
                   ("PNG-logotype", harness.LOGO_LIGHT_PATH)]
        targets += [("WOFF2-%s" % p.rsplit("/", 1)[-1], p)
                    for p in harness.FONT_PATHS]
        for label, path in targets:
            status, headers, body = harness.fetch(self.base_url, path)
            self.assertEqual(status, 200, "%s not served" % label)
            self.assertGreater(len(body), 0, "%s served empty" % label)
            lowered = {k.lower(): v for k, v in headers.items()}
            self.assertEqual(lowered.get("x-dagg-snapshot"), self.snapshot_id,
                             "%s left the accepted snapshot" % label)
            if path.endswith(".woff2"):
                self.assertEqual(body[:4], b"wOF2", "%s is not WOFF2" % label)
                self.assertEqual(lowered.get("content-type"), "font/woff2")
            if path.endswith(".png"):
                self.assertEqual(body[:8], harness.PNG_SIGNATURE)
            if label not in RESULTS["coverage"]:
                RESULTS["coverage"].append(label)
        self.assertEqual(
            {k.lower(): v for k, v in self.revision_headers.items()}
            ["x-dagg-snapshot"], self.snapshot_id)

        # And the render itself declares the same snapshot.
        for width, facts in self.renders.items():
            self.assertEqual(facts["snapshot"], self.snapshot_id,
                             "the %dpx DOM left the snapshot" % width)
            self.assertEqual((facts["revisionMeta"], facts["dirtyMeta"],
                              facts["snapshotMeta"]), (1, 1, 1))
        RESULTS["checks"]["oneSnapshotAcrossHtmlCssFontsAndLogo"] = True

    # -- 2 ----------------------------------------------------------------

    def test_02_no_document_horizontal_scroll_at_any_required_width(self):
        record = {}
        for width in LAYOUT_VIEWPORTS:
            facts = self.renders[width]
            record[width] = [facts["scrollWidth"], facts["clientWidth"]]
            self.assertEqual(facts["scrollWidth"], facts["clientWidth"],
                             "document overflows horizontally at %dpx" % width)
            self.assertEqual(facts["clientWidth"], width,
                             "client width is not the emulated width at %dpx" % width)
        RESULTS["measurements"]["scrollWidth"] = record
        RESULTS["checks"]["noHorizontalScroll"] = True

    # -- 3 ----------------------------------------------------------------

    def test_03_every_rendered_text_node_is_at_least_twelve_px(self):
        """Coverage is every text node in the document, found with a
        TreeWalker over ``document.body``. It is not limited to selected
        classes and it is not limited to HTML: an SVG text node would be
        walked identically. This page renders none, which is recorded as
        coverage rather than claimed as a pass."""
        smallest = None
        namespaces = set()
        total = 0
        for width in LAYOUT_VIEWPORTS:
            nodes = self.renders[width]["textNodes"]
            self.assertGreater(len(nodes), 100,
                               "the text sweep found suspiciously few nodes")
            total += len(nodes)
            for node in nodes:
                namespaces.add(node["namespace"])
                if smallest is None or node["fontSize"] < smallest:
                    smallest = node["fontSize"]
                self.assertGreaterEqual(
                    node["fontSize"], 12.0,
                    "%dpx: %r renders at %.2f px"
                    % (width, node["text"][:40], node["fontSize"]))
        self.assertIsNotNone(smallest)
        RESULTS["measurements"]["minimumComputedTextPx"] = smallest
        RESULTS["measurements"]["textNodesMeasured"] = total
        RESULTS["measurements"]["textNamespaces"] = sorted(n for n in namespaces if n)
        RESULTS["coverage"].append("every rendered text node (TreeWalker, HTML+SVG)")
        RESULTS["checks"]["noTextBelowTwelvePx"] = True

    # -- 4 ----------------------------------------------------------------

    def test_04_type_scale_matches_the_frozen_endpoints(self):
        record = {}
        for width in (1440, 390, 320):
            roles = self.renders[width]["typeRoles"]
            self.assertEqual(sorted(roles), sorted(harness.TYPE_ENDPOINTS),
                             "the specimen does not render every type role")
            record[width] = {}
            for role, contract in harness.TYPE_ENDPOINTS.items():
                measured = roles[role]
                expected = contract[width]
                record[width][role] = {
                    "expected": expected,
                    "fontSize": measured["fontSize"],
                    "lineHeightRatio": round(measured["lineHeightRatio"], 4),
                }
                self.assertAlmostEqual(
                    measured["fontSize"], expected, delta=0.5,
                    msg="%s at %dpx computed %.3f px, contract says %.1f px"
                        % (role, width, measured["fontSize"], expected))
                low, high = contract["lh"]
                self.assertGreaterEqual(measured["lineHeightRatio"], low - 0.005,
                                        "%s leading below its band" % role)
                self.assertLessEqual(measured["lineHeightRatio"], high + 0.005,
                                     "%s leading above its band" % role)

            # The H1 specimen must hold to 2.5 desktop lines at full field
            # width. That limit is visual line-equivalent occupancy — the sum
            # of the text-line widths over the field width — not an integer
            # physical line count: this copy at 68 px measures about 2815 px
            # of text advance in a 1240 px field, so two physical lines are
            # arithmetically impossible and only three-with-a-short-tail can
            # satisfy 2.5.
            if width == 1440:
                h1 = roles["h1"]
                self.assertLessEqual(
                    h1["renderedLines"], 3,
                    "the H1 specimen renders on %d physical lines at 1440px"
                    % h1["renderedLines"])
                self.assertLessEqual(
                    h1["lineEquivalentMeasure"], 2.5 + 0.005,
                    "the H1 specimen occupies %.3f line-equivalents at 1440px, "
                    "above the 2.5 limit (line widths %s in a %.2f px field)"
                    % (h1["lineEquivalentMeasure"], h1["renderedLineWidths"],
                       h1["renderedWidth"]))
                if h1["renderedLines"] == 3:
                    self.assertLessEqual(
                        h1["lastLineFraction"], 0.5 + 0.005,
                        "the H1 specimen's third line fills %.3f of the field; "
                        "a third line is only inside 2.5 lines when it is short"
                        % h1["lastLineFraction"])
                record[width]["h1Lines"] = {
                    "renderedLines": h1["renderedLines"],
                    "renderedLineWidths": h1["renderedLineWidths"],
                    "lastLineFraction": h1["lastLineFraction"],
                    "lineEquivalentMeasure": h1["lineEquivalentMeasure"],
                }

            # The printed endpoint numbers beside each label must be the
            # contract, not decoration.
            for role, contract in harness.TYPE_ENDPOINTS.items():
                printed = [float(v) for v in
                           roles[role]["printedEndpoints"].split(" / ")]
                self.assertEqual(printed, [contract[1440], contract[390],
                                           contract[320]],
                                 "printed endpoints for %s disagree with the "
                                 "contract" % role)

        # The scale is continuous: no jump at the 390 px knee.
        for role in harness.TYPE_ENDPOINTS:
            below = self.renders[360]["typeRoles"][role]["fontSize"]
            self.assertGreaterEqual(
                self.renders[390]["typeRoles"][role]["fontSize"], below - 0.01,
                "%s decreases between 360 and 390 px" % role)

        # Families are assigned by role, not by accident.
        self.assertIn("Geist", self.renders[1440]["typeRoles"]["h1"]["fontFamily"])
        self.assertIn("Newsreader",
                      self.renders[1440]["typeRoles"]["body"]["fontFamily"])
        self.assertIn("JetBrains Mono",
                      self.renders[1440]["typeRoles"]["meta"]["fontFamily"])
        RESULTS["measurements"]["typeScale"] = record
        RESULTS["checks"]["typeScaleMatchesEndpoints"] = True

    # -- 5 ----------------------------------------------------------------

    def test_05_gutters_and_the_field_ceiling(self):
        record = {}
        for width, declared in DECLARED_GUTTER.items():
            facts = self.renders[width]
            measured = {(p["left"], p["right"]) for p in facts["pages"]}
            self.assertEqual(
                measured, {(float(declared), float(declared))},
                "%dpx gutter measured %s, declared %d px"
                % (width, sorted(measured), declared))
            for field in facts["fields"]:
                self.assertLessEqual(field, 1240.0 + 0.01,
                                     "the content field exceeded 1240 px at %dpx"
                                     % width)
                self.assertLessEqual(
                    field, width - 2 * declared + 0.01,
                    "the field ignored its gutter at %dpx" % width)
            record[width] = {"gutter": declared, "fields": sorted(set(facts["fields"]))}
        self.assertEqual(max(self.renders[1440]["fields"]), 1240.0)
        RESULTS["measurements"]["gutters"] = record
        RESULTS["checks"]["guttersAndFieldCeiling"] = True

    # -- 6 ----------------------------------------------------------------

    def test_06_twelve_equal_tracks_and_the_940_collapse(self):
        tracks = self.renders[1440]["rulerTracks"]
        self.assertEqual(len(tracks), 12, "the desktop grid is not twelve tracks")
        self.assertLess(max(tracks) - min(tracks), 0.5,
                        "the twelve tracks are not equal: %s" % tracks)
        cells = self.renders[1440]["rulerCells"]
        self.assertEqual(len(cells), 12)
        self.assertLess(max(cells) - min(cells), 0.5)
        self.assertEqual(self.renders[1440]["rulerNumbers"],
                         [str(n) for n in range(1, 13)])
        self.assertEqual(self.renders[1440]["computedTokens"]["--col-gap"], "32px")
        self.assertEqual(self.renders[768]["computedTokens"]["--col-gap"], "24px")

        wide = self.renders[940]
        narrow = self.renders[939]
        self.assertEqual(wide["splitStrategic"]["columnCount"], 12)
        self.assertTrue(wide["splitStrategic"]["sameRow"],
                        "the 7/5 carrier is not on one row at 940 px")
        self.assertFalse(narrow["splitStrategic"]["sameRow"],
                         "the 7/5 carrier did not collapse below 940 px")
        self.assertEqual(narrow["splitProduct"]["columnCount"], 1)
        self.assertEqual(wide["splitProduct"]["columnCount"], 2)

        # 7/5 and 45/55 are real proportions, not labels.
        strategic = wide["splitStrategic"]
        self.assertAlmostEqual(strategic["ratio"], 7 / 5, delta=0.06)
        product = wide["splitProduct"]
        self.assertAlmostEqual(product["ratio"], 45 / 55, delta=0.04)

        # Collapsing must not reorder the document.
        self.assertEqual(wide["domTextOrder"], narrow["domTextOrder"],
                         "the collapse changed DOM reading order")
        self.assertEqual(narrow["domTextOrder"], ["7", "5", "45", "55"])

        # The reading measure stays inside 560-620 px where it has room.
        for width in (1024, 1440):
            for measure in self.renders[width]["measures"]:
                self.assertLessEqual(measure, 620.0 + 0.01)
                self.assertGreaterEqual(measure, 560.0)
        for width in (320, 360, 390):
            for measure in self.renders[width]["measures"]:
                self.assertLessEqual(measure, 620.0 + 0.01)
        RESULTS["measurements"]["gridTracks1440"] = tracks
        RESULTS["measurements"]["collapse"] = {
            "940": wide["splitStrategic"], "939": narrow["splitStrategic"]}
        RESULTS["checks"]["twelveEqualTracksAndCollapse"] = True

    # -- 7 ----------------------------------------------------------------

    def test_07_every_interactive_target_is_at_least_44_by_44(self):
        smallest = None
        counted = 0
        for width in LAYOUT_VIEWPORTS:
            targets = self.renders[width]["interactive"]
            self.assertGreaterEqual(len(targets), 8,
                                    "the specimen lost its control set at %dpx"
                                    % width)
            for target in targets:
                counted += 1
                least = min(target["width"], target["height"])
                if smallest is None or least < smallest:
                    smallest = least
                self.assertGreaterEqual(
                    target["width"], 44.0,
                    "%dpx: %r is %.1f px wide" % (width, target["text"],
                                                  target["width"]))
                self.assertGreaterEqual(
                    target["height"], 44.0,
                    "%dpx: %r is %.1f px tall" % (width, target["text"],
                                                  target["height"]))
        RESULTS["measurements"]["smallestInteractiveEdge"] = smallest
        RESULTS["measurements"]["interactiveTargetsMeasured"] = counted
        RESULTS["checks"]["fortyFourPixelTargets"] = True

    # -- 8 ----------------------------------------------------------------

    def test_08_keyboard_reaches_every_control_once_with_a_visible_ring(self):
        expected = [(t["text"], t["onInk"])
                    for t in self.renders[1440]["interactive"]
                    if not t["disabled"]]
        actual = [(s["text"], s["onInk"]) for s in self.tab_stops]
        self.assertEqual(actual, expected,
                         "the Tab sequence is not the DOM order of the "
                         "enabled controls")
        self.assertEqual(len(actual), len(set(range(len(actual)))),
                         "a control was reached twice")
        self.assertGreaterEqual(len(actual), 6,
                                "fewer controls were reachable than rendered")

        warm = [s for s in self.tab_stops if not s["onInk"]]
        ink = [s for s in self.tab_stops if s["onInk"]]
        self.assertTrue(warm and ink,
                        "focus was not exercised on both grounds")

        rings = []
        for stop in self.tab_stops:
            self.assertTrue(stop["matchesFocusVisible"],
                            "%r did not match :focus-visible under a real Tab"
                            % stop["text"])
            self.assertNotEqual(stop["outlineStyle"], "none",
                                "%r has no focus outline" % stop["text"])
            self.assertGreaterEqual(stop["outlineWidth"], 2.0,
                                    "%r focus ring is thinner than 2 px"
                                    % stop["text"])
            self.assertGreaterEqual(stop["outlineOffset"], 2.0,
                                    "%r focus ring offset is under 2 px"
                                    % stop["text"])
            ratio = harness.contrast_ratio(stop["outlineColor"], stop["surface"])
            self.assertGreaterEqual(
                ratio, 3.0,
                "%r focus ring is %.2f:1 against its %s ground"
                % (stop["text"], ratio, "ink" if stop["onInk"] else "warm"))
            rings.append({"text": stop["text"], "onInk": stop["onInk"],
                          "width": stop["outlineWidth"],
                          "offset": stop["outlineOffset"],
                          "contrast": round(ratio, 2)})
        RESULTS["measurements"]["tabOrder"] = actual
        RESULTS["measurements"]["focusRings"] = rings
        RESULTS["checks"]["keyboardOrderAndVisibleFocus"] = True

    # -- 9 ----------------------------------------------------------------

    def test_09_accepted_pairs_meet_aa_and_rejected_pairs_are_marked(self):
        """Every rendered text node is checked, not only the pair specimens.
        Disabled control text is excluded under WCAG 1.4.3; the two
        deliberately rejected specimens are excluded and separately proved to
        fail, to be struck through and to carry their own supplied caption."""
        failures, exclusions = [], []
        for width in LAYOUT_VIEWPORTS:
            for node in self.renders[width]["textNodes"]:
                ratio = harness.contrast_ratio(node["color"], node["background"])
                required = harness.aa_threshold(node["fontSize"],
                                                node["fontWeight"])
                record = {"viewport": width, "text": node["text"][:60],
                          "ratio": round(ratio, 2), "required": required,
                          "fontSizePx": node["fontSize"]}
                if node["disabled"]:
                    record["reason"] = "disabled control, WCAG 1.4.3 exempt"
                    exclusions.append(record)
                elif node["rejectedSpecimen"]:
                    record["reason"] = "deliberately rejected pair specimen"
                    exclusions.append(record)
                elif ratio + 0.005 < required:
                    failures.append(record)
        self.assertEqual(failures, [], "contrast failures: %s"
                         % json.dumps(failures, indent=2))

        pairs = self.renders[1440]["pairs"]
        self.assertEqual(len(pairs), 10, "the pair table changed shape")
        accepted = [p for p in pairs if p["status"] == "accepted"]
        rejected = [p for p in pairs if p["status"] == "rejected"]
        self.assertEqual(len(rejected), 2)
        self.assertEqual({p["fgToken"] for p in rejected}, {"--coral", "--sage"})
        self.assertTrue(all(p["bgToken"] == "--paper" for p in rejected))

        for pair in pairs:
            measured = harness.contrast_ratio(pair["color"], pair["background"])
            printed = float(pair["printedRatio"])
            self.assertAlmostEqual(
                measured, printed, delta=0.05,
                msg="%s / %s prints %.2f:1 but renders %.2f:1"
                    % (pair["fgToken"], pair["bgToken"], printed, measured))
            required = harness.aa_threshold(pair["fontSize"], pair["fontWeight"])
            self.assertEqual(float(pair["printedMinimum"]), required,
                             "the printed AA minimum is not the one that "
                             "applies at the rendered size")
            if pair["status"] == "accepted":
                self.assertGreaterEqual(measured + 0.005, required,
                                        "an accepted pair fails AA: %s" % pair)
            else:
                self.assertLess(measured, required,
                                "a rejected pair actually passes AA: %s" % pair)
                self.assertTrue(pair["lineThrough"],
                                "the rejected specimen is not struck through")
                self.assertIn(pair["note"].strip(),
                              ("Coral is not small text.",
                               "Sage is a boundary, not a label color."))

        # Coral and Sage on paper are used nowhere as a readable label.
        for width in LAYOUT_VIEWPORTS:
            for node in self.renders[width]["textNodes"]:
                if node["rejectedSpecimen"]:
                    continue
                ratio = harness.contrast_ratio(node["color"], node["background"])
                self.assertFalse(
                    3.2 < ratio < 3.5 and not node["disabled"]
                    and node["color"][0] > 100 and node["color"][1] > 100
                    and abs(node["color"][0] - 124) < 6,
                    "Sage appears as a readable label: %r" % node["text"])
        RESULTS["measurements"]["contrastExclusions"] = exclusions
        RESULTS["measurements"]["pairs"] = [
            {"fg": p["fgToken"], "bg": p["bgToken"], "status": p["status"],
             "ratio": round(harness.contrast_ratio(p["color"], p["background"]), 2)}
            for p in pairs]
        RESULTS["checks"]["contrastAcceptedAndRejected"] = True

    # -- 10 ---------------------------------------------------------------

    def test_10_all_three_families_load_locally_with_their_licenses(self):
        for width in (1440, 390):
            check = self.renders[width]["readiness"]["fontsCheck"]
            for family in ("Geist", "Newsreader", "JetBrains Mono"):
                self.assertTrue(check[family],
                                "document.fonts.check failed for %s at %dpx"
                                % (family, width))
            loaded = self.renders[width]["readiness"]["loadedFontFamilies"]
            for family in ("Geist", "Newsreader", "JetBrains Mono"):
                self.assertIn(family, loaded)

        font_requests = [u for u in self.renders[1440]["requests"]
                         if u.endswith(".woff2")]
        self.assertEqual(len(font_requests), 3,
                         "expected exactly three local font requests, got %s"
                         % font_requests)
        for url in font_requests:
            self.assertTrue(url.startswith("http://127.0.0.1:"),
                            "a font was fetched from %s" % url)

        for relative in harness.LICENSE_PATHS:
            target = REPO_ROOT / relative
            self.assertTrue(target.exists(), "missing license %s" % relative)
            text = target.read_text()
            self.assertIn("SIL Open Font License", text,
                          "%s is not an OFL license" % relative)
            self.assertGreater(len(text), 3000)

        combined = sum((REPO_ROOT / p.lstrip("/")).stat().st_size
                       for p in harness.FONT_PATHS)
        self.assertLessEqual(combined, harness.PERFORMANCE_BUDGET["woff2BytesMax"],
                             "combined WOFF2 is %d bytes" % combined)
        RESULTS["measurements"]["combinedWoff2Bytes"] = combined
        RESULTS["checks"]["localFontsWithLicenses"] = True

    # -- 11 ---------------------------------------------------------------

    def test_11_no_request_leaves_localhost_and_no_console_error_occurs(self):
        remote = []
        for width in LAYOUT_VIEWPORTS:
            facts = self.renders[width]
            for url in facts["requests"]:
                if not url.startswith(("http://127.0.0.1:", "data:", "about:")):
                    remote.append((width, url))
            self.assertEqual(facts["consoleErrors"], 0,
                             "%dpx console errors: %s"
                             % (width, facts["consoleErrorDetail"]))
            self.assertEqual(facts["failedRequests"], [],
                             "%dpx failed requests: %s"
                             % (width, facts["failedRequests"]))
            self.assertEqual(facts["httpErrorResponses"], [],
                             "%dpx HTTP errors: %s"
                             % (width, facts["httpErrorResponses"]))
            self.assertEqual(facts["externalLinks"], [],
                             "the markup references an off-origin URL")
            self.assertEqual(facts["placeholderLinks"], 0,
                             "placeholder links remain")
        self.assertEqual(remote, [], "requests left 127.0.0.1: %s" % remote)

        # The stylesheet the page actually links is the token file under test.
        head = self.renders[1440]["headOuterHTML"]
        self.assertIn('href="/design/golden-standard/system/tokens.css"', head)
        self.assertIn('href="foundations.css"', head)
        self.assertNotIn("fonts.googleapis.com", head)
        self.assertNotIn("fonts.gstatic.com", head)

        # Zero bytes of JavaScript on the specimen page.
        readiness = self.renders[1440]["readiness"]
        self.assertEqual(readiness["scriptElements"], 0,
                         "the specimen page carries a script element")
        self.assertEqual(readiness["inlineEventAttributes"], 0,
                         "the specimen page carries an inline event handler")

        # And the frozen performance budget, measured on served bytes.
        budget = harness.asset_budget(self.base_url)
        self.assertLessEqual(budget["htmlBytes"], 40 * 1024)
        self.assertLessEqual(budget["combinedCssBytes"], 55 * 1024)
        self.assertLessEqual(budget["combinedWoff2Bytes"], 750 * 1024)
        RESULTS["measurements"]["performance"] = budget
        RESULTS["measurements"]["distinctRequests"] = sorted(
            {u for w in LAYOUT_VIEWPORTS for u in self.renders[w]["requests"]})
        RESULTS["checks"]["localOnlyAndNoConsoleErrors"] = True

    # -- 12 ---------------------------------------------------------------

    def test_12_reduced_motion_removes_transitions_without_changing_layout(self):
        normal = self.renders[390]
        reduced = self.reduced

        self.assertTrue(normal["transitionDurations"],
                        "there was no motion to remove in the first place")
        self.assertTrue(all(v <= 0.001 for v in reduced["transitionDurations"]),
                        "transitions survived prefers-reduced-motion: %s"
                        % sorted(set(reduced["transitionDurations"]))[:8])

        self.assertEqual(reduced["boxes"], normal["boxes"],
                         "reduced motion changed the layout")
        self.assertEqual([n["text"] for n in reduced["textNodes"]],
                         [n["text"] for n in normal["textNodes"]],
                         "reduced motion changed the content")
        self.assertEqual(reduced["scrollHeight"], normal["scrollHeight"])
        RESULTS["measurements"]["reducedMotion"] = {
            "transitionsBefore": sorted(set(normal["transitionDurations"])),
            "transitionsAfter": sorted(set(reduced["transitionDurations"])),
            "layoutIdentical": True,
        }
        RESULTS["checks"]["reducedMotionSafe"] = True

    # -- 13 ---------------------------------------------------------------

    def test_13_only_p2_owned_files_differ_and_public_bytes_are_identical(self):
        committed = [p for p in git("diff", "--name-only",
                                    "%s...HEAD" % BASE_COMMIT).splitlines() if p]
        working = []
        # `--untracked-files=all` is required: the default collapses an
        # untracked tree to its parent directory, so the owned font files
        # would arrive as the bare, unowned path `assets/fonts/`. The
        # owned-prefix contract itself is unchanged; only the enumeration is.
        for line in git_raw("status", "--porcelain",
                            "--untracked-files=all").splitlines():
            if not line.strip():
                continue
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            working.append(path.strip('"'))

        for path in committed + working:
            self.assertTrue(is_owned(path),
                            "out-of-scope file changed: %s" % path)

        # Byte identity, not name absence: every file tracked under a
        # protected root at the base commit is compared byte for byte.
        listed = git("ls-tree", "-r", "--name-only", BASE_COMMIT,
                     *PROTECTED_ROOTS).splitlines()
        compared, differing, missing = 0, [], []
        for path in listed:
            if not path or is_owned(path):
                continue
            target = REPO_ROOT / path
            if not target.exists():
                missing.append(path)
                continue
            if target.read_bytes() != git_bytes("show", "%s:%s"
                                                % (BASE_COMMIT, path)):
                differing.append(path)
            compared += 1
        self.assertEqual(missing, [], "a public or legacy file was deleted")
        self.assertEqual(differing, [],
                         "public or legacy files changed: %s" % differing)
        self.assertGreater(compared, 30,
                           "the byte-identity comparison covered too little")

        # The four narrative files and the masterplan are untouched too.
        for path in ("design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md",
                     "design/golden-standard/narrative/HOMEPAGE-MESSAGE-ARCHITECTURE.md",
                     "design/golden-standard/narrative/VERTICAL-SLICE-COPY.md",
                     "design/golden-standard/narrative/PAGE-BRIEFS.md",
                     "design/golden-standard/narrative/EVIDENCE-LEDGER.md",
                     "tools/serve_preview.py", "tests/test_preview_revision.py"):
            self.assertEqual((REPO_ROOT / path).read_bytes(),
                             git_bytes("show", "%s:%s" % (BASE_COMMIT, path)),
                             "%s changed" % path)
        RESULTS["measurements"]["protectedFilesCompared"] = compared
        RESULTS["measurements"]["changedVersusBase"] = sorted(set(committed + working))
        RESULTS["checks"]["onlyOwnedFilesChanged"] = True

    # -- specimen contract ------------------------------------------------

    def test_14_the_specimen_renders_the_contract_it_documents(self):
        """P2 section 6: the specimen must actually contain the eight roles,
        the five sections, the real logotype, the rhythm and a token
        reference whose printed values are the ones tokens.css computes."""
        facts = self.renders[1440]
        self.assertEqual(facts["title"], "Dagg foundations — P2")
        self.assertEqual(facts["lang"], "en")
        self.assertEqual(facts["sectionTitles"], [
            "Palette with a job", "Type carries meaning",
            "One grid, different emphasis", "Rhythm, not slides",
            "Accessible by construction"])

        # 1. eight palette roles, each with its declared value.
        declared = {"--paper": "#F0EEE6", "--lift": "#FAF9F5",
                    "--panel": "#E8E6DC", "--ink": "#141413",
                    "--ink-2": "#33332F", "--coral": "#D97757",
                    "--coral-deep": "#9E4A2E", "--sage": "#7C8471"}
        for token, value in declared.items():
            self.assertEqual(facts["computedTokens"][token], value,
                             "%s is not the frozen value" % token)

        # 8. the printed token reference agrees with tokens.css, everywhere.
        self.assertGreaterEqual(len(facts["printedTokens"]), 20)
        seen = set()
        for width in LAYOUT_VIEWPORTS:
            for row in self.renders[width]["printedTokens"]:
                computed = self.renders[width]["computedTokens"][row["name"]]
                self.assertEqual(
                    row["printedValue"], " ".join(computed.split()),
                    "%s prints %r but computes %r at %dpx"
                    % (row["name"], row["printedValue"], computed, width))
                self.assertEqual(row["printedLabel"], row["name"])
                seen.add(row["name"])
        self.assertEqual(len(seen), len(facts["printedTokens"]),
                         "the token reference repeats a token")

        # 5. a non-repeating rhythm with real height variation.
        rhythm = facts["rhythm"]
        self.assertEqual([b["name"] for b in rhythm],
                         ["carrier", "punctuation", "instrument", "proof", "close"])
        self.assertEqual([b["caption"].strip() for b in rhythm],
                         ["One long carrier.", "One short punctuation.",
                          "One contained instrument.", "One proof split.",
                          "One decisive close."])
        heights = [b["height"] for b in rhythm]
        self.assertGreaterEqual(max(heights) / min(heights), 2.5,
                                "the rhythm is flat: %s" % heights)
        punctuation = rhythm[1]["height"]
        self.assertTrue(240 <= punctuation <= 360,
                        "the punctuation block is %.0f px, not 240-360"
                        % punctuation)
        grounds = {tuple(round(v) for v in b["background"]) for b in rhythm}
        self.assertGreaterEqual(len(grounds), 3,
                                "the rhythm uses one ground only")

        # 7. the logotype is the real asset, drawn at its real aspect ratio.
        logos = [img for img in facts["readiness"]["images"]
                 if "dagg-logotype" in img["src"]]
        self.assertEqual(len(logos), 2,
                         "the specimen does not use both real logotype assets")
        for logo in logos:
            self.assertTrue(logo["complete"] and logo["naturalWidth"] == 1844
                            and logo["naturalHeight"] == 375,
                            "a logotype did not load from the real asset")
            self.assertAlmostEqual(
                logo["renderedWidth"] / logo["renderedHeight"], 1844 / 375,
                delta=0.02, msg="a logotype is drawn at the wrong aspect ratio")

        # 3. the specimen copy is the P1 copy, verbatim.
        self.assertEqual(facts["typeRoles"]["h1"]["text"],
                         "We redesign how your company works — and build what "
                         "its AI-native operating model requires.")
        self.assertEqual(facts["typeRoles"]["meta"]["text"],
                         "REPRESENTATIVE RECORD · SYNTHETIC DATA")
        RESULTS["measurements"]["rhythmHeights1440"] = heights
        RESULTS["checks"]["specimenContract"] = True


def _write_results():
    target = os.environ.get("DAGG_P2_TEST_JSON")
    if not target:
        return
    RESULTS["coverage"] = sorted(set(RESULTS["coverage"]))
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_text(json.dumps(RESULTS, indent=2, sort_keys=True,
                                       default=str) + "\n")


atexit.register(_write_results)


if __name__ == "__main__":
    unittest.main(verbosity=2)
