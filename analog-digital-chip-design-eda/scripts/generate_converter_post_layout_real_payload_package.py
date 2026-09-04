#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-payload-package.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-post-layout-real-payload-package.md"


def main() -> None:
    package = {
        "result_type": "converter_post_layout_real_payload_package",
        "status": "real_payload_package_contract_ready",
        "purpose": "Define the exact package a post-layout simulation or measured-silicon converter result must provide before local converter break-even assumptions can be replaced.",
        "submission_command": "python3 scripts/submit_converter_post_layout_payload.py REAL_PAYLOAD.json",
        "required_files": [
            {
                "name": "REAL_PAYLOAD.json",
                "reason": "The structured record that names the converter, target boundary, extraction, simulation, energy, latency, noise, area, sharing, provenance, and claim boundary.",
            },
            {
                "name": "extracted netlist",
                "payload_field": "extraction.extracted_netlist",
                "reason": "The circuit equations must come from extracted layout or measured setup, not from the earlier local behavioral estimate.",
            },
            {
                "name": "process or measurement model files",
                "payload_field": "simulation.model_files[]",
                "reason": "The run must name the device models, corner files, or measurement setup files that set the electrical world being tested.",
            },
            {
                "name": "prior rerun artifact",
                "payload_field": "break_even_rerun.rerun_artifact",
                "reason": "The payload must show the break-even decision it is asking the project to trust before the project writes its own accepted rerun.",
            },
        ],
        "required_numeric_terms": {
            "adc_energy_per_conversion": "energy cost of one readout decision",
            "dac_energy_per_row_drive": "energy cost of driving one selected row",
            "conversion_time_ns": "time cost of the ADC decision",
            "settling_time_ns": "time cost before the sampled value is trustworthy",
            "output_noise_rms": "readout uncertainty after the analog chain",
            "input_referred_noise": "same uncertainty expressed at the array input boundary",
            "adc_area_um2": "physical area cost of readout",
            "dac_area_um2": "physical area cost of row drive",
        },
        "fixed_target_boundary": {
            "dac_bits": 10,
            "adc_bits": 12,
            "output_noise_budget_max": 0.004,
            "rows_served": 64,
            "columns_served": 4,
            "outputs_per_conversion_cost": 16,
            "converter_instances": 4,
        },
        "acceptance_path": [
            "ordinary payload shape validation passes",
            "strict referenced-file validation passes",
            "break-even rerun uses extracted energy, latency, noise, area, and the same sharing rule",
            "submission report is written only after the validator and rerun both pass",
        ],
        "refused_claim": "This package contract does not claim post-layout evidence exists, does not claim measured silicon exists, and does not upgrade analog energy or latency by itself. It only defines the packet a real result must provide.",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Converter Post-Layout Real Payload Package",
        "",
        f"- status: `{package['status']}`",
        f"- command: `{package['submission_command']}`",
        "",
        "This page names the actual handoff packet. A converter result is not enough as a sentence. It must arrive as a payload plus the files that let the result be inspected.",
        "",
        "## First Principle",
        "",
        "A converter claim is a claim about a boundary. On one side is the analog array, where current and voltage carry the multiply. On the other side is digital logic, where numbers are stored, routed, compared, and scheduled. The converter is the point where a physical voltage becomes a digital value. If that boundary is wrong, the analog array may look cheap only because the cost, delay, or noise of translation was hidden.",
        "",
        "So the package must expose the translation cost directly. The project needs the extracted netlist or measured setup, the model files, the energy terms, the latency terms, the noise terms, the area terms, and the sharing rule. Then it can rerun the break-even calculation instead of trusting an old planning number.",
        "",
        "## Required Files",
        "",
    ]
    for item in package["required_files"]:
        field = f" `{item['payload_field']}`" if "payload_field" in item else ""
        lines.append(f"- `{item['name']}`{field}: {item['reason']}")
    lines.extend(["", "## Required Numbers", ""])
    for key, reason in package["required_numeric_terms"].items():
        lines.append(f"- `{key}`: {reason}")
    lines.extend(["", "## Fixed Boundary", ""])
    for key, value in package["fixed_target_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Acceptance Path", ""])
    for step in package["acceptance_path"]:
        lines.append(f"- {step}")
    lines.extend(["", "## Refused Claim", "", package["refused_claim"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("converter_post_layout_real_payload_package")
    print(f"status,{package['status']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
