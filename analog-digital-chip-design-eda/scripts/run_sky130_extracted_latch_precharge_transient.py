#!/usr/bin/env python3
"""Test reset/precharge followed by decision on the extracted latch topology."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import run_sky130_extracted_regenerative_latch_transient as base

ROOT = base.ROOT
DECK = base.LAB / "spice" / "sky130-extracted-latch-precharge-transient.sp"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-latch-precharge-transient.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-extracted-latch-precharge-transient.md"


def measure(text: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    if not values:
        raise ValueError(name)
    return float(values[-1])


def make_deck(diff_mv: float, balance_cap_ff: float) -> str:
    text = base.deck(diff_mv, 0.0)
    text = text.replace("RLP vdd out_p 20k\nRLN vdd out_n 20k", f"RLP vdd out_p 20k\nRLN vdd out_n 20k\nC_BAL out_p 0 {balance_cap_ff:.12g}f\n.model PRECHARGE SW(Ron=10 Roff=1e12 Vt=0.9 Vh=0.05)\nVRESET reset 0 PULSE(1.8 0 0.20n 20p 20p 0.80n 20n)\nSCP vdd out_p reset 0 PRECHARGE\nSCN vdd out_n reset 0 PRECHARGE")
    text = text.replace(".ic v(out_p)=0.9 v(out_n)=0.9", ".ic v(out_p)=1.8 v(out_n)=1.8")
    text = text.replace(".measure tran out_p_final FIND v(out_p) AT=3.00n", ".measure tran out_p_released FIND v(out_p) AT=1.20n\n.measure tran out_p_final FIND v(out_p) AT=3.00n")
    text = text.replace(".measure tran out_n_final FIND v(out_n) AT=3.00n", ".measure tran out_n_released FIND v(out_n) AT=1.20n\n.measure tran out_n_final FIND v(out_n) AT=3.00n")
    text = text.replace(".measure tran output_diff_initial PARAM='out_p_initial-out_n_initial'", ".measure tran output_diff_released PARAM='out_p_released-out_n_released'\n.measure tran output_diff_initial PARAM='out_p_initial-out_n_initial'")
    return text


def main() -> int:
    rows = []
    for balance_cap in (0.0, 1.0, 2.0, 4.0, 6.2, 8.0, 10.0):
      for diff in (-10.0, -0.5, 0.5, 10.0):
        DECK.write_text(make_deck(diff, balance_cap), encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(DECK)], cwd=ROOT, text=True,
                                  capture_output=True, check=False, timeout=30)
        except subprocess.TimeoutExpired:
            rows.append({"balance_cap_ff": balance_cap, "input_diff_mv": diff, "measured": False, "timed_out": True})
            continue
        row = {"balance_cap_ff": balance_cap, "input_diff_mv": diff, "measured": proc.returncode == 0, "timed_out": False, "returncode": proc.returncode}
        if proc.returncode == 0:
            row.update({"output_diff_released_v": measure(proc.stdout, "output_diff_released"),
                        "output_diff_final_v": measure(proc.stdout, "output_diff_final"),
                        "out_p_released_v": measure(proc.stdout, "out_p_released"),
                        "out_n_released_v": measure(proc.stdout, "out_n_released")})
            row["polarity_pass"] = (row["output_diff_final_v"] < 0) == (diff > 0)
            row["regenerated"] = abs(row["output_diff_final_v"]) >= 0.5
        else:
            row["error_excerpt"] = (proc.stdout + proc.stderr)[-1200:]
        rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("polarity_pass") and r.get("regenerated")]
    by_cap = {cap: [r for r in measured if r["balance_cap_ff"] == cap] for cap in sorted({r["balance_cap_ff"] for r in rows})}
    cap_summary = {str(cap): {"passing_case_count": sum(1 for r in cap_rows if r.get("polarity_pass") and r.get("regenerated")), "case_count": len(cap_rows)} for cap, cap_rows in by_cap.items()}
    report = {"result_type": "sky130_extracted_latch_precharge_balance_cap_sweep", "status": "extracted_latch_precharge_balance_sweep_open", "case_count": len(rows), "measured_case_count": len(measured), "passing_case_count": len(passing), "reset_window": "0.20 ns to 1.00 ns", "balance_capacitance_sweep_ff": sorted(by_cap), "cap_summary": cap_summary, "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "measures how an external output capacitance balance changes startup/precharge polarity using the exact extracted connectivity and parasitic capacitors with a bounded structural MOS model", "not_allowed": "does not prove physical precharge devices, Sky130-model convergence, kickback/noise/mismatch, LVS, SAR conversion, or converter acceptance"}}
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(["# Sky130 Extracted Latch Precharge Balance Sweep", "", f"- status: `{report['status']}`", f"- measured cases: `{len(measured)}` of `{len(rows)}`", f"- passing cases: `{len(passing)}`", f"- capacitance sweep fF: `{report['balance_capacitance_sweep_ff']}`", "", "Both extracted output nodes are precharged through behavioral switches before the differential decision. The sweep tests whether compensating the extracted output-node capacitance imbalance improves polarity; the switches and compensation capacitor are not physical signoff devices.", "", "| balance cap fF | input differential mV | final output diff V | polarity | regenerated |", "|---:|---:|---:|---|---|"] + [f"| `{r['balance_cap_ff']}` | `{r['input_diff_mv']}` | `{r.get('output_diff_final_v', 'failed')}` | `{r.get('polarity_pass', False)}` | `{r.get('regenerated', False)}` |" for r in rows] + ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{len(measured)}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT_JSON}")
    return 0 if len(measured) == len(rows) and len(passing) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
