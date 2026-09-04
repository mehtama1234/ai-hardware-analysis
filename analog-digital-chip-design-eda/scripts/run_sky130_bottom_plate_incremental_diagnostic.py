#!/usr/bin/env python3
"""Find the first added element that breaks the Sky130 sample-switch deck."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from run_sky130_transistor_sample_switch_ngspice import Case, build_deck

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-bottom-plate-incremental-diagnostic.json"
OUT_MD = EVIDENCE / "sky130-bottom-plate-incremental-diagnostic.md"
TIMEOUT_S = 120


def measure(stdout: str, name: str) -> float:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", stdout)
    if not values:
        raise ValueError(f"missing measurement {name}")
    return float(values[-1])


def stage_source(stage: str) -> str:
    source = build_deck(Case(stage, 0.9, 6.8))
    if stage == "large_sample_switch":
        source = source.replace("W={wn}", "W=32.0").replace("W={wp}", "W=64.0")
        source = source.replace("7n 20n", "15n 20n")
    insert = "CLOAD sample 0 {cload}\nRLEAK sample 0 100G"
    if stage in {"baseline_plus_capacitor", "large_sample_switch"}:
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G"
    elif stage == "plus_capacitor_plus_nfet":
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G\nVPLATE bottom_ctrl 0 1.8\nXPLATE bottom bottom_ctrl 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15"
    elif stage == "large_sample_switch_plus_nfet":
        source = source.replace("W={wn}", "W=32.0").replace("W={wp}", "W=64.0")
        source = source.replace("7n 20n", "15n 20n")
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G\nVPLATE bottom_ctrl 0 1.8\nXPLATE bottom bottom_ctrl 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15"
    elif stage == "very_large_sample_switch_plus_nfet":
        source = source.replace("W={wn}", "W=256.0").replace("W={wp}", "W=512.0")
        source = source.replace("7n 20n", "15n 20n")
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G\nVPLATE bottom_ctrl 0 1.8\nXPLATE bottom bottom_ctrl 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15"
    elif stage == "larger_legal_sample_switch_plus_nfet":
        source = source.replace("W={wn}", "W=64.0").replace("W={wp}", "W=128.0")
        source = source.replace("7n 20n", "15n 20n")
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G\nVPLATE bottom_ctrl 0 1.8\nXPLATE bottom bottom_ctrl 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15"
    elif stage == "long_large_sample_switch_plus_nfet":
        source = source.replace("W={wn}", "W=32.0").replace("W={wp}", "W=64.0")
        source = source.replace("7n 20n", "15n 20n")
        source = source.replace(".tran 2p 8n", ".tran 2p 20n")
        source = source.replace("AT=6.8n", "AT=10.0n")
        insert += "\nCBOTTOM sample bottom 8p\nR_BOTTOM bottom 0 1G\nVPLATE bottom_ctrl 0 1.8\nXPLATE bottom bottom_ctrl 0 0 sky130_fd_pr__nfet_01v8 W=8.0 L=0.15"
    source = source.replace("CLOAD sample 0 {cload}\nRLEAK sample 0 100G", insert)
    if stage != "baseline":
        source = source.replace(".measure tran switch_mid_v FIND v(sample) AT=0.5n", ".measure tran switch_mid_v FIND v(sample) AT=0.5n\n.measure tran bottom_v FIND v(bottom) AT=6.8n")
    return source


def run(stage: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="aimc-bottom-plate-incremental-") as tmp:
        path = Path(tmp) / "stage.sp"
        path.write_text(stage_source(stage), encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"stage": stage, "measured": False, "timed_out": True}
    row: dict[str, Any] = {"stage": stage, "measured": result.returncode == 0, "timed_out": False, "returncode": result.returncode}
    if result.returncode != 0:
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    try:
        row.update({"sampled_v": measure(result.stdout, "sampled_v"), "input_v": measure(result.stdout, "input_v"), "bottom_v": measure(result.stdout, "bottom_v") if "bottom_v" in result.stdout else None})
    except ValueError as exc:
        row["measured"] = False
        row["measurement_error"] = str(exc)
        row["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        return row
    row["sample_error_v"] = abs(row["input_v"] - row["sampled_v"])
    return row


def main() -> int:
    stages = ("baseline", "baseline_plus_capacitor", "plus_capacitor_plus_nfet", "large_sample_switch_plus_nfet", "very_large_sample_switch_plus_nfet")
    rows = [run(stage) for stage in stages]
    report = {
        "result_type": "sky130_bottom_plate_incremental_diagnostic",
        "status": "incremental_diagnostic_complete" if all(row["measured"] for row in rows) else "incremental_diagnostic_isolated_timeout",
        "stage_count": len(rows),
        "measured_stage_count": sum(row["measured"] for row in rows),
        "rows": rows,
        "claim_boundary": {
            "allowed": "identifies which incremental addition changes convergence in a known-good Sky130 sample-switch deck",
            "not_allowed": "does not prove a working bottom-plate cell, four-bit DAC, SAR accuracy, PVT behavior, mismatch/noise yield, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Sky130 Bottom-Plate Incremental Diagnostic", "", f"- status: `{report['status']}`", f"- measured stages: `{report['measured_stage_count']}` of `{report['stage_count']}`", "", "The stages start from the known-good transmission-gate sample-switch deck and add one bottom-plate element at a time.", "", "| stage | measured | sampled V | bottom V | sample error V |", "| --- | --- | ---: | ---: | ---:|"]
    for row in rows:
        if row["measured"]:
            lines.append(f"| {row['stage']} | True | {row['sampled_v']:.6f} | {row['bottom_v'] if row['bottom_v'] is not None else 'n/a'} | {row['sample_error_v']:.6e} |")
        else:
            lines.append(f"| {row['stage']} | False | timeout | timeout | timeout |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_stage_count']}/{report['stage_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
