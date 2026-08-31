from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .builder import MEASUREMENT_SPECS, evaluate_step_metrics


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "gpu-measurement-queue" / "acceptance-logic-report.json"
REPORT_MD = ROOT / "gpu-measurement-queue" / "reports" / "acceptance-logic-report.md"


PASSING_METRICS: dict[str, dict[str, Any]] = {
    "cuda-kernel-compile": {"nvcc": True, "nvidia_smi": True, "torch_device": "cuda", "passed_benchmarks": 14},
    "triton-kernel-sweep": {"cuda_available": True, "triton_cases": 4, "passed_benchmarks": 14},
    "tensor-core-gemm": {"nvcc": True, "nvidia_smi": True, "ncu": True, "tensor_core_scenarios": 5, "mma_instruction_seen": True},
    "persistent-kernels": {"triton": True, "nvidia_smi": True, "ncu": True, "persistent_scenarios": 6, "speedup_vs_baseline": 1.30, "occupancy_proxy": 0.50, "hbm_reduction": 0.25},
    "parallel-primitives": {"accelerator_ready": True, "primitive_scenarios": 6, "work_efficiency": 1.35, "bandwidth_proxy_gbps": 1200.0, "occupancy_proxy": 0.55, "stable_order_scenarios": 3},
    "torch-custom-extension": {"compiled_extension_status": "cuda-ready", "passed_cases": 4},
    "model-integration-gpu": {"accelerator_ready": True, "passed_cases": 3, "uses_custom_op": "fused_bias_gelu_residual"},
    "vllm-serving-trace": {"cuda_available": True, "passed_traces": 3, "prefix_cache_blocks_saved": 1},
    "attention-serving-stack": {"cuda_available": True, "attention_scenarios": 5, "hbm_reduction": 0.50, "prefix_blocks_reused": 1, "profiler_rows": 1},
    "flash-attention-backward": {"cuda_available": True, "flash_backward_scenarios": 6, "gradient_paths": 4, "max_abs_error": 0.005, "hbm_reduction": 0.50, "recompute_overhead_ratio": 0.20, "occupancy_proxy": 0.60},
    "sparse-attention-kernels": {"cuda_available": True, "sparse_attention_scenarios": 6, "pattern_count": 6, "ragged_scenarios": 2, "backward_scenarios": 5, "max_abs_error": 0.006, "hbm_reduction": 0.72, "load_balance_proxy": 0.86},
    "fused-training-kernels": {"cuda_available": True, "fused_training_scenarios": 6, "family_count": 5, "backward_scenarios": 4, "optimizer_state_scenarios": 2, "max_abs_error": 0.006, "hbm_reduction": 0.52, "launch_reduction": 0.55},
    "speculative-decoding-serving": {"cuda_available": True, "speculative_scenarios": 6, "passed_scenarios": 4, "engine_count": 5, "scheduler_policy_count": 2, "min_acceptance_rate": 0.43, "max_speedup_vs_baseline": 6.6, "max_wasted_draft_ratio": 0.55},
    "profiler-capture": {"ncu": True, "nsys": True, "rocprof": False, "profiler_rows": 9},
    "rocm-hip-port": {"hipcc": True, "rocprof": True, "starter_status": "ran"},
    "distributed-collectives": {"torchrun": True, "accelerator_ready": True, "collective_scenarios": 6, "bandwidth_efficiency": 0.62, "overlap_gain": 0.12, "nccl_or_rccl": True},
    "distributed-training-optimizer": {"torchrun": True, "accelerator_ready": True, "training_optimizer_scenarios": 6, "passed_scenarios": 5, "max_memory_gb_per_gpu": 74.0, "step_time_ms": 820.0, "optimizer_state_savings": 0.82},
    "full-gpu-regression": {"accelerator_ready": True, "metric_count": 79, "failed_metrics": 0},
}


