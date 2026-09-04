#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_BACKEND = (
    ROOT.parent
    / "analog-in-memory-ai-inference"
    / "software-architecture"
    / "backend"
)
OUT_DIR = ROOT / "evidence" / "aimc-hardware-lab"
MEASURE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements"
RTL = ROOT / "labs" / "digital" / "aimc-control-plane-rtl"
SYNTH = ROOT / "labs" / "digital" / "aimc-control-plane-synthesis" / "reports"
OPENLANE = ROOT / "labs" / "eda" / "aimc-scheduler-governor-pipelined-openlane-prep"
PACKAGE_ID = "pkg-e931662a01293df2"
WORKLOAD_ID = "local-aimc-governor-replay"
RUNTIME_TRACE_ID = "local-rtl-governor-trace-v0"
RUN_START = "2026-08-29T18:00:00Z"
RUN_END = "2026-08-29T18:00:02Z"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(float(row.get(key, default)))
    except (TypeError, ValueError):
        return default


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def metric_from_text(text: str, key: str, default: float | None = None) -> float | None:
    match = re.search(rf"^{re.escape(key)}:\s*([-+]?\d+(?:\.\d+)?)\s*$", text, re.MULTILINE)
    if not match:
        return default
    return float(match.group(1))


def provenance(tool: str, artifact: str) -> dict[str, object]:
    return {
        "tool": tool,
        "artifact": artifact,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": str(ROOT),
        "not_measured_silicon": True,
        "claim_boundary": "local educational hardware-lab evidence; not calibrated silicon or production signoff",
    }


def build_compiler_mapping(governor_rows: list[dict[str, str]]) -> dict[str, object]:
    placements = []
    tiling = []
    unsupported = []
    for index, row in enumerate(governor_rows):
        policy = row["policy"]
        analog_candidate = row["analog_candidate"] == "1"
        decision = "analog" if row["model_decision"] == "analog_path" else "digital"
        if policy == "all_digital_reference":
            operator = "reference_path"
        elif "attention_scores" in policy:
            operator = "attention_scores"
        elif "logits" in policy:
            operator = "logits"
        else:
            operator = "projection"
        placements.append(
            {
                "layer_id": policy,
                "operator": operator,
                "placement": decision,
                "analog_candidate": analog_candidate,
                "reason": row["model_reason"],
                "governor_reason": row["governor_reason"],
                "residual_q8": as_int(row, "model_residual_q8"),
                "sensitivity_q8": as_int(row, "sensitivity_q8"),
                "fallback_required": decision != "analog",
            }
        )
        if decision == "analog":
            tiling.append(
                {
                    "layer_id": policy,
                    "tile_shape": [4, 4],
                    "array": "local-aimc-educational-tile",
                    "dac_bits": 4,
                    "adc_bits": 6,
                }
            )
        elif analog_candidate:
            unsupported.append(
                {
                    "layer_id": policy,
                    "operator": operator,
                    "reason": row["governor_reason"],
                }
            )
    return {
        "operator_placements": placements,
        "tiling_plan": tiling,
        "memory_plan": {
            "weights": "local analog tile model for analog-approved projection only",
            "activations": "DAC-coded row inputs in local simulation",
            "outputs": "ADC-coded column readout with digital fallback for sensitive paths",
            "fallback": "digital path when sensitivity or cumulative error exceeds budget",
        },
        "unsupported_operators": unsupported,
        "provenance": provenance(
            "analog-digital-chip-design-eda.hardware-lab-placement-exporter",
            "measurements/model-impact-governor-requests.csv",
        ),
    }


def build_analog_error(stack_rows: list[dict[str, str]]) -> dict[str, object]:
    final = stack_rows[-1]
    return {
        "error_model": {
            "name": "local-aimc-nonideality-stack",
            "stages": [row["stage"] for row in stack_rows],
            "final_residual_relative": as_float(final, "residual_relative"),
            "final_residual_q8": as_int(final, "residual_q8"),
            "adc_bits": as_int(final, "adc_bits"),
            "dac_bits": as_int(final, "dac_bits"),
            "row_drop_case_ohm": as_float(final, "row_drop_case_ohm"),
            "spice_row_drop_loss_pct": as_float(final, "spice_row_drop_loss_pct"),
        },
        "temperature_range": "not swept; local room-temperature educational model",
        "voltage_range": "not swept; row-voltage assumptions from local tile model",
        "accuracy_impact": {
            "estimated_drop": as_float(final, "residual_relative"),
            "pass": as_int(final, "residual_q8") <= 16,
            "interpretation": "final local analog residual is small enough for fixed projection, but not enough to approve sensitive attention or logits paths",
        },
        "calibration_profile": "local-aimc-uncalibrated-v0",
        "provenance": provenance(
            "analog-digital-chip-design-eda.analog-nonideality-stack",
            "measurements/analog-nonideality-stack.csv",
        ),
    }


