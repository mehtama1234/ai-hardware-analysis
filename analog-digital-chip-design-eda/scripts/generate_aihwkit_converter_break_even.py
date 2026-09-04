#!/usr/bin/env python3
"""Compute the break-even boundary for the AIHWKIT converter target."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COST = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-cost-model.json"
NOISE = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-target-noise-sensitivity.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def saved_array_energy_per_output(rows: int, analog_mac_unit_energy: float, digital_mac_unit_energy: float) -> float:
    return rows * max(0.0, digital_mac_unit_energy - analog_mac_unit_energy)


def scenario(
    name: str,
    rows: int,
    columns: int,
    target_converter_energy: float,
    current_converter_energy: float,
    analog_mac_unit_energy: float,
    digital_mac_unit_energy: float,
    amortized_outputs_per_conversion: int,
) -> dict[str, object]:
    saving_per_output = saved_array_energy_per_output(rows, analog_mac_unit_energy, digital_mac_unit_energy)
    target_converter_per_output = target_converter_energy / float(amortized_outputs_per_conversion)
    current_converter_per_output = current_converter_energy / float(amortized_outputs_per_conversion)
    target_total = target_converter_per_output + rows * analog_mac_unit_energy
    current_total = current_converter_per_output + rows * analog_mac_unit_energy
    digital_total = rows * digital_mac_unit_energy
    margin = digital_total - target_total
    if saving_per_output <= 0:
        required_outputs = None
    else:
        required_outputs = target_converter_energy / saving_per_output
    return {
        "name": name,
        "rows": rows,
        "columns": columns,
        "analog_mac_unit_energy": analog_mac_unit_energy,
        "digital_mac_unit_energy": digital_mac_unit_energy,
        "amortized_outputs_per_conversion": amortized_outputs_per_conversion,
        "saved_array_energy_per_output": saving_per_output,
        "target_converter_energy_per_output": target_converter_per_output,
        "current_converter_energy_per_output": current_converter_per_output,
        "digital_energy_per_output": digital_total,
        "current_analog_energy_per_output": current_total,
        "target_analog_energy_per_output": target_total,
        "target_margin_vs_digital_per_output": margin,
        "target_beats_digital": margin > 0,
        "required_outputs_to_pay_target_converter": required_outputs,
    }


def main() -> None:
    cost = load_json(COST)
    noise = load_json(NOISE)
    target_cost = cost["target_cost"]
    current_cost = cost["current_cost"]
    noise_summary = noise["summary"]
    columns = int(target_cost["columns"])
    base_rows = int(target_cost["rows"])
    target_converter_energy = float(target_cost["energy_relative_to_4x4"])
    current_converter_energy = float(current_cost["energy_relative_to_4x4"])

    scenarios = [
        scenario(
            "four-row_fixture_no_sharing",
            base_rows,
            columns,
            target_converter_energy,
            current_converter_energy,
            analog_mac_unit_energy=0.10,
            digital_mac_unit_energy=1.00,
            amortized_outputs_per_conversion=1,
        ),
        scenario(
            "sixty_four_row_tile_no_sharing",
            64,
            columns,
            target_converter_energy,
            current_converter_energy,
            analog_mac_unit_energy=0.10,
            digital_mac_unit_energy=1.00,
            amortized_outputs_per_conversion=1,
        ),
        scenario(
            "sixty_four_row_tile_shared_over_16_outputs",
            64,
            columns,
            target_converter_energy,
            current_converter_energy,
            analog_mac_unit_energy=0.10,
            digital_mac_unit_energy=1.00,
            amortized_outputs_per_conversion=16,
        ),
        scenario(
            "two_fifty_six_row_tile_shared_over_64_outputs",
            256,
            columns,
            target_converter_energy,
            current_converter_energy,
            analog_mac_unit_energy=0.10,
            digital_mac_unit_energy=1.00,
            amortized_outputs_per_conversion=64,
        ),
    ]
    first_passing = next((item for item in scenarios if item["target_beats_digital"]), None)
    payload = {
        "result_type": "aihwkit_converter_break_even",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "converter_cost_model": str(COST.relative_to(ROOT)),
            "target_noise_sensitivity": str(NOISE.relative_to(ROOT)),
        },
        "model_boundary": {
            "allowed": "local break-even accounting for the target converter boundary",
            "not_allowed": "not measured converter energy, measured latency, layout area, silicon noise, or board power",
            "mac_energy_units": "dimensionless local units; digital MAC is normalized to 1.0 in each scenario",
        },
        "target_boundary": {
            "adc_bits": int(target_cost["adc_bits"]),
            "dac_bits": int(target_cost["dac_bits"]),
            "converter_energy_relative_to_4x4": target_converter_energy,
            "latency_comparisons": int(target_cost["latency_comparisons"]),
            "highest_all_pass_out_noise": noise_summary.get("highest_all_pass_out_noise"),
            "passes_any_nonzero_noise": bool(noise_summary.get("passes_any_nonzero_noise")),
        },
        "scenarios": scenarios,
        "summary": {
            "scenario_count": len(scenarios),
            "passing_scenarios": sum(1 for item in scenarios if item["target_beats_digital"]),
            "first_passing_scenario": first_passing["name"] if first_passing else None,
            "default_decision": "digital_fallback_until_real_converter_and_array_savings_are_measured",
        },
        "required_next_evidence": [
            "real ADC and DAC energy for the target precision",
            "number of rows and columns served per converter instance",
            "whether converters are per-column, shared, multiplexed, or reused across tokens",
            "analog array energy for the same matrix rows",
            "digital fallback energy and latency for the same rows",
            "noise source that explains why output noise stays at or below 0.004",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# AIHWKIT Converter Break-Even Boundary",
        "",
        "This file turns the converter target into a break-even question. The target can pass the replay only if the input and output codes are much finer. The hardware question is whether enough array work is being saved to pay for that finer conversion.",
        "",
        f"- target ADC bits: `{payload['target_boundary']['adc_bits']}`",
        f"- target DAC bits: `{payload['target_boundary']['dac_bits']}`",
        f"- target converter energy relative to 4x4 baseline: `{target_converter_energy:.3f}`",
        f"- highest all-pass output noise: `{payload['target_boundary']['highest_all_pass_out_noise']}`",
        f"- passing break-even scenarios: `{payload['summary']['passing_scenarios']}` of `{payload['summary']['scenario_count']}`",
        f"- default decision: `{payload['summary']['default_decision']}`",
        "",
        "## Scenario Table",
        "",
        "| scenario | rows | sharing | target analog/output | digital/output | margin | beats digital | outputs needed to pay converter |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for item in scenarios:
        required = item["required_outputs_to_pay_target_converter"]
        required_text = f"{required:.2f}" if isinstance(required, float) else "not possible"
        lines.append(
            f"| {item['name']} | {item['rows']} | {item['amortized_outputs_per_conversion']} | "
            f"{item['target_analog_energy_per_output']:.3f} | {item['digital_energy_per_output']:.3f} | "
            f"{item['target_margin_vs_digital_per_output']:.3f} | {item['target_beats_digital']} | {required_text} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "An analog array saves work only on multiplication and accumulation. The converter sits at the edge of that array. If the converter spends more energy than the array saves, the analog result is not useful even when the numerical residual is small.",
            "",
            "The break-even object is therefore not a single MatMul. It is a served volume: rows, columns, outputs, tokens, and how many outputs share one converter cost. A tiny four-row fixture cannot pay for a high-precision converter. A larger tile can begin to pay for it only if the converter is reused across enough useful outputs and if the analog MAC energy is truly lower than the digital fallback for the same rows.",
            "",
            "The current local scenarios say the target is still a candidate, not permission. It can become interesting when the rows are larger and the converter cost is shared. It still needs real circuit energy, real timing, area, and a noise source that keeps the output disturbance inside the 0.004 budget.",
            "",
            "## Required Next Evidence",
            "",
            *[f"- {item}" for item in payload["required_next_evidence"]],
            "",
            "## Refused Claim",
            "",
            payload["model_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("aihwkit_converter_break_even")
    print(f"scenario_count,{payload['summary']['scenario_count']}")
    print(f"passing_scenarios,{payload['summary']['passing_scenarios']}")
    print(f"first_passing_scenario,{payload['summary']['first_passing_scenario']}")
    print(f"default_decision,{payload['summary']['default_decision']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
