#!/usr/bin/env python3
"""Freeze a validation-selected profile and previously unscored test contexts."""
import argparse
import json
from pathlib import Path
import shutil

import pyarrow.parquet as pq
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from check_gpt2_wikitext_projection import check
from run_gpt2_hybrid_evaluation import digest


def select_disjoint_windows(token_count, excluded, count, length):
    if count < 2 or length < 2:
        raise ValueError("Need at least two windows and two targets per window")
    width = length + 1
    eligible = [start for start in range(0, token_count-width+1, width)
                if all(start+width <= old["start"] or old["start"]+len(old["ids"]) <= start for old in excluded)]
    if len(eligible) < count:
        raise ValueError("Insufficient disjoint contexts")
    return [eligible[i*(len(eligible)-1)//(count-1)] for i in range(count)]


def run(args):
    check(args.validation)
    check(args.previous_test)
    validation=json.loads((args.validation / "result.json").read_text())
    previous=json.loads((args.previous_test / "protocol.json").read_text())
    protocol=validation["protocol"]
    if protocol.get("experiment") != "adc_range_calibration_validation_v1" or previous["evaluation_split"] != "test":
        raise ValueError("Need range validation and earlier test evidence")
    for key in ["model_revision", "revision", "predictions_per_window", "screen"]:
        if protocol[key] != previous[key]:
            raise ValueError(f"Protocols differ: {key}")
    eligible=[(row["contract"]["profile"]["adc_bits"],name) for name,row in validation["variants"].items()
              if name.startswith("calibrated_") and row["screen_pass"]]
    if not eligible:
        raise ValueError("No calibrated candidate passes validation")
    _,selected=min(eligible)
    contract=validation["variants"][selected]["contract"]
    args.output.mkdir(parents=True,exist_ok=False)
    for name in [Path(__file__).name, "check_gpt2_wikitext_projection.py", "run_gpt2_hybrid_evaluation.py"]:
        shutil.copy2(Path(__file__).with_name(name),args.output / name)
    snapshot=snapshot_download("openai-community/gpt2",revision=protocol["model_revision"],local_files_only=True)
    tokenizer=AutoTokenizer.from_pretrained(snapshot,local_files_only=True)
    data=args.previous_test / "test.parquet"
    texts=pq.read_table(data)["text"].to_pylist()
    ids=tokenizer.encode("\n".join(texts),add_special_tokens=False,verbose=False)
    if len(ids) != previous["test"]["total_tokens"]:
        raise ValueError("Tokenization differs from earlier protocol")
    excluded=previous["test"]["windows"]
    for old in excluded:
        if ids[old["start"]:old["start"]+len(old["ids"])] != old["ids"]:
            raise ValueError("Earlier test token IDs do not reproduce")
    length=protocol["predictions_per_window"]
    starts=select_disjoint_windows(len(ids),excluded,args.windows,length)
    plan={"schema_version":"calibrated_adc_holdout_plan.v1", "status":"frozen_before_holdout_inference",
          "selected_variant":selected, "selected_contract":contract, "model_revision":protocol["model_revision"],
          "model_files":validation["model_files"], "dataset_revision":protocol["revision"],
          "selection_rule":"lowest ADC bit count among calibrated candidates passing the unchanged validation screen",
          "screen":protocol["screen"], "numerical_control":protocol["numerical_control"],
          "seed":protocol["seed"], "predictions_per_window":length,
          "windows":[{"start":start,"ids":ids[start:start+length+1]} for start in starts],
          "excluded_previous_test_windows":excluded,
          "context_selection":"evenly spaced eligible nonoverlapping blocks after excluding every previously scored context",
          "calibration_policy":"reuse exact frozen training activation tensor and range contract; no holdout fitting",
          "claim_boundary":"Previously unscored token contexts, not necessarily unseen articles or absent from model pretraining. No hardware qualification.",
          "sources":{name:{"path":str(path.resolve()),"sha256":digest(path)} for name,path in {
              "validation_result":args.validation/"result.json", "validation_manifest":args.validation/"manifest.json",
              "previous_test_protocol":args.previous_test/"protocol.json", "test_data":data,
              "calibration_inputs":args.validation/"calibration_inputs.pt"}.items()}}
    shutil.copy2(args.validation/"calibration_inputs.pt",args.output/"calibration_inputs.pt")
    (args.output/"plan.json").write_text(json.dumps(plan,indent=2)+"\n")
    (args.output/"manifest.json").write_text(json.dumps({p.name:digest(p) for p in args.output.iterdir() if p.is_file()},indent=2)+"\n")
    print(json.dumps({"selected":selected,"contexts":len(starts),"targets":len(starts)*length,"overlap_with_previous_contexts":0,"output":str(args.output)}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation",type=Path,required=True)
    parser.add_argument("--previous-test",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--windows",type=int,default=32)
    run(parser.parse_args())
