#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-fill-checklist.json"
HANDOFF = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-handoff-manifest.json"
READINESS = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-candidate-readiness-run.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-run-recipe.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def fields_for_group(checklist: dict[str, Any], group: str) -> list[str]:
    items = checklist.get("items") if isinstance(checklist.get("items"), list) else []
    return [
        str(item.get("field"))
        for item in items
        if isinstance(item, dict) and item.get("group") == group and item.get("field")
    ]


def main() -> None:
    checklist = load_json(CHECKLIST)
    handoff = load_json(HANDOFF)
    readiness = load_json(READINESS)
    fixed_boundary = handoff.get("fixed_target_boundary") if isinstance(handoff.get("fixed_target_boundary"), dict) else {}
    commands = handoff.get("commands") if isinstance(handoff.get("commands"), dict) else {}
    run_id_fields = [
        "provenance.run_id",
        "simulation.run_id",
        "energy.run_id",
        "latency.run_id",
        "noise.run_id",
        "area.run_id",
        "break_even_rerun.run_id",
    ]
    recipe_steps = [
        {
            "order": 1,
            "name": "choose_converter_layout",
            "action": "Choose one converter layout for the 10-bit DAC input and 12-bit ADC readout target.",
            "proof_object": "one named converter macro, extracted view, or silicon measurement object",
            "payload_fields": ["converter_id"],
        },
        {
            "order": 2,
            "name": "extract_post_layout_circuit",
            "action": "Produce an inspectable extracted circuit file and place it under the candidate netlist folder.",
            "proof_object": "extracted SPICE, DSPF, SPEF, or equivalent extracted circuit artifact",
            "payload_fields": fields_for_group(checklist, "extraction") + ["netlist"],
        },
        {
            "order": 3,
            "name": "collect_run_models_or_measurement_setup",
            "action": "Place process model files or measurement setup records under the candidate models folder.",
            "proof_object": "model deck, corner include, parasitic include, or measurement setup record",
            "payload_fields": ["simulation.model_files[0]", "model_file_0"],
        },
        {
            "order": 4,
            "name": "run_one_named_experiment",
            "action": "Use one non-placeholder run id for the whole post-layout or measured-silicon run.",
            "proof_object": "shared run identity",
            "payload_fields": [
                "provenance.created_at",
                "provenance.generator_or_lab_notebook",
                "provenance.operator",
                *run_id_fields,
            ],
        },
        {
            "order": 5,
            "name": "record_physical_values",
            "action": "Record energy, latency, noise, area, voltage, temperature, and process or measured condition from that same run.",
            "proof_object": "numbers tied to the extracted converter or measured silicon object",
            "payload_fields": fields_for_group(checklist, "energy")
            + fields_for_group(checklist, "latency")
            + fields_for_group(checklist, "noise")
            + fields_for_group(checklist, "area")
            + ["simulation.voltage_v", "simulation.temperature_c", "simulation.process_corner", "simulation.command", "simulation.simulator"],
        },
        {
            "order": 6,
            "name": "check_fixed_boundary",
            "action": "Keep the fixed DAC, ADC, noise, and sharing boundary unless the break-even model changes too.",
            "proof_object": "fixed target boundary",
            "payload_fields": ["target_boundary", "sharing"],
        },
        {
            "order": 7,
            "name": "rerun_break_even",
            "action": "Rerun the break-even calculation with extracted or measured values and place the source rerun JSON under the candidate rerun folder.",
            "proof_object": "source break-even rerun artifact",
            "payload_fields": fields_for_group(checklist, "break_even") + ["rerun_artifact"],
        },
        {
            "order": 8,
            "name": "fill_candidate_payload",
            "action": "Fill payload.json, remove template_only only after all placeholders and file paths are real, then run readiness.",
            "proof_object": "candidate payload ready for strict preflight",
            "payload_fields": ["payload.json", "template_only"],
        },
        {
            "order": 9,
            "name": "strict_submit_only_if_ready",
            "action": "Submit only after readiness reports ready for strict submission.",
            "proof_object": "accepted post-layout rerun and submission report written by the strict command",
            "payload_fields": ["accepted-post-layout"],
        },
    ]
    payload = {
        "result_type": "converter_post_layout_real_run_recipe",
        "status": "real_run_recipe_ready_not_evidence",
        "source_checklist": str(CHECKLIST.relative_to(ROOT)),
        "source_handoff_manifest": str(HANDOFF.relative_to(ROOT)),
        "source_readiness_run": str(READINESS.relative_to(ROOT)),
        "current_candidate_status": readiness.get("status"),
        "ready_for_strict_submission": readiness.get("ready_for_strict_submission"),
        "recipe_steps": recipe_steps,
        "step_count": len(recipe_steps),
        "required_shared_run_id_fields": run_id_fields,
        "fixed_target_boundary": fixed_boundary,
        "commands": {
            "readiness": "python3 scripts/run_converter_post_layout_candidate_readiness.py",
            "submit_if_ready": commands.get("submit_if_ready"),
        },
        "manual_write_forbidden": "accepted-post-layout must be written only by scripts/submit_converter_post_layout_payload.py",
        "claim_boundary": {
            "allowed": "turns the current checklist and handoff manifest into an ordered real-run recipe",
            "not_allowed": "does not provide extracted files, measured values, accepted evidence, or analog replacement proof",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Real Run Recipe Artifact",
        "",
        f"- status: `{payload['status']}`",
        f"- current candidate status: `{payload['current_candidate_status']}`",
        f"- ready for strict submission: `{payload['ready_for_strict_submission']}`",
        f"- step count: `{payload['step_count']}`",
        f"- source checklist: `{payload['source_checklist']}`",
        f"- source handoff manifest: `{payload['source_handoff_manifest']}`",
        "",
        "This generated artifact turns the current fill checklist and handoff manifest into one ordered run recipe.",
        "",
        "## Ordered Steps",
        "",
    ]
    for step in recipe_steps:
        fields = ", ".join(f"`{field}`" for field in step["payload_fields"])
        lines.extend([
            f"### {step['order']}. {step['name']}",
            "",
            f"- action: {step['action']}",
            f"- proof object: `{step['proof_object']}`",
            f"- payload fields: {fields}",
            "",
        ])
    lines.extend([
        "## Shared Run Id Fields",
        "",
        *[f"- `{field}`" for field in run_id_fields],
        "",
        "## Fixed Target Boundary",
        "",
        *[f"- {key}: `{value}`" for key, value in fixed_boundary.items()],
        "",
        "## Commands",
        "",
        *[f"- {name}: `{command}`" for name, command in payload["commands"].items()],
        "",
        "## Manual Write Boundary",
        "",
        payload["manual_write_forbidden"],
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_real_run_recipe")
    print(f"status,{payload['status']}")
    print(f"step_count,{payload['step_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
