#!/usr/bin/env python3
"""Verify first-principles teaching notes exist and avoid vague stock prose."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
TEACHING = ROOT / "teaching"
SITE = ROOT / "site"
REQUIRED_SECTIONS = [
    "## First Question",
    "## What The Code Does",
    "## What The Measurement Proves",
    "## What It Does Not Prove",
    "## Read Next",
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
CODE_PATH_RE = re.compile(r"`([^`]+)`")


def main() -> int:
    failures: list[str] = []
    notes = sorted(path for path in TEACHING.glob("*.md") if path.name != "README.md")
    if len(notes) < 11:
        failures.append(f"expected at least 11 teaching notes, found {len(notes)}")
    if not (SITE / "teaching.html").exists():
        failures.append("missing site/teaching.html")
    for note in notes:
        text = note.read_text(encoding="utf-8")
        lower = text.lower()
        for section in REQUIRED_SECTIONS:
            if section not in text:
                failures.append(f"{note}: missing {section}")
        for phrase in FORBIDDEN:
            if phrase in lower:
                failures.append(f"{note}: forbidden vague phrase {phrase!r}")
        code_refs = text.count("`")
        if code_refs < 6:
            failures.append(f"{note}: expected code path references")
        for match in CODE_PATH_RE.findall(text):
            candidate = match.split()[0]
            if candidate.startswith(("http://", "https://")):
                continue
            if "/" in candidate and not (ROOT / candidate).exists():
                failures.append(f"{note}: missing referenced path {candidate}")
    facts = {
        "teaching_notes": len(notes),
        "site_page": str(SITE / "teaching.html"),
        "required_sections": len(REQUIRED_SECTIONS),
        "forbidden_phrases": FORBIDDEN,
    }
    print(json.dumps({"facts": facts, "failures": failures}, indent=2))
    if failures:
        return 1
    print("GPUMODE teaching page verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
