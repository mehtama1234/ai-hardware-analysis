#!/usr/bin/env python3
"""Measure capture-input transitions and internal peaks without causal claims."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def crossings(time,values,threshold,rising):
    mask=(values[:-1]<threshold)&(values[1:]>=threshold) if rising else (values[:-1]>threshold)&(values[1:]<=threshold)
    indices=np.flatnonzero(mask)
    return [float((time[i]+(threshold-values[i])*(time[i+1]-time[i])/(values[i+1]-values[i]))*1e9)
            for i in indices]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path)
    args=parser.parse_args(); run=args.run.resolve()
    c=json.loads((run/"contract.json").read_text())
    r=json.loads((run/"result.json").read_text())
    for name in ("circuit.spice","deck.spice"):
        if hashlib.sha256((run/name).read_bytes()).hexdigest()!=c["sha256"][name]:
            raise ValueError("Source hash mismatch")
    raw=(run/"waveform.raw").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=r["waveform_sha256"]:
        raise ValueError("Waveform hash mismatch")
    header,binary=raw.split(b"Binary:\n",1)
    names=[line.split()[1] for line in header.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
    wave=np.frombuffer(binary,dtype=np.float64).reshape(-1,len(names)); t=wave[:,0]
    if names[0]!="time" or not np.isfinite(wave).all() or not np.all(np.diff(t)>0) or t[-1]<200e-9:
        raise ValueError("Invalid/incomplete waveform")
    rows=[]
    for cycle,expected in enumerate(c["expected_bits"]):
        lo=cycle*50+8; hi=cycle*50+19
        grid=np.r_[lo*1e-9,t[(t>lo*1e-9)&(t<hi*1e-9)],hi*1e-9]
        values=np.interp(grid,t,wave[:,names.index("v(rx_n)")])
        # Retain all crossings; no selection that hides ringing or absent transitions.
        edges={str(level):crossings(grid,values,level,bool(expected)) for level in (.18,.9,1.62)}
        ordered=(edges["0.18"],edges["1.62"]) if expected else (edges["1.62"],edges["0.18"])
        duration=ordered[1][0]-ordered[0][0] if all(len(x)==1 for x in ordered) else None
        internal=np.interp(grid,t,wave[:,names.index("v(xu.a_1561_36413#)")])
        peak=int(np.argmax(internal)); at=grid[peak]
        rows.append({"cycle":cycle,"expected":expected,"window_ns":[lo,hi],
                     "directed_crossings_ns":edges,"unambiguous_10_90_transition_ns":duration,
                     "internal_peak_v":float(internal[peak]),"internal_peak_ns":float(at*1e9),
                     "coincident_data_v":float(np.interp(at,t,wave[:,names.index("v(rx_n)")]))})
    out=ROOT/"evidence/aimc-simulator-adapters/capture-data-transition"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False); shutil.copy2(__file__,out/"analyzer.py")
    result={"source_run":str(run),"cycles":rows,"accepted_converter":False,
            "source_sha256":{name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in
                             ("contract.json","result.json","circuit.spice","deck.spice","waveform.raw")},
            "boundary":"Same named 40-device extracted topology only; interpolated sampled transitions in pre-capture windows, not causal proof, delay signoff or voltage qualification."}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(rows,indent=2)); print(out)


if __name__=="__main__":
    main()