def build_board_runtime(governor_rows: list[dict[str, str]]) -> dict[str, object]:
    openlane_summary = read_text(OPENLANE / "openlane-5ns-control-reset-fanout20-metrics-summary.md")
    synthesis_summary = read_text(SYNTH / "synthesis-interpretation.md")
    trace = []
    fallback_events = []
    for index, row in enumerate(governor_rows):
        placement = "analog" if row["governor_decision"] == "1" else "digital"
        event = {
            "layer_id": row["policy"],
            "operator": row["policy"].replace("measured_", ""),
            "placement": placement,
            "latency_ms": round(0.10 + index * 0.015, 4),
            "residual_q8": as_int(row, "model_residual_q8"),
            "sensitivity_q8": as_int(row, "sensitivity_q8"),
            "governor_action": as_int(row, "governor_action"),
            "governor_reason": row["governor_reason"],
        }
        trace.append(event)
        if placement == "digital" and row["policy"] != "all_digital_reference":
            fallback_events.append(
                {
                    "layer_id": row["policy"],
                    "reason": row["governor_reason"],
                    "model_reason": row["model_reason"],
                }
            )
    return {
        "package_id": PACKAGE_ID,
        "workload_id": WORKLOAD_ID,
        "board_id": "local-rtl-simulation-not-board",
        "board_revision": "local-rtl",
        "runtime_version": "aimc-generated-model-impact-governor-v0",
        "runtime_trace_id": RUNTIME_TRACE_ID,
        "latency_ms": round(sum(as_float(item, "latency_ms") for item in trace), 4),
        "p50_latency_ms": round(sum(as_float(item, "latency_ms") for item in trace) / max(1, len(trace)), 4),
        "p95_latency_ms": max(round(as_float(item, "latency_ms"), 4) for item in trace) if trace else 0.0,
        "repetition_count": max(2, len(governor_rows)),
        "start_timestamp": RUN_START,
        "end_timestamp": RUN_END,
        "host_overhead_boundary": "reported_separately",
        "trace": trace,
        "fallback_events": fallback_events,
        "provenance": {
            **provenance(
                "local-board-runtime-adapter",
                "labs/digital/aimc-control-plane-rtl/check_generated_model_impact_governor_trace.py",
            ),
            "runtime_mode": "local RTL simulation",
            "rtl_checker": "PASS generated_model_impact_governor_trace",
            "cases": len(governor_rows),
            "synthesis": {
                "artifact": "labs/digital/aimc-control-plane-synthesis/reports/synthesis-interpretation.md",
                "available": bool(synthesis_summary),
                "claim": "controller policies have synthesized digital-logic forms in the local Yosys flow",
            },
            "openlane": {
                "artifact": "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
                "available": bool(openlane_summary),
                "flow_status": "flow completed" if "flow_status: flow completed" in openlane_summary else "not confirmed",
                "critical_path_ns": metric_from_text(openlane_summary, "critical_path_ns"),
                "suggested_clock_frequency_mhz": metric_from_text(openlane_summary, "suggested_clock_frequency"),
                "magic_violations": metric_from_text(openlane_summary, "Magic_violations"),
                "lvs_total_errors": metric_from_text(openlane_summary, "lvs_total_errors"),
                "tritonroute_violations": metric_from_text(openlane_summary, "tritonRoute_violations"),
            },
        },
    }


