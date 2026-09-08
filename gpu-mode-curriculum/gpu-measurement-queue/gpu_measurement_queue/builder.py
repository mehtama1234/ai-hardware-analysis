from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gpu-measurement-queue"
REPORT_JSON = OUT / "gpu-measurement-queue.json"
REPORT_MD = OUT / "reports" / "gpu-measurement-queue.md"


MEASUREMENT_SPECS: dict[str, dict[str, Any]] = {
    "cuda-kernel-compile": {
        "host_class": "nvidia-cuda",
        "required_metrics": ["nvcc", "nvidia_smi", "torch_device", "passed_benchmarks"],
        "acceptance_thresholds": ["nvcc == true", "nvidia_smi == true", "torch_device == cuda", "passed_benchmarks >= 14"],
    },
    "triton-kernel-sweep": {
        "host_class": "nvidia-cuda",
        "required_metrics": ["cuda_available", "triton_cases", "passed_benchmarks"],
        "acceptance_thresholds": ["cuda_available == true", "triton_cases >= 4", "passed_benchmarks >= 14"],
    },
    "tensor-core-gemm": {
        "host_class": "nvidia-cuda-profiler",
        "required_metrics": ["nvcc", "nvidia_smi", "ncu", "tensor_core_scenarios", "mma_instruction_seen"],
        "acceptance_thresholds": ["nvcc == true", "nvidia_smi == true", "ncu == true", "tensor_core_scenarios >= 5", "mma_instruction_seen == true"],
    },
    "persistent-kernels": {
        "host_class": "nvidia-cuda-profiler",
        "required_metrics": ["triton", "nvidia_smi", "ncu", "persistent_scenarios", "speedup_vs_baseline", "occupancy_proxy", "hbm_reduction"],
        "acceptance_thresholds": ["triton == true", "nvidia_smi == true", "ncu == true", "persistent_scenarios >= 6", "speedup_vs_baseline >= 1.15", "occupancy_proxy >= 0.30", "hbm_reduction >= 0.15"],
    },
    "parallel-primitives": {
        "host_class": "nvidia-or-amd-profiler",
        "required_metrics": ["accelerator_ready", "primitive_scenarios", "work_efficiency", "bandwidth_proxy_gbps", "occupancy_proxy", "stable_order_scenarios"],
        "acceptance_thresholds": ["accelerator_ready == true", "primitive_scenarios >= 6", "work_efficiency >= 1.20", "bandwidth_proxy_gbps > 0", "occupancy_proxy >= 0.35", "stable_order_scenarios >= 3"],
    },
    "torch-custom-extension": {
        "host_class": "nvidia-cuda",
        "required_metrics": ["compiled_extension_status", "passed_cases"],
        "acceptance_thresholds": ["compiled_extension_status == cuda-ready", "passed_cases >= 4"],
    },
    "model-integration-gpu": {
        "host_class": "accelerator-torch",
        "required_metrics": ["accelerator_ready", "passed_cases", "uses_custom_op"],
        "acceptance_thresholds": ["accelerator_ready == true", "passed_cases >= 3", "uses_custom_op == fused_bias_gelu_residual"],
    },
    "vllm-serving-trace": {
        "host_class": "nvidia-cuda-serving",
        "required_metrics": ["cuda_available", "passed_traces", "prefix_cache_blocks_saved"],
        "acceptance_thresholds": ["cuda_available == true", "passed_traces >= 3", "prefix_cache_blocks_saved > 0"],
    },
    "attention-serving-stack": {
        "host_class": "nvidia-cuda-serving-profiler",
        "required_metrics": ["cuda_available", "attention_scenarios", "hbm_reduction", "prefix_blocks_reused", "profiler_rows"],
        "acceptance_thresholds": ["cuda_available == true", "attention_scenarios >= 5", "hbm_reduction > 0", "prefix_blocks_reused > 0", "profiler_rows >= 1"],
    },
    "flash-attention-backward": {
        "host_class": "nvidia-cuda-training-profiler",
        "required_metrics": ["cuda_available", "flash_backward_scenarios", "gradient_paths", "max_abs_error", "hbm_reduction", "recompute_overhead_ratio", "occupancy_proxy"],
        "acceptance_thresholds": ["cuda_available == true", "flash_backward_scenarios >= 6", "gradient_paths >= 4", "max_abs_error <= 0.02", "hbm_reduction >= 0.40", "recompute_overhead_ratio >= 0", "occupancy_proxy >= 0.45"],
    },
    "sparse-attention-kernels": {
        "host_class": "nvidia-cuda-sparse-profiler",
        "required_metrics": ["cuda_available", "sparse_attention_scenarios", "pattern_count", "ragged_scenarios", "backward_scenarios", "max_abs_error", "hbm_reduction", "load_balance_proxy"],
        "acceptance_thresholds": ["cuda_available == true", "sparse_attention_scenarios >= 6", "pattern_count >= 6", "ragged_scenarios >= 1", "backward_scenarios >= 4", "max_abs_error <= 0.02", "hbm_reduction >= 0.55", "load_balance_proxy >= 0.75"],
    },
    "fused-training-kernels": {
        "host_class": "nvidia-cuda-training-profiler",
        "required_metrics": ["cuda_available", "fused_training_scenarios", "family_count", "backward_scenarios", "optimizer_state_scenarios", "max_abs_error", "hbm_reduction", "launch_reduction"],
        "acceptance_thresholds": ["cuda_available == true", "fused_training_scenarios >= 6", "family_count >= 5", "backward_scenarios >= 4", "optimizer_state_scenarios >= 2", "max_abs_error <= 0.02", "hbm_reduction >= 0.45", "launch_reduction >= 0.45"],
    },
    "speculative-decoding-serving": {
        "host_class": "nvidia-cuda-serving-profiler",
        "required_metrics": ["cuda_available", "speculative_scenarios", "passed_scenarios", "engine_count", "scheduler_policy_count", "min_acceptance_rate", "max_speedup_vs_baseline", "max_wasted_draft_ratio"],
        "acceptance_thresholds": ["cuda_available == true", "speculative_scenarios >= 6", "passed_scenarios >= 4", "engine_count >= 4", "scheduler_policy_count >= 2", "min_acceptance_rate < 0.50", "max_speedup_vs_baseline >= 2.0", "max_wasted_draft_ratio > 0.35"],
    },
    "profiler-capture": {
        "host_class": "nvidia-or-amd-profiler",
        "required_metrics": ["ncu", "nsys", "rocprof", "profiler_rows"],
        "acceptance_thresholds": ["ncu/nsys or rocprof available", "profiler_rows >= 9"],
    },
    "rocm-hip-port": {
        "host_class": "amd-rocm",
        "required_metrics": ["hipcc", "rocprof", "starter_status"],
        "acceptance_thresholds": ["hipcc == true", "rocprof == true", "starter_status == ran"],
    },
    "distributed-collectives": {
        "host_class": "multi-gpu",
        "required_metrics": ["torchrun", "accelerator_ready", "collective_scenarios", "bandwidth_efficiency", "overlap_gain", "nccl_or_rccl"],
        "acceptance_thresholds": ["torchrun == true", "accelerator_ready == true", "collective_scenarios >= 6", "bandwidth_efficiency >= 0.45", "overlap_gain > 0", "nccl_or_rccl == true"],
    },
    "distributed-training-optimizer": {
        "host_class": "multi-gpu-training",
        "required_metrics": ["torchrun", "accelerator_ready", "training_optimizer_scenarios", "passed_scenarios", "max_memory_gb_per_gpu", "step_time_ms", "optimizer_state_savings"],
        "acceptance_thresholds": ["torchrun == true", "accelerator_ready == true", "training_optimizer_scenarios >= 6", "passed_scenarios >= 4", "max_memory_gb_per_gpu <= 80", "step_time_ms > 0", "optimizer_state_savings > 0"],
    },
    "full-gpu-regression": {
        "host_class": "final-gpu-regression",
        "required_metrics": ["accelerator_ready", "metric_count", "failed_metrics"],
        "acceptance_thresholds": ["accelerator_ready == true", "metric_count >= 79", "failed_metrics == 0"],
    },
}

