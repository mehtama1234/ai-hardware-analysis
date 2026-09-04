#!/usr/bin/env python3
"""Validate the contract for the continuous physical SAR proof rung."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-continuous-physical-sar-spec.json"


def main() -> int:
    data = json.loads(SPEC.read_text(encoding="utf-8"))
    required = data["acceptance_requirements"]
    terms = ("continuous transient", "preceding decision", "off during redistribution", "before comparator kickback", "ideal numerical DAC", "cycle-to-cycle state")
    if data.get("schema_version") != "sky130_continuous_physical_sar_spec.v1":
        raise SystemExit("unexpected schema version")
    if data.get("hardware_profile_id") != "educational-hybrid-tile-v1" or data.get("topology") != "pmos_only_to_vdd":
        raise SystemExit("continuous SAR spec is not bound to the selected hardware")
    if data.get("required_bits") != 4 or data.get("required_cycles_per_conversion") != 4 or data.get("required_representative_conversions") != 5:
        raise SystemExit("continuous SAR coverage contract is incomplete")
    if not all(any(term in item for item in required) for term in terms):
        raise SystemExit("continuous SAR phase and claim requirements are incomplete")
    print("PASS")
    print(f"spec_id {data['spec_id']}")
    print(f"cycles {data['required_cycles_per_conversion']}")
    print(f"conversions {data['required_representative_conversions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
