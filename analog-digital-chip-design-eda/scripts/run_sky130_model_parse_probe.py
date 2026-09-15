#!/usr/bin/env python3
"""Check whether ngspice can parse the Sky130 model section without devices."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDK = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
OUT = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-model-parse-probe.json"


def main() -> int:
    deck = f'.lib "{PDK}" tt\nV1 n 0 1\nR1 n 0 1k\n.op\n.control\nop\n.endc\n.end\n'
    timeout = float(os.environ.get("AIMC_MODEL_PARSE_TIMEOUT_S", "10"))
    with tempfile.TemporaryDirectory(prefix="aimc-sky130-parse-") as tmp:
        path = Path(tmp) / "parse.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            # sky130.lib.spice uses relative corner includes; resolve them
            # from the PDK ngspice directory rather than the repository root.
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=PDK.parent, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            report = {"result_type": "sky130_model_parse_probe", "status": "sky130_model_parse_timeout", "timeout_s": timeout}
        else:
            report = {"result_type": "sky130_model_parse_probe", "status": "sky130_model_parse_pass" if proc.returncode == 0 else "sky130_model_parse_failed", "returncode": proc.returncode, "output_excerpt": (proc.stdout + proc.stderr)[-800:]}
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["status"])
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
