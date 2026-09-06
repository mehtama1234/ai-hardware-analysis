#!/usr/bin/env python3
"""Separate ngspice startup, full PDK parsing, and transistor operating point."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
LIB = Path.home() / "eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdk-init", action="store_true")
    parser.add_argument("--minimal-models", action="store_true")
    args = parser.parse_args()
    output = ROOT / "evidence/aimc-simulator-adapters/model-startup-probe" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    circuits = {
        "resistor": "V1 a 0 1\nR1 a 0 1k\n",
        "library_only": f'.lib "{LIB}" tt\nV1 a 0 1\nR1 a 0 1k\n',
        "one_nfet": f'.lib "{LIB}" tt\nV1 a 0 1\nVG g 0 0.9\nX1 a g 0 0 sky130_fd_pr__nfet_01v8 w=1.2 l=0.6\n',
    }
    if args.minimal_models:
        models = LIB.parents[2] / "libs.ref/sky130_fd_pr/spice"
        model_names = ["nfet_01v8__tt.pm3", "nfet_01v8__mismatch.corner", "pfet_01v8__tt.corner", "pfet_01v8__mismatch.corner"]
        includes = ".option scale=1u\n.param mc_mm_switch=0 mc_pr_switch=0\n" + "\n".join(f'.include "{models / ("sky130_fd_pr__" + name + ".spice")}"' for name in model_names)
        circuits = {name: circuit.replace(f'.lib "{LIB}" tt', includes) for name, circuit in circuits.items()}
    results = {}
    for name, circuit in circuits.items():
        directory = output / name
        directory.mkdir()
        if args.pdk_init:
            shutil.copy2(LIB.parent / "spinit", directory / ".spiceinit")
        (directory / "deck.spice").write_text("* Model startup isolation\n" + circuit + ".op\n.control\necho CONTROL_ENTERED\nop\nprint v(a)\nquit\n.endc\n.end\n")
        started = time.monotonic()
        try:
            proc = subprocess.run(["ngspice", "-b", "-o", "simulator.log", "deck.spice"], cwd=directory,
                                  capture_output=True, text=True, timeout=10)
            result = {"returncode": proc.returncode, "timeout": False}
            (directory / "stdout.log").write_text(proc.stdout)
            (directory / "stderr.log").write_text(proc.stderr)
        except subprocess.TimeoutExpired:
            result = {"returncode": None, "timeout": True}
        result["elapsed_s"] = time.monotonic() - started
        result["pdk_init"] = args.pdk_init
        result["minimal_models"] = args.minimal_models
        log = (directory / "simulator.log").read_text() if (directory / "simulator.log").exists() else ""
        result["control_entered"] = "CONTROL_ENTERED" in log
        result["log_bytes"] = len(log)
        results[name] = result
        print(name, result, flush=True)
    (output / "result.json").write_text(json.dumps(results, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
