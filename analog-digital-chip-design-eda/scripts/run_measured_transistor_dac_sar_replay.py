#!/usr/bin/env python3
"""Replay SAR decisions against the measured physical DAC transfer curve."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-transistor-switched-capacitor-dac.json"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "measured-transistor-dac-sar-replay.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "measured-transistor-dac-sar-replay.md"
BITS = 4
VIN = 0.9
VDD = 1.8


def sar(input_v: float, thresholds: dict[int, float]) -> dict[str, Any]:
    code = 0
    trace = []
    for bit in reversed(range(BITS)):
        trial = code | (1 << bit)
        threshold = thresholds[trial]
        accepted = input_v >= threshold
        if accepted:
            code = trial
        trace.append({"bit": bit, "trial_code": trial, "threshold_v": threshold, "accepted": accepted})
    return {"final_code": code, "trace": trace}


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row.get("measured")]
    thresholds = {int(row["code"]): float(row["top_settled_v"]) for row in rows}
    missing = sorted(set(range(1 << BITS)) - set(thresholds))
    if missing:
        raise SystemExit(f"measured DAC transfer is incomplete; missing codes: {missing}")
    tests = []
    # Test each ideal quantization region. The top region uses the ideal code-15
    # level because the finite DAC cannot represent an input above full scale.
    for expected_code in range(1 << BITS):
        if expected_code < (1 << BITS) - 1:
            input_v = VIN + VDD * (expected_code + 0.5) / (1 << BITS)
        else:
            input_v = VIN + VDD * expected_code / (1 << BITS)
        result = sar(input_v, thresholds)
        tests.append({
            "expected_code": expected_code,
            "input_v": input_v,
            **result,
            "correct": result["final_code"] == expected_code,
        })
    report = {
        "result_type": "measured_transistor_dac_sar_replay",
        "status": "measured_dac_transfer_replay_characterized_not_closed_loop_spice_proof",
        "source_artifact": str(SOURCE.relative_to(ROOT)),
        "bits": BITS,
        "test_count": len(tests),
        "correct_count": sum(row["correct"] for row in tests),
        "wrong_count": sum(not row["correct"] for row in tests),
        "thresholds": thresholds,
        "tests": tests,
        "claim_boundary": {
            "allowed": "replays the SAR algorithm against all 16 measured nominal physical DAC thresholds",
            "not_allowed": "does not prove a same-deck comparator-DAC transient, comparator noise, mismatch yield, PVT SAR accuracy, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Measured Transistor DAC SAR Replay", "",
        f"- status: `{report['status']}`",
        f"- measured thresholds: `{len(thresholds)}` of `{1 << BITS}`",
        f"- correct quantization regions: `{report['correct_count']}` of `{report['test_count']}`",
        f"- wrong quantization regions: `{report['wrong_count']}`", "",
        "## What This Means", "",
        "This replay takes the measured 16-code top-plate transfer and puts it inside the digital SAR decision rule. It is deliberately separate from a transistor transient: the measured transfer is real, but the comparator is represented by an exact voltage comparison. That makes the source of any wrong code visible instead of hiding it behind a new idealized circuit.", "",
        "The input tests use the center of each ideal quantization region. A correct converter should return the region's expected code. A wrong result means the measured DAC threshold has moved far enough that the current transfer curve changes the digital answer even before comparator noise and mismatch are added.", "",
        "## Results", "",
        "| expected code | input V | replayed code | correct |", "| ---: | ---: | ---: | --- |",
    ]
    for row in tests:
        lines.append(f"| {row['expected_code']} | {row['input_v']:.6f} | {row['final_code']} | {row['correct']} |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"correct,{report['correct_count']}/{report['test_count']}")
    print(f"wrong,{report['wrong_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
