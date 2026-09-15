"""Independently validate the cross-sim historical parasitics replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("report", type=Path); args = parser.parse_args(); report = json.loads(args.report.read_text(encoding="utf-8")); errors = []
    expected = {"schema_version": "cross-sim-historical-parasitics-agent-repair-report-v1", "repository": "cross-sim", "historical_fix_commit": "d9548c0", "historical_source_revision": "d9548c0^", "source_file": "simulator/circuits/array_simulator.py", "baseline_status": "failed", "agent_status": "available", "patch_candidate_status": "review_required", "repaired_status": "passed", "canonical_unchanged": True, "status": "passed"}
    for key, value in expected.items():
        if report.get(key) != value: errors.append(f"{key} expected {value!r}, got {report.get(key)!r}")
    unsigned = dict(report); recorded = unsigned.pop("report_sha256", None)
    if recorded != digest(unsigned): errors.append("report digest mismatch")
    result = {"schema_version": "cross-sim-historical-parasitics-agent-repair-check-v1", "status": "passed" if not errors else "blocked", "errors": errors, "report": str(args.report)}; result["check_sha256"] = digest(result); print(json.dumps(result, sort_keys=True)); return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
