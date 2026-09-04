#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from preflight_converter_post_layout_payload import build_report as build_preflight
from preview_converter_post_layout_submission import build_report as build_preview
from validate_converter_post_layout_same_run import validate_same_run
from validate_converter_post_layout_payload import SCHEMA, load_json, validate_payload, validate_referenced_files


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PACKET = EVIDENCE / "first-real-converter-candidate-packet.json"
WORKSPACE = EVIDENCE / "first-real-converter-rehearsal-payload"
PAYLOAD = WORKSPACE / "payload.json"
OUT_JSON = EVIDENCE / "first-real-converter-rehearsal-payload.json"
OUT_MD = EVIDENCE / "first-real-converter-rehearsal-payload.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def payload_ref(path: Path) -> str:
    resolved = path.resolve()
    payload_dir = PAYLOAD.resolve().parent
    return str(resolved.relative_to(payload_dir)) if resolved.is_relative_to(payload_dir) else rel(resolved)


def build_payload(packet: dict[str, Any]) -> dict[str, Any]:
    measured = packet["measured_terms"]
    run_id = packet["proposed_run_id"]
    macro_netlist = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice"
    model_file = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/sky130-ngspice.includes"
    rerun_artifact = EVIDENCE / "converter-starter-parasitic-break-even-rerun.json"
    return {
        "result_type": "converter_post_layout_evidence",
        "converter_id": packet["candidate_id"],
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": payload_ref(macro_netlist),
            "parasitic_format": "extracted-spice",
            "includes_row_dac": False,
            "includes_sar_readout": False,
            "includes_shared_mux": False,
            "includes_references": False,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": "ngspice",
            "command": "python3 scripts/run_converter_starter_extracted_rc_ngspice.py",
            "process_corner": "sky130 starter extracted RC; not transistor corner signoff",
            "voltage_v": measured["voltage_v"],
            "temperature_c": measured["temperature_c"],
            "model_files": [payload_ref(model_file)],
            "run_id": run_id,
        },
        "energy": {
            "adc_energy_per_conversion": 0.0,
            "dac_energy_per_row_drive": measured["starter_total_pin_charge_energy_j"],
            "energy_unit": "joule",
            "method": "starter pin-charge estimate only; ADC supply energy not measured",
            "run_id": run_id,
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": 0.0,
            "settling_time_ns": measured["starter_max_settle_0p1pct_s"] * 1e9,
            "method": "starter RC settling only; conversion decision latency not measured",
            "run_id": run_id,
        },
        "noise": {
            "output_noise_rms": None,
            "input_referred_noise": None,
            "meets_output_noise_budget": False,
            "method": "not measured for this rehearsal payload",
            "run_id": run_id,
        },
        "area": {
            "adc_area_um2": 0.0,
            "dac_area_um2": 0.0,
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": "not measured for this rehearsal payload",
            "run_id": run_id,
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": payload_ref(rerun_artifact),
            "uses_extracted_energy": False,
            "uses_extracted_latency": False,
            "uses_extracted_noise": False,
            "uses_extracted_area": False,
            "uses_same_sharing_rule": True,
            "replacement_decision": "keep_digital_fallback",
            "run_id": run_id,
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generator_or_lab_notebook": rel(Path(__file__)),
            "operator": "local rehearsal generator",
            "source_schema": rel(SCHEMA),
            "run_id": run_id,
        },
        "claim_boundary": {
            "allowed": "rehearses candidate payload wiring from the partial measurement packet without touching the canonical candidate payload",
            "not_allowed": "does not write accepted evidence, does not claim row-DAC/SAR/mux completeness, and does not replace real post-layout converter measurements",
        },
    }


def collect_issues(payload: dict[str, Any]) -> list[str]:
    schema = load_json(SCHEMA)
    issues = validate_payload(payload, schema)
    issues.extend(validate_referenced_files(payload, PAYLOAD))
    issues.extend(validate_same_run(payload))
    return issues


