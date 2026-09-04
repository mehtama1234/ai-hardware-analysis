#!/usr/bin/env python3
"""Compare full-path normalized cost for digital, hybrid, and fallback execution."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKLOAD = ROOT / "evidence" / "aimc-hardware-lab" / "audio-workload-v1"
OUT = WORKLOAD / "wake-nonwake-end-to-end-cost-v1.json"


def main() -> None:
    # These are explicit relative planning units, not measured joules or milliseconds.
    digital = {
        "feature_extraction": {"latency": 4.0, "energy": 8.0},
        "dense1_matmul": {"latency": 16.0, "energy": 96.0},
        "digital_remainder": {"latency": 8.0, "energy": 48.0},
    }
    hybrid = {
        "feature_extraction": {"latency": 4.0, "energy": 8.0},
        "dac": {"latency": 4.0, "energy": 12.9},
        "analog_dense1_matmul": {"latency": 1.0, "energy": 8.0},
        "adc_and_partial_sum": {"latency": 24.0, "energy": 77.3},
        "digital_remainder": {"latency": 8.0, "energy": 48.0},
    }
    def total(parts: dict[str, dict[str, float]]) -> dict[str, float]:
        return {metric: sum(part[metric] for part in parts.values()) for metric in ["latency", "energy"]}
    digital_total = total(digital)
    hybrid_total = total(hybrid)
    report = {
        "schema_version": "aimc_end_to_end_cost.v1",
        "status": "normalized_planning_estimate",
        "workload_id": "wake-nonwake-audio-v1",
        "profile": {"adc_bits": 6, "dac_bits": 4, "converter_energy_relative": 3.222, "latency_comparisons": 24},
        "digital_baseline": {"parts": digital, "total": digital_total},
        "hybrid_analog_dense1": {"parts": hybrid, "total": hybrid_total},
        "comparison": {
            "latency_ratio_hybrid_to_digital": hybrid_total["latency"] / digital_total["latency"],
            "energy_ratio_hybrid_to_digital": hybrid_total["energy"] / digital_total["energy"],
            "decision": "digital_for_this_small_workload",
            "reason": "ADC comparisons and boundary overhead exceed the saved dense1 arithmetic at this workload size."
        },
        "fallback_rule": "If the governor rejects analog, use the digital baseline path without changing the task contract.",
        "claim_boundary": "Normalized planning estimate only; values are not measured latency, energy, board power, or silicon evidence."
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"digital_latency,{digital_total['latency']:.1f}")
    print(f"hybrid_latency,{hybrid_total['latency']:.1f}")
    print(f"latency_ratio,{report['comparison']['latency_ratio_hybrid_to_digital']:.3f}")
    print(f"energy_ratio,{report['comparison']['energy_ratio_hybrid_to_digital']:.3f}")
    print(f"decision,{report['comparison']['decision']}")


if __name__ == "__main__":
    main()
