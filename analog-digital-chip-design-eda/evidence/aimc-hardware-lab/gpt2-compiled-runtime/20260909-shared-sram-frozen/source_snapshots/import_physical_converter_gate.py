#!/usr/bin/env python3
"""Normalize the EDA converter physical gate for the workload evidence package."""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json"
DEFAULT_STARTER_AREA = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-area-measurement.json"
DEFAULT_READINESS = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.json"
DEFAULT_ACTIVE_MACRO_ROOT = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "active-converter-macro-candidate"
DEFAULT_ACTIVE_MACRO_TRANSIENT_ROOT = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "active-converter-macro-transient"
DEFAULT_COUPLED_BIT = ROOT.parent.parent / "analog-digital-chip-design-eda" / "evidence" / "aimc-simulator-adapters" / "sky130-coupled-dac-comparator-bit.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_active_macro_candidate() -> dict[str, Any] | None:
    reports = sorted(DEFAULT_ACTIVE_MACRO_ROOT.glob("*/active-converter-macro-candidate.json"))
    if not reports:
        return None
    eligible = []
    for candidate_path in reports:
        candidate_raw = json.loads(candidate_path.read_text(encoding="utf-8"))
        unverified = candidate_raw.get("unverified_top_level_connections", [])
        includes_physical_preamp = "sky130_transistor_active_isolation_pair" in candidate_raw.get("included_cells", [])
        physical_preamp_ready = includes_physical_preamp and candidate_raw.get("physical_preamp_routing_complete", False)
        legacy_macro_ready = not includes_physical_preamp and candidate_raw.get("top_level_ports_complete", True) and not any(item.startswith("physical_preamp_") for item in unverified)
        if candidate_raw.get("top_level_ports_complete", True) and (legacy_macro_ready or physical_preamp_ready):
            eligible.append(candidate_path)
    report_path = max(
        eligible,
        key=lambda candidate_path: json.loads(candidate_path.read_text(encoding="utf-8")).get("run_id", ""),
    ) if eligible else reports[-1]
    raw = json.loads(report_path.read_text(encoding="utf-8"))
    eda_root = ROOT.parent.parent / "analog-digital-chip-design-eda"
    extracted_path = eda_root / raw.get("extracted_netlist", "missing-netlist")
    boundary = None
    if "sky130_transistor_active_isolation_pair" in raw.get("included_cells", []):
        auditor = runpy.run_path(str(eda_root / "scripts/audit_extracted_converter_boundary.py"))["audit"]
        boundary = auditor(extracted_path.read_text()) if extracted_path.is_file() else {"physical_preamp_routing_complete": False, "reason": "final netlist missing"}
    area_path = report_path.parent / "active-converter-macro-area-measurement.json"
    area = json.loads(area_path.read_text(encoding="utf-8")) if area_path.exists() else None
    return {
        "source": str(report_path),
        "source_sha256": sha256(report_path),
        "status": raw.get("status"),
        "run_id": raw.get("run_id"),
        "layout": raw.get("layout"),
        "extracted_netlist": raw.get("extracted_netlist"),
        "magic_returncode": raw.get("magic_returncode"),
        "magic_drc_count": raw.get("magic_drc_count"),
        "netlist_exists": raw.get("netlist_exists", False),
        "extracted_sky130_device_count": raw.get("extracted_sky130_device_count", 0),
        "extracted_subcircuit_count": raw.get("extracted_subcircuit_count", 0),
        "included_cells": raw.get("included_cells", []),
        "transistor_geometry_present": raw.get("transistor_geometry_present", False),
        "starter_geometry_present": raw.get("starter_geometry_present", False),
        "verified_top_level_connections": raw.get("verified_top_level_connections", []),
        "unverified_top_level_connections": raw.get("unverified_top_level_connections", []),
        "differential_input_integration_complete": raw.get("differential_input_integration_complete", False),
        "physical_preamp_routing_complete": boundary["physical_preamp_routing_complete"] if boundary else raw.get("physical_preamp_routing_complete", False),
        "recorded_physical_preamp_routing_complete": raw.get("physical_preamp_routing_complete", False),
        "physical_preamp_final_netlist_audit": boundary,
        "physical_preamp_extracted_equivalences": raw.get("physical_preamp_extracted_equivalences", {}),
        "strict_signoff_ready": raw.get("strict_signoff_ready", False),
        "candidate_area_measurement": ({
            "source": str(area_path),
            "source_sha256": sha256(area_path),
            "status": area.get("status"),
            "bounding_area_um2": area.get("bounding_area_um2"),
            "width_um": area.get("width_um"),
            "height_um": area.get("height_um"),
            "strict_signoff": area.get("strict_signoff", False),
        } if area else {"status": "not_imported", "strict_signoff": False}),
    }


def latest_active_macro_transient() -> dict[str, Any] | None:
    reports = sorted(DEFAULT_ACTIVE_MACRO_TRANSIENT_ROOT.glob("*/result.json"))
    reports = [path for path in reports if json.loads(path.read_text()).get("evidence_kind") != "hypothetical_netlist_reconnection"]
    if not reports:
        return None
    report_path = reports[-1]
    raw = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        "source": str(report_path),
        "source_sha256": sha256(report_path),
        "status": raw.get("status"),
        "netlist": raw.get("netlist"),
        "netlist_sha256": raw.get("netlist_sha256"),
        "decision_time_ns": raw.get("decision_time_ns"),
        "measured_case_count": raw.get("measured_case_count"),
        "polarity_pass_count": raw.get("polarity_pass_count"),
        "logic_margin_pass_count": raw.get("logic_margin_pass_count"),
        "rows": raw.get("rows", []),
        "accepted_converter": raw.get("accepted_converter", False),
    }