def issue_category(issue: str) -> str:
    if "extraction.includes_" in issue:
        return "incomplete_converter_object"
    if "uses_extracted_" in issue:
        return "not_same_evidence_level"
    if "noise" in issue:
        return "noise_missing"
    if "energy" in issue:
        return "energy_missing"
    if "latency" in issue:
        return "latency_missing"
    if "area" in issue:
        return "area_missing"
    if "must point to an existing file" in issue:
        return "missing_file"
    return "strict_boundary"


def build_report() -> dict[str, Any]:
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    payload = build_payload(packet)
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    PAYLOAD.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    issues = collect_issues(payload)
    preflight = build_preflight(PAYLOAD)
    preview = build_preview(PAYLOAD, EVIDENCE / "accepted-post-layout")
    return {
        "result_type": "first_real_converter_rehearsal_payload",
        "status": "rehearsal_payload_written_still_rejected",
        "source_packet": rel(PACKET),
        "payload": rel(PAYLOAD),
        "canonical_candidate_payload_touched": False,
        "ready_for_strict_submission": False,
        "strict_issue_count": len(issues),
        "strict_issues": [{"category": issue_category(issue), "message": issue} for issue in issues],
        "preflight_status": preflight.get("status"),
        "preflight_issue_count": preflight.get("issue_count"),
        "preview_status": preview.get("status"),
        "preview_would_write_accepted_evidence": preview.get("would_write_accepted_evidence"),
        "blockers_removed_compared_with_canonical_preflight": {
            "identity_run_id_placeholders": "removed in rehearsal",
            "simulation_voltage_temperature_placeholders": "removed in rehearsal",
            "referenced_file_placeholders": "removed in rehearsal",
        },
        "remaining_real_blockers": {
            "converter_object": "the rehearsal netlist is an RC starter macro and does not include real row DAC, SAR readout, shared mux, or references",
            "adc_energy": "ADC/readout supply energy is still not measured",
            "conversion_latency": "full conversion decision latency is still not measured",
            "noise": "output noise and input-referred noise are still not measured",
            "area": "ADC and DAC physical area are still not measured",
            "break_even": "rerun uses starter estimates, not accepted extracted energy, latency, noise, and area",
        },
        "claim_boundary": {
            "allowed": "shows which strict blockers remain after identity, setup, and existing-file wiring are rehearsed from the partial packet",
            "not_allowed": "does not modify the canonical candidate payload, does not write accepted evidence, and does not make the starter RC macro a real converter",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Rehearsal Payload",
        "",
        f"- status: `{report['status']}`",
        f"- source packet: `{report['source_packet']}`",
        f"- payload: `{report['payload']}`",
        f"- canonical candidate payload touched: `{report['canonical_candidate_payload_touched']}`",
        f"- ready for strict submission: `{report['ready_for_strict_submission']}`",
        f"- strict issue count: `{report['strict_issue_count']}`",
        f"- preflight status: `{report['preflight_status']}`",
        f"- preview would write accepted evidence: `{report['preview_would_write_accepted_evidence']}`",
        "",
        "## First Principle",
        "",
        "A rehearsal payload is a controlled failure. It fills the identity fields, setup fields, and existing file references so we can see what remains when the easy wiring mistakes are gone.",
        "",
        "The result should still fail. If it passed, the validator would be treating starter RC evidence as a complete converter. The useful result is a smaller and clearer failure list.",
        "",
        "## Blockers Removed Compared With The Canonical Scaffold",
        "",
    ]
    lines.extend(f"- `{key}`: {value}" for key, value in report["blockers_removed_compared_with_canonical_preflight"].items())
    lines.extend([
        "",
        "## Remaining Real Blockers",
        "",
    ])
    lines.extend(f"- `{key}`: {value}" for key, value in report["remaining_real_blockers"].items())
    lines.extend([
        "",
        "## Strict Issues",
        "",
    ])
    lines.extend(f"- `{item['category']}`: {item['message']}" for item in report["strict_issues"])
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_rehearsal_payload")
    print(f"status,{report['status']}")
    print(f"payload,{report['payload']}")
    print(f"ready_for_strict_submission,{report['ready_for_strict_submission']}")
    print(f"strict_issue_count,{report['strict_issue_count']}")
    print(f"preview_would_write_accepted_evidence,{report['preview_would_write_accepted_evidence']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
