#!/usr/bin/env python3
"""Integrate the two saved supply currents; explicitly exclude unsaved drivers."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def integrate_power(time,power,start,stop):
    if start<time[0] or stop>time[-1] or stop<=start:
        raise ValueError("Integration interval must be fully covered")
    t=np.r_[start,time[(time>start)&(time<stop)],stop]
    p=np.interp(t,time,power)
    crossings=np.flatnonzero(p[:-1]*p[1:]<0)
    zero_times=t[crossings]-p[crossings]*(t[crossings+1]-t[crossings])/(p[crossings+1]-p[crossings])
    grid=np.sort(np.r_[t,zero_times]); values=np.interp(grid,t,p)
    delivered=float(np.trapezoid(np.maximum(values,0),grid))
    returned=float(np.trapezoid(np.maximum(-values,0),grid))
    return {"net_delivered_j":delivered-returned,"positive_delivered_j":delivered,"returned_j":returned}


def constant_supply(deck,name,node):
    matches=[line.split() for line in deck.splitlines() if line.startswith(name+" ")]
    if len(matches)!=1 or len(matches[0])!=4 or matches[0][1:3]!=[node,"0"]:
        raise ValueError("Expected a constant grounded supply")
    value=float(matches[0][3])
    if not np.isfinite(value) or value<=0:
        raise ValueError("Invalid supply voltage")
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs",type=Path,nargs="+")
    args=parser.parse_args(); reports=[]
    for path in args.runs:
        run=path.resolve(); c=json.loads((run/"contract.json").read_text())
        r=json.loads((run/"result.json").read_text())
        for name in ("deck.spice","circuit.spice"):
            if hashlib.sha256((run/name).read_bytes()).hexdigest()!=c["sha256"][name]:
                raise ValueError("Source hash mismatch")
        header,binary=(run/"waveform.raw").read_bytes().split(b"Binary:\n",1)
        names=[line.split()[1] for line in header.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
        wave=np.frombuffer(binary,dtype=np.float64).reshape(-1,len(names)); time=wave[:,0]
        if names[0]!="time" or not np.isfinite(wave).all() or not np.all(np.diff(time)>0):
            raise ValueError("Invalid waveform")
        deck=(run/"deck.spice").read_text()
        voltage={"vdd":constant_supply(deck,"VDD","vdd"),
                 "vactive":constant_supply(deck,"VACTIVE","vdd_active")}
        rows=[]
        for index in range(len(c["input_diffs_mv"])):
            start=index*c["period_ns"]*1e-9; stop=(index+1)*c["period_ns"]*1e-9
            rails={name:integrate_power(time,-v*wave[:,names.index(f"i({name})")],start,stop)
                   for name,v in voltage.items()}
            rows.append({"cycle":index,"startup_cycle":index==0,"rails":rails,
                         "two_rail_net_energy_j":sum(item["net_delivered_j"] for item in rails.values())})
        reports.append({"source_run":str(run),"rows":rows,"supply_voltage_v":voltage,
                        "mean_nonstartup_two_rail_energy_j":float(np.mean([row["two_rail_net_energy_j"] for row in rows[1:]])),
                        "strict_waveform_legal":r.get("waveform_legal") is True,
                        "profile":{key:c.get(key) for key in ("input_diffs_mv","calibration_offset_mv","period_ns","reset_rise_ps","reset_fall_ps","clock_fall_ps","equalizer_release_ns","reltol","max_step_ps")},
                        "source_sha256":{name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in
                            ("contract.json","result.json","deck.spice","circuit.spice","waveform.raw")}})
    out=ROOT/"evidence/aimc-simulator-adapters/latch-supply-energy"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False); shutil.copy2(Path(__file__),out/"analyzer.py")
    result={"runs":reports,"accepted_converter":False,
            "boundary":"Net energy from VDD and VACTIVE only, including devices and external resistive loads fed by those rails. Excludes unsaved clock/input/bias-source energy, physical driver generation, ADC/DAC/array, memory and runtime costs. First cycle starts from SPICE operating point and is excluded from the reported nonstartup mean. Not total comparator or inference energy, nor a hardware measurement."}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    for report in reports:
        print(report["source_run"],"mean_nonstartup_two_rail_energy_fj",report["mean_nonstartup_two_rail_energy_j"]*1e15)
    print(out)


if __name__=="__main__":
    main()
