#!/usr/bin/env python3
"""Check the frozen P1 vertical-slice copy and emit a reproducible JSON gate."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COPY_PATH = ROOT / "design/golden-standard/narrative/VERTICAL-SLICE-COPY.md"
OUTPUT_PATH = ROOT / "evidence/P1R1/copy-check.json"

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[’'\-][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*")
NON_DEFAULT_DECISION_STATES = {"Simplify", "Automate", "Rebuild", "Retire"}
NON_DEFAULT_WORKGRAPH_STATES = {"Decide", "Build", "Govern", "Operate"}
NON_DEFAULT_FACTORY_STATES = {"Rebuild what should change"}


def word_count(value: str) -> int:
    return len(WORD_RE.findall(value))


def field_values(lines: list[str], label: str) -> list[str]:
    marker = f"**{label}**"
    values: list[str] = []
    for index, line in enumerate(lines):
        if line.strip() != marker:
            continue
        cursor = index + 1
        blocks: list[str] = []
        while cursor < len(lines):
            value = lines[cursor].strip()
            if value.startswith("**") or value.startswith("## ") or value.startswith("### ") or value == "---":
                break
            if value:
                blocks.append(value.removeprefix("- "))
            cursor += 1
        values.append(" ".join(blocks))
    return values


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.index(marker)
    next_section = text.find("\n## ", start + len(marker))
    return text[start:] if next_section == -1 else text[start:next_section]


def public_lines(lines: list[str]) -> list[tuple[int, str, str | None]]:
    start = next(index for index, line in enumerate(lines) if line.startswith("## Global navigation"))
    section: str | None = None
    state: str | None = None
    output: list[tuple[int, str, str | None]] = []

    for index, raw in enumerate(lines[start + 1 :], start=start + 2):
        value = raw.strip()
        if value.startswith("## "):
            section = value.removeprefix("## ")
            state = None
            continue
        if value.startswith("### "):
            state = value.removeprefix("### ")
            output.append((index, state, state))
            continue
        if not value or value == "---" or value.startswith("**"):
            continue
        output.append((index, value.removeprefix("- "), state if section else None))
    return output


def main() -> int:
    text = COPY_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    visible = public_lines(lines)
    all_copy = " ".join(value for _, value, _ in visible)

    default_values: list[str] = []
    section = ""
    current_state: str | None = None
    start = next(index for index, line in enumerate(lines) if line.startswith("## Global navigation"))
    for raw in lines[start + 1 :]:
        value = raw.strip()
        if value.startswith("## "):
            section = value.removeprefix("## ")
            current_state = None
            continue
        if value.startswith("### "):
            current_state = value.removeprefix("### ")
            default_values.append(current_state)
            continue
        if not value or value == "---" or value.startswith("**"):
            continue
        hidden_decision = section.startswith("3 ·") and current_state in NON_DEFAULT_DECISION_STATES
        hidden_workgraph = section.startswith("4 ·") and current_state in NON_DEFAULT_WORKGRAPH_STATES
        hidden_factory = section.startswith("5 ·") and current_state in NON_DEFAULT_FACTORY_STATES
        if not hidden_decision and not hidden_workgraph and not hidden_factory:
            default_values.append(value.removeprefix("- "))

    h1_values = field_values(lines, "H1")
    h2_values = field_values(lines, "H2")
    body_values = field_values(lines, "Body")
    disclosure = "All artifacts on this page are constructed examples, not client data or production deployments."
    hero = section_text(text, "1 · Hero")
    workgraph = section_text(text, "4 · WorkGraph")
    factory = section_text(text, "5 · Factory")
    operating = section_text(text, "6 · Govern, operate and prove")
    workgraph_fields = [
        "Source:", "Captured state:", "System:", "Work item:", "Owner:",
        "Exception:", "Decision state:", "Permission:", "Provenance:",
    ]
    rebuild_fields = [
        "Intervention:", "Target workflow:", "Application boundary:", "Interfaces:",
        "Behavior:", "Acceptance test:", "Release owner:", "Way back:",
    ]
    required_lines = [
        "Five outcomes. The build is a result, never a premise.",
        "Each decision, evaluation and operating record can strengthen the next intervention.",
        "Reusable tools and evaluations improve the next build.",
        "The delivery system is designed to keep client-specific context out of reusable cross-engagement patterns.",
        "Intervention: prepare the payment draft; preserve human release.",
        "Prepare a supplier payment draft for Finance review from approved company records.",
        "a source mismatch withholds the draft from release and routes the exception to the Finance owner.",
        "The agent prepares a payment draft from approved sources. It remains withheld from release.",
        "The Finance owner confirms the exception and returns the item for source correction.",
        "No payment proceeds. The decision and evidence remain recorded; the agent can be disabled and the item returned to the manual queue.",
    ]
    forbidden = [
        "10x", "100x", "1000x", "fully autonomous", "Systems operated",
        "proprietary mechanism", "payment proposal",
    ]

    checks: dict[str, bool] = {
        "one_h1": len(h1_values) == 1,
        "h1_6_to_12_words": len(h1_values) == 1 and 6 <= word_count(h1_values[0]) <= 12,
        "all_h2_4_to_9_words": bool(h2_values) and all(4 <= word_count(value) <= 9 for value in h2_values),
        "hero_body_18_to_32_words": bool(body_values) and 18 <= word_count(body_values[0]) <= 32,
        "other_body_blocks_20_to_45_words": len(body_values) > 1 and all(20 <= word_count(value) <= 45 for value in body_values[1:]),
        "default_visible_copy_600_to_800_words": 600 <= word_count(" ".join(default_values)) <= 800,
        "all_interactive_copy_at_most_1100_words": word_count(all_copy) <= 1100,
        "one_shared_page_disclosure_in_hero": text.count(disclosure) == 1 and disclosure in hero,
        "hero_provenance_present": "Representative WorkGraph record · synthetic data" in hero,
        "workgraph_local_provenance_present": "Representative WorkGraph record · synthetic data" in workgraph,
        "factory_local_provenance_present": "Illustrative Factory build plan · not a client deployment" in factory,
        "operating_local_provenance_present": "Illustrative operating record · constructed example" in operating,
        "workgraph_record_schema_complete": all(field in workgraph for field in workgraph_fields),
        "factory_automate_mode_complete": "### Automate what stays" in factory and all(field in factory for field in ["Context:", "Tools:", "Permission:", "Evaluation:", "Release owner:", "Way back:"]),
        "factory_rebuild_mode_complete": "### Rebuild what should change" in factory and all(field in factory for field in rebuild_fields),
        "required_narrative_lines_present": all(line in text for line in required_lines),
        "forbidden_claims_absent": all(term.lower() not in all_copy.lower() for term in forbidden),
    }

    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    git_dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    )
    source_hash = hashlib.sha256(COPY_PATH.read_bytes()).hexdigest()
    checker_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    report = {
        "source": str(COPY_PATH.relative_to(ROOT)),
        "source_sha256": source_hash,
        "checker": str(Path(__file__).resolve().relative_to(ROOT)),
        "checker_sha256": checker_hash,
        "git_head_at_generation": git_head,
        "working_tree_dirty_at_generation": git_dirty,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "measurements": {
            "h1_words": [word_count(value) for value in h1_values],
            "h2_words": [word_count(value) for value in h2_values],
            "body_block_words": [word_count(value) for value in body_values],
            "default_visible_words": word_count(" ".join(default_values)),
            "all_interactive_words": word_count(all_copy),
            "shared_disclosures": text.count(disclosure),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
