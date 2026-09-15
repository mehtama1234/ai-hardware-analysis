#!/usr/bin/env python3
"""Validate an explicitly biased Sky130 differential preamp reference stage."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDK = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-explicit-bias-preamp-reference.json"


def measure(text: str, name: str) -> float | None:
    values = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    return float(values[-1]) if values else None


def run(diff_mv: float) -> dict[str, object]:
    vp, vn = 0.9 + diff_mv / 2000.0, 0.9 - diff_mv / 2000.0
    deck = f""".lib \"{PDK}\" tt
.param vdd=1.8
VDD vdd 0 1.8
VINP inp 0 {vp:.9f}
VINN inn 0 {vn:.9f}
I_TAIL tail 0 20u
RLP vdd outp 100k
RLN vdd outn 100k
M1 outp inp tail 0 sky130_fd_pr__nfet_01v8 W=8u L=0.15u
M2 outn inn tail 0 sky130_fd_pr__nfet_01v8 W=8u L=0.15u
CP outp 0 2f
CN outn 0 2f
.options method=gear reltol=2e-3 abstol=1e-14 vntol=1e-7 gmin=1e-10
.ic v(outp)=0.9 v(outn)=0.9 v(tail)=0.2
.tran 20p 1n uic
.measure tran outp_v FIND v(outp) AT=0.8n
.measure tran outn_v FIND v(outn) AT=0.8n
.control
run
.endc
.end
"""
    with tempfile.TemporaryDirectory(prefix="aimc-explicit-preamp-") as tmp:
        path = Path(tmp) / "reference.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, timeout=float(os.environ.get("AIMC_EXPLICIT_PREAMP_TIMEOUT_S", "10")), check=False)
        except subprocess.TimeoutExpired:
            return {"diff_mv": diff_mv, "measured": False, "timed_out": True}
    if proc.returncode != 0:
        return {"diff_mv": diff_mv, "measured": False, "timed_out": False, "returncode": proc.returncode, "error_excerpt": (proc.stdout + proc.stderr)[-1200:]}
    p, n = measure(proc.stdout, "outp_v"), measure(proc.stdout, "outn_v")
    return {"diff_mv": diff_mv, "measured": p is not None and n is not None, "timed_out": False, "outp_v": p, "outn_v": n, "output_diff_v": None if p is None or n is None else n - p}


def main() -> int:
    diffs = [float(x) for x in os.environ.get("AIMC_EXPLICIT_PREAMP_DIFFS_MV", "-0.1,0.0,0.1").split(",")]
    rows = [run(diff) for diff in diffs]
    report = {"result_type": "sky130_explicit_bias_preamp_reference", "status": "explicit_bias_reference_measured" if all(row.get("measured") for row in rows) else "explicit_bias_reference_incomplete", "rows": rows, "claim_boundary": "Explicitly biased differential-pair reference only; not the candidate latch, DAC, SAR, PVT, noise, mismatch, or converter acceptance."}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"], len(rows), sum(bool(row.get("measured")) for row in rows))
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
