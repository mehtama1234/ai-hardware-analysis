#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "payload.json"
CHECKLIST = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
LEDGER = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-blocker-ledger.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-edit-plan.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-edit-plan.md"


FIELD_SOURCES = {
    "converter_id": ("layout run name or silicon run id", "non-empty string naming one converter object"),
    "extraction.extracted_netlist": ("post-layout extraction output", "path to an existing extracted netlist file"),
    "extraction.parasitic_format": ("extraction tool output type", "SPEF, DSPF, extracted SPICE, or a similarly concrete format"),
    "simulation.simulator": ("simulation or measurement setup", "non-empty simulator, lab setup, or measurement system name"),
    "simulation.command": ("reproducible run record", "command, script path, or lab procedure id"),
    "simulation.process_corner": ("model deck or measured condition", "corner name or measured operating condition"),
    "simulation.voltage_v": ("same run as energy/noise/latency", "positive number in volts"),
    "simulation.temperature_c": ("same run as energy/noise/latency", "number in Celsius"),
    "simulation.model_files[0]": ("process, parasitic, or measurement model", "path to an existing model/setup file"),
    "energy.adc_energy_per_conversion": ("supply integration over ADC conversion window", "positive joules"),
    "energy.dac_energy_per_row_drive": ("supply integration over row-drive window", "positive joules"),
    "latency.conversion_time_ns": ("ADC decision timing measurement", "positive nanoseconds"),
    "latency.settling_time_ns": ("row/sample settling measurement", "positive nanoseconds"),
    "noise.output_noise_rms": ("readout noise measurement from same path", "number at or below 0.004"),
    "noise.input_referred_noise": ("same noise result referred to the input boundary", "numeric value"),
    "area.adc_area_um2": ("layout area report", "positive square microns"),
    "area.dac_area_um2": ("layout area report", "positive square microns"),
    "break_even_rerun.rerun_artifact": ("source break-even rerun with extracted values", "path to an existing rerun JSON"),
    "break_even_rerun.replacement_decision": ("source break-even rerun summary", "replace_converter_break_even_assumption or keep_digital_fallback"),
    "provenance.created_at": ("run metadata", "timestamp for the run"),
    "provenance.generator_or_lab_notebook": ("run metadata", "script, notebook, lab record, or CI job"),
    "provenance.operator": ("run metadata", "person, tool, or CI job that produced the evidence"),
    "provenance.run_id": ("run metadata", "same non-empty run id used by simulation, energy, latency, noise, area, and break_even_rerun"),
    "simulation.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "energy.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "latency.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "noise.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "area.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "break_even_rerun.run_id": ("same run as provenance", "must equal provenance.run_id"),
    "netlist": ("post-layout extraction output", "create the referenced netlist file"),
    "model_file_0": ("process, parasitic, or measurement model", "create the referenced model/setup file"),
    "rerun_artifact": ("source break-even rerun", "create the referenced rerun JSON"),
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_plan() -> dict[str, Any]:
    checklist = load_json(CHECKLIST)
    ledger = load_json(LEDGER)
    blockers = ledger.get("blockers") if isinstance(ledger.get("blockers"), list) else []
    blocker_fields = {item.get("field") for item in blockers if isinstance(item, dict)}
    items = checklist.get("items") if isinstance(checklist.get("items"), list) else []
    edits = []
    for item in items:
        if not isinstance(item, dict):
            continue
        field = str(item.get("field"))
        source, accepted_shape = FIELD_SOURCES.get(field, ("same post-layout or measured run", str(item.get("what_to_supply"))))
        edits.append({
            "field": field,
            "group": item.get("group"),
            "current_value": item.get("current_value"),
            "evidence_source": source,
            "accepted_value_shape": accepted_shape,
            "validator_check": item.get("what_to_supply"),
            "currently_blocked": field in blocker_fields,
        })
    return {
        "result_type": "converter_post_layout_candidate_edit_plan",
        "status": "candidate_edit_plan_ready",
        "payload": str(PAYLOAD.relative_to(ROOT)),
        "source_checklist": str(CHECKLIST.relative_to(ROOT)),
        "source_blocker_ledger": str(LEDGER.relative_to(ROOT)),
        "edit_count": len(edits),
        "blocked_edit_count": sum(1 for item in edits if item["currently_blocked"]),
        "edits": edits,
        "recommended_order": [
            "files",
            "identity",
            "simulation",
            "extraction",
            "energy",
            "latency",
            "noise",
            "area",
            "break_even",
            "provenance",
        ],
        "check_command": "python3 scripts/run_converter_post_layout_candidate_readiness.py",
        "claim_boundary": {
            "allowed": "turns the current blocker ledger into a field-by-field candidate payload edit plan",
            "not_allowed": "does not create post-layout files, does not invent values, does not submit evidence, and does not prove analog replacement",
        },
    }


def write_markdown(plan: dict[str, Any]) -> None:
    lines = [
        "# Converter Post-Layout Candidate Edit Plan",
        "",
        f"- status: `{plan['status']}`",
        f"- payload: `{plan['payload']}`",
        f"- edit count: `{plan['edit_count']}`",
        f"- blocked edit count: `{plan['blocked_edit_count']}`",
        "",
        "This plan says how to edit the candidate payload once real post-layout or measured converter evidence exists. It keeps the fill work tied to evidence sources, accepted value shapes, and the command that checks the result.",
        "",
        "## First Principle",
        "",
        "Editing the payload is part of the proof. Each value must come from the same converter object. If energy comes from one run, noise from another, and area from a guess, the package is only a collection of numbers. The candidate becomes evidence only when the fields point back to one physical converter path.",
        "",
        "The plan therefore starts with inspectable files, then fills identity and simulation conditions, then fills cost values, and only then records the break-even decision.",
        "",
        "## Recommended Order",
        "",
    ]
    lines.extend(f"- `{item}`" for item in plan["recommended_order"])
    lines.extend(["", "## Field Edits", ""])
    for edit in plan["edits"]:
        lines.extend([
            f"### {edit['field']}",
            "",
            f"- group: `{edit['group']}`",
            f"- current value: `{edit['current_value']}`",
            f"- evidence source: {edit['evidence_source']}",
            f"- accepted value shape: {edit['accepted_value_shape']}",
            f"- validator check: {edit['validator_check']}",
            f"- currently blocked: `{edit['currently_blocked']}`",
            "",
        ])
    lines.extend([
        "## Check Command",
        "",
        f"`{plan['check_command']}`",
        "",
        "## Refused Claim",
        "",
        plan["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    plan = build_plan()
    OUT_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(plan)
    print("converter_post_layout_candidate_edit_plan")
    print(f"status,{plan['status']}")
    print(f"edit_count,{plan['edit_count']}")
    print(f"blocked_edit_count,{plan['blocked_edit_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
