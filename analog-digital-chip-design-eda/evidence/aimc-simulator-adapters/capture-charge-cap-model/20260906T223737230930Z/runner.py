#!/usr/bin/env python3
"""Check charge of the installed MIM model at the drawn 2 um dimensions."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PDK=Path("/home/mehtama1/eda-tools/pdks/sky130A")
SOURCE=ROOT/"evidence/aimc-simulator-adapters/capture-charge-cap/20260906T223618590469Z"


def main():
    physical=json.loads((SOURCE/"result.json").read_text())
    if physical["drc_errors"]!=0 or not physical["lvs_unique_match"]:
        raise ValueError("Capacitor physical preflight failed")
    for name,digest in physical["sha256"].items():
        if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()!=digest:
            raise ValueError("Changed physical source")
    tech=PDK/"libs.tech/ngspice"
    deps=[tech/"r+c/res_typical__cap_typical.spice",tech/"r+c/res_typical__cap_typical__lin.spice",
          PDK/"libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_mim_m3_1.model.spice"]
    out=ROOT/"evidence/aimc-simulator-adapters/capture-charge-cap-model"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False); shutil.copy2(__file__,out/"runner.py")
    shutil.copy2(SOURCE/"reference.spice",out/"cell.spice")
    # Recursively snapshot include dependencies for an auditable installed-model probe.
    import re
    seen={}
    def visit(path):
        path=path.resolve()
        if str(path) in seen:
            return
        data=path.read_bytes(); seen[str(path)]=hashlib.sha256(data).hexdigest()
        for child in re.findall(r'(?im)^\.include\s+"([^"]+)"',data.decode()):
            visit(path.parent/child)
    for dep in deps:
        visit(dep)
    deck="* Installed MIM model charge probe, not combined-circuit evidence.\n.param mc_mm_switch=0 mc_pr_switch=0\n"
    deck+="".join(f'.include "{p}"\n' for p in deps)
    deck+=f'''.include "{out/'cell.spice'}"
.temp 25
.options reltol=1e-6 abstol=1e-16 method=gear
VIN top 0 PWL(0n 0 1n 0 2n 1 4n 1)
XCAP top 0 capture_charge_cap
.tran 1p 4n 0 1p
.measure tran final_v FIND v(top) AT=4n
.control
run
write waveform.raw v(top) i(vin)
.endc
.end
'''
    (out/"deck.spice").write_text(deck)
    (out/".spiceinit").write_text("set ngbehavior=hsa\nset ng_nomodcheck\n")
    proc=subprocess.run(["ngspice","-b","-o","simulator.log","deck.spice"],cwd=out,text=True,capture_output=True,timeout=60)
    (out/"console.log").write_text(proc.stdout+proc.stderr)
    result={"status":"model_probe_incomplete","source_layout":str(SOURCE),"accepted_converter":False,"model_file_sha256":seen,
            "boundary":"Nominal installed MIM model and series resistances at l=w=2 micrometres. Does not include extracted routing/substrate capacitance or integration into capture circuit."}
    if proc.returncode==0:
        h,b=(out/"waveform.raw").read_bytes().split(b"Binary:\n",1)
        names=[line.split()[1] for line in h.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
        wave=np.frombuffer(b,dtype=np.float64).reshape(-1,len(names))
        if names!=["time","v(top)","i(vin)"] or not np.isfinite(wave).all() or wave[-1,0]<4e-9:
            raise ValueError("Invalid model waveform")
        charge=float(np.trapezoid(-wave[:,2],wave[:,0]))
        result.update(status="nominal_model_charge_measured",charge_c=charge,effective_capacitance_ff=charge/1e-15)
    else:
        result["error"]=f"ngspice returned {proc.returncode}; inspect simulator.log"
    result["sha256"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)


if __name__=="__main__":
    main()
