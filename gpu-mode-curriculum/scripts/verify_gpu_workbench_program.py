#!/usr/bin/env python3
"""Verify the programmable GPU workbench CLI/API layer."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run_json(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/gpu_workbench.py", *args, "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"command failed: {args}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return json.loads(proc.stdout)


def run_program_json(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/gpu_workbench_programs.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"program command failed: {args}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return json.loads(proc.stdout)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_diagnosis() -> dict[str, Any]:
    result = run_json(["kv cache decode latency"])
    require(result["matched_bottleneck_class"] in {"attention-serving", "serving-scheduler", "memory-bandwidth"}, "unexpected KV-cache diagnosis")
    require(result.get("lessons"), "diagnosis returned no GPUMODE lessons")
    require(result.get("labs"), "diagnosis returned no labs")
    require(result.get("tutorial_sources"), "diagnosis returned no tutorial sources")
    require(result.get("papers"), "diagnosis returned no paper cross-checks")
    require(result.get("measurements"), "diagnosis returned no measurements")
    require(result.get("exercise_path", {}).get("lab", {}).get("command"), "diagnosis returned no runnable lab command")
    require(result.get("graph", {}).get("node_count", 0) >= 100, "graph context is missing or too small")
    require(result.get("corpus", {}).get("coverage", {}).get("link_count", 0) >= 300, "corpus bridge coverage is missing or too small")
    return result


def verify_runtime_doctor() -> dict[str, Any]:
    doctor = run_json(["--doctor"])
    for key in ("nvidia_smi", "nvcc", "ncu", "nsys", "hipcc"):
        require(key in doctor.get("tools", {}), f"runtime doctor missing tool {key}")
    for key in ("torch", "triton", "vllm", "jax"):
        require(key in doctor.get("python_modules", {}), f"runtime doctor missing Python module {key}")
    for key in ("cuda_source", "triton", "vllm", "rocm_hip", "jax", "cpu_proxy"):
        require(key in doctor.get("lab_runtime_groups", {}), f"runtime doctor missing lab group {key}")
    return doctor


def verify_tutorial() -> dict[str, Any]:
    result = run_json(["tensor core quantization", "--tutorial"])
    tutorial = result.get("tutorial_file", {})
    require(tutorial.get("status") == "written", "tutorial generation did not report written status")
    path = ROOT / tutorial.get("path", "")
    require(path.exists(), f"tutorial file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    for section in ("## Diagnosis", "## Read First", "## Run The Lab", "## Success Checks", "## Research Cross-Checks"):
        require(section in text, f"tutorial missing section {section}")
    return tutorial


def verify_lab_dry_run() -> dict[str, Any]:
    result = run_json(["nccl all reduce bandwidth", "--run-lab", "--dry-run"])
    run = result.get("lab_run", {})
    require(run.get("status") == "dry-run", "lab dry-run did not stay in dry-run mode")
    require("26-gpumode-distributed-communication" in run.get("lab_dir", ""), "dry-run chose the wrong distributed lab")
    require(any(command.endswith("run.py") for command in run.get("commands", [])), "dry-run missing run.py command")
    require(any(command.endswith("build_page.py") for command in run.get("commands", [])), "dry-run missing build_page.py command")
    return run


def verify_example_programs() -> dict[str, Any]:
    batch = run_program_json(["batch-triage"])
    require(batch.get("status") == "written", "batch triage did not write output")
    batch_path = ROOT / batch.get("path", "")
    require(batch_path.exists(), f"batch triage output missing: {batch_path}")
    require(batch.get("query_count", 0) >= 5, "batch triage should cover the default representative query set")
    require(
        {"attention-serving", "triton-autotune", "tensor-core-cutlass", "distributed-communication"}.issubset(
            {row.get("profile") for row in batch.get("rows", [])}
        ),
        "batch triage did not cover the expected programming tracks",
    )

    roadmap = run_program_json(["roadmap", "triton fused softmax"])
    require(roadmap.get("status") == "written", "roadmap did not write output")
    roadmap_path = ROOT / roadmap.get("path", "")
    require(roadmap_path.exists(), f"roadmap output missing: {roadmap_path}")
    roadmap_text = roadmap_path.read_text(encoding="utf-8")
    for section in ("## Phase 1: Source Model", "## Phase 3: Program And Run", "## Phase 4: Evidence"):
        require(section in roadmap_text, f"roadmap missing section {section}")

    report = run_program_json(["evidence-report", "nsight roofline dram counters"])
    require(report.get("status") == "written", "evidence report did not write output")
    report_path = ROOT / report.get("path", "")
    require(report_path.exists(), f"evidence report output missing: {report_path}")
    report_data = json.loads(report_path.read_text(encoding="utf-8"))
    require(report_data.get("recommended_lab", {}).get("path"), "evidence report missing recommended lab")
    require(report_data.get("latest_measurement_matches"), "evidence report missing measurement matches")
    return {
        "batch": batch.get("path", ""),
        "roadmap": roadmap.get("path", ""),
        "report": report.get("path", ""),
    }


def main() -> int:
    facts = {
        "diagnosis": verify_diagnosis()["matched_bottleneck_class"],
        "doctor_groups": sorted(verify_runtime_doctor()["lab_runtime_groups"]),
        "tutorial": verify_tutorial()["path"],
        "lab_dry_run": verify_lab_dry_run()["lab_dir"],
        "example_programs": verify_example_programs(),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPU workbench programming layer verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
