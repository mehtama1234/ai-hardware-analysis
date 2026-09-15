#!/usr/bin/env python3
"""Join independent workload-context receipts into a conservative qualification matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stateful_report", type=Path)
    parser.add_argument("third_holdout_report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stateful_path = args.stateful_report.resolve()
    third_path = args.third_holdout_report.resolve()
    stateful = json.loads(stateful_path.read_text(encoding="utf-8"))
    third = json.loads(third_path.read_text(encoding="utf-8"))
    contexts = [
        ("original_four_text", stateful["results"]["stateful_previous_token_original"], stateful_path),
        ("prior_six_text_stress", stateful["results"]["stateful_previous_token_stress"], stateful_path),
        ("third_six_text_holdout", third["results"]["stateful_previous_token_original"], third_path),
    ]
    rows = []
    for context, result, source_path in contexts:
        quality = result["quality"]
        rows.append({
            "context": context, "source": {"path": str(source_path), "sha256": digest(source_path)},
            "evaluation_cases": len(quality["rows"]),
            "predicted_tokens": quality["predicted_tokens"],
            "teacher_forced_argmax_agreement": quality["teacher_forced_argmax_agreement"],
            "nll_increase_nats": quality["nll_increase_nats"],
            "generation_exact_match_count": quality["generation_exact_match_count"],
            "screen_pass": quality["screen_pass"],
        })
    all_pass = all(row["screen_pass"] for row in rows)
    matrix = {
        "schema_version": "gpt2-multicontext-qualification-matrix-v0.1",
        "result_type": "local_conservative_multi_context_profile_qualification",
        "profile": {"weight_bits": 16, "dac_bits": 16, "adc_bits": 14,
                     "range_multiplier": 1.25, "transfer": "per-channel previous provisional output row"},
        "contexts": rows, "context_count": len(rows),
        "all_contexts_pass": all_pass,
        "decision": "candidate_profile_not_generalized_full_digital_fallback" if not all_pass else "candidate_profile_generalized_authorization_still_closed",
        "analog_authorized": False,
        "claim_boundary": "Local CPU multi-context matrix only; every context must pass before numerical promotion, and no hardware latency, energy, silicon yield, or analog authorization is claimed.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    matrix_path = args.output / "multicontext_matrix.json"
    matrix_path.write_text(json.dumps(matrix, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(matrix_path), "sha256": digest(matrix_path)},
        {"path": str(stateful_path), "sha256": digest(stateful_path)},
        {"path": str(third_path), "sha256": digest(third_path)},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(matrix_path), "contexts": len(rows), "all_contexts_pass": all_pass}, sort_keys=True))


if __name__ == "__main__":
    main()
