#!/usr/bin/env python3
"""Bridge one accepted LLM diagnosis into an explicitly approved RTL retest."""
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
from verification_platform.triage import Failure


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/llm-approved-counter-repair")
    decision = parser.add_mutually_exclusive_group()
    decision.add_argument("--approve", action="store_true", help="apply the bounded repair to a copy and retest it")
    decision.add_argument("--reject", action="store_true", help="record a human rejection without applying the repair")
    parser.add_argument("--reviewer", help="human reviewer identity required with --approve")
    parser.add_argument("--approval-note", help="human approval note required with --approve")
    args = parser.parse_args()
    args.model_report = args.model_report.resolve()
    args.output = args.output.resolve()

    model_report = load(args.model_report)
    rows = model_report.get("model_runs", {}).get("local-batch-command", [])
    row = next((item for item in rows if item.get("design_id") == "seeded_counter"), None)
    if row is None:
        raise SystemExit("model report has no seeded_counter diagnosis")
    if not (
        row.get("status") == "available"
        and row.get("grounded") is True
        and row.get("diagnosis_match") is True
        and row.get("adversarial_review", {}).get("accepted") is True
    ):
        raise SystemExit("seeded_counter model diagnosis is not accepted for review")
    model_repair = model_report.get("counter_repair_run")
    expected_before = "counter_q <= counter_q + 4'd1;"
    expected_after = "if (enable) counter_q <= counter_q + 4'd1;"
    model_repair_payload = model_repair.get("raw_output", {}) if isinstance(model_repair, dict) else {}
    if not isinstance(model_repair, dict) or model_repair.get("status") != "available" or model_repair.get("grounded") is not True or model_repair.get("repair_match") is not True or model_repair_payload.get("before") != expected_before or model_repair_payload.get("after") != expected_after:
        raise SystemExit("seeded_counter model repair is not an accepted exact bounded edit")

    source = ROOT / "benchmarks/seeded_counter/counter.sv"
    testbench = ROOT / "benchmarks/seeded_counter/tb.sv"
    triage = load(ROOT / "benchmarks/seeded_counter/runs/latest/triage-report.json")
    taxonomy = load(ROOT / "benchmarks/multi_design_pilot/fault-taxonomy.json")
    expected_source_revision = taxonomy["failure_cases"]["seeded_counter"]["source_revision"]
    divergence = triage["first_divergence"]
    failure = Failure(
        cycle=int(divergence["cycle"]),
        signal=str(divergence["signal"]),
        expected=str(divergence["expected"]),
        actual=str(divergence["actual"]),
    )
    diagnosis = row["proposal"]
    if diagnosis["source_revision"] != expected_source_revision:
        raise SystemExit("model diagnosis source revision does not match RTL triage")
    proposal = RepairProposal(
        "REQ-COUNTER-HOLD",
        "counter.sv",
        6,
        model_repair_payload["before"],
        model_repair_payload["after"],
        model_repair_payload["rationale"],
    )
    scope = {
        "simulation": {
            "tool": "iverilog-vvp",
            "source": str(source),
            "testbench": str(testbench),
            "testbench_sha256": digest(testbench),
            "pass_marker": "PASS",
        },
        "formal": {
            "tool": "yosys-sat",
            "specification_model": str(ROOT / "benchmarks/seeded_counter/formal_model_check.sv"),
            "specification_model_sha256": digest(ROOT / "benchmarks/seeded_counter/formal_model_check.sv"),
            "properties": str(ROOT / "benchmarks/seeded_counter/formal_properties.sv"),
            "properties_sha256": digest(ROOT / "benchmarks/seeded_counter/formal_properties.sv"),
            "property_count": 3,
        },
    }
    scope_sha256 = object_digest(scope)

    args.output.mkdir(parents=True, exist_ok=True)
    original_hash = digest(source)
    review = {
        "schema_version": "llm-approved-counter-repair-v2",
        "design_id": "seeded_counter",
        "model_diagnosis": diagnosis,
        "repair": {
            "requirement_id": proposal.requirement_id,
            "file": proposal.file,
            "line": proposal.line,
            "before": proposal.before,
            "after": proposal.after,
            "rationale": proposal.rationale,
            "decision": proposal.decision(human_approved=args.approve),
            "model_generated": True,
            "model_repair_sha256": model_repair["proposal"].get("proposal_sha256"),
        },
        "source": {"path": str(source), "sha256": original_hash},
        "verification_scope": {**scope, "scope_sha256": scope_sha256},
        "claim_boundary": "One seeded RTL repair/retest only; no autonomous signoff, commercial EDA equivalence, silicon correctness, or tapeout claim.",
    }

    if not args.approve and not args.reject:
        review["approval"] = {"status": "required", "reviewer": None, "note": None}
        (args.output / "repair-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "review_required", "output": str(args.output / 'repair-review.json')}))
        return 0

    if not args.reviewer or not args.approval_note:
        raise SystemExit("--approve/--reject requires --reviewer and --approval-note")
    if args.reject:
        review["approval"] = {"status": "rejected", "reviewer": args.reviewer, "note": args.approval_note, "proposal_sha256": model_repair["proposal"].get("proposal_sha256"), "source_sha256": original_hash, "scope_sha256": scope_sha256}
        (args.output / "repair-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": "rejected", "output": str(args.output / 'repair-review.json')}))
        return 0
    review["approval"] = {
        "status": "approved",
        "reviewer": args.reviewer,
        "note": args.approval_note,
        "proposal_sha256": model_repair["proposal"].get("proposal_sha256"),
        "source_sha256": original_hash,
        "scope_sha256": scope_sha256,
    }
    repaired = args.output / "counter_repaired.sv"
    apply_to_copy(source, repaired, proposal, human_approved=True)
    compile_path = args.output / "counter.vvp"
    compile_run = subprocess.run(
        ["iverilog", "-g2012", "-o", str(compile_path), str(repaired), str(testbench)],
        cwd=args.output,
        capture_output=True,
        text=True,
        check=False,
    )
    sim_run = subprocess.run(
        ["vvp", str(compile_path)],
        cwd=args.output,
        capture_output=True,
        text=True,
        check=False,
    ) if compile_run.returncode == 0 else None
    (args.output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8")
    (args.output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    if sim_run is not None:
        (args.output / "simulation.stdout.log").write_text(sim_run.stdout, encoding="utf-8")
        (args.output / "simulation.stderr.log").write_text(sim_run.stderr, encoding="utf-8")
    formal_dir = args.output / "formal"
    formal_run = subprocess.run(
        [
            sys.executable,
            "scripts/run_seeded_counter_formal.py",
            "--repaired-source",
            str(repaired),
            "--output",
            str(formal_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    (args.output / "formal.stdout.log").write_text(formal_run.stdout, encoding="utf-8")
    (args.output / "formal.stderr.log").write_text(formal_run.stderr, encoding="utf-8")
    formal_report = load(formal_dir / "formal-report.json") if (formal_dir / "formal-report.json").is_file() else {}
    passed = (
        compile_run.returncode == 0
        and sim_run is not None
        and sim_run.returncode == 0
        and "PASS" in sim_run.stdout
        and formal_run.returncode == 0
        and formal_report.get("status") == "passed"
    )
    review["retest"] = {
        "compile_returncode": compile_run.returncode,
        "simulation_returncode": sim_run.returncode if sim_run is not None else None,
        "pass_marker": bool(sim_run is not None and "PASS" in sim_run.stdout),
        "formal": {
            "status": formal_report.get("status", "failed"),
            "report": str(formal_dir / "formal-report.json"),
            "sha256": digest(formal_dir / "formal-report.json") if (formal_dir / "formal-report.json").is_file() else None,
        },
        "status": "passed" if passed else "failed",
        "repaired_sha256": digest(repaired),
        "original_unchanged": digest(source) == original_hash,
    }
    (args.output / "repair-review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if passed and review["retest"]["original_unchanged"] else "failed", "output": str(args.output)}))
    return 0 if passed and review["retest"]["original_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
