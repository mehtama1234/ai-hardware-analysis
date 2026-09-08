#!/usr/bin/env python3
"""Compile the WMMA probe and inspect emitted SASS/profiler availability."""

from __future__ import annotations

import hashlib
import csv
import io
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "native_wmma_runner.cu"
OUT = HERE / "profiler-evidence.json"


def main() -> int:
    nvcc, cuobjdump, ncu = (shutil.which(name) for name in ("nvcc", "cuobjdump", "ncu"))
    report = {
        "project": "tensor-core-gemm",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {"native_wmma_runner.cu": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                           "profile_native.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "tool_availability": {"nvcc": bool(nvcc), "cuobjdump": bool(cuobjdump), "ncu": bool(ncu)},
        "status": "unavailable",
        "sass": {"status": "unavailable", "tensor_core_instruction_seen": False},
        "nsight_compute": {"status": "unavailable"},
    }
    if not nvcc:
        report["reason"] = "nvcc not found on PATH"
        OUT.write_text(json.dumps(report, indent=2) + "\n")
        return 2
    with tempfile.TemporaryDirectory(prefix="wmma-profile-") as build:
        binary = Path(build) / "native_wmma_runner"
        command = [nvcc, "-O3", "-lineinfo", "-std=c++17", "-arch=sm_75", str(SOURCE), "-lcublas", "-o", str(binary)]
        compiled = subprocess.run(command, cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
        report["compile"] = {"status": "passed" if compiled.returncode == 0 else "failed", "command": command,
                              "stderr_tail": compiled.stderr[-4000:], "stdout_tail": compiled.stdout[-2000:]}
        if compiled.returncode:
            report["status"] = "compile-failed"
        elif not cuobjdump:
            report["sass"] = {"status": "unavailable", "reason": "cuobjdump not found on PATH", "tensor_core_instruction_seen": False}
        else:
            sass = subprocess.run([cuobjdump, "--dump-sass", str(binary)], cwd=HERE, capture_output=True, text=True, timeout=120, check=False)
            tensor_lines = [line.strip() for line in sass.stdout.splitlines() if re.search(r"(?:HMMA|MMA\.SYNC|WGMMA)", line, re.IGNORECASE)]
            report["sass"] = {"status": "measured" if sass.returncode == 0 else "failed", "returncode": sass.returncode,
                               "tensor_core_instruction_seen": bool(tensor_lines), "instruction_line_count": len(tensor_lines),
                               "instruction_lines": tensor_lines[:32], "stdout_sha256": hashlib.sha256(sass.stdout.encode()).hexdigest(),
                               "stderr_tail": sass.stderr[-2000:]}
            if ncu:
                ncu_result = subprocess.run([ncu, "--version"], cwd=HERE, capture_output=True, text=True, timeout=30, check=False)
                ncu_command = [ncu, "--target-processes", "all", "--csv", "--page", "raw",
                               "--metrics", "sm__inst_executed_pipe_tensor.sum", str(binary)]
                try:
                    measured = subprocess.run(ncu_command, cwd=HERE, capture_output=True, text=True, timeout=180, check=False)
                    report["nsight_compute"] = {
                        "status": "measured" if measured.returncode == 0 else "failed",
                        "version": (ncu_result.stdout or ncu_result.stderr).strip()[-1000:],
                        "command": ncu_command,
                        "returncode": measured.returncode,
                        "metric": "sm__inst_executed_pipe_tensor.sum",
                        "stdout_tail": measured.stdout[-12000:],
                        "stderr_tail": measured.stderr[-4000:],
                    }
                    rows = list(csv.reader(io.StringIO(measured.stdout)))
                    metric_row = next((row for row in rows if "sm__inst_executed_pipe_tensor.sum" in row), None)
                    if metric_row is not None:
                        metric_index = metric_row.index("sm__inst_executed_pipe_tensor.sum")
                        trailing = metric_row[metric_index + 1:]
                        numeric_values = []
                        metric_row_index = rows.index(metric_row)
                        for candidate in rows[metric_row_index + 1:]:
                            if metric_index < len(candidate):
                                try:
                                    float(candidate[metric_index])
                                    numeric_values.append(candidate[metric_index])
                                except ValueError:
                                    pass
                        report["nsight_compute"].update({
                            "metric_header_found": True,
                            "metric_unit": trailing[0] if trailing else "",
                            "metric_value": numeric_values[0] if numeric_values else (trailing[1] if len(trailing) > 1 else ""),
                        })
                        kernel_rows = [row for row in rows if any("wmma_gemm" in cell for cell in row)]
                        report["nsight_compute"]["wmma_kernel_rows"] = [row[:24] for row in kernel_rows[:8]]
                        report["nsight_compute"]["wmma_metric_values"] = [
                            row[metric_index] for row in kernel_rows if metric_index < len(row)
                        ]
                        if report["nsight_compute"]["wmma_metric_values"]:
                            report["nsight_compute"]["metric_value"] = report["nsight_compute"]["wmma_metric_values"][0]
                            report["nsight_compute"]["metric_unit"] = "tensor-pipe-instruction-count"
                    else:
                        report["nsight_compute"]["metric_header_found"] = False
                except subprocess.TimeoutExpired as exc:
                    report["nsight_compute"] = {"status": "timeout", "version": (ncu_result.stdout or ncu_result.stderr).strip()[-1000:], "command": ncu_command, "error": str(exc)}
            else:
                report["nsight_compute"] = {"status": "unavailable", "reason": "ncu not found on PATH"}
            report["status"] = "passed" if sass.returncode == 0 and bool(tensor_lines) else "sass-check-failed"
    report["gpu_execution_accepted"] = report["status"] == "passed"
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "gpu_execution_accepted": report["gpu_execution_accepted"],
                      "tensor_core_instruction_seen": report["sass"].get("tensor_core_instruction_seen", False),
                      "ncu": report["nsight_compute"]["status"]}, indent=2))
    return 0 if report["gpu_execution_accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
