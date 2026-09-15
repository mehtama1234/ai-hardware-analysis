#!/usr/bin/env python3
"""Run the four-workstream digital verification pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification_platform.orchestration import run_four_workstream_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--rtl", type=Path, action="append", required=True)
    parser.add_argument("--top", required=True)
    parser.add_argument("--protocol-plan", type=Path, required=True)
    parser.add_argument("--protocol-coverage-gaps", type=Path, help="JSON list of validated protocol transactions to add for uncovered scenarios")
    parser.add_argument("--protocol-coverage-report", type=Path, action="append", help="JSON coverage report with kind, covered, and total fields; may be repeated in measurement order")
    parser.add_argument("--protocol-execution-command", type=Path, action="append", help="JSON file containing a no-shell command list that executes the generated protocol sequence; may be repeated for convergence")
    parser.add_argument("--protocol-require-generated-sequence", action="store_true", help="refuse protocol execution unless every command contains the generated sequence path")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--collateral-root", type=Path, help="root directory for optional typed collateral entries")
    parser.add_argument("--collateral-entry", action="append", nargs=2, metavar=("KIND", "PATH"), help="optional collateral entry; may be repeated")
    parser.add_argument("--agent-team-input", type=Path, help="JSON list of bounded multi-agent role requests")
    parser.add_argument("--agent-team-backend", choices=("none", "local", "openai_compatible"), default="none")
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--debug-input", type=Path, help="JSON file with debug traces/evidence; optionally filtered_dut_output and filtered_dut_top")
    parser.add_argument("--optimization-proposals", type=Path, help="JSON file containing a list of predicted optimization proposals")
    parser.add_argument("--optimization-mode", choices=("explore", "exploit", "diversify", "repair", "prior_refinement"), default="exploit")
    parser.add_argument("--optimization-max-runtime-seconds", type=float)
    parser.add_argument("--optimization-measurement", type=Path, help="JSON file with one measured proxy/full optimization result")
    parser.add_argument("--agent-backend", choices=("none", "local", "openai_compatible"), default="none")
    parser.add_argument("--repair-agent-backend", choices=("none", "local", "openai_compatible"), default="none")
    parser.add_argument("--approved-repair", type=Path, help="JSON object for an explicit approval-gated copy/retest; canonical RTL is never mutated")
    parser.add_argument("--assertion-agent-backend", choices=("none", "local", "openai_compatible"), default="none")
    parser.add_argument("--assertion-antecedent-signal")
    parser.add_argument("--assertion-solver-antecedent", help="Boolean antecedent for bounded Yosys reachability; requires an admitted assertion")
    parser.add_argument("--assertion-refinement", type=Path, help="JSON file containing feedback and replacement_assertion")
    parser.add_argument("--assertion-formal-source", type=Path, action="append", help="Supplemental formal-model source; may be repeated")
    parser.add_argument("--assertion-formal-top", help="Top module containing immediate formal assertions")
    parser.add_argument("--assertion-formal-sequence", type=int, default=6)
    parser.add_argument("--compiled-sim-harness", type=Path, help="C++ harness for an optional Verilator compile-and-run stage")
    parser.add_argument("--compiled-sim-rtl", type=Path, action="append", dest="compiled_sim_rtl_sources", help="RTL source for compiled simulation instead of the primary RTL; may be repeated")
    parser.add_argument("--scheduling-regression-source", type=Path, help="SystemVerilog fixture for optional runtime scheduling classification")
    parser.add_argument("--svm-checker-source", type=Path, help="Synthesizable checker source for optional SVM compile/run evidence")
    parser.add_argument("--svm-harness", type=Path, help="Simulation harness for optional SVM compile/run evidence")
    parser.add_argument("--svm-harness-top", default="svm_harness")
    parser.add_argument("--svm-rtl", type=Path, action="append", dest="svm_rtl_sources", help="RTL source for SVM instead of the primary RTL; may be repeated")
    parser.add_argument("--verilator-option", action="append", dest="verilator_options", help="Verilator option to probe against the supplied RTL; may be repeated")
    parser.add_argument("--structural-partition-target", action="append", dest="structural_partition_targets", help="Parser-CDFG node ID to use as a functional dependency-cone target; may be repeated")
    parser.add_argument("--uvm-root", type=Path, help="Explicit UVM package root or uvm_pkg.sv path for capability probing")
    parser.add_argument("--uvm-source", type=Path, help="Generated UVM/SystemVerilog source for an explicit compile evidence stage")
    parser.add_argument("--uvm-compile-command", type=Path, help="JSON file containing the no-shell UVM compile command as a string list")
    parser.add_argument("--uvm-compile-expected-artifact", action="append", dest="uvm_compile_expected_artifacts", help="Expected relative compile artifact; may be repeated")
    parser.add_argument("--uvm-runtime-command", type=Path, help="JSON file containing the no-shell bounded UVM runtime command as a string list")
    parser.add_argument("--uvm-runtime-marker", action="append", dest="uvm_runtime_expected_markers", help="Required marker in bounded UVM runtime output; may be repeated")
    parser.add_argument("--structural-partition-output", type=Path, help="Output path for compile-ready single-source functional partition reconstruction")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="execution command after --")
    args = parser.parse_args()
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("an execution command is required after --")
    debug = json.loads(args.debug_input.read_text(encoding="utf-8")) if args.debug_input else {}
    agent_team_requests = json.loads(args.agent_team_input.read_text(encoding="utf-8")) if args.agent_team_input else None
    if args.agent_team_input and not isinstance(agent_team_requests, list):
        parser.error("--agent-team-input must contain a JSON list")
    proposals = json.loads(args.optimization_proposals.read_text(encoding="utf-8")) if args.optimization_proposals else None
    refinement = json.loads(args.assertion_refinement.read_text(encoding="utf-8")) if args.assertion_refinement else None
    approved_repair = json.loads(args.approved_repair.read_text(encoding="utf-8")) if args.approved_repair else None
    measurement = json.loads(args.optimization_measurement.read_text(encoding="utf-8")) if args.optimization_measurement else None
    coverage_gaps = json.loads(args.protocol_coverage_gaps.read_text(encoding="utf-8")) if args.protocol_coverage_gaps else None
    protocol_execution_commands = [json.loads(path.read_text(encoding="utf-8")) for path in args.protocol_execution_command] if args.protocol_execution_command else None
    uvm_compile_command = json.loads(args.uvm_compile_command.read_text(encoding="utf-8")) if args.uvm_compile_command else None
    uvm_runtime_command = json.loads(args.uvm_runtime_command.read_text(encoding="utf-8")) if args.uvm_runtime_command else None
    if args.protocol_coverage_gaps and not isinstance(coverage_gaps, list):
        parser.error("--protocol-coverage-gaps must contain a JSON list")
    if protocol_execution_commands and any(not isinstance(command, list) or not command or any(not isinstance(item, str) or not item for item in command) for command in protocol_execution_commands):
        parser.error("--protocol-execution-command files must contain JSON lists of non-empty strings")
    if args.optimization_proposals and not isinstance(proposals, list):
        parser.error("--optimization-proposals must contain a JSON list")
    if args.uvm_compile_command and (not isinstance(uvm_compile_command, list) or any(not isinstance(item, str) or not item for item in uvm_compile_command)):
        parser.error("--uvm-compile-command must contain a JSON list of non-empty strings")
    if args.uvm_runtime_command and (not isinstance(uvm_runtime_command, list) or any(not isinstance(item, str) or not item for item in uvm_runtime_command)):
        parser.error("--uvm-runtime-command must contain a JSON list of non-empty strings")
    if args.uvm_runtime_expected_markers and not uvm_runtime_command:
        parser.error("--uvm-runtime-marker requires --uvm-runtime-command")
    result = run_four_workstream_pipeline(
        args.spec, args.rtl, top=args.top, protocol_plan=args.protocol_plan,
        protocol_coverage_gaps=coverage_gaps,
        protocol_coverage_report=args.protocol_coverage_report[0] if args.protocol_coverage_report and len(args.protocol_coverage_report) == 1 else None,
        protocol_coverage_reports=args.protocol_coverage_report if args.protocol_coverage_report and len(args.protocol_coverage_report) > 1 else None,
        protocol_execution_command=protocol_execution_commands[0] if protocol_execution_commands and len(protocol_execution_commands) == 1 else None,
        protocol_execution_commands=protocol_execution_commands if protocol_execution_commands and len(protocol_execution_commands) > 1 else None,
        protocol_require_generated_sequence=args.protocol_require_generated_sequence,
        command=command, tool=command[0], run_root=args.run_root,
        source_revision=args.source_revision, timeout_seconds=args.timeout_seconds,
        collateral_entries=[{"kind": kind, "path": path} for kind, path in args.collateral_entry] if args.collateral_entry else None,
        collateral_root=args.collateral_root,
        agent_team_requests=agent_team_requests, agent_team_backend=args.agent_team_backend,
        debug_waveform=debug.get("waveform"), debug_rtl=debug.get("rtl"), debug_signal=debug.get("signal"), debug_requirement_id=debug.get("requirement_id"),
        debug_observed=[tuple(item) for item in debug.get("observed", [])] if debug else None,
        debug_reference=[tuple(item) for item in debug.get("reference", [])] if debug else None,
        debug_reference_cdfg=debug.get("reference_cdfg"), debug_rtl_cdfg=debug.get("rtl_cdfg"),
        debug_reference_traces={name: [tuple(item) for item in values] for name, values in debug.get("reference_traces", {}).items()} if debug.get("reference_traces") else None,
        debug_rtl_traces={name: [tuple(item) for item in values] for name, values in debug.get("rtl_traces", {}).items()} if debug.get("rtl_traces") else None,
        debug_alignment_explicit=debug.get("alignment_explicit"),
        debug_for_evidence=debug.get("for_evidence"), debug_against_evidence=debug.get("against_evidence"),
        debug_filtered_dut_output=debug.get("filtered_dut_output"), debug_filtered_dut_top=debug.get("filtered_dut_top"),
        debug_filtered_dut_module_targets=debug.get("filtered_dut_module_targets"),
        optimization_proposals=proposals, optimization_mode=args.optimization_mode,
        optimization_max_runtime_seconds=args.optimization_max_runtime_seconds,
        optimization_measurement=measurement,
        agent_backend=args.agent_backend,
        repair_agent_backend=args.repair_agent_backend,
        approved_repair=approved_repair,
        assertion_agent_backend=args.assertion_agent_backend,
        assertion_antecedent_signal=args.assertion_antecedent_signal,
        assertion_solver_antecedent=args.assertion_solver_antecedent,
        assertion_refinement=refinement,
        assertion_formal_sources=args.assertion_formal_source,
        assertion_formal_top=args.assertion_formal_top,
        assertion_formal_sequence=args.assertion_formal_sequence,
        compiled_sim_harness=args.compiled_sim_harness,
        compiled_sim_rtl_sources=args.compiled_sim_rtl_sources,
        scheduling_regression_source=args.scheduling_regression_source,
        svm_checker_source=args.svm_checker_source,
        svm_harness=args.svm_harness,
        svm_harness_top=args.svm_harness_top,
        svm_rtl_sources=args.svm_rtl_sources,
        verilator_options=args.verilator_options,
        structural_partition_targets=args.structural_partition_targets,
        structural_partition_output=args.structural_partition_output,
        uvm_root=args.uvm_root,
        uvm_source=args.uvm_source,
        uvm_compile_command=uvm_compile_command,
        uvm_compile_expected_artifacts=args.uvm_compile_expected_artifacts,
        uvm_runtime_command=uvm_runtime_command,
        uvm_runtime_expected_markers=args.uvm_runtime_expected_markers,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
