#!/usr/bin/env python3
"""Run a small SAR controller whose comparison primitive is the Sky130 transistor latch."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, build_deck, read_measure

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-comparator-sar-cycle.json"
OUT_MD = EVIDENCE / "sky130-transistor-comparator-sar-cycle.md"
TIMEOUT_S = 60
BITS = 4
# The comparator fixture is characterized around a 0.153 mV input difference.
FULL_SCALE_MV = 0.8
INPUT_CODES = (2, 8, 13)


def read_output_diff(stdout: str) -> float:
    return read_measure(stdout, "output_n_final_v") - read_measure(stdout, "output_p_final_v")


def compare(diff_mv: float) -> dict[str, Any]:
    deck = build_deck(Case(f"sar_trial_{diff_mv:+.6f}mV", diff_mv))
    with tempfile.TemporaryDirectory(prefix="aimc-sar-transistor-") as tmp:
        path = Path(tmp) / "comparison.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"input_diff_mv": diff_mv, "measured": False, "timed_out": True, "decision": None}
    if result.returncode != 0:
        return {"input_diff_mv": diff_mv, "measured": False, "timed_out": False, "returncode": result.returncode, "decision": None, "error_excerpt": (result.stdout + result.stderr)[-1000:]}
    output_diff = read_output_diff(result.stdout)
    # The fixture's raw contract is outn-outp: positive input -> negative output.
    decision = 1 if output_diff < 0.0 else 0
    return {"input_diff_mv": diff_mv, "measured": True, "timed_out": False, "returncode": result.returncode, "output_diff_v": output_diff, "decision": decision}


def sar_conversion(input_code: int) -> dict[str, Any]:
    denominator = (1 << BITS) - 1
    input_mv = input_code / denominator * FULL_SCALE_MV
    code = 0
    trace = []
    for decision_number, bit in enumerate(reversed(range(BITS)), start=1):
        trial_code = code | (1 << bit)
        trial_mv = trial_code / denominator * FULL_SCALE_MV
        signed_diff_mv = input_mv - trial_mv
        comparison = compare(signed_diff_mv)
        accepted = comparison.get("decision") == 1
        if accepted:
            code = trial_code
        trace.append({
            "decision_number": decision_number,
            "bit": bit,
            "input_code": input_code,
            "input_mv": input_mv,
            "trial_code": trial_code,
            "trial_mv": trial_mv,
            "signed_comparator_input_mv": signed_diff_mv,
            "accepted": accepted,
            "comparison": comparison,
        })
        if not comparison.get("measured"):
            break
    return {"input_code": input_code, "expected_code": input_code, "final_code": code, "comparison_count": len(trace), "all_comparisons_measured": len(trace) == BITS and all(row["comparison"].get("measured") for row in trace), "correct_code": code == input_code and len(trace) == BITS, "trace": trace}


def main() -> int:
    conversions = [sar_conversion(code) for code in INPUT_CODES]
    comparisons = [row["comparison"] for conversion in conversions for row in conversion["trace"]]
    measured = [row for row in comparisons if row.get("measured")]
    report = {
        "result_type": "sky130_transistor_comparator_sar_cycle",
        "status": "transistor_comparator_sar_cycle_passed_ideal_dac_only" if all(row["correct_code"] for row in conversions) else "transistor_comparator_sar_cycle_failed_or_incomplete",
        "bits": BITS,
        "full_scale_mv": FULL_SCALE_MV,
        "input_codes": list(INPUT_CODES),
        "conversion_count": len(conversions),
        "comparison_count": len(comparisons),
        "measured_comparison_count": len(measured),
        "timed_out_comparison_count": sum(row.get("timed_out", False) for row in comparisons),
        "correct_conversion_count": sum(row["correct_code"] for row in conversions),
        "accepted_for_converter": all(row["correct_code"] for row in conversions),
        "conversions": conversions,
        "claim_boundary": {
            "allowed": "uses the Sky130 transistor preamp/latch as the comparison primitive inside a sequential SAR controller",
            "not_allowed": "does not prove a capacitor-DAC network, DAC settling, capacitor mismatch, comparator noise yield, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor Comparator SAR Cycle", "",
        f"- status: `{report['status']}`",
        f"- bits: `{BITS}`",
        f"- conversions: `{report['conversion_count']}`",
        f"- comparator decisions: `{report['comparison_count']}`",
        f"- measured decisions: `{report['measured_comparison_count']}`",
        f"- timed-out decisions: `{report['timed_out_comparison_count']}`",
        f"- correct conversions: `{report['correct_conversion_count']}` of `{report['conversion_count']}`", "",
        "## What Is Real", "",
        "The controller performs a genuine most-significant-bit-first SAR update. For every trial code it computes the signed input difference, runs the transistor preamp/latch, reads the regenerated output, and uses that result to decide whether to retain the trial bit.", "",
        "The DAC reference in this first loop is an ideal numerical threshold. That keeps the experiment focused on the transistor comparator/controller boundary and prevents an ideal capacitor overlay from being mistaken for a physical DAC result.", "",
        "## Next Physical Gate", "",
        "Replace the numerical threshold with a switched capacitor-DAC network, measure its settling and reference loading, then repeat the exact same trace with mismatch and noise applied at each decision.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"comparison_count,{report['comparison_count']}")
    print(f"measured_comparison_count,{report['measured_comparison_count']}")
    print(f"correct_conversion_count,{report['correct_conversion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
