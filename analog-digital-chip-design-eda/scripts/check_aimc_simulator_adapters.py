#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters"
OUTPUT_CONTRACT = ROOT / "sources" / "evidence" / "analog-simulator-adapter-output-schema.json"
PLACEMENT = MEASURE / "model-impact-governor-requests.csv"
NONIDEALITY = MEASURE / "analog-nonideality-stack.csv"
JSON_OUT = OUT_DIR / "simulator-adapter-status.json"
MD_OUT = OUT_DIR / "simulator-adapter-status.md"
AIHWKIT_PAYLOAD = OUT_DIR / "aihwkit-analog-error-simulation.json"
CROSSSIM_PAYLOAD = OUT_DIR / "crosssim-analog-error-simulation.json"
AIHWKIT_SMOKE = OUT_DIR / "aihwkit-smoke-run.json"
CROSSSIM_SMOKE = OUT_DIR / "crosssim-smoke-run.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def aihwkit_smoke() -> dict[str, object]:
    if not module_available("aihwkit"):
        return {
            "status": "skipped",
            "reason": "aihwkit is not importable",
            "claim_effect": "no claim upgraded",
        }
    try:
        import torch
        import aihwkit
        from aihwkit.nn import AnalogLinear
        from aihwkit.simulator.configs import TorchInferenceRPUConfig

        torch.manual_seed(7)
        layer = AnalogLinear(4, 2, rpu_config=TorchInferenceRPUConfig())
        sample_input = torch.tensor([[1.0, -0.5, 0.25, 2.0]], dtype=torch.float32)
        analog_output = layer(sample_input).detach()
        report = {
            "status": "ran",
            "tool": "aihwkit",
            "tool_version": getattr(aihwkit, "__version__", "unknown"),
            "torch_version": getattr(torch, "__version__", "unknown"),
            "analog_forward_shape": list(analog_output.shape),
            "analog_forward_sum": round(float(analog_output.sum()), 6),
            "claim_effect": "availability smoke only; not strict simulator evidence until a contract payload is produced",
        }
        AIHWKIT_SMOKE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report
    except Exception as exc:
        return {
            "status": "failed",
            "reason": str(exc),
            "claim_effect": "no claim upgraded",
        }


def crosssim_smoke() -> dict[str, object]:
    if not module_available("simulator"):
        return {
            "status": "skipped",
            "reason": "CrossSim simulator module is not importable",
            "claim_effect": "no claim upgraded",
        }
    try:
        import numpy as np
        from simulator import AnalogCore, CrossSimParameters

        params = CrossSimParameters()
        weights = np.array([[1.0, -0.5], [0.25, 0.75]], dtype=float)
        vector = np.array([2.0, 4.0], dtype=float)
        core = AnalogCore(weights, params=params)
        analog_output = core @ vector
        ideal_output = weights @ vector
        max_abs_error = round(float(np.max(np.abs(analog_output - ideal_output))), 10)
        report = {
            "status": "ran",
            "tool": "crosssim",
            "matrix_shape": [2, 2],
            "vector_length": 2,
            "analog_output": [round(float(item), 6) for item in analog_output.tolist()],
            "ideal_output": [round(float(item), 6) for item in ideal_output.tolist()],
            "max_abs_error": max_abs_error,
            "claim_effect": "availability smoke only; not strict simulator evidence until a contract payload is produced",
        }
        CROSSSIM_SMOKE.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report
    except Exception as exc:
        return {
            "status": "failed",
            "reason": str(exc),
            "claim_effect": "no claim upgraded",
        }


def tool_status(name: str, modules: list[str], planned_payload: Path, smoke_report: Path, smoke: dict[str, object]) -> dict[str, object]:
    available = any(module_available(module) for module in modules)
    return {
        "tool": name,
        "status": "available" if available else "skipped",
        "checked_modules": modules,
        "planned_payload": str(planned_payload.relative_to(ROOT)),
        "smoke_report": str(smoke_report.relative_to(ROOT)),
        "smoke_run": smoke,
        "reason": "python module importable" if available else "python module not installed in the active environment",
        "claim_effect": (
            "may emit a normalized simulator payload after a real adapter run is implemented"
            if available
            else "no claim upgraded"
        ),
    }


def adapter_reading(tool: dict[str, object]) -> str:
    smoke = tool.get("smoke_run") if isinstance(tool.get("smoke_run"), dict) else {}
    if smoke.get("status") == "ran":
        return "availability smoke ran; strict payload still required"
    if tool.get("status") == "available":
        return "module importable; smoke did not produce strict evidence"
    return f"skipped; {tool.get('reason', 'tool is not available')}"


