#!/usr/bin/env python3
"""Audit saved compiled GPT-2 execution against the schedule and SRAM map."""

import argparse
import hashlib
import json
from pathlib import Path


def checked_source(record):
    path = Path(record["path"])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], str(path)


def check(package):
    load = lambda name: json.loads((package/name).read_text())
    for record in load("manifest.json")["files"]:
        checked_source(record)
    result = load("execution_result.json")
    checked_source(result["sources"]["sensitivity"])
    for record in result["sources"]["code"]:
        checked_source(record)
    assert result["status"] == "compiled_projection_fallback_pass"
    assert result["analog_instructions_executed"] == 0 and result["fallback_fraction"] == 1
    assert result["sram_bytes"] <= 65536
    commands=load("runtime_commands.json")["commands"]
    assert len(commands) == 1 and commands[0]["command"] == "RUN_DIGITAL_SUPPORT"
    compiled=load("compiled_target_execution_package.json")
    memory=compiled["sram_memory_maps"][0]
    assert memory["sram_bytes_used"] == result["sram_bytes"]
    allocation=memory["allocations"][0]
    totals={}
    for event in result["trace"]:
        assert event["route"] == "digital_fallback" and event["instruction"] == "RUN_DIGITAL_SUPPORT"
        assert event["executed_commands"] == event["vectors"]
        assert event["activation_offset_bytes"] == allocation["activation_offset_bytes"]
        assert event["partial_sum_offset_bytes"] == allocation["partial_sum_offset_bytes"]
        assert event["boundary_input_bytes"] == event["vectors"]*768*4
        assert event["boundary_output_bytes"] == event["vectors"]*3072*4
        phase=totals.setdefault(event["phase"],{key:0 for key in ("vectors","executed_commands","boundary_input_bytes","boundary_output_bytes")})
        for key in phase: phase[key] += event[key]
    assert totals == result["phase_totals"]
    for row in result["quality"]["rows"]:
        assert row["maximum_logit_abs_error"] < 1e-3
        assert row["baseline_generated_ids"] == row["candidate_generated_ids"]
    schedule=load("analog_candidate_schedule.json")
    assert len(schedule["tiles"]) == 144
    assert len(schedule["waves_per_vector"]) == 18
    assert [i for wave in schedule["waves_per_vector"] for i in wave["tile_ids"]] == list(range(144))
    assert all(wave["duration_ns"] is None for wave in schedule["waves_per_vector"])
    for phase,total in totals.items():
        for key,value in schedule["per_vector_cost_counts"].items():
            assert result["candidate_accounting"][phase][key] == value*total["vectors"]
    assert not load("physical_gate.json")["analog_allowed_for_physical_claim"]
    assert not load("physical_gate.json")["active_macro_candidate"]["physical_preamp_routing_complete"]
    return {"status":"passed", "vectors":sum(p["vectors"] for p in totals.values()),
            "scope":"saved identities, command/trace counts, SRAM map, model parity and physical claim boundary"}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package",type=Path,required=True)
    print(json.dumps(check(parser.parse_args().package),indent=2))
