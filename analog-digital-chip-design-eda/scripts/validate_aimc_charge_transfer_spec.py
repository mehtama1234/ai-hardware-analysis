#!/usr/bin/env python3
"""Validate the acceptance contract for the next physical charge-transfer cell."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-charge-transfer-redesign-spec.json"


def fail(message: str) -> int:
    print(f"FAIL {message}")
    return 1


def main() -> int:
    try:
        data = json.loads(SPEC.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read spec: {exc}")
    if data.get("schema_version") != "sky130_charge_transfer_redesign_spec.v1":
        return fail("unexpected schema version")
    if data.get("target_profile_id") != "educational-hybrid-tile-v1":
        return fail("spec is not bound to the frozen hardware profile")
    expected_phases = [
        "top_plate_initialization", "source_acquisition", "break_before_make_isolation",
        "bottom_plate_redistribution", "comparator_sample", "preamp_and_latch",
    ]
    if data.get("required_phases") != expected_phases:
        return fail("required phase order is incomplete or reordered")
    electrical = data.get("electrical_requirements", {})
    if electrical.get("supply_v") != 1.8 or electrical.get("top_plate_min_v") != 0.0 or electrical.get("top_plate_max_v") != 1.8:
        return fail("top-plate legal range is incorrect")
    if electrical.get("bits") != 4 or electrical.get("minimum_code_spacing_v") != 0.05625:
        return fail("4-bit spacing contract is incorrect")
    simulation = data.get("simulation_requirements", {})
    if simulation.get("all_code_count") != 16 or simulation.get("representative_sar_conversion_count") != 5:
        return fail("simulation coverage is incomplete")
    if simulation.get("mismatch_trials_required", 0) < 100 or len(simulation.get("pvt_corners_required", [])) < 5:
        return fail("PVT or mismatch coverage is incomplete")
    constraints = data.get("architecture_constraints", [])
    required_terms = ("VDD and ground", "disconnected", "off during DAC", "floating node", "same topology")
    if not all(any(term in constraint for constraint in constraints) for term in required_terms):
        return fail("architecture constraints do not cover rail, isolation, initialization, and topology identity")
    print("PASS")
    print(f"spec_id {data['spec_id']}")
    print(f"phases {len(data['required_phases'])}")
    print(f"pvt_corners {len(simulation['pvt_corners_required'])}")
    print(f"mismatch_trials {simulation['mismatch_trials_required']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
