#!/usr/bin/env python3
"""Bind a saved calibration diagnostic to its separately frozen contract."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"evidence/aimc-simulator-adapters"


def profile_mismatches(frozen,actual):
    mapping={"logical_validation_sequence_mv":"input_diffs_mv","correction_mv":"calibration_offset_mv",
             "corner":"effective_model_corner","temperature_c":"effective_temperature_c",
             "reset_early_ns":"reset_advance_ns"}
    fields=("logical_validation_sequence_mv","correction_mv","corner","temperature_c",
            "reset_early_ns","mismatch_seed","period_ns","equalizer_release_ns","reset_high_v",
            "clock_fall_ps","input_setup_ns","reltol","max_step_ps")
    bad=[key for key in fields if key not in frozen or mapping.get(key,key) not in actual
         or frozen[key]!=actual[mapping.get(key,key)]]
    expected=[x+frozen["correction_mv"] for x in frozen["logical_validation_sequence_mv"]]
    if actual.get("applied_input_diffs_mv")!=expected:
        bad.append("applied_input_diffs_mv")
    if actual.get("mismatch_seed_method")!="startup_seed_plus_control_setseed_reset":
        bad.append("mismatch_seed_method")
    if actual.get("reset_rise_ps",20)!=frozen.get("reset_rise_ps",20):
        bad.append("reset_rise_ps")
    if actual.get("reset_fall_ps",actual["clock_fall_ps"])!=frozen.get("reset_fall_ps",frozen["clock_fall_ps"]):
        bad.append("reset_fall_ps")
    return bad


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen_contract",type=Path)
    parser.add_argument("run",type=Path)
    args=parser.parse_args()
    frozen=json.loads(args.frozen_contract.read_text())
    run=args.run.resolve()
    actual=json.loads((run/"contract.json").read_text())
    result=json.loads((run/"result.json").read_text())
    bad=profile_mismatches(frozen,actual)
    if Path(actual["combined_layout"]).resolve()!=(EVIDENCE/frozen["combined_layout"]).resolve():
        bad.append("combined_layout")
    checks={EVIDENCE/frozen["selection_evidence"]:frozen["selection_evidence_sha256"],
            run/"circuit.spice":frozen["extracted_spice_sha256"]}
    checks.update({run/name:actual["sha256"][name] for name in ("deck.spice",".spiceinit")})
    for path,digest in checks.items():
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            bad.append(str(path))
    rows=result.get("rows",[])
    complete=len(rows)==len(frozen["logical_validation_sequence_mv"])
    for index,row in enumerate(rows):
        if index>=len(frozen["logical_validation_sequence_mv"]) or row.get("input_diff_mv")!=frozen["logical_validation_sequence_mv"][index]:
            bad.append(f"result_input_cycle_{index}")
    diagnostic=complete and not bad and all(all(row.get(key) is True for key in
        ("sample_polarity_pass","hold_margin_pass","reset_pass","receiver_hold_pass")) for row in rows)
    out=EVIDENCE/"latch-calibration-validation"/datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(args.frozen_contract,out/"frozen_contract.json")
    shutil.copy2(Path(__file__),out/"verifier.py")
    report={"source_run":str(run),"profile_mismatches":bad,"complete":complete,
            "decision_only_diagnostic_pass":diagnostic,"strict_waveform_legal":result.get("waveform_legal") is True,
            "declared_validation_pass":diagnostic and result.get("waveform_legal") is True,
            "accepted_converter":False,
            "sha256":{str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in
                (args.frozen_contract,run/"contract.json",run/"result.json",run/"waveform.raw",Path(__file__))},
            "boundary":"Profile/hash binding and aggregation of saved runner checks, not an independent waveform or physical-qualification verifier. Same-device ideal correction only."}
    (out/"result.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2)); print(out)
    return 0 if report["declared_validation_pass"] else 1


if __name__=="__main__":
    raise SystemExit(main())
