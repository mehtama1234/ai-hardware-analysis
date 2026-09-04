#!/usr/bin/env python3
"""Run the independent 3x3x3 PVT matrix at the latch-free preamp boundary."""

from __future__ import annotations

import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from run_sky130_two_phase_preamp_latch_candidate import Case, build_deck, read_measure

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-two-phase-transistor-full-pvt.json"
OUT_MD = EVIDENCE / "sky130-two-phase-transistor-full-pvt.md"
TIMEOUT_S = 100
MARGIN_TARGET_V = 0.0005


def cases() -> list[dict[str, Any]]:
    return [
        {"process": process, "temperature_c": temperature, "supply_v": supply,
         "name": f"{process}_{temperature:+g}c_{supply:.2f}v"}
        for process in ("tt", "ss", "ff")
        for temperature in (-20.0, 25.0, 85.0)
        for supply in (1.62, 1.80, 1.98)
    ]


def make_deck(diff_mv: float, corner: dict[str, Any], path: Path) -> None:
    deck = build_deck(Case(f"full_pvt_{diff_mv:+.3f}mV", diff_mv))
    deck = deck.replace('" tt', f'" {corner["process"]}')
    deck = deck.replace(".param vdd=1.8", f".param vdd={corner['supply_v']}")
    deck = deck.replace(".tran 5p 3n", ".tran 20p 1.5n")
    deck = deck.replace(".tran 20p 1.5n", f".temp {corner['temperature_c']}\n.tran 20p 1.5n")
    deck = deck.replace(
        ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25 v(outp)=1.8 v(outn)=1.8",
        ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=1.0 v(pre_n)=1.0 v(pre_tail_node)=0.25",
    )
    remove_markers = (
        "VCLK clk", "VCLKB clkb", "XLPRE1 ", "XLPRE2 ", "XLP ", "XLN ",
        "XRP ", "XRN ", "XINP ", "XINN ", "XTAIL ", "XEVAL ",
        "COUTP ", "COUTN ", "sampled_p_after_v", "sampled_n_after_v",
        "preamp_p_after_latch_v", "preamp_n_after_latch_v", "output_p_final_v", "output_n_final_v",
    )
    path.write_text("\n".join(line for line in deck.splitlines() if not any(marker in line for marker in remove_markers)) + "\n", encoding="utf-8")


def run_one(item: tuple[dict[str, Any], float]) -> dict[str, Any]:
    corner, diff_mv = item
    with tempfile.TemporaryDirectory(prefix="aimc-full-pvt-") as tmp:
        path = Path(tmp) / "full-pvt.sp"
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
        row.update({
            "preamp_diff_before_latch_v": preamp,
            "preamp_abs_v": abs(preamp),
            "expected_sign": 1 if diff_mv > 0 else -1,
            "sign_preserved": (preamp > 0) == (diff_mv > 0),
            "margin_pass": abs(preamp) >= MARGIN_TARGET_V,
        })
        return row


def main() -> int:
    inputs = [(corner, diff) for corner in cases() for diff in (-0.2, 0.2)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run_one, inputs))
    measured = [row for row in rows if row["measured"]]
    report = {
        "result_type": "sky130_two_phase_transistor_full_pvt",
        "status": "full_pvt_matrix_measured_not_noise_or_mismatch_proof",
        "process_count": 3,
        "temperature_count": 3,
        "supply_count": 3,
        "corner_count": len(cases()),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(row["timed_out"] for row in rows),
        "margin_target_v": MARGIN_TARGET_V,
        "sign_pass_count": sum(row.get("sign_preserved", False) for row in measured),
        "margin_pass_count": sum(row.get("margin_pass", False) for row in measured),
        "minimum_nonzero_preamp_abs_v": min((row["preamp_abs_v"] for row in measured), default=None),
        "worst_case": min(measured, key=lambda row: row["preamp_abs_v"], default=None),
        "rows": rows,
        "claim_boundary": {
            "allowed": "measures deterministic preamp polarity and amplitude across an independent 3x3x3 process, temperature, and supply matrix",
            "not_allowed": "does not prove random noise, mismatch distributions, SAR conversion, extracted layout, board behavior, or silicon yield",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    worst = report["worst_case"]
    lines = [
        "# Sky130 Two-Phase Transistor Full PVT Matrix", "",
        f"- status: `{report['status']}`",
        f"- matrix: `{report['process_count']} process x {report['temperature_count']} temperature x {report['supply_count']} supply`",
        f"- cases: `{report['case_count']}`",
        f"- measured cases: `{report['measured_case_count']}`",
        f"- timed-out cases: `{report['timed_out_case_count']}`",
        f"- sign passes: `{report['sign_pass_count']}` of `{report['measured_case_count']}`",
        f"- preamp-margin passes: `{report['margin_pass_count']}` of `{report['measured_case_count']}`",
        f"- margin target: `{MARGIN_TARGET_V:.9e} V`",
        f"- worst preamp magnitude: `{report['minimum_nonzero_preamp_abs_v']:.9e} V`" if worst else "- worst preamp magnitude: not measured",
        "",
        "## First-Principles Reading", "",
        "The preamp differential is the signal that must survive before the latch can make a reliable decision. Process changes transistor gain, temperature changes mobility and leakage, and supply changes headroom. Sweeping them independently prevents a favorable process-temperature-supply combination from hiding the operating limit.", "",
        "A sign pass is only directional evidence. The amplitude-margin pass is the service rule: any measured row below the target must be redesigned, derated, or sent to digital fallback.", "",
        "## Worst Case", "",
        f"- corner: `{worst['name']}`" if worst else "- corner: not measured",
        f"- preamp magnitude: `{worst['preamp_abs_v']:.9e} V`" if worst else "- preamp magnitude: not measured",
        "",
        "## Next Gate", "",
        "Add mismatch and transistor noise at the worst independent corners, then repeat the same margin rule at every SAR transition.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"margin_pass_count,{report['margin_pass_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
