#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-workspace-audit.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.md"


GROUPS = [
    ("identity", ["converter_id", "measurement_level"]),
    ("extraction", ["extraction."]),
    ("simulation", ["simulation."]),
    ("energy", ["energy."]),
    ("latency", ["latency."]),
    ("noise", ["noise."]),
    ("area", ["area."]),
    ("break_even", ["break_even_rerun."]),
    ("provenance", ["provenance."]),
]

EXPLANATIONS = {
    "converter_id": "Name the exact converter macro, extracted view, or silicon measurement run.",
    "extraction.extracted_netlist": "Point to the extracted netlist file inside the workspace.",
    "extraction.parasitic_format": "Say whether the file is SPEF, DSPF, extracted SPICE, or another concrete extraction format.",
    "simulation.simulator": "Name the simulator or measurement system that produced the values.",
    "simulation.command": "Record the command or lab procedure so the run can be repeated or audited.",
    "simulation.process_corner": "Name the process corner or measured operating condition.",
    "simulation.voltage_v": "Use a numeric supply voltage.",
    "simulation.temperature_c": "Use a numeric temperature.",
    "simulation.model_files[0]": "Point to an existing model or measurement setup file.",
    "energy.adc_energy_per_conversion": "Use positive joules for one ADC conversion.",
    "energy.dac_energy_per_row_drive": "Use positive joules for one DAC row drive.",
    "latency.conversion_time_ns": "Use positive nanoseconds for the ADC decision window.",
    "latency.settling_time_ns": "Use positive nanoseconds for the row/sample settling window.",
    "noise.output_noise_rms": "Use a numeric RMS value at or below 0.004.",
    "noise.input_referred_noise": "Use a numeric input-referred noise value.",
    "area.adc_area_um2": "Use positive square microns for ADC area.",
    "area.dac_area_um2": "Use positive square microns for DAC area.",
    "break_even_rerun.rerun_artifact": "Point to the source rerun artifact before accepted submission writes its own rerun.",
    "break_even_rerun.replacement_decision": "Use a real decision such as replace_local_break_even or keep_digital_fallback.",
    "provenance.created_at": "Record the run timestamp.",
    "provenance.generator_or_lab_notebook": "Name the script, notebook, or lab record.",
    "provenance.operator": "Name the person or CI job responsible for the run.",
    "provenance.run_id": "Name the one post-layout or measured run that produced all accepted converter values.",
    "simulation.run_id": "Use the same run id as provenance.run_id.",
    "energy.run_id": "Use the same run id as provenance.run_id.",
    "latency.run_id": "Use the same run id as provenance.run_id.",
    "noise.run_id": "Use the same run id as provenance.run_id.",
    "area.run_id": "Use the same run id as provenance.run_id.",
    "break_even_rerun.run_id": "Use the same run id as provenance.run_id.",
}

SAME_RUN_ITEMS = [
    ("provenance", "provenance.run_id"),
    ("simulation", "simulation.run_id"),
    ("energy", "energy.run_id"),
    ("latency", "latency.run_id"),
    ("noise", "noise.run_id"),
    ("area", "area.run_id"),
    ("break_even", "break_even_rerun.run_id"),
]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing audit artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def group_for(field: str) -> str:
    for group, prefixes in GROUPS:
        if any(field == prefix.rstrip(".") or field.startswith(prefix) for prefix in prefixes):
            return group
    return "other"


def get_field(payload: dict[str, Any], field: str) -> Any:
    value: Any = payload
    normalized = field.replace("[0]", ".0")
    for part in normalized.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit():
            index = int(part)
            value = value[index] if index < len(value) else None
        else:
            return None
    return value


def present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def main() -> None:
    audit = load(AUDIT_JSON)
    payload_path = ROOT / str(audit.get("payload"))
    payload = load(payload_path) if payload_path.exists() else {}
    placeholders = audit.get("placeholders") if isinstance(audit.get("placeholders"), list) else []
    missing_files = audit.get("missing_or_unresolved_files") if isinstance(audit.get("missing_or_unresolved_files"), list) else []
    items = []
    for item in placeholders:
        if not isinstance(item, dict):
            continue
        field = str(item.get("field", "unknown"))
        items.append({
            "group": group_for(field),
            "field": field,
            "current_value": item.get("value"),
            "what_to_supply": EXPLANATIONS.get(field, "Replace the placeholder with a real value from the extracted or measured run."),
        })
    for item in missing_files:
        if not isinstance(item, dict):
            continue
        items.append({
            "group": "files",
            "field": str(item.get("kind", "file")),
            "current_value": item.get("path"),
            "what_to_supply": "Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.",
        })
    existing_fields = {item["field"] for item in items}
    for group, field in SAME_RUN_ITEMS:
        if field in existing_fields or present(get_field(payload, field)):
            continue
        items.append({
            "group": group,
            "field": field,
            "current_value": "missing",
            "what_to_supply": EXPLANATIONS[field],
        })
    report = {
        "result_type": "converter_post_layout_candidate_fill_checklist",
        "status": "fill_checklist_ready",
        "source_audit": str(AUDIT_JSON.relative_to(ROOT)),
        "workspace": audit.get("workspace"),
        "payload": audit.get("payload"),
        "item_count": len(items),
        "groups": sorted(set(item["group"] for item in items)),
        "items": items,
        "next_commands": [
            "python3 scripts/audit_converter_post_layout_candidate_workspace.py",
            f"python3 scripts/preflight_converter_post_layout_payload.py {audit.get('payload')}",
            f"python3 scripts/submit_converter_post_layout_payload.py {audit.get('payload')}",
        ],
        "claim_boundary": {
            "allowed": "turns the current scaffold audit into a field-by-field editing checklist",
            "not_allowed": "does not supply real values, does not validate physics, does not submit evidence, and does not replace converter break-even assumptions",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Converter Post-Layout Candidate Fill Checklist",
        "",
        f"- status: `{report['status']}`",
        f"- source audit: `{report['source_audit']}`",
        f"- workspace: `{report['workspace']}`",
        f"- payload: `{report['payload']}`",
        f"- checklist items: `{report['item_count']}`",
        "",
        "This checklist translates the scaffold audit into the exact edits needed before preflight can pass.",
        "",
        "## First Principle",
        "",
        "Filling the payload is not clerical work. Each field ties a number to a physical object. The netlist says what circuit was tested. The model files say what electrical world the circuit lived in. Energy, latency, noise, and area say what the converter costs. The rerun artifact says what system decision follows from those costs.",
        "",
        "When every placeholder is gone and every referenced file exists, the next question becomes physics: whether the numbers are good enough. Until then the question is simpler: the packet is still incomplete.",
        "",
    ]
    for group in sorted(set(item["group"] for item in items)):
        lines.extend([f"## {group.replace('_', ' ').title()}", ""])
        for item in [entry for entry in items if entry["group"] == group]:
            lines.append(f"- `{item['field']}` currently `{item['current_value']}`: {item['what_to_supply']}")
        lines.append("")
    lines.extend([
        "## Next Commands",
        "",
        *[f"- `{command}`" for command in report["next_commands"]],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_candidate_fill_checklist")
    print(f"status,{report['status']}")
    print(f"items,{report['item_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
