#!/usr/bin/env python3
"""Promote accepted Colab artifacts into the canonical GPU-run import shape.

The individual Colab handoffs are intentionally retained verbatim.  This
adapter only indexes reports whose own status and ``gpu_execution_accepted``
fields pass, and keeps partial/scope-limited rows explicit instead of treating
every CUDA smoke as a full curriculum promotion.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMPORTS = ROOT / "gpu-runs" / "imports"
OUT = IMPORTS / "colab-t4-promoted.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest(pattern: str, filename: str) -> tuple[Path, dict[str, Any]]:
    candidates = sorted(IMPORTS.glob(pattern), reverse=True)
    for directory in candidates:
        path = directory / filename
        if not path.exists():
            continue
        report = load(path)
        gpu_report_passed = report.get("gpu_execution_accepted") is True
        suite_report_passed = report.get("failed") == 0 and report.get("passed", 0) == report.get("benchmark_count", -1) and report.get("accelerator_readiness", {}).get("torch_device") == "cuda"
        if (gpu_report_passed and report.get("status") in {None, "passed", "ran", "task_gate_passed"}) or suite_report_passed:
            return path, report
    raise FileNotFoundError(f"no accepted artifact for {pattern}/{filename}")


def metrics(report: dict[str, Any], *keys: str) -> dict[str, Any]:
    result = {"status": report.get("status"), "gpu_execution_accepted": report.get("gpu_execution_accepted")}
    for key in keys:
        if key in report:
            result[key] = report[key]
    # Native WMMA profiler handoffs keep the complete SASS/Nsight payload
    # nested for fidelity.  Flatten only the queue's acceptance facts so the
    # measurement ledger can distinguish a real partial capture from missing
    # evidence without rewriting the source artifact.
    if "nsight_compute" in report or "sass" in report:
        tool_availability = report.get("tool_availability", {})
        nsight = report.get("nsight_compute", {})
        sass = report.get("sass", {})
        result["ncu"] = tool_availability.get("ncu") is True
        result["nsys"] = False
        result["rocprof"] = False
        # Nsight can emit more metric values than the human-readable kernel
        # row preview retains. Count the measured values, not the preview cap.
        result["profiler_rows"] = len(nsight.get("wmma_metric_values", []))
        result["tensor_core_instruction_seen"] = sass.get("tensor_core_instruction_seen") is True
    return result


def main() -> int:
    # Each mapping is deliberately claim-scoped.  In particular, the NCCL
    # smoke is partial because it is world-size one and cannot prove scaling.
    selected = [
        ("cuda-kernel-compile", "colab-t4-gemm-*", "gemm.json", "passed", ("session", "timestamp", "shared_memory_gemm")),
        ("eager-kernel-suite-cuda", "colab-t4-eager-kernels-*", "kernel-benchmark-report.json", "passed", ("benchmark_count", "passed", "failed", "accelerator_readiness", "benchmarks")),
        ("low-precision-native", "colab-t4-low-precision-*", "low-precision-cuda.json", "passed", ("project", "device_name", "torch_version", "rows", "scope")),
        ("trained-digits-quality-cuda", "colab-t4-digits-quality-*", "digits-quality-cuda.json", "passed", ("project", "device_name", "torch_version", "protocol", "seed_pairs", "cases", "scope")),
        ("rl-simulation-cuda", "colab-t4-rl-simulation-*", "vectorized-simulation-cuda.json", "passed", ("experiment", "device", "device_name", "env_count", "steps", "position_match", "reward_match", "policy_position_match", "policy_reward_match", "policy_termination_match", "policy_reset_match", "policy_episode_resets", "median_seconds", "steps_per_second", "scope")),
        ("rl-policy-quality-cuda", "colab-t4-rl-policy-*", "policy-quality-cuda.json", "passed", ("experiment", "device", "device_name", "train_samples", "train_steps", "eval_envs", "eval_steps", "action_accuracy", "success_rate", "oracle_success_rate", "policy_episode_resets", "training_seconds", "scope")),
        ("triton-layout-cuda", "colab-t4-layout-algebra-*", "triton-layout-cuda.json", "passed", ("experiment", "device", "device_name", "triton_version", "shape", "tile", "rows", "timing_scope", "scope")),
        ("bank-conflict-cuda", "colab-t4-bank-conflict-*", "bank-conflict-cuda.json", "passed", ("experiment", "native", "scope")),
        ("cuda-graphs-native", "colab-t4-cuda-graphs-*", "cuda-graphs-cuda.json", "passed", ("project", "device_name", "torch_version", "shape", "max_abs_error", "eager_median_ms", "graph_median_ms", "speedup_eager_over_graph", "scope")),
        ("model-integration-gpu", "colab-t4-attention-*", "compiled-training-cuda.json", "passed", ("project", "cases", "max_output_error", "max_parameter_gradient_error")),
        ("neural-serving-cuda", "colab-t4-neural-serving-*", "neural-serving-cuda.json", "passed", ("project", "device_name", "torch_version", "prompt_count", "max_tokens", "decode_median_ms", "model_trained", "scope")),
        ("trained-neural-quality-cuda", "colab-t4-trained-neural-quality-*", "trained-neural-quality-cuda.json", "passed", ("project", "device", "device_name", "train_steps", "batch", "context", "model_trained", "final_train_loss", "eval_loss", "heldout_next_token_accuracy", "cached_full_parity", "training_seconds", "scope")),
        ("paged-kv-gather-cuda", "colab-t4-paged-kv-*", "paged-kv-cuda.json", "passed", ("experiment", "native", "scope")),
        ("paged-attention-cuda", "colab-t4-paged-attention-*", "paged-attention-cuda.json", "passed", ("experiment", "native", "scope")),
        ("serving-tail-load-cuda", "colab-t4-serving-tail-*", "serving-tail-load-cuda.json", "passed", ("experiment", "device_name", "torch_version", "concurrency_levels", "requests_per_level", "rows", "scope")),
        ("triton-kernel-sweep", "colab-t4-triton-*", "triton-cuda.json", "partial:matmul-only", ("project", "device_name", "triton_version", "rows", "scope")),
        ("triton-kernel-families", "colab-t4-triton-families-*", "triton-families-cuda.json", "passed", ("project", "device_name", "triton_version", "rows", "scope")),
        ("tensor-core-gemm", "colab-t4-wmma-*", "native-execution.json", "passed", ("project", "shape", "wmma_max_abs_error", "cublas_max_abs_error", "wmma_median_ms", "cublas_median_ms")),
        ("profiler-capture", "colab-t4-wmma-*", "profiler-evidence.json", "passed", ("project", "sass", "nsight_compute")),
        ("parallel-primitives", "colab-t4-native-families-*", "native-family-execution.json", "passed", ("project", "native")),
        ("distributed-collectives", "colab-t4-nccl-*", "nccl-gpu.json", "partial:world-size-one", ("project", "world_size", "backend", "scope", "median_all_reduce_ms")),
    ]
    steps: list[dict[str, Any]] = []
    artifact_paths: list[str] = []
    missing_artifacts: list[dict[str, str]] = []
    for step_id, pattern, filename, status, keys in selected:
        try:
            path, report = latest(pattern, filename)
        except FileNotFoundError:
            # A promotion index must never manufacture evidence for a hardware
            # run that was not captured. Keep the claim visible as a missing
            # handoff so the next Colab run has an explicit target.
            missing_artifacts.append({
                "id": step_id,
                "expected_pattern": f"{pattern}/{filename}",
                "status": "unavailable:no-accepted-artifact",
            })
            continue
        relative = path.relative_to(ROOT).as_posix()
        artifact_paths.append(relative)
        step_metrics = metrics(report, *keys)
        steps.append({
            "id": step_id,
            "status": status,
            "evidence": [relative],
            "metrics": step_metrics,
            "scope": report.get("scope", "claim-scoped imported Colab artifact"),
        })

    payload = {
        "run_id": "colab-t4-promoted-20260907",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "collector": "scripts/build_colab_gpu_import.py",
        "provenance": {
            "kind": "real-measured",
            "measured": True,
            "description": "Claim-scoped index of independently captured Colab T4 handoffs; source artifacts remain authoritative.",
            "artifact_paths": artifact_paths,
        },
        "host": {
            "name": "Google Colab runtime (imported)",
            "platform": "Google Colab Linux runtime",
            "accelerator": "Tesla T4",
            "vendor": "NVIDIA",
            "cuda_available": True,
            "rocm_available": False,
            "tools": {"nvcc": True, "nvidia_smi": True, "ncu": True, "hipcc": False},
        },
        "promotion_steps": steps,
        "missing_artifacts": missing_artifacts,
        "limitations": [
            "This index does not merge or rewrite source artifacts.",
            "The NCCL row is world-size one and remains partial; it is not multi-GPU evidence.",
            "Unlisted curriculum steps remain unaccepted.",
            "Missing artifacts are handoff gaps, not successful measurements.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(steps)} claim-scoped steps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