def coupled_dac_comparator_bit() -> dict[str, Any] | None:
    if not DEFAULT_COUPLED_BIT.exists():
        return None
    raw = json.loads(DEFAULT_COUPLED_BIT.read_text(encoding="utf-8"))
    return {
        "source": str(DEFAULT_COUPLED_BIT),
        "source_sha256": sha256(DEFAULT_COUPLED_BIT),
        "status": raw.get("status"),
        "case_count": raw.get("case_count"),
        "measured_case_count": raw.get("measured_case_count"),
        "correct_polarity_count": raw.get("correct_polarity_count"),
        "all_polarities_correct": raw.get("all_polarities_correct", False),
        "failing_codes": raw.get("failing_codes", []),
        "claim_boundary": raw.get("claim_boundary", {}),
    }


def import_gate(path: Path, starter_area_path: Path | None = None) -> dict[str, Any]:
    source = json.loads(path.read_text(encoding="utf-8"))
    missing = [item["path"] for item in source.get("required_extracted_artifacts", []) if not item.get("present")]
    starter_area = None
    if starter_area_path is None:
        starter_area_path = DEFAULT_STARTER_AREA
    if starter_area_path.exists():
        raw_area = json.loads(starter_area_path.read_text(encoding="utf-8"))
        starter_area = {
            "source": str(starter_area_path),
            "source_sha256": sha256(starter_area_path),
            "status": raw_area.get("status"),
            "measured_cell_count": raw_area.get("measured_cell_count"),
            "cell_count": raw_area.get("cell_count"),
            "macro_bounding_area_um2": next(
                (row.get("bounding_area_um2") for row in raw_area.get("cells", []) if row.get("name") == "aimc_converter_macro"),
                None,
            ),
            "strict_signoff": False,
        }
    readiness = None
    if DEFAULT_READINESS.exists():
        raw_readiness = json.loads(DEFAULT_READINESS.read_text(encoding="utf-8"))
        readiness = {
            "source": str(DEFAULT_READINESS),
            "source_sha256": sha256(DEFAULT_READINESS),
            "status": raw_readiness.get("status"),
            "audit_status": raw_readiness.get("audit_status"),
            "progress_status": raw_readiness.get("progress_status"),
            "preflight_status": raw_readiness.get("preflight_status"),
            "placeholder_count": raw_readiness.get("placeholder_count"),
            "missing_or_unresolved_file_count": raw_readiness.get("missing_or_unresolved_file_count"),
            "open_checklist_items": raw_readiness.get("open_checklist_items"),
            "preflight_issue_count": raw_readiness.get("preflight_issue_count"),
            "ready_for_strict_submission": raw_readiness.get("ready_for_strict_submission", False),
        }
    active_macro = latest_active_macro_candidate()
    active_macro_transient = latest_active_macro_transient()
    coupled_bit = coupled_dac_comparator_bit()
    return {
        "schema_version": "physical-converter-gate-import-v0.1",
        "result_type": "guarded_physical_converter_gate_import",
        "provenance": {
            "source_gate": str(path),
            "source_gate_sha256": sha256(path),
            "workbench": source.get("workbench"),
        },
        "status": source.get("status"),
        "physical_cells": {
            "required": source.get("required_cell_count"),
            "present": source.get("present_cell_count"),
            "missing": source.get("missing_cell_count"),
            "all_required_present": source.get("all_required_cells_present", False),
        },
        "extracted_artifacts": {
            "required": source.get("required_extracted_artifact_count"),
            "present": source.get("present_extracted_artifact_count"),
            "missing": source.get("missing_extracted_artifact_count"),
            "missing_paths": missing,
            "all_required_present": source.get("all_required_extracted_artifacts_present", False),
        },
        "starter_layout_measurement": starter_area or {"status": "not_imported", "strict_signoff": False},
        "candidate_readiness": readiness or {"status": "not_imported", "ready_for_strict_submission": False},
        "active_macro_candidate": active_macro or {"status": "not_imported", "strict_signoff_ready": False},
        "active_macro_transient": active_macro_transient or {"status": "not_imported", "accepted_converter": False},
        "coupled_dac_comparator_bit": coupled_bit or {"status": "not_imported", "all_polarities_correct": False},
        "analog_allowed_for_physical_claim": bool(source.get("ready_for_candidate_post_layout_payload", False)),
        "next_actions": [
            "produce the extracted layout-area record from the assembled converter macro boundary",
            "run the same-run post-layout break-even rerun using extracted area, energy, latency, noise, and the declared sharing rule",
            "rerun the EDA physical-cell gate and only then re-enable physical analog placement claims",
        ],
        "claim_boundary": {
            "allowed": "The named converter cells and missing extracted-artifact state are imported into the workload package.",
            "refused": "Starter payloads, skeleton scripts, and temporary positive-path fixtures are not promoted to extracted physical evidence.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.gate.exists():
        raise SystemExit(f"physical gate not found: {args.gate}")
    result = import_gate(args.gate)
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "physical_converter_gate_import.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "status": result["status"], "analog_allowed_for_physical_claim": result["analog_allowed_for_physical_claim"]}, indent=2))


if __name__ == "__main__":
    main()
