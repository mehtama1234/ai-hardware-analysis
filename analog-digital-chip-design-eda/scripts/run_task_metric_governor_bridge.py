#!/usr/bin/env python3
"""Convert a model-backed task result into a governor decision trace."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASK_RESULT = ROOT / "evidence" / "aimc-hardware-lab" / "tiny-mlp-task-evaluation-v1.json"
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
sys.path.insert(0, str(PY_DIR))
from error_budget_governor_trace import govern  # noqa: E402


def q8(value: float) -> int:
    return max(0, min(255, round(value * 255)))


def main() -> int:
    task_result = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_TASK_RESULT
    output = task_result.with_name(task_result.stem.replace("-evaluation", "-governor-bridge") + ".json")
    task = json.loads(task_result.read_text(encoding="utf-8"))
    drop = float(task["metric_drop"])
    changed = int(task.get("changed_predictions", sum(1 for row in task.get("records", []) if isinstance(row, dict) and row.get("prediction_changed"))))
    sample_count = int(task["sample_count"])
    residual_q8 = q8(drop)
    # A changed task decision makes this path decision-sensitive even when the average drop is small.
    sensitivity_q8 = 224 if changed else 96
    decision, action, reason, next_error = govern(
        sample_valid=1,
        analog_candidate=1,
        residual_q8=residual_q8,
        drift_age=1,
        sensitivity_q8=sensitivity_q8,
        cumulative_error_q8=0,
    )
    report = {
        "schema_version": "aimc_task_metric_governor_bridge.v1",
        "status": "task_metric_drives_governor",
        "source_task_result": str(task_result),
        "workload_id": task["dataset_id"],
        "model_id": task["model_id"],
        "metric_name": task["metric_name"],
        "baseline_metric": task["baseline_metric"],
        "candidate_metric": task["candidate_metric"],
        "metric_drop": drop,
        "sample_count": sample_count,
        "changed_predictions": changed,
        "residual_q8": residual_q8,
        "sensitivity_q8": sensitivity_q8,
        "analog_candidate": True,
        "governor_decision": decision,
        "governor_action": action,
        "governor_reason": reason,
        "next_cumulative_error_q8": next_error,
        "interpretation": "The task result is allowed to request analog service only as a bounded rehearsal; a changed task decision raises sensitivity and larger degradation would trigger digital fallback.",
        "claim_boundary": "This connects a model-backed synthetic task result to the governor. It does not prove physical analog residual, board runtime, power, thermal behavior, or silicon.",
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "residual_q8", "sensitivity_q8", "governor_decision", "governor_action", "governor_reason"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
