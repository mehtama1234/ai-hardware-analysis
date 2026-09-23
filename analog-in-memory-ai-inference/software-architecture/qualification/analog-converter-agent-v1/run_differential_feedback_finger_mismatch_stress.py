#!/usr/bin/env python3
"""Stress the best finger-refinement candidate before workload transfer."""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run_differential_residue_correction_search import candidate

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = RESULTS / "differential-feedback-finger-mismatch-stress.json"
PROTOCOL = RESULTS / "differential-feedback-finger-mismatch-stress-preregistered-protocol.json"

WIDTHS = ("100u", "2.5u", "10u")
FINGERS = (32, 1, 2)
TRIALS = (
    ("nominal", ("1u", "6u", "80u"), "96u"),
    ("lsb_minus5", ("0.95u", "6u", "80u"), "96u"),
    ("lsb_plus5", ("1.05u", "6u", "80u"), "96u"),
    ("mid_minus5", ("1u", "5.7u", "80u"), "96u"),
    ("mid_plus5", ("1u", "6.3u", "80u"), "96u"),
    ("msb_minus5", ("1u", "6u", "76u"), "96u"),
    ("msb_plus5", ("1u", "6u", "84u"), "96u"),
    ("load_minus5", ("1u", "6u", "80u"), "91u"),
    ("load_plus5", ("1u", "6u", "80u"), "100u"),
)


def protocol() -> dict:
    return {
        "schema_version": "analog_converter_differential_feedback_finger_mismatch_stress_protocol.v1",
        "candidate": {"correction_width": list(WIDTHS), "finger_count": list(FINGERS),
                       "correction_topology": "matched_cascode_nmos", "cascode_bias_fraction": 1.0},
        "trials": [{"name": name, "base_widths": list(base), "load_width": load}
                   for name, base, load in TRIALS],
        "evaluation": {"corners": ["tt", "ss", "ff"], "codes": list(range(8)),
                        "settling_limit_v": 0.01, "strict_inl_gate_lsb": 0.5},
        "claim_boundary": "Bounded geometry/load stress proxy; not a foundry mismatch distribution, silicon yield, or hardware claim.",
    }


def evaluate(trial: tuple[str, tuple[str, ...], str]) -> dict:
    name, base, load = trial
    result = candidate(WIDTHS, FINGERS, base_widths=base, load=load,
                       correction_device="nmos", correction_topology="matched_cascode_nmos",
                       cascode_bias_fraction=1.0)
    return {"name": name, "base_widths": list(base), "load_width": load,
            "status": result["status"], "summary": result["summary"],
            "corners": result["corners"]}


def main() -> int:
    protocol_doc = protocol()
    PROTOCOL.write_text(json.dumps(protocol_doc, indent=2, sort_keys=True) + "\n")
    rows: list[dict | None] = [None] * len(TRIALS)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(evaluate, trial): index for index, trial in enumerate(TRIALS)}
        for future in as_completed(futures):
            index = futures[future]
            rows[index] = future.result()
            print(json.dumps({"trial": rows[index]["name"], "status": rows[index]["status"],
                              "max_inl_lsb": rows[index]["summary"]["max_inl_lsb"]}), flush=True)
    complete = [row for row in rows if row is not None]
    passing = [row for row in complete if row["status"] == "passed"
               and row["summary"]["all_monotonic"] and row["summary"]["all_settled"]]
    result = {
        "schema_version": "analog_converter_differential_feedback_finger_mismatch_stress.v1",
        "protocol": {"path": PROTOCOL.name, "sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()},
        "candidate": {"correction_width": list(WIDTHS), "finger_count": list(FINGERS)},
        "trials": complete,
        "summary": {"trials": len(complete), "passing": len(passing),
                    "all_electrical_pass": len(passing) == len(complete),
                    "worst_max_inl_lsb": max((row["summary"]["max_inl_lsb"] for row in passing), default=None),
                    "nominal_max_inl_lsb": next((row["summary"]["max_inl_lsb"] for row in complete if row["name"] == "nominal"), None),
                    "strict_inl_gate_lsb": 0.5,
                    "strict_gate_passed": bool(passing and all(row["summary"]["max_inl_lsb"] <= 0.5 for row in passing))},
        "status": "passed" if len(passing) == len(complete) == len(TRIALS) else "mixed",
        "claim_boundary": "Topology-matched bounded geometry/load stress proxy; not foundry mismatch statistics, Monte Carlo yield, extracted layout, silicon, board, or runtime promotion evidence.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
