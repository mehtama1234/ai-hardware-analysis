#!/usr/bin/env python3
"""Nominal SKY130-switch R-2R reference experiment; no layout qualification."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

import numpy as np
from run_active_converter_macro_extracted_transient import selected_model_header,PDK_ROOT


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def circuit(initial,final=None,capacitance=100e-15,load=1e12):
    lines=["* Candidate 8-bit reference DAC: ideal resistors, SKY130 transmission gates.",
           selected_model_header(),".temp 27","VDD vdd 0 1.8","VREF ref 0 1.2"]
    for bit in range(8):
        before=(initial>>(7-bit))&1
        after=before if final is None else (final>>(7-bit))&1
        for suffix,invert in [("",False),("bar",True)]:
            a,b=((1-before)*1.8,(1-after)*1.8) if invert else (before*1.8,after*1.8)
            value=f"{a:.12g}" if a==b else f"PULSE({a:.12g} {b:.12g} 20n 100p 100p 1u 2u)"
            lines.append(f"VB{bit}{suffix} b{bit}{suffix} 0 {value}")
        for label,gate,terminal,model,width,bulk in [
            ("hn",f"b{bit}","ref","nfet",4,0),("hp",f"b{bit}bar","ref","pfet",8,"vdd"),
            ("ln",f"b{bit}bar",0,"nfet",4,0),("lp",f"b{bit}",0,"pfet",8,"vdd")]:
            lines.append(f"X{bit}{label} bit{bit} {gate} {terminal} {bulk} sky130_fd_pr__{model}_01v8 w={width} l=0.15")
        lines.append(f"Rbranch{bit} n{bit} bit{bit} 20000")
        if bit<7:lines.append(f"Rseries{bit} n{bit} n{bit+1} 10000")
    lines += ["Rterminate n7 0 20000",f"Rload n0 0 {load:.12g}",f"Cload n0 0 {capacitance:.12g}",
              ".options reltol=1e-5 abstol=1e-14 vntol=1e-9"]
    return "\n".join(lines)+"\n"


def simulate(directory,deck,timeout=90):
    directory.mkdir(parents=True,exist_ok=False)
    path=directory/"deck.spice";path.write_text(deck)
    started=time.monotonic()
    try:
        p=subprocess.run(["ngspice","-b",str(path.resolve())],cwd=directory,capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired as error:
        (directory/"stdout.log").write_bytes(error.stdout or b"")
        (directory/"stderr.log").write_bytes(error.stderr or b"")
        raise RuntimeError(f"Simulation timeout: {directory}") from error
    (directory/"stdout.log").write_text(p.stdout);(directory/"stderr.log").write_text(p.stderr)
    if p.returncode!=0:raise RuntimeError(f"ngspice failed in {directory}; inspect logs")
    return p.stdout,{"returncode":p.returncode,"wall_seconds":time.monotonic()-started,"deck_sha256":digest(path)}


def transfer_deck(codes,load):
    control=[".control","set numdgt=15"]
    for code in codes:
        for bit in range(8):
            value=((code>>(7-bit))&1)*1.8
            control += [f"alter VB{bit} = {value:.12g}",f"alter VB{bit}bar = {1.8-value:.12g}"]
        control += ["op",f"echo REF_CODE_{code}","print v(n0) i(VREF) i(VDD)"]
    control += ["quit",".endc",".end"]
    return circuit(0,load=load)+"\n".join(control)+"\n"


def parse_transfer(log,codes):
    blocks=re.findall(r"REF_CODE_(\d+)\s*\n(.*?)(?=REF_CODE_|\Z)",log,re.S)
    rows=[]
    for code,block in blocks:
        values={}
        for name in ["v(n0)","i(vref)","i(vdd)"]:
            match=re.search(r"(?mi)^"+re.escape(name)+r"\s*=\s*([-+0-9.eE]+)",block)
            if not match:raise ValueError(f"Missing {name} at code {code}")
            values[name]=float(match.group(1))
        rows.append({"code":int(code),"output_v":values["v(n0)"],"reference_source_current_a":values["i(vref)"],
                     "reference_source_static_power_w":-1.2*values["i(vref)"],"vdd_source_current_a":values["i(vdd)"]})
    if [r['code'] for r in rows]!=codes:raise ValueError("Missing or duplicated transfer samples")
    if not all(np.isfinite(r['output_v']) for r in rows):raise ValueError("Nonfinite transfer")
    return rows


def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    for name in [Path(__file__).name,"run_active_converter_macro_extracted_transient.py"]:
        shutil.copy2(Path(__file__).with_name(name),args.output/name)
    codes=[0,26,127,128,255] if args.smoke else list(range(256))
    protocol={"kind":"nominal_schematic_characterization","switch_corner":"SKY130 TT","temperature_c":27,
              "vdd_v":1.8,"reference_source_v":1.2,"bits":8,"R_ohms":10000,"two_R_ohms":20000,
              "switch_nfet_w_l_um":[4,.15],"switch_pfet_w_l_um":[8,.15],"switch_transistors":32,
              "dc_loads_ohm":[1e12,1e6],"transient_load_capacitances_f":[10e-15,100e-15,1e-12],
              "transitions":[[26,255],[255,26],[127,128]],"code_transition_s":20e-9,"edge_s":100e-12,
              "settling_fraction_of_target_reference":1/4094,"settling_rationale":"half of one symmetric signed 12-bit ADC full-scale code step",
              "excluded":["extracted layout parasitics","resistor process/tolerance/noise","mismatch/PVT sweep","reference buffer",
                          "actual ADC reference loading","gate-driver loss","array and inference execution"],
              "claim":"Circuit experiment values; not assigned to the unresolved physical array target", "smoke":args.smoke}
    (args.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    transfers=[]
    for load in protocol['dc_loads_ohm']:
        print(f"DC transfer at load {load:g} ohm",flush=True)
        log,meta=simulate(args.output/f'dc-{load:g}',transfer_deck(codes,load))
        rows=parse_transfer(log,codes)
        full=next(r['output_v'] for r in rows if r['code']==255)
        for row in rows:row['normalized_to_code255']=row['output_v']/full
        transfers.append({'load_ohm':load,'simulation':meta,'rows':rows,'code255_output_v':full,
                          'monotonic':all(b['output_v']>a['output_v'] for a,b in zip(rows,rows[1:]))})
    transients=[]
    if not args.smoke:
        target={r['code']:r['output_v'] for r in transfers[0]['rows']}
        for cap in protocol['transient_load_capacitances_f']:
            for before,after in protocol['transitions']:
                print(f"Transient {before}->{after}, C={cap:g} F",flush=True)
                directory=args.output/f'tran-{before}-{after}-{cap:g}'
                deck=circuit(before,after,capacitance=cap)+".tran 20p 220n\n.control\nset numdgt=15\nset wr_singlescale\nset wr_vecnames\nrun\nwrdata waveform.txt v(n0)\nquit\n.endc\n.end\n"
                _,meta=simulate(directory,deck)
                data=np.loadtxt(directory/'waveform.txt',skiprows=1)
                times,volts=data[:,0],data[:,1]
                tolerance=abs(target[after])/4094
                active=np.flatnonzero(times>=20.1e-9)
                outside=active[np.abs(volts[active]-target[after])>tolerance]
                first=(outside[-1]+1) if len(outside) else active[0]
                settled=first<len(times)
                transients.append({'from_code':before,'to_code':after,'load_capacitance_f':cap,'simulation':meta,
                                   'target_v':target[after],'tolerance_v':tolerance,'settled_within_observation':bool(settled),
                                   'sampled_settling_after_edge_s':float(times[first]-20.1e-9) if settled else None,
                                   'final_error_v':float(volts[-1]-target[after]),'waveform_samples':len(times)})
    result={'schema_version':'switched_reference_dac_characterization.v1','protocol':protocol,
            'transfers':transfers,'transients':transients,'physical_converter_qualified':False,'analog_authorized':False,
            'claim_boundary':'Nominal SKY130-switch schematic with ideal resistors and assumed loads. No extracted circuit, full ADC, silicon or inference qualification.'}
    (args.output/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    # Preserve all directly and transitively included local PDK sources.
    pending=[PDK_ROOT/'sky130A/libs.tech/ngspice/all.spice']
    pending += [Path(s) for s in re.findall(r'\.include\s+"([^"]+)"',selected_model_header())]
    model_hashes={}
    while pending:
        path=pending.pop().resolve()
        if str(path) in model_hashes:continue
        model_hashes[str(path)]=digest(path)
        for name in re.findall(r'(?mi)^\s*\.include\s+"?([^"\s]+)',path.read_text()):
            child=Path(name);child=child if child.is_absolute() else path.parent/child
            if child.is_file():pending.append(child)
    (args.output/'model_sources.json').write_text(json.dumps(model_hashes,indent=2)+'\n')
    (args.output/'manifest.json').write_text(json.dumps({str(p.relative_to(args.output)):digest(p) for p in args.output.rglob('*') if p.is_file()},indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'dc_cases':sum(len(t['rows']) for t in transfers),'transient_cases':len(transients)}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--smoke',action='store_true')
    run(p.parse_args())
