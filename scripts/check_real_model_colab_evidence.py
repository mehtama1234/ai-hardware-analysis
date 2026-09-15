#!/usr/bin/env python3
"""Independently validate the authenticated real-model evidence boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_run(run_dir: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    summary = read(run_dir / "aimc-llm-agent-colab-summary.json")
    benchmark = read(run_dir / "llm-agent-benchmark-colab.json")
    heldout = read(run_dir / "agent-repair-heldout-evaluation-report.json")
    pipeline = read(run_dir / "real-four-workstream-colab.json")
    if summary.get("schema_version") != "aimc-llm-agent-colab-run-v1": errors.append("summary schema mismatch")
    if summary.get("model_id") != "Qwen/Qwen2.5-0.5B-Instruct": errors.append("unexpected authenticated model")
    provenance = benchmark.get("model_provenance", {})
    if provenance.get("provider") != "google-colab" or provenance.get("gpu") != "Tesla T4, 15360 MiB": errors.append("GPU/provider provenance is not authenticated")
    if benchmark.get("schema_version") != "llm-verification-agent-benchmark-v1": errors.append("benchmark schema mismatch")
    metrics = benchmark.get("metrics", {})
    if benchmark.get("design_count") != 11 or metrics.get("grounded_proposals") != 11 or metrics.get("model_diagnosis_match", {}).get("local-batch-command") != 11:
        errors.append("primary 11-design grounded diagnosis result is incomplete")
    if metrics.get("unsafe_rejected") != 3 or benchmark.get("reference_execution", {}).get("passed_retests") != 11:
        errors.append("unsafe-claim or reference retest boundary is incomplete")
    for gate in ("aimc_root_cause_gate", "aimc_repair_gate", "counter_repair_gate", "register_repair_gate", "timeout_repair_gate"):
        if benchmark.get(gate) is not True: errors.append(f"benchmark gate is not passed: {gate}")
    if heldout.get("schema_version") != "agent-repair-heldout-evaluation-report-v1" or heldout.get("status") != "blocked": errors.append("held-out result did not remain blocked")
    if heldout.get("train", {}).get("total") != 8 or heldout.get("heldout", {}).get("total") != 8: errors.append("train/held-out split is incomplete")
    if heldout.get("heldout", {}).get("all_passed") is not False or heldout.get("heldout", {}).get("model_selected_repair_count", 0) < 0: errors.append("held-out negative boundary is malformed")
    pipeline_result = pipeline.get("pipeline_result", {})
    if (pipeline.get("status") != "failed" or pipeline.get("returncode") == 0
            or (pipeline_result and pipeline_result.get("agent", {}).get("status") != "blocked")
            or (not pipeline_result and "did not meet its expected classifications" not in pipeline.get("stderr_tail", ""))):
        errors.append("full pipeline failure was not preserved as blocked")
    result = {"summary_status": summary.get("status"), "benchmark_design_count": benchmark.get("design_count"), "heldout_closure_rate": heldout.get("heldout", {}).get("closure_rate"), "heldout_model_selected_repairs": heldout.get("heldout", {}).get("model_selected_repair_count"), "pipeline_status": pipeline.get("status"), "files": {name: hashlib.sha256((run_dir / name).read_bytes()).hexdigest() for name in ("aimc-llm-agent-colab-summary.json", "llm-agent-benchmark-colab.json", "agent-repair-heldout-evaluation-report.json", "real-four-workstream-colab.json")}}
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", type=Path, nargs="*")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.receipt:
        errors = []
        try:
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "blocked", "errors": [str(exc)]}, sort_keys=True))
            return 1
        unsigned = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        expected = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if receipt.get("schema_version") != "real-model-colab-evidence-check-v1": errors.append("unsupported receipt schema")
        if receipt.get("receipt_sha256") != expected: errors.append("receipt digest mismatch")
        if receipt.get("status") != "passed" or set(receipt.get("runs", {})) != {"20260915T173123Z", "20260915T182003Z"}: errors.append("receipt does not contain both authenticated runs")
        result = {"schema_version": "real-model-colab-evidence-receipt-check-v1", "status": "passed" if not errors else "blocked", "receipt": str(args.receipt.resolve()), "errors": sorted(errors)}
        result["check_sha256"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        print(json.dumps(result, sort_keys=True))
        return 0 if not errors else 1
    if not args.run_dirs or not args.output:
        parser.error("provide run directories and --output, or provide --receipt")
    runs = {}
    errors = []
    for run_dir in args.run_dirs:
        try:
            result, run_errors = check_run(run_dir.resolve())
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            result, run_errors = {}, [f"{run_dir}: {exc}"]
        runs[run_dir.name] = result
        errors.extend(f"{run_dir.name}: {error}" for error in run_errors)
    receipt = {"schema_version": "real-model-colab-evidence-check-v1", "status": "passed" if not errors else "blocked", "runs": runs, "errors": sorted(errors), "claim_boundary": "Authenticated Qwen/T4 proposal and bounded repair-choice evidence only; held-out generalization and full pipeline remain blocked, and this does not authorize autonomous repair, silicon, or production signoff."}
    receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output = args.output.resolve(); output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "runs": sorted(runs), "output": str(output)}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
