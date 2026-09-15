#!/usr/bin/env python3
"""Portable Colab/runtime probe for ngspice and a supplied Sky130 model bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run_ngspice(deck: str, cwd: Path, timeout: float) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="sky130-colab-probe-") as tmp:
        path = Path(tmp) / "probe.sp"
        path.write_text(deck, encoding="utf-8")
        try:
            proc = subprocess.run(["ngspice", "-b", str(path)], cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "timeout_s": timeout}
    return {"status": "pass" if proc.returncode == 0 else "failed", "returncode": proc.returncode, "output_excerpt": (proc.stdout + proc.stderr)[-1200:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sky130-lib", type=Path, required=True)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    parser.add_argument("--output", type=Path, default=Path("sky130-runtime-probe.json"))
    args = parser.parse_args()
    lib = args.sky130_lib.resolve()
    include_root = lib.parent
    required = [include_root / "corners" / "tt.spice", include_root / "r+c" / "res_typical__cap_typical.spice"]
    report: dict[str, object] = {"result_type": "sky130_colab_runtime_probe", "sky130_lib": str(lib), "ngspice_path": shutil.which("ngspice"), "required_includes_present": all(path.exists() for path in required), "required_includes": [str(path) for path in required]}
    if not lib.exists() or not report["required_includes_present"] or not report["ngspice_path"]:
        report["status"] = "preflight_failed"
    else:
        report["resistor_control"] = run_ngspice("V1 n 0 1\nR1 n 0 1k\n.op\n.control\nop\n.endc\n.end\n", include_root, args.timeout_s)
        model_deck = f'.lib "{lib}" tt\nVDD d 0 1.8\nVG g 0 0.9\nVS s 0 0\nVB b 0 0\nX1 d g s b sky130_fd_pr__nfet_01v8\n.op\n.control\nop\n.endc\n.end\n'
        report["sky130_device"] = run_ngspice(model_deck, include_root, args.timeout_s)
        report["status"] = "sky130_device_pass" if report["sky130_device"].get("status") == "pass" else "sky130_device_unavailable"
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
