"""Execute a baseline and targeted counter test, then compare coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from verification_platform.coverage_closure import bound_coverage_snapshot, compare_coverage


ROOT = Path(__file__).resolve().parents[1]
RTL = ROOT / "benchmarks/seeded_counter/counter.sv"
BASELINE_TB = ROOT / "benchmarks/repository_scale/counter_baseline_coverage_tb.sv"
TARGETED_TB = ROOT / "benchmarks/repository_scale/counter_targeted_coverage_tb.sv"
POINTS = ("reset", "hold", "enable", "post-enable-hold")


def execute(rtl: Path, testbench: Path, output: Path) -> tuple[str, str, int]:
    with tempfile.TemporaryDirectory(prefix="coverage-closure-") as directory:
        binary = Path(directory) / "counter.vvp"
        compiled = subprocess.run(["iverilog", "-g2012", "-o", str(binary), str(rtl), str(testbench)], capture_output=True, text=True, check=False)
        if compiled.returncode:
            return compiled.stdout, compiled.stderr, compiled.returncode
        ran = subprocess.run(["vvp", str(binary)], capture_output=True, text=True, check=False)
        return ran.stdout, ran.stderr, ran.returncode


def snapshot(stdout: str, stderr: str, evidence_name: str) -> dict:
    text = stdout + stderr
    covered = sum(f"COVERED {point}" in text for point in POINTS)
    digest = hashlib.sha256(text.encode()).hexdigest()
    return bound_coverage_snapshot(kind="functional-counter-points", covered=covered, total=len(POINTS), source_revision="seeded-counter-v1", evidence_digest=digest) | {"evidence_name": evidence_name}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/repository-scale-m2/coverage-closure")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    candidate_rtl = args.output / "candidate_counter.sv"
    candidate_rtl.write_text(RTL.read_text(encoding="utf-8").replace(
        "else\n      counter_q <= counter_q + 4'd1; // SEEDED_BUG: missing enable guard",
        "else if (enable)\n      counter_q <= counter_q + 4'd1;\n    else\n      counter_q <= counter_q;",
        1,
    ), encoding="utf-8")
    baseline_stdout, baseline_stderr, baseline_code = execute(RTL, BASELINE_TB, args.output)
    targeted_stdout, targeted_stderr, targeted_code = execute(candidate_rtl, TARGETED_TB, args.output)
    (args.output / "baseline.stdout.log").write_text(baseline_stdout, encoding="utf-8")
    (args.output / "baseline.stderr.log").write_text(baseline_stderr, encoding="utf-8")
    (args.output / "targeted.stdout.log").write_text(targeted_stdout, encoding="utf-8")
    (args.output / "targeted.stderr.log").write_text(targeted_stderr, encoding="utf-8")
    before = snapshot(baseline_stdout, baseline_stderr, "baseline.stdout.log")
    after = snapshot(targeted_stdout, targeted_stderr, "targeted.stdout.log")
    report = compare_coverage(before, after, required_source_revision="seeded-counter-v1")
    report["baseline_command_status"] = "pass" if baseline_code == 0 else "fail"
    report["targeted_command_status"] = "pass" if targeted_code == 0 else "fail"
    report["status"] = "converged" if report["status"] == "converged" and baseline_code == 0 and targeted_code == 0 else "blocked"
    report["report_sha256"] = hashlib.sha256(json.dumps({key: value for key, value in report.items() if key != "report_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (args.output / "coverage-closure-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "before": before["covered"], "after": after["covered"], "delta": report["coverage_delta"], "report": str(args.output / "coverage-closure-report.json")}, sort_keys=True))
    return 0 if report["status"] == "converged" else 1


if __name__ == "__main__":
    raise SystemExit(main())
