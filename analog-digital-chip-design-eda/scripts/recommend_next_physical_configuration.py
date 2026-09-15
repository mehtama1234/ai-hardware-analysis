#!/usr/bin/env python3
"""Recommend a physical-flow candidate from the latest measured Pareto set."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_latest(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    rows = [item for item in rows if "variants" in item and "pareto_frontier" in item]
    if not rows:
        raise SystemExit("optimization history is empty")
    return rows[-1]


def normalized(value: float, values: list[float]) -> float:
    lo, hi = min(values), max(values)
    return 0.5 if hi == lo else (value - lo) / (hi - lo)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--area-weight", type=float, default=0.5)
    parser.add_argument("--runtime-weight", type=float, default=0.3)
    parser.add_argument("--timing-weight", type=float, default=0.2)
    args = parser.parse_args()
    weights = {
        "area": args.area_weight,
        "runtime": args.runtime_weight,
        "timing": args.timing_weight,
    }
    if any(value < 0 for value in weights.values()) or sum(weights.values()) <= 0:
        raise SystemExit("objective weights must be nonnegative and not all zero")
    total = sum(weights.values())
    weights = {key: value / total for key, value in weights.items()}

    record = load_latest(args.history)
    candidates = [
        item for item in record["variants"] if item["label"] in record["pareto_frontier"]
    ]
    if not candidates:
        raise SystemExit("latest optimization record has no Pareto candidates")
    areas = [item["die_area_mm2"] for item in candidates]
    runtimes = [item["runtime_seconds"] for item in candidates]
    timings = [item["spef_wns"] for item in candidates]
    scored = []
    for item in candidates:
        # Lower area/runtime is better; higher WNS is better.
        score = (
            weights["area"] * normalized(item["die_area_mm2"], areas)
            + weights["runtime"] * normalized(item["runtime_seconds"], runtimes)
            + weights["timing"] * (1.0 - normalized(item["spef_wns"], timings))
        )
        scored.append({"label": item["label"], "objective_score": round(score, 8)})
    recommendation = min(scored, key=lambda item: (item["objective_score"], item["label"]))
    result = {
        "schema_version": "physical-optimization-recommendation-v1",
        "source_record_hash": record["record_hash"],
        "weights": weights,
        "candidates": scored,
        "recommended_candidate": recommendation["label"],
        "decision": "human_review_required_before_next_run",
        "claim_boundary": "Deterministic recommendation from measured local Pareto candidates; it does not authorize execution or establish commercial signoff.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "passed", **{key: result[key] for key in ("recommended_candidate", "weights")}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
