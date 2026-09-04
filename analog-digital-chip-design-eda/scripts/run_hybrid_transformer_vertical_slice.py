#!/usr/bin/env python3
"""Validate and trace the first hybrid transformer execution package."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "aimc-hybrid-transformer-vertical-slice"


def read(name: str) -> dict:
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))


def main() -> int:
    plan = read("hybrid_execution_plan.json")
    replay = read("analog_error_replay.json")
    comparison = read("hybrid_output_comparison.json")
    analog_rows = [row for row in plan["operator_placements"] if row["placement"] == "analog_memory"]
    digital_rows = [row for row in plan["operator_placements"] if row["placement"] == "digital_support"]
    replay_rows = replay["error_model"]["per_candidate_results"]
    plan_ids = [row["operator_id"] for row in analog_rows]
    replay_ids = [row["candidate_id"] for row in replay_rows]
    if plan_ids != replay_ids:
        raise SystemExit(f"plan/replay candidate mismatch: {plan_ids!r} != {replay_ids!r}")
    if len(plan["operator_placements"]) != len(plan_ids) + len(digital_rows):
        raise SystemExit("placement rows are not partitioned into analog and digital rows")

    events: list[dict[str, object]] = []
    sequence = 0
    for row, replay_row in zip(analog_rows, replay_rows):
        candidate_id = row["operator_id"]
        for event_type, location, detail in (
            ("activation_load", "local_sram", "load source activation"),
            ("dac_encode", "converter_boundary", "encode activation for analog row input"),
            ("analog_matmul", "analog_memory", f"execute {row['tile_count']} physical tiles"),
            ("adc_decode", "converter_boundary", "digitize analog column output"),
            ("calibration_apply", "digital_support", row["calibration_profile"]),
            ("partial_sum_store", "local_sram", "store corrected output for next operator"),
        ):
            sequence += 1
            events.append(
                {
                    "sequence": sequence,
                    "operator_id": candidate_id,
                    "event": event_type,
                    "location": location,
                    "detail": detail,
                }
            )
        if replay_row["candidate_id"] != candidate_id:
            raise SystemExit(f"replay row changed during trace: {candidate_id!r}")

    for row in digital_rows:
        sequence += 1
        events.append(
            {
                "sequence": sequence,
                "operator_id": row["operator_id"],
                "event": "digital_support",
                "location": "digital_memory_and_sram",
                "detail": row["reason"],
            }
        )

    schedule = {
        "schema_version": "aimc_hybrid_execution_schedule.v1",
        "schedule_id": "deep_transformer_mlp_stack_hybrid_schedule_v1",
        "source_plan": "hybrid_execution_plan.json",
        "source_replay": "analog_error_replay.json",
        "event_count": len(events),
        "operator_count": len(plan["operator_placements"]),
        "analog_operator_count": len(analog_rows),
        "digital_support_operator_count": len(digital_rows),
        "events": events,
        "status": "replay_schedule_valid_physical_converter_blocked",
        "claim_boundary": "operator-level replay schedule; not a compiled chip binary or measured hardware trace",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    trace = {
        "schema_version": "aimc_hybrid_runtime_trace.v1",
        "trace_id": "deep_transformer_mlp_stack_hybrid_replay_v1",
        "schedule_id": schedule["schedule_id"],
        "comparison_id": comparison["comparison_id"],
        "proof_level": "calibrated simulator replay",
        "simulator_result": {
            "relative_l2_output_difference": comparison["relative_l2_output_difference"],
            "threshold": comparison["threshold"],
            "pass": comparison["pass"],
        },
        "physical_converter_gate": plan["converter_plan"]["compatibility_status"],
        "events": events,
        "claim_boundary": "does not prove compiled runtime, board latency, measured energy, calibrated silicon, or production readiness",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (PACKAGE / "execution_schedule.json").write_text(json.dumps(schedule, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PACKAGE / "hybrid_runtime_trace.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"schedule,{schedule['schedule_id']}")
    print(f"events,{len(events)}")
    print(f"operators,{len(plan['operator_placements'])}")
    print(f"analog_operators,{len(analog_rows)}")
    print(f"digital_support_operators,{len(digital_rows)}")
    print(f"simulator_pass,{comparison['pass']}")
    print(f"physical_converter_gate,{plan['converter_plan']['compatibility_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
