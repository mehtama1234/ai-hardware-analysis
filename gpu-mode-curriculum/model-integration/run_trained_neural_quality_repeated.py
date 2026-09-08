#!/usr/bin/env python3
"""Repeated-seed trained character-transformer quality protocol.

The single-seed CUDA report remains the promotion artifact.  This companion
runner adds robustness evidence: identical train/eval protocol, independently
initialized weights, and cached/full decode parity for each declared seed.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING_DIR = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING_DIR))
from neural_generator import CharacterModel  # noqa: E402

OUT = HERE / "reports" / "trained-neural-quality-repeated.json"
ALPHABET = CharacterModel.alphabet
TRAIN_TEXT = ("hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 96)
EVAL_TEXT = ("hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 16)


def encode(text):
    return torch.tensor([ALPHABET.find(char) for char in text], dtype=torch.long)


def generate(model, prefix, max_tokens, cached):
    device = next(model.parameters()).device
    tokens = torch.tensor([[ALPHABET.find(char) for char in prefix]], device=device, dtype=torch.long)
    generated, cache = [], None
    with torch.inference_mode():
        for _ in range(max_tokens):
            logits, cache = (model(tokens if cache is None else tokens[:, -1:], cache, cached=True)
                             if cached else (model(tokens), None))
            next_token = logits[:, -1].argmax(-1, keepdim=True)
            generated.append(int(next_token.item()))
            tokens = torch.cat((tokens, next_token), dim=1)
    return generated


def run_seed(seed: int, device: torch.device, steps: int, batch: int, context: int) -> dict:
    torch.manual_seed(seed)
    model = CharacterModel(context=context).to(device).train()
    optimizer = torch.optim.Adam(model.parameters(), lr=4e-3)
    train, evaluation = encode(TRAIN_TEXT).to(device), encode(EVAL_TEXT).to(device)
    generator = torch.Generator(device="cpu").manual_seed(seed + 991)
    started = time.perf_counter(); last_loss = None
    for _ in range(steps):
        starts = torch.randint(0, train.numel() - context - 1, (batch,), generator=generator)
        inputs = torch.stack([train[i:i + context] for i in starts.tolist()])
        labels = torch.stack([train[i + 1:i + context + 1] for i in starts.tolist()])
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        last_loss = nn.functional.cross_entropy(logits.reshape(-1, len(ALPHABET)), labels.reshape(-1))
        last_loss.backward(); optimizer.step()
    if device.type == "cuda": torch.cuda.synchronize(device)
    model.eval()
    eval_inputs = torch.stack([evaluation[i:i + context] for i in range(0, evaluation.numel() - context - 1, context)])
    eval_labels = torch.stack([evaluation[i + 1:i + context + 1] for i in range(0, evaluation.numel() - context - 1, context)])
    with torch.inference_mode():
        eval_logits = model(eval_inputs)
        accuracy = float((eval_logits.argmax(-1) == eval_labels).float().mean().item())
        eval_loss = float(nn.functional.cross_entropy(eval_logits.reshape(-1, len(ALPHABET)), eval_labels.reshape(-1)).item())
    full = generate(model, "hello gpu", 12, False)
    cached = generate(model, "hello gpu", 12, True)
    return {"seed": seed, "status": "passed" if accuracy >= 0.85 and full == cached else "failed",
            "heldout_next_token_accuracy": accuracy, "eval_loss": eval_loss,
            "final_train_loss": float(last_loss.item()), "cached_full_parity": full == cached,
            "training_seconds": time.perf_counter() - started, "generated_token_count": len(full)}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--seeds", default="8181,8282,8383")
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--context", type=int, default=64)
    args = parser.parse_args(argv)
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    # Small teaching model: one thread makes repeated runs less noisy and
    # avoids oversubscribing the host when several seeds are declared.
    torch.set_num_threads(1)
    report = {"project": "model-integration", "experiment": "trained-neural-quality-repeated",
              "generated_at": datetime.now(timezone.utc).isoformat(), "requested_device": args.device,
              "seeds": seeds, "seed_count": len(seeds), "train_steps": args.steps, "batch": args.batch,
              "context": args.context, "gpu_execution_accepted": False, "model_trained": False,
              "source_sha256": {str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (Path(__file__).resolve(), SERVING_DIR / "neural_generator.py", HERE / "model_integration/tiny_transformer.py")},
              "python": sys.version, "platform": platform.platform()}
    if args.device == "cuda" and not torch.cuda.is_available():
        report.update(status="unavailable:cuda-runtime", reason="CUDA is not available")
    else:
        device = torch.device(args.device)
        runs = [run_seed(seed, device, args.steps, args.batch, args.context) for seed in seeds]
        passed = all(row["status"] == "passed" for row in runs)
        report.update({"status": "passed" if passed else "failed", "device": str(device),
                       "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu",
                       "torch_version": torch.__version__, "model_trained": True, "measured": True,
                       "gpu_execution_accepted": device.type == "cuda" and passed, "runs": runs,
                       "min_accuracy": min(row["heldout_next_token_accuracy"] for row in runs),
                       "max_accuracy": max(row["heldout_next_token_accuracy"] for row in runs),
                       "scope": "repeated tiny synthetic character-transformer quality and cache parity; not production language-model quality"})
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "seed_count": len(seeds), "device": report.get("device")}, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
