#!/usr/bin/env python3
"""Validate a profile-driven Colab receipt and optional CUDA requirement."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PINNED_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    failures = []
    env = receipt.get("environment", {})
    if args.require_cuda and not str(env.get("device", "")).startswith("cuda"):
        failures.append(f"CUDA required, receipt reports {env.get('device')!r}")
    fetched = receipt.get("model_fetch") or {}
    if fetched.get("revision") != PINNED_REVISION:
        failures.append("model fetch revision does not match pinned fixture")
    for key in ("contract_check_output", "dispatch_simulation_check_output"):
        if '"status": "passed"' not in receipt.get(key, ""):
            failures.append(f"{key} does not report passed")
    if not receipt.get("environment", {}).get("execute_model"):
        failures.append("receipt did not execute the model")
    evaluation = args.receipt.parent / "model-evaluation/evaluation.json"
    if not evaluation.exists():
        failures.append(f"missing model evaluation: {evaluation}")
    else:
        result = json.loads(evaluation.read_text())
        if result.get("model", {}).get("revision") != PINNED_REVISION:
            failures.append("evaluation model revision does not match pinned fixture")
        if result.get("controls", {}).get("digital_fallback_pass") is not True:
            failures.append("digital fallback control did not pass")
        if result.get("placement", {}).get("authorized_analog_modules") != []:
            failures.append("analog placement guard is not empty")
    output = {"status": "passed" if not failures else "failed",
              "cuda_required": args.require_cuda, "failures": failures,
              "claim_boundary": "Receipt validation only; no analog hardware performance or yield claim."}
    print(json.dumps(output, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
