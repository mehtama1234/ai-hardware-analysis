#!/usr/bin/env python3
"""Couple the verified latch extraction to an installed transistor capture cell.

This is a mixed-view integration diagnostic, not a combined-layout result.
"""
from datetime import datetime,timezone
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import numpy as np
from run_latch_repeated_readout import replace_line

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"evidence/aimc-simulator-adapters"
LATCH=EVIDENCE/"latch-repeated-readout/20260906T211819331198Z"
CAPTURE=EVIDENCE/"decision-capture-cell/20260906T215435738569Z"


def check_logic_window(time,values,lo_ns,hi_ns,expected):
    if expected not in (0,1) or lo_ns>=hi_ns or lo_ns*1e-9<time[0] or hi_ns*1e-9>time[-1]:
        raise ValueError("Invalid or uncovered logic window")
    grid=np.r_[lo_ns*1e-9,time[(time>lo_ns*1e-9)&(time<hi_ns*1e-9)],hi_ns*1e-9]
    sample=np.interp(grid,time,values)
    return {"window_ns":[lo_ns,hi_ns],"expected":expected,"min_v":float(sample.min()),"max_v":float(sample.max()),
            "pass":bool(np.isfinite(sample).all() and (np.all(sample>=1.62) if expected else np.all(sample<=.18)))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disable-capture-clock",action="store_true",help="Negative control: retain expected decisions but hold capture clock low")
    args=parser.parse_args()
    lc=json.loads((LATCH/"contract.json").read_text()); cc=json.loads((CAPTURE/"contract.json").read_text())
    if lc["mismatch_enabled"] or lc["input_diffs_mv"]!=[-.5,.5,-.5,.5] or lc["period_ns"]!=50:
        raise ValueError("Unexpected analog source profile")
    if not lc["combined_layout_lvs_verified"] or json.loads((CAPTURE/"result.json").read_text())["status"]!="capture_logic_diagnostic_pass":
        raise ValueError("Missing source physical/capture preflight")
    for path,contract,files in ((LATCH,lc,("circuit.spice","deck.spice",".spiceinit")),(CAPTURE,cc,("cell.spice","deck.spice",".spiceinit"))):
        for name in files:
            if hashlib.sha256((path/name).read_bytes()).hexdigest()!=contract["sha256"][name]:
                raise ValueError("Source artifact changed")
    models={**lc["effective_model_file_sha256"],**cc["model_file_sha256"]}
    for name,digest in models.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:
            raise ValueError("PDK model changed")
    out=EVIDENCE/"latch-capture-integration"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    for name,source in (("circuit.spice",LATCH/"circuit.spice"),("cell.spice",CAPTURE/"cell.spice"),
                        (".spiceinit",LATCH/".spiceinit"),("runner.py",Path(__file__))):
        shutil.copy2(source,out/name)
    deck=(LATCH/"deck.spice").read_text().replace(str(LATCH/"circuit.spice"),str(out/"circuit.spice"))
    deck=replace_line(deck,".temp ",".temp 25")
    includes="".join(f'.include "{name}"\n' for name in models if "pfet_01v8_hvt" in name)
    capture_clock="0" if args.disable_capture_clock else "PULSE(0 1.8 20n 100p 100p 5n 50n)"
    extra=includes+f'''.include "{out/'cell.spice'}"
VDCAP vdd_capture 0 1.8
VCAP capture_clk 0 {capture_clock}
XCAP capture_clk rx_n vss vss vdd_capture vdd_capture captured_q sky130_fd_sc_hd__dfxtp_1
CCAP captured_q vss 2f
'''
    deck=deck.replace(".tran 20p",extra+".tran 20p",1)
    vectors=["v(out_p)","v(out_n)","v(latch_sense_p)","v(latch_sense_n)","v(iso_tail)","v(tail)",
             "v(reset)","v(eval)","v(eq_reset)","v(rx_p)","v(rx_n)","v(capture_clk)","v(captured_q)",
             "v(sense_p)","v(sense_n)","i(vdd)","i(vactive)","i(vdcap)","i(vcap)","i(vreset)","i(veval)","i(veqreset)","i(vp)","i(vn)"]
    deck=replace_line(deck,"write waveform.raw ","write waveform.raw "+" ".join(vectors))
    (out/"deck.spice").write_text(deck)
    contract={"source_latch":str(LATCH),"source_capture":str(CAPTURE),"temperature_c":25,"corner":"tt","mismatch_enabled":False,
              "input_diffs_mv":lc["input_diffs_mv"],"period_ns":50,"expected_bits":[0,1,0,1],
              "capture_offset_ns":20,"capture_clock_rise_ps":100,"d_check_offset_ns":[19,21],
              "negative_control_capture_clock_disabled":args.disable_capture_clock,
              "q_check_windows_ns":[[22,69],[72,119],[122,169],[172,199]],
              "clock_input_current_observables_saved":True,"model_file_sha256":models,
              "sha256":{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ("deck.spice","circuit.spice","cell.spice","runner.py",".spiceinit")},
              "boundary":"Extracted 16-device latch/receiver plus 24-device installed-library DFF, ideal interconnect and clocks. Original 2 fF rx loads are retained in addition to actual DFF input loading. Q has 2 fF external load. No combined-layout LVS/extraction, qualified converter or hardware execution; analog source changes from 27 C to common 25 C."}
    (out/"contract.json").write_text(json.dumps(contract,indent=2)+"\n")
    result={"status":"integration_incomplete","accepted_converter":False}
    try:
        proc=subprocess.run(["ngspice","-b","-o","simulator.log","deck.spice"],cwd=out,text=True,capture_output=True,timeout=300)
        (out/"console.log").write_text(proc.stdout+proc.stderr)
        if proc.returncode!=0:
            raise ValueError(f"ngspice exited {proc.returncode}; inspect log")
        h,b=(out/"waveform.raw").read_bytes().split(b"Binary:\n",1)
        names=[line.split()[1] for line in h.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
        wave=np.frombuffer(b,dtype=np.float64).reshape(-1,len(names)); time=wave[:,0]
        if names!=["time"]+vectors or not np.isfinite(wave).all() or not np.all(np.diff(time)>0) or time[-1]<200e-9:
            raise ValueError("Invalid/incomplete waveform")
        rows=[]
        for index,(expected,window) in enumerate(zip(contract["expected_bits"],contract["q_check_windows_ns"])):
            rows.append({"cycle":index,"d":check_logic_window(time,wave[:,names.index("v(rx_n)")],index*50+19,index*50+21,expected),
                         "q":check_logic_window(time,wave[:,names.index("v(captured_q)")],*window,expected)})
        extrema={name:[float(wave[:,i].min()),float(wave[:,i].max())] for i,name in enumerate(names) if name.startswith("v(")}
        result.update(status="coupled_capture_logic_diagnostic_pass" if all(row["d"]["pass"] and row["q"]["pass"] for row in rows) else "coupled_capture_logic_diagnostic_fail",
                      rows=rows,node_extrema_v=extrema,strict_saved_node_envelope_pass=all(lo>=0 and hi<=1.8 for lo,hi in extrema.values()),
                      waveform_sha256=hashlib.sha256((out/"waveform.raw").read_bytes()).hexdigest())
    except (ValueError,subprocess.TimeoutExpired) as error:
        result["error"]=str(error)
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2)); print(out)
    return 0 if result["status"]=="coupled_capture_logic_diagnostic_pass" else 1


if __name__=="__main__":
    raise SystemExit(main())
