#!/usr/bin/env python3
"""Reclassify an interrupted DAC sweep without inventing missing measurements."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-switched-capacitor-dac.json"
OUT_MD = EVIDENCE / "sky130-transistor-switched-capacitor-dac.md"


def main() -> int:
    report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    rows = report.get("rows", [])
    measured = [row for row in rows if row.get("measured")]
    code_count = int(report.get("code_count", 16))
    half_lsb = float(report.get("half_lsb_v", 0.0))
    complete = len(measured) == code_count
    all_pass = complete and all(float(row["settling_error_v"]) <= half_lsb for row in measured)
    report["status"] = "transistor_switched_capacitor_dac_passed_boundary" if all_pass else "transistor_switched_capacitor_dac_incomplete_or_half_lsb_failed"
    report["measured_code_count"] = len(measured)
    report["all_codes_within_half_lsb"] = all_pass
    report["max_settling_error_v"] = max((float(row["settling_error_v"]) for row in measured), default=None)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor-Switched Capacitor DAC", "",
        f"- status: `{report['status']}`",
        f"- codes measured: `{len(measured)}` of `{code_count}`",
        f"- half-LSB target V: `{half_lsb:.9e}`",
        f"- maximum measured settling error V: `{report['max_settling_error_v']:.9e}`" if measured else "- maximum measured settling error V: not measured",
        f"- all codes within half-LSB: `{all_pass}`", "",
        "The latest bounded run did not measure every requested code. Missing codes remain missing; this page does not treat a passing measured subset as a complete DAC boundary.", "",
        "## Refused Claim", "",
        report.get("claim_boundary", {}).get("not_allowed", "does not prove a complete physical DAC or SAR"), "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_code_count,{len(measured)}/{code_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