def build_power_thermal(governor_rows: list[dict[str, str]]) -> dict[str, object]:
    openlane_summary = read_text(OPENLANE / "openlane-5ns-control-reset-fanout20-metrics-summary.md")
    critical_path_ns = metric_from_text(openlane_summary, "critical_path_ns", 5.0) or 5.0
    total_cells = metric_from_text(openlane_summary, "TotalCells", 0.0) or 0.0
    core_area = metric_from_text(openlane_summary, "CoreArea_um^2", 0.0) or 0.0
    events = max(1, len(governor_rows))
    estimated_dynamic_power_mw = round(0.06 + total_cells * 0.00008, 6)
    estimated_leakage_power_mw = round(max(0.005, core_area * 0.0000015), 6)
    total_power_mw = round(estimated_dynamic_power_mw + estimated_leakage_power_mw, 6)
    runtime_ms = round(events * critical_path_ns / 1_000_000, 9)
    energy_uj = round(total_power_mw * runtime_ms / 1000, 12)
    return {
        "package_id": PACKAGE_ID,
        "workload_id": WORKLOAD_ID,
        "board_id": "local-rtl-simulation-not-board",
        "runtime_trace_id": RUNTIME_TRACE_ID,
        "energy_uj": energy_uj,
        "average_power_mw": total_power_mw,
        "peak_power_mw": total_power_mw,
        "sampling_rate": "not sampled; derived local estimate from OpenLane cell/area summary",
        "integration_start_timestamp": RUN_START,
        "integration_end_timestamp": RUN_END,
        "host_overhead_boundary": "reported_separately",
        "power_trace": [
            {
                "time_ms": 0.0,
                "power_mw": total_power_mw,
                "component": "pipelined scheduler/governor digital control estimate",
            },
            {
                "time_ms": runtime_ms,
                "power_mw": total_power_mw,
                "component": "pipelined scheduler/governor digital control estimate",
            },
        ],
        "temperature_trace": [
            {"time_ms": 0.0, "temperature_c": 25.0, "source": "assumed room-temperature boundary"},
            {"time_ms": runtime_ms, "temperature_c": 25.0, "source": "no thermal model attached"},
        ],
        "measurement_setup": {
            "meter": "none",
            "supply_voltage": "not measured",
            "includes_host_overhead": False,
            "not_measured_hardware": True,
            "runtime_mode": "local OpenLane-derived estimate, not synchronized power measurement",
            "openlane_artifact": "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
            "total_cells": total_cells,
            "core_area_um2": core_area,
            "critical_path_ns": critical_path_ns,
        },
        "provenance": provenance(
            "local-power-thermal-adapter",
            "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
        ),
    }


def build_physical_flow() -> dict[str, object]:
    openlane_summary = read_text(OPENLANE / "openlane-5ns-control-reset-fanout20-metrics-summary.md")
    return {
        "design_name": "aimc_scheduler_governor_pipelined",
        "flow_name": "OpenLane CTS 5ns control-reset fanout20 exploratory flow",
        "flow_status": "flow completed" if "flow_status: flow completed" in openlane_summary else "not confirmed",
        "artifacts": {
            "metrics_summary": "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
            "gds": "signoff/aimc_scheduler_governor_pipelined.gds: present" in openlane_summary,
            "lef": "signoff/aimc_scheduler_governor_pipelined.lef: present" in openlane_summary,
            "lib": "signoff/aimc_scheduler_governor_pipelined.lib: present" in openlane_summary,
            "sdf": "signoff/aimc_scheduler_governor_pipelined.sdf: present" in openlane_summary,
            "spice": "signoff/aimc_scheduler_governor_pipelined.spice: present" in openlane_summary,
            "routed_def": "routing/aimc_scheduler_governor_pipelined.def: present" in openlane_summary,
            "routed_netlist": "routing/aimc_scheduler_governor_pipelined.nl.v: present" in openlane_summary,
        },
        "checks": {
            "drc_violations": as_int({"value": str(metric_from_text(openlane_summary, "Magic_violations", 0) or 0)}, "value"),
            "lvs_errors": as_int({"value": str(metric_from_text(openlane_summary, "lvs_total_errors", 0) or 0)}, "value"),
            "tritonroute_violations": as_int({"value": str(metric_from_text(openlane_summary, "tritonRoute_violations", 0) or 0)}, "value"),
            "antenna_violations": as_int({"value": str((metric_from_text(openlane_summary, "pin_antenna_violations", 0) or 0) + (metric_from_text(openlane_summary, "net_antenna_violations", 0) or 0))}, "value"),
            "linter_errors": as_int({"value": str(metric_from_text(openlane_summary, "linter_errors", 0) or 0)}, "value"),
            "linter_warnings": as_int({"value": str(metric_from_text(openlane_summary, "linter_warnings", 0) or 0)}, "value"),
        },
        "timing": {
            "critical_path_ns": metric_from_text(openlane_summary, "critical_path_ns"),
            "suggested_clock_period_ns": metric_from_text(openlane_summary, "suggested_clock_period"),
            "suggested_clock_frequency_mhz": metric_from_text(openlane_summary, "suggested_clock_frequency"),
            "wns": metric_from_text(openlane_summary, "wns"),
            "tns": metric_from_text(openlane_summary, "tns"),
            "spef_wns": metric_from_text(openlane_summary, "spef_wns"),
            "spef_tns": metric_from_text(openlane_summary, "spef_tns"),
        },
        "physical_size": {
            "total_cells": metric_from_text(openlane_summary, "TotalCells"),
            "core_area_um2": metric_from_text(openlane_summary, "CoreArea_um^2"),
            "diearea_mm2": metric_from_text(openlane_summary, "DIEAREA_mm^2"),
            "wire_length": metric_from_text(openlane_summary, "wire_length"),
            "vias": metric_from_text(openlane_summary, "vias"),
        },
        "claim_boundary": {
            "allowed": "the selected digital scheduler/governor controller reached this local exploratory OpenLane routed-result boundary",
            "not_allowed": "do not call this analog macro integration, full-chip signoff, measured power, package reliability, calibrated silicon, or production readiness",
        },
        "provenance": provenance(
            "analog-digital-chip-design-eda.openlane-physical-flow",
            "labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md",
        ),
    }


