#!/usr/bin/env python3
"""Draw and extract one native PDK MIM capacitor, not an integrated revision."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PDK=Path("/home/mehtama1/eda-tools/pdks/sky130A")


def main():
    out=ROOT/"evidence/aimc-simulator-adapters/capture-charge-cap"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    commands="""load capture_charge_cap -force
box position 0um 0um
box size 0um 0um
sky130::sky130_fd_pr__cap_mim_m3_1_draw [sky130::sky130_fd_pr__cap_mim_m3_1_defaults]
box position -0.73um 0um
box size 0um 0um
label top 0 metal4
port make 1
box position 1.67um 0um
box size 0um 0um
label bottom 0 metal4
port make 2
save capture_charge_cap
drc on
drc catchup
drc count
drc listall why
extract all
ext2spice lvs
ext2spice hierarchy off
ext2spice subcircuit on
ext2spice subcircuit top on
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o extracted.spice
quit -noprompt
"""
    (out/"commands.tcl").write_text(commands); shutil.copy2(__file__,out/"builder.py")
    magic=Path("/home/mehtama1/eda-tools/magic-8.3.682/bin/magic")
    proc=subprocess.run([str(magic),"-dnull","-noconsole","-rcfile",str(PDK/"libs.tech/magic/sky130A.magicrc")],
                        input=commands,text=True,capture_output=True,cwd=out,timeout=120,
                        env={**os.environ,"PDK_ROOT":str(PDK.parent)})
    log=proc.stdout+proc.stderr; (out/"magic.log").write_text(log)
    counts=re.findall(r"Total DRC errors found:\s*(\d+)",log)
    extracted=(out/"extracted.spice").read_text() if (out/"extracted.spice").exists() else ""
    devices=[line for line in extracted.splitlines() if "sky130_fd_pr__cap_mim_m3_1" in line and line.startswith("X")]
    (out/"reference.spice").write_text("* Independent two-terminal 2 um square MIM capacitor.\n.subckt capture_charge_cap top bottom\nXCAP top bottom sky130_fd_pr__cap_mim_m3_1 l=2 w=2\n.ends capture_charge_cap\n")
    (out/"lvs_devices.spice").write_text("\n".join(line for line in extracted.splitlines() if not line.startswith("C"))+"\n")
    netgen=Path("/home/mehtama1/eda-tools/netgen-1.5/bin/netgen")
    lvs=subprocess.run([str(netgen),"-batch","lvs",f"{out/'lvs_devices.spice'} capture_charge_cap",
                        f"{out/'reference.spice'} capture_charge_cap",str(PDK/"libs.tech/netgen/sky130A_setup.tcl"),
                        str(out/"lvs.log")],cwd=out,text=True,capture_output=True,timeout=120)
    (out/"netgen-console.log").write_text(lvs.stdout+lvs.stderr)
    lvs_text=(out/"lvs.log").read_text() if (out/"lvs.log").exists() else ""
    matched="Circuits match uniquely." in lvs_text and lvs.returncode==0
    result={"status":"native_cap_draw_extract_diagnostic","returncode":proc.returncode,
            "drc_errors":int(counts[-1]) if counts else None,"extracted_cap_devices":devices,
            "lvs_unique_match":matched,
            "accepted_converter":False,"integrated_layout_verified":False,
            "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                             (magic,netgen,PDK/"libs.tech/netgen/sky130A_setup.tcl",PDK/"libs.tech/magic/sky130A.tcl",PDK/"libs.tech/magic/sky130A.magicrc")},
            "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()},
            "boundary":"Single native capacitor geometry; DRC and capacitor-only LVS results reported explicitly. No combined capture layout, transient or workload qualification. Extracted VSUBS connection needs explicit binding before circuit integration."}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)


if __name__=="__main__":
    main()
