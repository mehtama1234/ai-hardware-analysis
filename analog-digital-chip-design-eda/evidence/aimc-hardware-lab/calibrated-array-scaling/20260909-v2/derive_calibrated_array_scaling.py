#!/usr/bin/env python3
"""Derive model-specific normalized differential-array gain requirements."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import torch
import safetensors
from safetensors import safe_open

ROOT=Path(__file__).resolve().parents[1]
SOFTWARE=ROOT.parent/"analog-in-memory-ai-inference/software-architecture"
sys.path.insert(0,str(SOFTWARE/"scripts"))
from check_gpt2_adc_holdout import check
from tiled_projection_model import quantize


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized_gain(activation_bound,weight_step,bits,adc_bound):
    values=[activation_bound,weight_step,adc_bound]
    if any(not np.isfinite(v) or v<=0 for v in values) or not 2<=bits<=16:
        raise ValueError("Positive finite scales and valid precision required")
    return activation_bound*((1<<(bits-1))-1)*weight_step/adc_bound


def run(args):
    check(args.quality)
    plan=json.loads((args.quality/"frozen_plan/plan.json").read_text())
    result=json.loads((args.quality/"result.json").read_text())
    selected=plan["selected_variant"]
    if not result["variants"][selected]["screen_pass"]:
        raise ValueError("Profile is not quality-screened")
    if digest(args.weights)!=plan["model_files"]["model.safetensors"]:
        raise ValueError("Checkpoint hash differs from evaluated model")
    if digest(SOFTWARE/"scripts/tiled_projection_model.py")!=digest(args.quality/"source_snapshot/tiled_projection_model.py"):
        raise ValueError("Quantizer source differs from the frozen evaluation")
    args.output.mkdir(parents=True,exist_ok=False)
    shutil.copy2(Path(__file__),args.output/Path(__file__).name)
    shutil.copy2(SOFTWARE/"scripts/tiled_projection_model.py",args.output/"tiled_projection_model.py")
    shutil.copy2(SOFTWARE/"scripts/check_gpt2_adc_holdout.py",args.output/"check_gpt2_adc_holdout.py")
    torch.set_num_threads(2)
    key="h.0.mlp.c_fc.weight"
    with safe_open(args.weights,framework="numpy") as checkpoint:
        weights=checkpoint.get_tensor(key)
    contract=plan["selected_contract"]
    if list(weights.shape)!=contract["weight_shape_input_output"]:
        raise ValueError("Projection shape mismatch")
    calibration_path=args.quality/"frozen_plan/calibration_inputs.pt"
    captured=torch.load(calibration_path,weights_only=True,map_location="cpu").reshape(-1,weights.shape[0])
    tensor_hash=hashlib.sha256(captured.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
    if tensor_hash!=contract["adc_range"]["input_tensor_sha256"]:
        raise ValueError("Training activation identity mismatch")
    a=contract["calibrated_activation_abs_max"]
    profile=contract["profile"];bits=profile["weight_bits"];maximum=(1<<(bits-1))-1
    if bits!=8:
        raise ValueError("This code-table export uses signed int8 storage")
    sample_indices=[0,len(captured)//3,2*len(captured)//3,len(captured)-1]
    x=quantize(captured[sample_indices],a,profile["dac_bits"]).numpy().astype(np.float64)
    dac_maximum=(1<<(profile["dac_bits"]-1))-1
    dac_step=np.float32(np.float32(a)/np.float32(dac_maximum))
    dac_codes=np.clip(np.rint(captured[sample_indices].numpy()/dac_step),-dac_maximum,dac_maximum).astype(np.int32)
    if not np.array_equal((dac_codes.astype(np.float32)*dac_step).astype(np.float64),x):
        raise ValueError("DAC codes do not reproduce frozen float32 inputs")
    activation_span=dac_maximum*float(dac_step)
    all_dac_codes=np.arange(-dac_maximum,dac_maximum+1,dtype=np.int32)
    maximum_dac_rounding=float(np.abs((all_dac_codes.astype(np.float32)*dac_step).astype(np.float64)-all_dac_codes*float(dac_step)).max())
    codes=np.zeros(weights.shape,dtype=np.int8)
    scales=[];checks=[]
    nr,nc=profile["tile_rows"],profile["tile_columns"]
    for index,row in enumerate(contract["adc_range"]["ranges"]):
        r,c=row["row"],row["column"]
        w=weights[r:r+nr,c:c+nc]
        peak=np.max(np.abs(w));step=np.float32(peak/np.float32(maximum))
        if step<=0: raise ValueError("Unexcited weight tile needs an explicit zero-tile mapping")
        qcode=np.clip(np.rint(w/step),-maximum,maximum).astype(np.int8)
        qw=(qcode.astype(np.float32)*step).astype(np.float32)
        original=quantize(torch.from_numpy(w.copy()),float(peak),bits).numpy()
        if not np.array_equal(qw,original):
            raise ValueError("Code export does not reproduce frozen float32 weights")
        codes[r:r+nr,c:c+nc]=qcode
        bound=row["selected_bound"]
        gain=normalized_gain(activation_span,float(step),bits,bound)
        # Ideal normalized differential current, with unitless row amplitude
        # and conductance difference. No physical voltage/conductance is chosen.
        normalized_current=(dac_codes[:,r:r+nr].astype(np.float64)/dac_maximum)@(qcode.astype(np.float64)/maximum)
        decoded_partial=normalized_current*gain*bound
        frozen_partial=x[:,r:r+nr]@qw.astype(np.float64)
        delta=np.abs(decoded_partial-frozen_partial)
        weight_rounding=np.abs(qw.astype(np.float64)-qcode.astype(np.float64)*float(step))
        # For every possible DAC-code vector, triangle inequality bounds the
        # code-level real-valued dot product versus the rounded model operands.
        error_bounds=activation_span*weight_rounding.sum(axis=0)+maximum_dac_rounding*np.abs(qw.astype(np.float64)).sum(axis=0)
        if not np.all(delta<=error_bounds[None,:]+1e-12):
            raise ValueError("Probe violates analytic rounding bound")
        checks.append({"tile_id":index,"tested_vectors":len(sample_indices),
                       "maximum_partial_abs_error":float(delta.max()),
                       "all_input_code_vectors_partial_error_bound":float(error_bounds.max()),
                       "relative_l2_error":float(np.linalg.norm(decoded_partial-frozen_partial)/max(np.linalg.norm(frozen_partial),1e-12))})
        scales.append({"tile_id":index,"row":r,"column":c,"weight_abs_max":float(peak),
                       "weight_step_model_units":float(step),"equivalent_signed_span_model_units":maximum*float(step),
                       "adc_bound_model_units":bound,"normalized_transimpedance_gain":gain,
                       "codes_sha256":hashlib.sha256(qcode.tobytes()).hexdigest()})
    low=min(s["normalized_transimpedance_gain"] for s in scales)
    high=max(s["normalized_transimpedance_gain"] for s in scales)
    for row in scales:
        row["gain_relative_to_minimum"]=row["normalized_transimpedance_gain"]/low
        row["adc_reference_fraction_of_max_at_fixed_gain"]=low/row["normalized_transimpedance_gain"]
    maximum_error=max(c["maximum_partial_abs_error"] for c in checks)
    maximum_bound=max(c["all_input_code_vectors_partial_error_bound"] for c in checks)
    if maximum_error>=1e-5 or maximum_bound>=1e-5:
        raise ValueError("Normalized mapping exceeds the declared partial-output rounding check")
    np.savez_compressed(args.output/"signed_weight_codes.npz",codes=codes)
    report={"schema_version":"calibrated_array_normalized_scaling.v1",
            "status":"model_specific_normalized_mapping_verified_not_physical_characterization",
            "runtime_module":"transformer.h.0.mlp.c_fc","checkpoint_tensor":key,
            "sources":{name:{"path":str(path.resolve()),"sha256":digest(path)} for name,path in {
                "weights":args.weights,"quality":args.quality/"result.json","plan":args.quality/"frozen_plan/plan.json",
                "training_activations":calibration_path}.items()},
            "signed_weight_codes":{"minimum":int(codes.min()),"maximum":int(codes.max()),
                                   "specified_signed_levels":2*maximum+1,"specified_levels_per_differential_branch":maximum+1,
                                   "representation":"G_plus=G_base+G_span*max(code,0)/127; G_minus=G_base+G_span*max(-code,0)/127"},
            "dac_codes":{"signed_maximum":dac_maximum,"model_step":float(dac_step),
                         "equivalent_span_model_units":activation_span,"maximum_float32_code_rounding_error":maximum_dac_rounding},
            "normalized_gain":{"minimum":low,"maximum":high,"span_ratio":high/low},"tiles":scales,
            "physical_equations":{"row_voltage":"V_drive_full_scale * DAC_code / signed_DAC_maximum",
                                  "variable_gain":"R_tile = [V_ADC_full_scale/(V_drive_full_scale*G_span)] * normalized_transimpedance_gain",
                                  "fixed_gain":"R_fixed uses minimum normalized gain; V_ref_tile/V_ref_max = min_gain/gain_tile"},
            "unassigned_physical_values":{"G_span_siemens":None,"G_base_siemens":None,"V_drive_full_scale":None,
                                          "V_ADC_full_scale":None,"transimpedance_ohms":None},
            "assumptions":["linear conductance","equal positive/negative baseline conductance cancels",
                           "virtual-ground column readout","common conductance span and DAC full scale across tiles",
                           "signed row drive and differential subtraction","ideal programmable gain/reference"],
            "rounding_check":{"training_vector_indices":sample_indices,"tile_count":len(scales),"tile_vector_cases":len(scales)*len(sample_indices),
                              "maximum_partial_abs_error":maximum_error,"limit":1e-5,"rows":checks,
                              "maximum_all_input_code_vectors_bound":maximum_bound,
                              "scope":"four training probes per tile plus analytic bound over all DAC-code vectors; compares real-valued code products to mathematical dots of rounded operands, excluding FP32 GEMM accumulation error and physical effects",
                              "residual_cause":"ideal equispaced real-valued DAC/conductance codes versus rounded float32 input and weight products"},
            "runtime":{"python":sys.version,"numpy":np.__version__,"torch":torch.__version__,"safetensors":safetensors.__version__},
            "analog_authorized":False,"physical_io_performed":False,
            "claim_boundary":"Relative gains and code requirements derived from real model data. No demonstrated device levels, gain circuit, voltage range, noise or timing/energy benefit."}
    (args.output/"normalized_array_scaling.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    (args.output/"manifest.json").write_text(json.dumps({p.name:digest(p) for p in args.output.iterdir() if p.is_file()},indent=2)+"\n")
    print(json.dumps({"tiles":len(scales),"gain":report["normalized_gain"],"maximum_partial_error":maximum_error,"output":str(args.output)}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality",type=Path,required=True)
    parser.add_argument("--weights",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
