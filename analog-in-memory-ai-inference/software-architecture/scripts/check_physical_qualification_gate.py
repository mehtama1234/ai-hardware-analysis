#!/usr/bin/env python3
"""Verify the model-to-chip qualification gate and its source artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(obj: dict) -> str:
    body = dict(obj)
    body.pop("artifact_sha256", None)
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("gate", type=Path)
    ap.add_argument("--require-analog", action="store_true")
    args = ap.parse_args()
    gate = json.loads(args.gate.read_text())
    errors: list[str] = []
    if gate.get("schema_version") != "physical-qualification-gate-v0.1":
        errors.append("unsupported schema")
    if gate.get("artifact_sha256") != digest(gate):
        errors.append("artifact digest mismatch")
    checks = gate.get("checks", {})
    open_items = gate.get("open_items", [])
    expected_open = sorted(k for k, value in checks.items() if not value)
    if sorted(open_items) != expected_open:
        errors.append("open_items do not match checks")
    decision = gate.get("decision")
    if open_items and decision != "retain_native_digital_gpu_execution":
        errors.append("open physical items require digital GPU decision")
    if not open_items and decision != "authorized_analog_execution":
        errors.append("closed physical gate requires analog authorization")
    if args.require_analog and (open_items or decision != "authorized_analog_execution"):
        errors.append("analog authorization requested but gate is open")
    result = {"status": "passed" if not errors else "failed", "decision": decision, "open_items": open_items, "errors": errors, "gate": str(args.gate)}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
