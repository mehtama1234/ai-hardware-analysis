#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CANDIDATE = EVIDENCE / "candidate-post-layout"
ENERGY = CANDIDATE / "measurements" / "readout-energy.json"
LATENCY = CANDIDATE / "measurements" / "readout-latency.json"
NOISE = CANDIDATE / "measurements" / "readout-noise.json"
AREA = CANDIDATE / "measurements" / "readout-area.json"
OUT_JSON = EVIDENCE / "first-real-converter-break-even-candidate.json"
OUT_MD = EVIDENCE / "first-real-converter-break-even-candidate.md"
RERUN_JSON = CANDIDATE / "rerun" / "aimc_readout_candidate_001_break_even_rerun.json"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def positive(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise SystemExit(f"{name} must be positive")
    return float(value)


def scenario(
    name: str,
    rows: int,
    columns: int,
    converter_energy_j: float,
    analog_mac_energy_j: float,
    digital_mac_energy_j: float,
    outputs_per_conversion: int,
) -> dict[str, Any]:
    analog_array_per_output = rows * analog_mac_energy_j
    digital_per_output = rows * digital_mac_energy_j
    converter_per_output = converter_energy_j / outputs_per_conversion
    target_total = analog_array_per_output + converter_per_output
    margin = digital_per_output - target_total
    saved_array_energy = rows * max(0.0, digital_mac_energy_j - analog_mac_energy_j)
    required_outputs = None if saved_array_energy <= 0 else converter_energy_j / saved_array_energy
    return {
        "name": name,
        "rows": rows,
        "columns": columns,
        "analog_mac_energy_j": analog_mac_energy_j,
        "digital_mac_energy_j": digital_mac_energy_j,
        "outputs_per_conversion_cost": outputs_per_conversion,
        "converter_energy_j": converter_energy_j,
        "converter_energy_per_output_j": converter_per_output,
        "analog_array_energy_per_output_j": analog_array_per_output,
        "digital_energy_per_output_j": digital_per_output,
        "target_analog_energy_per_output_j": target_total,
        "margin_vs_digital_per_output_j": margin,
        "target_beats_digital": margin > 0,
        "required_outputs_to_pay_converter": required_outputs,
    }


def build_report() -> dict[str, Any]:
    energy = load_json(ENERGY)
    latency = load_json(LATENCY)
    noise = load_json(NOISE)
    area = load_json(AREA)
    candidate_ids = {energy["candidate_id"], latency["candidate_id"], noise["candidate_id"], area["candidate_id"]}
    if candidate_ids != {"aimc_readout_candidate_001"}:
        raise SystemExit(f"candidate ids do not match: {candidate_ids}")
    adc_energy = positive(energy["adc_energy_per_conversion"], "adc_energy_per_conversion")
    dac_energy = positive(energy["dac_energy_per_row_drive"], "dac_energy_per_row_drive")
    converter_energy = adc_energy + dac_energy
    rows = 64
    columns = 4
    outputs_per_conversion = 16
    analog_mac_energy_j = 1.0e-15
    digital_mac_energy_j = 1.0e-14
    scenarios = [
        scenario("candidate_sharing_rule", rows, columns, converter_energy, analog_mac_energy_j, digital_mac_energy_j, outputs_per_conversion),
        scenario("no_sharing_same_rows", rows, columns, converter_energy, analog_mac_energy_j, digital_mac_energy_j, 1),
    ]
    replacement_decision = "candidate_would_replace_under_sharing_rule" if scenarios[0]["target_beats_digital"] else "candidate_keeps_digital_fallback"
    rerun = {
        "result_type": "first_real_converter_candidate_break_even_rerun",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "aimc_readout_candidate_001",
        "run_id": "aimc_readout_candidate_001_candidate_break_even_run001",
        "rerun_level": "candidate_values_mixed_evidence_levels_not_strict_extracted_rerun",
        "source_measurements": {
            "energy": rel(ENERGY),
            "latency": rel(LATENCY),
            "noise": rel(NOISE),
            "area": rel(AREA),
        },
        "input_terms": {
            "adc_energy_per_conversion_j": adc_energy,
            "dac_energy_per_row_drive_j": dac_energy,
            "combined_converter_energy_j": converter_energy,
            "conversion_time_ns": positive(latency["conversion_time_ns"], "conversion_time_ns"),
            "settling_time_ns": positive(latency["settling_time_ns"], "settling_time_ns"),
            "output_noise_rms": noise["output_noise_rms"],
            "input_referred_noise": noise["input_referred_noise"],
            "adc_area_um2": positive(area["adc_area_um2"], "adc_area_um2"),
            "dac_area_um2": positive(area["dac_area_um2"], "dac_area_um2"),
            "rows_served": rows,
            "columns_served": columns,
            "outputs_per_conversion_cost": outputs_per_conversion,
            "analog_mac_energy_j": analog_mac_energy_j,
            "digital_mac_energy_j": digital_mac_energy_j,
        },
        "scenarios": scenarios,
        "summary": {
            "default_scenario": "candidate_sharing_rule",
            "passing_scenarios": sum(1 for item in scenarios if item["target_beats_digital"]),
            "replacement_decision": replacement_decision,
            "claim_ready_to_replace_break_even": False,
        },
        "claim_boundary": {
            "allowed": "reruns break-even using the current named-candidate B2-B5 values",
            "not_allowed": "does not use strict extracted energy, latency, noise, and area; does not fill the strict payload; does not write accepted post-layout evidence",
        },
    }
    RERUN_JSON.parent.mkdir(parents=True, exist_ok=True)
    RERUN_JSON.write_text(json.dumps(rerun, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "result_type": "first_real_converter_break_even_candidate",
        "created_at": rerun["created_at"],
        "status": "b6_break_even_candidate_written_not_strict_replacement",
        "candidate_id": rerun["candidate_id"],
        "run_id": rerun["run_id"],
        "rerun_artifact": rel(RERUN_JSON),
        "combined_converter_energy_j": converter_energy,
        "default_target_beats_digital": scenarios[0]["target_beats_digital"],
        "default_margin_vs_digital_per_output_j": scenarios[0]["margin_vs_digital_per_output_j"],
        "replacement_decision": replacement_decision,
        "claim_ready_to_replace_break_even": False,
        "claim_boundary": rerun["claim_boundary"],
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Break-Even Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- rerun artifact: `{report['rerun_artifact']}`",
        f"- combined converter energy: `{report['combined_converter_energy_j']}` J",
        f"- default target beats digital: `{report['default_target_beats_digital']}`",
        f"- default margin vs digital per output: `{report['default_margin_vs_digital_per_output_j']}` J",
        f"- replacement decision: `{report['replacement_decision']}`",
        f"- claim ready to replace break-even: `{report['claim_ready_to_replace_break_even']}`",
        "",
        "## First Principle",
        "",
        "Break-even asks whether the analog path still saves enough work after paying for the converter. The array can be cheap and the converter can still erase the benefit. Sharing matters because one conversion cost can be paid by one output or spread across many useful outputs.",
        "",
        "This candidate rerun uses the same candidate object, energy, latency, noise, area, and sharing rule collected in B1 through B5. It is the first end-to-end economic loop for this named candidate, but it is not the final loop because those values are not strict extracted measurements from one accepted run.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_break_even_candidate")
    print(f"status,{report['status']}")
    print(f"rerun_artifact,{report['rerun_artifact']}")
    print(f"replacement_decision,{report['replacement_decision']}")
    print(f"claim_ready_to_replace_break_even,{report['claim_ready_to_replace_break_even']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