# These claim-scoped runs use their report's explicit status as the metric
# contract.  They are still real GPU artifacts when imported by
# ``build_colab_gpu_import.py``; keeping the contract here prevents them from
# becoming invisible holes in the measurement queue.
for _step_id in (
    "triton-kernel-families",
    "low-precision-native",
    "trained-digits-quality-cuda",
    "rl-simulation-cuda",
    "rl-policy-quality-cuda",
    "triton-layout-cuda",
    "bank-conflict-cuda",
    "cuda-graphs-native",
    "neural-serving-cuda",
    "trained-neural-quality-cuda",
    "trained-serving-e2e-cuda",
    "trained-serving-tail-cuda",
    "paged-kv-gather-cuda",
    "paged-attention-cuda",
):
    MEASUREMENT_SPECS[_step_id] = {
        "host_class": "accelerator-claim-scoped",
        "required_metrics": ["status"],
        "acceptance_thresholds": ["status in {passed, task_gate_passed}"],
    }
MEASUREMENT_SPECS["eager-kernel-suite-cuda"] = {
    "host_class": "nvidia-cuda",
    "required_metrics": ["benchmark_count", "passed", "failed", "accelerator_readiness"],
    "acceptance_thresholds": [
        "failed == 0",
        "passed == benchmark_count",
        "benchmark_count >= 14",
        "accelerator_readiness.torch_device == cuda",
        "accelerator_readiness.nvidia_smi == true",
    ],
}
MEASUREMENT_SPECS["serving-tail-load-cuda"] = {
    "host_class": "nvidia-cuda-serving",
    "required_metrics": ["status", "gpu_execution_accepted", "concurrency_levels", "requests_per_level", "rows"],
    "acceptance_thresholds": [
        "status == passed",
        "gpu_execution_accepted == true",
        "concurrency_levels == [1, 2, 4, 8]",
        "requests_per_level >= 12",
        "all rows have p95 and parity",
        "vectorized batching observed above concurrency 1",
    ],
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _real_measured_rows(gpu_runs: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in gpu_runs.get("rows", [])
        if row.get("measured") is True and row.get("provenance_kind") == "real-measured"
    ]


def _truthy(value: Any) -> bool:
    return value is True or value == "true" or value == "cuda-ready" or value == "ran" or value == "cuda"


def _metric_checks(step_id: str, metrics: dict[str, Any]) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    if step_id == "cuda-kernel-compile":
        checks = {
            "nvcc == true": _truthy(metrics.get("nvcc")),
            "nvidia_smi == true": _truthy(metrics.get("nvidia_smi")),
            "torch_device == cuda": metrics.get("torch_device") == "cuda",
            "passed_benchmarks >= 14": metrics.get("passed_benchmarks", 0) >= 14,
        }
    elif step_id == "triton-kernel-sweep":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "triton_cases >= 4": metrics.get("triton_cases", 0) >= 4,
            "passed_benchmarks >= 14": metrics.get("passed_benchmarks", 0) >= 14,
        }
    elif step_id == "tensor-core-gemm":
        checks = {
            "nvcc == true": _truthy(metrics.get("nvcc")),
            "nvidia_smi == true": _truthy(metrics.get("nvidia_smi")),
            "ncu == true": _truthy(metrics.get("ncu")),
            "tensor_core_scenarios >= 5": metrics.get("tensor_core_scenarios", 0) >= 5,
            "mma_instruction_seen == true": _truthy(metrics.get("mma_instruction_seen")),
        }
    elif step_id == "persistent-kernels":
        checks = {
            "triton == true": _truthy(metrics.get("triton")),
            "nvidia_smi == true": _truthy(metrics.get("nvidia_smi")),
            "ncu == true": _truthy(metrics.get("ncu")),
            "persistent_scenarios >= 6": metrics.get("persistent_scenarios", 0) >= 6,
            "speedup_vs_baseline >= 1.15": metrics.get("speedup_vs_baseline", 0) >= 1.15,
            "occupancy_proxy >= 0.30": metrics.get("occupancy_proxy", 0) >= 0.30,
            "hbm_reduction >= 0.15": metrics.get("hbm_reduction", 0) >= 0.15,
        }
    elif step_id == "parallel-primitives":
        checks = {
            "accelerator_ready == true": _truthy(metrics.get("accelerator_ready")),
            "primitive_scenarios >= 6": metrics.get("primitive_scenarios", 0) >= 6,
            "work_efficiency >= 1.20": metrics.get("work_efficiency", 0) >= 1.20,
            "bandwidth_proxy_gbps > 0": metrics.get("bandwidth_proxy_gbps", 0) > 0,
            "occupancy_proxy >= 0.35": metrics.get("occupancy_proxy", 0) >= 0.35,
            "stable_order_scenarios >= 3": metrics.get("stable_order_scenarios", 0) >= 3,
        }
    elif step_id == "torch-custom-extension":
        checks = {
            "compiled_extension_status == cuda-ready": metrics.get("compiled_extension_status") == "cuda-ready",
            "passed_cases >= 4": metrics.get("passed_cases", 0) >= 4,
        }
    elif step_id == "model-integration-gpu":
        checks = {
            "accelerator_ready == true": _truthy(metrics.get("accelerator_ready")),
            "passed_cases >= 3": metrics.get("passed_cases", 0) >= 3,
            "uses_custom_op == fused_bias_gelu_residual": metrics.get("uses_custom_op") == "fused_bias_gelu_residual",
        }
    elif step_id == "vllm-serving-trace":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "passed_traces >= 3": metrics.get("passed_traces", 0) >= 3,
            "prefix_cache_blocks_saved > 0": metrics.get("prefix_cache_blocks_saved", 0) > 0,
        }
    elif step_id == "attention-serving-stack":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "attention_scenarios >= 5": metrics.get("attention_scenarios", 0) >= 5,
            "hbm_reduction > 0": metrics.get("hbm_reduction", 0) > 0,
            "prefix_blocks_reused > 0": metrics.get("prefix_blocks_reused", 0) > 0,
            "profiler_rows >= 1": metrics.get("profiler_rows", 0) >= 1,
        }
    elif step_id == "flash-attention-backward":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "flash_backward_scenarios >= 6": metrics.get("flash_backward_scenarios", 0) >= 6,
            "gradient_paths >= 4": metrics.get("gradient_paths", 0) >= 4,
            "max_abs_error <= 0.02": metrics.get("max_abs_error", 1.0) <= 0.02,
            "hbm_reduction >= 0.40": metrics.get("hbm_reduction", 0) >= 0.40,
            "recompute_overhead_ratio >= 0": metrics.get("recompute_overhead_ratio", -1) >= 0,
            "occupancy_proxy >= 0.45": metrics.get("occupancy_proxy", 0) >= 0.45,
        }
    elif step_id == "sparse-attention-kernels":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "sparse_attention_scenarios >= 6": metrics.get("sparse_attention_scenarios", 0) >= 6,
            "pattern_count >= 6": metrics.get("pattern_count", 0) >= 6,
            "ragged_scenarios >= 1": metrics.get("ragged_scenarios", 0) >= 1,
            "backward_scenarios >= 4": metrics.get("backward_scenarios", 0) >= 4,
            "max_abs_error <= 0.02": metrics.get("max_abs_error", 1.0) <= 0.02,
            "hbm_reduction >= 0.55": metrics.get("hbm_reduction", 0) >= 0.55,
            "load_balance_proxy >= 0.75": metrics.get("load_balance_proxy", 0) >= 0.75,
        }
    elif step_id == "fused-training-kernels":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "fused_training_scenarios >= 6": metrics.get("fused_training_scenarios", 0) >= 6,
            "family_count >= 5": metrics.get("family_count", 0) >= 5,
            "backward_scenarios >= 4": metrics.get("backward_scenarios", 0) >= 4,
            "optimizer_state_scenarios >= 2": metrics.get("optimizer_state_scenarios", 0) >= 2,
            "max_abs_error <= 0.02": metrics.get("max_abs_error", 1.0) <= 0.02,
            "hbm_reduction >= 0.45": metrics.get("hbm_reduction", 0) >= 0.45,
            "launch_reduction >= 0.45": metrics.get("launch_reduction", 0) >= 0.45,
        }
    elif step_id == "speculative-decoding-serving":
        checks = {
            "cuda_available == true": _truthy(metrics.get("cuda_available")),
            "speculative_scenarios >= 6": metrics.get("speculative_scenarios", 0) >= 6,
            "passed_scenarios >= 4": metrics.get("passed_scenarios", 0) >= 4,
            "engine_count >= 4": metrics.get("engine_count", 0) >= 4,
            "scheduler_policy_count >= 2": metrics.get("scheduler_policy_count", 0) >= 2,
            "min_acceptance_rate < 0.50": metrics.get("min_acceptance_rate", 1.0) < 0.50,
            "max_speedup_vs_baseline >= 2.0": metrics.get("max_speedup_vs_baseline", 0.0) >= 2.0,
            "max_wasted_draft_ratio > 0.35": metrics.get("max_wasted_draft_ratio", 0.0) > 0.35,
        }
    elif step_id == "profiler-capture":
        checks = {
            "ncu/nsys or rocprof available": _truthy(metrics.get("ncu")) or _truthy(metrics.get("nsys")) or _truthy(metrics.get("rocprof")),
            "profiler_rows >= 9": metrics.get("profiler_rows", 0) >= 9,
        }
    elif step_id == "rocm-hip-port":
        checks = {
            "hipcc == true": _truthy(metrics.get("hipcc")),
            "rocprof == true": _truthy(metrics.get("rocprof")),
            "starter_status == ran": metrics.get("starter_status") == "ran",
        }
    elif step_id == "distributed-collectives":
        checks = {
            "torchrun == true": _truthy(metrics.get("torchrun")),
            "accelerator_ready == true": _truthy(metrics.get("accelerator_ready")),
            "collective_scenarios >= 6": metrics.get("collective_scenarios", 0) >= 6,
            "bandwidth_efficiency >= 0.45": metrics.get("bandwidth_efficiency", 0) >= 0.45,
            "overlap_gain > 0": metrics.get("overlap_gain", 0) > 0,
            "nccl_or_rccl == true": _truthy(metrics.get("nccl_or_rccl")),
        }
    elif step_id == "distributed-training-optimizer":
        checks = {
            "torchrun == true": _truthy(metrics.get("torchrun")),
            "accelerator_ready == true": _truthy(metrics.get("accelerator_ready")),
            "training_optimizer_scenarios >= 6": metrics.get("training_optimizer_scenarios", 0) >= 6,
            "passed_scenarios >= 4": metrics.get("passed_scenarios", 0) >= 4,
            "max_memory_gb_per_gpu <= 80": 0 < metrics.get("max_memory_gb_per_gpu", 999) <= 80,
            "step_time_ms > 0": metrics.get("step_time_ms", 0) > 0,
            "optimizer_state_savings > 0": metrics.get("optimizer_state_savings", 0) > 0,
        }
    elif step_id == "full-gpu-regression":
        checks = {
            "accelerator_ready == true": _truthy(metrics.get("accelerator_ready")),
            "metric_count >= 79": metrics.get("metric_count", 0) >= 79,
            "failed_metrics == 0": metrics.get("failed_metrics", 1) == 0,
        }
    elif step_id == "serving-tail-load-cuda":
        rows = metrics.get("rows", [])
        levels = metrics.get("concurrency_levels", [])
        checks = {
            "status == passed": metrics.get("status") == "passed",
            "gpu_execution_accepted == true": metrics.get("gpu_execution_accepted") is True,
            "concurrency_levels == [1, 2, 4, 8]": levels == [1, 2, 4, 8],
            "requests_per_level >= 12": metrics.get("requests_per_level", 0) >= 12,
            "all rows have p95 and parity": len(rows) == len(levels) and all(
                isinstance(row.get("latency_ms", {}).get("p95_nearest_rank"), (int, float))
                and row.get("output_parity") is True
                for row in rows
            ),
            "vectorized batching observed above concurrency 1": any(
                row.get("concurrency", 1) > 1 and "vectorized" in row.get("batch_modes", [])
                for row in rows
            ),
        }
    elif step_id == "eager-kernel-suite-cuda":
        readiness = metrics.get("accelerator_readiness", {})
        checks = {
            "failed == 0": metrics.get("failed", 1) == 0,
            "passed == benchmark_count": metrics.get("passed", 0) == metrics.get("benchmark_count", -1),
            "benchmark_count >= 14": metrics.get("benchmark_count", 0) >= 14,
            "accelerator_readiness.torch_device == cuda": readiness.get("torch_device") == "cuda",
            "accelerator_readiness.nvidia_smi == true": readiness.get("nvidia_smi") is True,
        }
    elif step_id in MEASUREMENT_SPECS:
        checks = {"status in {passed, task_gate_passed}": metrics.get("status") in {"passed", "task_gate_passed"}}
    return checks


