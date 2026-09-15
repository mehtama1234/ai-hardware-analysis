#!/usr/bin/env python3
"""Evaluate one real GPT-2 projection with an explicit provisional array model."""

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import torch
import transformers
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

from tiled_projection_model import Profile, TiledProjection

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
DEFAULT_FIXTURE = ROOT / "experiments/gpt2-hybrid-v1/fixture.json"
EDA = REPO / "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters"


def synchronize(device):
    """Make wall-time measurements include queued CUDA work."""
    if torch.device(device).type == "cuda":
        torch.cuda.synchronize(torch.device(device))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source(path):
    return {"path": str(path), "sha256": digest(path)}


@contextmanager
def replace_forward(module, replacement):
    original = module.forward
    module.forward = replacement
    try:
        yield
    finally:
        module.forward = original


def evaluate(model, tokenizer, texts, new_tokens, projection=None, device="cpu"):
    results = []
    for text in texts:
        encoded = {key: value.to(device) for key, value in tokenizer(text, return_tensors="pt").items()}
        if projection:
            projection.phase = "teacher_forced_prefill"
        synchronize(device)
        started = time.perf_counter()
        with torch.inference_mode():
            logits = model(**encoded, use_cache=False).logits.float()
            target = encoded["input_ids"][:, 1:]
            nll = torch.nn.functional.cross_entropy(logits[:, :-1].reshape(-1, logits.shape[-1]),
                                                   target.reshape(-1), reduction="sum")
            if projection:
                projection.phase = "generation_prefill_and_cached_decode"
            generated = model.generate(**encoded, max_new_tokens=new_tokens, do_sample=False,
                                       use_cache=True, pad_token_id=tokenizer.eos_token_id)
        synchronize(device)
        results.append({"logits": logits, "token_count": target.numel(), "nll_sum": float(nll),
                        "generated_ids": generated[0, encoded["input_ids"].shape[-1]:].tolist(),
                        "reference_wall_ms": (time.perf_counter() - started) * 1000})
    return results


def compare(baseline, candidate):
    count = sum(row["token_count"] for row in baseline)
    matches = total = 0
    rows = []
    for ref, test in zip(baseline, candidate):
        a, b = ref["logits"][:, :-1], test["logits"][:, :-1]
        equal = int((a.argmax(-1) == b.argmax(-1)).sum())
        matches += equal
        total += ref["token_count"]
        rows.append({"predicted_tokens": ref["token_count"], "argmax_matches": equal,
                     "logit_relative_l2": float(torch.linalg.vector_norm(b - a) / torch.linalg.vector_norm(a).clamp_min(1e-12)),
                     "maximum_logit_abs_error": float((b - a).abs().max()),
                     "baseline_generated_ids": ref["generated_ids"], "candidate_generated_ids": test["generated_ids"],
                     "generation_exact_match": ref["generated_ids"] == test["generated_ids"],
                     "baseline_reference_wall_ms": ref["reference_wall_ms"],
                     "candidate_reference_wall_ms": test["reference_wall_ms"]})
    baseline_nll = sum(row["nll_sum"] for row in baseline) / count
    candidate_nll = sum(row["nll_sum"] for row in candidate) / count
    return {"predicted_tokens": count, "baseline_nll_nats_per_token": baseline_nll,
            "candidate_nll_nats_per_token": candidate_nll, "nll_increase_nats": candidate_nll - baseline_nll,
            "teacher_forced_argmax_agreement": matches / total,
            "generation_exact_match_count": sum(row["generation_exact_match"] for row in rows),
            "rows": rows}


