#!/usr/bin/env python3
"""Locate receiver envelope excursions and save coincident circuit observables."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def excursion_events(time,values,low=0,high=1.8):
    events=[]
    for side,mask in (("below",values<low),("above",values>high)):
        edges=np.diff(np.r_[False,mask,False].astype(int))
        for start,stop in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)):
            peak=int(start)+int(np.argmin(values[start:stop]) if side=="below" else np.argmax(values[start:stop]))
            events.append({"side":side,"peak_index":peak,"peak_v":float(values[peak]),
                "excursion_v":float(low-values[peak] if side=="below" else values[peak]-high),
                "first_outside_ns":float(time[start]*1e9),"last_outside_ns":float(time[stop-1]*1e9),
                "bracketing_start_ns":float(time[max(0,start-1)]*1e9),
                "bracketing_end_ns":float(time[min(len(time)-1,stop)]*1e9)})
    return sorted(events,key=lambda event:event["excursion_v"],reverse=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path)
    args=parser.parse_args(); run=args.run.resolve()
    contract=json.loads((run/"contract.json").read_text())
    for name in ("deck.spice","circuit.spice"):
        if hashlib.sha256((run/name).read_bytes()).hexdigest()!=contract["sha256"][name]:
            raise ValueError(f"Source hash mismatch: {name}")
    header,binary=(run/"waveform.raw").read_bytes().split(b"Binary:\n",1)
    names=[line.split()[1] for line in header.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
    wave=np.frombuffer(binary,dtype=np.float64).reshape(-1,len(names)); time=wave[:,0]
    if names[0]!="time" or not np.isfinite(wave).all() or not np.all(np.diff(time)>0):
        raise ValueError("Invalid waveform")
    if time[-1]<len(contract["input_diffs_mv"])*contract["period_ns"]*1e-9-1e-15:
        raise ValueError("Incomplete waveform")
    reports={}
    for side in ("p","n"):
        receiver=f"v(rx_{side})"; driver=f"v(out_{side})"
        events=excursion_events(time,wave[:,names.index(receiver)])
        for event in events:
            index=event["peak_index"]; ns=float(time[index]*1e9)
            event.update(peak_ns=ns,cycle=int(ns//contract["period_ns"]),offset_ns=ns%contract["period_ns"],
                coincident_v={name:float(wave[index,names.index(name)]) for name in
                    (driver,"v(reset)","v(eval)","v(eq_reset)") if name in names})
        reports[receiver]={"event_count":len(events),"largest_events":events[:12],
            "largest_by_side":{side:next((event for event in events if event["side"]==side),None)
                               for side in ("below","above")}}
    out=ROOT/"evidence/aimc-simulator-adapters/latch-receiver-excursions"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False); shutil.copy2(Path(__file__),out/"analyzer.py")
    report={"source_run":str(run),"receivers":reports,"accepted_converter":False,
            "source_sha256":{name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in
                ("contract.json","circuit.spice","deck.spice","waveform.raw")},
            "boundary":"Sampled extrema and contiguous out-of-envelope events; coincident voltages are observations, not causal proof or reliability qualification. No threshold is relaxed."}
    (out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    for name,receiver in reports.items():
        print(name,json.dumps(receiver["largest_by_side"]))
    print(out)


if __name__=="__main__":
    main()
