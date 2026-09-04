#!/usr/bin/env python3
"""Generate a behavioral circuit-simulation estimate for the converter boundary."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sources" / "evidence" / "converter-circuit-evidence-schema.json"
CONTRACT = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-evidence-contract.json"
BREAK_EVEN = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-break-even.json"
LOCAL_ESTIMATE = ROOT / "evidence" / "aimc-simulator-adapters" / "local-converter-circuit-estimate.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-circuit-simulation-estimate.md"
OUT_CSV = (
    ROOT
    / "labs"
    / "analog"
    / "analog-in-memory-foundation-model-hardware"
    / "measurements"
    / "converter-circuit-simulation-estimate.csv"
)


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def missing_fields(schema: dict, payload: dict) -> list[str]:
    missing: list[str] = []
    for field in schema["required_top_level_fields"]:
        if field not in payload:
            missing.append(field)
    nested = {
        "target_boundary": "required_target_boundary_fields",
        "energy": "required_energy_fields",
        "latency": "required_latency_fields",
        "noise": "required_noise_fields",
        "area": "required_area_fields",
        "sharing": "required_sharing_fields",
    }
    for parent, schema_key in nested.items():
        value = payload.get(parent) if isinstance(payload.get(parent), dict) else {}
        for field in schema[schema_key]:
            if field not in value:
                missing.append(f"{parent}.{field}")
    return missing


def round_sig(value: float, digits: int = 6) -> float:
    return float(f"{value:.{digits}g}")


def main() -> None:
    schema = load_json(SCHEMA)
    contract = load_json(CONTRACT)
    break_even = load_json(BREAK_EVEN)
    local = load_json(LOCAL_ESTIMATE)
    target = break_even["target_boundary"]
    local_payload = local["estimate"]

    adc_bits = int(target["adc_bits"])
    dac_bits = int(target["dac_bits"])
    output_noise_budget = float(target["highest_all_pass_out_noise"])
    rows = int(local_payload["sharing"]["rows_served"])
    columns = int(local_payload["sharing"]["columns_served"])
    outputs_shared = int(local_payload["sharing"]["outputs_per_conversion_cost"])
    converter_instances = int(local_payload["sharing"]["converter_instances"])

    full_scale_v = 1.0
    adc_lsb = full_scale_v / (2**adc_bits)
    dac_lsb = full_scale_v / (2**dac_bits)
    adc_quant_rms = adc_lsb / math.sqrt(12.0)
    dac_quant_rms = dac_lsb / math.sqrt(12.0)

    tau_ns = 0.60
    settling_time_ns = 4.0
    settling_residual_fraction = math.exp(-settling_time_ns / tau_ns)
    settling_error_rms = settling_residual_fraction / math.sqrt(12.0)

    comparator_noise_rms = 0.00055
    row_driver_noise_rms = 0.00045
    output_noise_rms = math.sqrt(
        adc_quant_rms**2
        + dac_quant_rms**2
        + settling_error_rms**2
        + comparator_noise_rms**2
        + row_driver_noise_rms**2
    )
    input_referred_noise = math.sqrt(dac_quant_rms**2 + row_driver_noise_rms**2)
    meets_output_noise_budget = output_noise_rms <= output_noise_budget

    comparison_time_ns = 1.0
    conversion_time_ns = adc_bits * comparison_time_ns
    adc_unit_cap = 1.0
    dac_unit_cap = 0.035
    adc_energy = adc_unit_cap * (2**adc_bits)
    dac_energy = dac_unit_cap * (2**dac_bits) * rows / outputs_shared
    adc_area_um2 = 3.0 * (2**adc_bits)
    dac_area_um2 = 0.65 * (2**dac_bits) * columns

    payload = {
        "result_type": "converter_circuit_evidence",
        "converter_id": "behavioral-rc-sar12-dac10-circuit-simulation-estimate",
        "measurement_level": "circuit_simulation",
        "target_boundary": {
            "adc_bits": adc_bits,
            "dac_bits": dac_bits,
            "output_noise_budget": output_noise_budget,
        },
        "energy": {
            "adc_energy_per_conversion": round_sig(adc_energy),
            "dac_energy_per_row_drive": round_sig(dac_energy),
            "energy_unit": "relative_capacitance_switching_units",
            "method": "behavioral switched-capacitance estimate: ADC energy scales with 2^bits and DAC row-drive energy scales with 2^bits, active rows, and sharing",
        },
        "latency": {
            "adc_comparisons": adc_bits,
            "conversion_time_ns": round_sig(conversion_time_ns),
            "settling_time_ns": round_sig(settling_time_ns),
            "method": "one SAR comparison per ADC bit plus first-order RC row-drive settling before readout",
        },
        "noise": {
            "output_noise_rms": round_sig(output_noise_rms),
            "input_referred_noise": round_sig(input_referred_noise),
            "meets_output_noise_budget": meets_output_noise_budget,
            "method": "root-sum-square of ADC quantization, DAC quantization, RC settling residue, comparator noise, and row-driver noise",
        },
        "area": {
            "adc_area_um2": round_sig(adc_area_um2),
            "dac_area_um2": round_sig(dac_area_um2),
            "replication_or_sharing_rule": "four shared converter readout paths serve 64 rows and amortize one conversion cost over 16 output uses",
            "method": "behavioral capacitor-count proxy, not placed layout area",
        },
        "sharing": {
            "rows_served": rows,
            "columns_served": columns,
            "outputs_per_conversion_cost": outputs_shared,
            "converter_instances": converter_instances,
        },
        "provenance": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "schema": str(SCHEMA.relative_to(ROOT)),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "break_even": str(BREAK_EVEN.relative_to(ROOT)),
            "local_estimate": str(LOCAL_ESTIMATE.relative_to(ROOT)),
            "simulation_type": "deterministic_behavioral_rc_sar_model",
        },
        "claim_boundary": {
            "allowed": "narrows the converter target by checking settling, quantization, noise, latency, energy, area proxy, and sharing in one behavioral circuit model",
            "not_allowed": "does not replace break-even assumptions, post-layout parasitics, extracted area, measured converter energy, measured silicon noise, or board power",
        },
    }
    missing = missing_fields(schema, payload)
    claim_ready = (
        payload["measurement_level"] in {"post_layout_simulation", "measured_silicon"}
        and payload["noise"]["meets_output_noise_budget"] is True
        and not missing
    )
    output = {
        "result_type": "converter_circuit_simulation_estimate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "schema": str(SCHEMA.relative_to(ROOT)),
            "contract": str(CONTRACT.relative_to(ROOT)),
            "break_even": str(BREAK_EVEN.relative_to(ROOT)),
            "local_estimate": str(LOCAL_ESTIMATE.relative_to(ROOT)),
        },
        "simulation_terms": {
            "full_scale_v": full_scale_v,
            "adc_lsb": round_sig(adc_lsb),
            "dac_lsb": round_sig(dac_lsb),
            "adc_quantization_rms": round_sig(adc_quant_rms),
            "dac_quantization_rms": round_sig(dac_quant_rms),
            "tau_ns": tau_ns,
            "settling_residual_fraction": round_sig(settling_residual_fraction),
            "settling_error_rms": round_sig(settling_error_rms),
            "comparator_noise_rms": comparator_noise_rms,
            "row_driver_noise_rms": row_driver_noise_rms,
        },
        "estimate": payload,
        "validation": {
            "missing_required_fields": missing,
            "schema_complete": not missing,
            "claim_ready_to_replace_break_even": claim_ready,
            "status": "circuit_simulation_complete_not_replacement_ready",
        },
    }

    OUT_JSON.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.write_text(
        "\n".join(
            [
                "term,value",
                f"adc_bits,{adc_bits}",
                f"dac_bits,{dac_bits}",
                f"output_noise_budget,{output_noise_budget}",
                f"adc_lsb,{round_sig(adc_lsb)}",
                f"dac_lsb,{round_sig(dac_lsb)}",
                f"adc_quantization_rms,{round_sig(adc_quant_rms)}",
                f"dac_quantization_rms,{round_sig(dac_quant_rms)}",
                f"settling_residual_fraction,{round_sig(settling_residual_fraction)}",
                f"settling_error_rms,{round_sig(settling_error_rms)}",
                f"comparator_noise_rms,{comparator_noise_rms}",
                f"row_driver_noise_rms,{row_driver_noise_rms}",
                f"output_noise_rms,{round_sig(output_noise_rms)}",
                f"meets_output_noise_budget,{meets_output_noise_budget}",
                f"adc_energy_per_conversion,{round_sig(adc_energy)}",
                f"dac_energy_per_row_drive,{round_sig(dac_energy)}",
                f"conversion_time_ns,{round_sig(conversion_time_ns)}",
                f"settling_time_ns,{round_sig(settling_time_ns)}",
                f"adc_area_um2,{round_sig(adc_area_um2)}",
                f"dac_area_um2,{round_sig(dac_area_um2)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Converter Circuit-Simulation Estimate",
        "",
        "This file is the next proof layer after the local converter estimate. It does not pretend to be layout or silicon. It asks a narrower question: if the ADC is 12 bits and the row drive is 10 bits, do the simple circuit terms point in the same direction as the simulator target?",
        "",
        f"- status: `{output['validation']['status']}`",
        f"- claim-ready to replace break-even: `{claim_ready}`",
        f"- ADC bits: `{adc_bits}`",
        f"- DAC bits: `{dac_bits}`",
        f"- output noise budget: `{output_noise_budget}`",
        f"- modeled output noise RMS: `{round_sig(output_noise_rms)}`",
        f"- meets output noise budget: `{meets_output_noise_budget}`",
        f"- conversion time: `{round_sig(conversion_time_ns)}` ns",
        f"- settling time: `{round_sig(settling_time_ns)}` ns",
        f"- rows served: `{rows}`",
        f"- outputs sharing converter cost: `{outputs_shared}`",
        f"- measurement CSV: `{OUT_CSV.relative_to(ROOT)}`",
        "",
        "## First-Principles Reading",
        "",
        "An analog tile is useful only if a small voltage error stays small after it becomes a number. The converter is where that question becomes precise. The row driver chooses an input voltage. The array turns conductance and voltage into current. The readout circuit waits for that current or voltage to settle. The ADC turns the settled value into a code. Each step adds a bounded error.",
        "",
        "The model uses five error terms. Quantization error comes from the finite ADC step. Row-drive quantization comes from the finite DAC step. Settling error comes from the fact that a capacitor does not move instantly; after time `t`, a first-order residue is `exp(-t/tau)`. Comparator noise is the uncertainty in the ADC decision. Row-driver noise is the uncertainty in the voltage applied to the selected row.",
        "",
        "These errors are combined by root-sum-square because the model treats them as independent small errors. That is not a claim that real silicon will behave this cleanly. It is a clear test: if this clean model failed the `0.004` output-noise budget, the converter target would be too weak even before layout. Here the clean model passes the noise budget, so the target remains worth carrying into a stronger circuit run.",
        "",
        "## Cost Meaning",
        "",
        "The ADC cost grows with the number of decision levels. A 12-bit SAR ADC makes 12 timed comparisons. The DAC cost grows with the number of row-drive levels and the number of rows that must be driven. Sharing matters because one expensive conversion can serve several useful outputs. Without sharing, the converter eats the advantage of doing multiply-add work in the array.",
        "",
        "## Refused Claim",
        "",
        payload["claim_boundary"]["not_allowed"],
        "",
        "The schema rule is still binding: only `post_layout_simulation` or `measured_silicon` can replace the break-even assumptions. This behavioral circuit estimate narrows the target. It does not close the evidence loop.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("converter_circuit_simulation_estimate")
    print(f"status,{output['validation']['status']}")
    print(f"schema_complete,{output['validation']['schema_complete']}")
    print(f"claim_ready,{claim_ready}")
    print(f"meets_output_noise_budget,{meets_output_noise_budget}")
    print(f"output_noise_rms,{round_sig(output_noise_rms)}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{OUT_CSV}")


if __name__ == "__main__":
    main()
