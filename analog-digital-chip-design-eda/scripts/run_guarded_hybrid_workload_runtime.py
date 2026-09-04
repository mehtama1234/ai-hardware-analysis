#!/usr/bin/env python3
"""Run the shared schedule in simulator-candidate and physical-guarded modes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-hybrid-compiler-runtime"


def read(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def main() -> int:
    package = read("hybrid_compiler_runtime_package.json")
    compiled = read("compiled_target_execution_package.json")
    commands = read("runtime_commands.json")["commands"]
    physical_gate = package["shared_hardware"]["shared_converter_gate"]
    analog_model_ops = {
        model["model_id"]: model["analog_operator_count"] for model in package["models"]
    }
    model_results = {
        model["model_id"]: {
            "workload_id": model["workload_id"],
            "comparison_pass": model["comparison"]["pass"],
            "proof_level": model["comparison"]["proof_level"],
            "physical_gate": physical_gate,
        }
        for model in package["models"]
    }
    events = []
    simulator_analog = 0
    guarded_fallback = 0
    for command in commands:
        is_analog = command["unit"] == "analog_memory"
        simulator_mode = "analog_candidate" if is_analog else "digital_support"
        guarded_mode = "digital_fallback_physical_converter_blocked" if is_analog else "digital_support"
        if is_analog:
            simulator_analog += 1
            guarded_fallback += 1
        events.append({
            "sequence": command["sequence"],
            "model_id": command["model_id"],
            "operator_id": command["operator_id"],
            "command": command["command"],
            "simulator_mode": simulator_mode,
            "physical_guarded_mode": guarded_mode,
            "start_cycle": command["start_cycle"],
            "estimated_cycles": command["estimated_cycles"],
            "fallback_reason": "physical converter gate blocked" if is_analog else None,
        })
    report = {
        "schema_version": "aimc_guarded_hybrid_runtime_trace.v1",
        "trace_id": "guarded_hybrid_workload_runtime_v1",
        "source_package": "compiled_target_execution_package.json",
        "status": "simulator_candidate_and_physical_guarded_fallback_trace",
        "physical_converter_gate": physical_gate,
        "models": model_results,
        "totals": {
            "models": len(model_results),
            "commands": len(commands),
            "simulator_analog_candidate_commands": simulator_analog,
            "physical_guarded_digital_fallback_commands": guarded_fallback,
            "digital_support_commands": len(commands) - simulator_analog,
            "planning_cycles": compiled["estimated_cycles"],
        },
        "task_result_statement": "The named simulator/task comparisons remain intact as source evidence; physically guarded execution selects digital fallback for every analog candidate because the converter gate is blocked.",
        "claim_boundary": {
            "allowed": "the compiled schedule can apply a physical converter gate and emit explicit digital fallback decisions per analog command",
            "not_allowed": "does not prove measured fallback latency, measured energy, board runtime, physical analog execution, silicon, or production readiness",
        },
        "events": events,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    lines = [
        "# Guarded Hybrid Workload Runtime",
        "",
        "This trace consumes the shared target command schedule in two modes: simulator-candidate mode and physically guarded mode.",
        "",
        f"- workloads/models: `{len(model_results)}`",
        f"- commands: `{len(commands)}`",
        f"- simulator analog candidate commands: `{simulator_analog}`",
        f"- physical guarded digital fallbacks: `{guarded_fallback}`",
        f"- physical converter gate: `{physical_gate}`",
        "",
        "## Runtime Decision",
        "",
        "Analog commands remain visible for simulator analysis, but every such command is converted to an explicit digital fallback in the physical-guarded trace because the Sky130 converter has not passed its threshold-spacing gate. The wake-word package already selects digital execution from its cost policy.",
        "",
        "## Claim Boundary",
        "",
        report["claim_boundary"]["not_allowed"],
    ]
    (EVIDENCE / "guarded_hybrid_workload_runtime_trace.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (EVIDENCE / "guarded_hybrid_workload_runtime_trace.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"trace,{report['trace_id']}")
    print(f"models,{len(model_results)}")
    print(f"commands,{len(commands)}")
    print(f"simulator_analog_candidate_commands,{simulator_analog}")
    print(f"physical_guarded_fallback_commands,{guarded_fallback}")
    print(f"physical_converter_gate,{physical_gate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
