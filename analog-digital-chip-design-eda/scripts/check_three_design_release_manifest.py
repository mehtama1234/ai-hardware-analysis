#!/usr/bin/env python3
"""Independently verify the aggregate three-design release manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    report = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = []
    if report.get("schema_version") != "three-design-closed-loop-release-manifest-v1": errors.append("unexpected schema")
    if report.get("status") != "passed" or report.get("design_count") != 4: errors.append("release is not a passed four-design aggregate")
    for design, item in report.get("designs", {}).items():
        path = Path(item.get("handoff_path", ""))
        if not path.is_file() or digest(path) != item.get("handoff_sha256"): errors.append(f"{design}: handoff hash mismatch")
        physical = item.get("physical", {})
        if item.get("status") != "passed" or physical.get("flow_status") != "flow completed" or physical.get("source_match") is not True or physical.get("lvs_errors") != 0 or physical.get("gds_present") is not True: errors.append(f"{design}: physical evidence incomplete")
        formal = item.get("formal", {})
        suite = Path(formal.get("suite_path", ""))
        if formal.get("status") != "passed" or formal.get("property_count", 0) < 1 or not suite.is_file() or digest(suite) != formal.get("suite_sha256"): errors.append(f"{design}: formal property suite incomplete or hash mismatch")
        temporal = item.get("temporal", {})
        if temporal.get("status") != "not-required":
            temporal_suite = Path(temporal.get("suite_path", ""))
            if temporal.get("status") != "passed" or temporal.get("property_count", 0) < 1 or not temporal_suite.is_file() or digest(temporal_suite) != temporal.get("suite_sha256"): errors.append(f"{design}: temporal property suite incomplete or hash mismatch")
        stateful = item.get("stateful_formal", {})
        if stateful.get("status") != "not-required":
            stateful_suite = Path(stateful.get("suite_path", ""))
            if stateful.get("status") != "passed" or stateful.get("assertion_count", 0) < 1 or not stateful_suite.is_file() or digest(stateful_suite) != stateful.get("suite_sha256"): errors.append(f"{design}: stateful formal suite incomplete or hash mismatch")
    colab = Path(report.get("colab_model_evaluation", {}).get("path", ""))
    if not colab.is_file() or digest(colab) != report.get("colab_model_evaluation", {}).get("sha256"): errors.append("Colab report hash mismatch")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "design_count": 4, "designs": sorted(report["designs"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
