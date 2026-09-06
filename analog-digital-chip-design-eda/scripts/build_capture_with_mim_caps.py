#!/usr/bin/env python3
"""Explore a routed four-MIM revision; retain all physical failures."""
from collections import defaultdict
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from run_latch_capture_integration import add_internal_charge_caps

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"evidence/aimc-simulator-adapters"
SOURCE=E/"combined-latch-capture/20260906T220543571833Z"
CAP=E/"capture-charge-cap/20260906T223826369432Z"
PDK=Path("/home/mehtama1/eda-tools/pdks/sky130A")
CELL="combined_latch_capture"


def geometry(source,cap):
    layers=defaultdict(list); labels=[]
    for text,dx,dy,keep in [(source,0,0,True)]+[(cap,x,y,False) for x,y in ((1000,39000),(2500,39000),(1000,33000),(2500,33000))]:
        if "magscale 1 2" not in text:
            raise ValueError("Unexpected drawing grid")
        section=None
        for line in text.splitlines():
            if line.startswith("<< "):
                section=line[3:-3]
            elif line.startswith("rect ") and section not in ("checkpaint","properties"):
                x1,y1,x2,y2=map(int,line.split()[1:]); layers[section].append(f"rect {x1+dx} {y1+dy} {x2+dx} {y2+dy}")
            elif keep and line.startswith(("rlabel ","port ")):
                labels.append(line)
    def rect(layer,x1,y1,x2,y2):
        layers[layer].append(f"rect {x1} {y1} {x2} {y2}")
    def wire(layer,x1,y1,x2,y2,width=60):
        if x1!=x2 and y1!=y2:
            raise ValueError("Non-Manhattan wire")
        h=width//2; rect(layer,min(x1,x2)-h,min(y1,y2)-h,max(x1,x2)+h,max(y1,y2)+h)
    def via2(x,y):
        rect("metal2",x-40,y-40,x+40,y+40)
        rect("via2",x-20,y-20,x+20,y+20)
        rect("metal3",x-40,y-40,x+40,y+40)
    # Extend uncontacted diffusion beyond the native LI crossings before
    # adding contacts. Never place a contact directly on a crossed LI net.
    rect("nwell",1500,36400,2130,36850)
    rect("pwell",1500,35650,2150,36120)
    for x in (1598,2017):
        rect("pdiff",x-29,36450,x+29,36729)
    for x in (1626,2050):
        rect("ndiff",x-29,35771,x+29,36085)
    targets=[(1598,36700,"pdiffc",1000,39000),(2017,36700,"pdiffc",2500,39000),
             (1626,35800,"ndiffc",1000,33000),(2050,35800,"ndiffc",2500,33000)]
    for x,y,contact,cx,cy in targets:
        rect(contact,x-17,y-17,x+17,y+17)
        rect("locali",x-17,y-17,x+17,y+17)
        rect("viali",x-17,y-17,x+17,y+17)
        if x==1626:
            wire("metal1",x,y,x+100,y,40)
            x+=100
        rect("metal1",x-36,y-26,x+36,y+26)
        rect("via1",x-26,y-26,x+26,y+26)
        rect("metal2",x-26,y-36,x+26,y+36)
        via2(x,y)
        rect("via3",x-32,y-32,x+32,y+32)
        rect("metal3",x-48,y-48,x+48,y+48)
        rect("metal4",x-48,y-48,x+48,y+48)
        elbow=cy-600 if cy>y else cy+600
        wire("metal4",x,y,x,elbow)
        wire("metal4",x,elbow,cx-146,elbow)
        wire("metal4",cx-146,elbow,cx-146,cy)
    # Bottom plate access is the native capacitor's M3-to-M4 contact at dx+334.
    # Supply routes remain on M3; signal routes use M4.
    via2(400,36544); wire("metal3",400,36544,400,39000)
    wire("metal3",400,39000,2834,39000)
    via2(600,34000); wire("metal3",600,34000,5000,34000)
    wire("metal3",5000,34000,5000,33000); wire("metal3",1334,33000,5000,33000)
    lines=["magic","tech sky130A","magscale 1 2","timestamp 1788735000"]
    for layer,rects in layers.items():
        lines += [f"<< {layer} >>",*rects]
    return "\n".join(lines+["<< labels >>",*labels,"<< end >>"])+"\n"