def build_candidate_rows(rows: list[dict[str, str]], final_residual: float, aihwkit: dict[str, object], crosssim: dict[str, object]) -> list[dict[str, object]]:
    candidates = [row for row in rows if row.get("governor_decision") == "1"]
    output = []
    for row in candidates:
        output.append(
            {
                "layer_id": row.get("policy"),
                "operator": row.get("operator", row.get("policy", "unknown")),
                "local_residual_relative": final_residual,
                "local_residual_q8": int(round(final_residual * 128)),
                "aihwkit_result": adapter_reading(aihwkit),
                "crosssim_result": adapter_reading(crosssim),
                "model_sensitivity_q8": int(row.get("sensitivity_q8", "0") or 0),
                "governor_action": int(row.get("governor_action", "0") or 0),
                "claim_effect": "external simulator payload is required before this candidate receives stronger simulator evidence",
            }
        )
    return output


def main() -> int:
    placement_rows = read_rows(PLACEMENT)
    nonideality_rows = read_rows(NONIDEALITY)
    if not nonideality_rows:
        raise SystemExit(f"missing rows in {NONIDEALITY}")
    final = nonideality_rows[-1]
    final_residual = as_float(final, "residual_relative")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    aihwkit = tool_status("aihwkit", ["aihwkit"], AIHWKIT_PAYLOAD, AIHWKIT_SMOKE, aihwkit_smoke())
    crosssim = tool_status("crosssim", ["simulator", "cross_sim"], CROSSSIM_PAYLOAD, CROSSSIM_SMOKE, crosssim_smoke())
    candidates = build_candidate_rows(placement_rows, final_residual, aihwkit, crosssim)
    payload = {
        "result_type": "aimc_simulator_adapter_status",
        "schema_version": "aimc-simulator-adapter-status-v0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": str(ROOT),
        "input_artifacts": {
            "placement_rows": str(PLACEMENT.relative_to(ROOT)),
            "local_nonideality_stack": str(NONIDEALITY.relative_to(ROOT)),
        },
        "run_output_contract": str(OUTPUT_CONTRACT.relative_to(ROOT)),
        "planned_run_payloads": {
            "aihwkit": str(AIHWKIT_PAYLOAD.relative_to(ROOT)),
            "crosssim": str(CROSSSIM_PAYLOAD.relative_to(ROOT)),
        },
        "tools": [aihwkit, crosssim],
        "analog_candidates": candidates,
        "summary": {
            "analog_candidates": len(candidates),
            "tools_available": sum(1 for item in [aihwkit, crosssim] if item["status"] == "available"),
            "tools_skipped": sum(1 for item in [aihwkit, crosssim] if item["status"] == "skipped"),
            "final_local_residual_relative": final_residual,
            "final_local_residual_q8": int(round(final_residual * 128)),
        },
        "claim_boundary": {
            "allowed": "the simulator adapter boundary was checked and tool availability or missing-tool state was recorded without upgrading broad claims",
            "not_allowed": "do not call availability smoke checks calibrated silicon, measured board runtime, measured power, physical signoff, or production readiness",
        },
        "next_handoff": "run the optional simulator payload exporter, validate any real payload, then import only if the guarded importer accepts it",
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# AIMC Simulator Adapter Status",
        "",
        "This report checks whether AIHWKIT or CrossSim can produce stronger analog simulator evidence for the current AIMC proof slice.",
        "",
        f"Run-output contract: `{OUTPUT_CONTRACT.relative_to(ROOT)}`.",
        "",
        "## Result",
        "",
        f"- AIHWKIT: {aihwkit['status']} ({aihwkit['reason']})",
        f"- CrossSim: {crosssim['status']} ({crosssim['reason']})",
        f"- analog candidates: {len(candidates)}",
        f"- local residual: {final_residual:.6f}",
        f"- AIHWKIT future payload: `{AIHWKIT_PAYLOAD.relative_to(ROOT)}`",
        f"- CrossSim future payload: `{CROSSSIM_PAYLOAD.relative_to(ROOT)}`",
        f"- AIHWKIT smoke: {aihwkit['smoke_run']['status']}",
        f"- CrossSim smoke: {crosssim['smoke_run']['status']}",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"]["allowed"],
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
        "## Candidate Comparison",
        "",
        "| Layer | Local residual | AIHWKIT | CrossSim | Claim effect |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for item in candidates:
        lines.append(
            f"| {item['layer_id']} | {item['local_residual_relative']:.6f} | "
            f"{item['aihwkit_result']} | {item['crosssim_result']} | {item['claim_effect']} |"
        )
    lines.extend(["", "## Next Handoff", "", payload["next_handoff"], ""])
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print("aimc_simulator_adapter_status")
    print(f"aihwkit,{aihwkit['status']}")
    print(f"crosssim,{crosssim['status']}")
    print(f"analog_candidates,{len(candidates)}")
    print(f"json,{JSON_OUT}")
    print(f"markdown,{MD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
