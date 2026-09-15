#!/usr/bin/env python3
"""Consolidate independently measured four-bit DAC timing probes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUTPUT = EVIDENCE / "local-fourbit-79ns-dummy1p-16code-diagnostic-matrix.json"

INPUTS = (
    "local-fourbit-79ns-20ps-dummy1p-batch0247.json",
    "local-fourbit-79ns-20ps-dummy1p-probes.json",
    "local-fourbit-79ns-20ps-dummy1p-batch35.json",
    "local-fourbit-79ns-20ps-dummy1p-batch69.json",
    "local-fourbit-79ns-50ps-dummy1p-batch1011.json",
    "local-fourbit-79ns-50ps-dummy1p-batch1214.json",
)


def main() -> int:
    rows = []
    sources = []
    for name in INPUTS:
        path = EVIDENCE / name
        data = json.loads(path.read_text(encoding="utf-8"))
        sources.append(name)
        rows.extend(data["rows"])
    rows.sort(key=lambda row: row["code"])
    codes = [row["code"] for row in rows]
    if codes != list(range(16)):
        raise SystemExit(f"expected one measured row for every code 0..15, got {codes}")
    if not all(row.get("measured") for row in rows):
        raise SystemExit("all consolidated rows must be measured")
    decision_times = {json.loads((EVIDENCE / name).read_text(encoding="utf-8"))["decision_time_ns"] for name in sources}
    steps = sorted({json.loads((EVIDENCE / name).read_text(encoding="utf-8"))["transient_step_ps"] for name in sources})
    half_lsb = 1.8 / 16.0 / 2.0
    report = {
        "result_type": "sky130_transistor_switched_capacitor_dac_16code_diagnostic_matrix",
        "status": "four_bit_16code_nominal_diagnostic_complete_not_acceptance",
        "bits": 4,
        "code_count": 16,
        "measured_code_count": 16,
        "requested_codes": codes,
        "decision_times_ns": sorted(decision_times),
        "transient_steps_ps": steps,
        "half_lsb_v": half_lsb,
        "max_settling_error_v": max(row["settling_error_v"] for row in rows),
        "all_codes_within_half_lsb": all(row["settling_error_v"] <= half_lsb for row in rows),
        "measured_code_order_monotonic": all(a["top_settled_v"] <= b["top_settled_v"] for a, b in zip(rows, rows[1:])),
        "sources": sources,
        "rows": rows,
        "claim_boundary": "Complete nominal 16-code transistor-array diagnostic at an extended 7.9 ns measurement point, using 20/50 ps diagnostic steps; not same-resolution acceptance, PVT, mismatch, comparator, SAR, energy, layout, board, or silicon proof.",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_code_count,{report['measured_code_count']}")
    print(f"max_settling_error_v,{report['max_settling_error_v']}")
    print(f"all_codes_within_half_lsb,{report['all_codes_within_half_lsb']}")
    print(f"measured_code_order_monotonic,{report['measured_code_order_monotonic']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
