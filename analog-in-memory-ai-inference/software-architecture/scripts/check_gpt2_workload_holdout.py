#!/usr/bin/env python3
"""Check held-out GPT-2 workload binding for a device evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PINNED_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evaluation", type=Path)
    parser.add_argument("--require-cuda", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.evaluation.read_text())
    fixture = report["fixture"]
    calibration, workload = set(fixture["calibration"]), set(fixture["evaluation"])
    failures = []
    if calibration & workload:
        failures.append("calibration and workload contexts overlap")
    if report.get("model", {}).get("revision") != PINNED_REVISION:
        failures.append("model revision is not pinned")
    if args.require_cuda and report.get("runtime", {}).get("device") != "cuda":
        failures.append(f"CUDA required, got {report.get('runtime', {}).get('device')!r}")
    selected = next((v for v in report.get("variants", []) if v.get("id") == "dac10_weight8_adc12"), None)
    if selected is None:
        failures.append("ADC12 variant missing")
    else:
        quality = selected["quality"]
        if quality.get("teacher_forced_argmax_agreement") < 0.99:
            failures.append("ADC12 argmax agreement below 0.99")
        if quality.get("generation_exact_match_count") != len(workload):
            failures.append("ADC12 generation parity failed")
    result = {"schema_version": "gpt2-workload-holdout-check-v0.1",
              "status": "passed" if not failures else "failed",
              "device": report.get("runtime", {}).get("device"),
              "calibration_contexts": len(calibration), "held_out_contexts": len(workload),
              "failures": failures,
              "claim_boundary": "Held-out numerical workload gate only; no analog hardware performance or yield claim."}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
