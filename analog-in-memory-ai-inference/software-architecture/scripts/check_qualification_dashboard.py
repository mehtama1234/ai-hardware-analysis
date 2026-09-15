#!/usr/bin/env python3
"""Check that the human review dashboard reflects the guarded gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dashboard", type=Path)
    ap.add_argument("gate", type=Path)
    args = ap.parse_args()
    html = args.dashboard.read_text()
    gate = json.loads(args.gate.read_text())
    errors = []
    decision = gate.get("decision")
    labels = {
        "retain_native_digital_gpu_execution": "Retain native digital GPU execution",
        "authorized_analog_execution": "Authorize analog execution",
    }
    if labels.get(decision, decision) not in html:
        errors.append("dashboard decision does not match gate")
    if gate.get("open_items") and "Analog execution is not authorized" not in html:
        errors.append("dashboard omits the open-gate warning")
    result = {"status": "passed" if not errors else "failed", "decision": decision, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
