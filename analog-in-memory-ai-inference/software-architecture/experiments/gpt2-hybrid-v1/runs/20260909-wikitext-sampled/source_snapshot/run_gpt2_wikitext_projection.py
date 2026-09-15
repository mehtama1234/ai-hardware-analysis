#!/usr/bin/env python3
"""Pinned WikiText sample: whole-model sensitivity, not hardware performance."""
import argparse
from contextlib import nullcontext
import json
import math
from pathlib import Path
import shutil
import sys
import time
import urllib.request

import pyarrow.parquet as pq
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
from run_gpt2_hybrid_evaluation import digest, replace_forward
from tiled_projection_model import Profile, TiledProjection

DATA_REV = "b08601e04326c79dfdd32d625aee71d232d685c3"
MODEL_REV = "607a30d783dfa663caf39e06633721c8d4cfcd7e"


def windows(ids, count, length):
    """Evenly spaced, disjoint contexts across a split; one extra target token."""
    available = len(ids) // (length + 1)
    if count < 2 or available < count:
        raise ValueError("Need at least two nonoverlapping windows")
    starts = [(i * (available - 1) // (count - 1)) * (length + 1) for i in range(count)]
    return [(start, ids[start:start + length + 1]) for start in starts]


def run(args):
    if args.tokens < 2 or args.tokens > 1023 or args.threads < 1:
        raise ValueError("Invalid context length or thread count")
    args.output.mkdir(parents=True, exist_ok=False)
    snapshots = args.output / "source_snapshot"
    snapshots.mkdir()
    for name in [Path(__file__).name, "run_gpt2_hybrid_evaluation.py", "tiled_projection_model.py"]:
        shutil.copy2(Path(__file__).with_name(name), snapshots / name)
    protocol = {"dataset": "Salesforce/wikitext", "config": "wikitext-2-raw-v1", "revision": DATA_REV,
                "license": "CC-BY-SA-4.0", "attribution": "WikiText contributors and source Wikipedia authors; see pinned dataset card",
                "calibration_split": "train", "evaluation_split": "test", "calibration_windows": 16,
                "evaluation_windows": args.windows, "predictions_per_window": args.tokens,
                "selection": "evenly spaced nonoverlapping windows in newline-joined split rows; no padding; reset context per window",
                "scope": "sampled encyclopedia language modeling; not full WikiText perplexity or general task acceptance",
                "screen": {"maximum_nll_increase_nats": .05, "minimum_argmax_agreement": .99,
                           "status": "provisional engineering screen inherited before this run"},
                "model_revision": MODEL_REV, "seed": 8181, "command": sys.argv}
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    torch.set_num_threads(args.threads)
    torch.manual_seed(8181)
    snapshot = Path(snapshot_download("openai-community/gpt2", revision=MODEL_REV, local_files_only=True))
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True)
    selections = {}
    for split, count in [("train", 16), ("test", args.windows)]:
        dest = args.output / (split + ".parquet")
        url = f"https://huggingface.co/datasets/Salesforce/wikitext/resolve/{DATA_REV}/wikitext-2-raw-v1/{split}-00000-of-00001.parquet"
        print(f"Downloading pinned {split} split", flush=True)
        with urllib.request.urlopen(url, timeout=90) as response, dest.open("wb") as out:
            shutil.copyfileobj(response, out)
        rows = pq.read_table(dest)["text"].to_pylist()
        ids = tokenizer.encode("\n".join(rows), add_special_tokens=False, verbose=False)
        selections[split] = windows(ids, count, args.tokens)
        protocol[split] = {"url": url, "sha256": digest(dest), "rows": len(rows), "total_tokens": len(ids),
                           "windows": [{"start": start, "ids": values} for start, values in selections[split]]}
    card = args.output / "DATASET_CARD.md"
    with urllib.request.urlopen(f"https://huggingface.co/datasets/Salesforce/wikitext/resolve/{DATA_REV}/README.md", timeout=90) as response:
        card.write_bytes(response.read())
    protocol["dataset_card_sha256"] = digest(card)
    (args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    print("Loading GPT-2 and calibrating on train only", flush=True)
    model = AutoModelForCausalLM.from_pretrained(snapshot, local_files_only=True, attn_implementation="eager").eval()
    module = model.get_submodule("transformer.h.0.mlp.c_fc")
    bound = [0.0]
    def calibrate(_module, inputs):
        bound[0] = max(bound[0], float(inputs[0].abs().max()))
    hook = module.register_forward_pre_hook(calibrate)
    try:
        with torch.inference_mode():
            for _, ids in selections["train"]:
                model(torch.tensor([ids]), use_cache=False)
    finally:
        hook.remove()
    variants = [("ideal", Profile(), True), ("adc8", Profile(adc_bits=8), False),
                ("adc12", Profile(), False), ("adc12_noise001", Profile(read_noise_fraction=.001), False)]
    projections = {name: TiledProjection(module.weight, module.bias, bound[0], profile, 8181)
                   for name, profile, _ in variants}
    rows = []
    with torch.inference_mode(), (args.output / "rows.jsonl").open("w") as stream:
        for index, (start, ids) in enumerate(selections["test"]):
            tokens = torch.tensor([ids])
            baseline = model(tokens, use_cache=False).logits[:, :-1].float()
            target = tokens[:, 1:].reshape(-1)
            base_nll = float(torch.nn.functional.cross_entropy(baseline.reshape(-1, baseline.shape[-1]), target, reduction="sum"))
            for name, _, ideal in variants:
                projection = projections[name]
                before = time.perf_counter()
                with replace_forward(module, lambda x: projection(x, ideal=ideal)):
                    candidate = model(tokens, use_cache=False).logits[:, :-1].float()
                row = {"window": index, "start": start, "variant": name, "tokens": target.numel(),
                       "baseline_nll_sum": base_nll,
                       "candidate_nll_sum": float(torch.nn.functional.cross_entropy(candidate.reshape(-1, candidate.shape[-1]), target, reduction="sum")),
                       "argmax_matches": int((candidate.argmax(-1) == baseline.argmax(-1)).sum()),
                       "max_logit_error": float((candidate-baseline).abs().max()),
                       "cpu_emulation_seconds": time.perf_counter()-before}
                rows.append(row)
                stream.write(json.dumps(row) + "\n")
                stream.flush()
            restored = model(tokens, use_cache=False).logits[:, :-1].float()
            if not torch.equal(restored, baseline):
                raise RuntimeError("Restored digital fallback differs")
            print(f"Completed window {index+1}/{args.windows}", flush=True)
    summaries = {}
    for name, _, _ in variants:
        subset = [r for r in rows if r["variant"] == name]
        n = sum(r["tokens"] for r in subset)
        a = sum(r["baseline_nll_sum"] for r in subset)/n
        b = sum(r["candidate_nll_sum"] for r in subset)/n
        agreement = sum(r["argmax_matches"] for r in subset)/n
        summaries[name] = {"tokens": n, "baseline_nll": a, "candidate_nll": b, "nll_increase": b-a,
                           "baseline_sample_perplexity": math.exp(a), "candidate_sample_perplexity": math.exp(b),
                           "argmax_agreement": agreement, "maximum_logit_error": max(r["max_logit_error"] for r in subset),
                           "screen_pass": b-a <= .05 and agreement >= .99,
                           "contract": projections[name].contract(), "trace": projections[name].trace}
    if summaries["ideal"]["maximum_logit_error"] >= .001:
        raise RuntimeError("Ideal tiled control failed")
    report = {"protocol": protocol, "variants": summaries, "digital_fallback_exact_all_windows": True,
              "ideal_control_pass": True, "analog_authorized": False, "physical_profile_calibrated": False,
              "claim": "Whole GPT-2 sensitivity on sampled WikiText test contexts; no measured hybrid performance or energy",
              "runtime": {"torch": torch.__version__, "transformers": transformers.__version__, "threads": args.threads},
              "model_files": {p.name: digest(p) for p in snapshot.iterdir() if p.is_file()}}
    (args.output / "result.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    files = [p for p in args.output.rglob("*") if p.is_file()]
    (args.output / "manifest.json").write_text(json.dumps({str(p.relative_to(args.output)): digest(p) for p in files}, indent=2)+"\n")
    print(json.dumps({name: {k:v for k,v in item.items() if k not in ("contract", "trace")} for name,item in summaries.items()}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--windows", type=int, default=32)
    parser.add_argument("--tokens", type=int, default=128)
    parser.add_argument("--threads", type=int, default=2)
    run(parser.parse_args())
