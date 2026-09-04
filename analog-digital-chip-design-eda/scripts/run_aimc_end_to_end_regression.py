#!/usr/bin/env python3
"""Run the reproducible software-side AIMC vertical-slice regression."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-hardware-lab" / "end-to-end-regression-latest.json"
OUT_MD = ROOT / "evidence" / "aimc-hardware-lab" / "end-to-end-regression-latest.md"
REVIEW_MD = ROOT / "docs" / "research" / "aimc-end-to-end-regression.md"
SRAM_CAPACITY_BYTES = 65536


def python_with(module: str) -> str:
    requested = os.environ.get("AIMC_PYTHON")
    if requested:
        return requested
    probe = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if probe.returncode == 0:
        return sys.executable
    sibling = (
        ROOT.parent
        / "analog-in-memory-ai-inference"
        / "software-architecture"
        / "backend"
        / ".venv"
        / "bin"
        / "python"
    )
    return str(sibling) if sibling.exists() else sys.executable


def run(label: str, command: list[str]) -> dict[str, object]:
    print(f"[{label}] {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output, flush=True)
    return {
        "label": label,
        "command": command,
        "returncode": result.returncode,
        "pass": result.returncode == 0,
        "output_tail": output[-1600:],
    }


def artifact_checks() -> list[dict[str, object]]:
    def load(path: str) -> dict[str, object]:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    tiny = load("evidence/aimc-hardware-lab/tiny-mlp-task-evaluation-v1.json")
    governor = load("evidence/aimc-hardware-lab/deep-transformer-mlp-integrated-governor-v1.json")
    runtime = load("evidence/aimc-hybrid-compiler-runtime/guarded_hybrid_workload_runtime_trace.json")
    compiler = load("evidence/aimc-hybrid-compiler-runtime/hybrid_compiler_runtime_package.json")
    compiled = load("evidence/aimc-hybrid-compiler-runtime/compiled_target_execution_package.json")
    bytecode = load("evidence/aimc-hybrid-compiler-runtime/target_bytecode.json")
    bytecode_reference = load("evidence/aimc-hybrid-compiler-runtime/target_bytecode_reference_execution.json")
    physical = load("evidence/aimc-hardware-lab/physical-evidence-gate-latest.json")
    profile = load("evidence/aimc-hardware-lab/hardware-profile-educational-hybrid-tile-v1.json")
    charge_spec = load("evidence/aimc-simulator-adapters/sky130-charge-transfer-redesign-spec.json")
    continuous_sar_spec = load("evidence/aimc-simulator-adapters/sky130-continuous-physical-sar-spec.json")
    serving_task = load("evidence/aimc-hardware-lab/language-model-serving-task-rehearsal-v1.json")
    serving_comparison = load("evidence/aimc-hybrid-language-model-serving/hybrid_output_comparison.json")
    traces = governor.get("traces", [])
    crosssim = next((item for item in traces if item.get("tool") == "crosssim"), {})
    aihwkit = next((item for item in traces if item.get("tool") == "aihwkit"), {})
    totals = runtime.get("totals", {})
    return [
        {"name": "tiny_task_pass", "pass": tiny.get("pass") is True and tiny.get("candidate_metric") == 0.9375},
        {"name": "serving_task_rehearsal_pass", "pass": serving_task.get("pass") is True and serving_task.get("baseline_metric") == 1.0 and serving_task.get("candidate_metric") == 0.9375},
        {"name": "serving_package_carries_task_metric", "pass": serving_comparison.get("metric") == "next_token_accuracy" and serving_comparison.get("pass") is True},
        {"name": "crosssim_governor_accepts_12", "pass": crosssim.get("payload_status") == "accepted" and crosssim.get("analog_service_count") == 12},
        {"name": "aihwkit_governor_falls_back_12", "pass": aihwkit.get("payload_status") == "rejected" and aihwkit.get("digital_or_maintenance_count") == 12},
        {"name": "guarded_runtime_has_12_models", "pass": totals.get("models") == 12},
        {"name": "guarded_runtime_has_46_fallbacks", "pass": totals.get("physical_guarded_digital_fallback_commands") == 46},
        {"name": "compiler_has_12_models", "pass": len(compiler.get("models", [])) == 12},
        {"name": "target_compiler_covers_12_models", "pass": len(compiled.get("models", [])) == 12 and compiled.get("command_count") == 321 and compiled.get("register_write_count") == 460},
        {"name": "target_bytecode_is_reproducible_shape", "pass": bytecode.get("schema_version") == "aimc_target_bytecode.v1" and bytecode.get("word_width_bits") == 64 and bytecode.get("word_count") == compiled.get("command_count") and len(bytecode.get("words", [])) == bytecode.get("word_count") and all(isinstance(item.get("word"), str) and item.get("word", "").startswith("0x") for item in bytecode.get("words", []))},
        {"name": "target_bytecode_reference_interpreter_passes", "pass": bytecode_reference.get("status") == "reference_interpreter_pass" and bytecode_reference.get("word_count") == compiled.get("command_count") and bytecode_reference.get("decoded_command_count") == compiled.get("command_count") and bytecode_reference.get("total_planning_cycles") == compiled.get("estimated_cycles") and bytecode_reference.get("errors") == []},
        {"name": "sram_allocations_fit_profile", "pass": all(item.get("sram_bytes_used", SRAM_CAPACITY_BYTES + 1) <= SRAM_CAPACITY_BYTES for item in compiled.get("sram_memory_maps", []))},
        {"name": "hardware_profile_is_bound", "pass": profile.get("profile_id") == "educational-hybrid-tile-v1" and compiler.get("shared_hardware", {}).get("profile_id") == profile.get("profile_id") and all(model.get("hardware_profile_id") == profile.get("profile_id") for model in compiler.get("models", []))},
        {"name": "charge_transfer_spec_is_bound", "pass": charge_spec.get("target_profile_id") == profile.get("profile_id") and charge_spec.get("simulation_requirements", {}).get("all_code_count") == 16 and charge_spec.get("simulation_requirements", {}).get("mismatch_trials_required") >= 100},
        {"name": "continuous_sar_spec_is_bound", "pass": continuous_sar_spec.get("hardware_profile_id") == profile.get("profile_id") and continuous_sar_spec.get("topology") == "pmos_only_to_vdd" and continuous_sar_spec.get("required_cycles_per_conversion") == 4 and continuous_sar_spec.get("required_representative_conversions") == 5},
        {"name": "physical_gate_is_consistent_blocked", "pass": physical.get("status") == "blocked_physical_converter_evidence_is_consistent"},
    ]


def main() -> int:
    task_python = python_with("onnx")
    python = sys.executable
    commands = [
        ("transformer_vertical_slice", [python, "scripts/run_hybrid_transformer_vertical_slice.py"]),
        ("deep_transformer_governor", [task_python, "scripts/run_deep_mlp_integrated_governor.py"]),
        ("tiny_task_evaluation", [task_python, "scripts/run_tiny_mlp_task_evaluation.py"]),
        ("language_model_task_rehearsal", [python, "scripts/run_language_model_serving_task_rehearsal.py"]),
        ("language_model_serving_package", [python, "scripts/generate_language_model_serving_package.py"]),
        ("shared_compiler_package", [python, "scripts/build_hybrid_compiler_runtime_package.py"]),
        ("target_compiler", [python, "scripts/compile_hybrid_transformer_execution_package.py"]),
        ("target_bytecode_reference", [python, "scripts/run_target_bytecode_reference.py"]),
        ("guarded_runtime", [python, "scripts/run_guarded_hybrid_workload_runtime.py"]),
        ("workload_comparison", [python, "scripts/generate_hybrid_workload_comparison_report.py"]),
        ("physical_evidence_gate", [python, "scripts/validate_aimc_physical_evidence.py"]),
        ("charge_transfer_spec", [python, "scripts/validate_aimc_charge_transfer_spec.py"]),
        ("continuous_physical_sar_spec", [python, "scripts/validate_aimc_continuous_physical_sar_spec.py"]),
        ("current_state", [python, "scripts/generate_current_aimc_system_state.py"]),
        ("portfolio_validation", [python, "scripts/validate_aimc_workload_portfolio.py"]),
        ("project_validation", [python, "scripts/validate_project.py"]),
    ]
    results = [run(label, command) for label, command in commands]
    checks = artifact_checks()
    report = {
        "schema_version": "aimc_end_to_end_regression.v1",
        "status": "pass_software_vertical_slice_physical_converter_blocked" if all(item["pass"] for item in results) and all(item["pass"] for item in checks) else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "python": python,
        "task_python": task_python,
        "task_environment_note": "The task runner uses the sibling backend virtualenv when the default interpreter lacks ONNX.",
        "results": results,
        "artifact_checks": checks,
        "claim_boundary": "This regression proves reproducible software-side workload, compiler, simulator-replay, guarded-runtime, and report-validation steps. It does not prove physical converter acceptance, measured board latency, measured energy, calibrated silicon, or production readiness.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# AIMC End-To-End Regression",
        "",
        f"- status: `{report['status']}`",
        f"- generated: `{report['generated_at']}`",
        f"- task Python: `{task_python}`",
        "",
        "| check | pass |",
        "| --- | --- |",
    ]
    lines.extend(f"| `{item['label']}` | `{item['pass']}` |" for item in results)
    lines.extend(["", "## Artifact Checks", "", "| check | pass |", "| --- | --- |"])
    lines.extend(f"| `{item['name']}` | `{item['pass']}` |" for item in checks)
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    markdown = "\n".join(lines)
    OUT_MD.write_text(markdown, encoding="utf-8")
    REVIEW_MD.write_text(markdown, encoding="utf-8")
    site_result = run("site_build", [python, "scripts/build_site.py"])
    results.append(site_result)
    report["results"] = results
    report["status"] = "pass_software_vertical_slice_physical_converter_blocked" if all(item["pass"] for item in results) and all(item["pass"] for item in checks) else "failed"
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# AIMC End-To-End Regression",
        "",
        f"- status: `{report['status']}`",
        f"- generated: `{report['generated_at']}`",
        f"- task Python: `{task_python}`",
        "",
        "| check | pass |",
        "| --- | --- |",
    ]
    lines.extend(f"| `{item['label']}` | `{item['pass']}` |" for item in results)
    lines.extend(["", "## Artifact Checks", "", "| check | pass |", "| --- | --- |"])
    lines.extend(f"| `{item['name']}` | `{item['pass']}` |" for item in checks)
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    markdown = "\n".join(lines)
    OUT_MD.write_text(markdown, encoding="utf-8")
    REVIEW_MD.write_text(markdown, encoding="utf-8")
    print(f"regression_status,{report['status']}")
    print(f"json,{OUT_JSON}")
    return 0 if report["status"].startswith("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
