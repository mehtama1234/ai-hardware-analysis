#!/usr/bin/env python3
"""Train a tiny character transformer and measure held-out quality on CUDA."""
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

OUT = HERE / "reports" / "trained-neural-quality-cuda.json"
ALPHABET = CharacterModel.alphabet
TRAIN_TEXT = ("hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 96)
EVAL_TEXT = ("hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 16)


def encode(text):
    return torch.tensor([ALPHABET.find(char) for char in text], dtype=torch.long)


def generate(model, prefix, max_tokens, cached):
    tokens = torch.tensor([[ALPHABET.find(char) for char in prefix]], device=next(model.parameters()).device, dtype=torch.long)
    generated = []
    cache = None
    with torch.inference_mode():
        for _ in range(max_tokens):
            if cached:
                logits, cache = model(tokens if cache is None else tokens[:, -1:], cache, cached=True)
            else:
                logits = model(tokens)
            next_token = logits[:, -1].argmax(-1, keepdim=True)
            generated.append(int(next_token.item()))
            tokens = torch.cat((tokens, next_token), dim=1)
    return generated


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda", choices=("cpu", "cuda"))
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--context", type=int, default=64)
    args = parser.parse_args(argv)
    report = {
        "project": "model-integration",
        "experiment": "trained-neural-quality-cuda",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "requested_device": args.device,
        "train_steps": args.steps,
        "batch": args.batch,
        "context": args.context,
        "gpu_execution_accepted": False,
        "model_trained": False,
        "source_sha256": {
            str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__).resolve(), SERVING_DIR / "neural_generator.py", HERE / "model_integration/tiny_transformer.py")
        },
        "python": sys.version,
        "platform": platform.platform(),
    }
    if args.device == "cuda" and not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available", "scope": "trained quality request; no device"})
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2) + "\n"); print(json.dumps(report, indent=2)); return 2
    device = torch.device(args.device)
    torch.manual_seed(8181)
    model = CharacterModel(context=args.context).to(device)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=4e-3)
    train = encode(TRAIN_TEXT).to(device)
    evaluation = encode(EVAL_TEXT).to(device)
    generator = torch.Generator(device="cpu").manual_seed(991)
    started = time.perf_counter()
    last_loss = None
    for _ in range(args.steps):
        starts = torch.randint(0, train.numel() - args.context - 1, (args.batch,), generator=generator)
        inputs = torch.stack([train[index:index + args.context] for index in starts.tolist()])
        labels = torch.stack([train[index + 1:index + args.context + 1] for index in starts.tolist()])
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        last_loss = nn.functional.cross_entropy(logits.reshape(-1, len(ALPHABET)), labels.reshape(-1))
        last_loss.backward()
        optimizer.step()
    if device.type == "cuda": torch.cuda.synchronize(device)
    training_seconds = time.perf_counter() - started
    model.eval()
    eval_inputs = torch.stack([evaluation[index:index + args.context] for index in range(0, evaluation.numel() - args.context - 1, args.context)])
    eval_labels = torch.stack([evaluation[index + 1:index + args.context + 1] for index in range(0, evaluation.numel() - args.context - 1, args.context)])
    with torch.inference_mode():
        eval_logits = model(eval_inputs)
        predictions = eval_logits.argmax(-1)
        accuracy = float((predictions == eval_labels).float().mean().item())
        eval_loss = float(nn.functional.cross_entropy(eval_logits.reshape(-1, len(ALPHABET)), eval_labels.reshape(-1)).item())
    prefix = "hello gpu"
    full_tokens = generate(model, prefix, 12, cached=False)
    cached_tokens = generate(model, prefix, 12, cached=True)
    parity = full_tokens == cached_tokens
    report.update({
        "status": "passed" if accuracy >= 0.85 and parity else "failed",
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu",
        "torch_version": torch.__version__,
        "model_trained": True,
        "training_seconds": training_seconds,
        "final_train_loss": float(last_loss.item()),
        "eval_loss": eval_loss,
        "heldout_next_token_accuracy": accuracy,
        "cached_full_parity": parity,
        "generated_token_count": len(full_tokens),
        "measured": True,
        "gpu_execution_accepted": device.type == "cuda" and accuracy >= 0.85 and parity,
        "scope": "tiny synthetic character-transformer quality and cache parity; not language-model benchmark or production serving capacity",
    })
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n"); print(json.dumps(report, indent=2)); return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
