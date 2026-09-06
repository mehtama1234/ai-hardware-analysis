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


def capture_clock_source(rise_ps,disabled=False,fall_ps=100):
    if disabled:
        return "0"
    # Preserve both 50% crossings (20.05 and 25.15 ns), rather than
    # confounding slew with capture phase or nominal clock duty cycle.
    shift=(100-rise_ps)/2000
    width=5+shift+(100-fall_ps)/2000
    return f"PULSE(0 1.8 {20+shift:.12g}n {rise_ps:.12g}p {fall_ps:.12g}p {width:.12g}n 50n)"


def internal_capture_vectors(netlist):
    ports=[]; devices=[]; caps=[]; in_header=False
    for line in netlist.splitlines():
        if line.startswith(".subckt "):
            if ports:
                raise ValueError("Require a single flat extracted cell")
            ports=line.split()[2:]; in_header=True
        elif in_header and line.startswith("+"):
            ports+=line.split()[1:]
        elif line.startswith("XCHARGE"):
            fields=line.split()
            if len(fields)!=6 or fields[3:]!=["sky130_fd_pr__cap_mim_m3_1","l=2","w=2"]:
                raise ValueError("Unexpected modeled capacitor")
            caps.append(fields[0].lower())
        elif line.startswith("X"):
            in_header=False; devices.append(line.split()[1:5])
    if len(devices)!=40 or len(ports)!=19:
        raise ValueError("Unexpected combined extraction topology")
    if caps and sorted(caps)!=[f"xcharge{i}" for i in range(4)]:
        raise ValueError("Incomplete modeled capacitor coverage")
    internal=sorted({node for terminals in devices for node in terminals}-set(ports)-{"0"})
    return [f"v(xu.{node.lower()})" for node in internal]+[f"v(xu.{cap}.{node})" for cap in caps for node in ("a","b1")]


