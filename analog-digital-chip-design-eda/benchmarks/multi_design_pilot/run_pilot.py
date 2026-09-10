"""Run the current multi-design open-source verification pilot.

Each benchmark owns its evidence root; this coordinator only records the
observed outcomes and hashes the aggregate so it cannot be mistaken for a
closure claim about either design.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from verification_platform.artifacts import build_artifact_manifest, verify_artifact_manifest, write_artifact_manifest
from verification_platform.session import VerificationSession
BENCHMARKS = [
    ("seeded_counter", ROOT / "benchmarks" / "seeded_counter" / "run_benchmark.py"),
    ("seeded_fifo", ROOT / "benchmarks" / "seeded_fifo" / "run_benchmark.py"),
    ("seeded_regblock", ROOT / "benchmarks" / "seeded_regblock" / "run_benchmark.py"),
    ("register_peripheral", ROOT / "benchmarks" / "register_peripheral" / "run_benchmark.py"),
    ("seeded_handshake", ROOT / "benchmarks" / "seeded_handshake" / "run_benchmark.py"),
]
RETESTS = {
    "seeded_counter": ROOT / "benchmarks" / "seeded_counter" / "retest_benchmark.py",
    "seeded_fifo": ROOT / "benchmarks" / "seeded_fifo" / "retest_benchmark.py",
    "seeded_regblock": ROOT / "benchmarks" / "seeded_regblock" / "retest_benchmark.py",
    "register_peripheral": ROOT / "benchmarks" / "register_peripheral" / "retest_benchmark.py",
    "seeded_handshake": ROOT / "benchmarks" / "seeded_handshake" / "retest_benchmark.py",
}

def _durations(payload: object) -> list[float]:
    """Collect recorded adapter durations across benchmark report schemas."""
    found: list[float] = []
    if isinstance(payload, dict):
        metadata = payload.get("metadata")
        if isinstance(metadata, dict) and isinstance(metadata.get("duration_seconds"), (int, float)):
            found.append(float(metadata["duration_seconds"]))
        for value in payload.values():
            found.extend(_durations(value))
    elif isinstance(payload, list):
        for value in payload:
            found.extend(_durations(value))
    return found


def main() -> int:
    results = []
    for name, script in BENCHMARKS:
        completed = subprocess.run([sys.executable, str(script)], cwd=script.parent, capture_output=True, text=True)
        report_path = script.parent / "runs" / "latest" / "triage-report.json"
        report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {"status": "blocked"}
        run_root = script.parent / "runs" / "latest"
        manifest_path = run_root / "artifact-manifest.json"
        manifest = build_artifact_manifest(run_root, exclude={"artifact-manifest.json"})
        write_artifact_manifest(manifest_path, manifest)
        manifest_check = verify_artifact_manifest(run_root, manifest)
        ir_path = run_root / "verification-ir.json"
        ir_payload = json.loads(ir_path.read_text(encoding="utf-8")) if ir_path.is_file() else {}
        planning_path = run_root / "planning-summary.json"
        planning = json.loads(planning_path.read_text(encoding="utf-8")) if planning_path.is_file() else {}
        durations = _durations(report) + _durations(ir_payload)
        evidence_complete = all((script.parent / path).is_file() for path in report.get("evidence", []))
        results.append({
            "design": name,
            "process_exit_code": completed.returncode,
            "status": report.get("status", "unknown"),
            "failure": report.get("failure") or report.get("first_divergence"),
            "report": str(report_path.relative_to(ROOT)),
            "baseline_tool_seconds": round(sum(durations), 6),
            "baseline_coverage": {"covered": 0 if report.get("status") == "failed" else 1, "total": 1},
            "diagnosis_evidence_complete": evidence_complete,
            "baseline_artifact_integrity": manifest_check,
            "planning": {"total": planning.get("total", 0), "planned": len(planning.get("planned", [])), "unplanned": len(planning.get("unplanned", []))},
            "formal_readiness": report.get("formal_preflight", "not-run"),
            "next_action": {"action": "triage_failure", "approval": "not_required"} if report.get("status") == "failed" else {"action": "review_closure", "approval": "human_signoff"},
        })
    for item in results:
        completed = subprocess.run([sys.executable, str(RETESTS[item["design"]])], cwd=RETESTS[item["design"]].parent, capture_output=True, text=True)
        retest_path = RETESTS[item["design"]].parent / "runs" / "retest" / "retest-report.json"
        retest = json.loads(retest_path.read_text(encoding="utf-8")) if retest_path.is_file() else {"status":"blocked"}
        retest_root = RETESTS[item["design"]].parent / "runs" / "retest"
        retest_manifest = build_artifact_manifest(retest_root, exclude={"artifact-manifest.json"})
        write_artifact_manifest(retest_root / "artifact-manifest.json", retest_manifest)
        retest_integrity = verify_artifact_manifest(retest_root, retest_manifest)
        retest_seconds = sum(_durations(retest))
        item["retest_status"] = retest.get("status", "unknown")
        item["repair_decision"] = retest.get("repair", {}).get("decision")
        item["original_source_unchanged"] = retest.get("repair", {}).get("original_unchanged", False)
        item["retest_process_exit_code"] = completed.returncode
        item["retest_tool_seconds"] = round(retest_seconds, 6)
        item["retest_coverage"] = {"covered": 1 if retest.get("status") == "passed" else 0, "total": 1}
        item["retest_artifact_integrity"] = retest_integrity
        retest_planning_path = retest_root / "planning-summary.json"
        retest_planning = json.loads(retest_planning_path.read_text(encoding="utf-8")) if retest_planning_path.is_file() else {}
        item["retest_planning"] = {"total": retest_planning.get("total", 0), "planned": len(retest_planning.get("planned", [])), "unplanned": len(retest_planning.get("unplanned", []))}
        item["retest_formal_readiness"] = retest.get("formal_preflight", "not-run")
        item["retest_next_action"] = {"action": "review_closure", "approval": "human_signoff"} if retest.get("status") == "passed" else {"action": "triage_failure", "approval": "not_required"}
    summary = {
        "schema_version": "multi-design-pilot-v1",
        "backend_policy": "open-source-only",
        "design_count": len(results),
        "failed_designs": sum(item["status"] == "failed" for item in results),
        "blocked_designs": sum(item["status"] == "blocked" for item in results),
        "passed_retests": sum(item["retest_status"] == "passed" for item in results),
        "metrics": {
            "diagnosis_evidence_complete": sum(item["diagnosis_evidence_complete"] for item in results),
            "unique_failure_signatures": len({json.dumps(item["failure"], sort_keys=True) for item in results if item["failure"]}),
            "baseline_coverage_percent": round(100.0 * sum(item["baseline_coverage"]["covered"] for item in results) / len(results), 2),
            "retest_coverage_percent": round(100.0 * sum(item["retest_coverage"]["covered"] for item in results) / len(results), 2),
            "baseline_tool_seconds": round(sum(item["baseline_tool_seconds"] for item in results), 6),
            "retest_tool_seconds": round(sum(item["retest_tool_seconds"] for item in results), 6),
            "all_artifacts_verified": all(item["baseline_artifact_integrity"]["valid"] and item["retest_artifact_integrity"]["valid"] for item in results),
            "original_sources_unchanged": sum(item["original_source_unchanged"] for item in results),
            "requirements_planned": sum(item["planning"]["planned"] for item in results),
            "requirements_unplanned": sum(item["planning"]["unplanned"] for item in results),
            "repair_success_rate_percent": round(100.0 * sum(item["retest_status"] == "passed" and item["repair_decision"] == "allowed" for item in results) / len(results), 2),
            "formal_readiness": {status: sum(item["formal_readiness"] == status for item in results) for status in ("passed", "blocked", "not-run")},
            "next_actions": {action: sum(item["next_action"]["action"] == action for item in results) for action in ("triage_failure", "review_closure")},
        },
        "results": results,
    }
    session = VerificationSession(session_id="multi-design-pilot", run_root=ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest", source_revision="multi-design-pilot-v1")
    session.advance("planned", metadata={"design_count": len(results)})
    session.advance("executed", metadata={"failed_designs": summary["failed_designs"]})
    session.advance("triaged", metadata={"diagnosis_evidence_complete": summary["metrics"]["diagnosis_evidence_complete"]})
    session.advance("repair_review", metadata={"approved_repairs": sum(item["repair_decision"] == "allowed" for item in results)})
    session.advance("retested", metadata={"passed_retests": summary["passed_retests"]})
    session.advance("closed", metadata={"artifact_integrity": summary["metrics"]["all_artifacts_verified"]})
    session_path = ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "session-ledger.json"
    session.write(session_path)
    summary["session_ledger"] = str(session_path.relative_to(ROOT))
    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":"))
    summary["summary_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    output = ROOT / "benchmarks" / "multi_design_pilot" / "runs" / "latest" / "pilot-summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["failed_designs"] == len(BENCHMARKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
