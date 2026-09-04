#!/usr/bin/env python3
"""Join physical PVT eligibility with the accepted model-shaped task gate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PVT = EVIDENCE / "sky130-two-phase-transistor-full-pvt.json"
TASK = ROOT / "evidence" / "aimc-hardware-lab" / "deep-transformer-mlp-task-quality-v1.json"
OUT_JSON = EVIDENCE / "sky130-full-pvt-task-policy-bridge.json"
OUT_MD = EVIDENCE / "sky130-full-pvt-task-policy-bridge.md"


def main() -> int:
    pvt = json.loads(PVT.read_text(encoding="utf-8"))
    task = json.loads(TASK.read_text(encoding="utf-8"))
    crosssim = next(row for row in task["results"] if row.get("tool") == "crosssim")
    model_gate = bool(crosssim.get("pass"))
    rows = []
    for source in pvt["rows"]:
        physical_gate = bool(source.get("measured")) and bool(source.get("margin_pass")) and bool(source.get("sign_preserved"))
        analog_allowed = physical_gate and model_gate
        rows.append({
            "corner": source["name"],
            "input_diff_mv": source["input_diff_mv"],
            "physical_measured": bool(source.get("measured")),
            "physical_margin_pass": bool(source.get("margin_pass", False)),
            "physical_sign_pass": bool(source.get("sign_preserved", False)),
            "model_gate_pass": model_gate,
            "analog_allowed": analog_allowed,
            "decision": "analog_service" if analog_allowed else "digital_fallback",
            "fallback_reason": None if analog_allowed else (
                "model_quality_gate_failed" if not model_gate else
                "physical_simulation_did_not_converge" if not source.get("measured") else
                "physical_preamp_margin_too_low"
            ),
        })
    report = {
        "result_type": "sky130_full_pvt_task_policy_bridge",
        "status": "physical_and_model_gates_joined_with_fallback",
        "physical_source": str(PVT.relative_to(ROOT)),
        "task_source": str(TASK.relative_to(ROOT)),
        "model_gate": {
            "tool": "crosssim",
            "pass": model_gate,
            "metric_name": crosssim.get("metric_name"),
            "surrogate_error": crosssim.get("surrogate_error"),
            "analog_candidate_count": crosssim.get("candidate_count"),
        },
        "case_count": len(rows),
        "analog_allowed_count": sum(row["analog_allowed"] for row in rows),
        "digital_fallback_count": sum(not row["analog_allowed"] for row in rows),
        "fallback_reasons": {
            reason: sum(row["fallback_reason"] == reason for row in rows)
            for reason in {row["fallback_reason"] for row in rows if row["fallback_reason"]}
        },
        "rows": rows,
        "claim_boundary": {
            "allowed": "joins a calibrated model-shaped CrossSim gate with deterministic transistor PVT eligibility and records fallback reasons",
            "not_allowed": "does not prove task quality at every physical corner, random noise or mismatch yield, SAR conversion, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Full PVT And Task Policy Bridge", "",
        "This page joins two gates that must both pass before an analog projection is allowed to serve the model: physical converter eligibility and model-quality evidence.", "",
        f"- PVT policy cases: `{report['case_count']}`",
        f"- analog-allowed cases: `{report['analog_allowed_count']}`",
        f"- digital-fallback cases: `{report['digital_fallback_count']}`",
        f"- CrossSim model gate: `{model_gate}`",
        f"- CrossSim surrogate error: `{crosssim.get('surrogate_error')}`", "",
        "## First-Principles Reading", "",
        "A model-level simulator pass cannot rescue a converter that loses amplitude or fails to converge at a physical corner. Conversely, a circuit that produces a large signal is not enough if the mapped model operation exceeds its error budget. The service decision is the intersection of both gates.", "",
        "In this run the CrossSim calibrated deep MLP surrogate passes, so the remaining exclusions come from the physical matrix: low preamp amplitude or a non-convergent transient forces digital fallback. This is a policy bridge, not a claim that task accuracy was remeasured at each PVT point.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"analog_allowed_count,{report['analog_allowed_count']}")
    print(f"digital_fallback_count,{report['digital_fallback_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
