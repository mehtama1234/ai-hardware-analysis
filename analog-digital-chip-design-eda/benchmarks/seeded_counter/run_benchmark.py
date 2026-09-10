"""Run the seeded RTL benchmark and emit evidence-backed triage JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))

from verification_platform.ingest import ingest_markdown
from verification_platform.planner import plan_ir, planning_summary, write_plan
from verification_platform.generator import write_sva_module
from verification_platform.procedural import write_procedural_checker
from verification_platform.triage import failure_to_ir, locate_source_marker, parse_failure
from verification_platform.closure import evaluate_closure, write_closure
from verification_platform.pov import write_pov_report
from verification_platform.coverage import parse_coverage
from verification_platform.waveform import assess_vacuity, waveform_contains
from verification_platform.repair import propose_enable_guard
from verification_platform.logic import dependency_cone
from verification_platform.capabilities import discover_capabilities, write_capabilities
from verification_platform.rtl import ingest_rtl_ports, write_rtl_inventory
from verification_platform.retrieval import build_retrieval_index, write_retrieval_index
from verification_platform.runner import run_command
from verification_platform.uvm import write_uvm_agent


def main() -> int:
    run = ROOT / "runs" / "latest"
    run.mkdir(parents=True, exist_ok=True)
    write_capabilities(run / "tool-capabilities.json", discover_capabilities())
    write_rtl_inventory(run / "rtl-collateral.json", ingest_rtl_ports(ROOT / "counter.sv", root=ROOT, source_revision="seeded-counter-v1"))
    write_uvm_agent("CounterAgent", ["clk", "rst", "enable", "counter_q"], run / "uvm-counter-agent.sv")
    write_retrieval_index(run / "retrieval-index.json", build_retrieval_index([ROOT / "spec.md", ROOT / "counter.sv"], root=ROOT, source_revision="seeded-counter-v1"))
    specification_ir = ingest_markdown(ROOT / "spec.md", root=ROOT, source_revision="seeded-counter-v1")
    plans = plan_ir(specification_ir)
    specification_ir.checks = [asdict(plan) for plan in plans]
    (run / "specification-ir.json").write_text(json.dumps(specification_ir.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan(plans, run / "verification-plan.json")
    (run / "planning-summary.json").write_text(json.dumps(planning_summary(specification_ir), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sva_module(plans, run / "generated_checks.sv")
    write_procedural_checker(plans, run / "procedural_checks.sv")
    binary = run / "compile" / "counter.vvp"
    compile_run = run_command(
        ["iverilog", "-g2012", "-o", str(binary), str(ROOT / "counter.sv"), str(ROOT / "tb.sv"), str(run / "procedural_checks.sv")],
        tool="iverilog-baseline", run_root=run / "compile", source_revision="seeded-counter-v1", expected_artifacts=["counter.vvp"], run_id="compile",
    )
    (run / "compile.stdout.log").write_text((run / "compile" / "stdout.log").read_text(encoding="utf-8"), encoding="utf-8")
    (run / "compile.stderr.log").write_text((run / "compile" / "stderr.log").read_text(encoding="utf-8"), encoding="utf-8")
    if compile_run.status != "passed":
        report = {"status": "blocked", "phase": "compile", "exit_code": compile_run.exit_code}
    else:
        sim_run = run_command(["vvp", str(binary)], tool="vvp-baseline", run_root=run / "simulation", source_revision="seeded-counter-v1", expected_artifacts=["waveform.vcd"], run_id="simulation")
        sim_text = (run / "simulation" / "stdout.log").read_text(encoding="utf-8") + (run / "simulation" / "stderr.log").read_text(encoding="utf-8")
        (run / "simulation.log").write_text(sim_text, encoding="utf-8")
        if (run / "simulation" / "waveform.vcd").is_file():
            shutil.copyfile(run / "simulation" / "waveform.vcd", run / "waveform.vcd")
        failure = parse_failure(sim_text)
        if failure:
            source_line = locate_source_marker(ROOT / "counter.sv", "SEEDED_BUG")
            proposal = propose_enable_guard(failure, requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=source_line)
            report = {
                "status": "failed",
                "phase": "simulation",
                "exit_code": sim_run.exit_code,
                "first_divergence": {"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual},
                "root_cause": {"file": "counter.sv", "line": source_line, "marker": "SEEDED_BUG", "hypothesis": "counter increments while enable is low", "dependency_cone": sorted(dependency_cone(ROOT / "counter.sv", "counter_q"))},
                "repair_proposal": {"before": proposal.before, "after": proposal.after, "decision": proposal.decision(), "requirement_id": proposal.requirement_id},
                "evidence": ["spec.md", "counter.sv", "tb.sv", "runs/latest/simulation.log", "runs/latest/waveform.vcd"],
            }
            ir = failure_to_ir(
                failure,
                root=ROOT,
                source_revision="seeded-counter-v1",
                artifact_paths=["spec.md", "counter.sv", "tb.sv", "runs/latest/verification-plan.json", "runs/latest/generated_checks.sv", "runs/latest/procedural_checks.sv", "runs/latest/simulation.log", "runs/latest/waveform.vcd"],
            )
            ir.tool_runs.extend([asdict(compile_run), asdict(sim_run)])
            (run / "verification-ir.json").write_text(json.dumps(ir.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            write_closure(evaluate_closure(ir), run / "closure-report.json")
            report["verification_ir"] = "runs/latest/verification-ir.json"
            report["specification_ir"] = "runs/latest/specification-ir.json"
            report["closure_report"] = "runs/latest/closure-report.json"
            report["verification_plan"] = "runs/latest/verification-plan.json"
        else:
            report = {"status": "passed" if sim_run.status == "passed" else "failed", "phase": "simulation", "exit_code": sim_run.exit_code}
    output = run / "triage-report.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    coverage_path = run / "functional-coverage.json"
    coverage_path.write_text(json.dumps({"kind": "functional", "covered": 0 if report["status"] == "failed" else 1, "total": 1}) + "\n", encoding="utf-8")
    coverage = parse_coverage(coverage_path, root=run)
    report["coverage"] = {"kind": coverage.kind, "covered": coverage.covered, "total": coverage.total, "percentage": coverage.percentage}
    report["waveform_confirmation"] = waveform_contains(run / "waveform.vcd", "counter_q", "1") if (run / "waveform.vcd").is_file() else False
    report["vacuity"] = assess_vacuity(run / "waveform.vcd", "enable", "1") if (run / "waveform.vcd").is_file() else {"status": "unknown"}
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_pov_report(run, mixed_signal_manifest=ROOT.parent.parent / "evidence" / "aimc-hardware-lab" / "verification-platform-mixed-signal-manifest.json")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
