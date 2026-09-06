#!/usr/bin/env python3
"""Re-extract a copied latch and inspect substrate capacitance export."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CELL = "sky130_isolated_frontend_active_load_latch_v2"
WB = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"


def main():
    output = ROOT / "evidence/aimc-simulator-adapters/extraction-consistency" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    magic = Path.home() / "eda-tools/magic-8.3.682/bin/magic"
    rc = Path.home() / "eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc"
    results = {}
    for mode in ("lvs", "default", "lvs_flat", "default_wrapped"):
        case = output / mode
        case.mkdir()
        shutil.copy2(WB / f"cells/{CELL}.mag", case / f"{CELL}.mag")
        commands = [f"load {CELL} -force", "select top cell", "extract all"]
        if mode.startswith("lvs"):
            commands.append("ext2spice lvs")
        if mode == "lvs_flat":
            commands += ["ext2spice hierarchy off", "ext2spice subcircuit on", "ext2spice subcircuit top on"]
        if mode == "default_wrapped":
            commands += ["ext2spice format ngspice", "ext2spice subcircuit top on"]
        commands += ["ext2spice cthresh 0", "ext2spice rthresh 0", "ext2spice -o extracted.spice", "quit -noprompt"]
        (case / "commands.tcl").write_text("\n".join(commands) + "\n")
        proc = subprocess.run([str(magic), "-dnull", "-noconsole", "-rcfile", str(rc)], input="\n".join(commands) + "\n", cwd=case, capture_output=True, text=True, timeout=30, env={**os.environ, "PDK_ROOT": str(Path.home() / "eda-tools/pdks")})
        (case / "stdout.log").write_text(proc.stdout)
        (case / "stderr.log").write_text(proc.stderr)
        if not (case / "extracted.spice").exists():
            results[mode] = {"returncode": proc.returncode, "missing_extraction": True}
            continue
        caps = [line for line in (case / "extracted.spice").read_text().splitlines() if line.startswith("C") and ("out_p vss" in line or "out_n vss" in line)]
        nodes = [line for line in (case / f"{CELL}.ext").read_text().splitlines() if line.startswith(('node "out_p"', 'node "out_n"'))]
        results[mode] = {"returncode": proc.returncode, "substrate_caps": caps, "raw_nodes": nodes}
    (output / "result.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    print(output)


if __name__ == "__main__":
    main()
