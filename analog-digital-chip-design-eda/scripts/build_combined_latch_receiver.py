#!/usr/bin/env python3
"""Compose verified geometry, route receivers, and independently LVS all 15 MOS."""
from collections import defaultdict
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from audit_isolated_latch_connectivity import audit_substrate_capacitance

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/"evidence/aimc-simulator-adapters"
LATCH = EVIDENCE/"isolated-latch-v2-lvs/20260906T202553317062Z"
RECEIVER = EVIDENCE/"compact-receiver-layout/20260906T203157079188Z"
CELL = "combined_latch_receiver"


def geometry(latch, receiver, internal_equalizer=False):
    layers = defaultdict(list)
    labels = []
    def merge(source, scale, sign=1, dx=0, dy=0, keep_labels=False):
        section = None
        for line in source.splitlines():
            if line.startswith("<< "):
                section = line[3:-3]
            elif line.startswith("rect ") and section not in ("checkpaint", "properties"):
                x1,y1,x2,y2 = map(int,line.split()[1:])
                xs = sorted((x1*scale*sign+dx,x2*scale*sign+dx))
                layers[section].append(f"rect {xs[0]} {y1*scale+dy} {xs[1]} {y2*scale+dy}")
            elif keep_labels and line.startswith("rlabel "):
                p=line.split()
                for i in range(2,6):
                    p[i]=str(int(p[i])*scale)
                labels.append(" ".join(p))
            elif keep_labels and line.startswith("port "):
                labels.append(line)
    if "magscale" in latch or "magscale 1 2" not in receiver:
        raise ValueError("Source drawing grids changed")
    merge(latch,2,keep_labels=True)
    merge(receiver,1,dx=-2000,dy=14000)
    merge(receiver,1,sign=-1,dx=2000,dy=14000)
    def rect(layer,x1,y1,x2,y2):
        layers[layer].append(f"rect {x1} {y1} {x2} {y2}")
    def wire(layer,x1,y1,x2,y2):
        if x1!=x2 and y1!=y2:
            raise ValueError("Manhattan route required")
        rect(layer,min(x1,x2)-30,min(y1,y2)-30,max(x1,x2)+30,max(y1,y2)+30)
    def via(x,y,lo=1,hi=3):
        for i in range(lo,hi+1):
            rect(f"metal{i}",x-40,y-40,x+40,y+40)
            if i<hi:
                rect(f"via{i}",x-30,y-30,x+30,y+30)
    for sign,name in ((-1,"p"),(1,"n")):
        # Receiver input is already a M2 pin; latch output is a M2 trunk.
        wire("metal2",sign*2300,14500,sign*4000,14500)
        # Source/body rails: M3 crosses latch M2 buses without unintended vias.
        via(sign*2400,15000)
        wire("metal3",sign*2400,15000,sign*16000,15000)
        via(sign*16000,15000,2,3)
        # Extend the active supply bus down to this new branch landing.
        wire("metal2",sign*16000,15000,sign*16000,19460)
        via(sign*2400,14000)
        wire("metal3",sign*2400,14000,600,14000)
        labels += [f"rlabel metal1 {sign*1600-10} 14490 {sign*1600+10} 14510 0 rx_{name}",
                   f"port {14 if name=='p' else 15} nsew"]
    via(600,14000,2,3)
    wire("metal2",600,14000,600,34000)
    via(600,34000,2,3)
    wire("metal3",600,34000,-2000,34000)
    via(-2000,34000,2,3)
    if internal_equalizer:
        # Separate 1.2/0.6 um PFET bridges the two internal sense nodes.
        # Grid is 0.005 um/unit. Body is tied to the 1.8 V active rail,
        # independently of both signal terminals and the output reset rail.
        rect("nwell",-2000,2700,2000,5500)
        rect("pdiffusion",-600,4000,600,4240)
        rect("polysilicon",-60,3000,60,4600)
        for x in (-420,420):
            for layer in ("pdc","mcon"):
                rect(layer,x-120,4020,x+120,4140)
            rect("metal1",x-200,3860,x+200,4220)
            via(x,4080)
            landing=-3000 if x<0 else 3000
            wire("metal3",x,4080,landing,4080)
            via(landing,4080,2,3)
        for layer in ("pc","locali","mcon","metal1"):
            rect(layer,-60,3040,60,3160)
        via(0,3100,1,2)
        wire("metal2",0,2000,0,3100)
        labels += ["rlabel metal2 -20 1980 20 2020 0 eq_reset","port 16 nsew"]
        for layer in ("nsubdiff","nsubdiffcont","locali","viali","metal1"):
            rect(layer,1440,4900,1560,5100)
        via(1500,5000)
        wire("metal3",1500,5000,16000,5000)
        via(16000,5000,2,3)
        wire("metal2",16000,5000,16000,15000)
    result=["magic","tech sky130A","magscale 1 2","timestamp 1788726900"]
    for layer, shapes in layers.items():
        result += [f"<< {layer} >>",*shapes]
    return "\n".join(result+["<< labels >>",*labels,"<< end >>"])+"\n"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--internal-equalizer",action="store_true",
                        help="Add a separately controlled, physically drawn sense-node equalizer")
    args=parser.parse_args()
    for directory,names,status in ((LATCH,("layout.mag","reference.spice"),"lvs_pass_subblock_only"),
                                    (RECEIVER,("compact_receiver.mag","reference.spice"),"receiver_drc_lvs_pass_subblock_only")):
        report=json.loads((directory/"result.json").read_text())
        if report["status"]!=status:
            raise ValueError("Source physical verification missing")
        for name in names:
            if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=report["sha256"][name]:
                raise ValueError(f"Source geometry/reference changed: {name}")
    out=EVIDENCE/"combined-latch-receiver"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    (out/f"{CELL}.mag").write_text(geometry((LATCH/"layout.mag").read_text(),(RECEIVER/"compact_receiver.mag").read_text(),args.internal_equalizer))
    shutil.copy2(Path(__file__),out/"generator.py")
    reference=(LATCH/"reference.spice").read_text().replace("sky130_isolated_frontend_active_load_latch_v2",CELL)
    reference=reference.replace("iso_tail vdd_active\n","iso_tail vdd_active rx_p rx_n\n",1)
    extras="\n".join(f"XRXN{s} rx_{s} out_{s} vss vss sky130_fd_pr__nfet_01v8 w=0.42 l=0.15\n"
                      f"XRXP{s} rx_{s} out_{s} vdd_active vdd_active sky130_fd_pr__pfet_01v8 w=0.42 l=0.15" for s in ("p","n"))
    reference=reference.replace(f".ends {CELL}",extras+f"\n.ends {CELL}")
    if args.internal_equalizer:
        reference=reference.replace("vdd_active rx_p rx_n\n","vdd_active rx_p rx_n eq_reset\n",1)
        reference=reference.replace(f".ends {CELL}",
            "Xequalizer latch_sense_p eq_reset latch_sense_n vdd_active sky130_fd_pr__pfet_01v8 w=1.2 l=0.6\n"+f".ends {CELL}")
    (out/"reference.spice").write_text(reference)
    pdk=Path(os.environ.get("PDK_ROOT",str(Path.home()/"eda-tools/pdks")))
    commands="\n".join([f"load {CELL} -force","select top cell","drc on","drc catchup","drc count","drc listall why",
                         "extract all","ext2spice lvs","ext2spice hierarchy off","ext2spice subcircuit on",
                         "ext2spice subcircuit top on","ext2spice cthresh 0","ext2spice rthresh 0",
                         "ext2spice -o extracted.spice","quit -noprompt",""])
    (out/"commands.tcl").write_text(commands)
    proc=subprocess.run([str(Path.home()/"eda-tools/magic-8.3.682/bin/magic"),"-dnull","-noconsole","-rcfile",
                         str(pdk/"sky130A/libs.tech/magic/sky130A.magicrc")],input=commands,text=True,capture_output=True,
                        cwd=out,timeout=120,env={**os.environ,"PDK_ROOT":str(pdk)})
    (out/"magic.log").write_text(proc.stdout+proc.stderr)
    counts=re.findall(r"Total DRC errors found:\s*(\d+)",proc.stdout+proc.stderr)
    caps=audit_substrate_capacitance(out/f"{CELL}.ext",out/"extracted.spice")
    internal_caps=audit_substrate_capacitance(out/f"{CELL}.ext",out/"extracted.spice",
        ("latch_sense_p","latch_sense_n","eq_reset")) if args.internal_equalizer else None
    (out/"lvs_devices.spice").write_text("\n".join(line for line in (out/"extracted.spice").read_text().splitlines()
                                                    if not line.lower().startswith("c"))+"\n")
    setup=pdk/"sky130A/libs.tech/netgen/sky130A_setup.tcl"
    lvs=subprocess.run([str(Path.home()/"eda-tools/netgen-1.5/bin/netgen"),"-batch","lvs",
                        f"{out/'lvs_devices.spice'} {CELL}",f"{out/'reference.spice'} {CELL}",str(setup),str(out/"netgen.log")],
                       text=True,capture_output=True,cwd=out,timeout=60,env={**os.environ,"PDK_ROOT":str(pdk)})
    (out/"netgen_stdout.log").write_text(lvs.stdout+lvs.stderr)
    log=(out/"netgen.log").read_text() if (out/"netgen.log").exists() else ""
    drc=int(counts[-1]) if counts else None
    match=lvs.returncode==0 and "Final result: Circuits match uniquely." in log and "Property errors were found" not in log
    passed=proc.returncode==0 and drc==0 and caps["pass"] and match and (internal_caps is None or internal_caps["pass"])
    report={"status":"combined_drc_lvs_pass_not_transient" if passed else "combined_physical_fail",
            "drc_errors":drc,"lvs_pass":match,"output_capacitance_export":caps,"accepted_converter":False,
            "internal_equalizer":args.internal_equalizer,
            "expected_mos_count":16 if args.internal_equalizer else 15,
            "internal_capacitance_export":internal_caps,
            "source_latch":str(LATCH),"source_receiver":str(RECEIVER),
            "sha256":{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in
                      (f"{CELL}.mag",f"{CELL}.ext","extracted.spice","reference.spice","generator.py","netgen.log")}}
    (out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2)); print(out)
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
