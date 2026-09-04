#!/usr/bin/env python3
"""Verify the target schedule and emit a bounded runtime estimate."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def main() -> int:
    compiled = load("compiled_target_execution_package.json")
    commands = load("runtime_commands.json")["commands"]
    registers = load("register_writes.json")["registers"]
    if len(commands) != compiled["command_count"]:
        raise SystemExit("command artifact count does not match compiled package")
    if len(registers) != compiled["register_write_count"]:
        raise SystemExit("register artifact count does not match compiled package")
    previous_end = 0
    for index, command in enumerate(commands, 1):
        if command["sequence"] != index:
            raise SystemExit(f"command sequence gap at {index}")
        if command["start_cycle"] < previous_end:
            raise SystemExit(f"overlapping command at sequence {index}")
        previous_end = command["start_cycle"] + command["estimated_cycles"]
    per_model = defaultdict(lambda: {"commands": 0, "cycles": 0, "event_types": Counter(), "units": Counter()})
    for command in commands:
        stats = per_model[command["model_id"]]
        stats["commands"] += 1
        stats["cycles"] = max(stats["cycles"], command["start_cycle"] + command["estimated_cycles"])
        stats["event_types"][command["command"]] += 1
        stats["units"][command["unit"]] += 1
    model_reports = []
    source_package = json.loads((ROOT / compiled["source_package"]).read_text(encoding="utf-8"))
    model_lookup = {model["model_id"]: model for model in source_package["models"]}
    for model_id, stats in sorted(per_model.items()):
        model = model_lookup[model_id]
        operator_count = model["operator_count"]
        analog_candidates = model["analog_operator_count"]
        hybrid_cycles = stats["cycles"]
        digital_only_cycles = operator_count * 3
        model_reports.append(
            {
                "model_id": model_id,
                "commands": stats["commands"],
                "estimated_cycles": hybrid_cycles,
                "digital_only_estimated_cycles": digital_only_cycles,
                "hybrid_to_digital_cycle_ratio": hybrid_cycles / digital_only_cycles if digital_only_cycles else None,
                "operator_count": operator_count,
                "analog_candidate_count": analog_candidates,
                "converter_command_count": stats["units"]["converter"],
                "guarded_fallback_command_count": analog_candidates,
                "event_types": dict(sorted(stats["event_types"].items())),
                "units": dict(sorted(stats["units"].items())),
            }
        )
    estimate = {
        "schema_version": "aimc_hybrid_runtime_estimate.v1",
        "estimate_id": "hybrid_transformer_runtime_estimate_v1",
        "source_package": "compiled_target_execution_package.json",
        "status": "schedule_verified_estimate_physical_converter_blocked",
        "schedule_verified": True,
        "model_reports": model_reports,
        "totals": {
            "models": len(model_reports),
            "commands": len(commands),
            "register_writes": len(registers),
            "estimated_cycles": previous_end,
            "analog_tile_compute_commands": sum(command["command"] == "RUN_ANALOG_TILE" for command in commands),
            "converter_commands": sum(command["unit"] == "converter" for command in commands),
            "sram_commands": sum(command["unit"] == "local_sram" for command in commands),
            "digital_support_commands": sum(command["command"] == "RUN_DIGITAL_SUPPORT" for command in commands),
        },
        "digital_only_comparison": {
            "model_reports": model_reports,
            "method": "digital-only planning baseline assigns three planning cycles to each operator; hybrid values come from the serialized target schedule",
            "not_measured": True,
        },
        "assumptions": {
            "cycle_counts": "planning values from target compiler; not measured latency",
            "parallelism": "all commands serialized for a conservative review schedule",
            "energy": "not estimated because physical converter and memory energy are not accepted",
            "sram": "symbolic buffers only; no byte allocator or bandwidth model",
        },
        "physical_converter_gate": "blocked_sar_source_common_mode",
        "claim_boundary": "schedule consistency and planning cost only; not board runtime, measured energy, or silicon behavior",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report = "\n".join(
        [
            "# Hybrid Runtime Estimate",
            "",
            "The target command schedule was checked for complete coverage, sequence ordering, and overlap.",
            "",
            f"- schedule verified: `{str(estimate['schedule_verified']).lower()}`",
            f"- models: `{estimate['totals']['models']}`",
            f"- commands: `{estimate['totals']['commands']}`",
            f"- register writes: `{estimate['totals']['register_writes']}`",
            f"- serialized planning cost: `{estimate['totals']['estimated_cycles']}` cycles",
            f"- analog tile commands: `{estimate['totals']['analog_tile_compute_commands']}`",
            f"- converter commands: `{estimate['totals']['converter_commands']}`",
            f"- SRAM commands: `{estimate['totals']['sram_commands']}`",
            f"- digital support commands: `{estimate['totals']['digital_support_commands']}`",
            "",
            "## Digital-Only Planning Comparison",
            "",
            "Each workload is compared with a deliberately simple digital-only planning baseline. This is useful for exposing converter and fallback overhead, but it is not measured latency, energy, or power.",
            "",
        ] + [
            f"- `{row['model_id']}`: hybrid `{row['estimated_cycles']}` cycles versus digital-only `{row['digital_only_estimated_cycles']}` cycles; ratio `{row['hybrid_to_digital_cycle_ratio']:.3f}`; converter commands `{row['converter_command_count']}`; guarded fallback commands `{row['guarded_fallback_command_count']}`"
            for row in model_reports
        ] + [
            "",
            "These are schedule estimates, not observed runtime or energy. The physical converter gate remains blocked by high-code threshold compression.",
            "",
        ]
    )
    (EVIDENCE / "hybrid_runtime_estimate.json").write_text(json.dumps(estimate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EVIDENCE / "hybrid_runtime_estimate.md").write_text(report, encoding="utf-8")
    print(f"estimate,{estimate['estimate_id']}")
    print("schedule_verified,True")
    print(f"models,{estimate['totals']['models']}")
    print(f"commands,{estimate['totals']['commands']}")
    print(f"estimated_cycles,{estimate['totals']['estimated_cycles']}")
    print(f"analog_tile_commands,{estimate['totals']['analog_tile_compute_commands']}")
    print(f"converter_commands,{estimate['totals']['converter_commands']}")
    print(f"sram_commands,{estimate['totals']['sram_commands']}")
    print("physical_converter_gate,blocked_sar_source_common_mode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
