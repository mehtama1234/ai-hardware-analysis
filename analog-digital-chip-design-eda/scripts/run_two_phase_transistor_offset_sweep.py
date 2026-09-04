#!/usr/bin/env python3
"""Measure the two-phase transistor fixture's deterministic input threshold."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, PDK_LIB, build_deck, read_measure


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
DECK = LAB / "spice" / "sky130_two_phase_transistor_offset_sweep.sp"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-two-phase-transistor-offset-sweep.json"
OUT_MD = EVIDENCE / "sky130-two-phase-transistor-offset-sweep.md"
TIMEOUT_S = 70


def run_case(diff_mv: float) -> dict[str, Any]:
    deck = build_deck(Case(f"offset_{diff_mv:+.3f}mV", diff_mv))
    # Offset is a preamp property. Stop before the regenerative latch clock so
    # an exactly balanced input cannot become a metastable latch decision.
    deck = deck.replace(".tran 5p 3n", ".tran 20p 1.5n")
    deck = "\n".join(
        line
        for line in deck.splitlines()
        if not any(
            marker in line
            for marker in (
                "sampled_p_after_v",
                "sampled_n_after_v",
                "preamp_p_after_latch_v",
                "preamp_n_after_latch_v",
                "output_p_final_v",
                "output_n_final_v",
                "VCLK clk",
                "VCLKB clkb",
                "XLPRE1 ",
                "XLPRE2 ",
                "XLP ",
                "XLN ",
                "XRP ",
                "XRN ",
                "XINP ",
                "XINN ",
                "XTAIL ",
                "XEVAL ",
                "COUTP ",
                "COUTN ",
            )
        )
    ) + "\n"
    deck = deck.replace(
        ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25 v(outp)=1.8 v(outn)=1.8",
        ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25",
    )
    DECK.write_text(deck, encoding="utf-8")
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {"input_diff_mv": diff_mv, "measured": False, "timed_out": True}
    row: dict[str, Any] = {"input_diff_mv": diff_mv, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1400:]
        return row
    preamp = read_measure(result.stdout, "preamp_n_before_latch_v") - read_measure(result.stdout, "preamp_p_before_latch_v")
    row.update(
        {
            "preamp_diff_before_latch_v": preamp,
            "preamp_sign": 1 if preamp > 0 else -1 if preamp < 0 else 0,
            "expected_preamp_sign": 1 if diff_mv > 0 else -1 if diff_mv < 0 else 0,
            "preamp_sign_preserved": (preamp > 0) == (diff_mv > 0) if diff_mv else preamp == 0.0,
        }
    )
    return row


def estimate_crossing(rows: list[dict[str, Any]]) -> float | None:
    measured = sorted((row for row in rows if row.get("measured")), key=lambda row: row["input_diff_mv"])
    for left, right in zip(measured, measured[1:]):
        if float(left["preamp_diff_before_latch_v"]) <= 0.0 <= float(right["preamp_diff_before_latch_v"]):
            x0, x1 = float(left["input_diff_mv"]), float(right["input_diff_mv"])
            y0, y1 = float(left["preamp_diff_before_latch_v"]), float(right["preamp_diff_before_latch_v"])
            if y1 == y0:
                return (x0 + x1) / 2.0
            return x0 + (0.0 - y0) * (x1 - x0) / (y1 - y0)
    return None


def main() -> int:
    if not PDK_LIB.exists():
        raise SystemExit(f"missing Sky130 model library: {PDK_LIB}")
    # Five points are enough to bracket the zero crossing while keeping this
    # transistor-level sweep practical to rerun.
    diffs_mv = [-0.20, -0.10, 0.0, 0.10, 0.20]
    rows = [run_case(diff) for diff in diffs_mv]
    measured = [row for row in rows if row.get("measured")]
    crossing = estimate_crossing(rows)
    sign_pass = sum(row.get("preamp_sign_preserved") for row in measured if row["input_diff_mv"] != 0.0)
    report = {
        "result_type": "sky130_two_phase_transistor_offset_sweep",
        "status": "transistor_threshold_sweep_measured_not_noise_or_sar_proof",
        "generated_deck": str(DECK.relative_to(ROOT)),
        "measurement_boundary": "latch-free transient stopped at 1.5 ns; preamp measured at 1.45 ns",
        "transient_timestep_ps": 20.0,
        "input_differential_sweep_mv": diffs_mv,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row.get("timed_out", False) for row in rows),
        "estimated_preamp_zero_crossing_mv": crossing,
        "sign_pass_count": sign_pass,
        "nonzero_sign_case_count": sum(row["input_diff_mv"] != 0.0 for row in measured),
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures a deterministic transistor-level input threshold and polarity across the two-phase fixture sweep",
            "not_allowed": "does not measure random noise, mismatch distributions, process corners, SAR bit cycling, extracted layout, or accepted converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Two-Phase Transistor Offset Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- cases: `{report['case_count']}`",
        f"- measured cases: `{report['measured_case_count']}`",
        f"- timed-out cases: `{report['timed_out_case_count']}`",
        f"- estimated preamp zero crossing mV: `{crossing}`",
        f"- polarity sign passes: `{sign_pass}` of `{report['nonzero_sign_case_count']}`",
        f"- transient timestep ps: `{report['transient_timestep_ps']}`",
        f"- preamp sign passes: `{sign_pass}` of `{report['nonzero_sign_case_count']}`",
        "",
        "## First-Principles Reading",
        "",
        "A fixed offset shifts the input value at which the differential preamp changes sign. Sweeping the signed input and locating that zero crossing turns offset from an assumed number into a circuit-derived threshold. The sweep stops before latch regeneration so the balanced operating point can be measured directly.",
        "",
        "This is deterministic offset characterization. It does not include random device mismatch or thermal noise, so it cannot yet support a production 12-bit converter claim.",
        "",
        "## Next Gate",
        "",
        "Repeat the sweep over process, voltage, and temperature corners, add a transistor noise analysis around the same operating point, and combine the measured threshold distribution with the 12-bit SAR transition test.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_phase_transistor_offset_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"estimated_preamp_zero_crossing_mv,{crossing}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
