#!/usr/bin/env python3
"""Standalone installed-library transistor DFF smoke test before analog coupling."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PDK=Path("/home/mehtama1/eda-tools/pdks/sky130A")
CELL="sky130_fd_sc_hd__dfxtp_1"


def select_cell(text):
    matches=re.findall(rf"^\.subckt {CELL} .+?^\.ends[^\n]*",text,re.M|re.S)
    if len(matches)!=1 or matches[0].splitlines()[0]!=f".subckt {CELL} CLK D VGND VNB VPB VPWR Q":
        raise ValueError("Capture-cell interface changed")
    if sum(line.startswith("X") for line in matches[0].splitlines())!=24:
        raise ValueError("Capture-cell transistor count changed")
    return matches[0]+"\n"


def main():
    out=ROOT/"evidence/aimc-simulator-adapters/decision-capture-cell"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    library=PDK/"libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice"
    liberty=PDK/"libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
    source=ROOT/"evidence/aimc-simulator-adapters/isolated-latch-v2-transient/20260906T202600550851Z"
    source_result=json.loads((source/"result.json").read_text())
    models={Path(name):digest for name,digest in source_result["config"]["model_file_sha256"].items()}
    for path,digest in models.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError("PDK dependency changed")
    cell=select_cell(library.read_text())
    notice="""* Copyright 2020 The SkyWater PDK Authors
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* https://www.apache.org/licenses/LICENSE-2.0
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
* Unmodified cell selection from the installed library.
"""
    (out/"cell.spice").write_text(notice+cell)
    prefix=(source/"case-0/deck.spice").read_text().split(f'.include "{source/"circuit.spice"}"')[0]
    if ".subckt" in prefix or ".tran " in prefix:
        raise ValueError("Unexpected source model preamble")
    # The regular TT NFET file already supplies the special-NFET alias.
    # Do not load another same-named subcircuit from a standalone special file.
    nfet=PDK/"libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8__tt.pm3.spice"
    if ".subckt  sky130_fd_pr__special_nfet_01v8 d g s b" not in nfet.read_text():
        raise ValueError("Installed special-NFET alias changed")
    for filename in ("sky130_fd_pr__pfet_01v8_hvt__tt.pm3.spice",
                     "sky130_fd_pr__pfet_01v8_hvt__mismatch.corner.spice"):
        path=PDK/"libs.ref/sky130_fd_pr/spice"/filename
        models[path]=hashlib.sha256(path.read_bytes()).hexdigest()
        prefix+=f'.include "{path}"\n'
    deck=prefix+f'''
.include "{out/'cell.spice'}"
.temp 25
.options method=gear reltol=1e-4 abstol=1e-14 vntol=1e-7
VDD vdd 0 1.8
VCLK clk 0 PULSE(0 1.8 20n 100p 100p 5n 50n)
VD d 0 PWL(0n 0 51n 0 51.02n 1.8 151n 1.8 151.02n 0)
XCAP clk d 0 0 vdd vdd q {CELL}
CQ q 0 2f
.tran 20p 200n
.control
run
write waveform.raw v(clk) v(d) v(q) i(vdd) i(vclk) i(vd)
.endc
.end
'''
    (out/"deck.spice").write_text(deck)
    shutil.copy2(source/"case-0/.spiceinit",out/".spiceinit")
    shutil.copy2(Path(__file__),out/"runner.py")
    contract={"cell":CELL,"port_order":["CLK","D","VGND","VNB","VPB","VPWR","Q"],
              "corner":"tt","temperature_c":25,"mismatch_enabled":False,
              "period_ns":50,"capture_offset_ns":20,"capture_rise_ps":100,
              "q_check_windows_ns":[[22,69],[72,119],[122,169],[172,199]],
              "expected_q":[0,1,1,0],"q_low_max_v":.18,"q_high_min_v":1.62,
              "source_file_sha256":{str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (library,liberty)},
              "model_file_sha256":{str(path):digest for path,digest in models.items()},
              "sha256":{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ("cell.spice","deck.spice",".spiceinit","runner.py")},
              "boundary":"Standalone installed-library transistor cell, not combined-layout extraction, DRC/LVS, analog coupling, setup/hold characterization, PVT/mismatch qualification or implemented clock distribution."}
    (out/"contract.json").write_text(json.dumps(contract,indent=2)+"\n")
    result={"status":"capture_simulation_incomplete","accepted_converter":False}
    try:
        proc=subprocess.run(["ngspice","-b","-o","simulator.log","deck.spice"],cwd=out,capture_output=True,text=True,timeout=180)
        (out/"console.log").write_text(proc.stdout+proc.stderr)
        if proc.returncode!=0:
            raise ValueError(f"ngspice failed: {proc.returncode}; inspect simulator.log")
        h,b=(out/"waveform.raw").read_bytes().split(b"Binary:\n",1)
        names=[line.split()[1] for line in h.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
        wave=np.frombuffer(b,dtype=np.float64).reshape(-1,len(names)); t=wave[:,0]; q=wave[:,names.index("v(q)")]
        if not np.isfinite(wave).all() or not np.all(np.diff(t)>0) or t[-1]<200e-9:
            raise ValueError("Invalid or incomplete waveform")
        checks=[]
        for (lo,hi),expected in zip(contract["q_check_windows_ns"],contract["expected_q"]):
            times=np.r_[lo*1e-9,t[(t>lo*1e-9)&(t<hi*1e-9)],hi*1e-9]
            values=np.interp(times,t,q)
            checks.append({"window_ns":[lo,hi],"expected_q":expected,"min_q_v":float(values.min()),"max_q_v":float(values.max()),
                           "pass":bool(np.all(values>=1.62) if expected else np.all(values<=.18))})
        result.update(status="capture_logic_diagnostic_pass" if all(row["pass"] for row in checks) else "capture_logic_diagnostic_fail",checks=checks,
                      q_extrema_v=[float(q.min()),float(q.max())],strict_q_envelope_pass=bool(np.all((q>=0)&(q<=1.8))),
                      waveform_sha256=hashlib.sha256((out/"waveform.raw").read_bytes()).hexdigest())
    except (ValueError,subprocess.TimeoutExpired) as error:
        result["error"]=str(error)
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)
    return 0 if result["status"]=="capture_logic_diagnostic_pass" else 1


if __name__=="__main__":
    raise SystemExit(main())
