#!/usr/bin/env python3
"""Audit the direct fixed-decision rail-control waveform before Colab.

The checker is intentionally a control contract, not a circuit pass: it
ensures that the direct complementary pass devices never request both rails at
once and that every gate waveform has finite, strictly increasing PWL time.
"""
from __future__ import annotations

import os
import re
import sys

from run_sky130_continuous_physical_sar import CONVERSION_CODES, fixed_gate_pwl


def parse_pwl(text: str) -> list[tuple[float, float]]:
    values = text.removeprefix("PWL(").removesuffix(")").split()
    return [(float(values[i][:-1]), float(values[i + 1])) for i in range(0, len(values), 2)]


def value_at(points: list[tuple[float, float]], time_ns: float) -> float:
    prior = points[0][1]
    for point_time, value in points:
        if point_time > time_ns:
            break
        prior = value
    return prior


def main() -> int:
    os.environ.setdefault("AIMC_CONTINUOUS_FIXED_DECISIONS", "1")
    gate_edge = float(os.environ.get("AIMC_CONTINUOUS_GATE_DEAD_TIME_NS", "0.5"))
    gp = parse_pwl(fixed_gate_pwl(0, "1.8", len(CONVERSION_CODES)))
    gn = parse_pwl(fixed_gate_pwl(0, "0", len(CONVERSION_CODES)))
    finite = all(a < b for (a, _), (b, _) in zip(gp, gp[1:])) and all(a < b for (a, _), (b, _) in zip(gn, gn[1:]))
    overlap = []
    for time in sorted({t for t, _ in gp} | {t for t, _ in gn}):
        p, n = value_at(gp, time + 1e-6), value_at(gn, time + 1e-6)
        if p < 1.7 and n > 0.1:
            overlap.append({"time_ns": time, "pmos_gate_v": p, "nmos_gate_v": n})
    report = {
        "result_type": "direct_gate_phase_contract",
        "status": "passed" if finite and not overlap else "rejected",
        "gate_dead_time_ns": gate_edge,
        "pwl_points": {"pmos": len(gp), "nmos": len(gn)},
        "finite_strict_pwl": finite,
        "simultaneous_rail_request": overlap,
        "claim_boundary": "Control waveform contract only; no transistor transient, PVT, mismatch, energy, or workload claim.",
    }
    print(report)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
