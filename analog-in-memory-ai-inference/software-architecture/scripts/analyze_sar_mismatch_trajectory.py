#!/usr/bin/env python3
"""Compare continuous-SAR cycle trajectories for a nominal and mismatch case."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data.get("conversions", [])) != 5:
        raise ValueError(f"{path}: expected five conversions")
    return data


def analyze(nominal: dict[str, Any], mismatch: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for n, m in zip(nominal["conversions"], mismatch["conversions"]):
        dac_n = n.get("dac_threshold_before_comparator_v", [])
        dac_m = m.get("dac_threshold_before_comparator_v", [])
        pre_n = n.get("preamp_difference_v", [])
        pre_m = m.get("preamp_difference_v", [])
        rows.append({
            "conversion": n["conversion_number"],
            "expected_code": n["expected_code"],
            "nominal_code": n["final_code"],
            "mismatch_code": m["final_code"],
            "nominal_decisions": n.get("comparator_decision", []),
            "mismatch_decisions": m.get("comparator_decision", []),
            "dac_delta_v_by_cycle": [b - a for a, b in zip(dac_n, dac_m)],
            "preamp_delta_v_by_cycle": [b - a for a, b in zip(pre_n, pre_m)],
            "mismatch_dac_v": dac_m,
            "mismatch_preamp_v": pre_m,
        })
    deltas = [value for row in rows for value in row["dac_delta_v_by_cycle"]]
    pre_deltas = [value for row in rows for value in row["preamp_delta_v_by_cycle"]]
    return {
        "result_type": "continuous_sar_mismatch_trajectory_diagnosis",
        "nominal_status": nominal.get("status"),
        "mismatch_status": mismatch.get("status"),
        "rows": rows,
        "aggregate": {
            "max_abs_dac_delta_v": max((abs(v) for v in deltas), default=None),
            "max_abs_preamp_delta_v": max((abs(v) for v in pre_deltas), default=None),
            "mean_dac_delta_v": sum(deltas) / len(deltas) if deltas else None,
            "mean_preamp_delta_v": sum(pre_deltas) / len(pre_deltas) if pre_deltas else None,
            "first_decision_change_by_conversion": [
                next((i + 1 for i, (a, b) in enumerate(zip(row["nominal_decisions"], row["mismatch_decisions"])) if a != b), None)
                for row in rows
            ],
        },
        "claim_boundary": "Trajectory comparison of two schematic continuous-SAR transients; it localizes observed sensitivity but does not prove device mismatch statistics, layout behavior, or a circuit fix.",
        "next_experiment": "Use the earliest changed decision cycle to target that bit's charge-transfer path, then replay this exact seed before running another population.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nominal", type=Path, required=True)
    parser.add_argument("--mismatch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze(load(args.nominal), load(args.mismatch))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["aggregate"], sort_keys=True))
