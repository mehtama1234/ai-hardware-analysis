#!/usr/bin/env python3
"""Run the integrated structural transient on the widened physical variant."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import run_sky130_flat_latch_precharge_extracted_transient as base

ROOT = base.ROOT
CELL = "sky130_latch_precharge_wide_input_flat"
base.EXTRACTED = base.LAB / "layout-workbench" / "extracted" / f"{CELL}_extracted.spice"
base.DECK = base.LAB / "spice" / "sky130-wide-input-latch-precharge-extracted-transient.sp"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-wide-input-latch-precharge-extracted-transient.json"
MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-wide-input-latch-precharge-extracted-transient.md"


def main() -> int:
    rows = []
    for diff in (-10.0, -0.5, 0.5, 10.0):
        deck = base.make_deck(diff).replace("sky130_latch_precharge_flat", CELL)
        base.DECK.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(base.DECK)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=30)
        except subprocess.TimeoutExpired:
            rows.append({"input_diff_mv": diff, "measured": False, "timed_out": True})
            continue
        row = {"input_diff_mv": diff, "measured": proc.returncode == 0, "timed_out": False, "returncode": proc.returncode}
        if proc.returncode == 0:
            import re
            def read(name: str) -> float:
                return float(re.findall(rf"{name}\s*=\s*([-+0-9.eE]+)", proc.stdout)[-1])
            row["output_diff_final_v"] = read("output_diff_final")
            row["polarity_pass"] = (row["output_diff_final_v"] < 0) == (diff > 0)
            row["regenerated"] = abs(row["output_diff_final_v"]) >= 0.5
        else:
            row["error_excerpt"] = (proc.stdout + proc.stderr)[-1200:]
        rows.append(row)
    measured = [r for r in rows if r.get("measured")]
    passing = [r for r in measured if r.get("polarity_pass") and r.get("regenerated")]
    report = {"result_type": "sky130_wide_input_latch_precharge_extracted_transient", "status": "wide_input_latch_transient_passed_not_sky130_model_or_converter_signoff" if len(passing) == len(rows) else "wide_input_latch_transient_open", "cell": CELL, "layout_extracted_netlist": str(base.EXTRACTED.relative_to(ROOT)), "case_count": len(rows), "measured_case_count": len(measured), "passing_case_count": len(passing), "rows": rows, "accepted_post_layout_written": False, "claim_boundary": {"allowed": "tests the widened-sense six-device extracted physical variant with reset/precharge using bounded structural MOS models", "not_allowed": "does not prove Sky130-model convergence, noise, mismatch, LVS, PVT yield, SAR conversion, or converter acceptance"}}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD.write_text("\n".join(["# Sky130 Wide-Input Latch plus Precharge Extracted Transient", "", f"- status: `{report['status']}`", f"- measured cases: `{len(measured)}` of `{len(rows)}`", f"- passing cases: `{len(passing)}`", "", "This runs the widened-sense physical variant after Magic extraction, using the exact six-device connectivity and parasitics with bounded structural MOS models.", "", "| input differential mV | final output differential V | polarity | regenerated |", "|---:|---:|---|---|"] + [f"| `{r['input_diff_mv']}` | `{r.get('output_diff_final_v', 'failed')}` | `{r.get('polarity_pass', False)}` | `{r.get('regenerated', False)}` |" for r in rows] + ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured_case_count,{len(measured)}")
    print(f"passing_case_count,{len(passing)}")
    print(f"json,{OUT}")
    return 0 if len(measured) == len(rows) and len(passing) == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
