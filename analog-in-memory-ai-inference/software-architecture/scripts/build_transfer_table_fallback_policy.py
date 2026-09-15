#!/usr/bin/env python3
"""Create an explicit per-code fallback policy from a partial circuit table."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("circuit_table", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    table = json.loads(args.circuit_table.read_text(encoding="utf-8"))
    present = {int(code) for code in table["rows"]}
    routes = {}
    for code in range(table["requested_code_count"]):
        if code in present:
            routes[str(code)] = {"status": "measured_diagnostic_only", "route": "digital_fallback",
                                 "reason": "partial table cannot authorize any code for workload use"}
        else:
            routes[str(code)] = {"status": "unsupported", "route": "digital_fallback",
                                 "reason": "no circuit receipt exists for this code"}
    output = {
        "schema_version": "sky130-transfer-table-fallback-policy-v0.1",
        "result_type": "local_partial_transfer_table_fallback_policy",
        "source_table": {"path": str(args.circuit_table), "sha256": digest(args.circuit_table)},
        "requested_code_count": 16, "routes": routes,
        "unsupported_codes": [code for code in range(16) if code not in present],
        "measured_diagnostic_only_codes": sorted(present),
        "overall_route": "digital_fallback",
        "analog_authorized": False,
        "claim_boundary": "Local per-code fallback policy from an incomplete circuit table; no code authorizes analog workload execution or hardware acceptance.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "transfer_table_fallback_policy.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        {"path": str(args.circuit_table), "sha256": digest(args.circuit_table)},
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "unsupported_codes": output["unsupported_codes"],
                      "overall_route": output["overall_route"]}, sort_keys=True))


if __name__ == "__main__":
    main()
