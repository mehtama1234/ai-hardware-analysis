#!/usr/bin/env python3
"""Check identical-seed replay and different-seed sensitivity from saved runs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs",type=Path,nargs=3,help="Two equal seeds, then a distinct seed")
    args=parser.parse_args()
    records=[]
    contracts=[]
    for path in args.runs:
        run=path.resolve()
        contract=json.loads((run/"contract.json").read_text())
        result=json.loads((run/"result.json").read_text())
        if contract.get("mismatch_seed_method")!="startup_seed_plus_control_setseed_reset":
            raise ValueError("Unsupported or historically nonreproducible seed method")
        for name in ("circuit.spice","deck.spice",".spiceinit"):
            if hashlib.sha256((run/name).read_bytes()).hexdigest()!=contract["sha256"][name]:
                raise ValueError(f"Source hash mismatch: {name}")
        numeric=(run/"waveform.raw").read_bytes().split(b"Binary:\n",1)[1]
        rows=result.get("rows",[])
        if len(rows)!=len(contract["input_diffs_mv"]):
            raise ValueError("Incomplete simulation")
        contracts.append(contract)
        records.append({"run":str(run),"seed":contract["mismatch_seed"],
                        "numeric_waveform_sha256":hashlib.sha256(numeric).hexdigest(),
                        "contract_sha256":hashlib.sha256((run/"contract.json").read_bytes()).hexdigest(),
                        "result_sha256":hashlib.sha256((run/"result.json").read_bytes()).hexdigest(),
                        "correct_polarities":[row["sample_polarity_pass"] for row in rows]})
    for key in ("input_diffs_mv","period_ns","effective_model_corner","effective_temperature_c","effective_model_file_sha256",
                "reset_high_v","reset_advance_ns","clock_fall_ps","combined_layout"):
        if any(c[key]!=contracts[0][key] for c in contracts[1:]):
            raise ValueError(f"Profiles differ beyond seed: {key}")
    if any(c.get("calibration_offset_mv",0)!=contracts[0].get("calibration_offset_mv",0) for c in contracts[1:]):
        raise ValueError("Calibration corrections differ between replay profiles")
    if any(c.get("input_setup_ns",5)!=contracts[0].get("input_setup_ns",5) for c in contracts[1:]):
        raise ValueError("Input settling differs between replay profiles")
    for key,default in (("max_step_ps",None),("reltol",1e-4),("equalizer_release_ns",None),("reset_rise_ps",20)):
        if any(c.get(key,default)!=contracts[0].get(key,default) for c in contracts[1:]):
            raise ValueError(f"Solver settings differ: {key}")
    if any(c.get("reset_fall_ps",c["clock_fall_ps"])!=contracts[0].get("reset_fall_ps",contracts[0]["clock_fall_ps"]) for c in contracts[1:]):
        raise ValueError("Output precharge slew differs")
    passed=(records[0]["seed"]==records[1]["seed"]!=records[2]["seed"]
            and records[0]["numeric_waveform_sha256"]==records[1]["numeric_waveform_sha256"]
            and records[0]["numeric_waveform_sha256"]!=records[2]["numeric_waveform_sha256"])
    out=ROOT/"evidence/aimc-simulator-adapters/latch-mismatch-reproducibility"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    report={"status":"replay_and_seed_sensitivity_pass" if passed else "reproducibility_fail","runs":records,
            "accepted_converter":False,"boundary":"Two distinct mismatch realizations are not a yield estimate or offset distribution."}
    (out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2)); print(out)
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
