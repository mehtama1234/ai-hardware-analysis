#!/usr/bin/env python3
"""Estimate converter cost for the AIHWKIT upgrade target."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-upgrade-target.json"
TILE = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "measurements" / "tile-operating-point.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-cost-model.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "aihwkit-converter-cost-model.md"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def converter_energy(adc_bits: int, dac_bits: int, columns: int, rows: int) -> float:
    adc = columns * (2 ** max(0, adc_bits - 4))
    dac = rows * 0.35 * (2 ** max(0, dac_bits - 4))
    return adc + dac


def estimate(adc_bits: int, dac_bits: int, columns: int, rows: int, base_energy: float) -> dict[str, float | int]:
    energy = converter_energy(adc_bits, dac_bits, columns, rows)
    return {
        "adc_bits": adc_bits,
        "dac_bits": dac_bits,
        "columns": columns,
        "rows": rows,
        "energy_relative_to_4x4": energy / base_energy,
        "latency_comparisons": columns * adc_bits,
        "adc_unit_terms": columns * (2 ** max(0, adc_bits - 4)),
        "dac_unit_terms": rows * 0.35 * (2 ** max(0, dac_bits - 4)),
    }


def main() -> None:
    target = load_json(TARGET)
    current = target.get("current_boundary") if isinstance(target.get("current_boundary"), dict) else {}
    minimum = target.get("minimum_passing_aihwkit_target") if isinstance(target.get("minimum_passing_aihwkit_target"), dict) else {}
    columns = 4
    rows = 4
    base_energy = converter_energy(4, 4, columns, rows)
    current_cost = estimate(int(current["adc_bits"]), int(current["dac_bits"]), columns, rows, base_energy)
    target_cost = estimate(int(minimum["effective_output_bits"]), int(minimum["effective_input_bits"]), columns, rows, base_energy)
    delta = {
        "energy_multiplier_vs_current": target_cost["energy_relative_to_4x4"] / current_cost["energy_relative_to_4x4"],
        "latency_comparison_multiplier_vs_current": target_cost["latency_comparisons"] / current_cost["latency_comparisons"],
        "extra_adc_comparisons_per_four_column_read": target_cost["latency_comparisons"] - current_cost["latency_comparisons"],
    }
    decision = {
        "status": "fallback_preferred_until_cost_is_justified",
        "reason": (
            "The target converter boundary is far more precise than the current tile. "
            "Under the local cost model, it costs much more converter energy and more SAR comparisons before any board-level benefit is proven."
        ),
    }
    body = {
        "result_type": "aihwkit_converter_cost_model",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": {
            "converter_upgrade_target": str(TARGET.relative_to(ROOT)),
            "tile_operating_point": str(TILE.relative_to(ROOT)),
        },
        "model_boundary": {
            "formula_source": "labs/analog/analog-in-memory-foundation-model-hardware/python/converter_boundary_sweep.py",
            "columns": columns,
            "rows": rows,
            "base": "4-bit ADC and 4-bit DAC converter energy is 1.0x",
            "allowed": "relative local design-cost comparison",
            "not_allowed": "not measured silicon energy, board energy, layout area, or production power",
        },
        "current_cost": current_cost,
        "target_cost": target_cost,
        "delta": delta,
        "decision": decision,
        "required_next_evidence": [
            "measured or circuit-level energy for the stronger ADC and DAC choice",
            "timing model showing whether the extra SAR comparisons fit prefill or decode latency",
            "macro area estimate for converter replication, sharing, or multiplexing",
            "AIHWKIT replay with a nonzero noise model that matches the proposed converter design",
            "scheduler policy showing when the high-precision analog path beats digital fallback",
        ],
    }
    OUT_JSON.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = [
        "# AIHWKIT Converter Cost Model",
        "",
        "This file prices the AIHWKIT converter target with the same relative cost formula used by the local converter sweep.",
        "",
        f"- status: `{decision['status']}`",
        f"- source target: `{body['source_artifacts']['converter_upgrade_target']}`",
        f"- formula source: `{body['model_boundary']['formula_source']}`",
        "",
        "## Current Tile Cost",
        "",
        f"- ADC bits: `{current_cost['adc_bits']}`",
        f"- DAC bits: `{current_cost['dac_bits']}`",
        f"- energy relative to 4x4 baseline: `{current_cost['energy_relative_to_4x4']:.3f}`",
        f"- SAR comparisons per four-column read: `{current_cost['latency_comparisons']}`",
        "",
        "## Target Cost",
        "",
        f"- ADC bits: `{target_cost['adc_bits']}`",
        f"- DAC bits: `{target_cost['dac_bits']}`",
        f"- energy relative to 4x4 baseline: `{target_cost['energy_relative_to_4x4']:.3f}`",
        f"- SAR comparisons per four-column read: `{target_cost['latency_comparisons']}`",
        "",
        "## Delta",
        "",
        f"- energy multiplier versus current tile: `{delta['energy_multiplier_vs_current']:.3f}`",
        f"- latency comparison multiplier versus current tile: `{delta['latency_comparison_multiplier_vs_current']:.3f}`",
        f"- extra ADC comparisons per four-column read: `{delta['extra_adc_comparisons_per_four_column_read']}`",
        "",
        "## First-Principles Reading",
        "",
        "The target fixes the numerical problem by asking the converters to make much finer decisions. That changes the hardware problem. A converter is not a label on a diagram; it is a timed circuit that spends switching, comparison, reference, routing, and calibration cost to turn an analog value into a code.",
        "",
        "The current tile uses a small converter boundary because analog compute only helps when the array work saved is larger than the converter work added. The 10-bit input and 12-bit output target may make AIHWKIT residuals pass, but under this local formula it makes converter energy far larger than the current operating point and adds more output comparison work.",
        "",
        "So the honest architecture rule is simple: until that cost is justified by measured or circuit-level evidence, the high-precision target is a design candidate, not an analog placement permission. Rows that need this much precision should stay on the digital path unless a later proof shows the higher-precision analog path wins for the same workload.",
        "",
        "## Required Next Evidence",
        "",
        *[f"- {item}" for item in body["required_next_evidence"]],
        "",
        "## Refused Claim",
        "",
        body["model_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print("aihwkit_converter_cost_model")
    print(f"status,{decision['status']}")
    print(f"current_energy_x,{current_cost['energy_relative_to_4x4']:.3f}")
    print(f"target_energy_x,{target_cost['energy_relative_to_4x4']:.3f}")
    print(f"energy_multiplier_vs_current,{delta['energy_multiplier_vs_current']:.3f}")
    print(f"latency_multiplier_vs_current,{delta['latency_comparison_multiplier_vs_current']:.3f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
