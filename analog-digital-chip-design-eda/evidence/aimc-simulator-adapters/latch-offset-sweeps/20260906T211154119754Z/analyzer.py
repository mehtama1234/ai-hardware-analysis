#!/usr/bin/env python3
"""Bracket stable receiver decisions independently of the expected input sign."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def classify_hold(p,n,rp,rn,margin=0.5,low=0.18,high=1.62):
    if all(len(x)>0 and np.isfinite(x).all() for x in (p,n,rp,rn)):
        if np.all(p-n>=margin) and np.all(rn>=high) and np.all(rp<=low):
            return "positive"
        if np.all(n-p>=margin) and np.all(rp>=high) and np.all(rn<=low):
            return "negative"
    return "unresolved"


def transition_bracket(rows):
    negatives=[r["input_diff_mv"] for r in rows if r["stable_receiver_decision"]=="negative"]
    positives=[r["input_diff_mv"] for r in rows if r["stable_receiver_decision"]=="positive"]
    return [max(negatives),min(positives)] if negatives and positives and max(negatives)<min(positives) else None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs",type=Path,nargs="+")
    args=parser.parse_args()
    reports=[]
    profiles=[]
    for source in args.runs:
        source=source.resolve()
        contract=json.loads((source/"contract.json").read_text())
        if contract.get("calibration_offset_mv",0)!=0:
            raise ValueError("Raw offset bracketing requires uncorrected physical input axes")
        result=json.loads((source/"result.json").read_text())
        if contract.get("mismatch_seed_method")!="startup_seed_plus_control_setseed_reset" or not contract.get("combined_layout_lvs_verified"):
            raise ValueError("Require seeded, combined-layout evidence")
        for name in ("circuit.spice","deck.spice"):
            if hashlib.sha256((source/name).read_bytes()).hexdigest()!=contract["sha256"][name]:
                raise ValueError(f"Input artifact hash mismatch: {name}")
        profiles.append({key:contract[key] for key in ("mismatch_seed","effective_model_corner","effective_temperature_c",
            "effective_model_file_sha256","reset_high_v","clock_fall_ps","reset_advance_ns","combined_layout")})
        profiles[-1]["input_setup_ns"] = contract.get("input_setup_ns",5)
        profiles[-1]["period_ns"] = contract["period_ns"]
        profiles[-1]["max_step_ps"] = contract.get("max_step_ps")
        profiles[-1]["reltol"] = contract.get("reltol",1e-4)
        h,b=(source/"waveform.raw").read_bytes().split(b"Binary:\n",1)
        names=[x.split()[1] for x in h.decode().split("Variables:\n",1)[1].splitlines() if x.strip()]
        wave=np.frombuffer(b,dtype=np.float64).reshape(-1,len(names))
        if names[0]!="time" or not np.isfinite(wave).all() or not np.all(np.diff(wave[:,0])>0):
            raise ValueError("Invalid waveform")
        rows=[]
        for i,diff in enumerate(contract["input_diffs_mv"]):
            lo,hi=[(i*contract["period_ns"]+x)*1e-9 for x in contract["hold_window_ns"]]
            if wave[-1,0]<hi:
                raise ValueError("Incomplete hold window")
            # Include exact window endpoints as well as every interior sample.
            t=np.concatenate(([lo],wave[(wave[:,0]>lo)&(wave[:,0]<hi),0],[hi]))
            traces=[np.interp(t,wave[:,0],wave[:,names.index(name)]) for name in ("v(out_p)","v(out_n)","v(rx_p)","v(rx_n)")]
            state=classify_hold(*traces)
            reset_time=(i*contract["period_ns"]+contract["reset_check_offset_ns"])*1e-9
            reset_sense=[float(np.interp(reset_time,wave[:,0],wave[:,names.index(name)]))
                         for name in ("v(latch_sense_p)","v(latch_sense_n)")]
            rows.append({"cycle":i,"input_diff_mv":diff,"stable_receiver_decision":state,
                         "reset_latch_sense_v":reset_sense,
                         "reset_latch_sense_diff_mv":1000*(reset_sense[0]-reset_sense[1]),
                         "preceding_decision":rows[-1]["stable_receiver_decision"] if rows else "initial_condition",
                         "reset_pass":result["rows"][i]["reset_pass"]})
        bracket=transition_bracket(rows)
        by_previous={state:transition_bracket([row for row in rows if row["preceding_decision"]==state])
                     for state in ("negative","positive")}
        history_conflicts=[value for value in sorted({row["input_diff_mv"] for row in rows})
                           if {row["stable_receiver_decision"] for row in rows if row["input_diff_mv"]==value} >= {"negative","positive"}]
        reports.append({"run":str(source),"rows":rows,"stable_transition_bracket_mv":bracket,
                        "brackets_by_preceding_decision_mv":by_previous,"history_conflict_inputs_mv":history_conflicts,
                        "all_reset_checks_pass":all(r["reset_pass"] for r in rows),
                        "sha256":{name:hashlib.sha256((source/name).read_bytes()).hexdigest() for name in ("contract.json","result.json","waveform.raw")}})
    if any(profile!=profiles[0] for profile in profiles[1:]):
        raise ValueError("Sweeps do not use identical mismatch/physical profiles")
    out=ROOT/"evidence/aimc-simulator-adapters/latch-offset-sweeps"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    report={"status":"offset_diagnostic_only","profile":profiles[0],"sweeps":reports,"accepted_converter":False,
            "analyzer_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "boundary":"Stable 16..20 ns receiver decisions at sampled inputs under specific histories, not DC offset, hysteresis-free proof or a statistical distribution. Rail/model-range qualification remains separate."}
    (out/"analyzer.py").write_text(Path(__file__).read_text())
    (out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    for sweep in reports:
        print(sweep["run"],sweep["stable_transition_bracket_mv"],sweep["rows"])
    print(out)


if __name__=="__main__":
    main()
