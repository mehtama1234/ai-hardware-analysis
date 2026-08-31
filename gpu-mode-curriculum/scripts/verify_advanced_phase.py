#!/usr/bin/env python3
"""Verify phase 2-7 advanced GPU AI systems coverage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "advanced-lab-phase" / "phase-2-7-plan.json"
PLAN_MD = ROOT / "advanced-lab-phase" / "PHASE-2-7-PLAN.md"
REQUIRED_LANES = {
    "speculative-decoding-serving",
    "multi-node-training-systems",
    "compiler-stack-deep-dive",
    "quantized-training-inference-kernels",
    "moe-end-to-end-systems",
    "jax-scaling-book-implementation",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    plan = load_json(PLAN)
    lanes = plan.get("lanes", [])
    lane_ids = {lane.get("id") for lane in lanes}
    require(plan.get("status") == "phase-plan-ready", "advanced phase plan is not ready")
    require(REQUIRED_LANES.issubset(lane_ids), f"missing advanced lanes: {sorted(REQUIRED_LANES - lane_ids)}")
    require(all(lane.get("status") != "planned" for lane in lanes), "advanced phase still contains planned-only lanes")
    for lane in lanes:
        evidence = lane.get("primary_evidence", [])
        require(evidence, f"{lane.get('id')} missing primary evidence")
        missing = [path for path in evidence if not (ROOT / path).exists()]
        require(not missing, f"{lane.get('id')} missing evidence paths: {missing}")
        require(lane.get("gpu_measurement_step"), f"{lane.get('id')} missing GPU measurement step")
    require(PLAN_MD.exists(), "advanced phase markdown plan missing")
    facts = {
        "status": plan["status"],
        "lanes": len(lanes),
        "implemented_first_class": sum(1 for lane in lanes if lane.get("status") == "implemented-first-class"),
        "implemented_existing": sum(1 for lane in lanes if lane.get("status") == "implemented-existing-lanes"),
        "implemented_project": sum(1 for lane in lanes if lane.get("status") == "implemented-project-lane"),
        "execution_target": plan.get("execution_target"),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE advanced phase 2-7 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
