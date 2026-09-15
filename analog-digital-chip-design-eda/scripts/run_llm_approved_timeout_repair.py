#!/usr/bin/env python3
"""Apply the accepted temporal repair to a disposable timeout copy."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from verification_platform.repair import RepairProposal, apply_to_copy
from verification_platform.simulation import run_iverilog_vvp


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    decision = parser.add_mutually_exclusive_group()
    decision.add_argument("--approve", action="store_true")
    decision.add_argument("--reject", action="store_true")
    parser.add_argument("--reviewer")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    model_path = args.model_report.resolve()
    output = args.output.resolve()
    model = json.loads(model_path.read_text(encoding="utf-8"))
    model_repair = model.get("timeout_repair_run") or {}
    payload = model_repair.get("raw_output") or {}
    if model_repair.get("status") != "available" or model_repair.get("grounded") is not True or model_repair.get("repair_match") is not True or payload.get("edit_operator") != "lower_timeout_threshold":
        raise SystemExit("seeded_timeout model repair is not an accepted bounded operator")
    source = ROOT / "benchmarks/seeded_timeout/timeout.sv"
    testbench = ROOT / "benchmarks/seeded_timeout/tb.sv"
    proposal = RepairProposal("REQ-TIMEOUT-BOUNDARY", "timeout.sv", 10, "  assign timed_out = count >= 3'd4;", "  assign timed_out = count >= 3'd3;", payload["rationale"])
    output.mkdir(parents=True, exist_ok=True)
    original_hash = digest(source)
    scope = {
        "simulation": {"tool": "iverilog-vvp", "source": str(source), "testbench": str(testbench), "testbench_sha256": digest(testbench)},
        "formal": {
            "tool": "yosys-sat",
            "specification_model": str(ROOT / "benchmarks/seeded_timeout/formal_model_check.sv"),
            "specification_model_sha256": digest(ROOT / "benchmarks/seeded_timeout/formal_model_check.sv"),
            "properties": str(ROOT / "benchmarks/seeded_timeout/formal_properties.sv"),
            "properties_sha256": digest(ROOT / "benchmarks/seeded_timeout/formal_properties.sv"),
            "property_count": 4,
        },
    }
    scope_sha256 = object_digest(scope)
    report = {"schema_version": "llm-approved-timeout-repair-v1", "design_id": "seeded_timeout", "model_report": {"path": str(model_path), "sha256": digest(model_path)}, "model_repair": {"operator": payload["edit_operator"], "proposal": model_repair.get("proposal")}, "repair": {"requirement_id": proposal.requirement_id, "file": proposal.file, "line": proposal.line, "before": proposal.before, "after": proposal.after, "rationale": proposal.rationale, "decision": proposal.decision(human_approved=args.approve), "model_generated": True}, "source": {"path": str(source), "sha256": original_hash}, "verification_scope": {**scope, "scope_sha256": scope_sha256}}
    if not args.approve and not args.reject:
        report["approval"] = {"status": "required", "reviewer": None, "note": None}
        (output / "repair-review.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "review_required", "output": str(output)}))
        return 0
    if not args.reviewer or not args.approval_note:
        raise SystemExit("--approve/--reject requires --reviewer and --approval-note")
    if args.reject:
        report["approval"] = {"status": "rejected", "reviewer": args.reviewer, "note": args.approval_note, "proposal_sha256": model_repair.get("proposal", {}).get("proposal_sha256"), "source_sha256": original_hash, "scope_sha256": scope_sha256}
        (output / "repair-review.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "rejected", "output": str(output)}, sort_keys=True))
        return 0
    report["approval"] = {"status": "approved", "reviewer": args.reviewer, "note": args.approval_note, "proposal_sha256": model_repair.get("proposal", {}).get("proposal_sha256"), "source_sha256": original_hash, "scope_sha256": scope_sha256}
    repaired = output / "timeout_repaired.sv"
    apply_to_copy(source, repaired, proposal, human_approved=True)
    compile_run, simulation_run = run_iverilog_vvp(repaired, testbench, run_root=output, source_revision="seeded-timeout-v1-model-repair", binary_name="timeout.vvp", tool_prefix="timeout-model-repair")
    formal_dir = output / "formal"
    formal_run = subprocess.run([sys.executable, "scripts/run_seeded_timeout_formal.py", "--repaired-source", str(repaired), "--output", str(formal_dir)], cwd=ROOT, capture_output=True, text=True, check=False)
    (output / "formal.stdout.log").write_text(formal_run.stdout, encoding="utf-8")
    (output / "formal.stderr.log").write_text(formal_run.stderr, encoding="utf-8")
    formal_report = json.loads((formal_dir / "formal-report.json").read_text(encoding="utf-8")) if (formal_dir / "formal-report.json").is_file() else {}
    passed = simulation_run is not None and simulation_run.status == "passed" and formal_run.returncode == 0 and formal_report.get("status") == "passed"
    report["retest"] = {"status": "passed" if passed else "failed", "compile": compile_run.__dict__, "simulation": simulation_run.__dict__ if simulation_run else None, "formal": {"status": formal_report.get("status", "failed"), "report": str(formal_dir / "formal-report.json"), "sha256": digest(formal_dir / "formal-report.json") if (formal_dir / "formal-report.json").is_file() else None}, "repaired_sha256": digest(repaired), "original_unchanged": digest(source) == original_hash}
    (output / "repair-review.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["retest"]["status"], "output": str(output), "original_unchanged": report["retest"]["original_unchanged"]}, sort_keys=True))
    return 0 if passed and report["retest"]["original_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
