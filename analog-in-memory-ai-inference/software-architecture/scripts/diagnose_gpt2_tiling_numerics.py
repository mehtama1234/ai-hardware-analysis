#!/usr/bin/env python3
"""Compare native/tiled projection rounding without changing benchmark gates."""
import argparse
import json
from pathlib import Path
import shutil

import torch
from transformers import AutoModelForCausalLM
from huggingface_hub import snapshot_download
from run_gpt2_hybrid_evaluation import digest, replace_forward
from tiled_projection_model import Profile, TiledProjection


def metrics(reference, candidate):
    difference = (reference-candidate).abs()
    flat = int(difference.argmax())
    coord = []
    for size in reversed(reference.shape):
        coord.insert(0, flat % size)
        flat //= size
    return {"maximum_abs_error": float(difference.max()),
            "relative_l2": float(torch.linalg.vector_norm(reference-candidate) / torch.linalg.vector_norm(reference)),
            "worst_coordinate": coord, "reference_at_worst": float(reference[tuple(coord)]),
            "candidate_at_worst": float(candidate[tuple(coord)]),
            "max_error_over_1e5_scaled_tolerance": float((difference / (1e-5 + 1e-5*reference.abs())).max())}


def run(args):
    args.output.mkdir(parents=True, exist_ok=False)
    for name in [Path(__file__).name, "run_gpt2_hybrid_evaluation.py", "tiled_projection_model.py"]:
        shutil.copy2(Path(__file__).with_name(name), args.output / name)
    protocol = json.loads((args.package / "protocol.json").read_text())
    torch.set_num_threads(2)
    torch.manual_seed(8181)
    snapshot = snapshot_download("openai-community/gpt2", revision=protocol["model_revision"], local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, attn_implementation="eager").eval()
    module = model.get_submodule("transformer.h.0.mlp.c_fc")
    rows = []
    with torch.inference_mode():
        for index in args.windows:
            tokens = torch.tensor([protocol["test"]["windows"][index]["ids"]])
            captured = []
            hook = module.register_forward_hook(lambda _m, inputs, output: captured.append((inputs[0].clone(), output.clone())))
            baseline = model(tokens, use_cache=False).logits[:, :-1].float()
            hook.remove()
            x, native = captured[0]
            projection = TiledProjection(module.weight, module.bias, float(x.abs().max()), Profile())
            dense64 = x.double() @ module.weight.double() + module.bias.double()
            tiled64 = TiledProjection(module.weight.double(), module.bias.double(), float(x.abs().max()), Profile())
            for name, forward in [("tiled_fp32", lambda value: projection(value, ideal=True)),
                                  ("tiled_fp64_cast_fp32", lambda value: tiled64(value.double(), ideal=True).float()),
                                  ("dense_fp64_cast_fp32", lambda value: (value.double() @ module.weight.double()+module.bias.double()).float())]:
                local = forward(x)
                with replace_forward(module, forward):
                    candidate = model(tokens, use_cache=False).logits[:, :-1].float()
                lp = baseline.double().log_softmax(-1)
                lq = candidate.double().log_softmax(-1)
                target = tokens[:, 1:].unsqueeze(-1)
                row = {"window": index, "variant": name, "projection_vs_native": metrics(native, local),
                       "projection_vs_dense64": metrics(dense64, local.double()),
                       "native_projection_vs_dense64": metrics(dense64, native.double()),
                       "logits": metrics(baseline, candidate),
                       "log_probabilities": metrics(lp, lq),
                       "mean_nll_difference": float((lp-lq).gather(-1,target).mean()),
                       "maximum_target_log_probability_error": float((lp-lq).gather(-1,target).abs().max()),
                       "argmax_matches": int((baseline.argmax(-1)==candidate.argmax(-1)).sum()),
                       "tokens": baseline.shape[1]}
                rows.append(row)
                print(json.dumps(row), flush=True)
    result = {"status": "numerical_diagnosis_only", "original_benchmark_remains_rejected": True,
              "protocol_sha256": digest(args.package / "protocol.json"), "rows": rows,
              "sources": {p.name:digest(p) for p in args.output.iterdir() if p.is_file()}}
    (args.output / "result.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--windows",type=int,nargs="+",default=[21,23])
    run(parser.parse_args())