def evaluate_step_metrics(step_id: str, metrics: dict[str, Any], row_status: str = "passed") -> dict[str, Any]:
    checks = _metric_checks(step_id, metrics)
    checks_passed = bool(checks) and all(checks.values())
    return {
        "row_status": row_status,
        "checks": checks,
        "checks_passed": checks_passed,
        "accepted": row_status == "passed" and checks_passed,
    }


def _evaluate_rows(step_id: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evaluations = []
    for row in rows:
        evaluation = evaluate_step_metrics(step_id, row.get("metrics", {}), row_status=row.get("status", "missing"))
        evaluations.append(
            {
                "run_id": row.get("run_id", "unknown"),
                **evaluation,
            }
        )
    return evaluations


def _task(step: dict[str, Any], real_rows: list[dict[str, Any]]) -> dict[str, Any]:
    step_id = step.get("id", "")
    spec = MEASUREMENT_SPECS.get(step_id, {})
    matching_rows = [row for row in real_rows if row.get("step_id") == step_id]
    evaluations = _evaluate_rows(step_id, matching_rows)
    accepted_rows = [row for row in evaluations if row["accepted"]]
    failed_rows = [row for row in evaluations if not row["accepted"]]
    command_count = len(step.get("commands", []))
    required_metrics = spec.get("required_metrics", [])
    measurement_status = "queued-for-gpu-host"
    if accepted_rows:
        measurement_status = "measured-accepted"
    elif failed_rows:
        measurement_status = "measured-failed"
    return {
        "step_id": step_id,
        "title": step.get("title", ""),
        "host_class": spec.get("host_class", "unspecified"),
        "required_capabilities": step.get("required_capabilities", []),
        "missing_capabilities": step.get("missing_capabilities", []),
        "command_count": command_count,
        "commands": step.get("commands", []),
        "expected_evidence": step.get("expected_evidence", []),
        "required_metrics": required_metrics,
        "acceptance_thresholds": spec.get("acceptance_thresholds", []),
        "real_measured_rows": len(matching_rows),
        "accepted_measured_rows": len(accepted_rows),
        "failed_measured_rows": len(failed_rows),
        "measurement_evaluations": evaluations,
        "has_metric_contract": bool(required_metrics),
        "has_commands": command_count > 0,
        "has_expected_evidence": bool(step.get("expected_evidence")),
        "measurement_status": measurement_status,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Measurement Queue",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Real measured completion: `{report['real_measured_completion']}`",
        f"Measured tasks: `{report['measured_task_count']}/{report['task_count']}`",
        "",
        "| step | host class | status | accepted rows | commands | required metrics | thresholds |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for task in report["tasks"]:
        lines.append(
            f"| `{task['step_id']}` | {task['host_class']} | `{task['measurement_status']}` | "
            f"{task['accepted_measured_rows']}/{task['real_measured_rows']} | "
            f"{task['command_count']} | {', '.join(task['required_metrics'])} | "
            f"{'; '.join(task['acceptance_thresholds'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_measurement_queue() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    manifest = load_json(ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json", {})
    gpu_runs = load_json(ROOT / "gpu-runs" / "gpu-run-report.json", {})
    provenance = load_json(ROOT / "gpu-provenance" / "gpu-provenance-report.json", {})
    real_rows = _real_measured_rows(gpu_runs)
    tasks = [_task(step, real_rows) for step in manifest.get("steps", [])]
    queued = sum(1 for task in tasks if task["measurement_status"] == "queued-for-gpu-host")
    measured = sum(1 for task in tasks if task["real_measured_rows"] > 0)
    accepted = sum(1 for task in tasks if task["measurement_status"] == "measured-accepted")
    failed_measured = sum(1 for task in tasks if task["measurement_status"] == "measured-failed")
    has_contracts = all(task["has_metric_contract"] and task["has_commands"] and task["has_expected_evidence"] for task in tasks)
    real_complete = bool(tasks) and accepted == len(tasks)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "queue-ready" if len(tasks) >= 9 and has_contracts else "incomplete",
        "task_count": len(tasks),
        "queued_task_count": queued,
        "measured_task_count": measured,
        "accepted_task_count": accepted,
        "failed_measured_task_count": failed_measured,
        "real_measured_completion": real_complete,
        "source_manifest": "gpu-promotion/gpu-host-promotion-manifest.json",
        "source_gpu_runs": "gpu-runs/gpu-run-report.json",
        "source_provenance": "gpu-provenance/gpu-provenance-report.json",
        "real_gpu_evidence_status": provenance.get("real_gpu_evidence_status", "missing"),
        "measured_run_count": provenance.get("measured_run_count", 0),
        "tasks": tasks,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
