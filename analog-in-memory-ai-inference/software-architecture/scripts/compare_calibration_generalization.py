#!/usr/bin/env python3
"""Compare affine calibration across two disjoint local GPT-2 fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--generalization", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    primary = json.loads(args.primary.read_text(encoding="utf-8"))
    generalization = json.loads(args.generalization.read_text(encoding="utf-8"))

    def summary(report):
        uncal = report["held_out"]["uncalibrated_quality"]
        cal = report["held_out"]["calibrated_quality"]
        return {
            "fixture": report["provenance"]["fixture"],
            "split_disjoint": report["provenance"]["split_disjoint"],
            "uncalibrated": {"nll_increase_nats": uncal["nll_increase_nats"],
                             "argmax_agreement": uncal["teacher_forced_argmax_agreement"],
                             "exact_generations": uncal["generation_exact_match_count"]},
            "affine_calibrated": {"nll_increase_nats": cal["nll_increase_nats"],
                                  "argmax_agreement": cal["teacher_forced_argmax_agreement"],
                                  "exact_generations": cal["generation_exact_match_count"]},
        }

    rows = {"primary": summary(primary), "generalization": summary(generalization)}
    primary_nll_delta = rows["primary"]["affine_calibrated"]["nll_increase_nats"] - rows["primary"]["uncalibrated"]["nll_increase_nats"]
    generalization_nll_delta = rows["generalization"]["affine_calibrated"]["nll_increase_nats"] - rows["generalization"]["uncalibrated"]["nll_increase_nats"]
    result = {
        "schema_version": "gpt2-calibration-generalization-comparison-v0.1",
        "result_type": "cross_split_affine_calibration_comparison",
        "sources": [{"path": str(path), "sha256": sha256(path)} for path in (args.primary, args.generalization)],
        "splits": rows,
        "deltas": {"primary_nll_change": primary_nll_delta,
                   "generalization_nll_change": generalization_nll_delta,
                   "generalization_argmax_change": rows["generalization"]["affine_calibrated"]["argmax_agreement"] - rows["generalization"]["uncalibrated"]["argmax_agreement"]},
        "decision": "mixed_calibration_generalization",
        "interpretation": "Affine calibration generalizes for held-out argmax agreement and exact generations, but NLL is not uniformly improved.",
        "analog_authorized": False,
        "claim_boundary": "Local software cross-split evidence only; no circuit calibration, hardware, energy, yield, or analog authorization claim.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision": result["decision"], "generalization_argmax_change": result["deltas"]["generalization_argmax_change"]}, sort_keys=True))


if __name__ == "__main__":
    main()
