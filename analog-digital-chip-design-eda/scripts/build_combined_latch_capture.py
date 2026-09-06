#!/usr/bin/env python3
"""Route the existing latch/receiver layout to an installed physical DFF cell."""
from collections import defaultdict
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from audit_isolated_latch_connectivity import audit_substrate_capacitance

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"evidence/aimc-simulator-adapters"
ANALOG=EVIDENCE/"combined-latch-receiver/20260906T211728514831Z"
CAPTURE=EVIDENCE/"decision-capture-cell/20260906T215435738569Z"
PDK=Path("/home/mehtama1/eda-tools/pdks/sky130A")
CELL="combined_latch_capture"


def geometry(analog,capture):
    layers=defaultdict(list); labels=[]
    for source,dx,dy,keep in ((analog,0,0,True),(capture,1000,36000,False)):
        if "magscale 1 2" not in source:
            raise ValueError("Expected 0.005 um drawing grid")
        section=None
        for line in source.splitlines():
            if line.startswith("<< "):
                section=line[3:-3]
            elif line.startswith("rect ") and section not in ("checkpaint","properties"):
                x1,y1,x2,y2=map(int,line.split()[1:]); layers[section].append(f"rect {x1+dx} {y1+dy} {x2+dx} {y2+dy}")
            elif keep and line.startswith(("rlabel ","port ")):
                labels.append(line)
    def rect(layer,x1,y1,x2,y2):
        layers[layer].append(f"rect {x1} {y1} {x2} {y2}")
    def wire(x1,y1,x2,y2):
        if x1!=x2 and y1!=y2:
            raise ValueError("Manhattan M2 required")
        rect("metal2",min(x1,x2)-20,min(y1,y2)-20,max(x1,x2)+20,max(y1,y2)+20)
    def m1_to_m2(x,y,from_locali=False):
        if from_locali:
            rect("viali",x-17,y-17,x+17,y+17)
        rect("metal1",x-36,y-26,x+36,y+26)
        rect("via1",x-26,y-26,x+26,y+26)
        rect("metal2",x-26,y-36,x+26,y+36)
    # Explicit source-pin coordinates from the installed cell's physical labels.
    for name,layer,x,y in (("D","locali",306,238),("CLK","locali",46,238),("Q","locali",1407,102)):
        pattern=rf"^flabel {layer} s {x-17} {y-17} {x+17} {y+17} .* {name}$"
        if not re.search(pattern,capture,re.M):
            raise ValueError(f"Installed capture pin moved: {name}")
        m1_to_m2(x+1000,y+36000,True)
    m1_to_m2(1600,14500)
    wire(1600,14500,1600,36238); wire(1306,36238,1600,36238)
    wire(1046,36238,400,36238); wire(2407,36102,2800,36102)
    m1_to_m2(1046,36000); wire(1046,36000,600,36000); wire(600,34000,600,36000)
    m1_to_m2(1046,36544); wire(1046,36544,400,36544)
    # The standard-cell VPB port is a well connection, not an internal tap.
    # Extend that well and add a real n+ contact to the capture supply rail.
    rect("nwell",2400,36261,3400,36800)
    for layer in ("nsubdiff","nsubdiffcont","locali","viali","metal1"):
        rect(layer,2940,36444,3060,36644)
    rect("metal1",1046,36514,3000,36574)
    for index,name,x,y in ((17,"capture_clk",400,36238),(18,"captured_q",2800,36102),(19,"vdd_capture",400,36544)):
        labels += [f"rlabel metal2 {x-10} {y-10} {x+10} {y+10} 0 {name}",f"port {index} nsew"]
    lines=["magic","tech sky130A","magscale 1 2","timestamp 1788733000"]
    for layer,rects in layers.items():
        lines += [f"<< {layer} >>",*rects]
    return "\n".join(lines+["<< labels >>",*labels,"<< end >>"])+"\n"


