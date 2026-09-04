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
        {"name": "continuous_physical_sar_attempt_is_bounded", "pass": continuous.get("status") == "continuous_physical_sar_candidate_measured_not_accepted" and continuous.get("measured") is True and continuous.get("conversion_coverage_complete") is True and continuous.get("representative_conversions_measured") == continuous.get("required_representative_conversions") == 5 and continuous.get("all_conversions_correct") is False and continuous.get("bottom_plate_in_legal_range") is False},
    ]
    report = {
        "schema_version": "aimc_physical_evidence_gate.v1",
        "status": "blocked_physical_converter_evidence_is_consistent" if all(item["pass"] for item in checks) else "inconsistent_physical_evidence",
        "checks": checks,
        "physical_converter_gate": "blocked_sar_source_common_mode",
        "claim_boundary": "The measured evidence is internally consistent and preserves the distinction between bounded characterization and converter acceptance. It does not prove full-range physical SAR acceptance, PVT/mismatch/noise yield, extracted layout, board behavior, or silicon.",
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# AIMC Physical Evidence Gate", "", f"- status: `{report['status']}`", f"- converter gate: `{report['physical_converter_gate']}`", "", "| check | pass |", "| --- | --- |"]
    lines.extend(f"| `{item['name']}` | `{item['pass']}` |" for item in checks)
    lines.extend(["", "## Claim Boundary", "", report["claim_boundary"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"physical_evidence_status,{report['status']}")
    print(f"checks,{sum(item['pass'] for item in checks)}/{len(checks)}")
    return 0 if report["status"].startswith("blocked_physical") else 1


if __name__ == "__main__":
    raise SystemExit(main())
