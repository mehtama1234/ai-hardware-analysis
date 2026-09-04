#!/usr/bin/env python3
"""Generate the SPICE handoff spec for the converter evidence upgrade."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CIRCUIT_SIM = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
CONTRACT = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-spice-handoff-spec.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    circuit_sim = load_json(CIRCUIT_SIM)
    contract = load_json(CONTRACT)
    estimate = circuit_sim["estimate"]
    target = estimate["target_boundary"]
    noise = estimate["noise"]
    latency = estimate["latency"]
    sharing = estimate["sharing"]

    tests = [
        {
            "id": "S1",
            "name": "10-bit row DAC settling",
            "object": "row-driver DAC output node before the crossbar row input",
            "stimulus": "step through low, midscale, and near-full-scale codes with the selected row load attached",
            "measurement": "settled voltage error after the allowed settling window",
            "acceptance": "absolute settled error stays below half of one 10-bit DAC step and the row-driver noise term stays within the evidence budget",
        },
        {
            "id": "S2",
            "name": "12-bit SAR readout decision",
            "object": "ADC comparator, capacitor ladder or equivalent DAC, reference path, and sample node",
            "stimulus": "sweep input around every critical transition used by the selected output range",
            "measurement": "code transition error, comparator decision noise, conversion time, and failed-decision cases",
            "acceptance": "RMS readout error plus comparator noise stays below the budget carried by the behavioral estimate",
        },
        {
            "id": "S3",
            "name": "shared converter loading",
            "object": "four shared converter instances serving the 64-row, 4-column, 16-output sharing point",
            "stimulus": "toggle the muxed source, output load, and sample timing across the sharing schedule",
            "measurement": "extra settling error, added conversion latency, and loading-dependent noise",
            "acceptance": "sharing does not push total output noise above 0.004 and does not remove the break-even margin in the passing 64-row shared scenario",
        },
        {
            "id": "S4",
            "name": "energy accounting",
            "object": "row DAC references, ADC references, comparator, switch ladder, sampling capacitors, and mux control",
            "stimulus": "same conversion sequence used in the accuracy replay",
            "measurement": "integrated supply energy per row drive and per output conversion",
            "acceptance": "energy fields can replace the relative behavioral units with SPICE-derived numbers and a named voltage rail",
        },
    ]

    payload = {
        "result_type": "converter_spice_handoff_spec",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "converter_circuit_simulation_estimate": str(CIRCUIT_SIM.relative_to(ROOT)),
            "converter_circuit_evidence_contract": str(CONTRACT.relative_to(ROOT)),
        },
        "target": {
            "adc_bits": target["adc_bits"],
            "dac_bits": target["dac_bits"],
            "output_noise_budget": target["output_noise_budget"],
            "behavioral_output_noise_rms": noise["output_noise_rms"],
            "conversion_time_ns": latency["conversion_time_ns"],
            "settling_time_ns": latency["settling_time_ns"],
            "rows_served": sharing["rows_served"],
            "columns_served": sharing["columns_served"],
            "outputs_per_conversion_cost": sharing["outputs_per_conversion_cost"],
        },
        "required_testbenches": tests,
        "required_output_fields": [
            "measurement_level=circuit_simulation or post_layout_simulation",
            "adc_energy_per_conversion with units and rail voltage",
            "dac_energy_per_row_drive with units and row load",
            "conversion_time_ns from the timed decision path",
            "settling_time_ns from the row-drive and sample path",
            "output_noise_rms from transition, comparator, settling, and driver terms",
            "input_referred_noise for the row-drive boundary",
            "adc_area_um2 and dac_area_um2 if layout exists, otherwise explicit area proxy",
            "sharing rule that names rows, columns, instances, and outputs per conversion cost",
            "netlist path, model corner, simulator command, seed if noise is randomized, and date",
        ],
        "acceptance_rule": {
            "can_update_behavioral_target": True,
            "can_replace_break_even": False,
            "reason": "transistor-level SPICE can narrow the converter target, but the project schema still requires post-layout simulation or measured silicon before the break-even assumptions are replaced",
        },
        "claim_boundary": {
            "allowed": "defines the exact SPICE work needed to replace the behavioral converter terms with circuit-derived terms",
            "not_allowed": "does not claim a designed converter exists, does not claim extracted parasitics, does not claim measured silicon, and does not upgrade board energy",
        },
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter SPICE Handoff Spec",
        "",
        "This file says what the next converter proof must simulate. The current behavioral estimate is useful because it makes the math visible. It is still too clean. A SPICE handoff must turn each clean term into a circuit measurement.",
        "",
        f"- ADC target: `{target['adc_bits']}` bits",
        f"- DAC target: `{target['dac_bits']}` bits",
        f"- output noise budget: `{target['output_noise_budget']}`",
        f"- behavioral output noise RMS to beat or explain: `{noise['output_noise_rms']}`",
        f"- settling window: `{latency['settling_time_ns']}` ns",
        f"- conversion window: `{latency['conversion_time_ns']}` ns",
        f"- sharing point: `{sharing['rows_served']}` rows, `{sharing['columns_served']}` columns, `{sharing['outputs_per_conversion_cost']}` outputs per conversion cost",
        "",
        "## First-Principles Handoff",
        "",
        "The behavioral model says the converter target can fit under the noise budget if the row voltage settles, the quantization steps are fine enough, and comparator and driver noise stay small. SPICE must test those same nouns as circuit nodes and currents. A row DAC is no longer just `10 bits`; it is a reference ladder, switches, output resistance, capacitance, load, and settling time. A SAR ADC is no longer just `12 bits`; it is a sample node, comparator, reference movement, switching sequence, and timed decision chain.",
        "",
        "The important question is not whether the SPICE run produces a pretty waveform. The question is whether each waveform can replace one field in the converter evidence contract: energy, latency, output noise, input-referred noise, area or area proxy, and sharing rule.",
        "",
        "## Required Testbenches",
        "",
    ]
    for test in tests:
        lines.extend(
            [
                f"### {test['id']}. {test['name']}",
                "",
                f"- object: {test['object']}",
                f"- stimulus: {test['stimulus']}",
                f"- measurement: {test['measurement']}",
                f"- acceptance: {test['acceptance']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Required Output Fields",
            "",
            *[f"- {field}" for field in payload["required_output_fields"]],
            "",
            "## Claim Boundary",
            "",
            "Transistor-level SPICE can improve the behavioral converter model. It still cannot replace the break-even assumptions unless the evidence level becomes `post_layout_simulation` or `measured_silicon`.",
            "",
            f"Refused claim: {payload['claim_boundary']['not_allowed']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("converter_spice_handoff_spec")
    print(f"tests,{len(tests)}")
    print(f"can_replace_break_even,{payload['acceptance_rule']['can_replace_break_even']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
