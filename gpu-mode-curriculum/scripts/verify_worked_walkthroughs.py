#!/usr/bin/env python3
"""Verify worked walkthroughs are concrete and tied to real artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WALKTHROUGHS = ROOT / "worked-walkthroughs"
SITE = ROOT / "site"
SECTIONS = [
    "## Claim",
    "## Read The Code",
    "## Predict",
    "## Run",
    "## Change One Thing",
    "## Explain The Result",
]
FORBIDDEN = [
    "cutting edge",
    "game changer",
    "seamless",
    "robust",
    "synergy",
    "leverage",
    "best practice",
    "deep dive",
    "end to end",
    "unlock",
    "world class",
]
CODE_RE = re.compile(r"`([^`]+)`")


def main() -> int:
    failures: list[str] = []
    notes = sorted(path for path in WALKTHROUGHS.glob("*.md") if path.name != "README.md")
    if len(notes) < 8:
        failures.append(f"expected at least 8 walkthroughs, found {len(notes)}")
    if not (SITE / "worked-walkthroughs.html").exists():
        failures.append("missing site/worked-walkthroughs.html")
    for note in notes:
        text = note.read_text(encoding="utf-8")
        lower = text.lower()
        for section in SECTIONS:
            if section not in text:
                failures.append(f"{note}: missing {section}")
        if "```bash" not in text:
            failures.append(f"{note}: missing runnable bash block")
        for phrase in FORBIDDEN:
            if phrase in lower:
                failures.append(f"{note}: forbidden vague phrase {phrase!r}")
        for ref in CODE_RE.findall(text):
            candidate = ref.split()[0]
            if "/" in candidate and not (ROOT / candidate).exists():
                failures.append(f"{note}: missing referenced path {candidate}")
    facts = {
        "walkthroughs": len(notes),
        "site_page": str(SITE / "worked-walkthroughs.html"),
        "required_sections": len(SECTIONS),
    }
    print(json.dumps({"facts": facts, "failures": failures}, indent=2))
    if failures:
        return 1
    print("GPUMODE worked walkthrough verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
