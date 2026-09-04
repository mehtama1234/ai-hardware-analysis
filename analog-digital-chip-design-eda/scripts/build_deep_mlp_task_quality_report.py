#!/usr/bin/env python3
"""Normalize calibrated deep-MLP simulator results into a task-quality report."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence" / "aimc-simulator-adapters" / "calibrated-deep-transformer-mlp-stack-simulator-payload-run-summary.json"
OUT = ROOT / "evidence" / "aimc-hardware-lab" / "deep-transformer-mlp-task-quality-v1.json"


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    results = []
    for item in summary["results"]:
        payload_path = ROOT / item["payload"]
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        impact = payload["accuracy_impact"]
        error = payload["error_model"]
        results.append({
            "tool": item["tool"],
            "payload_status": item["status"],
            "metric_name": impact["metric"],
            "surrogate_baseline": impact["baseline_reference"],
            "surrogate_error": impact["estimated_drop"],
            "pass": impact["pass"],
            "final_residual_relative": error["final_residual_relative"],
            "final_residual_q8": error["final_residual_q8"],
            "candidate_count": len(error["array_assumptions"]["candidate_ids"]),
            "digital_only_ops": error["array_assumptions"]["digital_only_ops"],
        })
    report = {
        "schema_version": "aimc_task_quality_report.v1",
        "status": "calibrated_simulator_surrogate_task_quality",
        "workload_id": "deep-transformer-mlp-stack-v1",
        "model_id": "deep-transformer-mlp-stack",
        "calibration_cases": summary["calibration"]["calibration_cases"],
        "held_out_case": True,
        "analog_candidate_count": summary["candidate_count"],
        "results": results,
        "decision": "CrossSim-supported-calibrated-fixed-weight-MLP-slice; AIHWKIT-run-rejected-by-residual-gate",
        "digital_boundary": summary["digital_only_ops"],
        "claim_boundary": "This is a held-out simulator surrogate for repeated fixed-weight MLP MatMuls. It is not language task accuracy, pretrained foundation-model behavior, silicon calibration, board runtime, measured power, or production readiness.",
        "next_required_evidence": [
            "Run a real model task with labels or token-quality outputs.",
            "Feed the accepted CrossSim residuals into the integrated scheduler/governor trace.",
            "Replace simulator assumptions with extracted analog macro and converter evidence.",
            "Measure latency, power, and thermal behavior for the same package and workload."
        ]
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(f"{result['tool']}: status={result['payload_status']} residual={result['final_residual_relative']:.6g} pass={result['pass']}")


if __name__ == "__main__":
    main()
