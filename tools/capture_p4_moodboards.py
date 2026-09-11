#!/usr/bin/env python3
"""Capture the P4 moodboards with the installed Google Chrome over CDP.

The script reuses the accepted P2 Chrome and immutable-preview plumbing. It
does not use Playwright or a bundled browser. One local snapshot produces all
screenshots and measurements.
"""

from __future__ import annotations

import base64
import json
import tempfile
import urllib.request
from pathlib import Path

from capture_p2_evidence import (
    CDP,
    Page,
    WAIT_FOR_PAINT,
    start_chrome,
    start_server,
    stop_server,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "evidence" / "P4" / "moodboards"
PAGE_PATH = "/preview/golden-standard/p4/moodboards/"
BOARD_IDS = ("decision-field", "machine-signal", "operational-evidence")


class MoodboardPage(Page):
    """P2 browser plumbing without the P2-foundations-only DOM probe."""

    def open(self, url: str, width: int, height: int | None = None,
             reduced_motion: bool = False):
        self.cdp.events.clear()
        self.requests = []
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height or (1000 if width >= 600 else 844),
            "deviceScaleFactor": 1,
            "mobile": width < 600,
        }, session_id=self.session)
        self.set_reduced_motion(reduced_motion)
        self.cdp.call("Page.navigate", {"url": url}, session_id=self.session)
        self.cdp.wait_for_event("Page.loadEventFired")
        readiness = self.evaluate(WAIT_FOR_PAINT, await_promise=True)
        facts = {
            "readiness": readiness,
            "reducedMotion": reduced_motion,
        }
        facts.update(self.collect_events())
        return facts


def write_png(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def capture_clip(page: Page, selector: str) -> bytes:
    rect = page.evaluate(
        """(() => {
          const el = document.querySelector(%s);
          if (!el) throw new Error('missing capture target');
          const r = el.getBoundingClientRect();
          return {x: r.left + scrollX, y: r.top + scrollY,
                  width: r.width, height: r.height};
        })()""" % json.dumps(selector)
    )
    shot = page.cdp.call(
        "Page.captureScreenshot",
        {
            "format": "png",
            "captureBeyondViewport": True,
            "fromSurface": True,
            "clip": {**rect, "scale": 1},
        },
        session_id=page.session,
    )
    return base64.b64decode(shot["data"])


def measurements(page: Page) -> dict:
    return page.evaluate(
        """(() => {
          const visible = el => {
            const c = getComputedStyle(el), r = el.getBoundingClientRect();
            return c.display !== 'none' && c.visibility !== 'hidden' &&
                   Number(c.opacity) > 0 && r.width > 0 && r.height > 0;
          };
          const textNodes = [...document.querySelectorAll('body *')]
            .filter(el => visible(el) && [...el.childNodes].some(n =>
              n.nodeType === Node.TEXT_NODE && n.textContent.trim()));
          const sizes = textNodes.map(el => parseFloat(getComputedStyle(el).fontSize));
          const images = [...document.images].map(img => ({
            src: new URL(img.currentSrc || img.src).pathname,
            complete: img.complete,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            renderedWidth: img.getBoundingClientRect().width,
            renderedHeight: img.getBoundingClientRect().height,
          }));
          return {
            viewport: {width: innerWidth, height: innerHeight},
            document: {scrollWidth: document.documentElement.scrollWidth,
                       clientWidth: document.documentElement.clientWidth,
                       scrollHeight: document.documentElement.scrollHeight},
            noHorizontalOverflow:
              document.documentElement.scrollWidth === document.documentElement.clientWidth,
            minVisibleTextPx: Math.min(...sizes),
            imageCount: images.length,
            brokenImages: images.filter(i => !i.complete || i.naturalWidth === 0),
            images,
            boardRects: [...document.querySelectorAll('[data-board]')].map(el => {
              const r = el.getBoundingClientRect();
              return {id: el.id, width: r.width, height: r.height,
                      top: r.top + scrollY};
            }),
          };
        })()"""
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    server = chrome = cdp = None
    report: dict = {"page": PAGE_PATH, "viewports": {}, "captures": []}
    try:
        server, base, startup_seconds = start_server(port=0)
        report["serverStartupSeconds"] = startup_seconds
        with urllib.request.urlopen(base + "/__revision") as response:
            report["revision"] = json.loads(response.read())

        with tempfile.TemporaryDirectory(prefix="dagg-p4-moodboards-") as tmp:
            chrome, ws_url, chrome_path = start_chrome(Path(tmp))
            report["chrome"] = chrome_path
            cdp = CDP(ws_url)
            page = MoodboardPage(cdp)
            url = base + PAGE_PATH

            desktop = page.open(url, 1440, 1000)
            desktop.update(measurements(page))
            report["viewports"]["1440x1000"] = desktop
            intro_path = OUTPUT_DIR / "00-intro-1440x1000.png"
            write_png(intro_path, page.screenshot(beyond_viewport=False))
            report["captures"].append(str(intro_path.relative_to(REPO_ROOT)))

            for board_id in BOARD_IDS:
                path = OUTPUT_DIR / (board_id + "-full-1440.png")
                write_png(path, capture_clip(page, "#" + board_id))
                report["captures"].append(str(path.relative_to(REPO_ROOT)))

            for width, height in ((390, 844), (320, 568)):
                facts = page.open(url, width, height)
                facts.update(measurements(page))
                report["viewports"][f"{width}x{height}"] = facts
                for board_id in BOARD_IDS:
                    page.evaluate(
                        """new Promise(resolve => {
                          document.documentElement.style.scrollBehavior = 'auto';
                          document.getElementById(%s).scrollIntoView({
                            block: 'start', behavior: 'instant'
                          });
                          requestAnimationFrame(() => requestAnimationFrame(resolve));
                        })""" % json.dumps(board_id),
                        await_promise=True,
                    )
                    path = OUTPUT_DIR / f"{board_id}-top-{width}.png"
                    write_png(path, page.screenshot(beyond_viewport=False))
                    report["captures"].append(str(path.relative_to(REPO_ROOT)))

            page.open(url, 390, 844, reduced_motion=True)
            reduced_path = OUTPUT_DIR / "reduced-motion-390.png"
            write_png(reduced_path, page.screenshot(beyond_viewport=False))
            report["captures"].append(str(reduced_path.relative_to(REPO_ROOT)))
            report["reducedMotion"] = measurements(page)

        hard_failures = []
        for name, facts in report["viewports"].items():
            if not facts["noHorizontalOverflow"]:
                hard_failures.append(f"horizontal overflow at {name}")
            if facts["brokenImages"]:
                hard_failures.append(f"broken images at {name}")
            if facts["consoleErrors"]:
                hard_failures.append(f"console errors at {name}")
            if facts["failedRequests"] or facts["httpErrorResponses"]:
                hard_failures.append(f"request failures at {name}")
            if facts["minVisibleTextPx"] < 12:
                hard_failures.append(f"text below 12px at {name}")
        report["hardFailures"] = hard_failures
        report["passed"] = not hard_failures
        (OUTPUT_DIR / "result.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        print(json.dumps({
            "passed": report["passed"],
            "hardFailures": hard_failures,
            "output": str((OUTPUT_DIR / "result.json").relative_to(REPO_ROOT)),
            "captures": report["captures"],
        }, indent=2))
        return 0 if report["passed"] else 1
    finally:
        if cdp is not None:
            cdp.close()
        if chrome is not None and chrome.poll() is None:
            chrome.terminate()
            chrome.wait(timeout=10)
        if server is not None:
            stop_server(server)


if __name__ == "__main__":
    raise SystemExit(main())