def main():
    for path in (SOURCE,CAP):
        r=json.loads((path/"result.json").read_text())
        if r["drc_errors"]!=0 or not r.get("lvs_pass",r.get("lvs_unique_match")):
            raise ValueError("Unverified physical source")
        for name,digest in r["sha256"].items():
            if hashlib.sha256((path/name).read_bytes()).hexdigest()!=digest:
                raise ValueError("Changed physical source artifact")
    out=E/"capture-with-mim-layout"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False); shutil.copy2(__file__,out/"builder.py")
    (out/f"{CELL}.mag").write_text(geometry((SOURCE/f"{CELL}.mag").read_text(),(CAP/"capture_charge_cap.mag").read_text()))
    reference=add_internal_charge_caps((SOURCE/"extracted.spice").read_text(),1,True)
    reference="\n".join(line for line in reference.splitlines() if not line.startswith("C"))+"\n"
    (out/"reference.spice").write_text(reference)
    cmds="\n".join([f"load {CELL} -force","drc on","drc catchup","drc count","drc listall why","extract all",
        "ext2spice lvs","ext2spice hierarchy off","ext2spice subcircuit on","ext2spice subcircuit top on",
        "ext2spice cthresh 0","ext2spice rthresh 0","ext2spice -o extracted.spice","quit -noprompt",""])
    (out/"commands.tcl").write_text(cmds)
    env={**os.environ,"PDK_ROOT":str(PDK.parent)}
    p=subprocess.run(["/home/mehtama1/eda-tools/magic-8.3.682/bin/magic","-dnull","-noconsole","-rcfile",str(PDK/"libs.tech/magic/sky130A.magicrc")],input=cmds,text=True,capture_output=True,cwd=out,env=env,timeout=120)
    log=p.stdout+p.stderr; (out/"magic.log").write_text(log)
    counts=re.findall(r"Total DRC errors found:\s*(\d+)",log)
    net=(out/"extracted.spice").read_text()
    (out/"lvs_devices.spice").write_text("\n".join(line for line in net.splitlines() if not line.startswith("C"))+"\n")
    n=subprocess.run(["/home/mehtama1/eda-tools/netgen-1.5/bin/netgen","-batch","lvs",f"{out/'lvs_devices.spice'} {CELL}",f"{out/'reference.spice'} {CELL}",str(PDK/"libs.tech/netgen/sky130A_setup.tcl"),str(out/"lvs.log")],cwd=out,text=True,capture_output=True,timeout=120)
    (out/"netgen-console.log").write_text(n.stdout+n.stderr)
    lvs=(out/"lvs.log").read_text()
    result={"status":"physical_candidate_checked_not_transient","drc_errors":int(counts[-1]) if counts else None,
            "layout_read_errors":[line.strip() for line in log.splitlines() if "Unrecognized layer" in line or "Error" in line],
            "lvs_pass":n.returncode==0 and "Circuits match uniquely." in lvs and "Property errors were found" not in lvs,
            "source_layout":str(SOURCE),"source_capacitor":str(CAP),"accepted_converter":False,
            "sha256":{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()},
            "boundary":"Reference extends previously LVS-verified extraction with four capacitors. Physical result must be inspected; no transient, capacitance-export audit or converter qualification."}
    result["physical_pass"]=p.returncode==0 and result["drc_errors"]==0 and not result["layout_read_errors"] and result["lvs_pass"]
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)


if __name__=="__main__":
    main()
