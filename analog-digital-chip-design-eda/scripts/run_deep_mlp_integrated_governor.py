#!/usr/bin/env python3
"""Drive the integrated scheduler/governor with calibrated deep-MLP evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "evidence" / "aimc-simulator-adapters"
OUT = ROOT / "evidence" / "aimc-hardware-lab" / "deep-transformer-mlp-integrated-governor-v1.json"
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
sys.path.insert(0, str(PY_DIR))
from integrated_scheduler_governor_runtime import govern, integrate, schedule  # noqa: E402


def load(tool: str) -> dict[str, object]:
    path = SIM / f"{tool}-calibrated-deep-transformer-mlp-stack-analog-error-simulation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def trace(tool: str, payload: dict[str, object]) -> dict[str, object]:
    error = payload["error_model"]
    residual = int(error["final_residual_q8"])
    candidates = error["array_assumptions"]["candidate_ids"]
    rows = []
    for index, candidate in enumerate(candidates):
        scheduler_decision, selected_tile, scheduler_reason = schedule(1, 1, index, 1, "0000", "0000")
        governor_decision, action, governor_reason, next_error = govern(1, 1, residual, 4, 140, 0)
        final_decision, final_reason = integrate(scheduler_decision, scheduler_reason, governor_decision, action, governor_reason)
        rows.append({"operator": candidate, "residual_q8": residual, "sensitivity_q8": 140, "scheduler_decision": scheduler_decision, "selected_tile": selected_tile, "governor_decision": governor_decision, "governor_action": action, "governor_reason": governor_reason, "final_decision": final_decision, "final_reason": final_reason, "next_cumulative_error_q8": next_error})
    return {"tool": tool, "payload_status": "accepted" if payload["accuracy_impact"]["pass"] else "rejected", "residual_relative": error["final_residual_relative"], "rows": rows, "analog_service_count": sum(r["final_decision"] == 1 for r in rows), "digital_or_maintenance_count": sum(r["final_decision"] != 1 for r in rows)}


def main() -> None:
    report = {"schema_version": "aimc_integrated_governor_trace.v1", "status": "deep_mlp_evidence_drives_integrated_governor", "workload_id": "deep-transformer-mlp-stack-v1", "traces": [trace(tool, load(tool)) for tool in ["crosssim", "aihwkit"]], "claim_boundary": "This connects calibrated simulator evidence to the integrated scheduler/governor for a model-shaped fixture. It does not prove silicon, board runtime, power, thermal behavior, or production readiness."}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for item in report["traces"]:
        print(f"{item['tool']}: status={item['payload_status']} residual={item['residual_relative']:.6g} analog_service={item['analog_service_count']} fallback_or_maintenance={item['digital_or_maintenance_count']}")


if __name__ == "__main__":
    main()
