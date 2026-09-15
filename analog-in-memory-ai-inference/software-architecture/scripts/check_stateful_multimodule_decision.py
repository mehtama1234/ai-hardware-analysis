#!/usr/bin/env python3
"""Verify the stateful multi-module decision package."""

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
    decision = json.loads((args.package / "decision_audit.json").read_text(encoding="utf-8"))
    ledger = json.loads((args.package / "claim_ledger.json").read_text(encoding="utf-8"))
    manifest = json.loads((args.package / "manifest.json").read_text(encoding="utf-8"))
    failures = []
    for entry in manifest.get("files", []):
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path.cwd() / path
        if not path.is_file() or digest(path) != entry.get("sha256"):
            failures.append(f"manifest hash mismatch: {path}")
    gates = {row["gate"]: row["passed"] for row in decision.get("gates", [])}
    if decision.get("gate_count") != 8 or decision.get("passed_gate_count") != 6:
        failures.append("unexpected stateful gate counts")
    if decision.get("decision") != "stateful_profile_not_generalized":
        failures.append("stateful decision did not preserve failed third holdout")
    if gates.get("third_holdout_generalization") is not False or gates.get("analog_authorization") is not False:
        failures.append("stateful failure or authorization boundary was weakened")
    if decision.get("runtime_decision") != "digital_reference_and_deterministic_fallback_only":
        failures.append("stateful runtime decision is unsafe")
    if any(row.get("status") == "authorized" for row in ledger.get("claims", [])):
        failures.append("stateful claim ledger contains authorization")
    result = {"status": "passed" if not failures else "failed", "failures": failures,
              "finding": "stateful profile passes two contexts but fails third-holdout generalization; digital fallback remains enforced.",
              "claim_boundary": decision.get("claim_boundary")}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