def add_internal_charge_caps(netlist,cap_ff,modeled=False):
    """Exploratory capacitance at four floating series-stack nodes."""
    selected=(("a_1561_36413#","vdd_capture"),("a_1975_36413#","vdd_capture"),
              ("a_1592_36047#","vss"),("a_2017_36047#","vss"))
    vectors=internal_capture_vectors(netlist)
    if cap_ff not in (.5,1,2) or any(f"v(xu.{node})" not in vectors for node,_ in selected):
        raise ValueError("Unsupported charge-cap topology/value")
    lines=netlist.splitlines()
    ends=[i for i,line in enumerate(lines) if line.lower().startswith(".ends")]
    if len(ends)!=1 or "CCHARGE" in netlist or "XCHARGE" in netlist:
        raise ValueError("Unexpected subcircuit boundary or duplicate intervention")
    additions=[f"CCHARGE{i} {node} {rail} {cap_ff:g}f" for i,(node,rail) in enumerate(selected)]
    if modeled:
        additions=[f"XCHARGE{i} {node} {rail} sky130_fd_pr__cap_mim_m3_1 l=2 w=2" for i,(node,rail) in enumerate(selected)]
    lines[ends[0]:ends[0]]=["* Exploratory lumped caps: NOT part of source LVS extraction"]+additions
    return "\n".join(lines)+"\n"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--disable-capture-clock",action="store_true",help="Negative control: retain expected decisions but hold capture clock low")
    parser.add_argument("--combined-layout",type=Path,help="Use a verified 40-device combined extraction instead of ideal interconnect")
    parser.add_argument("--capture-rise-ps",type=float,choices=(100,500,1000),default=100,
                        help="Vary rise slew while keeping nominal 50%% capture crossing fixed")
    parser.add_argument("--capture-fall-ps",type=float,choices=(100,500,1000),default=100,
                        help="Vary fall slew while keeping falling 50%% crossing at 25.15 ns")
    parser.add_argument("--max-step-ps",type=float,choices=(2.5,5,10,20),default=None)
    parser.add_argument("--reltol",type=float,choices=(1e-4,1e-5),default=1e-4)
    parser.add_argument("--timeout-s",type=int,choices=(300,600),default=300)
    parser.add_argument("--receiver-n-load-ff",type=float,choices=(2,20,100),default=2,
                        help="External lumped rx_n load diagnostic; not added extracted layout")
    parser.add_argument("--internal-charge-cap-ff",type=float,choices=(0,.5,1,2),default=0,
                        help="Schematic-only four-node charge-cap intervention; invalidates combined-layout claim")
    parser.add_argument("--modeled-charge-caps",action="store_true",help="Four installed MIM capacitor models at verified 2 um dimensions; schematic integration only")
    args=parser.parse_args()
    if args.modeled_charge_caps and args.internal_charge_cap_ff:
        parser.error("Choose modeled or ideal charge caps, not both")
    charge_modified=bool(args.internal_charge_cap_ff or args.modeled_charge_caps)
    if charge_modified and not args.combined_layout:
        parser.error("Internal charge caps require the combined capture source")
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
    cap_includes=[]; cap_probe=None
    if args.modeled_charge_caps:
        cap_probe=EVIDENCE/"capture-charge-cap-model/20260906T223811603512Z"
        probe=json.loads((cap_probe/"result.json").read_text())
        if not probe["nominal_formula_agreement"]:
            raise ValueError("Missing capacitor model preflight")
        models.update(probe["model_file_sha256"])
        cap_includes=[name for name in probe["model_file_sha256"] if Path(name).name in
                      ("res_typical__cap_typical.spice","res_typical__cap_typical__lin.spice","sky130_fd_pr__cap_mim_m3_1.model.spice")]
        if len(cap_includes)!=3:
            raise ValueError("Capacitor include coverage mismatch")
    for name,digest in models.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:
            raise ValueError("PDK model changed")
    out=EVIDENCE/"latch-capture-integration"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    for name,source in (("circuit.spice",LATCH/"circuit.spice"),("cell.spice",CAPTURE/"cell.spice"),
                        (".spiceinit",LATCH/".spiceinit"),("runner.py",Path(__file__))):
        shutil.copy2(source,out/name)
    combined=None
    if args.combined_layout:
        combined=args.combined_layout.resolve()
        physical=json.loads((combined/"result.json").read_text())
        if (physical["status"]!="capture_combined_drc_lvs_pass_not_transient" or physical["source_analog"]!=lc["combined_layout"]
                or physical["source_capture_reference"]!=str(CAPTURE)):
            raise ValueError("Combined physical/source identity mismatch")
        for name in ("combined_latch_capture.mag","extracted.spice","reference.spice"):
            if hashlib.sha256((combined/name).read_bytes()).hexdigest()!=physical["sha256"][name]:
                raise ValueError("Combined physical artifact changed")
        shutil.copy2(combined/"extracted.spice",out/"circuit.spice")
        shutil.copy2(combined/"result.json",out/"physical_source.json")
    if charge_modified:
        shutil.copy2(out/"circuit.spice",out/"source_extracted.spice")
        (out/"circuit.spice").write_text(add_internal_charge_caps((out/"circuit.spice").read_text(),args.internal_charge_cap_ff or 1,args.modeled_charge_caps))
    deck=(LATCH/"deck.spice").read_text().replace(str(LATCH/"circuit.spice"),str(out/"circuit.spice"))
    deck=replace_line(deck,".temp ",".temp 25")
    deck=replace_line(deck,"CRXn ",f"CRXn rx_n vss {args.receiver_n_load_ff:.12g}f")
    deck=replace_line(deck,".options ",f".options method=gear reltol={args.reltol:.12g} abstol=1e-14 vntol=1e-7")
    if args.max_step_ps is not None:
        deck=replace_line(deck,".tran ",f".tran 20p 200n 0 {args.max_step_ps:.12g}p")
    includes="".join(f'.include "{name}"\n' for name in models if "pfet_01v8_hvt" in name)
    includes+="".join(f'.include "{name}"\n' for name in cap_includes)
    capture_clock=capture_clock_source(args.capture_rise_ps,args.disable_capture_clock,args.capture_fall_ps)
    extra=includes+f'''.include "{out/'cell.spice'}"
VDCAP vdd_capture 0 1.8
VCAP capture_clk 0 {capture_clock}
XCAP capture_clk rx_n vss vss vdd_capture vdd_capture captured_q sky130_fd_sc_hd__dfxtp_1
CCAP captured_q vss 2f
'''
    if combined:
        extra=extra.replace(f'.include "{out/"cell.spice"}"\n',"")
        extra=replace_line(extra,"XCAP ","* Capture transistors are part of the combined extraction")
        deck=replace_line(deck,"XU ","XU out_p out_n latch_sense_p latch_sense_n tail reset vdd vss eval sense_p sense_n iso_tail vdd_active rx_p rx_n eq_reset capture_clk captured_q vdd_capture combined_latch_capture")
    deck=deck.replace(".tran 20p",extra+".tran 20p",1)
    vectors=["v(out_p)","v(out_n)","v(latch_sense_p)","v(latch_sense_n)","v(iso_tail)","v(tail)",
             "v(reset)","v(eval)","v(eq_reset)","v(rx_p)","v(rx_n)","v(capture_clk)","v(captured_q)",
             "v(sense_p)","v(sense_n)","i(vdd)","i(vactive)","i(vdcap)","i(vcap)","i(vreset)","i(veval)","i(veqreset)","i(vp)","i(vn)"]
    internal_vectors=internal_capture_vectors((out/"circuit.spice").read_text()) if combined else []
    vectors+=internal_vectors
    deck=replace_line(deck,"write waveform.raw ","write waveform.raw "+" ".join(vectors))
    (out/"deck.spice").write_text(deck)
    contract={"source_latch":str(LATCH),"source_capture":str(CAPTURE),"temperature_c":25,"corner":"tt","mismatch_enabled":False,
              "input_diffs_mv":lc["input_diffs_mv"],"period_ns":50,"expected_bits":[0,1,0,1],
              "capture_offset_ns":20,"capture_clock_rise_ps":args.capture_rise_ps,"capture_50pct_ns":20.05,"d_check_offset_ns":[19,21],
              "capture_clock_fall_ps":args.capture_fall_ps,"capture_fall_50pct_ns":25.15,
              "internal_voltage_observables":internal_vectors,
              "external_receiver_n_load_ff":args.receiver_n_load_ff,
              "solver":{"method":"gear","reltol":args.reltol,"abstol":1e-14,"vntol":1e-7,
                        "max_step_ps":args.max_step_ps,"timeout_s":args.timeout_s},
              "negative_control_capture_clock_disabled":args.disable_capture_clock,
              "combined_layout":str(combined) if combined else None,
              "combined_layout_lvs_verified":bool(combined) and not charge_modified,
              "source_combined_layout_lvs_verified":bool(combined),
              "internal_charge_cap_ff":args.internal_charge_cap_ff,
              "modeled_charge_caps":args.modeled_charge_caps,"capacitor_model_probe":str(cap_probe) if cap_probe else None,
              "q_check_windows_ns":[[22,69],[72,119],[122,169],[172,199]],
              "clock_input_current_observables_saved":True,"model_file_sha256":models,
              "sha256":{name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ("deck.spice","circuit.spice","cell.spice","runner.py",".spiceinit")},
              "boundary":"Extracted 16-device latch/receiver plus 24-device installed-library DFF, ideal interconnect and clocks. Original 2 fF rx loads are retained in addition to actual DFF input loading. Q has 2 fF external load. No combined-layout LVS/extraction, qualified converter or hardware execution; analog source changes from 27 C to common 25 C."}
    if combined:
        contract["boundary"]="Single DRC/LVS-verified 40-device capture/latch extraction including routed interconnect capacitance; no distributed-R signoff. Ideal clocks/bias/supplies; external rx_p/Q loads 2 fF, rx_n load specified separately (lumped, not extracted). TT/25 C nominal only, no qualified converter or hardware execution."
    elif args.receiver_n_load_ff!=2:
        contract["boundary"]+=f" Diagnostic override: external rx_n load is {args.receiver_n_load_ff:g} fF instead of 2 fF."
    if charge_modified:
        contract["boundary"]="Exploratory schematic augmentation of verified 40-device extraction: four added ideal internal charge capacitors. Modified circuit has NO matching DRC/LVS layout. Ideal clocks, rails and external loads remain; no converter qualification or hardware execution."
        contract["sha256"]["source_extracted.spice"]=hashlib.sha256((out/"source_extracted.spice").read_bytes()).hexdigest()
        if args.modeled_charge_caps:
            contract["boundary"]="Schematic integration of unchanged 40-device extraction plus four installed 2x2 um MIM models and their series resistors. Capacitor-only DRC/LVS exists; combined modified layout does NOT. Capacitor routing/substrate parasitics omitted. Ideal clocks/supplies remain. No converter or hardware qualification."
    (out/"contract.json").write_text(json.dumps(contract,indent=2)+"\n")
    result={"status":"integration_incomplete","accepted_converter":False}
    try:
        proc=subprocess.run(["ngspice","-b","-o","simulator.log","deck.spice"],cwd=out,text=True,capture_output=True,timeout=args.timeout_s)
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