def main():
    physical=json.loads((ANALOG/"result.json").read_text())
    if physical["status"]!="combined_drc_lvs_pass_not_transient" or not physical["internal_equalizer"]:
        raise ValueError("Analog physical source not verified")
    for name in ("combined_latch_receiver.mag","reference.spice"):
        if hashlib.sha256((ANALOG/name).read_bytes()).hexdigest()!=physical["sha256"][name]:
            raise ValueError("Analog source changed")
    cc=json.loads((CAPTURE/"contract.json").read_text())
    if hashlib.sha256((CAPTURE/"cell.spice").read_bytes()).hexdigest()!=cc["sha256"]["cell.spice"]:
        raise ValueError("Capture reference changed")
    capture_mag=PDK/"libs.ref/sky130_fd_sc_hd/mag/sky130_fd_sc_hd__dfxtp_1.mag"
    out=EVIDENCE/"combined-latch-capture"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(Path(__file__),out/"generator.py"); shutil.copy2(capture_mag,out/"source_capture.mag")
    (out/f"{CELL}.mag").write_text(geometry((ANALOG/"combined_latch_receiver.mag").read_text(),capture_mag.read_text()))
    reference=(ANALOG/"reference.spice").read_text().replace("combined_latch_receiver",CELL)
    reference=reference.replace("rx_p rx_n eq_reset\n","rx_p rx_n eq_reset capture_clk captured_q vdd_capture\n",1)
    reference=reference.replace(f".ends {CELL}","XCAP capture_clk rx_n vss vss vdd_capture vdd_capture captured_q sky130_fd_sc_hd__dfxtp_1\n"+f".ends {CELL}")
    (out/"reference.spice").write_text(reference+"\n"+(CAPTURE/"cell.spice").read_text())
    commands="\n".join([f"load {CELL} -force","select top cell","drc on","drc catchup","drc count","drc listall why",
        "extract all","ext2spice lvs","ext2spice hierarchy off","ext2spice subcircuit on","ext2spice subcircuit top on",
        "ext2spice cthresh 0","ext2spice rthresh 0","ext2spice -o extracted.spice","quit -noprompt",""])
    (out/"commands.tcl").write_text(commands)
    env={**os.environ,"PDK_ROOT":str(PDK.parent)}
    proc=subprocess.run(["/home/mehtama1/eda-tools/magic-8.3.682/bin/magic","-dnull","-noconsole","-rcfile",str(PDK/"libs.tech/magic/sky130A.magicrc")],
                        input=commands,text=True,capture_output=True,cwd=out,env=env,timeout=120)
    (out/"magic.log").write_text(proc.stdout+proc.stderr)
    counts=re.findall(r"Total DRC errors found:\s*(\d+)",proc.stdout+proc.stderr)
    extracted=(out/"extracted.spice").read_text()
    (out/"lvs_devices.spice").write_text("\n".join(line for line in extracted.splitlines() if not line.lower().startswith("c"))+"\n")
    setup=PDK/"libs.tech/netgen/sky130A_setup.tcl"
    lvs=subprocess.run(["/home/mehtama1/eda-tools/netgen-1.5/bin/netgen","-batch","lvs",f"{out/'lvs_devices.spice'} {CELL}",
        f"{out/'reference.spice'} {CELL}",str(setup),str(out/"netgen.log")],text=True,capture_output=True,cwd=out,env=env,timeout=60)
    (out/"netgen_stdout.log").write_text(lvs.stdout+lvs.stderr)
    log=(out/"netgen.log").read_text(); drc=int(counts[-1]) if counts else None
    match=lvs.returncode==0 and "Final result: Circuits match uniquely." in log and "Property errors were found" not in log
    caps=audit_substrate_capacitance(out/f"{CELL}.ext",out/"extracted.spice",("out_p","out_n","rx_n","captured_q"))
    passed=proc.returncode==0 and drc==0 and match and caps["pass"]
    result={"status":"capture_combined_drc_lvs_pass_not_transient" if passed else "capture_combined_physical_fail",
            "drc_errors":drc,"lvs_pass":match,"capacitance_export":caps,"accepted_converter":False,
            "source_analog":str(ANALOG),"source_capture_reference":str(CAPTURE),"source_capture_mag_sha256":hashlib.sha256(capture_mag.read_bytes()).hexdigest(),
            "expected_mos_count":40,"sha256":{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in
                (f"{CELL}.mag",f"{CELL}.ext","extracted.spice","reference.spice","generator.py","netgen.log","magic.log")},
            "boundary":"Physical connection and capacitive export candidate; no extracted transient, distributed interconnect-R, timing or converter qualification."}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
