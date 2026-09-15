#!/usr/bin/env python3
"""Run a minimal DC-biased Sky130 preamp transient to isolate startup issues."""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from run_sky130_two_phase_preamp_latch_candidate import Case, PDK_LIB, build_deck

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-preamp-dc-sanity.json"
TIMEOUT = float(os.environ.get("AIMC_PREAMP_SANITY_TIMEOUT_S", "20"))


def measure(text: str, name: str) -> float | None:
    found = re.findall(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", text)
    return float(found[-1]) if found else None


def run(diff_mv: float) -> dict[str, object]:
    deck = build_deck(Case(f"sanity_{diff_mv:+.3f}mV", diff_mv))
    vinp = 0.9 + diff_mv / 2000.0
    vinn = 0.9 - diff_mv / 2000.0
    deck = re.sub(r"VINP inp 0 PULSE\([^\n]+", f"VINP inp 0 {vinp:.9f}", deck)
    deck = re.sub(r"VINN inn 0 PULSE\([^\n]+", f"VINN inn 0 {vinn:.9f}", deck)
    deck = re.sub(r"VCTRL ctrl 0 PULSE\([^\n]+", "VCTRL ctrl 0 1.8", deck)
    deck = re.sub(r"VCTRLB ctrlb 0 PULSE\([^\n]+", "VCTRLB ctrlb 0 0", deck)
    keep = []
    for line in deck.splitlines():
        if any(line.startswith(prefix) for prefix in ("XLPRE", "XLP ", "XLN ", "XRP ", "XRN ", "XINP", "XINN", "XTAIL", "XEVAL", "COUT")):
            continue
        keep.append(line)
    deck = "\n".join(keep).replace(".tran 5p 3n", ".tran 20p 1n")
    deck = deck.replace(".ic v(sp)=0.9 v(sn)=0.9", ".ic v(sp)=0.9 v(sn)=0.9 v(pre_p)=0.9 v(pre_n)=0.9")
    deck = deck.replace("CPREP pre_p 0 2f", "CPREP pre_p 0 2f\nRBIASP pre_p 0 10Meg\nRBiasN pre_n 0 10Meg")
    deck = deck.replace(".measure tran preamp_p_before_latch_v FIND v(pre_p) AT=1.45n", ".measure tran preamp_p_before_latch_v FIND v(pre_p) AT=0.90n")
    deck = deck.replace(".measure tran preamp_n_before_latch_v FIND v(pre_n) AT=1.45n", ".measure tran preamp_n_before_latch_v FIND v(pre_n) AT=0.90n")
    with tempfile.TemporaryDirectory(prefix="aimc-preamp-sanity-") as tmp:
        path = Path(tmp) / "sanity.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, timeout=TIMEOUT, check=False)
        except subprocess.TimeoutExpired:
            return {"diff_mv": diff_mv, "measured": False, "timed_out": True}
    if proc.returncode != 0:
        return {"diff_mv": diff_mv, "measured": False, "timed_out": False, "returncode": proc.returncode, "error_excerpt": (proc.stdout + proc.stderr)[-1000:]}
    p = measure(proc.stdout, "preamp_p_before_latch_v")
    n = measure(proc.stdout, "preamp_n_before_latch_v")
    return {"diff_mv": diff_mv, "measured": p is not None and n is not None, "timed_out": False, "preamp_diff_v": None if p is None or n is None else n - p}


def main() -> int:
    rows = [run(float(token)) for token in os.environ.get("AIMC_PREAMP_SANITY_DIFFS_MV", "-0.1,0.0,0.1").split(",")]
    report = {"result_type": "sky130_preamp_dc_sanity", "status": "dc_preamp_sanity_measured" if all(r.get("measured") for r in rows) else "dc_preamp_sanity_incomplete", "rows": rows, "claim_boundary": "Minimal DC-biased preamp startup diagnostic; not clocked latch, SAR, PVT, noise, mismatch, or converter acceptance."}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"], len(rows))
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
