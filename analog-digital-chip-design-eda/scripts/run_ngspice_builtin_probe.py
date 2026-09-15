#!/usr/bin/env python3
"""Check ngspice itself with a resistor-only operating point."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "ngspice-builtin-probe.json"


def main() -> int:
    deck = "V1 n 0 1\nR1 n 0 1k\n.op\n.control\nop\n.endc\n.end\n"
    timeout = float(os.environ.get("AIMC_BUILTIN_PROBE_TIMEOUT_S", "5"))
    with tempfile.TemporaryDirectory(prefix="aimc-ngspice-builtin-") as tmp:
        path = Path(tmp) / "builtin.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            report = {"result_type": "ngspice_builtin_probe", "status": "ngspice_runtime_timeout", "timeout_s": timeout}
        else:
            report = {"result_type": "ngspice_builtin_probe", "status": "ngspice_builtin_pass" if proc.returncode == 0 else "ngspice_builtin_failed", "returncode": proc.returncode, "output_excerpt": (proc.stdout + proc.stderr)[-800:]}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
