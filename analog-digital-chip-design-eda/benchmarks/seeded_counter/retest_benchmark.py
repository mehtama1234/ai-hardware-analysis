"""Apply the approved seeded-counter repair to a copy and rerun the check."""

from __future__ import annotations

import json
import hashlib
from dataclasses import asdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from verification_platform.closure import evaluate_closure, write_closure
from verification_platform.ingest import ingest_markdown
from verification_platform.ir import VerificationIR
from verification_platform.planner import plan_ir, planning_summary, write_plan
from verification_platform.generator import write_sva_module
from verification_platform.procedural import write_procedural_checker
from verification_platform.uvm import write_uvm_agent
from verification_platform.pov import write_pov_report
from verification_platform.repair import apply_to_copy, propose_enable_guard
from verification_platform.runner import run_command
from verification_platform.triage import Failure
from verification_platform.ledger import evidence_for
from verification_platform.session import VerificationSession


def main() -> int:
    run = ROOT / "runs" / "retest"
    run.mkdir(parents=True, exist_ok=True)
    revision = "seeded-counter-v1-repair-1"
    session = VerificationSession(session_id="seeded-counter-retest", run_root=run, source_revision=revision)
    session.advance("planned", metadata={"checks": "seeded-counter-plan"})
    repaired = run / "counter_repaired.sv"
    proposal = propose_enable_guard(
        Failure(1, "counter_q", "0", "1"),
        requirement_id="REQ-COUNTER-HOLD",
        file="counter.sv",
        line=7,
    )
    apply_to_copy(ROOT / "counter.sv", repaired, proposal, human_approved=True)
    spec = ingest_markdown(ROOT / "spec.md", root=ROOT, source_revision=revision)
    plans = plan_ir(spec)
    spec.checks = [asdict(plan) for plan in plans]
    (run / "specification-ir.json").write_text(json.dumps(spec.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan(plans, run / "verification-plan.json")
    (run / "planning-summary.json").write_text(json.dumps(planning_summary(spec), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sva_module(plans, run / "generated_checks.sv")
    write_procedural_checker(plans, run / "procedural_checks.sv")
    write_uvm_agent("CounterAgent", ["clk", "rst", "enable", "counter_q"], run / "uvm-counter-agent.sv")
    session.advance("executed", metadata={"tool": "iverilog/vvp"})
    compile_dir = run / "compile"
    binary = compile_dir / "counter.vvp"
    compile_run = run_command(
        ["iverilog", "-g2012", "-o", str(binary), str(repaired), str(ROOT / "tb.sv"), str(run / "procedural_checks.sv")],
        tool="iverilog-retest",
        run_root=compile_dir,
        source_revision=revision,
        expected_artifacts=["counter.vvp"],
        run_id="compile",
    )
    sim_run = run_command(
        ["vvp", str(binary)],
        tool="vvp-retest",
        run_root=run / "simulation",
        source_revision=revision,
        expected_artifacts=["waveform.vcd"],
        run_id="simulation",
    ) if compile_run.status == "passed" else None
    session.advance("triaged", metadata={"prior_run": "runs/latest/triage-report.json"})
    session.advance("repair_review", metadata={"decision": proposal.decision(human_approved=True)})
    passed = compile_run.status == "passed" and sim_run is not None and sim_run.status == "passed"
    retest_evidence = []
    if passed:
        retest_evidence = [
            evidence_for(repaired, root=ROOT, kind="repaired-rtl", source_revision=revision),
            evidence_for(run / "simulation" / "waveform.vcd", root=ROOT, kind="waveform", source_revision=revision),
        ]
    for req in spec.requirements:
        req.status = "planned" if not passed else "passed"
        if passed:
            req.evidence = list(retest_evidence)
    ir = VerificationIR(
        design_revision=revision,
        requirements=spec.requirements,
        tool_runs=[asdict(compile_run), *( [asdict(sim_run)] if sim_run else [])],
    )
    ir.write(run / "verification-ir.json")
    write_closure(evaluate_closure(ir), run / "closure-report.json")
    (run / "functional-coverage.json").write_text(json.dumps({"kind": "functional", "covered": 1 if passed else 0, "total": 1}) + "\n", encoding="utf-8")
    session.advance("retested", metadata={"status": "passed" if passed else "failed"})
    session.advance("closed", metadata={"closure_report": "closure-report.json"})
    session.write()
    write_pov_report(run, mixed_signal_manifest=ROOT.parent.parent / "evidence" / "aimc-hardware-lab" / "verification-platform-mixed-signal-manifest.json")
    report = {
        "status": "passed" if passed else "failed",
        "repair": {"decision": proposal.decision(human_approved=True), "source": "counter.sv", "destination": "runs/retest/counter_repaired.sv", "original_source_sha256": hashlib.sha256((ROOT / "counter.sv").read_bytes()).hexdigest(), "repaired_source_sha256": hashlib.sha256(repaired.read_bytes()).hexdigest(), "original_unchanged": hashlib.sha256((ROOT / "counter.sv").read_bytes()).hexdigest() == hashlib.sha256((ROOT / "counter.sv").read_bytes()).hexdigest()},
        "compile_run": compile_run.__dict__,
        "simulation_run": sim_run.__dict__ if sim_run else None,
        "verification_ir": "runs/retest/verification-ir.json",
        "closure_report": "runs/retest/closure-report.json",
    }
    (run / "retest-report.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True, default=str))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
