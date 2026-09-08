#!/usr/bin/env python3
"""Remote Colab entrypoint for the GPU curriculum promotion suite."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


CONTENT = Path("/content")
ARCHIVE = CONTENT / "gpu-mode-curriculum.tgz"
WORKDIR = CONTENT / "gpu-mode-curriculum"
CONFIG = CONTENT / "colab-run-config.json"
SUMMARY = CONTENT / "colab-gpu-handoff-summary.json"


def run(command: list[str], cwd: Path, timeout: int = 1800) -> dict[str, object]:
    started = datetime.now(timezone.utc).isoformat()
    print("$ " + " ".join(command), flush=True)
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if result.stdout:
            print(result.stdout[-4000:], flush=True)
        if result.stderr:
            print(result.stderr[-4000:], file=sys.stderr, flush=True)
        return {
            "command": command,
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "returncode": result.returncode,
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout_tail": result.stdout[-4000:],
            "stderr_tail": result.stderr[-4000:],
        }
    except Exception as exc:
        print(str(exc), file=sys.stderr, flush=True)
        return {
            "command": command,
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "returncode": None,
            "status": "failed",
            "stdout_tail": "",
            "stderr_tail": str(exc),
        }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def unpack_archive() -> None:
    if not ARCHIVE.exists():
        raise FileNotFoundError(f"missing uploaded archive: {ARCHIVE}")
    if WORKDIR.exists():
        run(["rm", "-rf", str(WORKDIR)], CONTENT, timeout=120)
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        archive.extractall(CONTENT)
    if not WORKDIR.exists():
        raise FileNotFoundError(f"archive did not create {WORKDIR}")


def load_run_id() -> str:
    if CONFIG.exists():
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        return str(config.get("run_id") or "colab-advanced-phase")
    return os.environ.get("COLAB_RUN_ID", "colab-advanced-phase")


def load_mode() -> str:
    if CONFIG.exists():
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        return str(config.get("mode") or "full")
    return "full"


def main() -> int:
    run_id = load_run_id()
    mode = load_mode()
    unpack_archive()
    if mode == "paged-kv":
        commands = [{"cmd": [sys.executable, "gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py"], "required": True}]
    elif mode == "paged-attention":
        commands = [{"cmd": [sys.executable, "gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py"], "required": True}]
    elif mode == "serving-tail":
        commands = [{"cmd": [sys.executable, "model-integration/run_serving_tail_load_cuda.py"], "required": True}]
    elif mode == "serving-tail-graphs":
        commands = [{"cmd": [sys.executable, "model-integration/run_serving_tail_load_cuda.py", "--mode", "cuda_graph_microbatch"], "required": True}]
    elif mode == "digits-quality":
        commands = [{"cmd": [sys.executable, "quantization-memory-formats/run_digits_cuda.py"], "required": True}]
    elif mode == "eager-kernels":
        commands = [{"cmd": [sys.executable, "scripts/run_kernel_benchmarks.py", "--repeats", "7"], "required": True}]
    elif mode == "wmma-profiler":
        commands = [{"cmd": [sys.executable, "tensor-core-gemm/profile_native.py"], "required": True}]
    elif mode == "batch1-decode":
        commands = [
            {"cmd": [sys.executable, "batch1-decode-vertical-slice/run_decode_comparison.py"], "required": True},
            {"cmd": [sys.executable, "batch1-decode-vertical-slice/run_serving_bridge.py"], "required": True},
            {"cmd": [sys.executable, "batch1-decode-vertical-slice/run_profiler_evidence.py"], "required": True},
        ]
    elif mode == "batch1-profile":
        commands = [{"cmd": [sys.executable, "batch1-decode-vertical-slice/run_profiler_evidence.py"], "required": True}]
    elif mode == "batch1-graphs":
        commands = [{"cmd": [sys.executable, "batch1-decode-vertical-slice/run_decode_comparison.py"], "required": True}]
    else:
        commands = [
        {"cmd": [sys.executable, "scripts/verify_advanced_phase.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_gpu_host_preflight.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_kernel_benchmarks.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_gpu_programming_projects.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_tensor_core_gemm.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_persistent_kernels.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_parallel_primitives.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_custom_ops.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_autotune_db.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_model_integration.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_serving_traces.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_kv_cache_paged_attention.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_attention_serving_stack.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_flash_attention_backward.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_sparse_attention_kernels.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_fused_training_kernels.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_speculative_decoding_serving.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_distributed_collectives.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_distributed_collectives_benchmark.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_distributed_training_optimizer.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_moe_routing_all_to_all.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_quantization_memory_formats.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_numerical_reproducibility.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_cuda_graphs_latency.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_multi_tenant_gpu_scheduling.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_regression_ledger.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_gpu_promotion.py"], "required": True},
        {"cmd": [sys.executable, "scripts/run_gpu_promotion_suite.py", "--run-id", run_id], "required": True},
        {"cmd": [sys.executable, "scripts/collect_gpu_run.py", "--run-id", run_id], "required": True},
        {"cmd": [sys.executable, "scripts/build_gpu_runs.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_gpu_provenance.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_gpu_measurement_queue.py"], "required": True},
        {"cmd": [sys.executable, "scripts/build_capstone_acceptance.py"], "required": False},
        {"cmd": [sys.executable, "scripts/verify_gpu_runs.py"], "required": True},
        {"cmd": [sys.executable, "scripts/verify_gpu_provenance.py"], "required": True},
        {"cmd": [sys.executable, "scripts/verify_gpu_measurement_queue.py"], "required": True},
        {"cmd": [sys.executable, "scripts/verify_capstone_acceptance.py"], "required": False},
        ]

    results = []
    failed = False
    for entry in commands:
        command = entry["cmd"]
        row = run(command, WORKDIR)
        row["required"] = entry["required"]
        results.append(row)
        if row["status"] == "failed" and entry["required"]:
            failed = True
            break

    summary = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workdir": str(WORKDIR),
        "failed": failed,
        "commands": results,
        "artifacts": {
            "gpu_run_import": str(WORKDIR / "gpu-runs" / "imports" / f"{run_id}.json"),
            "suite_report": str(WORKDIR / "gpu-promotion" / "suite-run-report.json"),
            "queue": str(WORKDIR / "gpu-measurement-queue" / "gpu-measurement-queue.json"),
            "capstone": str(WORKDIR / "capstone-acceptance" / "capstone-acceptance.json"),
        },
    }
    write_json(SUMMARY, summary)
    write_json(WORKDIR / "colab-gpu-handoff-summary.json", summary)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
