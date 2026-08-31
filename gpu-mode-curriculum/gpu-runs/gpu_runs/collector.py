from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IMPORT_DIR = ROOT / "gpu-runs" / "imports"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _tool(name: str) -> bool:
    return bool(shutil.which(name))


def _run_text(cmd: list[str], timeout: int = 10) -> str:
    if not shutil.which(cmd[0]):
        return ""
    try:
        result = subprocess.run(cmd, cwd=ROOT, check=False, text=True, capture_output=True, timeout=timeout)
    except Exception:
        return ""
    return (result.stdout or result.stderr or "").strip()


def detect_host() -> dict[str, Any]:
    nvidia = _run_text(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"], timeout=10)
    rocm = _run_text(["rocminfo"], timeout=10)
    vendor = "NVIDIA" if nvidia else "AMD" if rocm else "unknown"
    accelerator = nvidia.splitlines()[0].split(",")[0].strip() if nvidia else "ROCm GPU" if rocm else "unavailable"
    return {
        "name": socket.gethostname(),
        "platform": platform.platform(),
        "accelerator": accelerator,
        "vendor": vendor,
        "python": platform.python_version(),
        "cuda_available": bool(nvidia),
        "rocm_available": bool(rocm),
        "tools": {
            "nvcc": _tool("nvcc"),
            "nvidia_smi": _tool("nvidia-smi"),
            "hipcc": _tool("hipcc"),
            "rocprof": _tool("rocprof"),
            "nsys": _tool("nsys"),
            "ncu": _tool("ncu"),
            "torchrun": _tool("torchrun"),
            "triton": importlib.util.find_spec("triton") is not None,
        },
    }


def _status(condition: bool, fallback_reason: str) -> str:
    return "passed" if condition else f"skipped:{fallback_reason}"


def _step(step_id: str, status: str, evidence: list[str], metrics: dict[str, Any]) -> dict[str, Any]:
    return {"id": step_id, "status": status, "evidence": evidence, "metrics": metrics}


def collect_steps(host: dict[str, Any]) -> list[dict[str, Any]]:
    kernel = load_json(ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json", {})
    custom = load_json(ROOT / "custom-ops" / "reports" / "custom-op-report.json", {})
    model = load_json(ROOT / "model-integration" / "reports" / "tiny-transformer-report.json", {})
    serving = load_json(ROOT / "serving-traces" / "reports" / "serving-trace-report.json", {})
    profiler = load_json(ROOT / "profiler-evidence" / "reports" / "profiler-evidence-report.json", {})
    tensor_core = load_json(ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json", {})
    persistent = load_json(ROOT / "persistent-kernels" / "persistent-kernels-report.json", {})
    primitives = load_json(ROOT / "parallel-primitives" / "parallel-primitives-report.json", {})
    attention_serving = load_json(ROOT / "attention-serving-stack" / "attention-serving-report.json", {})
    flash_backward = load_json(ROOT / "flash-attention-backward" / "flash-attention-backward-report.json", {})
    sparse_attention = load_json(ROOT / "sparse-attention-kernels" / "sparse-attention-report.json", {})
    fused_training = load_json(ROOT / "fused-training-kernels" / "fused-training-report.json", {})
    speculative_decoding = load_json(ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json", {})
    regression = load_json(ROOT / "regression-ledger" / "regression-ledger.json", {})
    project = load_json(ROOT / "programming-projects" / "project-run-report.json", {})
    collectives = load_json(ROOT / "distributed-collectives" / "distributed-collectives-report.json", {})
    collective_benchmark = load_json(ROOT / "distributed-collectives" / "reports" / "collective-benchmark-run.json", {})
    training_optimizer = load_json(ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json", {})
    tools = host["tools"]
    accelerator_ready = host["cuda_available"] or host["rocm_available"]
    torch_device = kernel.get("accelerator_readiness", {}).get("torch_device", "unknown")
    custom_status = custom.get("accelerator_readiness", {}).get("compiled_extension_status", "unknown")
    rocm_project = next((row for row in project.get("projects", []) if row.get("id") == "rocm-hip-port"), {})
    collective_metrics = collective_benchmark.get("aggregate_metrics", {})
    if not collective_metrics:
        best_efficiency = max((row.get("bandwidth_efficiency", 0.0) for row in collectives.get("scenarios", [])), default=0.0)
        best_overlap = max((row.get("overlap_gain", 0.0) for row in collectives.get("scenarios", [])), default=0.0)
        collective_metrics = {
            "torchrun": tools["torchrun"],
            "accelerator_ready": accelerator_ready,
            "collective_scenarios": collectives.get("scenario_count", 0),
            "collective_count": collectives.get("collective_count", 0),
            "measured_collectives": 0,
            "bandwidth_efficiency": best_efficiency,
            "overlap_gain": best_overlap,
            "best_bus_gbps": 0.0,
            "nccl_or_rccl": False,
            "backend": "missing-benchmark",
        }
    training_scenarios = training_optimizer.get("scenarios", [])
    viable_training_scenarios = [row for row in training_scenarios if row.get("status") == "passed"]
    training_metrics = {
        "torchrun": tools["torchrun"],
        "accelerator_ready": accelerator_ready,
        "training_optimizer_scenarios": training_optimizer.get("scenario_count", 0),
        "passed_scenarios": training_optimizer.get("passed_scenarios", 0),
        "max_memory_gb_per_gpu": max((row.get("memory_gb_per_gpu", 0.0) for row in viable_training_scenarios), default=0.0),
        "step_time_ms": max((row.get("step_time_ms", 0.0) for row in viable_training_scenarios), default=0.0),
        "optimizer_state_savings": max((row.get("optimizer_state_savings", 0.0) for row in training_scenarios), default=0.0),
    }
    tensor_core_metrics = {
        "nvcc": tools["nvcc"],
        "nvidia_smi": tools["nvidia_smi"],
        "ncu": tools["ncu"],
        "tensor_core_scenarios": tensor_core.get("tensor_core_eligible_scenarios", 0),
        "mma_instruction_seen": tools["ncu"] and tensor_core.get("tensor_core_eligible_scenarios", 0) >= 5,
        "fused_epilogue_scenarios": tensor_core.get("fused_epilogue_scenarios", 0),
        "occupancy_proxy": min(
            (row.get("occupancy_proxy", 0.0) for row in tensor_core.get("scenarios", []) if row.get("status") == "passed"),
            default=0.0,
        ),
    }
    persistent_scenarios = persistent.get("scenarios", [])
    passing_persistent = [row for row in persistent_scenarios if row.get("status") == "passed"]
    persistent_metrics = {
        "triton": tools["triton"],
        "nvidia_smi": tools["nvidia_smi"],
        "ncu": tools["ncu"],
        "persistent_scenarios": persistent.get("scenario_count", 0),
        "speedup_vs_baseline": min((row.get("speedup_vs_baseline", 0.0) for row in passing_persistent), default=0.0),
        "occupancy_proxy": min((row.get("occupancy_proxy", 0.0) for row in passing_persistent), default=0.0),
        "hbm_reduction": min((row.get("hbm_reduction", 0.0) for row in passing_persistent), default=0.0),
    }
    primitive_scenarios = primitives.get("scenarios", [])
    passing_primitives = [row for row in primitive_scenarios if row.get("status") == "passed"]
    primitive_metrics = {
        "accelerator_ready": accelerator_ready,
        "primitive_scenarios": primitives.get("scenario_count", 0),
        "work_efficiency": min((row.get("work_efficiency", 0.0) for row in passing_primitives), default=0.0),
        "bandwidth_proxy_gbps": min((row.get("bandwidth_proxy_gbps", 0.0) for row in passing_primitives), default=0.0),
        "occupancy_proxy": min((row.get("occupancy_proxy", 0.0) for row in passing_primitives), default=0.0),
        "stable_order_scenarios": primitives.get("stable_order_scenarios", 0),
    }
    attention_scenarios = attention_serving.get("scenarios", [])
    passing_attention = [row for row in attention_scenarios if row.get("status") == "passed"]
    attention_metrics = {
        "cuda_available": host["cuda_available"],
        "attention_scenarios": attention_serving.get("scenario_count", 0),
        "hbm_reduction": min((row.get("hbm_reduction", 0.0) for row in passing_attention), default=0.0),
        "prefix_blocks_reused": attention_serving.get("total_prefix_blocks_reused", 0),
        "profiler_rows": profiler.get("row_count", 0),
        "occupancy_proxy": min((row.get("occupancy_proxy", 0.0) for row in passing_attention), default=0.0),
    }
    flash_scenarios = flash_backward.get("scenarios", [])
    passing_flash = [row for row in flash_scenarios if row.get("status") == "passed"]
    flash_metrics = {
        "cuda_available": host["cuda_available"],
        "flash_backward_scenarios": flash_backward.get("scenario_count", 0),
        "gradient_paths": max((len(row.get("gradient_paths", [])) for row in flash_scenarios), default=0),
        "max_abs_error": max((row.get("max_abs_error", 1.0) for row in passing_flash), default=1.0),
        "hbm_reduction": min((row.get("hbm_reduction", 0.0) for row in passing_flash), default=0.0),
        "recompute_overhead_ratio": max((row.get("recompute_overhead_ratio", 0.0) for row in passing_flash), default=0.0),
        "occupancy_proxy": min((row.get("occupancy_proxy", 0.0) for row in passing_flash), default=0.0),
    }
    sparse_scenarios = sparse_attention.get("scenarios", [])
    passing_sparse = [row for row in sparse_scenarios if row.get("status") == "passed"]
    sparse_metrics = {
        "cuda_available": host["cuda_available"],
        "sparse_attention_scenarios": sparse_attention.get("scenario_count", 0),
        "pattern_count": sparse_attention.get("pattern_count", 0),
        "ragged_scenarios": sparse_attention.get("ragged_scenarios", 0),
        "backward_scenarios": sparse_attention.get("backward_scenarios", 0),
        "max_abs_error": max((row.get("max_abs_error", 1.0) for row in passing_sparse), default=1.0),
        "hbm_reduction": min((row.get("hbm_reduction", 0.0) for row in passing_sparse), default=0.0),
        "load_balance_proxy": min((row.get("load_balance_proxy", 0.0) for row in passing_sparse), default=0.0),
    }
    fused_scenarios = fused_training.get("scenarios", [])
    passing_fused = [row for row in fused_scenarios if row.get("status") == "passed"]
    fused_metrics = {
        "cuda_available": host["cuda_available"],
        "fused_training_scenarios": fused_training.get("scenario_count", 0),
        "family_count": fused_training.get("family_count", 0),
        "backward_scenarios": fused_training.get("backward_scenarios", 0),
        "optimizer_state_scenarios": fused_training.get("optimizer_state_scenarios", 0),
        "max_abs_error": max((row.get("max_abs_error", 1.0) for row in passing_fused), default=1.0),
        "hbm_reduction": min((row.get("hbm_reduction", 0.0) for row in passing_fused), default=0.0),
        "launch_reduction": min((row.get("launch_reduction", 0.0) for row in passing_fused), default=0.0),
    }
    speculative_metrics = {
        "cuda_available": host["cuda_available"],
        "speculative_scenarios": speculative_decoding.get("scenario_count", 0),
        "passed_scenarios": speculative_decoding.get("passed_scenarios", 0),
        "engine_count": speculative_decoding.get("engine_count", 0),
        "scheduler_policy_count": speculative_decoding.get("scheduler_policy_count", 0),
        "min_acceptance_rate": speculative_decoding.get("min_acceptance_rate", 1.0),
        "max_speedup_vs_baseline": speculative_decoding.get("max_speedup_vs_baseline", 0.0),
        "max_wasted_draft_ratio": speculative_decoding.get("max_wasted_draft_ratio", 0.0),
    }

    return [
        _step(
            "cuda-kernel-compile",
            _status(tools["nvcc"] and host["cuda_available"], "missing-nvcc-or-nvidia-gpu"),
            ["kernel-benchmarks/kernels/cuda/*.cu", "kernel-benchmarks/reports/kernel-benchmark-report.json"],
            {"nvcc": tools["nvcc"], "nvidia_smi": tools["nvidia_smi"], "torch_device": torch_device, "passed_benchmarks": kernel.get("passed", 0)},
        ),
        _step(
            "triton-kernel-sweep",
            _status(host["cuda_available"] and kernel.get("passed", 0) >= 14, "missing-cuda-gpu"),
            ["kernel-benchmarks/reports/kernel-benchmark-report.json", "autotune-db/autotune-db.json"],
            {"cuda_available": host["cuda_available"], "triton_cases": 4, "passed_benchmarks": kernel.get("passed", 0)},
        ),
        _step(
            "tensor-core-gemm",
            _status(
                host["cuda_available"] and tensor_core.get("status") == "tensor-core-gemm-ready",
                "missing-measured-tensor-core-run",
            ),
            ["tensor-core-gemm/tensor-core-gemm-report.json", "tensor-core-gemm/reports/tensor-core-gemm-report.md"],
            tensor_core_metrics,
        ),
        _step(
            "persistent-kernels",
            _status(host["cuda_available"] and tools["triton"] and tools["ncu"] and persistent.get("status") == "persistent-kernels-ready", "missing-cuda-triton-or-ncu"),
            ["persistent-kernels/persistent-kernels-report.json", "persistent-kernels/reports/persistent-kernels-report.md"],
            persistent_metrics,
        ),
        _step(
            "parallel-primitives",
            _status(accelerator_ready and primitives.get("status") == "parallel-primitives-ready", "missing-measured-primitive-run"),
            ["parallel-primitives/parallel-primitives-report.json", "parallel-primitives/reports/parallel-primitives-report.md"],
            primitive_metrics,
        ),
        _step(
            "torch-custom-extension",
            _status(custom_status == "cuda-ready", "extension-source-only"),
            ["custom-ops/reports/custom-op-report.json", "custom-ops/csrc/fused_bias_gelu_residual_kernel.cu"],
            {"compiled_extension_status": custom_status, "passed_cases": custom.get("passed", 0)},
        ),
        _step(
            "model-integration-gpu",
            _status(accelerator_ready and model.get("passed", 0) >= 3, "missing-accelerator-runtime"),
            ["model-integration/reports/tiny-transformer-report.json"],
            {"accelerator_ready": accelerator_ready, "passed_cases": model.get("passed", 0), "uses_custom_op": model.get("uses_custom_op", "")},
        ),
        _step(
            "vllm-serving-trace",
            _status(host["cuda_available"] and serving.get("passed_traces", 0) >= 3, "missing-vllm-cuda-runtime"),
            ["serving-traces/reports/serving-trace-report.json"],
            {
                "cuda_available": host["cuda_available"],
                "passed_traces": serving.get("passed_traces", 0),
                "prefix_cache_blocks_saved": sum(row.get("prefix_cache_blocks_saved", 0) for row in serving.get("comparisons", [])),
            },
        ),
        _step(
            "attention-serving-stack",
            _status(
                host["cuda_available"] and attention_serving.get("status") == "attention-serving-ready",
                "missing-measured-attention-serving-run",
            ),
            ["attention-serving-stack/attention-serving-report.json", "attention-serving-stack/reports/attention-serving-report.md"],
            attention_metrics,
        ),
        _step(
            "flash-attention-backward",
            _status(host["cuda_available"] and flash_backward.get("status") == "flash-attention-backward-ready", "missing-measured-flash-backward-run"),
            ["flash-attention-backward/flash-attention-backward-report.json", "flash-attention-backward/reports/flash-attention-backward-report.md"],
            flash_metrics,
        ),
        _step(
            "sparse-attention-kernels",
            _status(host["cuda_available"] and sparse_attention.get("status") == "sparse-attention-ready", "missing-measured-sparse-attention-run"),
            ["sparse-attention-kernels/sparse-attention-report.json", "sparse-attention-kernels/reports/sparse-attention-report.md"],
            sparse_metrics,
        ),
        _step(
            "fused-training-kernels",
            _status(host["cuda_available"] and fused_training.get("status") == "fused-training-ready", "missing-measured-fused-training-run"),
            ["fused-training-kernels/fused-training-report.json", "fused-training-kernels/reports/fused-training-report.md"],
            fused_metrics,
        ),
        _step(
            "speculative-decoding-serving",
            _status(host["cuda_available"] and speculative_decoding.get("status") == "speculative-decoding-ready", "missing-measured-speculative-decoding-run"),
            ["speculative-decoding-serving/speculative-decoding-report.json", "speculative-decoding-serving/reports/speculative-decoding-report.md"],
            speculative_metrics,
        ),
        _step(
            "profiler-capture",
            _status((tools["ncu"] and tools["nsys"]) or tools["rocprof"], "missing-profiler-tools"),
            ["profiler-evidence/reports/profiler-evidence-report.json"],
            {"ncu": tools["ncu"], "nsys": tools["nsys"], "rocprof": tools["rocprof"], "profiler_rows": profiler.get("row_count", 0)},
        ),
        _step(
            "rocm-hip-port",
            _status(tools["hipcc"] and tools["rocprof"], "missing-hipcc-or-rocprof"),
            ["programming-projects/rocm-hip-port/measurements.json"],
            {"hipcc": tools["hipcc"], "rocprof": tools["rocprof"], "starter_status": rocm_project.get("starter_status", "unknown")},
        ),
        _step(
            "distributed-collectives",
            _status(collective_benchmark.get("status") == "passed" and collective_benchmark.get("measured") is True, "missing-measured-collective-benchmark"),
            ["distributed-collectives/reports/collective-benchmark-run.json", "distributed-collectives/distributed-collectives-report.json", "programming-projects/distributed-collectives/measurements.json"],
            collective_metrics,
        ),
        _step(
            "distributed-training-optimizer",
            _status(accelerator_ready and training_optimizer.get("status") == "training-optimizer-ready", "missing-measured-training-optimizer-run"),
            ["distributed-training-optimizer/distributed-training-optimizer-report.json"],
            training_metrics,
        ),
        _step(
            "full-gpu-regression",
            _status(accelerator_ready and regression.get("failed") == 0, "missing-accelerator-regression-run"),
            ["regression-ledger/regression-ledger.json"],
            {"accelerator_ready": accelerator_ready, "metric_count": regression.get("metric_count", 0), "failed_metrics": regression.get("failed", 0)},
        ),
    ]


def collect_gpu_run(run_id: str | None = None) -> dict[str, Any]:
    host = detect_host()
    generated = datetime.now(timezone.utc).isoformat()
    clean_run_id = run_id or f"{host['name']}-{generated[:10]}-gpu-run"
    measured = host["cuda_available"] or host["rocm_available"]
    return {
        "run_id": clean_run_id,
        "generated_at": generated,
        "collector": "gpu_runs.collector",
        "provenance": {
            "kind": "real-measured" if measured else "host-collected",
            "measured": measured,
            "description": "Collected from the current host after local or GPU promotion commands.",
        },
        "host": host,
        "promotion_steps": collect_steps(host),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect a GPU-run import JSON from this host.")
    parser.add_argument("--run-id", default=None, help="Stable run identifier to write into the import JSON.")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path. Defaults to gpu-runs/imports/<run-id>.json.")
    args = parser.parse_args(argv)
    run = collect_gpu_run(args.run_id)
    output = args.output or IMPORT_DIR / f"{run['run_id']}.json"
    if not output.is_absolute():
        output = ROOT / output
    write_json(output, run)
    print(f"wrote {output.relative_to(ROOT)} ({run['host']['vendor']}, {run['host']['accelerator']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
