#!/usr/bin/env python3
"""Measure activation-distribution coverage for calibration and held-out contexts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_gpt2_multimodule_replay import PINNED_REVISION


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(model, tokenizer, modules, texts):
    values = {name: [] for name in modules}
    handles = []
    for name, module in modules.items():
        def observe(_module, inputs, module_name=name):
            values[module_name].append(inputs[0].detach().cpu().reshape(-1).abs().numpy())
        handles.append(module.register_forward_pre_hook(observe))
    try:
        with torch.inference_mode():
            for text in texts:
                encoded = tokenizer(text, return_tensors="pt")
                model(**encoded, use_cache=False)
    finally:
        for handle in handles:
            handle.remove()
    result = {}
    for name, parts in values.items():
        flattened = np.concatenate(parts)
        per_text = []
        offset = 0
        for text, part in zip(texts, parts):
            per_text.append({"text_id": text, "count": int(part.size), "max_abs": float(part.max()),
                             "p99_abs": float(np.quantile(part, 0.99)), "mean_abs": float(part.mean())})
            offset += part.size
        result[name] = {"count": int(flattened.size), "min_abs": float(flattened.min()),
                        "max_abs": float(flattened.max()), "p50_abs": float(np.quantile(flattened, 0.50)),
                        "p95_abs": float(np.quantile(flattened, 0.95)), "p99_abs": float(np.quantile(flattened, 0.99)),
                        "mean_abs": float(flattened.mean()), "per_text": per_text}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", type=Path, required=True)
    parser.add_argument("--calibration-fixture", type=Path, required=True)
    parser.add_argument("--original-fixture", type=Path, required=True)
    parser.add_argument("--stress-fixture", type=Path, required=True)
    parser.add_argument("--third-fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()
    fixtures = {label: json.loads(path.read_text(encoding="utf-8")) for label, path in {
        "calibration": args.calibration_fixture, "original": args.original_fixture,
        "stress": args.stress_fixture, "third_holdout": args.third_fixture}.items()}
    if any(fixture["revision"] != PINNED_REVISION for fixture in fixtures.values()):
        raise SystemExit("all fixtures must use the pinned revision")
    calibration_texts = fixtures["calibration"]["calibration"]
    eval_texts = {label: fixture["evaluation"] for label, fixture in fixtures.items() if label != "calibration"}
    all_eval = [text for texts in eval_texts.values() for text in texts]
    if len(all_eval) != len(set(all_eval)) or set(calibration_texts) & set(all_eval):
        raise SystemExit("coverage contexts overlap")
    torch.set_num_threads(args.threads)
    model = AutoModelForCausalLM.from_pretrained(args.snapshot_path, local_files_only=True,
                                                 use_safetensors=True, attn_implementation="eager").eval()
    tokenizer = AutoTokenizer.from_pretrained(args.snapshot_path, local_files_only=True)
    modules = {name: model.get_submodule(name) for name in fixtures["calibration"]["target_modules"]}
    distributions = {"calibration": collect(model, tokenizer, modules, calibration_texts)}
    for label, texts in eval_texts.items():
        distributions[label] = collect(model, tokenizer, modules, texts)
    coverage = {}
    for name in modules:
        calibration_max = distributions["calibration"][name]["max_abs"]
        coverage[name] = {}
        for context in eval_texts:
            stats = distributions[context][name]
            coverage[name][context] = {
                "context_max_over_calibration_max": stats["max_abs"] / max(calibration_max, 1e-12),
                "context_p99_over_calibration_p99": stats["p99_abs"] / max(distributions["calibration"][name]["p99_abs"], 1e-12),
                "max_abs": stats["max_abs"], "p99_abs": stats["p99_abs"],
                "calibration_max_abs": calibration_max,
            }
    report = {"schema_version": "gpt2-multicontext-activation-coverage-v0.1",
              "result_type": "local_activation_distribution_coverage_matrix",
              "sources": {label: {"path": str(path), "sha256": digest(path)} for label, path in {
                  "calibration": args.calibration_fixture, "original": args.original_fixture,
                  "stress": args.stress_fixture, "third_holdout": args.third_fixture}.items()},
              "model_revision": PINNED_REVISION, "target_modules": list(modules),
              "contexts": {label: {"text_count": len(texts), "distributions": distributions[label]}
                           for label, texts in {"calibration": calibration_texts, **eval_texts}.items()},
              "coverage_ratios": coverage,
              "claim_boundary": "Local CPU activation coverage measurement only; no hardware latency, energy, silicon yield, or analog authorization."}
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "activation_coverage_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        *[{"path": str(path), "sha256": digest(path)} for path in (args.calibration_fixture, args.original_fixture, args.stress_fixture, args.third_fixture)],
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "modules": len(modules), "contexts": len(eval_texts) + 1}, sort_keys=True))


if __name__ == "__main__":
    main()
