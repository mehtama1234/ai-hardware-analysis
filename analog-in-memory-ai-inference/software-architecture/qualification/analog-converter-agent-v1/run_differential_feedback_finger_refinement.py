#!/usr/bin/env python3
"""Bounded finger-count refinement around the best differential correction.

This is a new geometry family: widths and matched-cascode bias are frozen to
the current best width-refinement candidate, while only the three correction
finger counts vary. Every candidate is evaluated over all eight codes at
TT/SS/FF by the shared transistor-level candidate runner.
"""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run_differential_current_sum_search import SOURCE
from run_differential_residue_correction_search import candidate


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = RESULTS / "differential-feedback-finger-refinement-search.json"
CORRECTION_WIDTHS = ("100u", "2.5u", "10u")
BASE_WIDTHS = ("1u", "6u", "80u")
LOAD = "96u"
BIAS = 1.0
WORKERS = 4
FINGER_COUNTS = (
    (8, 1, 1), (16, 1, 1), (32, 1, 1),
    (8, 2, 1), (16, 2, 1), (32, 2, 1),
    (8, 1, 2), (16, 1, 2), (32, 1, 2),
)


def model_library_sha256() -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in SOURCE.rglob("*") if path.is_file())
    for path in files:
        digest.update(str(path.relative_to(SOURCE)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    rows: list[dict | None] = [None] * len(FINGER_COUNTS)

    def evaluate(fingers: tuple[int, int, int]) -> dict:
        return candidate(
            CORRECTION_WIDTHS,
            fingers,
            base_widths=BASE_WIDTHS,
            load=LOAD,
            correction_device="nmos",
            correction_topology="matched_cascode_nmos",
            cascode_bias_fraction=BIAS,
        )

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(evaluate, fingers): index
                   for index, fingers in enumerate(FINGER_COUNTS)}
        for future in as_completed(futures):
            index = futures[future]
            fingers = FINGER_COUNTS[index]
            row = future.result()
            row["finger_count"] = list(fingers)
            rows[index] = row
            print(json.dumps({
                "candidate": index + 1,
                "of": len(FINGER_COUNTS),
                "finger_count": list(fingers),
                "status": row["status"],
                "max_inl_lsb": row["summary"]["max_inl_lsb"],
            }), flush=True)

    complete = [row for row in rows if row is not None and row["status"] == "passed"]
    best = min(complete, key=lambda row: row["summary"]["max_inl_lsb"]) if complete else None
    prior = 0.7730308829277323
    result = {
        "schema_version": "analog_converter_differential_feedback_finger_refinement_search.v1",
        "search": {
            "correction_widths": list(CORRECTION_WIDTHS),
            "base_widths": list(BASE_WIDTHS),
            "load_width": LOAD,
            "cascode_bias_fraction": BIAS,
            "finger_count_population": [list(item) for item in FINGER_COUNTS],
            "candidate_count": len(rows),
            "workers": WORKERS,
        },
        "model_library_sha256": model_library_sha256(),
        "candidates": rows,
        "summary": {
            "candidate_count": len(rows),
            "passing_candidate_count": len(complete),
            "best_max_inl_lsb": best["summary"]["max_inl_lsb"] if best else None,
            "prior_best_max_inl_lsb": prior,
            "strict_improvement_over_prior": bool(best and best["summary"]["max_inl_lsb"] < prior),
            "promotion_gate_lsb": 0.5,
            "promotion_gate_passed": bool(best and best["summary"]["max_inl_lsb"] <= 0.5),
        },
        "status": "passed" if rows else "blocked",
        "claim_boundary": "TT/SS/FF extracted-MOS simulator geometry search only; no mismatch population, silicon, measured energy, or runtime promotion claim.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
