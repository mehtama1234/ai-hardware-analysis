#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "sources" / "evidence" / "converter-post-layout-payload.template.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-template.md"
OUT_REPORT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-payload-template.json"


def main() -> None:
    template = {
        "template_only": True,
        "result_type": "converter_post_layout_evidence",
        "converter_id": "REPLACE_WITH_CONVERTER_MACRO_OR_MEASUREMENT_ID",
        "measurement_level": "post_layout_simulation",
        "target_boundary": {
            "adc_bits": 12,
            "dac_bits": 10,
            "output_noise_budget": 0.004,
        },
        "extraction": {
            "extracted_netlist": "REPLACE_WITH_EXTRACTED_NETLIST_PATH",
            "parasitic_format": "spef_or_dspf_or_extracted_spice",
            "includes_row_dac": True,
            "includes_sar_readout": True,
            "includes_shared_mux": True,
            "includes_references": True,
            "includes_sample_path": True,
        },
        "simulation": {
            "simulator": "REPLACE_WITH_SIMULATOR_NAME",
            "command": "REPLACE_WITH_REPRODUCIBLE_POST_LAYOUT_COMMAND",
            "process_corner": "REPLACE_WITH_PROCESS_CORNER",
            "voltage_v": "REPLACE_WITH_NUMERIC_SUPPLY",
            "temperature_c": "REPLACE_WITH_NUMERIC_TEMPERATURE",
            "model_files": ["REPLACE_WITH_MODEL_FILE_PATH"],
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "energy": {
            "adc_energy_per_conversion": "REPLACE_WITH_POSITIVE_JOULES",
            "dac_energy_per_row_drive": "REPLACE_WITH_POSITIVE_JOULES",
            "energy_unit": "joule",
            "method": "integrate named supply rail over the same conversion and row-drive windows used in the target",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "latency": {
            "adc_comparisons": 12,
            "conversion_time_ns": "REPLACE_WITH_POSITIVE_NS",
            "settling_time_ns": "REPLACE_WITH_POSITIVE_NS",
            "method": "measure conversion time and row settling under the same 10-bit input and 12-bit output target",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "noise": {
            "output_noise_rms": "REPLACE_WITH_NUMERIC_RMS_AT_OR_BELOW_0.004",
            "input_referred_noise": "REPLACE_WITH_NUMERIC_INPUT_REFERRED_NOISE",
            "meets_output_noise_budget": True,
            "method": "measure output noise at the readout boundary used by the break-even table",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "area": {
            "adc_area_um2": "REPLACE_WITH_POSITIVE_AREA",
            "dac_area_um2": "REPLACE_WITH_POSITIVE_AREA",
            "replication_or_sharing_rule": "64 rows, 4 columns, 4 converter instances, 16 outputs per conversion cost",
            "method": "use extracted or layout-reported converter macro area",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "sharing": {
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "break_even_rerun": {
            "rerun_artifact": "REPLACE_WITH_BREAK_EVEN_RERUN_ARTIFACT",
            "uses_extracted_energy": True,
            "uses_extracted_latency": True,
            "uses_extracted_noise": True,
            "uses_extracted_area": True,
            "uses_same_sharing_rule": True,
            "replacement_decision": "REPLACE_WITH_replace_or_keep_digital_fallback",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "provenance": {
            "created_at": "REPLACE_WITH_RUN_TIMESTAMP",
            "generator_or_lab_notebook": "REPLACE_WITH_SCRIPT_OR_NOTEBOOK",
            "operator": "REPLACE_WITH_PERSON_OR_CI_JOB",
            "source_schema": "sources/evidence/converter-post-layout-evidence-schema.json",
            "run_id": "REPLACE_WITH_SHARED_RUN_ID",
        },
        "claim_boundary": {
            "allowed": "after replacement fields are filled with real extracted or measured values and the validator passes, this payload can support a converter break-even replacement decision",
            "not_allowed": "this template is not evidence and must not be imported as a post-layout result",
        },
    }
    report = {
        "result_type": "converter_post_layout_payload_template",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "template_defined_not_evidence",
        "template": str(OUT_JSON.relative_to(ROOT)),
        "validator": "scripts/validate_converter_post_layout_payload.py",
        "claim_boundary": {
            "allowed": "shows every field a real extracted post-layout or measured silicon payload must provide",
            "not_allowed": "does not claim any extracted converter result exists and is intentionally not validator-ready",
        },
    }
    OUT_JSON.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Post-Layout Payload Template",
        "",
        "This is the field-by-field template for the real converter payload.",
        "",
        f"- status: `{report['status']}`",
        f"- template: `{report['template']}`",
        f"- validator: `{report['validator']}`",
        "",
        "## First-Principles Reading",
        "",
        "The converter claim has to join four objects that are easy to confuse. The layout creates a physical circuit. Extraction turns that layout into a circuit with wire and device parasitics. Simulation or silicon measurement turns that extracted circuit into numbers. The break-even rerun decides whether those numbers are good enough to replace the old digital fallback.",
        "",
        "A useful payload cannot skip any of those objects. If it has energy but no extracted netlist, the number is floating. If it has an extracted netlist but no model files or command, the run cannot be repeated. If it has noise but no shared converter rule, the cost is not the same system. If it has all circuit numbers but no break-even rerun, it has not answered the system question.",
        "",
        "## How To Fill It",
        "",
        "- replace every `REPLACE_WITH...` value with a value from the extracted post-layout run or measured silicon run",
        "- keep `adc_bits` at `12`, `dac_bits` at `10`, and `output_noise_budget` at or below `0.004`",
        "- keep the sharing rule at 64 rows, 4 columns, 4 converter instances, and 16 outputs per conversion cost unless the break-even model is changed too",
        "- use one shared `run_id` across provenance, simulation, energy, latency, noise, area, and break-even rerun fields",
        "- rerun the break-even calculation with extracted energy, latency, noise, area, and the same sharing rule",
        "- run `python3 scripts/validate_converter_post_layout_payload.py FILLED_PAYLOAD.json` before using it as evidence",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("converter_post_layout_payload_template")
    print(f"status,{report['status']}")
    print(f"template,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
