"""Run the baseline failure and approved retest as one reproducible workflow."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from verification_platform.waveform import compare_traces
from verification_platform.formal import counterexample_to_failure, yosys_sat_prove
from verification_platform.artifacts import build_artifact_manifest, verify_artifact_manifest, write_artifact_manifest


def main() -> int:
    baseline = subprocess.run([sys.executable, str(ROOT / "run_benchmark.py")], capture_output=True, text=True, check=False)
    retest = subprocess.run([sys.executable, str(ROOT / "retest_benchmark.py")], capture_output=True, text=True, check=False)
    formal_run = yosys_sat_prove(ROOT / "formal_constant.sv", top="formal_constant", signal="q", expected_value="0", run_root=ROOT / "runs" / "formal", sequence=2, source_revision="formal-constant-v1")
    formal_failure_run = yosys_sat_prove(ROOT / "formal_bad.sv", top="formal_bad", signal="q", expected_value="0", run_root=ROOT / "runs" / "formal-counterexample", sequence=2, source_revision="formal-bad-v1")
    formal_failure_log = (ROOT / "runs" / "formal-counterexample" / "stdout.log").read_text(encoding="utf-8")
    formal_failure = counterexample_to_failure(formal_failure_log, signal="q", expected_value="0")
    baseline_closure = json.loads((ROOT / "runs/latest/closure-report.json").read_text(encoding="utf-8"))
    retest_closure = json.loads((ROOT / "runs/retest/closure-report.json").read_text(encoding="utf-8"))
    baseline_coverage = json.loads((ROOT / "runs/latest/functional-coverage.json").read_text(encoding="utf-8"))
    retest_coverage = json.loads((ROOT / "runs/retest/functional-coverage.json").read_text(encoding="utf-8"))
    artifact_manifest_path = ROOT / "runs" / "artifact-manifest.json"
    artifact_manifest = build_artifact_manifest(ROOT / "runs", exclude={"artifact-manifest.json"})
    write_artifact_manifest(artifact_manifest_path, artifact_manifest)
    artifact_integrity = verify_artifact_manifest(ROOT / "runs", artifact_manifest)
    baseline_report = json.loads((ROOT / "runs/latest/triage-report.json").read_text(encoding="utf-8"))
    retest_report = json.loads((ROOT / "runs/retest/retest-report.json").read_text(encoding="utf-8"))
    summary = {
        "schema_version": "seeded-counter-end-to-end-v1",
        "baseline": {"process_exit": baseline.returncode, "verification_status": baseline_report["status"], "report": "runs/latest/triage-report.json"},
        "retest": {"process_exit": retest.returncode, "verification_status": retest_report["status"], "report": "runs/retest/retest-report.json", "closure": "runs/retest/closure-report.json", "session": "runs/retest/session-ledger.json"},
        "expected_baseline": "failed",
        "expected_retest": "passed",
        "trace_comparison": compare_traces(ROOT / "runs/latest/waveform.vcd", ROOT / "runs/retest/simulation/waveform.vcd", "counter_q"),
        "formal": {"tool": formal_run.tool, "execution_status": formal_run.status, "proof_result": formal_run.metadata.get("proof_result"), "ledger": "runs/formal/provenance-ledger.json"},
        "formal_counterexample": {"tool": formal_failure_run.tool, "proof_result": formal_failure_run.metadata.get("proof_result"), "failure": {"cycle": formal_failure.cycle, "signal": formal_failure.signal, "expected": formal_failure.expected, "actual": formal_failure.actual} if formal_failure else None, "ledger": "runs/formal-counterexample/provenance-ledger.json"},
        "artifact_manifest": "runs/artifact-manifest.json",
        "artifact_integrity": artifact_integrity,
        "pov_metrics": {"baseline_proven": sum(item.get("status") == "proven" for item in baseline_closure), "retest_proven": sum(item.get("status") == "proven" for item in retest_closure), "proven_delta": sum(item.get("status") == "proven" for item in retest_closure) - sum(item.get("status") == "proven" for item in baseline_closure), "baseline_coverage_percentage": round(100.0 * baseline_coverage["covered"] / baseline_coverage["total"], 4), "retest_coverage_percentage": round(100.0 * retest_coverage["covered"] / retest_coverage["total"], 4)},
    }
    summary["summary_sha256"] = hashlib.sha256(json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ROOT / "runs" / "end-to-end-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if baseline_report["status"] == "failed" and retest_report["status"] == "passed" and formal_run.metadata.get("proof_result") == "proven" and formal_failure_run.metadata.get("proof_result") == "counterexample" and formal_failure is not None and artifact_integrity["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
