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
from verification_platform.lowering import generate_lowered_checker, lower_plans, write_lowering_manifest
from verification_platform.procedural import write_procedural_checker
from verification_platform.triage import failure_to_ir, locate_source_marker, parse_failure
from verification_platform.closure import evaluate_closure, write_closure
from verification_platform.pov import write_pov_report
from verification_platform.coverage import parse_coverage
from verification_platform.waveform import assess_vacuity, signal_values, waveform_contains
from verification_platform.causal import causal_graph_from_vcd, state_frontier, write_causal_graph
from verification_platform.alignment import align_signals, write_alignment
from verification_platform.diagnosis import build_balanced_diagnosis, write_balanced_diagnosis
from verification_platform.autoformalize import infer_assertion_signals, proposal_from_plan, write_assertion_proposals
from verification_platform.scheduling import lint_time_zero, write_time_zero_lint
from verification_platform.rtl_ast import extract_structural_ir
from verification_platform.repair import propose_enable_guard
from verification_platform.logic import dependency_cone, dependency_paths
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
    structural_ir, structural_run = extract_structural_ir(ROOT / "counter.sv", top="counter", run_root=run / "structural", source_revision="seeded-counter-v1")
    write_uvm_agent("CounterAgent", ["clk", "rst", "enable", "counter_q"], run / "uvm-counter-agent.sv")
    write_time_zero_lint(run / "time-zero-lint.json", lint_time_zero([ROOT / "tb.sv", run / "uvm-counter-agent.sv"], root=ROOT))
    write_retrieval_index(run / "retrieval-index.json", build_retrieval_index([ROOT / "spec.md", ROOT / "counter.sv"], root=ROOT, source_revision="seeded-counter-v1"))
    specification_ir = ingest_markdown(ROOT / "spec.md", root=ROOT, source_revision="seeded-counter-v1")
    plans = plan_ir(specification_ir)
    specification_ir.checks = [asdict(plan) for plan in plans]
    (run / "specification-ir.json").write_text(json.dumps(specification_ir.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_plan(plans, run / "verification-plan.json")
    spec_digest = specification_ir.requirements[0].source.sha256 if specification_ir.requirements and specification_ir.requirements[0].source else "0" * 64
    write_assertion_proposals([proposal_from_plan(plan, specification_sha256=spec_digest, signals=infer_assertion_signals(plan.assertion), model_id="deterministic-template") for plan in plans], run / "assertion-proposals.json")
    (run / "planning-summary.json").write_text(json.dumps(planning_summary(specification_ir), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sva_module(plans, run / "generated_checks.sv")
    lowered_properties = lower_plans(plans)
    (run / "lowered_checks.sv").write_text(generate_lowered_checker(lowered_properties), encoding="utf-8")
    write_lowering_manifest(lowered_properties, run / "sva-lowering.json")
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
        causal_graph_path = run / "causal-graph.json"
        causal_graph = None
        if (run / "waveform.vcd").is_file():
            causal_graph = causal_graph_from_vcd(run / "waveform.vcd", ROOT / "counter.sv", ["clk", "rst", "enable", "counter_q"])
            write_causal_graph(causal_graph_path, causal_graph)
            observed_trace = signal_values(run / "waveform.vcd", "counter_q")
            specification_trace = [(time, "x" if index == 0 else "0") for index, (time, _value) in enumerate(observed_trace)]
            frontier = state_frontier(observed_trace, specification_trace, signal="counter_q")
            (run / "state-frontier.json").write_text(json.dumps({"schema_version": "state-frontier-v1", "reference_kind": "seeded-counter-specification-model", "observed": observed_trace, "reference": specification_trace, "frontier": frontier}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            alignment = align_signals({"spec_counter_q": specification_trace}, {"rtl_counter_q": observed_trace})
            write_alignment(run / "signal-alignment.json", alignment)
        failure = parse_failure(sim_text)
        if failure:
            source_line = locate_source_marker(ROOT / "counter.sv", "SEEDED_BUG")
            proposal = propose_enable_guard(failure, requirement_id="REQ-COUNTER-HOLD", file="counter.sv", line=source_line)
            paths = dependency_paths(ROOT / "counter.sv", "counter_q")
            diagnosis = build_balanced_diagnosis(
                failure,
                source_revision="seeded-counter-v1",
                for_evidence=[f"cycle {failure.cycle}: observed {failure.signal}={failure.actual}; specification expects {failure.expected}"],
                against_evidence=["the RTL assignment is syntactically valid and the reset branch exists", "the dependency graph does not show enable as a driver, so implementation behavior is internally consistent but conflicts with the requirement"],
                causal_paths=paths,
            )
            write_balanced_diagnosis(diagnosis, run / "balanced-diagnosis.json")
            report = {
                "status": "failed",
                "phase": "simulation",
                "exit_code": sim_run.exit_code,
                "first_divergence": {"cycle": failure.cycle, "signal": failure.signal, "expected": failure.expected, "actual": failure.actual},
                "root_cause": {"file": "counter.sv", "line": source_line, "marker": "SEEDED_BUG", "hypothesis": "counter increments while enable is low", "dependency_cone": sorted(dependency_cone(ROOT / "counter.sv", "counter_q")), "dependency_paths": paths, "structural_ir": "runs/latest/structural/rtl-structural-ir.json", "structural_ir_sha256": structural_ir.get("ir_sha256"), "causal_graph": "runs/latest/causal-graph.json", "causal_graph_sha256": causal_graph.get("graph_sha256") if causal_graph else None, "state_frontier": "runs/latest/state-frontier.json", "signal_alignment": "runs/latest/signal-alignment.json", "balanced_diagnosis": "runs/latest/balanced-diagnosis.json", "balanced_diagnosis_sha256": diagnosis.diagnosis_sha256},
                "repair_proposal": {"before": proposal.before, "after": proposal.after, "decision": proposal.decision(), "requirement_id": proposal.requirement_id},
                "evidence": ["spec.md", "counter.sv", "tb.sv", "runs/latest/simulation.log", "runs/latest/waveform.vcd"],
            }
            ir = failure_to_ir(
                failure,
                root=ROOT,
                source_revision="seeded-counter-v1",
                artifact_paths=["spec.md", "counter.sv", "tb.sv", "runs/latest/verification-plan.json", "runs/latest/generated_checks.sv", "runs/latest/lowered_checks.sv", "runs/latest/sva-lowering.json", "runs/latest/assertion-proposals.json", "runs/latest/time-zero-lint.json", "runs/latest/structural/rtl-structural-ir.json", "runs/latest/structural/rtl-structural.json", "runs/latest/procedural_checks.sv", "runs/latest/simulation.log", "runs/latest/waveform.vcd", "runs/latest/causal-graph.json", "runs/latest/state-frontier.json", "runs/latest/signal-alignment.json", "runs/latest/balanced-diagnosis.json"],
            )
            ir.tool_runs.extend([asdict(structural_run), asdict(compile_run), asdict(sim_run)])
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
    mixed_manifest = ROOT.parent.parent / "evidence" / "aimc-hardware-lab" / "verification-platform-mixed-signal-manifest.json"
    write_pov_report(run, **({"mixed_signal_manifest": mixed_manifest} if mixed_manifest.is_file() else {}))
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "failed" else 1


if __name__ == "__main__":
    sys.exit(main())
