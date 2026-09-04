#!/usr/bin/env python3
"""Persist the existing prefill/decode serving-policy scenarios as evidence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
OUT = ROOT / "evidence" / "aimc-hardware-lab" / "transformer-serving-cost-v1.json"
sys.path.insert(0, str(PY_DIR))
from serving_policy import CostModel, ModelShape, TileShape, decide_phase  # noqa: E402


def main() -> None:
    shape = ModelShape()
    tile = TileShape(adc_bits=6, dac_bits=6)
    cost = CostModel()
    scenarios = [
        ("prefill", 2048, 1, 2048, False, 0.02),
        ("decode", 128, 1, 2048, False, 0.02),
        ("decode", 128, 1, 8192, False, 0.02),
        ("decode", 128, 8, 2048, False, 0.02),
        ("prefill", 2048, 1, 2048, True, 0.08),
    ]
    rows = [dict(decide_phase(phase, tokens, batch, context, calibration, health, shape, tile, cost)) for phase, tokens, batch, context, calibration, health in scenarios]
    report = {
        "schema_version": "aimc_transformer_serving_cost.v1",
        "status": "normalized_serving_policy_estimate",
        "model_shape": shape.__dict__,
        "tile": tile.__dict__,
        "cost_model": cost.__dict__,
        "scenarios": rows,
        "interpretation": "Analog is a candidate for repeated fixed projections when boundary cost, cache traffic, and estimated state error remain within budget. Prefill and batched decode can qualify; long-context single-request decode or stale calibration can require digital service.",
        "claim_boundary": "Relative planning estimate only; not measured latency, energy, board power, thermal behavior, or silicon evidence."
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(f"{row['phase']} batch={row['batch']} context={row['active_context']}: {row['decision']} ({row['reason']})")


if __name__ == "__main__":
    main()
