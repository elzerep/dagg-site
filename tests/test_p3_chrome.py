#!/usr/bin/env python3
"""P3 global-chrome acceptance suite (P3B subpackage).

Drives the installed Google Chrome over the Chrome DevTools Protocol against
the P0R2 immutable-snapshot preview server, reusing the P2 raw-CDP
WebSocket/Chrome/server plumbing (``capture_p2_evidence``) and the
chrome-specific interactions in ``capture_p3_evidence``. No Playwright, no
bundled browser, no live-disk server.

This suite is P3B only: it tests the frozen P3A source
(``design/golden-standard/system/chrome.css``, ``chrome.js`` and
``preview/golden-standard/chrome/**``) without editing it. It does not grade
its own rendering -- that is Codex's P3C visual gate -- and it may not be
made to pass by changing P3A source.

Maps directly to P3-GLOBAL-CHROME.md section 9, items 1-14:

    python3 -B -m unittest discover -s tests -p test_p3_chrome.py -v
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

import capture_p2_evidence as p2  # noqa: E402
import capture_p3_evidence as harness  # noqa: E402

BASE_COMMIT = harness.BASE_COMMIT
CHROME_ROOT = harness.CHROME_ROOT
ROUTE_TABLE = harness.ROUTE_TABLE
PRIMARY_LABEL_ORDER = harness.PRIMARY_LABEL_ORDER
FOOTER_EXPLORE = harness.FOOTER_EXPLORE
FOOTER_COMPANY = harness.FOOTER_COMPANY
FOOTER_TRUST = harness.FOOTER_TRUST
LAYOUT_VIEWPORTS = harness.LAYOUT_VIEWPORTS
COLLAPSE_PROBES = harness.COLLAPSE_PROBES
INK_RGB = harness.INK_RGB
PAPER_RGB = harness.PAPER_RGB
MAIL_HREF = "mailto:hello@dagg.ai"

RESULTS: dict = {"checks": {}, "coverage": [], "measurements": {}, "notes": []}


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(REPO_ROOT), *args],
        check=True, capture_output=True, text=True).stdout.strip()


class RenderedChrome(unittest.TestCase):
    """Every assertion in this suite reads the class-level renders below,
    produced once by one immutable server process and one Chrome process."""

    server = None
    chrome = None
    cdp = None
    profile_dir = None

    @classmethod
    def setUpClass(cls):
        cls.server, cls.base_url, cls.startup_seconds = p2.start_server()
        cls.profile_dir = Path(tempfile.mkdtemp(prefix="dagg-p3-test-chrome-"))
        cls.chrome, browser_ws, cls.chrome_path = p2.start_chrome(cls.profile_dir)
        cls.cdp = p2.CDP(browser_ws)

        # One Chrome process, one immutable server, one snapshot ID -- but a
        # fresh CDP target (ChromePage) per interaction group below, so a
        # long chain of navigations/scrolls/focus-traps on a single page
        # target cannot leave it in a state where a later WAIT_FOR_PAINT
        # never settles. Each ChromePage still drives the same cls.cdp
        # browser connection and the same cls.base_url server.
        cls.page = harness.ChromePage(cls.cdp)  # (a) routes/layout/desktop keyboard

        status, headers, body = p2.fetch(cls.base_url, "/__revision")
        assert status == 200, status
        cls.revision = json.loads(body)
        cls.snapshot_id = cls.revision["snapshotId"]

        # One render per route destination at 1440px -- the route table.
        cls.routes = {}
        for route in ROUTE_TABLE:
            cls.routes[route["production"]] = cls.page.open_chrome(
                cls.base_url + route["preview"], 1440)

        # The root specimen across the required layout ladder.
        cls.root_by_width = {}
        for width in LAYOUT_VIEWPORTS:
            cls.root_by_width[width] = cls.page.open_chrome(
                cls.base_url + CHROME_ROOT + "/", width)

        # The 939/940 collapse probe.
        cls.collapse = {}
        for width in COLLAPSE_PROBES:
            cls.collapse[width] = cls.page.open_chrome(
                cls.base_url + CHROME_ROOT + "/", width)

        # 200% zoom reflow at a conventional 1280x900 desktop baseline.
        cls.zoomed = cls.page.open_zoomed(cls.base_url + CHROME_ROOT + "/")

        # Desktop keyboard order (disclosure forced open by chrome.css).
        cls.page.open_chrome(cls.base_url + CHROME_ROOT + "/", 1440)
        cls.tab_stops_desktop = cls.page.tab_through()

        # (b) Mobile disclosure interactions get their own target: closed by
        # default; keyboard-open the summary and trap.
        cls.page_mobile = harness.ChromePage(cls.cdp)
        cls.page_mobile.open_chrome(cls.base_url + CHROME_ROOT + "/", 390)
        cls.mobile_closed = cls.page_mobile.measure()
        cls.page_mobile.focus_selector("[data-summary]")
        cls.page_mobile.press_key("Enter", "Enter", 13, text="\r")
        cls.page_mobile.settle()
        cls.mobile_open = cls.page_mobile.measure()
        cls.mobile_trap_stops = cls.page_mobile.tab_through()
        cls.page_mobile.press_key("Escape", "Escape", 27)
        cls.mobile_after_escape = cls.page_mobile.measure()
        cls.mobile_focus_after_escape = cls.page_mobile.evaluate(harness.FOCUS_PROBE)

        # Reopen, then close by an outside click.
        cls.page_mobile.focus_selector("[data-summary]")
        cls.page_mobile.press_key("Enter", "Enter", 13, text="\r")
        cls.page_mobile.click_outside()
        cls.mobile_after_outside_click = cls.page_mobile.measure()

        # (c) Scroll/adaptive-header interactions get their own target,
        # opened fresh after the mobile focus-trap/overflow-lock sequence
        # above rather than reusing that target. Scroll hide/reveal at
        # 1440px on the root specimen. Targets are derived from the
        # specimen's own measured section positions rather than guessed
        # constants, so they land correctly regardless of the frozen rhythm
        # heights: the ink carrier's own top for the theme check, and the
        # long scroll-distance carrier (2400px min-height, section 4 of the
        # specimen) for the generic down/up hide-reveal.
        cls.page_scroll = harness.ChromePage(cls.cdp)
        cls.page_scroll.open_chrome(cls.base_url + CHROME_ROOT + "/", 1440)
        cls.scroll_to_ink = cls.page_scroll.scroll_to_selector_top(
            '[data-header-theme="ink"]', offset=120)
        # Reads the header's own declared transition-duration and waits it
        # out before measuring: without this, a color read taken right after
        # the data-theme flip can land mid-transition and report a blend of
        # warm and ink that matches neither declared pair -- a measurement-
        # timing defect in the rig, not a real theme failure.
        cls.page_scroll.wait_for_header_transition()
        cls.header_state_at_ink = cls.page_scroll.measure()

        cls.scroll_further_down = cls.page_scroll.scroll_to_selector_top(
            '.specimen-carrier--scroll', offset=800)
        cls.header_state_hidden = cls.page_scroll.measure()

        scroll_height = cls.header_state_hidden["scrollHeight"]
        near_top_of_scroll_carrier = cls.page_scroll.evaluate(
            "(() => { const el = document.querySelector("
            "'.specimen-carrier--scroll'); "
            "return el ? el.getBoundingClientRect().top + window.scrollY : null; })()")
        cls.scroll_up = cls.page_scroll.scroll_sequence([
            int(scroll_height * 0.9), int(scroll_height * 0.7),
            int(near_top_of_scroll_carrier or scroll_height * 0.5),
        ])
        cls.header_state_revealed = cls.page_scroll.measure()

        # Focus-entry reveal, from a scrolled-away, hidden state.
        cls.page_scroll.scroll_to_selector_top('.specimen-carrier--scroll', offset=800)
        cls.page_scroll.focus_selector(
            "[data-chrome-header] a, [data-chrome-header] summary")
        cls.header_state_after_focus_entry = cls.page_scroll.measure()

        # (d) No-JavaScript gets its own fresh target: only the exact local
        # chrome.js request is network-blocked (Network.setBlockedURLs), not
        # the JS engine itself, so chrome.js never executes on the page while
        # the CDP harness's own Runtime.evaluate calls -- the readiness wait,
        # measure() and the dispatched click below -- keep working.
        cls.page_nojs = harness.ChromePage(cls.cdp)
        cls.no_js = cls.page_nojs.open_nojs(cls.base_url + CHROME_ROOT + "/", 390)
        cls.page_nojs.click_selector("[data-summary]")
        cls.no_js_open_attempt = cls.page_nojs.measure()

        # Reduced motion at 390px, against the same width without it, on its
        # own fresh target.
        cls.page_reduced = harness.ChromePage(cls.cdp)
        cls.reduced = cls.page_reduced.open_chrome(
            cls.base_url + CHROME_ROOT + "/", 390, reduced_motion=True)

        RESULTS["snapshotId"] = cls.snapshot_id
        RESULTS["commit"] = cls.revision["commit"]
        RESULTS["dirty"] = cls.revision["dirty"]
        RESULTS["chrome"] = cls.chrome_path
        RESULTS["routesRendered"] = sorted(cls.routes)

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
            stderr = p2.stop_server(cls.server)
            RESULTS["checks"]["zeroServerExceptions"] = "Traceback" not in stderr
        if cls.profile_dir is not None:
            shutil.rmtree(cls.profile_dir, ignore_errors=True)

    # -- 1 : one snapshot ID across HTML, CSS, JS, fonts, both logotypes --

    def test_01_every_served_chrome_asset_carries_one_snapshot_id(self):
        targets = [("CSS-chrome", harness.CHROME_CSS_PATH),
                   ("JS-chrome", harness.CHROME_JS_PATH),
                   ("CSS-tokens", harness.TOKENS_CSS_PATH),
                   ("PNG-logotype-dark", harness.LOGO_DARK_PATH),
                   ("PNG-logotype", harness.LOGO_LIGHT_PATH)]
        targets += [("WOFF2-%s" % p.rsplit("/", 1)[-1], p)
                    for p in harness.FONT_PATHS]
        for label, path in targets:
            status, headers, body = p2.fetch(self.base_url, path)
            self.assertEqual(status, 200, "%s not served" % label)
            self.assertGreater(len(body), 0, "%s served empty" % label)
            lowered = {k.lower(): v for k, v in headers.items()}
            self.assertEqual(lowered.get("x-dagg-snapshot"), self.snapshot_id,
                             "%s left the accepted snapshot" % label)
            if label not in RESULTS["coverage"]:
                RESULTS["coverage"].append(label)

        for production, facts in self.routes.items():
            self.assertEqual(facts["snapshot"], self.snapshot_id,
                             "%s left the snapshot" % production)
            self.assertEqual((facts["revisionMeta"], facts["dirtyMeta"],
                              facts["snapshotMeta"]), (1, 1, 1),
                             "%s does not carry exactly one of each "
                             "revision meta tag" % production)
        RESULTS["checks"]["oneSnapshotAcrossHtmlCssJsFontsAndLogos"] = True

    # -- 2 : every destination 200s, correct production path, 1 header/footer

    def test_02_every_preview_destination_serves_one_header_and_footer(self):
        record = {}
        for route in ROUTE_TABLE:
            facts = self.routes[route["production"]]
            self.assertTrue(facts["header"]["present"], "%s has no header"
                            % route["production"])
            self.assertTrue(facts["footer"]["present"], "%s has no footer"
                            % route["production"])
            self.assertEqual(facts["headerCount"], 1, "%s renders %d headers"
                             % (route["production"], facts["headerCount"]))
            self.assertEqual(facts["footerCount"], 1, "%s renders %d footers"
                             % (route["production"], facts["footerCount"]))
            record[route["production"]] = {
                "preview": route["preview"], "url": facts["url"],
                "headerCount": facts["headerCount"], "footerCount": facts["footerCount"],
            }
        # The root's own brand link declares the production root, and every
        # nav/CTA/footer link declares the production path from the table.
        root = self.routes["/"]
        self.assertEqual(root["header"]["brandProductionHref"], "/")
        by_label = {r["label"]: r["production"] for r in ROUTE_TABLE}
        for link in root["header"]["navLinks"] + [root["header"]["cta"]]:
            self.assertEqual(link["productionHref"], by_label[link["text"]],
                             "%r declares the wrong production path" % link["text"])
        # The mail link is not one of ROUTE_TABLE's preview destinations --
        # it has no preview route, only a direct mailto: production href --
        # so it is checked explicitly rather than indexed through
        # by_label[link["text"]], which would KeyError on "hello@dagg.ai".
        for column in root["footer"]["columns"]:
            for link in column["links"]:
                if (link["href"] or "").startswith("mailto:"):
                    self.assertEqual(link["productionHref"], MAIL_HREF,
                                     "the mail link declares the wrong "
                                     "production href: %r" % link["productionHref"])
                    continue
                self.assertEqual(link["productionHref"], by_label[link["text"]],
                                 "%r declares the wrong production path" % link["text"])
        RESULTS["measurements"]["routeTable"] = record
        RESULTS["checks"]["everyDestinationServesOneHeaderAndFooter"] = True

    # -- 3 : primary label order; root is not Transformation ---------------

    def test_03_primary_label_order_and_root_is_not_transformation(self):
        root = self.routes["/"]
        nav_labels = [link["text"] for link in root["header"]["navLinks"]]
        cta_label = root["header"]["cta"]["text"]
        self.assertEqual(tuple(nav_labels) + (cta_label,), PRIMARY_LABEL_ORDER,
                         "primary order is %s" % (nav_labels + [cta_label]))
        self.assertEqual(root["header"]["brandProductionHref"], "/")
        self.assertNotEqual(root["header"]["brandProductionHref"], "/transformation")
        # No nav link is marked current on the root: the homepage is the
        # executive memo, not a disguised Transformation page.
        for link in root["header"]["navLinks"]:
            self.assertIsNone(link["ariaCurrent"],
                             "the root incorrectly marks %r current" % link["text"])
        RESULTS["measurements"]["primaryOrder"] = nav_labels + [cta_label]
        RESULTS["checks"]["primaryLabelOrderAndRootIsNotTransformation"] = True

    # -- 4 : no empty/hash/js links; mail is the only non-HTTP route -------

    def test_04_no_placeholder_links_and_mail_is_the_only_non_http_route(self):
        non_http = set()
        for production, facts in self.routes.items():
            self.assertEqual(facts["placeholderLinks"], 0,
                             "%s carries a placeholder, hash-only or "
                             "javascript: link" % production)
            for href in facts["allHrefs"]:
                if href is None or href in ("#", ""):
                    continue
                if not href.startswith(("/", "http://127.0.0.1", "mailto:")):
                    non_http.add((production, href))
        mail_hrefs = {href for facts in self.routes.values()
                     for href in facts["allHrefs"]
                     if href and href.startswith("mailto:")}
        self.assertEqual(mail_hrefs, {"mailto:hello@dagg.ai"},
                         "the only mail route must be mailto:hello@dagg.ai")
        non_mail = {pair for pair in non_http
                   if not pair[1].startswith("mailto:")}
        self.assertEqual(non_mail, set(),
                         "a non-HTTP, non-mail route exists: %s" % non_mail)
        RESULTS["checks"]["noPlaceholderLinksMailIsOnlyNonHttp"] = True

    # -- 5 : no horizontal scroll at required widths, or at 200% zoom ------

    def test_05_no_horizontal_scroll_at_required_widths_or_200pct_zoom(self):
        # Keys are normalized to deterministic strings (not raw ints) so
        # that json.dumps(..., sort_keys=True) can sort them: sort_keys
        # sorts dict items by key before stringifying, and Python raises
        # TypeError comparing an int key against the "zoom200pct" string key.
        record = {}
        for width in LAYOUT_VIEWPORTS:
            facts = self.root_by_width[width]
            record[str(width)] = [facts["scrollWidth"], facts["clientWidth"]]
            self.assertEqual(facts["scrollWidth"], facts["clientWidth"],
                             "document overflows horizontally at %dpx" % width)
        self.assertEqual(self.zoomed["scrollWidth"], self.zoomed["clientWidth"],
                         "document overflows horizontally at 200%% zoom "
                         "(emulated viewport %dpx)" % self.zoomed["clientWidth"])
        record["zoom200pct"] = [self.zoomed["scrollWidth"], self.zoomed["clientWidth"]]
        RESULTS["measurements"]["scrollWidth"] = record
        RESULTS["checks"]["noHorizontalScrollIncluding200PctZoom"] = True

    # -- 6 : every text node >= 12px, footer text >= 13px; controls >= 44 ---

    def test_06_text_floor_and_touch_target_floor(self):
        smallest_text = None
        smallest_footer_text = None
        smallest_target = None
        for width in LAYOUT_VIEWPORTS:
            facts = self.root_by_width[width]
            self.assertGreater(len(facts["textNodes"]), 5,
                               "the %dpx render found suspiciously few text nodes"
                               % width)
            for node in facts["textNodes"]:
                if smallest_text is None or node["fontSize"] < smallest_text:
                    smallest_text = node["fontSize"]
                self.assertGreaterEqual(node["fontSize"], 12.0,
                                        "%dpx: %r renders at %.2fpx"
                                        % (width, node["text"][:40], node["fontSize"]))
                if node["inFooter"]:
                    if (smallest_footer_text is None
                            or node["fontSize"] < smallest_footer_text):
                        smallest_footer_text = node["fontSize"]
                    self.assertGreaterEqual(
                        node["fontSize"], 13.0,
                        "%dpx footer: %r renders at %.2fpx, below the "
                        "P3 footer-specific 13px floor"
                        % (width, node["text"][:40], node["fontSize"]))
            self.assertGreaterEqual(len(facts["interactive"]), 6,
                                    "the %dpx render lost its control set" % width)
            for target in facts["interactive"]:
                least = min(target["width"], target["height"])
                if smallest_target is None or least < smallest_target:
                    smallest_target = least
                self.assertGreaterEqual(
                    target["width"], 44.0, "%dpx: %r is %.1fpx wide"
                    % (width, target["text"][:30], target["width"]))
                self.assertGreaterEqual(
                    target["height"], 44.0, "%dpx: %r is %.1fpx tall"
                    % (width, target["text"][:30], target["height"]))
        RESULTS["measurements"]["minimumComputedTextPx"] = smallest_text
        RESULTS["measurements"]["minimumFooterTextPx"] = smallest_footer_text
        RESULTS["measurements"]["smallestInteractiveEdge"] = smallest_target
        RESULTS["checks"]["textAndTouchTargetFloors"] = True

    def _desktop_panel_and_targets_ok(self, facts, width):
        """Asserts the desktop nav panel has positive visible width and that
        every visible nav link plus the CTA sits wholly inside both the
        viewport and the header's own field at ``width``. Guards against a
        collapsed (0-width) flex panel pushing its links outside the visible
        header row -- a real prior rendering failure, not a hypothetical
        one. Returns the geometry measured so callers can record it."""
        header = facts["header"]
        panel_rect = header["panelRect"]
        self.assertIsNotNone(panel_rect, "%dpx: no panel rendered" % width)
        self.assertGreater(panel_rect["width"], 0,
                           "%dpx: the desktop nav panel has zero visible width"
                           % width)
        header_rect = header["rect"]
        targets = list(header["navLinks"])
        if header["cta"]:
            targets.append(header["cta"])
        self.assertTrue(targets, "%dpx: no nav links or CTA rendered" % width)
        for link in targets:
            r = link["rect"]
            self.assertGreaterEqual(
                r["x"], -0.5, "%dpx: %r left edge %.1f is outside the viewport"
                % (width, link["text"], r["x"]))
            self.assertLessEqual(
                r["x"] + r["width"], facts["innerWidth"] + 0.5,
                "%dpx: %r right edge %.1f is outside the %dpx viewport"
                % (width, link["text"], r["x"] + r["width"], facts["innerWidth"]))
            self.assertGreaterEqual(
                r["y"], header_rect["y"] - 0.5,
                "%dpx: %r top %.1f sits above the header field"
                % (width, link["text"], r["y"]))
            self.assertLessEqual(
                r["y"] + r["height"], header_rect["y"] + header_rect["height"] + 0.5,
                "%dpx: %r bottom %.1f sits below the header field"
                % (width, link["text"], r["y"] + r["height"]))
        return {"panelWidth": panel_rect["width"], "panelRect": panel_rect}

    # -- 7 : desktop/mobile switch at 940px, DOM order unchanged, hidden ---
    # -- navigation is not focusable ---------------------------------------

    def test_07_the_940px_switch_preserves_dom_order_and_hides_navigation(self):
        wide = self.collapse[940]
        narrow = self.collapse[939]

        self.assertEqual(wide["header"]["summaryDisplay"], "none",
                         "the summary is not hidden at 940px")
        self.assertNotEqual(narrow["header"]["summaryDisplay"], "none",
                            "the summary is hidden below 940px")

        wide_order = [l["text"] for l in wide["header"]["navLinks"]]
        narrow_order = [l["text"] for l in narrow["header"]["navLinks"]]
        self.assertEqual(wide_order, narrow_order,
                         "primary DOM order changed across the 940px switch")
        self.assertEqual(tuple(wide_order), PRIMARY_LABEL_ORDER[:-1])

        self.assertFalse(narrow["header"]["disclosureOpen"],
                         "the mobile disclosure is open by default")
        # Below 940px with the disclosure closed, the native <details> body
        # removes its links from the accessibility tree and tab order; the
        # rendered interactive sweep (isRendered/getClientRects) must not
        # count them. Scoped to inHeader: every primary label is repeated
        # verbatim in the footer's Explore/Company columns (section 2's
        # supplied copy), which stays reachable regardless of the header's
        # disclosure state, so an unscoped page-wide text search would
        # always find the label via its footer twin and never actually
        # test the header disclosure.
        narrow_header_texts = {t["text"] for t in narrow["interactive"]
                               if t["inHeader"]}
        for label in PRIMARY_LABEL_ORDER:
            self.assertNotIn(label, narrow_header_texts,
                             "%r is reachable in the header while the "
                             "closed mobile menu hides it" % label)
        wide_header_texts = {t["text"] for t in wide["interactive"]
                             if t["inHeader"]}
        for label in PRIMARY_LABEL_ORDER:
            self.assertIn(label, wide_header_texts,
                         "%r is not reachable in the header at 940px" % label)

        # The panel must never again collapse to zero width and push nav
        # links/the CTA outside the viewport or the header's own field, at
        # either the 940px collapse boundary or a full desktop width.
        geometry_940 = self._desktop_panel_and_targets_ok(wide, 940)
        geometry_1440 = self._desktop_panel_and_targets_ok(
            self.root_by_width[1440], 1440)

        RESULTS["measurements"]["collapse"] = {
            "940": {"summaryDisplay": wide["header"]["summaryDisplay"],
                    "order": wide_order, "panelWidth": geometry_940["panelWidth"]},
            "939": {"summaryDisplay": narrow["header"]["summaryDisplay"],
                    "order": narrow_order},
            "1440": {"panelWidth": geometry_1440["panelWidth"]},
        }
        RESULTS["checks"]["collapseAt940PreservesOrderHidesNav"] = True

    # -- 8 : keyboard reaches every visible route; rings on warm/ink/footer -

    def test_08_keyboard_order_and_visible_focus_on_warm_ink_and_footer(self):
        stops = self.tab_stops_desktop
        texts = [s["text"] for s in stops]
        for label in PRIMARY_LABEL_ORDER:
            self.assertIn(label, texts, "%r was never reached by Tab" % label)
        self.assertEqual(len(texts), len(set(
            (s["tag"], s["text"], s["inHeader"], s["inFooter"],
             round(s["rect"]["y"], 1)) for s in stops)),
            "a control was reached twice")

        warm = [s for s in stops if s["headerTheme"] == "warm" and s["inHeader"]]
        footer_stops = [s for s in stops if s["inFooter"]]
        self.assertTrue(warm, "focus never landed on the warm header")
        self.assertTrue(footer_stops, "focus never reached the footer")

        rings = []
        for stop in warm[:1] + footer_stops[:1]:
            self.assertNotEqual(stop["outlineStyle"], "none",
                                "%r has no focus outline" % stop["text"])
            ratio = p2.contrast_ratio(stop["outlineColor"], stop["surface"])
            self.assertGreaterEqual(ratio, 3.0,
                                    "%r focus ring is %.2f:1 against its ground"
                                    % (stop["text"], ratio))
            rings.append({"text": stop["text"], "contrast": round(ratio, 2)})
        RESULTS["measurements"]["tabOrder"] = texts
        RESULTS["measurements"]["focusRings"] = rings
        RESULTS["checks"]["keyboardOrderAndVisibleFocus"] = True

    # -- 9 : mobile disclosure keyboard-open, trap, Escape, outside click --

    def test_09_mobile_disclosure_opens_traps_closes_and_restores_focus(self):
        self.assertFalse(self.mobile_closed["header"]["disclosureOpen"])
        self.assertEqual(self.mobile_closed["header"]["summaryLabel"], "Menu")

        self.assertTrue(self.mobile_open["header"]["disclosureOpen"],
                        "Enter on the focused summary did not open the panel")
        self.assertEqual(self.mobile_open["header"]["summaryAriaExpanded"], "true")
        self.assertEqual(self.mobile_open["header"]["summaryLabel"], "Close")
        self.assertEqual(self.mobile_open["documentOverflow"], "hidden",
                         "body scroll was not locked while the panel is open")

        # The open panel must render as an opaque, full-bleed reading
        # surface -- not a transparent overlay through which page content
        # bleeds -- with warm-mode paper background and ink text, its own
        # left edge and width matching the viewport, and its top beginning
        # below the fixed 60px mobile header.
        panel = self.mobile_open["header"]
        self.assertIsNotNone(panel["panelRect"],
                             "no panel rendered while the mobile menu is open")
        bg_rgba = _parse_rgba(panel["panelBackgroundColor"])
        self.assertGreaterEqual(
            bg_rgba[3], 0.999,
            "the open mobile panel background is not opaque: %s"
            % panel["panelBackgroundColor"])
        self.assertGreaterEqual(
            panel["panelOpacity"], 0.999,
            "the open mobile panel opacity is %.3f, not fully opaque"
            % panel["panelOpacity"])
        bg_rgb = tuple(round(c) for c in bg_rgba[:3])
        self.assertEqual(bg_rgb, PAPER_RGB,
                         "the open mobile panel background is %s in warm "
                         "mode, not paper %s" % (bg_rgb, PAPER_RGB))
        fg_rgb = tuple(round(c) for c in _parse_rgb(panel["panelColor"]))
        self.assertEqual(fg_rgb, INK_RGB,
                         "the open mobile panel text is %s in warm mode, "
                         "not ink %s" % (fg_rgb, INK_RGB))

        panel_rect = panel["panelRect"]
        viewport_width = self.mobile_open["innerWidth"]
        self.assertAlmostEqual(
            panel_rect["x"], 0, delta=0.5,
            msg="the open mobile panel left edge is %.1f, not flush with "
                "the viewport" % panel_rect["x"])
        self.assertAlmostEqual(
            panel_rect["width"], viewport_width, delta=0.5,
            msg="the open mobile panel width %.1f does not match the "
                "%dpx viewport" % (panel_rect["width"], viewport_width))
        self.assertGreaterEqual(
            panel_rect["y"], 60 - 0.5,
            "the open mobile panel top %.1f begins above the 60px header"
            % panel_rect["y"])
        RESULTS["measurements"]["mobilePanelOpen"] = {
            "panelRect": panel_rect, "backgroundColor": bg_rgb,
            "color": fg_rgb, "opacity": panel["panelOpacity"],
        }

        trap_texts = [s["text"] for s in self.mobile_trap_stops]
        self.assertTrue(all(s["inHeader"] for s in self.mobile_trap_stops),
                        "Tab left the header navigation surface while the "
                        "mobile panel was open: %s" % trap_texts)
        for label in PRIMARY_LABEL_ORDER:
            self.assertIn(label, trap_texts,
                         "%r is unreachable inside the open mobile panel" % label)

        self.assertFalse(self.mobile_after_escape["header"]["disclosureOpen"],
                         "Escape did not close the mobile panel")
        self.assertEqual(self.mobile_after_escape["documentOverflow"], "",
                         "body scroll was not unlocked after Escape")
        self.assertIsNotNone(self.mobile_focus_after_escape,
                             "focus was lost after Escape")
        self.assertTrue(
            self.mobile_focus_after_escape["tag"] == "SUMMARY"
            or "Menu" in self.mobile_focus_after_escape["text"],
            "focus did not return to the summary after Escape: %s"
            % self.mobile_focus_after_escape)

        self.assertFalse(self.mobile_after_outside_click["header"]["disclosureOpen"],
                         "an outside click did not close the open mobile panel")
        RESULTS["measurements"]["mobileTrapStops"] = trap_texts
        RESULTS["checks"]["mobileDisclosureOpenTrapCloseRestore"] = True

    # -- 10 : sustained down-scroll hides; up-scroll/focus/menu reveal; -----
    # -- the ink carrier adapts the header ----------------------------------

    def test_10_scroll_hide_reveal_and_ink_adaptation(self):
        at_ink = self.header_state_at_ink
        self.assertEqual(at_ink["header"]["theme"], "ink",
                         "the header did not adopt the ink theme over the "
                         "ink carrier (scrollY=%s)" % self.scroll_to_ink)
        ink_bg = tuple(round(c) for c in
                       _parse_rgb(at_ink["header"]["backgroundColor"]))
        ink_fg = tuple(round(c) for c in _parse_rgb(at_ink["header"]["color"]))
        self.assertEqual(ink_bg, INK_RGB,
                         "ink-adapted header background is %s, not %s"
                         % (ink_bg, INK_RGB))
        self.assertEqual(ink_fg, PAPER_RGB,
                         "ink-adapted header foreground is %s, not %s"
                         % (ink_fg, PAPER_RGB))

        self.assertTrue(self.header_state_hidden["header"]["hidden"],
                        "the header did not hide after a sustained "
                        "down-scroll past 160px: %s" % self.scroll_further_down)
        self.assertFalse(self.header_state_revealed["header"]["hidden"],
                         "up-scroll did not reveal the header: %s" % self.scroll_up)
        self.assertFalse(
            self.header_state_after_focus_entry["header"]["hidden"],
            "focus entry did not reveal a hidden header")
        RESULTS["measurements"]["scrollHideReveal"] = {
            "toInk": self.scroll_to_ink, "furtherDown": self.scroll_further_down,
            "up": self.scroll_up, "inkBackground": ink_bg, "inkForeground": ink_fg,
        }
        RESULTS["checks"]["scrollHideRevealAndInkAdaptation"] = True

    # -- 11 : aria-current correct on every route shell; absent on root ----

    def test_11_aria_current_is_correct_on_every_route_and_absent_on_root(self):
        by_production = {r["production"]: r for r in ROUTE_TABLE}
        for production, facts in self.routes.items():
            current_nav = [l["text"] for l in facts["header"]["navLinks"]
                          if l["ariaCurrent"] == "page"]
            current_cta = (facts["header"]["cta"] or {}).get("ariaCurrent") == "page"
            current_footer = [l["text"] for column in facts["footer"]["columns"]
                              for l in column["links"] if l["ariaCurrent"] == "page"]
            if production == "/":
                self.assertEqual(current_nav, [],
                                 "the root marks a nav link current")
                self.assertFalse(current_cta, "the root marks the CTA current")
            else:
                label = by_production[production]["label"]
                marked = set(current_nav + current_footer + (
                    [label] if current_cta else []))
                self.assertIn(label, marked,
                             "%s does not mark %r current anywhere" % (production, label))
                self.assertLessEqual(
                    len(current_nav) + len(current_footer) + (1 if current_cta else 0),
                    2, "%s marks more than one nav+footer instance current"
                    % production)
        RESULTS["checks"]["ariaCurrentCorrectEverywhere"] = True

    # -- 12 : no-JavaScript native disclosure still exposes every route -----

    def test_12_no_javascript_native_disclosure_exposes_every_route(self):
        self.assertEqual(self.no_js["readiness"]["scriptElements"], 1,
                         "expected exactly one <script> element (chrome.js), "
                         "found %d" % self.no_js["readiness"]["scriptElements"])
        self.assertEqual(self.no_js["readiness"]["inlineEventAttributes"], 0,
                         "found an inline event-handler attribute; the "
                         "no-JS page must have no other page script or "
                         "inline handler")

        # chrome.js was network-blocked at the exact local path, not the JS
        # engine; the CDP harness's own Runtime.evaluate calls are what
        # measured everything above and below this line.
        self.assertTrue(
            self.no_js["chromeJsBlocked"].endswith(harness.CHROME_JS_PATH),
            "the blocked URL was not the exact local chrome.js request: %s"
            % self.no_js["chromeJsBlocked"])
        # Exactly one failed request is accepted, and only if it is the
        # exact blocked chrome.js request -- not a broad "any failure whose
        # text mentions BLOCKED" exception. This build's blocked-by-CDP
        # loadingFailed event carries an empty errorText and puts the real
        # reason in blockedReason instead, so that field is checked too.
        self.assertEqual(
            len(self.no_js["failedRequests"]), 1,
            "expected exactly one failed network load (the intentionally "
            "blocked chrome.js request): %s" % self.no_js["failedRequests"])
        blocked = self.no_js["failedRequests"][0]
        self.assertEqual(
            blocked["url"], self.no_js["chromeJsBlocked"],
            "the failed request was not the intentionally blocked "
            "chrome.js request: %s" % blocked)
        self.assertTrue(
            blocked["errorText"] or blocked["blockedReason"],
            "the blocked chrome.js request recorded neither an errorText "
            "nor a blockedReason: %s" % blocked)
        non_block_console_errors = [
            e for e in self.no_js["consoleErrorDetail"]
            if "chrome.js" not in e and "BLOCKED" not in e.upper()]
        self.assertEqual(
            non_block_console_errors, [],
            "the no-JS capture raised console errors unrelated to the "
            "intentional chrome.js block: %s" % non_block_console_errors)

        nav_labels = [l["text"] for l in self.no_js["header"]["navLinks"]]
        for label in PRIMARY_LABEL_ORDER[:-1]:
            self.assertIn(label, nav_labels,
                         "%r is missing from the no-JS DOM" % label)
        self.assertIsNotNone(self.no_js["header"]["cta"],
                             "the assessment CTA is missing from the no-JS DOM")
        footer_labels = {l["text"] for c in self.no_js["footer"]["columns"]
                        for l in c["links"]}
        for label in FOOTER_EXPLORE + FOOTER_COMPANY + FOOTER_TRUST:
            self.assertIn(label, footer_labels,
                         "%r is missing from the no-JS footer" % label)

        # The native <summary>/<details> toggle is a browser behavior, not a
        # chrome.js behavior; a real dispatched mouse click must still open
        # it while chrome.js is blocked.
        self.assertIsNotNone(self.no_js_open_attempt,
                             "the native summary click was never dispatched")
        self.assertTrue(
            self.no_js_open_attempt["header"]["disclosureOpen"],
            "clicking the native <summary> did not open the panel with "
            "chrome.js blocked")
        nav_labels_open = [l["text"] for l in
                          self.no_js_open_attempt["header"]["navLinks"]]
        for label in PRIMARY_LABEL_ORDER[:-1]:
            self.assertIn(label, nav_labels_open,
                         "%r is missing from the opened no-JS panel" % label)
        footer_labels_open = {l["text"] for c in
                              self.no_js_open_attempt["footer"]["columns"]
                              for l in c["links"]}
        for label in FOOTER_EXPLORE + FOOTER_COMPANY + FOOTER_TRUST:
            self.assertIn(label, footer_labels_open,
                         "%r is missing from the no-JS footer once the "
                         "panel is open" % label)

        # Scroll lock and the "Menu"/"Close" label swap are chrome.js
        # behaviors; with chrome.js blocked, neither must appear.
        self.assertNotEqual(
            self.no_js_open_attempt["documentOverflow"], "hidden",
            "the document scrolled-locked without chrome.js running")
        self.assertEqual(
            self.no_js_open_attempt["header"]["summaryLabel"], "Menu",
            "the summary label synced to chrome.js's \"Close\" state "
            "without chrome.js running")
        RESULTS["checks"]["noJavaScriptDisclosureExposesEveryRoute"] = True

    # -- 13 : reduced motion removes transitions without changing anything -

    def test_13_reduced_motion_is_layout_and_content_safe(self):
        normal = self.root_by_width[390]
        reduced = self.reduced
        self.assertEqual(reduced["boxes"], normal["boxes"],
                         "reduced motion changed the layout")
        self.assertEqual([n["text"] for n in reduced["textNodes"]],
                         [n["text"] for n in normal["textNodes"]],
                         "reduced motion changed the content")
        self.assertEqual(
            [l["ariaCurrent"] for l in reduced["header"]["navLinks"]],
            [l["ariaCurrent"] for l in normal["header"]["navLinks"]],
            "reduced motion changed the active route")
        RESULTS["checks"]["reducedMotionLayoutContentSafe"] = True

    # -- 14 : local-only requests, zero console errors, owned-file scope ---

    def test_14_local_only_zero_console_errors_and_owned_scope(self):
        remote = []
        for production, facts in self.routes.items():
            for url in facts.get("requests", []):
                if not url.startswith(("http://127.0.0.1:", "data:", "about:")):
                    remote.append((production, url))
            self.assertEqual(facts.get("consoleErrors", 0), 0,
                             "%s console errors: %s"
                             % (production, facts.get("consoleErrorDetail")))
            self.assertEqual(facts.get("httpErrorResponses", []), [],
                             "%s HTTP errors: %s"
                             % (production, facts.get("httpErrorResponses")))
            self.assertEqual(facts["externalLinks"], [],
                             "%s references an off-origin URL" % production)
        self.assertEqual(remote, [], "requests left 127.0.0.1: %s" % remote)

        scope = harness.owned_scope()
        self.assertEqual(scope["outOfScope"], [],
                         "out-of-P3-scope files changed: %s" % scope["outOfScope"])
        protected = harness.protected_byte_identity()
        self.assertEqual(protected["missing"], [], "a protected file was deleted")
        self.assertEqual(protected["differing"], [],
                         "protected files changed: %s" % protected["differing"])
        self.assertGreater(protected["compared"], 10,
                           "the byte-identity comparison covered too little")
        RESULTS["measurements"]["scope"] = scope
        RESULTS["measurements"]["protectedByteIdentity"] = protected
        RESULTS["checks"]["localOnlyNoConsoleErrorsOwnedScope"] = True


def _parse_rgb(css_color: str):
    import re
    values = re.findall(r"[\d.]+", css_color or "")
    return [float(v) for v in values[:3]] if values else [0.0, 0.0, 0.0]


def _parse_rgba(css_color: str):
    """Like ``_parse_rgb`` but keeps the alpha channel (defaulting to fully
    opaque for a 3-channel color and fully transparent when unparseable),
    so callers can tell a genuinely opaque paper/ink surface apart from one
    that merely composites to the right color over an opaque ancestor."""
    import re
    values = [float(v) for v in re.findall(r"[\d.]+", css_color or "")]
    if len(values) >= 4:
        return values[:4]
    if len(values) == 3:
        return values + [1.0]
    return [0.0, 0.0, 0.0, 0.0]


def _write_results():
    target = os.environ.get("DAGG_P3_TEST_JSON")
    if not target:
        return
    RESULTS["coverage"] = sorted(set(RESULTS["coverage"]))
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    Path(target).write_text(json.dumps(RESULTS, indent=2, sort_keys=True,
                                       default=str) + "\n")


atexit.register(_write_results)


if __name__ == "__main__":
    unittest.main(verbosity=2)
