#!/usr/bin/env python3
"""Build a fresh paired-row latch layout; preserve v2 and verify real extraction.

This is an experimental layout, not a parasitic-edited netlist or converter.
All dimensions are in the same Magic internal units as the preserved v2 cell.
"""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from audit_isolated_latch_connectivity import audit, audit_substrate_capacitance

ROOT = Path(__file__).resolve().parents[1]
CELL = "sky130_isolated_frontend_active_load_latch_v2"


def geometry():
    layers = defaultdict(list)
    ports = {}

    def rect(layer, x1, y1, x2, y2):
        layers[layer].append(f"rect {min(x1,x2)} {min(y1,y2)} {max(x1,x2)} {max(y1,y2)}")

    def wire(layer, x1, y1, x2, y2):
        if x1 != x2 and y1 != y2:
            raise ValueError("Manhattan wires only")
        rect(layer, min(x1,x2)-30, min(y1,y2)-30, max(x1,x2)+30, max(y1,y2)+30)

    def via(x, y, lo=1, hi=3):
        for level in range(lo, hi+1):
            rect(f"metal{level}", x-30, y-30, x+30, y+30)
            if level < hi:
                rect(f"via{level}", x-30, y-30, x+30, y+30)

    def port(name, x, y, layer="metal2"):
        ports.setdefault(name, (layer, x, y))

    def tap(kind, x, y, net):
        for layer in (kind, kind+"cont", "locali", "viali", "metal1"):
            rect(layer, x-30, y-50, x+30, y+50)
        via(x, y)
        port(net, x, y)

    # Mirrored device primitives. Source is outward; drain is inward.
    # Pair rows: isolation, input, feedback, active PFET, reset PFET.
    rows = [(0, False, "iso_tail"), (3000, False, "tail"),
            (6000, False, "tail"), (9000, True, "vdd_active"),
            (12000, True, "vdd")]
    bus = {"iso_tail": 7000, "tail": 6000, "vdd_active": 8000, "vdd": 9000}
    for y, pfet, source_net in rows:
        for side in (-1, 1):
            def r(layer, x1, y1, x2, y2):
                rect(layer, side*x1, y+y1, side*x2, y+y2)
            if pfet:
                r("nwell", 2800, 150, 4300, 1400)
            r("pdiffusion" if pfet else "ndiffusion", 3100, 690, 3700, 810)
            r("polysilicon", 3380, 200, 3440, 1200)
            for x in (3140, 3540):
                for layer in (("pdc" if pfet else "ndc"), "mcon"):
                    r(layer, x, 700, x+120, 760)
                r("metal1", x-40, 620, x+160, 800)
            for layer in ("pc", "locali", "mcon", "metal1"):
                r(layer, 3380, 250, 3440, 310)
            d, s, g = side*3200, side*3600, side*3410
            via(s, y+730)
            wire("metal3", s, y+730, side*bus[source_net], y+730)
            via(side*bus[source_net], y+730, 2, 3)
            via(d, y+730)
            drain_bus = side*(1500 if y == 0 else 2000)
            wire("metal3", d, y+730, drain_bus, y+730)
            via(drain_bus, y+730, 2, 3)
            if y == 0:
                via(g, y+280, 1, 2)
                port("sense_p" if side == -1 else "sense_n", g, y+280)
            elif y == 3000:
                via(g, y+280)
                wire("metal3", g, y+280, side*1500, y+280)
                via(side*1500, y+280, 2, 3)
            elif y in (6000, 9000):
                # Two crossing feedback nets use separated M4 tracks; the
                # short gate stubs stay on M3 so crossings do not short.
                # Alternate the longer crossover stub between the NFET and
                # PFET rows rather than loading the same output twice.
                track = y+280+(200 if (side == 1) != (y == 9000) else 0)
                via(g, y+280)
                # Retain equal physical stub length on both gates, including
                # the unused extension above the lower crossover landing.
                wire("metal3", g, y+280, g, y+480)
                via(g, track, 3, 4)
                wire("metal4", g, track, -side*2000, track)
                via(-side*2000, track, 2, 4)
            else:
                via(g, y+280)
                wire("metal3", g, y+280, 0, y+280)
                port("reset", 0, y+280, "metal3")
            if pfet:
                tap("nsubdiff", side*4100, y+1100, source_net)
                wire("metal3", side*4100, y+1100, side*bus[source_net], y+1100)
                via(side*bus[source_net], y+1100, 2, 3)

    for side in (-1, 1):
        wire("metal2", side*1500, 730, side*1500, 3280)
        port("latch_sense_p" if side == -1 else "latch_sense_n", side*1500, 1000)
        wire("metal2", side*2000, 3730, side*2000, 12730)
        port("out_p" if side == -1 else "out_n", side*2000, 4000)
    # Paired source buses and symmetric common-net bridges.
    for net, x in bus.items():
        ys = [y+730 for y, _, source in rows if source == net]
        if net in ("vdd", "vdd_active"):
            ys += [y+1100 for y, _, source in rows if source == net]
        bridge = {"iso_tail": -500, "tail": 15800, "vdd_active": 10500, "vdd": 13500}[net]
        for side in (-1, 1):
            wire("metal2", side*x, min(ys+[bridge]), side*x, max(ys+[bridge]))
            via(side*x, bridge, 2, 3)
        wire("metal3", -x, bridge, x, bridge)
        port(net, 0, bridge, "metal3")
    # Single wide evaluation NFET, with source grounded and drain on tail.
    for layer, box in [("ndiffusion", (-300, 15200, 300, 15800)),
                       ("polysilicon", (-30, 15000, 30, 16000))]:
        rect(layer, *box)
    for x in (-200, 200):
        for layer in ("ndc", "mcon"):
            rect(layer, x-60, 15500, x+60, 15560)
        rect("metal1", x-100, 15420, x+100, 15600)
        via(x, 15530)
    wire("metal3", 200, 15530, 200, 15800)
    wire("metal3", -200, 15530, -1000, 15530)
    via(-1000, 15530, 2, 3)
    wire("metal2", -1000, 15530, -1000, 17000)
    tap("psubdiff", -1000, 17000, "vss")
    for layer in ("pc", "locali", "mcon", "metal1"):
        rect(layer, -30, 15050, 30, 15110)
    via(0, 15080, 1, 2)
    port("eval", 0, 15080)

    order = ["out_p", "out_n", "latch_sense_p", "latch_sense_n", "tail", "reset",
             "vdd", "vss", "eval", "sense_p", "sense_n", "iso_tail", "vdd_active"]
    result = ["magic", "tech sky130A", "timestamp 1788726000"]
    for layer, shapes in layers.items():
        result += [f"<< {layer} >>", *shapes]
    result.append("<< labels >>")
    for index, name in enumerate(order, 1):
        layer, x, y = ports[name]
        result += [f"rlabel {layer} {x-20} {y-20} {x+20} {y+20} 0 {name}", f"port {index} nsew"]
    return "\n".join(result+["<< end >>"]) + "\n"


