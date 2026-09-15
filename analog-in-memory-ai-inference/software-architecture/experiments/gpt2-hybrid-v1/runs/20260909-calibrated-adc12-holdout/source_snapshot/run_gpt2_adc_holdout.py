#!/usr/bin/env python3
"""Execute a frozen validation-selected ADC profile on disjoint test contexts."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import torch
import transformers
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM

from calibrated_adc_projection import CalibratedADCProjection
from tiled_projection_model import Profile, TiledProjection
from projection_numerical_control import CONTRACT, assess
from run_gpt2_hybrid_evaluation import digest, replace_forward


def run(args):
    plan=json.loads((args.plan/"plan.json").read_text())
    for name,expected in json.loads((args.plan/"manifest.json").read_text()).items():
        if digest(args.plan/name) != expected:
            raise ValueError(f"Frozen plan changed: {name}")
    for item in plan["sources"].values():
        if digest(item["path"]) != item["sha256"]:
            raise ValueError("Plan source changed")
    if plan["numerical_control"] != CONTRACT:
        raise ValueError("Numerical control changed")
    args.output.mkdir(parents=True,exist_ok=False)
    shutil.copytree(args.plan,args.output/"frozen_plan")
    source=args.output/"source_snapshot";source.mkdir()
    for name in [Path(__file__).name,"calibrated_adc_projection.py","tiled_projection_model.py",
                 "projection_numerical_control.py","run_gpt2_hybrid_evaluation.py"]:
        shutil.copy2(Path(__file__).with_name(name),source/name)
    torch.set_num_threads(2)
    torch.manual_seed(plan["seed"])
    snapshot=Path(snapshot_download("openai-community/gpt2",revision=plan["model_revision"],local_files_only=True))
    for name,expected in plan["model_files"].items():
        if digest(snapshot/name) != expected:
            raise ValueError(f"Model/tokenizer source changed: {name}")
    print("Loading frozen model and calibration",flush=True)
    model=AutoModelForCausalLM.from_pretrained(snapshot,local_files_only=True,attn_implementation="eager").eval()
    module=model.get_submodule("transformer.h.0.mlp.c_fc")
    contract=plan["selected_contract"]
    calibration=torch.load(args.plan/"calibration_inputs.pt",weights_only=True,map_location="cpu")
    candidate=CalibratedADCProjection(module.weight,module.bias,contract["calibrated_activation_abs_max"],
                                     Profile(**contract["profile"]),calibration,seed=plan["seed"],
                                     headroom=contract["adc_range"]["headroom"])
    if candidate.contract() != contract:
        raise ValueError("Training calibration does not reproduce frozen contract")
    del calibration
    ideal=TiledProjection(module.weight,module.bias,contract["calibrated_activation_abs_max"],Profile(),plan["seed"])
    rows=[];fallback=[]
    with torch.inference_mode(),(args.output/"rows.jsonl").open("w") as stream:
        for index,window in enumerate(plan["windows"]):
            tokens=torch.tensor([window["ids"]])
            captured=[]
            hook=module.register_forward_hook(lambda _m,_inputs,value:captured.append(value.clone()))
            try: baseline=model(tokens,use_cache=False).logits[:,:-1].float()
            finally: hook.remove()
            target=tokens[:,1:].reshape(-1)
            nll=float(torch.nn.functional.cross_entropy(baseline.reshape(-1,baseline.shape[-1]),target,reduction="sum"))
            for name,projection,is_ideal in [("ideal",ideal,True),(plan["selected_variant"],candidate,False)]:
                outputs=[]
                def forward(x):
                    value=projection(x,ideal=is_ideal)
                    if is_ideal: outputs.append(value.clone())
                    return value
                with replace_forward(module,forward):
                    logits=model(tokens,use_cache=False).logits[:,:-1].float()
                row={"window":index,"start":window["start"],"variant":name,"tokens":target.numel(),
                     "baseline_nll_sum":nll,"candidate_nll_sum":float(torch.nn.functional.cross_entropy(logits.reshape(-1,logits.shape[-1]),target,reduction="sum")),
                     "argmax_matches":int((baseline.argmax(-1)==logits.argmax(-1)).sum()),
                     "maximum_raw_logit_error":float((baseline-logits).abs().max())}
                if is_ideal: row["numerical_control"]=assess(captured[0],outputs[0],baseline,logits,target)
                rows.append(row);stream.write(json.dumps(row)+"\n");stream.flush()
            restored=model(tokens,use_cache=False).logits[:,:-1].float()
            exact=torch.equal(restored,baseline)
            fallback.append({"window":index,"exact":exact})
            if not exact: raise RuntimeError("Digital fallback changed outputs")
            print(f"Completed holdout window {index+1}/{len(plan['windows'])}",flush=True)
    if not all(row["numerical_control"]["pass"] for row in rows if row["variant"]=="ideal"):
        raise RuntimeError("Ideal numerical control failed")
    if candidate.contract()!=contract: raise RuntimeError("Contract changed during holdout evaluation")
    summaries={}
    for name,projection in [("ideal",ideal),(plan["selected_variant"],candidate)]:
        subset=[r for r in rows if r["variant"]==name];count=sum(r["tokens"] for r in subset)
        a=sum(r["baseline_nll_sum"] for r in subset)/count;b=sum(r["candidate_nll_sum"] for r in subset)/count
        agreement=sum(r["argmax_matches"] for r in subset)/count
        summaries[name]={"tokens":count,"baseline_nll":a,"candidate_nll":b,"nll_increase":b-a,
                         "argmax_agreement":agreement,"baseline_sample_perplexity":math.exp(a),"candidate_sample_perplexity":math.exp(b),
                         "screen_pass":b-a<=plan["screen"]["maximum_nll_increase_nats"] and agreement>=plan["screen"]["minimum_argmax_agreement"],
                         "contract":projection.contract(),"trace":projection.trace}
    result={"schema_version":"calibrated_adc_disjoint_holdout.v1","status":"numerical_evaluation_complete",
            "variants":summaries,"fallback_controls":fallback,"ideal_control_pass":True,
            "frozen_plan_sha256":digest(args.output/"frozen_plan/plan.json"),"analog_authorized":False,
            "physical_profile_calibrated":False,"task_acceptance_established":False,
            "runtime":{"torch":torch.__version__,"transformers":transformers.__version__,"threads":2,"command":sys.argv},
            "claim_boundary":plan["claim_boundary"]+" Noiseless numerical profile; no matched hardware latency or energy."}
    (args.output/"result.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    (args.output/"manifest.json").write_text(json.dumps({str(p.relative_to(args.output)):digest(p) for p in args.output.rglob('*') if p.is_file()},indent=2)+"\n")
    print(json.dumps({name:{k:v for k,v in row.items() if k not in ['contract','trace']} for name,row in summaries.items()}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
