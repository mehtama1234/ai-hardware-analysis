#!/usr/bin/env python3
"""Audit sampled terminal biases; never equate model ranges with reliability."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
from urllib.request import urlopen

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RANGES = {"nfet": {"vds": (0,1.95), "vgs": (0,1.95), "vbs": (-1.95,0.3)},
          "pfet": {"vds": (-1.95,0), "vgs": (-1.95,0), "vbs": (-0.1,1.95)}}


def range_summary(values, time, limits):
    low, high = limits
    outside = (values < low) | (values > high)
    return {"range_v": list(limits), "min_v": float(values.min()), "max_v": float(values.max()),
            "all_sampled_points_in_range": not bool(outside.any()),
            "outside_duration_ns_trapezoid_estimate": float(np.trapezoid(outside.astype(float), time)*1e9),
            "max_excursion_v": float(max(0,low-values.min(),values.max()-high))}


def device_biases(d,g,s,b,kind,normalize=False):
    if normalize:
        d,s = (np.maximum(d,s),np.minimum(d,s)) if kind=="nfet" else (np.minimum(d,s),np.maximum(d,s))
    return {"vds": d-s,"vgs":g-s,"vbs":b-s}


def validate_device_coverage(rows,equalizer_enabled):
    expected=16 if equalizer_enabled else 15
    if len(rows)!=expected:
        raise ValueError(f"Expected all {expected} devices in the combined cell")
    equalizers=[row for row in rows if row["terminals"]["g"]=="eq_reset"]
    if len(equalizers)!=int(equalizer_enabled):
        raise ValueError("Equalizer control/device coverage mismatch")
    if equalizers:
        row=equalizers[0]; terminals=row["terminals"]
        if (row["model"]!="sky130_fd_pr__pfet_01v8" or terminals["b"]!="vdd_active"
                or {terminals["d"],terminals["s"]}!={"latch_sense_p","latch_sense_n"}):
            raise ValueError("Unexpected equalizer terminals/model")


def ideal_source(deck,node,time):
    matches = [line.split(maxsplit=3)[3] for line in deck.splitlines()
               if re.match(rf"^V\S+\s+{re.escape(node)}\s+0\s+",line)]
    if len(matches)!=1:
        raise ValueError(f"No unique saved vector or grounded ideal source for {node}")
    value=matches[0]
    if value.startswith("PWL(") and value.endswith(")"):
        fields=value[4:-1].split()
        if len(fields)%2:
            raise ValueError("Malformed input PWL")
        times=[float(fields[i][:-1])*1e-9 for i in range(0,len(fields),2) if fields[i].endswith("n")]
        if len(times)*2 != len(fields) or not np.all(np.diff(times)>0):
            raise ValueError("Unsupported or nonmonotonic PWL time grid")
        return np.interp(time,times,[float(x) for x in fields[1::2]])
    return np.full(time.shape,float(value))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run",type=Path)
    args=parser.parse_args()
    run=args.run.resolve()
    contract=json.loads((run/"contract.json").read_text())
    for name in ("circuit.spice","deck.spice"):
        if hashlib.sha256((run/name).read_bytes()).hexdigest()!=contract["sha256"][name]:
            raise ValueError(f"Source artifact hash mismatch: {name}")
    h,binary=(run/"waveform.raw").read_bytes().split(b"Binary:\n",1)
    names=[line.split()[1] for line in h.decode().split("Variables:\n",1)[1].splitlines() if line.strip()]
    wave=np.frombuffer(binary,dtype=np.float64).reshape(-1,len(names))
    if names[0]!="time" or not np.isfinite(wave).all() or not np.all(np.diff(wave[:,0])>0):
        raise ValueError("Invalid waveform")
    time=wave[:,0]
    if time[-1] < len(contract["input_diffs_mv"])*contract["period_ns"]*1e-9-1e-15:
        raise ValueError("Truncated transient")
    nodes={name[2:-1]:wave[:,i] for i,name in enumerate(names) if name.startswith("v(")}
    deck=(run/"deck.spice").read_text()
    rows=[]
    for line in (run/"circuit.spice").read_text().splitlines():
        if not line.startswith("X"):
            continue
        name,d,g,s,bulk,model,*_=line.split()
        if model not in ("sky130_fd_pr__nfet_01v8","sky130_fd_pr__pfet_01v8"):
            raise ValueError(f"Unsupported device model {model}")
        kind="nfet" if "__nfet_" in model else "pfet"
        for node in (d,g,s,bulk):
            if node not in nodes:
                nodes[node]=ideal_source(deck,node,time)
        vd,vg,vs,vb=[nodes[node] for node in (d,g,s,bulk)]
        if not all(np.isfinite(value).all() for value in (vd,vg,vs,vb)):
            raise ValueError("Nonfinite reconstructed terminal voltage")
        raw=device_biases(vd,vg,vs,vb,kind)
        normalized=device_biases(vd,vg,vs,vb,kind,True)
        rows.append({"device":name,"model":model,"terminals":{"d":d,"g":g,"s":s,"b":bulk},
                     "as_netlisted":{key:range_summary(value,time,RANGES[kind][key]) for key,value in raw.items()},
                     "polarity_normalized_diagnostic_only":{key:range_summary(value,time,RANGES[kind][key]) for key,value in normalized.items()},
                     "max_abs_gate_to_any_terminal_v":float(max(np.abs(vg-vd).max(),np.abs(vg-vs).max(),np.abs(vg-vb).max()))})
    validate_device_coverage(rows,contract.get("equalizer_release_ns") is not None)
    out=ROOT/"evidence/aimc-simulator-adapters/latch-terminal-audit"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(Path(__file__),out/"auditor.py")
    sources={}
    for kind in ("nfet","pfet"):
        url=f"https://raw.githubusercontent.com/google/skywater-pdk/main/docs/rules/device-details/{kind}_01v8/index.rst"
        with urlopen(url,timeout=20) as response:
            data=response.read(20000)
        (out/f"{kind}_source.rst").write_bytes(data)
        sources[kind]={"url":url,"sha256":hashlib.sha256(data).hexdigest(),"scope":"Published SPICE model-validity ranges; not reliability limits"}
    result={"status":"terminal_range_audit_complete_not_qualification","source_run":str(run),
            "source_sha256":{name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in
                             ("contract.json","deck.spice","circuit.spice","waveform.raw")},
            "sources":sources,"devices":rows,
            "as_netlisted_all_in_range":all(item["all_sampled_points_in_range"] for row in rows for item in row["as_netlisted"].values()),
            "normalized_all_in_range":all(item["all_sampled_points_in_range"] for row in rows for item in row["polarity_normalized_diagnostic_only"].values()),
            "maximum_absolute_gate_terminal_voltage_v":max(row["max_abs_gate_to_any_terminal_v"] for row in rows),
            "accepted_converter":False,
            "boundary":"Sampled terminal biases, with constant/PWL ideal sources reconstructed from the exact deck. Polarity normalization is diagnostic, not authorization to extrapolate models. No reliability, duration tolerance, PVT or silicon signoff."}
    (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    for row in rows:
        print(row["device"],row["terminals"],{key:round(item["max_excursion_v"],6) for key,item in row["polarity_normalized_diagnostic_only"].items() if not item["all_sampled_points_in_range"]})
    print("maximum_absolute_gate_terminal_voltage_v",result["maximum_absolute_gate_terminal_voltage_v"])
    print(out)


if __name__=="__main__":
    main()
