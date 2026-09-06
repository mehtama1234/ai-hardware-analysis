#!/usr/bin/env python3
"""Regression check for measured board and power evidence boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_LAB_EVIDENCE = (
    ROOT.parents[2] / "analog-digital-chip-design-eda" / "evidence" / "aimc-hardware-lab"
)
IMPORT_TEMPLATES = ROOT.parent / "review-package-demo" / "import-templates"
sys.path.insert(0, str(ROOT))

from evidence_imports import build_measured_readiness_report, validate_imported_evidence  # noqa: E402
from claim_readiness import build_claim_readiness  # noqa: E402


def load_current(source_file: str) -> dict:
    path = CURRENT_LAB_EVIDENCE / source_file
    if not path.exists():
        raise SystemExit(f"missing current lab evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_template(template_file: str) -> dict:
    path = IMPORT_TEMPLATES / template_file
    if not path.exists():
        raise SystemExit(f"missing import template: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def measured_board_payload() -> dict:
    return {
        "package_id": "pkg-measured-test",
        "workload_id": "wake-word-v0",
        "board_id": "aimc-board-a1",
        "board_revision": "revA",
        "runtime_version": "runtime-v1",
        "runtime_trace_id": "runtime-trace-001",
        "latency_ms": 1.2,
        "p50_latency_ms": 1.1,
        "p95_latency_ms": 1.4,
        "repetition_count": 5,
        "start_timestamp": "2026-08-29T18:00:00Z",
        "end_timestamp": "2026-08-29T18:00:02Z",
        "host_overhead_boundary": "reported_separately",
        "trace": [{"layer_id": "dense_0", "latency_ms": 0.42}],
        "fallback_events": [],
        "provenance": {
            "tool": "bench-runtime-service",
            "measurement_level": "measured_board",
        },
    }


def measured_power_payload() -> dict:
    return {
        "package_id": "pkg-measured-test",
        "workload_id": "wake-word-v0",
        "board_id": "aimc-board-a1",
        "runtime_trace_id": "runtime-trace-001",
        "energy_uj": 12.3,
        "average_power_mw": 4.1,
        "peak_power_mw": 5.2,
        "sampling_rate": "1000 Hz",
        "integration_start_timestamp": "2026-08-29T18:00:00Z",
        "integration_end_timestamp": "2026-08-29T18:00:02Z",
        "host_overhead_boundary": "reported_separately",
        "power_trace": [
            {"time_ms": 0.0, "voltage_v": 0.8, "current_a": 0.005, "power_mw": 4.0},
            {"time_ms": 1.0, "voltage_v": 0.8, "current_a": 0.0052, "power_mw": 4.16},
        ],
        "temperature_trace": [
            {"time_ms": 0.0, "temperature_c": 25.1},
            {"time_ms": 1.0, "temperature_c": 26.0},
        ],
        "measurement_setup": {
            "meter": "joulescope-js220",
            "measured_rail": "core_vdd",
            "includes_host_overhead": False,
            "not_measured_hardware": False,
        },
        "provenance": {
            "tool": "bench-power-service",
            "measurement_level": "measured_board_power",
        },
    }


def expect(name: str, condition: bool, details: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL {name}: {details}")
    print(f"PASS {name}: {details}")


def expect_issue(name: str, readiness: dict, expected_fragment: str) -> None:
    issues = readiness.get("issues", [])
    issue_text = "\n".join(str(issue) for issue in issues)
    expect(name, expected_fragment in issue_text, f"found boundary issue: {expected_fragment}")


def expect_no_issue(name: str, readiness: dict, blocked_fragments: list[str]) -> None:
    issue_text = "\n".join(str(issue) for issue in readiness.get("issues", []))
    leaked = [fragment for fragment in blocked_fragments if fragment in issue_text]
    expect(name, not leaked, f"no blocked measured-boundary issue leaked: {leaked}")


def check_source(source_id: str, payload: dict, expected_ready: bool) -> dict:
    ordinary_errors = validate_imported_evidence(source_id, payload)
    readiness = build_measured_readiness_report(source_id, payload)
    expect(f"{source_id} ordinary validation", not ordinary_errors, "structural schema accepted")
    expect(
        f"{source_id} measured readiness",
        readiness["measured_ready"] is expected_ready,
        f"measured_ready={readiness['measured_ready']} issues={len(readiness['issues'])}",
    )
    return readiness


def measurement_with(runtime_payload: dict, power_payload: dict) -> dict:
    return {
        "required_sources": [
            {
                "id": "board_runtime",
                "status": "imported artifact",
                "artifact_name": "board-runtime-trace.json",
                "confidence": "high",
                "latest_import": {"import_id": "runtime-import", "payload": runtime_payload},
            },
            {
                "id": "power_thermal",
                "status": "imported artifact",
                "artifact_name": "power-thermal-report.json",
                "confidence": "high",
                "latest_import": {"import_id": "power-import", "payload": power_payload},
            },
        ],
        "summary": {"package_id": runtime_payload.get("package_id")},
    }


def claim_by_id(readiness: dict, claim_id: str) -> dict:
    return next(claim for claim in readiness["lab_claims"] if claim["id"] == claim_id)


def check_energy_synchronization(runtime_payload: dict, power_payload: dict) -> None:
    matched = build_claim_readiness(measurement_with(runtime_payload, power_payload))
    matched_energy = claim_by_id(matched, "C3")
    expect(
        "matched measured energy claim",
        matched_energy["status"] == "supported",
        f"status={matched_energy['status']} issues={matched_energy['quality_issues']}",
    )
    details = {detail["source_id"]: detail for detail in matched_energy["evidence_details"]}
    expect(
        "matched runtime detail carries sync fields",
        details["board_runtime"]["package_id"] == runtime_payload["package_id"]
        and details["board_runtime"]["workload_id"] == runtime_payload["workload_id"]
        and details["board_runtime"]["runtime_trace_id"] == runtime_payload["runtime_trace_id"]
        and details["board_runtime"]["start_timestamp"] == runtime_payload["start_timestamp"]
        and details["board_runtime"]["end_timestamp"] == runtime_payload["end_timestamp"]
        and details["board_runtime"]["measurement_level"] == "measured_board",
        "runtime detail exposes trace/package/workload/window/provenance",
    )
    expect(
        "matched power detail carries sync fields",
        details["power_thermal"]["package_id"] == power_payload["package_id"]
        and details["power_thermal"]["workload_id"] == power_payload["workload_id"]
        and details["power_thermal"]["integration_start_timestamp"] == power_payload["integration_start_timestamp"]
        and details["power_thermal"]["integration_end_timestamp"] == power_payload["integration_end_timestamp"]
        and details["power_thermal"]["measurement_level"] == "measured_board_power",
        "power detail exposes package/workload/window/provenance",
    )

    mismatched_power = json.loads(json.dumps(power_payload))
    mismatched_power["runtime_trace_id"] = "different-runtime-trace"
    mismatched = build_claim_readiness(measurement_with(runtime_payload, mismatched_power))
    mismatched_energy = claim_by_id(mismatched, "C3")
    expect(
        "mismatched measured energy claim",
        mismatched_energy["status"] == "needs review",
        f"status={mismatched_energy['status']}",
    )
    expect(
        "mismatched measured energy reason",
        any("do not describe the same run" in issue for issue in mismatched_energy["quality_issues"]),
        "same-run issue reported for runtime_trace_id",
    )


def main() -> None:
    current_runtime = load_current("board_runtime.json")
    current_power = load_current("power_thermal.json")
    measured_runtime = measured_board_payload()
    measured_power = measured_power_payload()
    runtime_template = load_template("measured-board-runtime.template.json")
    power_template = load_template("measured-power-thermal.template.json")

    runtime_readiness = check_source("board_runtime", current_runtime, expected_ready=False)
    expect_issue(
        "local runtime rejects local board id",
        runtime_readiness,
        "board_id must name a real board or instrumented runtime source",
    )
    expect_issue(
        "local runtime rejects local provenance",
        runtime_readiness,
        "provenance marks this runtime as local or not measured hardware",
    )
    expect_issue(
        "local runtime rejects missing measured level",
        runtime_readiness,
        "provenance.measurement_level must be measured_board or instrumented_runtime",
    )

    power_readiness = check_source("power_thermal", current_power, expected_ready=False)
    expect_issue(
        "local power rejects missing meter",
        power_readiness,
        "measurement_setup.meter must name the meter or instrument source",
    )
    expect_issue(
        "local power rejects local estimate",
        power_readiness,
        "payload marks power/thermal as local estimate or not measured hardware",
    )
    expect_issue(
        "local power rejects missing voltage/current samples",
        power_readiness,
        "power_trace must contain numeric time_ms, voltage_v, and current_a samples",
    )
    expect_issue(
        "local power rejects missing measured level",
        power_readiness,
        "provenance.measurement_level must be measured_board_power or instrumented_power",
    )

    measured_runtime_readiness = check_source("board_runtime", measured_runtime, expected_ready=True)
    expect_no_issue(
        "measured runtime keeps board path clean",
        measured_runtime_readiness,
        ["local simulation", "local or not measured hardware", "measurement_level must"],
    )
    expect(
        "measured runtime provenance",
        measured_runtime["provenance"]["measurement_level"] == "measured_board",
        "measurement_level=measured_board",
    )

    measured_power_readiness = check_source("power_thermal", measured_power, expected_ready=True)
    expect_no_issue(
        "measured power keeps meter path clean",
        measured_power_readiness,
        ["meter must", "local estimate", "voltage_v", "measurement_level must"],
    )
    expect(
        "measured power provenance",
        measured_power["provenance"]["measurement_level"] == "measured_board_power",
        "measurement_level=measured_board_power",
    )

    check_source("board_runtime", runtime_template, expected_ready=True)
    check_source("power_thermal", power_template, expected_ready=True)
    check_energy_synchronization(measured_runtime, measured_power)


if __name__ == "__main__":
    main()