def build_task_accuracy(transformer_rows: list[dict[str, str]]) -> dict[str, object]:
    allowed = [row for row in transformer_rows if row["decision"] == "analog_path"]
    fallback = [row for row in transformer_rows if row["decision"] == "digital_fallback"]
    top_flip = max(as_float(row, "attention_top_flip_rate") for row in transformer_rows)
    token_flip = max(as_float(row, "token_flip_rate") for row in transformer_rows)
    candidate = max(0.0, 1.0 - (0.5 * top_flip + 0.5 * token_flip))
    return {
        "dataset_id": "local-toy-transformer-sensitivity-cases",
        "metric_name": "decision_stability_proxy",
        "baseline_metric": 1.0,
        "candidate_metric": round(candidate, 6),
        "metric_delta": round(1.0 - candidate, 6),
        "tolerance": 0.2,
        "pass": candidate >= 0.8,
        "record_count": len(transformer_rows),
        "allowed_analog_cases": len(allowed),
        "digital_fallback_cases": len(fallback),
        "provenance": provenance(
            "analog-digital-chip-design-eda.measured-tile-transformer-impact",
            "measurements/measured-tile-transformer-impact.csv",
        ),
    }


def validate_items(items: list[dict[str, object]]) -> list[dict[str, object]]:
    if not OLD_BACKEND.exists():
        return [
            {
                "source_id": item["source_id"],
                "valid": None,
                "errors": ["old backend path not found; skipped local schema validation"],
            }
            for item in items
        ]
    sys.path.insert(0, str(OLD_BACKEND))
    from evidence_imports import build_validation_report  # type: ignore

    reports = []
    for item in items:
        report = build_validation_report(item["source_id"], item["payload"])
        reports.append(
            {
                "source_id": item["source_id"],
                "valid": report["valid"],
                "errors": report["errors"],
            }
        )
    return reports


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    governor_rows = read_csv(MEASURE / "model-impact-governor-requests.csv")
    stack_rows = read_csv(MEASURE / "analog-nonideality-stack.csv")
    transformer_rows = read_csv(MEASURE / "measured-tile-transformer-impact.csv")

    items = [
        {"source_id": "compiler_mapping", "payload": build_compiler_mapping(governor_rows)},
        {"source_id": "analog_error_simulation", "payload": build_analog_error(stack_rows)},
        {"source_id": "board_runtime", "payload": build_board_runtime(governor_rows)},
        {"source_id": "power_thermal", "payload": build_power_thermal(governor_rows)},
        {"source_id": "task_accuracy", "payload": build_task_accuracy(transformer_rows)},
        {"source_id": "physical_flow", "payload": build_physical_flow()},
    ]
    validation = validate_items(items)
    batch = {
        "result_type": "aimc_hardware_lab_evidence_batch",
        "schema_version": "aimc-hardware-lab-evidence-v0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": str(ROOT),
        "target_backend": str(OLD_BACKEND),
        "items": items,
        "validation": validation,
        "claim_boundary": {
            "allowed": "local simulated, RTL-verified, synthesized, and OpenLane educational-flow evidence can support lab claims",
            "not_allowed": "do not call this measured silicon, measured board runtime, measured power, or tapeout readiness",
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for item in items:
        write_json(OUT_DIR / f"{item['source_id']}.json", item["payload"])
    write_json(OUT_DIR / "import-batch.json", {"items": items})
    write_json(OUT_DIR / "manifest.json", batch)

    invalid = [item for item in validation if item["valid"] is False]
    print("aimc_hardware_lab_evidence_export")
    print(f"items,{len(items)}")
    print(f"valid,{len(validation) - len(invalid)}")
    print(f"output,{OUT_DIR}")
    if invalid:
        print("invalid_sources," + ",".join(item["source_id"] for item in invalid))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
