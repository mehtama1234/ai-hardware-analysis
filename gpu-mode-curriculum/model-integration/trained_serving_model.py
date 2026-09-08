"""Small deterministic trained-model adapter for the serving vertical slice.

The corpus is synthetic and deliberately narrow.  This module proves that a
trained state can cross the quality -> serving boundary; it does not claim
production language quality.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
import sys

import torch
from torch import nn

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from neural_generator import CharacterModel  # noqa: E402

ALPHABET = CharacterModel.alphabet
TRAIN_TEXT = "hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 96
EVAL_TEXT = "hello gpu systems\nattention cache decode\nmemory traffic kernel\n" * 16


def encode(text: str) -> torch.Tensor:
    return torch.tensor([ALPHABET.find(char) for char in text], dtype=torch.long)


def train_state(*, device: torch.device, steps: int = 200, batch: int = 32,
                context: int = 128, seed: int = 8181) -> tuple[dict[str, torch.Tensor], dict]:
    """Train the synthetic character model and return a portable state dict."""
    torch.manual_seed(seed)
    model = CharacterModel(context=context, hidden=128, heads=8).to(device).train()
    optimizer = torch.optim.Adam(model.parameters(), lr=4e-3)
    train = encode(TRAIN_TEXT).to(device)
    evaluation = encode(EVAL_TEXT).to(device)
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
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    model.eval()
    eval_inputs = torch.stack([
        evaluation[index:index + context]
        for index in range(0, evaluation.numel() - context - 1, context)
    ])
    eval_labels = torch.stack([
        evaluation[index + 1:index + context + 1]
        for index in range(0, evaluation.numel() - context - 1, context)
    ])
    with torch.inference_mode():
        eval_logits = model(eval_inputs)
        accuracy = float((eval_logits.argmax(-1) == eval_labels).float().mean().item())
        eval_loss = float(nn.functional.cross_entropy(
            eval_logits.reshape(-1, len(ALPHABET)), eval_labels.reshape(-1)
        ).item())
    state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    digest = hashlib.sha256()
    for key in sorted(state):
        digest.update(key.encode())
        digest.update(state[key].numpy().tobytes())
    return state, {
        "trained": True, "seed": seed, "steps": steps, "batch": batch,
        "context": context, "hidden": 128, "heads": 8,
        "training_seconds": time.perf_counter() - started,
        "final_train_loss": float(last_loss.item()), "eval_loss": eval_loss,
        "heldout_next_token_accuracy": accuracy, "state_sha256": digest.hexdigest(),
        "quality_passed": accuracy >= 0.85,
    }
