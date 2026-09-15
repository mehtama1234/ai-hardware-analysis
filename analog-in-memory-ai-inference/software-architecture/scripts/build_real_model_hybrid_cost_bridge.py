#!/usr/bin/env python3
"""Join measured real-model serving denominators to the bounded hybrid cost model."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(
    characterization: dict[str, Any],
    cost_benchmark: dict[str, Any],
    physical_gate: dict[str, Any],
    extended: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = characterization.get("rows", [])
    gate_allowed = bool(physical_gate.get("analog_allowed_for_physical_claim", False))
    batch_rows = []
    for row in rows:
        cached = row["cached"]
        total_ms = float(cached["wall_time_ms_median"])
        batch_rows.append({
            "batch_size": row["batch_size"],
            "output_parity": bool(row["output_parity"]),
            "prefill_ms": float(cached["last_prefill_ms"]),
            "decode_ms": float(cached["last_decode_ms"]),
            "total_ms": total_ms,
            "tokens_per_second_per_batch": (row["generated_token_count"] * row["batch_size"]) / max(total_ms / 1000.0, 1e-12),
            "kv_peak_memory_mb": float(cached["peak_memory_mb_max"]),
            "cache_ratio_uncached_over_cached": float(row["cache_speedup_ratio_uncached_over_cached"]),
        })
    extended_denominator = None
    if extended:
        power = extended.get("protocol", {}).get("power", {})
        extended_denominator = {
            "context_sweep": extended.get("context_sweep", []),
            "tail_latency": extended.get("tail_latency"),
            "concurrency": extended.get("concurrency", []),
            "operator_data_movement_profile": extended.get("operator_data_movement_profile"),
            "power": power,
            "status": "measured_gpu; power scope is entire characterization protocol",
        }
    return {
        "schema_version": "real-model-hybrid-cost-bridge-v0.1",
        "model": characterization.get("model_profile", {}),
        "device": {"device": characterization.get("device"), "device_name": characterization.get("device_name")},
        "measured_gpu_denominator": {
            "protocol": characterization.get("protocol", {}),
            "batch_rows": batch_rows,
            "timing_scope": characterization.get("scope"),
            "correctness": {"all_output_parity": all(row["output_parity"] for row in rows)},
        },
        "measured_gpu_extended_denominator": extended_denominator,
        "modeled_hybrid_denominator": {
            "source_schema": cost_benchmark.get("schema_version"),
            "placement": cost_benchmark.get("placement"),
            "energy_model": cost_benchmark.get("energy_model"),
            "summary": cost_benchmark.get("summary"),
            "status": "modeled_only; not calibrated by the T4 timing report",
        },
        "placement_decision": {
            "decision": "digital_execution_with_analog_candidate_blocked",
            "analog_allowed_for_physical_claim": gate_allowed,
            "reason": "Measured GPU timing supplies a serving denominator, but it cannot authorize analog placement or infer energy. The physical converter gate and synchronized power evidence remain required.",
            "digital_regions": ["prefill", "decode", "dynamic_attention", "KV_cache", "batch_scheduler"],
            "analog_regions": [],
            "next_required_evidence": [
                "Extracted converter layout area and post-layout break-even rerun",
                "Per-tile calibrated analog error/throughput measurements",
                "Synchronized board power and thermal samples on the same workload",
            ],
        },
        "claim_boundary": {
            "allowed": "Use measured T4 phase, batch, parity, and KV-memory values as the serving denominator for subsequent bounded comparisons.",
            "refused": "Analog speedup, analog energy savings, silicon performance, or production readiness.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characterization", type=Path, required=True)
    parser.add_argument("--cost-benchmark", type=Path, required=True)
    parser.add_argument("--physical-gate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(
        json.loads(args.characterization.read_text(encoding="utf-8")),
        json.loads(args.cost_benchmark.read_text(encoding="utf-8")),
        json.loads(args.physical_gate.read_text(encoding="utf-8")),
    )
    result["sources"] = {
        "characterization": {"path": str(args.characterization), "sha256": sha256(args.characterization)},
        "cost_benchmark": {"path": str(args.cost_benchmark), "sha256": sha256(args.cost_benchmark)},
        "physical_gate": {"path": str(args.physical_gate), "sha256": sha256(args.physical_gate)},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "real_model_hybrid_cost_bridge.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "decision": result["placement_decision"]["decision"], "analog_allowed": result["placement_decision"]["analog_allowed_for_physical_claim"]}, indent=2))


if __name__ == "__main__":
    main()
