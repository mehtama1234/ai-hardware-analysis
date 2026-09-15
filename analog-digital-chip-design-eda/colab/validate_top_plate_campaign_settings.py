#!/usr/bin/env python3
"""Validate the checked-in top-plate Colab campaign contract.

This is a configuration gate only. It does not claim that ngspice ran or that
the analog converter passed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = {
    "AIMC_CONTINUOUS_FIXED_DECISIONS": "1",
    "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
    "AIMC_CONTINUOUS_STATE_CAPTURE_RAW": "1",
    "AIMC_CONTINUOUS_STATE_DAMPED_RESTORE": "1",
    "AIMC_CONTINUOUS_SEQUENTIAL_RAIL_HANDOFF": "1",
    "AIMC_CONTINUOUS_ISOLATED_PLATE_SWITCH": "1",
    "AIMC_CONTINUOUS_CAPACITIVE_COPY": "1",
    "AIMC_CONTINUOUS_CAPACITIVE_COPY_FF": "100",
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "sky130-top-plate-acquisition-settings-v0.1":
        errors.append("schema_version is not the top-plate v0.1 contract")
    env = {str(k): str(v) for k, v in data.get("env", {}).items()}
    for key, expected in REQUIRED.items():
        if env.get(key) != expected:
            errors.append(f"{key} must be {expected!r}, got {env.get(key)!r}")
    if data.get("required_cases") != ["fs", "ff"]:
        errors.append("required_cases must be ['fs', 'ff']")
    if data.get("required_conversion_codes") != [0, 2, 4, 6, 7]:
        errors.append("required_conversion_codes must remain [0, 2, 4, 6, 7]")
    if data.get("required_conversion_count") != 5:
        errors.append("required_conversion_count must be 5")
    if "no ... authorization" not in data.get("claim_boundary", ""):
        # Keep this intentionally permissive: the exact prose may evolve, but
        # the contract must retain an explicit diagnostic-only boundary.
        if "diagnostic" not in data.get("claim_boundary", "").lower():
            errors.append("claim_boundary must state that this is diagnostic evidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", nargs="?", default=str(Path(__file__).with_name("sky130-top-plate-acquisition-settings.json")))
    args = parser.parse_args()
    path = Path(args.settings)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}))
        return 2
    errors = validate(data)
    result = {"result_type": "sky130_top_plate_campaign_settings", "status": "ready" if not errors else "invalid", "settings": str(path), "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
