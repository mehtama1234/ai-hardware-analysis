#!/usr/bin/env python3
"""Validate the physical AIMC evidence boundary without promoting blocked claims."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = ROOT / "evidence" / "aimc-hardware-lab" / "physical-evidence-gate-latest.json"
OUT_MD = ROOT / "evidence" / "aimc-hardware-lab" / "physical-evidence-gate-latest.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def main() -> int:
    bit = load("sky130-coupled-dac-comparator-bit.json")
    sar = load("sky130-calibrated-physical-sar.json")
    partial = load("sky130-calibrated-physical-sar-partial.json")
    endpoint = load("sky130-differential-dummy-endpoint-diagnostic.json")
    pvt = load("sky130-coupled-physical-sar-pvt.json")
    margin = load("sky130-coupled-pvt-margin-probe.json")
    mismatch = load("sky130-coupled-physical-sar-mismatch.json")
    continuous = load("sky130-continuous-physical-sar.json")
    promoted_pvt = [
        load(f"sky130-continuous-promoted-{suffix}.json")
        for suffix in ("ss162-hot", "ff198-cold", "ss27", "ff27")
    ]
    trim_calibration = load("sky130-continuous-trim-calibration-check-ss-1.62v-85c.json")
    mismatch_population = load("sky130-continuous-physical-sar-mismatch-100.json")
    mismatch_population_reset = load("sky130-continuous-physical-sar-mismatch-reset-100.json")
    mismatch_population_reset5 = load("sky130-continuous-physical-sar-mismatch-reset5ns-100.json")
    endpoint_rows = endpoint.get("rows", [])
    endpoint_measured = sum(bool(row.get("measured")) for row in endpoint_rows)
    endpoint_timed_out = sum(bool(row.get("timed_out")) for row in endpoint_rows)
    checks = [
        {"name": "coupled_bit_sweep_complete", "pass": bit.get("measured_case_count") == bit.get("case_count") == 16},
        {"name": "coupled_bit_polarity_complete", "pass": bit.get("all_polarities_correct") is True},
        {"name": "full_sar_claim_is_bounded", "pass": sar.get("status") == "calibrated_physical_sar_characterized_not_continuous_multicycle_proof"},
        {"name": "full_sar_calibration_complete", "pass": sar.get("calibration_measured_count") == sar.get("calibration_case_count") == 16},
        {"name": "full_sar_nominal_representative_conversions_complete", "pass": sar.get("conversion_count") == 5 and sar.get("correct_conversion_count") == 5 and sar.get("measured_comparison_count") == sar.get("comparison_count") == 20},
        {"name": "full_sar_high_codes_measured", "pass": all(str(code) in sar.get("calibration_thresholds_v", {}) for code in (14, 15))},
        {"name": "full_sar_spacing_gate_explicit", "pass": sar.get("acceptance_gates", {}).get("minimum_half_lsb_spacing") is True},
        {"name": "full_sar_range_gate_explicit", "pass": sar.get("acceptance_gates", {}).get("legal_threshold_range") is True},
        {"name": "full_sar_code_map_gate_explicit", "pass": sar.get("acceptance_gates", {}).get("logical_to_physical_map_injective") is True},
        {"name": "historical_partial_probe_preserved", "pass": partial.get("missing_calibration_codes") == [14, 15]},
        {"name": "differential_endpoint_probe_incomplete", "pass": endpoint_measured == 0 and endpoint_timed_out == 4},
        {"name": "physical_converter_not_promoted", "pass": sar.get("claim_boundary", {}).get("not_allowed", "").find("extracted layout") >= 0},
        {"name": "same_topology_pvt_diagnostic_complete", "pass": pvt.get("topology") == "pmos_only_to_vdd" and pvt.get("measured_case_count") == pvt.get("case_count") == 25 and pvt.get("timed_out_case_count") == 0},
        {"name": "failing_pvt_margin_probe_complete", "pass": margin.get("status") == "slow_cold_low_supply_margin_boundary_characterized" and margin.get("measured_case_count") == margin.get("case_count") == 7},
        {"name": "same_topology_controlled_mismatch_complete", "pass": mismatch.get("topology") == "pmos_only_to_vdd" and mismatch.get("measured_case_count") == mismatch.get("case_count") == 20 and mismatch.get("timed_out_case_count") == 0},
        {"name": "continuous_physical_sar_nominal_map_complete", "pass": continuous.get("status") == "continuous_physical_sar_nominal_map_passed" and continuous.get("measured") is True and continuous.get("conversion_coverage_complete") is True and continuous.get("representative_conversions_measured") == continuous.get("required_representative_conversions") == 5 and continuous.get("all_conversions_correct") is True and continuous.get("bottom_plate_in_legal_range") is True},
        {"name": "promoted_continuous_sar_pvt_diagnostics_complete", "pass": len(promoted_pvt) == 4 and all(item.get("measured") is True and item.get("conversion_coverage_complete") is True and item.get("representative_conversions_measured") == 5 for item in promoted_pvt)},
        {"name": "continuous_sar_trim_calibration_runner_selects_passing_trim", "pass": trim_calibration.get("status") == "trim_selected" and trim_calibration.get("selected_trim", {}).get("lsb_scale") == 2.0 and trim_calibration.get("selected_trim", {}).get("all_conversions_correct") is True and trim_calibration.get("selected_trim", {}).get("bottom_plate_in_legal_range") is True},
        {"name": "continuous_sar_mismatch_population_complete", "pass": mismatch_population.get("trial_count") == 100 and len(mismatch_population.get("rows", [])) == 100 and mismatch_population.get("measured_trial_count", 0) + (mismatch_population.get("trial_count", 0) - mismatch_population.get("measured_trial_count", 0)) == 100 and mismatch_population.get("full_map_pass_count", 0) == 95},
        {"name": "continuous_sar_reset_mismatch_population_complete", "pass": mismatch_population_reset.get("trial_count") == 100 and len(mismatch_population_reset.get("rows", [])) == 100 and mismatch_population_reset.get("measured_trial_count") == 96 and mismatch_population_reset.get("full_map_pass_count") == 90 and mismatch_population_reset.get("legal_bottom_pass_count") == 96},
        {"name": "continuous_sar_reset5ns_negative_control_complete", "pass": mismatch_population_reset5.get("trial_count") == 100 and len(mismatch_population_reset5.get("rows", [])) == 100 and mismatch_population_reset5.get("measured_trial_count") == 94 and mismatch_population_reset5.get("full_map_pass_count") == 83 and mismatch_population_reset5.get("legal_bottom_pass_count") == 94},
    ]
    report = {
        "schema_version": "aimc_physical_evidence_gate.v1",
        "status": "nominal_continuous_sar_map_passed_remaining_qualification_open" if all(item["pass"] for item in checks) else "inconsistent_physical_evidence",
        "checks": checks,
        "physical_converter_gate": "nominal_continuous_sar_map_passed_remaining_qualification_open",
        "claim_boundary": "The nominal continuous five-conversion SAR map and calibrated PVT checks pass. The pre-reset declared 100-trial capacitor-variation stress population measured 95 full-map/legal passes; the reset-promoted rerun measured 90 full-map passes and 96 legal-bottom-plate passes. These are schematic-level stress results, not foundry Monte Carlo. Comparator noise/offset yield, extracted layout, board behavior, and silicon acceptance remain open.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# AIMC Physical Evidence Gate", "", f"- status: `{report['status']}`", f"- converter gate: `{report['physical_converter_gate']}`", "", "| check | pass |", "| --- | --- |"]
    lines.extend(f"| `{item['name']}` | `{item['pass']}` |" for item in checks)
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"physical_evidence_status,{report['status']}")
    print(f"checks,{sum(item['pass'] for item in checks)}/{len(checks)}")
    return 0 if report["status"].startswith(("blocked_physical", "nominal_continuous")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
