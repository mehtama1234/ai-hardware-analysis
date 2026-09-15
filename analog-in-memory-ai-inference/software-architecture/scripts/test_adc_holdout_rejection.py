#!/usr/bin/env python3
"""Ensure a completed holdout package rejects changed evidence and scope."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

from check_gpt2_adc_holdout import check,digest


def write(path,value):
    path.write_text(json.dumps(value,indent=2)+"\n")


def run(package):
    check(package)
    for mode in ["overlap","profile_change","failed_selection","numerical_failure","metric_arithmetic","analog_claim","source_change"]:
        with tempfile.TemporaryDirectory(prefix="adc-holdout-rejection-") as temporary:
            root=Path(temporary)/"package";shutil.copytree(package,root)
            result=json.loads((root/"result.json").read_text())
            plan=json.loads((root/"frozen_plan/plan.json").read_text())
            if mode=="overlap":
                plan["windows"][0]=plan["excluded_previous_test_windows"][0]
            elif mode=="profile_change":
                result["variants"][plan["selected_variant"]]["contract"]["adc_range"]["ranges"][0]["selected_bound"]*=1.2
            elif mode=="failed_selection":
                plan["selected_variant"]="calibrated_adc8"
            elif mode=="numerical_failure":
                rows=[json.loads(x) for x in (root/"rows.jsonl").read_text().splitlines()]
                next(r for r in rows if r["variant"]=="ideal")["numerical_control"]["maximum_log_probability_error"]=.01
                (root/"rows.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))
            elif mode=="metric_arithmetic":
                result["variants"][plan["selected_variant"]]["candidate_nll"]+=1
            elif mode=="analog_claim":
                result["analog_authorized"]=True
            else:
                with (root/"source_snapshot/run_gpt2_adc_holdout.py").open("a") as stream:
                    stream.write("\n# source modified after execution\n")
            if mode!="source_change":
                write(root/"frozen_plan/plan.json",plan)
                frozen_manifest=json.loads((root/"frozen_plan/manifest.json").read_text())
                frozen_manifest["plan.json"]=digest(root/"frozen_plan/plan.json")
                write(root/"frozen_plan/manifest.json",frozen_manifest)
                result["frozen_plan_sha256"]=digest(root/"frozen_plan/plan.json")
                write(root/"result.json",result)
                manifest=json.loads((root/"manifest.json").read_text())
                write(root/"manifest.json",{name:digest(root/name) for name in manifest})
            try: check(root)
            except AssertionError: print(f"Correctly rejected {mode}")
            else: raise RuntimeError(f"Accepted altered holdout: {mode}")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package",type=Path)
    run(parser.parse_args().package)