def run(args):
    if args.threads < 1:
        raise ValueError("threads must be positive")
    # An existing result is immutable; interrupted directories can be inspected separately.
    args.output.mkdir(parents=True, exist_ok=False)
    fixture = json.loads(args.fixture.read_text())
    torch.set_num_threads(args.threads)
    torch.manual_seed(fixture["seed"])
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("requested CUDA device but CUDA is unavailable")
    snapshot = (Path(args.snapshot_path) if args.snapshot_path else
                Path(snapshot_download(fixture["model_id"], revision=fixture["revision"], local_files_only=True)))
    if not snapshot.exists():
        raise FileNotFoundError(f"model snapshot does not exist: {snapshot}")
    print("Loading pinned cached GPT-2", flush=True)
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, use_safetensors=True,
                                               attn_implementation="eager").to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    module = model.get_submodule(fixture["target_module"])
    activation_bound = [0.0]

    def calibrate(_module, inputs):
        activation_bound[0] = max(activation_bound[0], float(inputs[0].abs().max()))

    hook = module.register_forward_pre_hook(calibrate)
    try:
        with torch.inference_mode():
            for text in fixture["calibration"]:
                encoded = {key: value.to(device) for key, value in tokenizer(text, return_tensors="pt").items()}
                model(**encoded, use_cache=False)
    finally:
        hook.remove()
    baseline = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device)
    variants = []
    projection_tensor_outputs = {}
    for name, profile, ideal in [
        ("ideal_tiled_control", Profile(), True),
        ("dac10_weight8_adc8", Profile(adc_bits=8), False),
        ("dac10_weight8_adc12", Profile(adc_bits=12), False),
        ("dac10_weight8_adc12_noise001", Profile(adc_bits=12, read_noise_fraction=0.001), False),
    ]:
        print(f"Evaluating {name}", flush=True)
        projection = TiledProjection(module.weight, module.bias, activation_bound[0], profile, fixture["seed"])
        with replace_forward(module, lambda x: projection(x, ideal=ideal)):
            candidate = evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], projection, device=device)
        projection_tensor_outputs[name] = torch.cat(
            [torch.from_numpy(row) for row in projection.output_vectors], dim=0
        ).numpy()
        quality = compare(baseline, candidate)
        screen = fixture["exploratory_screen"]
        variants.append({"id": name, "contract": projection.contract(), "quality": quality,
                         "exploratory_quality_screen_pass": quality["nll_increase_nats"] <= screen["maximum_nll_increase_nats"]
                         and quality["teacher_forced_argmax_agreement"] >= screen["minimum_teacher_forced_argmax_agreement"],
                         "trace": projection.trace})
    # Re-execute restored native code: software fallback must preserve the whole model output.
    fallback = compare(baseline, evaluate(model, tokenizer, fixture["evaluation"], fixture["max_new_tokens"], device=device))
    fallback_pass = all(row["maximum_logit_abs_error"] == 0 and row["generation_exact_match"] for row in fallback["rows"])
    ideal_pass = all(row["maximum_logit_abs_error"] < 1e-3 and row["generation_exact_match"]
                     for row in variants[0]["quality"]["rows"])
    if not fallback_pass or not ideal_pass:
        raise RuntimeError("Digital fallback or ideal tiled control failed; reject this evaluation")

    physical_path = args.converter_result
    physical = json.loads(physical_path.read_text())
    netlist = Path(physical["netlist"])
    netlist_hash_matches = netlist.exists() and digest(netlist) == physical["netlist_sha256"]
    physical_evidence = {"source": source(physical_path), "accepted_converter": physical.get("accepted_converter", False),
                         "netlist_hash_matches": netlist_hash_matches,
                         "measured_case_count": physical.get("measured_case_count"),
                         "polarity_pass_count": physical.get("polarity_pass_count"),
                         "logic_margin_pass_count": physical.get("logic_margin_pass_count"),
                         "used_as_numeric_error_profile": False,
                         "reason": "A comparator boundary test is not an ADC transfer/noise/energy profile for this array."}
    gpu_path = REPO / "gpu-mode-curriculum/gpu-runs/imports/colab-real-model-persistent-page-cache-long-gpt2-20260909/real-model-device-resident-arrival-load.json"
    gpu = json.loads(gpu_path.read_text())
    tensor_path = args.output / "projection_tensors.npz"
    import numpy as np
    np.savez_compressed(tensor_path, **{
        name: values for name, values in projection_tensor_outputs.items()
    })
    report = {
        "schema_version": "gpt2-hybrid-projection-evaluation-v0.1",
        "evidence_kind": "real_pretrained_model_with_provisional_numerical_array_on_cpu",
        "sources": {"fixture": source(args.fixture), "runner": source(Path(__file__)),
                    "projection_model": source(Path(__file__).with_name("tiled_projection_model.py")),
                    "model_snapshot": [source(p) for p in sorted(snapshot.iterdir()) if p.is_file()],
                    "projection_tensor_artifact": source(tensor_path)},
        "model": {"id": fixture["model_id"], "revision": fixture["revision"], "target_module": fixture["target_module"],
                  "parameter_count": sum(p.numel() for p in model.parameters())},
        "runtime": {"python": sys.version, "torch": torch.__version__, "transformers": transformers.__version__,
                    "platform": platform.platform(), "device": str(device), "threads": args.threads,
                    "command": sys.argv},
        "fixture": fixture,
        "variants": variants,
        "controls": {"ideal_tiled_control_pass": ideal_pass, "digital_fallback_pass": fallback_pass, "fallback_quality": fallback},
        "physical_converter": physical_evidence,
        "measured_gpu_reference": {"source": source(gpu_path), "model_profile": gpu["model_profile"],
                                   "protocol": gpu["protocol"], "result": gpu["result"],
                                   "join_scope": "context only: different prompts and execution device; no CPU-to-T4 speedup or energy inference"},
        "placement": {"candidate": fixture["target_module"], "authorized_analog_modules": [],
                      "execution": "native_digital_fallback", "reason": "Array/converter mapping is provisional and no matched physical costs or task-qualified target exist.",
                      "always_digital": ["attention", "KV_cache", "normalization", "nonlinearity", "remaining_projections", "logits", "scheduler"]},
        "decision": "hybrid_hardware_benefit_unproven",
        "next_required_evidence": ["versioned representative token dataset and frozen task acceptance contract",
                                   "matched array technology and signed precision implementation",
                                   "accepted ADC transfer/noise/settling profile tied to this mapping",
                                   "same-target projection timing and energy including boundary transfers",
                                   "controller execution and measured analog hardware task comparison"],
        "claim_boundary": "Real GPT-2 sensitivity to one provisional tiled projection. CPU emulation time is not hybrid hardware latency. No silicon, energy advantage, or full-task acceptance claim.",
    }
    destination = args.output / "evaluation.json"
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    lines = ["# GPT-2 hybrid projection evaluation", "", report["claim_boundary"], "",
             "| Variant | NLL increase (nats/token) | Argmax agreement | Exact generations | Exploratory screen |",
             "| --- | ---: | ---: | ---: | --- |"]
    for variant in variants:
        q = variant["quality"]
        lines.append(f"| {variant['id']} | {q['nll_increase_nats']:.6f} | {q['teacher_forced_argmax_agreement']:.4f} | {q['generation_exact_match_count']}/{len(q['rows'])} | {variant['exploratory_quality_screen_pass']} |")
    lines.extend(["", "Digital fallback and ideal tiled controls passed.", "",
                  f"Physical converter accepted: {physical_evidence['accepted_converter']}; extracted netlist hash matches: {netlist_hash_matches}.",
                  "", "Hardware benefit remains unproven. Conversion counts are explicit; matched physical costs are missing."])
    (args.output / "README.md").write_text("\n".join(lines) + "\n")
    (args.output / "manifest.json").write_text(json.dumps({"files": [source(destination), source(args.output / "README.md")]}, indent=2) + "\n")
    print(json.dumps({"output": str(destination), "decision": report["decision"], "controls_pass": True}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--device", default="cpu", help="torch device, for example cpu or cuda")
    parser.add_argument("--snapshot-path", help="use an already downloaded exact snapshot directory")
    parser.add_argument("--converter-result", type=Path,
                        default=EDA / "active-converter-macro-transient/20260909T075601726677Z/result.json")
    run(parser.parse_args())
