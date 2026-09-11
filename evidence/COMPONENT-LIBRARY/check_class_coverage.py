#!/usr/bin/env python3
"""Static check: every class used in the specimen HTML has a CSS rule.

    python3 evidence/COMPONENT-LIBRARY/check_class_coverage.py

P4R5 rule 5 says machine tests do not overrule visible rendering failures, and
the most common cause of a visible rendering failure in this specimen is the
opposite of a broken test: markup that was written against CSS that was never
added, so the block renders unstyled. This check names those classes.

It reads only the specimen HTML plus the two stylesheets it links (the frozen
P2 tokens and the accepted P3 chrome), so it needs no browser and no network.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPECIMEN = REPO_ROOT / "preview" / "golden-standard" / "component-library"
SYSTEM = REPO_ROOT / "design" / "golden-standard" / "system"

# Classes that exist only as JavaScript state hooks or as inert specimen
# markers. They are toggled at runtime and may legitimately have no rule of
# their own beyond the compound selectors that read them.
STATE_ONLY = {
    "cl-enhanced",
    "is-active",
    "is-boundary",
    "is-coarse",
    "is-current",
    "is-decision",
    "is-done",
    "is-focus",
    "is-hold",
    "is-hover",
    "on-ink",
}


def classes_used(html: str) -> set[str]:
    out: set[str] = set()
    for match in re.finditer(r'class="([^"]*)"', html):
        out.update(match.group(1).split())
    return out


def classes_defined(*sheets: str) -> set[str]:
    return set(re.findall(r"\.([A-Za-z][\w-]*)", "\n".join(sheets)))


def main() -> int:
    html = (SPECIMEN / "index.html").read_text()
    sheets = [
        (SPECIMEN / "styles.css").read_text(),
        (SYSTEM / "chrome.css").read_text(),
        (SYSTEM / "tokens.css").read_text(),
    ]
    missing = sorted(
        (classes_used(html) - classes_defined(*sheets)) - STATE_ONLY)
    if missing:
        print("Classes used in index.html with no CSS rule anywhere:")
        for name in missing:
            print("  .%s" % name)
        return 1
    print("Every class used in index.html has at least one CSS rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
