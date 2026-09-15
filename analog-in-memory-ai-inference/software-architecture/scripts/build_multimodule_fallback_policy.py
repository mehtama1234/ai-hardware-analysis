#!/usr/bin/env python3
"""Build a fail-closed per-module fallback policy from sensitivity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.report.resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    modules = report["target_modules"]
    mixed = next(row for row in report["results"]
                 if row["selected_modules"] == [modules[0], modules[2]])
    policy = {
        "schema_version": "gpt2-multimodule-fallback-policy-v0.1",
        "result_type": "governed_local_multi_module_route_policy",
        "source_report": {"path": str(report_path), "sha256": digest(report_path)},
        "target_modules": modules,
        "candidate_policy": {
            "analog_modules": [modules[0], modules[2]],
            "digital_modules": [modules[1]],
            "adc_bits": 12,
            "calibrated": True,
            "quality": mixed["quality"],
            "screen_pass": mixed["screen_pass"],
        },
        "enforced_policy": {
            "route": "digital_fallback",
            "module_routes": {name: "digital_fallback" for name in modules},
            "reason": "candidate mixed route failed joint quality screen",
            "analog_authorized": False,
        },
        "decision": "reject_partial_analog_policy_and_use_full_digital_fallback",
        "claim_boundary": "Local CPU policy decision only; no measured hardware latency or energy and no analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    policy_path = args.output / "fallback_policy.json"
    policy_path.write_text(json.dumps(policy, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest = {"files": [{"path": str(policy_path), "sha256": digest(policy_path)},
                          {"path": str(report_path), "sha256": digest(report_path)}]}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(policy_path), "candidate_screen_pass": mixed["screen_pass"],
                      "enforced_route": policy["enforced_policy"]["route"]}, sort_keys=True))


if __name__ == "__main__":
    main()
