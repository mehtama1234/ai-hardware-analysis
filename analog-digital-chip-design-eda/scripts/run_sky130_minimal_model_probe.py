#!/usr/bin/env python3
"""Probe the local Sky130 model with a one-device operating point."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDK = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-minimal-model-probe.json"


def main() -> int:
    deck = f""".lib \"{PDK}\" tt
VDD d 0 1.8
VG g 0 0.9
VS s 0 0
VB b 0 0
M1 d g s b sky130_fd_pr__nfet_01v8 W=1u L=0.15u
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7
.op
.control
op
print @m1[id]
.endc
.end
"""
    timeout = float(os.environ.get("AIMC_MINIMAL_MODEL_TIMEOUT_S", "10"))
    with tempfile.TemporaryDirectory(prefix="aimc-sky130-minimal-") as tmp:
        path = Path(tmp) / "minimal.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, text=True, capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            report = {"result_type": "sky130_minimal_model_probe", "status": "model_operating_point_timeout", "timeout_s": timeout}
        else:
            report = {"result_type": "sky130_minimal_model_probe", "status": "model_operating_point_pass" if proc.returncode == 0 else "model_operating_point_failed", "returncode": proc.returncode, "output_excerpt": (proc.stdout + proc.stderr)[-1200:]}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
