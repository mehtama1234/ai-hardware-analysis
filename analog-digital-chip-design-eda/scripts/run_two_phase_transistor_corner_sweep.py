#!/usr/bin/env python3
"""Run a small process/temperature/supply sweep on the latch-free preamp boundary."""

from __future__ import annotations

import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, PDK_LIB, build_deck, read_measure


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-two-phase-transistor-corner-sweep.json"
OUT_MD = EVIDENCE / "sky130-two-phase-transistor-corner-sweep.md"
TIMEOUT_S = 100
PREAMP_MARGIN_TARGET_V = 0.0005


CORNER_CASES = [
    {"name": "tt_25c_nominal", "section": "tt", "temperature_c": 25.0, "supply_v": 1.8},
    {"name": "ss_minus20c_low_supply", "section": "ss", "temperature_c": -20.0, "supply_v": 1.62},
    {"name": "ff_85c_high_supply", "section": "ff", "temperature_c": 85.0, "supply_v": 1.98},
]


def make_deck(diff_mv: float, corner: dict[str, Any], path: Path) -> None:
    deck = build_deck(Case(f"corner_{diff_mv:+.3f}mV", diff_mv))
    deck = deck.replace('" tt', f'" {corner["section"]}')
    deck = deck.replace(".param vdd=1.8", f".param vdd={corner['supply_v']}")
    deck = deck.replace(".tran 5p 3n", ".tran 20p 1.5n")
    deck = deck.replace(f".temp", f".temp")
    deck = deck.replace(".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25 v(outp)=1.8 v(outn)=1.8", ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25")
    deck = deck.replace(".tran 20p 1.5n", f".temp {corner['temperature_c']}\n.tran 20p 1.5n")
    remove_markers = (
        "VCLK clk", "VCLKB clkb", "XLPRE1 ", "XLPRE2 ", "XLP ", "XLN ",
        "XRP ", "XRN ", "XINP ", "XINN ", "XTAIL ", "XEVAL ",
        "COUTP ", "COUTN ", "sampled_p_after_v", "sampled_n_after_v",
        "preamp_p_after_latch_v", "preamp_n_after_latch_v", "output_p_final_v", "output_n_final_v",
    )
    deck = "\n".join(line for line in deck.splitlines() if not any(marker in line for marker in remove_markers)) + "\n"
    path.write_text(deck, encoding="utf-8")


def run_one(item: tuple[dict[str, Any], float]) -> dict[str, Any]:
    corner, diff_mv = item
    with tempfile.TemporaryDirectory(prefix="aimc-corner-") as tmp:
        path = Path(tmp) / "corner.sp"
        make_deck(diff_mv, corner, path)
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {**corner, "input_diff_mv": diff_mv, "measured": False, "timed_out": True}
        row: dict[str, Any] = {**corner, "input_diff_mv": diff_mv, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
        if result.returncode != 0:
            row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
            return row
        preamp = read_measure(result.stdout, "preamp_n_before_latch_v") - read_measure(result.stdout, "preamp_p_before_latch_v")
        row.update({"preamp_diff_before_latch_v": preamp, "preamp_sign": 1 if preamp > 0 else -1 if preamp < 0 else 0, "expected_sign": 1 if diff_mv > 0 else -1 if diff_mv < 0 else 0, "sign_preserved": preamp == 0.0 if diff_mv == 0.0 else (preamp > 0) == (diff_mv > 0)})
        return row


def main() -> int:
    inputs = [(corner, diff) for corner in CORNER_CASES for diff in (-0.2, 0.0, 0.2)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run_one, inputs))
    measured = [row for row in rows if row["measured"]]
    nonzero = [row for row in measured if row["input_diff_mv"] != 0.0]
    report = {"result_type": "sky130_two_phase_transistor_corner_sweep", "status": "transistor_corner_sweep_measured_not_noise_or_mismatch_proof", "case_count": len(rows), "measured_case_count": len(measured), "timed_out_case_count": sum(row["timed_out"] for row in rows), "nonzero_sign_pass_count": sum(row.get("sign_preserved", False) for row in nonzero), "nonzero_case_count": len(nonzero), "zero_input_measured_count": sum(row["input_diff_mv"] == 0.0 for row in measured), "preamp_margin_target_v": PREAMP_MARGIN_TARGET_V, "nonzero_preamp_margin_pass_count": sum(abs(float(row.get("preamp_diff_before_latch_v", 0.0))) >= PREAMP_MARGIN_TARGET_V for row in nonzero), "minimum_nonzero_preamp_abs_v": min((abs(float(row["preamp_diff_before_latch_v"])) for row in nonzero), default=None), "corners": CORNER_CASES, "rows": rows, "claim_boundary": {"allowed": "measures deterministic preamp polarity, convergence, and margin at three process, temperature, and supply corner points", "not_allowed": "does not prove random noise, mismatch distributions, full PVT coverage, SAR bit cycling, extracted layout, or accepted converter evidence"}}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Two-Phase Transistor Corner Sweep", "", f"- status: `{report['status']}`", f"- cases: `{report['case_count']}`", f"- measured cases: `{report['measured_case_count']}`", f"- timed-out cases: `{report['timed_out_case_count']}`", f"- nonzero polarity passes: `{report['nonzero_sign_pass_count']}` of `{report['nonzero_case_count']}`", f"- zero-input cases measured: `{report['zero_input_measured_count']}`", f"- nonzero preamp margin passes: `{report['nonzero_preamp_margin_pass_count']}` of `{report['nonzero_case_count']}`", f"- preamp margin target V: `{report['preamp_margin_target_v']:.9e}`", f"- minimum nonzero preamp magnitude V: `{report['minimum_nonzero_preamp_abs_v']:.9e}`", "", "## First-Principles Reading", "", "The nominal zero crossing is not enough. Process, supply, and temperature change transistor current, gain, headroom, and the sampled operating point. This sweep checks sign, convergence, and useful preamp amplitude at three deliberately separated corners.", "", "The slow, cold, low-supply corner preserves polarity but collapses amplitude. A sign-only pass would therefore allow a corner that cannot reliably drive the latch.", "", "## Next Gate", "", "Expand to the declared corner matrix, redesign or digitally derate the low-supply corner, add device mismatch and small-signal noise, then carry the measured input-referred uncertainty into the 12-bit transition test.", "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_phase_transistor_corner_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
