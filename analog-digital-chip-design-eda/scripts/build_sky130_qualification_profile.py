#!/usr/bin/env python3
"""Export the current Sky130 converter evidence as a guarded workload profile."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-converter-qualification-profile.json"
SOURCES = {
    "continuous_nominal": "sky130-continuous-physical-sar.json",
    "continuous_mismatch": "sky130-continuous-physical-sar-mismatch-100.json",
    "coupled_pvt_calibrated": "sky130-coupled-physical-sar-pvt-calibrated.json",
    "coupled_margin": "sky130-coupled-pvt-margin-probe.json",
    "physical_gate": "../aimc-hardware-lab/physical-evidence-gate-latest.json",
}


def load(relative: str) -> dict:
    path = ROOT / "evidence" / "aimc-simulator-adapters" / relative
    if relative.startswith("../"):
        path = ROOT / "evidence" / relative[3:]
    return json.loads(path.read_text(encoding="utf-8"))


def source_record(relative: str) -> dict[str, str]:
    path = ROOT / "evidence" / "aimc-simulator-adapters" / relative
    if relative.startswith("../"):
        path = ROOT / "evidence" / relative[3:]
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def main() -> int:
    nominal = load(SOURCES["continuous_nominal"])
    mismatch = load(SOURCES["continuous_mismatch"])
    pvt = load(SOURCES["coupled_pvt_calibrated"])
    margin = load(SOURCES["coupled_margin"])
    physical_gate = load(SOURCES["physical_gate"])

    profile = {
        "schema_version": "aimc_circuit_derived_profile.v1",
        "profile_id": "sky130-continuous-sar-candidate-2026-09-11",
        "status": "bounded_nominal_profile_physical_qualification_open",
        "analog_authorized": False,
        "technology": {
            "process": "SkyWater 130 nm research target",
            "supply_nominal_v": 1.8,
            "source_v": nominal.get("source_v"),
            "topology": pvt.get("topology"),
        },
        "converter": {
            "bits": 4,
            "cycles_per_conversion": nominal.get("cycles_per_conversion"),
            "representative_conversions_measured": nominal.get("representative_conversions_measured"),
            "nominal_expected_code": nominal.get("expected_code"),
            "nominal_final_code": nominal.get("final_code"),
            "nominal_all_conversions_correct": nominal.get("all_conversions_correct"),
            "nominal_cycle_dac_in_legal_range": nominal.get("cycle_dac_in_legal_range"),
            "nominal_bottom_plate_in_legal_range": nominal.get("bottom_plate_in_legal_range"),
            "sample_point_ns": 9.0,
            "timing_status": "measured_nominal_only",
        },
        "robustness": {
            "pvt": {
                "measured_cases": pvt.get("measured_case_count"),
                "required_cases": 25,
                "correct_polarities": pvt.get("correct_polarity_count"),
                "timed_out_cases": pvt.get("timed_out_case_count"),
                "status": pvt.get("status"),
            },
            "mismatch": {
                "trials": mismatch.get("trial_count"),
                "measured_trials": mismatch.get("measured_trial_count"),
                "full_map_passes": mismatch.get("full_map_pass_count"),
                "legal_bottom_passes": mismatch.get("legal_bottom_pass_count"),
                "status": mismatch.get("status"),
            },
            "margin": {
                "measured_cases": margin.get("measured_case_count"),
                "correct_polarities": margin.get("correct_polarity_count"),
                "governor_conclusion": margin.get("governor_conclusion"),
            },
        },
        "workload_interface": {
            "transfer_error": "not_exported_from_accepted_full-range_converter",
            "conversion_latency_ns": "not accepted",
            "calibration_parameters": "corner-specific references exist; full calibration envelope open",
            "energy_scope": "not accepted",
            "unsupported_regions": ["source_common_mode_boundary", "low-margin PVT region", "post-layout converter"] ,
            "fallback": "digital_reference",
        },
        "qualification": {
            "physical_gate_status": physical_gate.get("status"),
            "required_before_authorization": [
                "exact full-range conversion map",
                "legal internal-node ranges",
                "continuous retained-state correctness",
                "declared PVT envelope",
                "statistical mismatch/noise evidence",
                "extracted/post-layout evidence",
            ],
        },
        "provenance": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sources": {name: source_record(path) for name, path in SOURCES.items()},
            "claim_boundary": "circuit-derived qualification profile; does not prove silicon, board runtime, measured power, or production readiness",
        },
    }
    OUT.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"profile,{profile['profile_id']}")
    print(f"status,{profile['status']}")
    print(f"analog_authorized,{profile['analog_authorized']}")
    print(f"pvt_cases,{pvt.get('measured_case_count')}/{profile['robustness']['pvt']['required_cases']}")
    print(f"mismatch_trials,{mismatch.get('measured_trial_count')}/{mismatch.get('trial_count')}")
    print(f"json,{OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
