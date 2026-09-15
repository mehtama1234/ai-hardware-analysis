#!/usr/bin/env python3
"""Join matched T4 workload evidence with guarded converter dispatch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--dispatch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evaluation = json.loads(args.evaluation.read_text())
    comparison = json.loads(args.comparison.read_text())
    dispatch = json.loads(args.dispatch.read_text())
    adc12 = next(row for row in comparison["variants"] if row["variant"] == "dac10_weight8_adc12")
    quality = next(row for row in evaluation["variants"] if row["id"] == "dac10_weight8_adc12")["quality"]
    result = {
        "schema_version": "t4-dispatch-decision-v0.1",
        "result_type": "matched_t4_workload_dispatch_decision",
        "model_revision": evaluation["model"]["revision"],
        "device": evaluation["runtime"]["device"],
        "quality": {"argmax_agreement": quality["teacher_forced_argmax_agreement"],
                    "generation_exact_matches": quality["generation_exact_match_count"],
                    "nll_increase_nats": quality["nll_increase_nats"]},
        "timing": {"median_cpu_ms": adc12["median_cpu_ms"],
                   "median_cuda_ms": adc12["median_cuda_ms"],
                   "cpu_to_cuda_speedup": adc12["cpu_to_cuda_speedup"]},
        "dispatch": {"routes": dispatch["routes"],
                     "analog_vectors_authorized": 0,
                     "mismatch_digital_correction_candidate": True},
        "decision": "retain_native_digital_gpu_execution_until_physical_converter_and_energy_data_close",
        "next_gate": "Run calibrated per-converter dispatch on held-out workload references, then replace numerical profile costs with matched converter/array/controller measurements.",
        "claim_boundary": "This decision joins matched numerical T4 execution with schematic converter routing. It does not claim analog hardware latency, energy, yield, or speedup.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "decision": result["decision"],
                      "median_cuda_ms": result["timing"]["median_cuda_ms"]}))


if __name__ == "__main__":
    main()
