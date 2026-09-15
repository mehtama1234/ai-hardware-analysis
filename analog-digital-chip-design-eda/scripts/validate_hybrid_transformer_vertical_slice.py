#!/usr/bin/env python3
"""Audit the transformer vertical-slice package without promoting blocked claims."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "evidence" / "aimc-hybrid-transformer-vertical-slice"
REQUIRED = (
    "workload_contract.json",
    "hybrid_execution_plan.json",
    "bit_slicing_plan.json",
    "analog_error_replay.json",
    "hybrid_output_comparison.json",
    "execution_schedule.json",
    "hybrid_runtime_trace.json",
)


def load(name: str) -> dict:
    path = PACKAGE / name
    if not path.is_file():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    contract, plan, bit_slicing, replay, comparison, schedule, trace = (
        load(name) for name in REQUIRED
    )
    placements = plan["operator_placements"]
    if len({row["operator_id"] for row in placements}) != len(placements):
        raise SystemExit("operator placement IDs are not unique")
    if not placements:
        raise SystemExit("operator placement is empty")

    analog = [row for row in placements if row["placement"] == "analog_memory"]
    digital = [row for row in placements if row["placement"] == "digital_support"]
    if len(analog) + len(digital) != len(placements):
        raise SystemExit("operator placement contains an unsupported placement")
    for row in analog:
        required = ("tile_count", "bit_slices", "calibration_profile", "fallback", "converter_boundaries")
        missing = [field for field in required if row.get(field) in (None, "")]
        if missing:
            raise SystemExit(f"{row['operator_id']}: missing analog contract fields {missing}")
    for row in digital:
        if not row.get("reason"):
            raise SystemExit(f"{row['operator_id']}: digital placement has no reason")

    replay_rows = replay["error_model"]["per_candidate_results"]
    if [row["operator_id"] for row in analog] != [row["candidate_id"] for row in replay_rows]:
        raise SystemExit("analog placement and replay candidate order differ")
    if len(replay_rows) != len(analog):
        raise SystemExit("not every analog operator has a replay result")
    if not comparison["pass"]:
        raise SystemExit("hybrid output comparison failed")
    if comparison["physical_converter_gate"] == "":
        raise SystemExit("physical converter gate is missing")
    if schedule["operator_count"] != len(placements):
        raise SystemExit("schedule operator count does not match plan")
    if schedule["analog_operator_count"] != len(analog):
        raise SystemExit("schedule analog count does not match plan")
    if schedule["digital_support_operator_count"] != len(digital):
        raise SystemExit("schedule digital count does not match plan")
    if schedule["event_count"] != len(schedule["events"]):
        raise SystemExit("schedule event count is incorrect")
    if trace["schedule_id"] != schedule["schedule_id"]:
        raise SystemExit("runtime trace does not consume the generated schedule")
    if trace["physical_converter_gate"] != plan["converter_plan"]["compatibility_status"]:
        raise SystemExit("runtime trace and plan disagree on physical converter gate")
    profile_path = ROOT / plan["converter_plan"]["circuit_qualification_profile"]
    if not profile_path.is_file():
        raise SystemExit(f"missing circuit qualification profile: {profile_path}")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("analog_authorized") is not False:
        raise SystemExit("circuit qualification profile must keep analog_authorized false")
    if profile.get("status") != "bounded_nominal_profile_physical_qualification_open":
        raise SystemExit("circuit qualification profile has an unexpected status")

    forbidden = ("silicon", "board runtime", "measured power", "production readiness")
    claim_text = json.dumps({"contract": contract, "plan": plan, "comparison": comparison, "trace": trace}).lower()
    boundaries = json.dumps([
        contract.get("claim_boundary"),
        comparison.get("claim_boundary"),
        trace.get("claim_boundary"),
    ]).lower()
    # These phrases are allowed only inside explicit negative claim boundaries.
    for phrase in forbidden:
        if phrase in claim_text and phrase not in boundaries:
            raise SystemExit(f"unbounded claim text detected: {phrase}")

    print("HYBRID VERTICAL SLICE AUDIT PASS")
    print(f"operators={len(placements)} analog={len(analog)} digital={len(digital)}")
    print(f"replay_candidates={len(replay_rows)} events={schedule['event_count']}")
    print(f"simulator_output_pass={comparison['pass']}")
    print(f"physical_converter_gate={comparison['physical_converter_gate']}")
    print("claim_boundary=simulator_replay_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
