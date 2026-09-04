#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
OUT_JSON = EVIDENCE / "first-real-converter-candidate-packet.json"
OUT_MD = EVIDENCE / "first-real-converter-candidate-packet.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def file_record(path: Path, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": rel(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def build_packet() -> dict[str, Any]:
    rc = load_json(EVIDENCE / "converter-starter-extracted-rc-ngspice.json")
    parasitic = load_json(EVIDENCE / "converter-starter-parasitic-load-estimate.json")
    ultra = load_json(EVIDENCE / "sky130-ultra-sense-frontend-candidate.json")
    preflight = load_json(EVIDENCE / "converter-post-layout-current-preflight.json")
    discovery = load_json(EVIDENCE / "converter-post-layout-real-artifact-discovery.json")

    packet_files = [
        file_record(ROOT / rc["source_netlist"], "starter macro extracted RC netlist"),
        file_record(ROOT / rc["generated_deck"], "starter macro transient deck"),
        file_record(ROOT / rc["csv"], "starter macro transient measurements"),
        file_record(ROOT / ultra["files"]["extracted_spice"]["path"], "ultra sense extracted frontend netlist"),
        file_record(ROOT / ultra["generated_deck"], "ultra sense frontend ngspice deck"),
        file_record(ROOT / ultra["csv"], "ultra sense frontend measurements"),
    ]
    missing_files = [item for item in packet_files if not item["exists"]]

    current_candidate = discovery.get("candidate_workspace", {})
    preflight_issues = preflight.get("issues", [])
    numeric_blockers = [
        item["message"]
        for item in preflight_issues
        if isinstance(item, dict) and item.get("category") in {"numeric_boundary", "noise_boundary"}
    ]
    file_blockers = [
        item["message"]
        for item in preflight_issues
        if isinstance(item, dict) and item.get("category") == "missing_file"
    ]
    identity_blockers = [
        item["message"]
        for item in preflight_issues
        if isinstance(item, dict) and "run_id" in str(item.get("message"))
    ]

    same_run_id = "aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001"
    return {
        "result_type": "first_real_converter_candidate_packet",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "proposed_run_id": same_run_id,
        "status": "partial_measurement_packet_ready_not_strict_submission_ready",
        "ready_for_strict_submission": False,
        "accepted_post_layout_written": False,
        "source_artifacts": {
            "rc_macro": rel(EVIDENCE / "converter-starter-extracted-rc-ngspice.json"),
            "parasitic_load": rel(EVIDENCE / "converter-starter-parasitic-load-estimate.json"),
            "ultra_frontend": rel(EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"),
            "preflight": rel(EVIDENCE / "converter-post-layout-current-preflight.json"),
            "real_artifact_discovery": rel(EVIDENCE / "converter-post-layout-real-artifact-discovery.json"),
        },
        "file_packet": packet_files,
        "missing_packet_file_count": len(missing_files),
        "current_candidate_non_scaffold_file_count": current_candidate.get("non_scaffold_file_count"),
        "current_preflight_status": preflight.get("status"),
        "current_preflight_issue_count": preflight.get("issue_count"),
        "measured_terms": {
            "voltage_v": rc.get("supply_v"),
            "temperature_c": 27.0,
            "starter_row_final_v": rc.get("row_final_v"),
            "starter_row_90_when_s": rc.get("row_90_when_s"),
            "starter_row_99_when_s": rc.get("row_99_when_s"),
            "starter_row_90_to_99_s": rc.get("row_90_to_99_s"),
            "starter_total_pin_charge_energy_j": parasitic.get("total_estimated_pin_charge_energy_j"),
            "starter_max_settle_0p1pct_s": parasitic.get("max_settle_0p1pct_s"),
            "ultra_frontend_transfer_ratio": ultra.get("minimum_sample_to_sense_transfer_ratio"),
            "ultra_frontend_remaining_transfer_improvement_x": ultra.get("remaining_transfer_improvement_x"),
            "ultra_frontend_direct_sample_to_sense_capacitance_ff": ultra.get("direct_sample_to_sense_capacitance_ff"),
            "ultra_frontend_passing_sign_case_count": ultra.get("passing_sign_case_count"),
        },
        "candidate_payload_terms_that_can_be_filled_now": {
            "converter_id": "aimc_readout_candidate_001",
            "run_id": same_run_id,
            "measurement_level": "post_layout_simulation",
            "simulation.simulator": "ngspice",
            "simulation.voltage_v": rc.get("supply_v"),
            "simulation.temperature_c": 27.0,
            "extraction.parasitic_format": "extracted-spice",
        },
        "candidate_payload_terms_still_missing": {
            "extraction.extracted_netlist": "one complete extracted netlist for the claimed converter/readout object",
            "simulation.model_files": "same-run model/setup file for the claimed converter/readout object",
            "energy.adc_energy_per_conversion": "supply-current integration for the readout decision, not only pin capacitance",
            "energy.dac_energy_per_row_drive": "supply-current integration for the row-drive event, not only pin capacitance",
            "latency.conversion_time_ns": "full readout decision time, not only row RC settling",
            "noise.output_noise_rms": "measured or simulated output noise at the digital code boundary",
            "noise.input_referred_noise": "input-referred readout noise for the same run",
            "area.adc_area_um2": "physical ADC/readout area for the claimed object",
            "area.dac_area_um2": "physical DAC/row-drive area for the claimed object",
            "break_even_rerun.rerun_artifact": "break-even rerun produced from the same measured values",
        },
        "preflight_blocker_summary": {
            "numeric_or_noise_blockers": numeric_blockers,
            "missing_file_blockers": file_blockers,
            "identity_blockers": identity_blockers,
        },
        "next_command_sequence": [
            "python3 scripts/run_converter_starter_extracted_rc_ngspice.py",
            "python3 scripts/generate_first_real_converter_candidate_packet.py",
            "python3 scripts/run_converter_post_layout_candidate_readiness.py",
            "python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
        ],
        "claim_boundary": {
            "allowed": "collects the strongest local starter measurements into one first-candidate packet and names exactly which strict payload fields remain unsupported",
            "not_allowed": "does not fill the canonical candidate payload, does not write accepted post-layout evidence, and does not prove a 10-bit DAC, 12-bit ADC, comparator noise, DRC/LVS, or replacement economics",
        },
    }


def write_markdown(packet: dict[str, Any]) -> None:
    measured = packet["measured_terms"]
    fillable = packet["candidate_payload_terms_that_can_be_filled_now"]
    missing = packet["candidate_payload_terms_still_missing"]
    lines = [
        "# First Real Converter Candidate Packet",
        "",
        f"- status: `{packet['status']}`",
        f"- candidate id: `{packet['candidate_id']}`",
        f"- proposed run id: `{packet['proposed_run_id']}`",
        f"- ready for strict submission: `{packet['ready_for_strict_submission']}`",
        f"- accepted post-layout written: `{packet['accepted_post_layout_written']}`",
        f"- current candidate non-scaffold files: `{packet['current_candidate_non_scaffold_file_count']}`",
        f"- current preflight status: `{packet['current_preflight_status']}`",
        f"- current preflight issue count: `{packet['current_preflight_issue_count']}`",
        f"- missing packet files: `{packet['missing_packet_file_count']}`",
        "",
        "## First Principle",
        "",
        "A candidate packet is not a claim that the converter works. It is the smallest honest bundle of things we know about one candidate. It separates measured terms from missing terms so the payload cannot quietly turn estimates into accepted evidence.",
        "",
        "The present packet says the extracted-RC path runs, the starter capacitance has a first-order energy and settling estimate, and the ultra frontend preserves signal sign but still loses too much voltage before the latch target.",
        "",
        "## Measured Terms Available Now",
        "",
        f"- supply voltage V: `{measured['voltage_v']}`",
        f"- assumed temperature C for this packet: `{measured['temperature_c']}`",
        f"- starter row final V: `{measured['starter_row_final_v']:.9f}`",
        f"- starter row 90 when s: `{measured['starter_row_90_when_s']:.6e}`",
        f"- starter row 99 when s: `{measured['starter_row_99_when_s']:.6e}`",
        f"- starter total pin charge energy J: `{measured['starter_total_pin_charge_energy_j']:.6e}`",
        f"- starter max settle 0.1 percent s: `{measured['starter_max_settle_0p1pct_s']:.6e}`",
        f"- ultra frontend transfer ratio: `{measured['ultra_frontend_transfer_ratio']:.6f}`",
        f"- ultra frontend remaining transfer improvement: `{measured['ultra_frontend_remaining_transfer_improvement_x']:.2f}x`",
        f"- ultra frontend direct sample-to-sense capacitance fF: `{measured['ultra_frontend_direct_sample_to_sense_capacitance_ff']}`",
        f"- ultra frontend passing sign cases: `{measured['ultra_frontend_passing_sign_case_count']}`",
        "",
        "## Payload Terms We Can Fill Now",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in fillable.items())
    lines.extend([
        "",
        "These fields are identity and setup fields. They do not make the candidate accepted.",
        "",
        "## Payload Terms Still Missing",
        "",
    ])
    lines.extend(f"- `{key}`: {value}" for key, value in missing.items())
    lines.extend([
        "",
        "## File Packet",
        "",
    ])
    for item in packet["file_packet"]:
        lines.append(f"- `{item['role']}`: `{item['path']}` exists `{item['exists']}` bytes `{item['bytes']}`")
    lines.extend([
        "",
        "## Next Commands",
        "",
    ])
    lines.extend(f"- `{command}`" for command in packet["next_command_sequence"])
    lines.extend([
        "",
        "## Refused Claim",
        "",
        packet["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(packet)
    print("first_real_converter_candidate_packet")
    print(f"status,{packet['status']}")
    print(f"candidate_id,{packet['candidate_id']}")
    print(f"ready_for_strict_submission,{packet['ready_for_strict_submission']}")
    print(f"current_preflight_issue_count,{packet['current_preflight_issue_count']}")
    print(f"missing_packet_file_count,{packet['missing_packet_file_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
