#!/usr/bin/env python3
"""Colab entry point for the guarded GPT-2/SAR workload handoff.

Run this after cloning the repository into ``/content/ai-hardware-analysis``.
The default mode validates the immutable contracts and derives the operation
trace. ``--execute-model`` additionally invokes the existing GPT-2 evaluator
when its pinned model snapshot and physical evidence are available locally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(command, cwd=cwd, check=False, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode:
        print(completed.stdout[-16000:], file=sys.stderr, flush=True)
        raise subprocess.CalledProcessError(completed.returncode, command, output=completed.stdout)
    return completed.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("/content/ai-hardware-analysis"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute-model", action="store_true")
    parser.add_argument("--device", default="cpu", help="torch device for model execution (cpu or cuda)")
    parser.add_argument("--fetch-model", action="store_true",
                        help="download the fixture's exact pinned model revision before execution")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    software = repo / "analog-in-memory-ai-inference/software-architecture"
    qualification = software / "experiments/gpt2-hybrid-v1/qualification"
    evaluation = software / "experiments/gpt2-hybrid-v1/runs/20260909-recovery-projection/evaluation.json"
    contract = qualification / "profile-driven-transformer-contract.json"
    sar_profile = qualification / "circuit-derived-sar-profile.json"
    remap = qualification / "sar-code-remap-contract.json"
    remap_holdout = qualification / "sar-code-remap-holdout-mismatch-per-converter.json"
    dispatch_policy = qualification / "converter-dispatch-policy.json"
    for path in (evaluation, contract, sar_profile, remap):
        if not path.exists():
            raise SystemExit(f"required repository artifact is missing: {path}")
    model_fetch_output = None
    if args.fetch_model:
        fixture = json.loads((software / "experiments/gpt2-hybrid-v1/fixture.json").read_text())
        runtime_files = ["config.json", "generation_config.json", "merges.txt", "model.safetensors",
                         "special_tokens_map.json", "tokenizer.json", "tokenizer_config.json", "vocab.json"]
        try:
            from huggingface_hub import snapshot_download
            snapshot = snapshot_download(fixture["model_id"], revision=fixture["revision"],
                                         allow_patterns=runtime_files)
            model_fetch_output = {"model_id": fixture["model_id"], "revision": fixture["revision"],
                                  "snapshot": snapshot, "allow_patterns": runtime_files,
                                  "status": "downloaded_or_cached"}
        except Exception as exc:  # preserve a receipt with actionable failure detail
            model_fetch_output = {"status": "failed", "error": repr(exc)}
            if args.execute_model:
                raise
    per_converter = None
    if remap_holdout.exists():
        per_converter = json.loads(remap_holdout.read_text())
    dispatch = json.loads(dispatch_policy.read_text()) if dispatch_policy.exists() else None
    checks = run([sys.executable, str(software / "scripts/check_profile_driven_transformer_contract.py"), str(contract)], repo)
    trace_path = args.output / "profile-driven-workload-trace.json"
    derived = run([sys.executable, str(software / "scripts/derive_profile_driven_workload_trace.py"),
                   "--evaluation", str(evaluation), "--contract", str(contract),
                   "--sar-profile", str(sar_profile), "--output", str(trace_path)], repo)
    dispatch_sim_path = args.output / "converter-dispatch-simulation.json"
    dispatch_sim = run([sys.executable, str(software / "scripts/simulate_converter_dispatch.py"),
                        "--trace", str(trace_path), "--dispatch-policy", str(dispatch_policy),
                        "--output", str(dispatch_sim_path)], repo) if dispatch else None
    dispatch_check = run([sys.executable, str(software / "scripts/check_converter_dispatch_simulation.py"),
                          str(dispatch_sim_path)], repo) if dispatch else None
    model_output = None
    holdout_check = None
    if args.execute_model:
        model_output_dir = args.output / "model-evaluation"
        model_command = [sys.executable, str(software / "scripts/run_gpt2_hybrid_evaluation.py"),
                         "--output", str(model_output_dir), "--device", args.device]
        if model_fetch_output and model_fetch_output.get("snapshot"):
            model_command.extend(["--snapshot-path", str(model_fetch_output["snapshot"])])
        model_output = run(model_command, software)
        holdout_command = [sys.executable, str(software / "scripts/check_gpt2_workload_holdout.py"),
                           str(model_output_dir / "evaluation.json")]
        if args.device == "cuda":
            holdout_command.append("--require-cuda")
        holdout_command.extend(["--output", str(args.output / "workload-holdout-check.json")])
        holdout_check = run(holdout_command, repo)
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": "colab-profile-driven-gpt2-receipt-v0.1",
        "environment": {"python": sys.version, "repo_root": str(repo),
                         "execute_model": args.execute_model, "fetch_model": args.fetch_model,
                         "device": args.device},
        "model_fetch": model_fetch_output,
        "inputs": {"evaluation": str(evaluation), "contract": str(contract),
                   "sar_profile": str(sar_profile), "remap_contract": str(remap),
                   "per_converter_remap_holdout": str(remap_holdout) if per_converter else None,
                   "dispatch_policy": str(dispatch_policy) if dispatch else None},
        "dispatch_policy": {"status": "available" if dispatch else "missing",
                             "decision": dispatch.get("decision") if dispatch else None,
                             "routes": dispatch.get("routes", []) if dispatch else []},
        "per_converter_remap": {
            "status": "available" if per_converter else "missing",
            "passed_holdouts": per_converter.get("passed_holdouts") if per_converter else 0,
            "total_holdouts": per_converter.get("total_holdouts") if per_converter else 0,
            "promotion_allowed": per_converter.get("promotion_allowed", False) if per_converter else False,
            "scope": "bounded mismatch campaign only",
        },
        "contract_check_output": checks,
        "trace_command_output": derived,
        "dispatch_simulation_output": dispatch_sim,
        "dispatch_simulation_check_output": dispatch_check,
        "model_command_output": model_output,
        "workload_holdout_check_output": holdout_check,
        "decision": "native_digital_fallback_until_held_out_validation_passes",
        "claim_boundary": "Colab orchestration and derived operation counts only; model execution remains subject to its own evidence checks, and no analog hardware latency, energy, yield, or speedup is claimed.",
    }
    (args.output / "colab-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": str(args.output / "colab-receipt.json"),
                      "trace": str(trace_path), "model_executed": args.execute_model}))


if __name__ == "__main__":
    main()
