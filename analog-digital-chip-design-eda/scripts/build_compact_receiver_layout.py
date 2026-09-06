#!/usr/bin/env python3
"""Generate a compact receiver with the installed PDK's native MOS drawers."""
from datetime import datetime, timezone
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/"evidence/aimc-simulator-adapters/compact-receiver-layout"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=False)
    pdk = Path(os.environ.get("PDK_ROOT", str(Path.home()/"eda-tools/pdks")))
    tech = pdk/"sky130A/libs.tech/magic"
    commands = "\n".join([
        "load receiver_nfet -force", "box position 0um 0um", "box size 0um 0um",
        "sky130::sky130_fd_pr__nfet_01v8_draw [sky130::sky130_fd_pr__nfet_01v8_defaults]",
        "save receiver_nfet", "load receiver_pfet -force", "box position 0um 0um", "box size 0um 0um",
        "sky130::sky130_fd_pr__pfet_01v8_draw [sky130::sky130_fd_pr__pfet_01v8_defaults]",
        "save receiver_pfet", "quit -noprompt", ""])
    (out/"commands.tcl").write_text(commands)
    (out/"generator.py").write_text(Path(__file__).read_text())
    proc = subprocess.run([str(Path.home()/"eda-tools/magic-8.3.682/bin/magic"), "-dnull", "-noconsole",
                           "-rcfile", str(tech/"sky130A.magicrc")], input=commands, text=True,
                          capture_output=True, cwd=out, timeout=120, env={**os.environ, "PDK_ROOT": str(pdk)})
    (out/"magic.log").write_text(proc.stdout+proc.stderr)
    layers = defaultdict(list)
    for name, dy in (("receiver_nfet", 0), ("receiver_pfet", 1000)):
        source = (out/f"{name}.mag").read_text()
        if "magscale 1 2" not in source:
            raise ValueError("PDK drawing grid changed; review placement coordinates")
        section = None
        for line in source.splitlines():
            if line.startswith("<< "):
                section = line[3:-3]
            elif line.startswith("rect ") and section not in ("checkpaint", "properties"):
                x1,y1,x2,y2 = map(int, line.split()[1:])
                layers[section].append(f"rect {x1} {y1+dy} {x2} {y2+dy}")
    def rect(layer, x1,y1,x2,y2):
        layers[layer].append(f"rect {x1} {y1} {x2} {y2}")
    for y in (0,1000):
        # Source plus native guard-ring body tap; drain runs outward on M1.
        rect("viali", -175,y-17,-141,y+17)
        rect("metal1", -181,y-23,-135,y+23)
        rect("metal1", -420,y-20,-44,y+20)
        rect("metal1", 44,y-20,420,y+20)
        # Enclosures follow the installed PDK's via1_draw procedure.
        rect("via1", -26,y+74,26,y+126)
        rect("metal1", -36,y+74,36,y+126)
        rect("metal2", -26,y+64,26,y+136)
        rect("metal2", -320,y+80,0,y+120)
    rect("metal1", 380,-20,420,1020)
    rect("metal2", -320,80,-280,1120)
    lines = ["magic", "tech sky130A", "magscale 1 2", "timestamp 1788726600"]
    for layer, shapes in layers.items():
        lines += [f"<< {layer} >>", *shapes]
    lines += ["<< labels >>"]
    for index, (name, layer, x, y) in enumerate((("input","metal2",-300,500), ("output","metal1",400,500),
                                                ("vdd","metal1",-400,1000), ("vss","metal1",-400,0)),1):
        lines += [f"rlabel {layer} {x-10} {y-10} {x+10} {y+10} 0 {name}",f"port {index} nsew"]
    (out/"compact_receiver.mag").write_text("\n".join(lines+["<< end >>"])+"\n")
    extraction = "\n".join(["load compact_receiver -force", "select top cell", "drc on", "drc catchup", "drc count",
                             "drc listall why", "extract all", "ext2spice lvs", "ext2spice hierarchy off",
                             "ext2spice subcircuit on", "ext2spice subcircuit top on", "ext2spice cthresh 0",
                             "ext2spice rthresh 0", "ext2spice -o extracted.spice", "quit -noprompt", ""])
    (out/"extract.tcl").write_text(extraction)
    extracted = subprocess.run([str(Path.home()/"eda-tools/magic-8.3.682/bin/magic"), "-dnull", "-noconsole",
                                "-rcfile", str(tech/"sky130A.magicrc")], input=extraction, text=True,
                               capture_output=True, cwd=out, timeout=120, env={**os.environ,"PDK_ROOT":str(pdk)})
    (out/"extraction.log").write_text(extracted.stdout+extracted.stderr)
    counts = re.findall(r"Total DRC errors found:\s*(\d+)",extracted.stdout+extracted.stderr)
    report = {"status": "receiver_extracted_not_lvs_verified", "returncode": extracted.returncode,
              "drc_errors": int(counts[-1]) if counts else None,
              "pdk_drawer_sha256": hashlib.sha256((tech/"sky130A.tcl").read_bytes()).hexdigest(),
              "accepted_converter": False}
    (out/"reference.spice").write_text("* Independently specified compact receiver, W/L in micrometres.\n"
        ".subckt compact_receiver input output vdd vss\n"
        "XN output input vss vss sky130_fd_pr__nfet_01v8 w=0.42 l=0.15\n"
        "XP output input vdd vdd sky130_fd_pr__pfet_01v8 w=0.42 l=0.15\n"
        ".ends compact_receiver\n")
    device_lines = [line for line in (out/"extracted.spice").read_text().splitlines() if not line.lower().startswith("c")]
    (out/"lvs_devices.spice").write_text("\n".join(device_lines)+"\n")
    setup = pdk/"sky130A/libs.tech/netgen/sky130A_setup.tcl"
    lvs = subprocess.run([str(Path.home()/"eda-tools/netgen-1.5/bin/netgen"), "-batch", "lvs",
                          f"{out/'lvs_devices.spice'} compact_receiver", f"{out/'reference.spice'} compact_receiver",
                          str(setup), str(out/"netgen.log")], text=True, capture_output=True, cwd=out,
                         timeout=60, env={**os.environ,"PDK_ROOT":str(pdk)})
    (out/"netgen_stdout.log").write_text(lvs.stdout+lvs.stderr)
    log = (out/"netgen.log").read_text() if (out/"netgen.log").exists() else ""
    report["lvs_pass"] = lvs.returncode == 0 and "Final result: Circuits match uniquely." in log and "Property errors were found" not in log
    if report["lvs_pass"] and report["drc_errors"] == 0 and extracted.returncode == 0:
        report["status"] = "receiver_drc_lvs_pass_subblock_only"
    report["sha256"] = {name: hashlib.sha256((out/name).read_bytes()).hexdigest() for name in
                        ("compact_receiver.mag", "compact_receiver.ext", "extracted.spice", "reference.spice", "generator.py", "netgen.log")}
    report["netgen_setup_sha256"] = hashlib.sha256(setup.read_bytes()).hexdigest()
    (out/"result.json").write_text(json.dumps(report, indent=2)+"\n")
    print(out)
    return 0 if report["status"] == "receiver_drc_lvs_pass_subblock_only" else 1


if __name__ == "__main__":
    raise SystemExit(main())
