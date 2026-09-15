#!/usr/bin/env python3
"""Bridge the accepted model proposal into an approved register RTL retest."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--reviewer")
    parser.add_argument("--approval-note")
    args = parser.parse_args()
    report = json.loads(args.model_report.read_text(encoding="utf-8"))
    model = report.get("register_repair_run") or {}
    raw = model.get("raw_output") or {}
    before = "else if (wr_en) control <= wdata;"
    after = "else if (wr_en && addr == 2'd0) control <= wdata;"
    if model.get("status") != "available" or model.get("grounded") is not True or model.get("repair_match") is not True or raw.get("before") != before or raw.get("after") != after or model.get("adversarial_review", {}).get("accepted") is not True:
        raise SystemExit("register_peripheral model repair is not an accepted exact bounded edit")
    source = ROOT / "benchmarks/register_peripheral/csr_regs.sv"
    args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    original_hash = digest(source)
    review = {"schema_version": "llm-approved-register-repair-v1", "design_id": "register_peripheral", "model_repair": {"before": before, "after": after, "proposal_sha256": model.get("proposal", {}).get("proposal_sha256")}, "repair": {"requirement_id": "REQ-CSR-ADDRESS", "before": before, "after": after, "rationale": raw.get("rationale", "gate CSR writes on address zero"), "decision": "allowed" if args.approve else "review_required", "model_generated": True}, "source": {"path": str(source), "sha256": original_hash}, "claim_boundary": "One hierarchical register routing repair/retest only; not silicon signoff."}
    if not args.approve:
        review["approval"] = {"status": "required", "reviewer": None, "note": None}
        (args.output / "repair-review.json").write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "review_required", "output": str(args.output / "repair-review.json")})); return 0
    if not args.reviewer or not args.approval_note:
        raise SystemExit("--approve requires --reviewer and --approval-note")
    review["approval"] = {"status": "approved", "reviewer": args.reviewer, "note": args.approval_note}
    repaired = args.output / "csr_regs_repaired.sv"
    original_text = source.read_text(encoding="utf-8")
    actual_before = before + " // SEEDED_BUG: decode addr zero before write"
    actual_after = after + " // SEEDED_BUG: decode addr zero before write"
    if original_text.count(actual_before) != 1:
        raise SystemExit("canonical register source does not contain the expected seeded edit")
    repaired.write_text(original_text.replace(actual_before, actual_after), encoding="utf-8")
    compile_path = args.output / "peripheral.vvp"
    compile_run = subprocess.run(["iverilog", "-g2012", "-o", str(compile_path), str(repaired), str(ROOT / "benchmarks/register_peripheral/peripheral.sv"), str(ROOT / "benchmarks/register_peripheral/tb.sv")], cwd=args.output, capture_output=True, text=True, check=False)
    sim_run = subprocess.run(["vvp", str(compile_path)], cwd=args.output, capture_output=True, text=True, check=False) if compile_run.returncode == 0 else None
    (args.output / "compile.stdout.log").write_text(compile_run.stdout, encoding="utf-8"); (args.output / "compile.stderr.log").write_text(compile_run.stderr, encoding="utf-8")
    if sim_run is not None:
        (args.output / "simulation.stdout.log").write_text(sim_run.stdout, encoding="utf-8"); (args.output / "simulation.stderr.log").write_text(sim_run.stderr, encoding="utf-8")
    passed = compile_run.returncode == 0 and sim_run is not None and sim_run.returncode == 0 and "PASS" in sim_run.stdout
    review["retest"] = {"status": "passed" if passed else "failed", "compile_returncode": compile_run.returncode, "simulation_returncode": sim_run.returncode if sim_run else None, "pass_marker": bool(sim_run and "PASS" in sim_run.stdout), "repaired_sha256": digest(repaired), "original_unchanged": digest(source) == original_hash}
    (args.output / "repair-review.json").write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if passed and review["retest"]["original_unchanged"] else "failed", "output": str(args.output)})); return 0 if passed and review["retest"]["original_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