def main():
    out = ROOT / "evidence/aimc-simulator-adapters/balanced-latch-layout" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True, exist_ok=False)
    (out/"generator.py").write_text(Path(__file__).read_text())
    mag = out / f"{CELL}.mag"
    mag.write_text(geometry())
    pdk = Path(os.environ.get("PDK_ROOT", str(Path.home()/"eda-tools/pdks")))
    magic = Path.home()/"eda-tools/magic-8.3.682/bin/magic"
    commands = "\n".join([f"load {CELL} -force", "select top cell", "drc on", "drc catchup", "drc count", "drc listall why",
                           "extract all", "ext2spice lvs", "ext2spice hierarchy off", "ext2spice subcircuit on",
                           "ext2spice subcircuit top on", "ext2spice cthresh 0", "ext2spice rthresh 0",
                           "ext2spice -o extracted.spice", "quit -noprompt", ""])
    proc = subprocess.run([str(magic), "-dnull", "-noconsole", "-rcfile", str(pdk/"sky130A/libs.tech/magic/sky130A.magicrc")],
                          input=commands, text=True, capture_output=True, cwd=out, timeout=120,
                          env={**os.environ, "PDK_ROOT": str(pdk)})
    (out/"magic.log").write_text(proc.stdout+proc.stderr)
    (out/"commands.tcl").write_text(commands)
    counts = re.findall(r"Total DRC errors found:\s*(\d+)", proc.stdout+proc.stderr)
    extracted = out/"extracted.spice"
    report = {"status": "layout_candidate_incomplete", "drc_errors": int(counts[-1]) if counts else None,
              "magic_returncode": proc.returncode, "accepted_converter": False,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if extracted.exists():
        report["connectivity"] = audit(extracted)
        report["capacitance_export"] = audit_substrate_capacitance(out/f"{CELL}.ext", extracted)
        if (proc.returncode == 0 and report["drc_errors"] == 0 and report["connectivity"]["topology_pass"]
                and report["connectivity"]["body_ties_pass"] and report["capacitance_export"]["pass"]):
            report["status"] = "physical_preflight_pass_not_lvs_or_transient"
    report["sha256"] = {name: hashlib.sha256((out/name).read_bytes()).hexdigest()
                        for name in (f"{CELL}.mag", f"{CELL}.ext", "extracted.spice", "magic.log", "commands.tcl")
                        if (out/name).exists()}
    (out/"result.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
    print(out)


if __name__ == "__main__":
    main()
