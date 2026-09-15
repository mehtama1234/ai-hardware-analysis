#!/usr/bin/env python3
"""Verify the retained first- and second-order stateful comparison boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    report_path = args.package / "stateful_transfer_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    results = report.get("results", {})
    expected = {
        "stateful_previous_token_original": True,
        "stateful_previous_token_stress": True,
        "stateful_previous_token_third_holdout": False,
        "stateful_previous_two_tokens_original": True,
        "stateful_previous_two_tokens_stress": False,
        "stateful_previous_two_tokens_third_holdout": False,
    }
    for name, expected_pass in expected.items():
        actual = results.get(name, {}).get("quality", {}).get("screen_pass")
        if actual is not expected_pass:
            failures.append(f"{name} expected screen_pass={expected_pass}, got {actual}")
    if report.get("analog_authorized") is not False:
        failures.append("stateful comparison authorized analog execution")
    boundary = report.get("claim_boundary", "")
    if "Local CPU" not in boundary or "analog authorization" not in boundary:
        failures.append("claim boundary is too broad")
    print(json.dumps({
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "finding": "first-order stateful correction passes two splits but fails the third; second-order correction fails stress and third holdout.",
        "claim_boundary": boundary,
    }, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
