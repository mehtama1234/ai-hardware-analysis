#!/usr/bin/env python3
"""Broader trained-quality matrix for the serving model adapter.

This is deliberately still a synthetic character-model protocol.  It expands
the evidence across disjoint held-out corpora, model widths, and seeds without
turning a local quality gate into a production language-model claim.
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
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from neural_generator import CharacterModel  # noqa: E402

OUT = HERE / "reports" / "trained-quality-matrix.json"
ALPHABET = CharacterModel.alphabet
CORPORA = {
    "systems": {
        "train": ("gpu kernels move memory\nattention keeps cache\nthreads launch work\n" * 96),
        "eval": ("memory kernels keep attention\ncache moves through threads\n" * 24),
        "prefix": "gpu kernels",
    },
    "serving": {
        "train": ("request enters queue\nbatch shares decode\nlatency follows load\n" * 96),
        "eval": ("decode enters batch\nload follows latency\n" * 24),
        "prefix": "request enters",
    },
}
CONFIGS = ((32, 4, 64), (64, 4, 96))


def encode(text: str) -> torch.Tensor:
    ids = [ALPHABET.find(char) for char in text]
    if any(index < 0 for index in ids):
        raise ValueError("corpus contains a character outside the model alphabet")
    return torch.tensor(ids, dtype=torch.long)


def generate(model, prefix: str, max_tokens: int, *, cached: bool) -> list[int]:
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


def run_case(*, corpus_name: str, seed: int, hidden: int, heads: int,
             context: int, device: torch.device, steps: int, batch: int,
             threshold: float) -> dict:
    corpus = CORPORA[corpus_name]
    torch.manual_seed(seed)
    model = CharacterModel(context=context, hidden=hidden, heads=heads).to(device).train()
    optimizer = torch.optim.Adam(model.parameters(), lr=4e-3)
    train, evaluation = encode(corpus["train"]).to(device), encode(corpus["eval"]).to(device)
    generator = torch.Generator(device="cpu").manual_seed(seed + 991)
    started = time.perf_counter()
    last_loss = None
    for _ in range(steps):
        starts = torch.randint(0, train.numel() - context - 1, (batch,), generator=generator)
        inputs = torch.stack([train[index:index + context] for index in starts.tolist()])
        labels = torch.stack([train[index + 1:index + context + 1] for index in starts.tolist()])
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        last_loss = nn.functional.cross_entropy(logits.reshape(-1, len(ALPHABET)), labels.reshape(-1))
        last_loss.backward()
        optimizer.step()
    model.eval()
    eval_inputs = torch.stack([evaluation[index:index + context]
                               for index in range(0, evaluation.numel() - context - 1, context)])
    eval_labels = torch.stack([evaluation[index + 1:index + context + 1]
                               for index in range(0, evaluation.numel() - context - 1, context)])
    with torch.inference_mode():
        eval_logits = model(eval_inputs)
        accuracy = float((eval_logits.argmax(-1) == eval_labels).float().mean().item())
        eval_loss = float(nn.functional.cross_entropy(
            eval_logits.reshape(-1, len(ALPHABET)), eval_labels.reshape(-1)).item())
    full = generate(model, corpus["prefix"], 12, cached=False)
    cached = generate(model, corpus["prefix"], 12, cached=True)
    return {
        "corpus": corpus_name, "seed": seed, "hidden": hidden, "heads": heads,
        "context": context, "steps": steps, "heldout_next_token_accuracy": accuracy,
        "eval_loss": eval_loss, "final_train_loss": float(last_loss.item()),
        "cached_full_parity": full == cached, "generated_token_count": len(full),
        "quality_passed": accuracy >= threshold and full == cached,
        "training_seconds": time.perf_counter() - started,
    }


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--seeds", default="8181,8282")
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--threshold", type=float, default=0.35)
    args = parser.parse_args(argv)
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    torch.set_num_threads(1)
    sources = (Path(__file__).resolve(), SERVING / "neural_generator.py",
               HERE / "model_integration/tiny_transformer.py")
    report = {
        "project": "model-integration", "experiment": "trained-quality-matrix",
        "generated_at": datetime.now(timezone.utc).isoformat(), "requested_device": args.device,
        "corpora": sorted(CORPORA), "configs": [list(row) for row in CONFIGS], "seeds": seeds,
        "train_steps": args.steps, "batch": args.batch, "quality_threshold": args.threshold,
        "model_trained": False, "gpu_execution_accepted": False,
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sources},
        "python": sys.version, "platform": platform.platform(),
    }
    if args.device == "cuda" and not torch.cuda.is_available():
        report.update({"status": "unavailable:cuda-runtime", "reason": "CUDA is not available"})
    else:
        device = torch.device(args.device)
        runs = [run_case(corpus_name=corpus, seed=seed, hidden=hidden, heads=heads,
                         context=context, device=device, steps=args.steps, batch=args.batch,
                         threshold=args.threshold)
                for corpus in sorted(CORPORA) for hidden, heads, context in CONFIGS for seed in seeds]
        report.update({
            "status": "passed" if all(row["quality_passed"] for row in runs) else "failed",
            "device": str(device), "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "cpu",
            "torch_version": torch.__version__, "model_trained": True, "measured": True,
            "gpu_execution_accepted": device.type == "cuda" and all(row["quality_passed"] for row in runs),
            "runs": runs, "run_count": len(runs),
            "min_accuracy": min(row["heldout_next_token_accuracy"] for row in runs),
            "max_accuracy": max(row["heldout_next_token_accuracy"] for row in runs),
            "scope": "two synthetic character corpora, two model widths, and repeated seeds with held-out next-token quality and cached/full decode parity; not production language-model quality or capacity",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "run_count": report.get("run_count", 0),
                      "min_accuracy": report.get("min_accuracy")}, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
