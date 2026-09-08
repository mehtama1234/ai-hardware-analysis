"""Bounded native HIP execution; missing compiler never becomes GPU evidence."""
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "gpu-kernels-serving-lab"))
from common.provenance import source_provenance


def validated(payload):
    def number(value):
        return type(value) in (int, float) and math.isfinite(value)
    rows = payload.get("rows", [])
    if payload.get("status") != "passed" or not isinstance(rows, list) or len(rows) != 5:
        return False
    if payload.get("warmup") != 3 or payload.get("launches_per_sample") != 100:
        return False
    if any(not isinstance(row, dict) for row in rows):
        return False
    if [r.get("n") for r in rows] != [1, 255, 256, 257, 65539]:
        return False
    for row in rows:
        error, samples = row.get("max_abs_error"), row.get("samples_ms")
        if not number(error) or not 0 <= error <= 1e-6:
            return False
        if not isinstance(samples, list) or len(samples) != 7 or not all(number(x) and x > 0 for x in samples):
            return False
    return True


def run():
    report = {"status": "unavailable", "gpu_execution_accepted": False, "rows": [],
              "scope": "native HIP vector add; five lengths, FP64 host oracle and seven event batch averages; not cross-platform performance parity",
              "provenance": source_provenance(REPO, [Path(__file__), HERE / "kernel.hip.cpp"])}
    compiler = shutil.which("hipcc")
    if compiler is None:
        report["reason"] = "hipcc not found"
        return report
    try:
        with tempfile.TemporaryDirectory(prefix="hip-vector-check-") as directory:
            binary = Path(directory) / "vector-check"
            command = [compiler, "-O2", "-std=c++17", str(HERE / "kernel.hip.cpp"), "-o", str(binary)]
            built = subprocess.run(command, capture_output=True, text=True, timeout=120)
            report["build"] = {"command": command, "returncode": built.returncode, "stdout": built.stdout, "stderr": built.stderr}
            if built.returncode:
                report.update(status="failed", reason="compilation failed")
                return report
            executed = subprocess.run([str(binary)], capture_output=True, text=True, timeout=60)
            report["execution"] = {"returncode": executed.returncode, "stdout": executed.stdout, "stderr": executed.stderr}
            payload = json.loads(executed.stdout)
            if not isinstance(payload, dict):
                raise ValueError("native payload is not an object")
            if executed.returncode == 2 and payload.get("status") == "unavailable" and payload.get("rows") == []:
                report["reason"] = "native program reports no device"
            elif executed.returncode == 0 and validated(payload):
                report.update(status="passed", gpu_execution_accepted=True, rows=payload["rows"], native=payload)
            else:
                report.update(status="failed", reason="native execution or numerical/timing contract failed")
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        report.update(status="failed", reason=str(exc))
    return report


if __name__ == "__main__":
    report = run()
    path = HERE / "native-execution.json"
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(report["status"], path)
    raise SystemExit(0 if report["status"] == "passed" else 2 if report["status"] == "unavailable" else 1)
