#!/usr/bin/env python3
"""Reproduce the advanced GEMM/attention/training checkpoint, not the full goal."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CURRICULUM = REPO / "gpu-mode-curriculum"
REPORT = CURRICULUM / "advanced-lab-phase/executable-checkpoint.json"


def check_source_hashes(artifact: dict, repo: Path = REPO) -> list[str]:
    # Reports in the older lab schema nest hashes under provenance; newer
    # experiment reports expose the same contract at the top level.  Both forms
    # are accepted, but every listed path is still resolved and byte-checked.
    hashes = (artifact.get("provenance", {}).get("source_sha256", {})
              or artifact.get("source_sha256", {}))
    if not hashes:
        return ["missing source hashes"]
    errors = []
    for relative, expected in hashes.items():
        path = (repo / relative).resolve()
        if not path.is_relative_to(repo.resolve()):
            errors.append(f"source outside repository: {relative}")
        elif not path.is_file():
            errors.append(f"missing source: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"stale source: {relative}")
    return errors


def tasks():
    for name, directory in (
        ("foundation-gemm-tests", "gpu-kernels-serving-lab/tests"),
        ("benchmark-validation-tests", "gpu-mode-curriculum/kernel-benchmarks/tests"),
        ("attention-tests", "gpu-mode-curriculum/flash-attention-backward/tests"),
        ("integration-tests", "gpu-mode-curriculum/model-integration/tests"),
        ("checkpoint-tests", "gpu-mode-curriculum/advanced-lab-phase/tests"),
        ("hip-harness-tests", "gpu-mode-curriculum/programming-projects/rocm-hip-port"),
        ("primitive-reference-tests", "gpu-mode-curriculum/parallel-primitives/tests"),
        ("collective-contract-tests", "gpu-mode-curriculum/distributed-collectives/tests"),
        ("moe-reference-contract-tests", "gpu-mode-curriculum/moe-routing-all-to-all/tests"),
        ("profiler-evidence-tests", "gpu-mode-curriculum/profiler-evidence/tests"),
    ):
        yield name, ["-m", "unittest", "discover", "-s", directory, "-v"], None
    for name, script, artifact, extra in (
        ("gemm", "gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/run.py",
         "gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/out_gpumode_shared_memory_gemm.json", []),
        ("packed-int4", "gpu-kernels-serving-lab/08-quantized-inference/run_packed_int4.py",
         "gpu-kernels-serving-lab/08-quantized-inference/out_packed_int4.json", []),
        ("digits-quality", "gpu-kernels-serving-lab/08-quantized-inference/run_digits_quality.py",
         "gpu-kernels-serving-lab/08-quantized-inference/out_digits_quality.json", []),
        ("digits-repeated-quality", "gpu-kernels-serving-lab/08-quantized-inference/run_digits_repeats.py",
         "gpu-kernels-serving-lab/08-quantized-inference/out_digits_repeats.json", []),
        ("attention-reference", "gpu-mode-curriculum/flash-attention-backward/run_reference.py",
         "gpu-mode-curriculum/flash-attention-backward/reports/executable-reference-cpu.json", []),
        ("training-equivalence", "gpu-mode-curriculum/model-integration/run_attention_training.py",
         "gpu-mode-curriculum/model-integration/reports/attention-training-cpu.json", []),
        ("training-benchmark-cpu", "gpu-mode-curriculum/model-integration/run_attention_benchmark.py",
         "gpu-mode-curriculum/model-integration/reports/attention-benchmark-cpu.json", ["--device", "cpu"]),
        ("cached-decode-cpu", "gpu-mode-curriculum/model-integration/run_cached_decode.py",
         "gpu-mode-curriculum/model-integration/reports/cached-decode-cpu.json", []),
        ("packed-model-cpu", "gpu-mode-curriculum/model-integration/run_packed_model.py",
         "gpu-mode-curriculum/model-integration/reports/packed-model-cpu.json", []),
        ("neural-serving-cpu", "gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_neural_load.py",
         "gpu-kernels-serving-lab/13-capstone-mini-serving-engine/out_neural_load.json", []),
        ("serving-admission-cpu", "gpu-mode-curriculum/model-integration/run_serving_admission.py",
         "gpu-mode-curriculum/model-integration/reports/serving-admission-cpu.json", []),
        ("serving-backpressure-cpu", "gpu-mode-curriculum/model-integration/run_serving_backpressure.py",
         "gpu-mode-curriculum/model-integration/reports/serving-backpressure-cpu.json", []),
        ("serving-microbatch-cpu", "gpu-mode-curriculum/model-integration/run_serving_microbatch.py",
         "gpu-mode-curriculum/model-integration/reports/serving-microbatch-cpu.json", []),
        ("serving-http-controls-cpu", "gpu-mode-curriculum/model-integration/run_serving_http_controls.py",
         "gpu-mode-curriculum/model-integration/reports/serving-http-controls-cpu.json", []),
        ("serving-disconnect-cancellation-cpu", "gpu-mode-curriculum/model-integration/run_serving_disconnect_cancellation.py",
         "gpu-mode-curriculum/model-integration/reports/serving-disconnect-cancellation-cpu.json", []),
        ("serving-streaming-cpu", "gpu-mode-curriculum/model-integration/run_serving_streaming.py",
         "gpu-mode-curriculum/model-integration/reports/serving-streaming-cpu.json", []),
        ("serving-tail-load-cpu", "gpu-mode-curriculum/model-integration/run_serving_tail_load.py",
         "gpu-mode-curriculum/model-integration/reports/serving-tail-load-cpu.json", []),
        ("distributed-serving-cpu", "gpu-mode-curriculum/model-integration/run_distributed_serving_cpu.py",
         "gpu-mode-curriculum/model-integration/reports/distributed-serving-cpu.json", []),
        ("compiler-forward-backward-cpu", "gpu-mode-curriculum/compiler-runtime-inspection/run_cpu_compile.py",
         "gpu-mode-curriculum/compiler-runtime-inspection/reports/cpu-compile.json", []),
        ("compiled-training-cpu", "gpu-mode-curriculum/model-integration/run_compiled_training.py",
         "gpu-mode-curriculum/model-integration/reports/compiled-training-cpu.json", []),
        ("training-benchmark-cuda", "gpu-mode-curriculum/model-integration/run_attention_benchmark.py",
         "gpu-mode-curriculum/model-integration/reports/attention-benchmark-cuda.json", ["--device", "cuda"]),
        ("hip-native", "gpu-mode-curriculum/programming-projects/rocm-hip-port/run_native.py",
         "gpu-mode-curriculum/programming-projects/rocm-hip-port/native-execution.json", []),
        ("collective-correctness-cpu", "gpu-mode-curriculum/distributed-collectives/run_cpu_correctness.py",
         "gpu-mode-curriculum/distributed-collectives/reports/cpu-correctness.json", []),
        ("moe-distributed-cpu", "gpu-mode-curriculum/moe-routing-all-to-all/run_distributed_reference.py",
         "gpu-mode-curriculum/moe-routing-all-to-all/reports/distributed-reference-cpu.json", []),
        ("profiler-evidence", "gpu-mode-curriculum/scripts/run_profiler_evidence.py",
         "gpu-mode-curriculum/profiler-evidence/reports/profiler-evidence-report.json", []),
        ("colab-handoff-contract", "gpu-mode-curriculum/scripts/verify_colab_handoff.py",
         "gpu-mode-curriculum/gpu-runs/reports/colab-handoff-contract.json", []),
    ):
        yield name, [script, *extra], artifact


def test_source_hashes():
    hashes = {}
    # This CPU reference has tests but no experiment artifact carrying its hashes.
    reference = CURRICULUM / "parallel-primitives/parallel_primitives/reference.py"
    hashes[str(reference.relative_to(REPO))] = hashlib.sha256(reference.read_bytes()).hexdigest()
    for _, args, artifact in tasks():
        if artifact is None and "-s" in args:
            directory = REPO / args[args.index("-s") + 1]
            for path in sorted(directory.rglob("*.py")):
                hashes[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    initial_tests = test_source_hashes()
    rows = []
    for name, args, relative in tasks():
        command = [sys.executable, *args]
        started = time.time()
        errors = []
        timeout_seconds = 1200 if name in {"compiler-forward-backward-cpu", "compiled-training-cpu"} else 600
        print(f"running {name}", flush=True)
        try:
            process = subprocess.run(command, cwd=REPO, capture_output=True, text=True, timeout=timeout_seconds)
            row = {"name": name, "command": command, "returncode": process.returncode,
                   "stdout": process.stdout, "stderr": process.stderr,
                   "timeout_seconds": timeout_seconds}
            artifact = None
            if relative:
                path = REPO / relative
                if not path.exists() or path.stat().st_mtime < started:
                    errors.append("artifact missing or not regenerated by this invocation")
                else:
                    artifact = json.loads(path.read_text())
                    errors.extend(check_source_hashes(artifact))
                    row["artifact"] = relative
                    row["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            unavailable = (name in {"training-benchmark-cuda", "hip-native"} and process.returncode == 2
                           and artifact is not None and artifact.get("status") == "unavailable"
                           and artifact.get("rows") == [] and artifact.get("gpu_execution_accepted") is False)
            if process.returncode != 0 and not unavailable:
                errors.append(f"command exited {process.returncode}")
            row["status"] = "failed" if errors else "unavailable" if unavailable else "passed"
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            row = {"name": name, "command": command, "status": "failed",
                   "timeout_seconds": timeout_seconds}
            errors.append(str(exc))
        row.update({"errors": errors, "elapsed_seconds": time.time() - started})
        rows.append(row)
        print(f"{name}: {row['status']}", flush=True)
    tests_unchanged = initial_tests == test_source_hashes()
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "steps": rows,
        "test_source_sha256": initial_tests, "test_sources_unchanged_during_run": tests_unchanged,
        "runner_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "status": "failed" if not tests_unchanged or any(row["status"] == "failed" for row in rows) else "checkpoint_passed",
        "full_goal_accepted": False,
        "scope": "GEMM, attention references and small training-block checkpoint; does not accept the complete advanced curriculum",
        "unavailable_steps": [row["name"] for row in rows if row["status"] == "unavailable"]}
    REPORT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], REPORT)
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
