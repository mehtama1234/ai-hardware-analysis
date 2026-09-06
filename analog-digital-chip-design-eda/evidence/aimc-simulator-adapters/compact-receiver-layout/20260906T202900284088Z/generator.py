#!/usr/bin/env python3
"""Generate a compact receiver with the installed PDK's native MOS drawers."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/"evidence/aimc-simulator-adapters/compact-receiver-layout"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=False)
    pdk = Path(os.environ.get("PDK_ROOT", str(Path.home()/"eda-tools/pdks")))
    tech = pdk/"sky130A/libs.tech/magic"
    commands = "\n".join([
        "load compact_receiver -force", "box position 0um 0um", "box size 0um 0um",
        "sky130::sky130_fd_pr__nfet_01v8_draw [sky130::sky130_fd_pr__nfet_01v8_defaults]",
        "box position 0um 5um", "box size 0um 0um",
        "sky130::sky130_fd_pr__pfet_01v8_draw [sky130::sky130_fd_pr__pfet_01v8_defaults]",
        "save compact_receiver", "select top cell", "drc on", "drc catchup", "drc count",
        "extract all", "ext2spice lvs", "ext2spice hierarchy off", "ext2spice subcircuit on",
        "ext2spice subcircuit top on", "ext2spice cthresh 0", "ext2spice rthresh 0",
        "ext2spice -o extracted.spice", "quit -noprompt", ""])
    (out/"commands.tcl").write_text(commands)
    (out/"generator.py").write_text(Path(__file__).read_text())
    proc = subprocess.run([str(Path.home()/"eda-tools/magic-8.3.682/bin/magic"), "-dnull", "-noconsole",
                           "-rcfile", str(tech/"sky130A.magicrc")], input=commands, text=True,
                          capture_output=True, cwd=out, timeout=120, env={**os.environ, "PDK_ROOT": str(pdk)})
    (out/"magic.log").write_text(proc.stdout+proc.stderr)
    report = {"status": "primitive_placement_only_not_connected", "returncode": proc.returncode,
              "pdk_drawer_sha256": hashlib.sha256((tech/"sky130A.tcl").read_bytes()).hexdigest(),
              "accepted_converter": False}
    (out/"result.json").write_text(json.dumps(report, indent=2)+"\n")
    print(out)


if __name__ == "__main__":
    main()
