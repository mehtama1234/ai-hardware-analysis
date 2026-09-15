#!/usr/bin/env python3
"""Classify sampled-storage versus preamp motion in a SAR handoff probe."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(report: dict) -> dict:
    probe = report.get("handoff_probe", {})
    pre = [float(row["preamp_diff_v"]) for row in probe.values() if "preamp_diff_v" in row]
    active = [float(row["active_handoff_diff_v"]) for row in probe.values() if "active_handoff_diff_v" in row]
    sample = active or [float(row["sample_diff_v"]) for row in probe.values() if "sample_diff_v" in row]
    pre_range = max(pre) - min(pre) if pre else None
    sample_range = max(sample) - min(sample) if sample else None
    frozen = bool(pre_range is not None and sample_range is not None and pre_range > 0.05 and sample_range < 1e-4)
    switched = bool(report.get("switched_handoff_enabled"))
    status = "legacy_storage_not_active_handoff" if switched and not active else ("active_handoff_frozen_during_preamp_transition" if frozen else "insufficient_or_nonfrozen_probe")
    return {"status": status, "probe_points": len(probe), "preamp_range_v": pre_range, "active_handoff_range_v": max(active) - min(active) if active else None, "sample_range_v": sample_range, "sample_storage_frozen": frozen and not switched, "active_handoff_measured": bool(active), "switched_handoff_enabled": switched, "source_status": report.get("status"), "decision_values": report.get("decision_values"), "final_codes": [r.get("final_code") for r in report.get("conversions", [])]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("summary", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    summary = json.loads(args.summary.read_text())
    corners = {}
    for name, case in summary.get("cases", {}).items():
        report = case.get("report", {})
        if report:
            corners[name] = analyze(report)
    result = {"schema_version": "handoff-trajectory-diagnosis-v0.1", "result_type": "sar_handoff_trajectory_diagnosis", "campaign_summary": str(args.summary), "corners": corners, "claim_boundary": "Trajectory diagnosis only. When switched handoff is enabled, legacy sp/sn measurements are not evidence about the active handoff path; the active handoff nodes must be measured before assigning a storage failure."}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"corners": corners, "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
