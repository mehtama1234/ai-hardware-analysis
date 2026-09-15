#!/usr/bin/env python3
"""Fresh-Colab control for the ngspice executable."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    install = os.environ.get("COLAB_INSTALL_NGSPICE", "1") == "1"
    install_result = None
    if install and not shutil.which("ngspice"):
        install_result = subprocess.run(["apt-get", "update", "-qq"], capture_output=True, text=True, check=False)
        if install_result.returncode == 0:
            install_result = subprocess.run(["apt-get", "install", "-y", "-qq", "ngspice"], capture_output=True, text=True, check=False)
    report: dict[str, object] = {"result_type": "colab_ngspice_control_probe", "ngspice_path": shutil.which("ngspice")}
    if install_result is not None:
        report["install_returncode"] = install_result.returncode
        report["install_excerpt"] = (install_result.stdout + install_result.stderr)[-800:]
    if not report["ngspice_path"]:
        report["status"] = "ngspice_missing"
    else:
        with tempfile.TemporaryDirectory(prefix="colab-ngspice-control-") as tmp:
            deck = Path(tmp) / "control.sp"
            deck.write_text("V1 n 0 1\nR1 n 0 1k\n.op\n.control\nop\n.endc\n.end\n", encoding="utf-8")
            proc = subprocess.run(["ngspice", "-b", str(deck)], capture_output=True, text=True, check=False)
        report.update({"status": "pass" if proc.returncode == 0 else "failed", "returncode": proc.returncode, "output_excerpt": (proc.stdout + proc.stderr)[-800:]})
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
