#!/usr/bin/env python3
"""Verify the trained-model serving bridge without rerunning training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    checks = report.get("checks", {})
    profile = report.get("model_profile", {})
    required = {
        "report_passed": report.get("status") == "passed",
        "trained_model": profile.get("trained") is True,
        "quality_gate": profile.get("quality_passed") is True,
        "serving_quality_gate": checks.get("trained_quality_gate") is True,
        "candidate_parity": checks.get("serving_search_candidates_accepted") is True,
        "candidate_selected": checks.get("serving_search_selection_present") is True,
        "all_requests_completed": checks.get("all_requests_completed") is True,
        "output_nonempty": checks.get("all_outputs_nonempty") is True,
    }
    result = {"status": "passed" if all(required.values()) else "failed", "checks": required}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