FAILING_METRICS: dict[str, dict[str, Any]] = {
    "cuda-kernel-compile": {"nvcc": True, "nvidia_smi": False, "torch_device": "cpu", "passed_benchmarks": 14},
    "triton-kernel-sweep": {"cuda_available": False, "triton_cases": 4, "passed_benchmarks": 14},
    "tensor-core-gemm": {"nvcc": True, "nvidia_smi": True, "ncu": False, "tensor_core_scenarios": 5, "mma_instruction_seen": True},
    "persistent-kernels": {"triton": True, "nvidia_smi": True, "ncu": False, "persistent_scenarios": 6, "speedup_vs_baseline": 1.30, "occupancy_proxy": 0.50, "hbm_reduction": 0.25},
    "parallel-primitives": {"accelerator_ready": True, "primitive_scenarios": 6, "work_efficiency": 1.05, "bandwidth_proxy_gbps": 1200.0, "occupancy_proxy": 0.55, "stable_order_scenarios": 3},
    "torch-custom-extension": {"compiled_extension_status": "source-only", "passed_cases": 4},
    "model-integration-gpu": {"accelerator_ready": False, "passed_cases": 3, "uses_custom_op": "fused_bias_gelu_residual"},
    "vllm-serving-trace": {"cuda_available": False, "passed_traces": 3, "prefix_cache_blocks_saved": 1},
    "attention-serving-stack": {"cuda_available": False, "attention_scenarios": 5, "hbm_reduction": 0.50, "prefix_blocks_reused": 1, "profiler_rows": 1},
    "flash-attention-backward": {"cuda_available": True, "flash_backward_scenarios": 6, "gradient_paths": 4, "max_abs_error": 0.05, "hbm_reduction": 0.50, "recompute_overhead_ratio": 0.20, "occupancy_proxy": 0.60},
    "sparse-attention-kernels": {"cuda_available": True, "sparse_attention_scenarios": 6, "pattern_count": 6, "ragged_scenarios": 2, "backward_scenarios": 5, "max_abs_error": 0.006, "hbm_reduction": 0.72, "load_balance_proxy": 0.60},
    "fused-training-kernels": {"cuda_available": True, "fused_training_scenarios": 6, "family_count": 5, "backward_scenarios": 4, "optimizer_state_scenarios": 2, "max_abs_error": 0.006, "hbm_reduction": 0.30, "launch_reduction": 0.55},
    "speculative-decoding-serving": {"cuda_available": True, "speculative_scenarios": 6, "passed_scenarios": 4, "engine_count": 5, "scheduler_policy_count": 2, "min_acceptance_rate": 0.43, "max_speedup_vs_baseline": 1.4, "max_wasted_draft_ratio": 0.55},
    "profiler-capture": {"ncu": False, "nsys": False, "rocprof": False, "profiler_rows": 9},
    "rocm-hip-port": {"hipcc": False, "rocprof": True, "starter_status": "ran"},
    "distributed-collectives": {"torchrun": True, "accelerator_ready": True, "collective_scenarios": 6, "bandwidth_efficiency": 0.40, "overlap_gain": 0.12, "nccl_or_rccl": True},
    "distributed-training-optimizer": {"torchrun": True, "accelerator_ready": True, "training_optimizer_scenarios": 6, "passed_scenarios": 5, "max_memory_gb_per_gpu": 96.0, "step_time_ms": 820.0, "optimizer_state_savings": 0.82},
    "full-gpu-regression": {"accelerator_ready": True, "metric_count": 79, "failed_metrics": 1},
}


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE GPU Acceptance Logic",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Accepted good cases: `{report['accepted_good_cases']}/{report['case_count']}`",
        f"Rejected bad cases: `{report['rejected_bad_cases']}/{report['case_count']}`",
        "",
        "| step | good accepted | bad rejected | checks |",
        "|---|---:|---:|---|",
    ]
    for row in report["cases"]:
        checks = ", ".join(row["good"]["checks"].keys())
        lines.append(f"| `{row['step_id']}` | `{row['good']['accepted']}` | `{not row['bad']['accepted']}` | {checks} |")
    return "\n".join(lines).rstrip() + "\n"


def build_acceptance_logic_report() -> dict[str, Any]:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    cases = []
    for step_id in sorted(MEASUREMENT_SPECS):
        good = evaluate_step_metrics(step_id, PASSING_METRICS[step_id])
        bad = evaluate_step_metrics(step_id, FAILING_METRICS[step_id])
        cases.append(
            {
                "step_id": step_id,
                "good_metrics": PASSING_METRICS[step_id],
                "bad_metrics": FAILING_METRICS[step_id],
                "good": good,
                "bad": bad,
            }
        )
    accepted_good = sum(1 for row in cases if row["good"]["accepted"])
    rejected_bad = sum(1 for row in cases if not row["bad"]["accepted"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if accepted_good == len(cases) and rejected_bad == len(cases) else "failed",
        "case_count": len(cases),
        "accepted_good_cases": accepted_good,
        "rejected_bad_cases": rejected_bad,
        "cases": cases,
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
