#!/usr/bin/env python3
"""Measure greedy draft/target speculative decoding on one CUDA device.

The draft and target are deliberately small character transformers so the lab
can exercise the control plane without downloading a model.  The target's
greedy output remains authoritative: every accepted draft token is compared to
the target prediction, rejected suffixes are rolled back, and the final token
stream must match ordinary target decoding exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
SERVING = ROOT / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
if not SERVING.is_dir():
    SERVING = REPO / "gpu-kernels-serving-lab" / "13-capstone-mini-serving-engine"
sys.path.insert(0, str(SERVING))
from neural_generator import NeuralGenerator  # noqa: E402

OUT = HERE / "reports" / "speculative-decoding-cuda.json"
SCENARIOS = (
    {"id": "exact-draft", "prompt": "attention cache", "max_tokens": 24, "draft_width": 4, "draft_seed": 151},
    {"id": "shifted-draft", "prompt": "attention cache", "max_tokens": 24, "draft_width": 4, "draft_seed": 152},
    {"id": "wide-draft", "prompt": "gpu serving", "max_tokens": 24, "draft_width": 6, "draft_seed": 152},
    {"id": "long-prefix", "prompt": "attention cache " * 3, "max_tokens": 20, "draft_width": 5, "draft_seed": 152},
)
HIDDEN = 128
HEADS = 8


def _tokens_to_text(model: NeuralGenerator, tokens: list[int]) -> str:
    return "".join(model.model.alphabet[token] for token in tokens)


@torch.inference_mode()
def verify_draft(target: NeuralGenerator, prefix: str, draft_tokens: list[int]) -> dict:
    """Verify a draft suffix against target greedy predictions.

    The returned correction is the target token at the first mismatch.  When
    the entire draft is accepted, `correction` is the bonus target token after
    the draft; the caller may commit it as the next exact token.
    """
    ids = target.encode(prefix)
    tokens = torch.tensor([ids], dtype=torch.long, device=target.device)
    logits, cache = target.model(tokens, cached=True)
    accepted = 0
    for candidate in draft_tokens:
        predicted = int(logits[:, -1].argmax(-1).item())
        if predicted != candidate:
            return {"accepted": accepted, "correction": predicted, "rollback": len(draft_tokens) - accepted, "target_steps": accepted + 1}
        accepted += 1
        next_token = torch.tensor([[candidate]], dtype=torch.long, device=target.device)
        logits, cache = target.model(next_token, cache=cache, cached=True)
    correction = int(logits[:, -1].argmax(-1).item())
    return {"accepted": accepted, "correction": correction, "rollback": 0, "target_steps": accepted + 1}


def speculative_generate(target: NeuralGenerator, draft: NeuralGenerator, prompt: str, max_tokens: int, width: int) -> tuple[list[int], dict]:
    generated: list[int] = []
    prefix = prompt
    stats = {"draft_tokens": 0, "accepted_tokens": 0, "rollback_tokens": 0,
             "rollback_count": 0, "target_verify_steps": 0, "kv_tokens_committed": 0,
             "draft_rounds": 0}
    while len(generated) < max_tokens:
        count = min(width, max_tokens - len(generated))
        proposed, _ = draft.generate(prefix, count, cached=True, cache_storage="preallocated")
        stats["draft_rounds"] += 1
        stats["draft_tokens"] += len(proposed)
        verification = verify_draft(target, prefix, proposed)
        stats["accepted_tokens"] += verification["accepted"]
        stats["rollback_tokens"] += verification["rollback"]
        stats["rollback_count"] += int(verification["rollback"] > 0)
        stats["target_verify_steps"] += verification["target_steps"]
        committed = proposed[:verification["accepted"]]
        remaining = max_tokens - len(generated)
        committed = committed[:remaining]
        generated.extend(committed)
        stats["kv_tokens_committed"] += len(committed)
        if len(generated) >= max_tokens:
            break
        correction = verification["correction"]
        generated.append(correction)
        stats["kv_tokens_committed"] += 1
        prefix = prompt + _tokens_to_text(target, generated)
    return generated, stats


def _elapsed_cuda(fn):
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    value = fn()
    end.record()
    torch.cuda.synchronize()
    return value, start.elapsed_time(end)


def run_scenario(target: NeuralGenerator, scenario: dict) -> dict:
    draft = NeuralGenerator("cuda", hidden=HIDDEN, heads=HEADS, seed=scenario["draft_seed"])
    prompt = scenario["prompt"]
    max_tokens = scenario["max_tokens"]
    baseline_tokens, baseline_ms = _elapsed_cuda(
        lambda: target.generate(prompt, max_tokens, cached=True, cache_storage="preallocated")[0]
    )
    (spec_tokens, stats), speculative_ms = _elapsed_cuda(
        lambda: speculative_generate(target, draft, prompt, max_tokens, scenario["draft_width"])
    )
    output_parity = spec_tokens == baseline_tokens
    stats.update({
        "acceptance_rate": stats["accepted_tokens"] / max(stats["draft_tokens"], 1),
        "wasted_draft_ratio": stats["rollback_tokens"] / max(stats["draft_tokens"], 1),
        "baseline_ms": baseline_ms,
        "speculative_ms": speculative_ms,
        "speedup_vs_baseline": baseline_ms / max(speculative_ms, 1e-9),
        "baseline_tpot_ms": baseline_ms / max(len(baseline_tokens), 1),
        "speculative_tpot_ms": speculative_ms / max(len(spec_tokens), 1),
        "output_parity": output_parity,
        "generated_tokens": len(spec_tokens),
        "draft_width": scenario["draft_width"],
    })
    return {"scenario_id": scenario["id"], "prompt": prompt, "draft_seed": scenario["draft_seed"], **stats}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    report = {
        "experiment": "speculative_decoding_cuda",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "unavailable:cuda-runtime", "measured": False,
        "gpu_execution_accepted": False,
    }
    if not torch.cuda.is_available():
        report["reason"] = "CUDA is not available"
    else:
        target = NeuralGenerator("cuda", hidden=HIDDEN, heads=HEADS, seed=151)
        rows = [run_scenario(target, scenario) for scenario in SCENARIOS]
        checks = {
            "scenario_count": len(rows) >= 4,
            "all_output_parity": all(row["output_parity"] for row in rows),
            "acceptance_accounted": all(row["accepted_tokens"] <= row["draft_tokens"] for row in rows),
            "rollback_accounted": all(row["rollback_tokens"] >= 0 and row["rollback_count"] >= 0 for row in rows),
            "cuda_timings_present": all(row["baseline_ms"] > 0 and row["speculative_ms"] > 0 for row in rows),
            "low_acceptance_covered": min(row["acceptance_rate"] for row in rows) < 0.95,
            "kv_commit_accounted": all(row["kv_tokens_committed"] == row["generated_tokens"] for row in rows),
        }
        report.update({
            "status": "passed" if all(checks.values()) else "failed",
            "measured": True, "gpu_execution_accepted": all(checks.values()),
            "device_name": torch.cuda.get_device_name(0), "torch_version": torch.__version__,
            "target_seed": 151, "hidden": HIDDEN, "heads": HEADS,
            "rows": rows, "checks": checks,
            "scope": "greedy draft/target execution on one CUDA device using an untrained character transformer; no production model or multi-GPU claim",
        })
    source_paths = [Path(__file__).resolve(), SERVING / "neural_generator.py"]
    report["source_sha256"] = {
        str(path.relative_to(ROOT.parent)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
