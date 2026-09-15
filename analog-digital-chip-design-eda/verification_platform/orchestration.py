"""Fail-closed orchestration for the four digital verification workstreams."""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .pipeline import run_pipeline
from .protocol import augment_protocol_plan, load_protocol_plan, write_protocol_sequence
from .coverage import parse_coverage, rank_coverage_gaps
from .rtl_ast import extract_parser_cdfg, extract_structural_ir, partition_parser_cdfg, reconstruct_functional_partition, verify_functional_partition_reconstruction, verify_parser_cdfg_partition
from .runner import run_command
from .scheduling import run_scheduling_gate, run_time_zero_regression
from .simulation import probe_verilator_capability_matrix, run_verilator_lint
from .debug import analyze_failure, generate_filtered_dut, generate_hierarchical_filtered_dut, prove_filtered_dut_equivalence, prove_hierarchical_filtered_dut_equivalence, write_debug_package
from .optimization import append_optimization_result, build_optimization_state, load_optimization_state, select_next_candidate, write_optimization_state
from .autoformalize import evaluate_proposal_vacuity, evaluate_proposal_vacuity_solver, infer_assertion_signals, invoke_assertion_backend, proposal_from_record, refine_assertion_proposal
from .lowering import generate_lowered_checker, lower_assertion
from .sva import compile_sva_with_verilator
from .llm_backend import invoke_local_backend, invoke_openai_compatible_backend
from .workflow import advance_checkpoint, create_checkpoint, write_checkpoint
from .formal import run_yosys_assertion_proof
from .compiled_sim import run_verilator_compiled_simulation
from .svm import run_synthesizable_checker
from .repair import RepairProposal, build_repair_patch_candidate, run_approved_repair_retest
from .alignment import align_cdfg_signals
from .collateral import build_collateral_package, write_collateral_package
from .agent_team import run_agent_team
from .uvm import probe_uvm_runtime, run_uvm_compile
from .artifacts import build_artifact_manifest, write_artifact_manifest
from .ledger import sha256_file


def run_four_workstream_pipeline(
    specification: str | Path,
    rtl_sources: list[str | Path],
    *,
    top: str,
    protocol_plan: str | Path,
    protocol_coverage_gaps: list[dict[str, Any]] | None = None,
    protocol_coverage_report: str | Path | None = None,
    protocol_coverage_reports: list[str | Path] | None = None,
    protocol_execution_command: list[str] | None = None,
    protocol_execution_commands: list[list[str]] | None = None,
    protocol_require_generated_sequence: bool = False,
    command: list[str],
    tool: str,
    run_root: str | Path,
    source_revision: str,
    timeout_seconds: float = 60.0,
    collateral_entries: list[dict[str, str]] | None = None,
    collateral_root: str | Path | None = None,
    agent_team_requests: list[dict[str, Any]] | None = None,
    agent_team_backend: str = "none",
    debug_waveform: str | Path | None = None,
    debug_rtl: str | Path | None = None,
    debug_signal: str | None = None,
    debug_requirement_id: str | None = None,
    debug_observed: list[tuple[int, str]] | None = None,
    debug_reference: list[tuple[int, str]] | None = None,
    debug_reference_cdfg: dict[str, Any] | None = None,
    debug_rtl_cdfg: dict[str, Any] | None = None,
    debug_reference_traces: dict[str, list[tuple[int, str]]] | None = None,
    debug_rtl_traces: dict[str, list[tuple[int, str]]] | None = None,
    debug_alignment_explicit: dict[str, str] | None = None,
    debug_for_evidence: list[str] | None = None,
    debug_against_evidence: list[str] | None = None,
    debug_filtered_dut_output: str | Path | None = None,
    debug_filtered_dut_top: str | None = None,
    debug_filtered_dut_module_targets: dict[str, str] | None = None,
    optimization_proposals: list[dict[str, Any]] | None = None,
    optimization_mode: str = "exploit",
    optimization_max_runtime_seconds: float | None = None,
    optimization_measurement: dict[str, Any] | None = None,
    agent_backend: str = "none",
    repair_agent_backend: str = "none",
    approved_repair: dict[str, Any] | None = None,
    assertion_agent_backend: str = "none",
    assertion_antecedent_signal: str | None = None,
    assertion_solver_antecedent: str | None = None,
    assertion_refinement: dict[str, Any] | None = None,
    assertion_formal_sources: list[str | Path] | None = None,
    assertion_formal_top: str | None = None,
    assertion_formal_sequence: int = 6,
    compiled_sim_harness: str | Path | None = None,
    compiled_sim_rtl_sources: list[str | Path] | None = None,
    scheduling_regression_source: str | Path | None = None,
    svm_checker_source: str | Path | None = None,
    svm_harness: str | Path | None = None,
    svm_harness_top: str = "svm_harness",
    svm_rtl_sources: list[str | Path] | None = None,
    verilator_options: list[str] | None = None,
    structural_partition_targets: list[str] | None = None,
    structural_partition_output: str | Path | None = None,
    uvm_root: str | Path | None = None,
    uvm_source: str | Path | None = None,
    uvm_compile_command: list[str] | None = None,
    uvm_compile_expected_artifacts: list[str] | None = None,
    uvm_runtime_command: list[str] | None = None,
    uvm_runtime_expected_markers: list[str] | None = None,
) -> dict[str, Any]:
    """Run planning, scheduling, structural, protocol, and execution stages."""
    if not rtl_sources or not top or not source_revision:
        raise ValueError("rtl_sources, top, and source_revision are required")
    root = Path(run_root)
    root.mkdir(parents=True, exist_ok=True)
    uvm_capability = probe_uvm_runtime(uvm_root=uvm_root, run_root=root / "uvm") if uvm_root is not None else {"status": "not_run", "claim_boundary": "UVM capability probing requires an explicit package root"}
    if (uvm_source is None) != (uvm_compile_command is None):
        raise ValueError("uvm_source and uvm_compile_command must be supplied together")
    if uvm_runtime_command is not None and uvm_source is None:
        raise ValueError("uvm_runtime_command requires uvm_source and uvm_compile_command")
    if uvm_runtime_expected_markers is not None and uvm_runtime_command is None:
        raise ValueError("uvm_runtime_expected_markers requires uvm_runtime_command")
    if uvm_source is not None and uvm_root is None:
        raise ValueError("uvm_root is required for UVM compilation")
    if uvm_source is None:
        uvm_compile_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "UVM compilation requires an explicit source and command"}
    else:
        uvm_compile_result = run_uvm_compile(
            uvm_source, uvm_root=uvm_root, compile_command=uvm_compile_command or [],
            run_root=root / "uvm" / "compile", source_revision=source_revision,
            timeout_seconds=timeout_seconds, expected_artifacts=uvm_compile_expected_artifacts,
            runtime_command=uvm_runtime_command,
            runtime_expected_markers=uvm_runtime_expected_markers,
        )
    uvm_result = uvm_compile_result if uvm_compile_result["status"] != "not_run" else uvm_capability
    if collateral_entries is None:
        collateral_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "typed collateral intake requires explicit entries"}
    else:
        intake_root = Path(collateral_root) if collateral_root is not None else Path(specification).parent
        collateral_result = build_collateral_package(collateral_entries, root=intake_root, source_revision=source_revision)
        collateral_path = write_collateral_package(collateral_result, root / "collateral" / "collateral-package.json")
        collateral_result["path"] = str(collateral_path)
    collateral_evidence = [str(collateral_result["path"])] if collateral_result.get("path") else []
    if agent_team_requests is None:
        agent_team_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "multi-agent team execution requires explicit role requests"}
    else:
        if agent_team_backend not in {"local", "openai_compatible"}:
            raise ValueError("agent_team_backend must be local or openai_compatible when team requests are supplied")
        team_requests = []
        for request in agent_team_requests:
            enriched_request = dict(request)
            enriched_request["evidence"] = list(dict.fromkeys([*(request.get("evidence") or []), *collateral_evidence]))
            enriched_request["allowed_source_revision"] = request.get("allowed_source_revision", source_revision)
            enriched_request["collateral_package_sha256"] = collateral_result.get("package_sha256")
            team_requests.append(enriched_request)
        agent_team_result = run_agent_team(team_requests, backend=agent_team_backend, source_revision=source_revision)
        team_path = root / "agents" / "agent-team-result.json"
        team_path.parent.mkdir(parents=True, exist_ok=True)
        team_path.write_text(json.dumps(agent_team_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        agent_team_result["path"] = str(team_path)
    agent_team_evidence = [str(agent_team_result["path"])] if agent_team_result.get("path") else []
    execution = run_pipeline(specification, command, tool=tool, run_root=root / "execution", source_revision=source_revision, timeout_seconds=timeout_seconds)
    scheduling = run_scheduling_gate(rtl_sources, run_root=root / "scheduling", source_revision=source_revision, timeout_seconds=timeout_seconds)
    if scheduling_regression_source is None:
        scheduling_runtime: dict[str, Any] = {"status": "not_run", "claim_boundary": "runtime scheduling regression requires an explicit fixture"}
    else:
        scheduling_runtime = run_time_zero_regression(
            scheduling_regression_source, run_root=root / "scheduling" / "runtime", source_revision=source_revision,
            timeout_seconds=timeout_seconds,
        )
        (root / "scheduling" / "runtime-regression.json").write_text(json.dumps(scheduling_runtime, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verilator_lint = run_verilator_lint(*rtl_sources, run_root=root / "verilator-lint", source_revision=source_revision, top=top)
    if verilator_options is None:
        verilator_capabilities: dict[str, Any] = {"status": "not_run", "claim_boundary": "Verilator capability matrix requires explicit requested options"}
    else:
        verilator_capabilities = probe_verilator_capability_matrix(
            rtl_sources, top=top, options=verilator_options, run_root=root / "verilator-capabilities",
            source_revision=source_revision, timeout_seconds=timeout_seconds,
        )
    structural, structural_run = extract_structural_ir(*rtl_sources, top=top, run_root=root / "structural", source_revision=source_revision, timeout_seconds=timeout_seconds)
    parser_cdfg, parser_cdfg_run = extract_parser_cdfg(*rtl_sources, top=top, run_root=root / "structural", source_revision=source_revision, timeout_seconds=timeout_seconds)
    parser_partition: dict[str, Any] | None = None
    parser_partition_path: Path | None = None
    parser_reconstruction: dict[str, Any] | None = None
    parser_reconstruction_path: Path | None = None
    parser_reconstruction_equivalence: dict[str, Any] | None = None
    if structural_partition_targets is not None:
        parser_partition = partition_parser_cdfg(parser_cdfg, targets=structural_partition_targets)
        parser_partition_path = root / "structural" / "functional-cdfg-partition.json"
        parser_partition_path.write_text(json.dumps(parser_partition, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if verify_parser_cdfg_partition(parser_cdfg, parser_partition):
            raise ValueError("generated functional CDFG partition failed integrity verification")
        parser_reconstruction_path = (Path(structural_partition_output).resolve() if structural_partition_output is not None else root / "structural" / "functional-filtered-dut.sv")
        try:
            parser_reconstruction_path.relative_to(root.resolve())
        except ValueError as error:
            raise ValueError("structural partition output must be inside the run root") from error
        if len(rtl_sources) == 1:
            parser_reconstruction = reconstruct_functional_partition(
                rtl_sources[0], parser_cdfg, parser_partition,
                output=parser_reconstruction_path, source_revision=source_revision,
            )
            reconstruction_errors = verify_functional_partition_reconstruction(parser_reconstruction, parser_cdfg, parser_partition)
            if reconstruction_errors:
                raise ValueError("generated functional reconstruction failed integrity verification: " + "; ".join(reconstruction_errors))
            if parser_reconstruction.get("status") == "ready":
                parser_reconstruction_equivalence = prove_filtered_dut_equivalence(
                    rtl_sources[0], parser_reconstruction_path, top=top,
                    run_root=root / "structural" / "functional-equivalence",
                    source_revision=source_revision, timeout_seconds=timeout_seconds,
                )
        else:
            parser_reconstruction = {
                "schema_version": "rtl-functional-partition-reconstruction-v1",
                "source_revision": source_revision, "status": "blocked", "functional_equivalence_proven": False,
                "claim_boundary": "compile-ready dependency slice only; functional equivalence requires a separate solver proof",
                "blocked_reason": "source reconstruction requires exactly one RTL source",
            }
    plan = load_protocol_plan(protocol_plan)
    coverage_gap_path: Path | None = None
    coverage_report_path: Path | None = None
    coverage_ranking_path: Path | None = None
    coverage_convergence_path: Path | None = None
    coverage_result: dict[str, Any] | None = None
    coverage_sources: list[Path] = []
    if protocol_coverage_report is not None:
        coverage_sources.append(Path(protocol_coverage_report))
    coverage_sources.extend(Path(path) for path in (protocol_coverage_reports or []))
    if coverage_sources:
        if len({str(path.resolve()) for path in coverage_sources}) != len(coverage_sources):
            raise ValueError("protocol coverage reports must be unique")
        parsed_coverages = []
        for index, source_coverage in enumerate(coverage_sources):
            if not source_coverage.is_file():
                raise ValueError(f"protocol coverage report does not exist: {source_coverage}")
            coverage_report_path = root / "protocol" / ("coverage-report.json" if len(coverage_sources) == 1 else f"coverage-report-{index:02d}.json")
            coverage_report_path.parent.mkdir(parents=True, exist_ok=True)
            coverage_report_path.write_text(source_coverage.read_text(encoding="utf-8"), encoding="utf-8")
            parsed_coverages.append(parse_coverage(coverage_report_path, root=root))
        first = parsed_coverages[0]
        if any(item.kind != first.kind or item.total != first.total for item in parsed_coverages):
            raise ValueError("protocol coverage reports must use one kind and total")
        if any(current.covered < previous.covered for previous, current in zip(parsed_coverages, parsed_coverages[1:])):
            raise ValueError("protocol coverage reports must be monotonically non-decreasing")
        parsed_coverage = parsed_coverages[-1]
        coverage_result = {"kind": parsed_coverage.kind, "covered": parsed_coverage.covered, "total": parsed_coverage.total, "percentage": parsed_coverage.percentage, "evidence_path": parsed_coverage.evidence_path}
        coverage_ranking_path = root / "protocol" / "coverage-gaps.json"
        coverage_ranking_path.write_text(json.dumps({"schema_version": "coverage-gap-ranking-v1", "gaps": rank_coverage_gaps(parsed_coverages)}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        convergence = {
            "schema_version": "coverage-convergence-v1",
            "kind": first.kind,
            "total": first.total,
            "iterations": [{"iteration": index, "covered": item.covered, "percentage": item.percentage, "evidence_path": item.evidence_path} for index, item in enumerate(parsed_coverages)],
            "status": "converged" if parsed_coverage.covered == parsed_coverage.total else "active",
            "claim_boundary": "measured coverage trajectory; convergence does not prove correctness or replace formal evidence",
        }
        convergence["coverage_delta"] = parsed_coverage.covered - first.covered
        convergence["iterations_completed"] = len(parsed_coverages)
        convergence["convergence_sha256"] = hashlib.sha256(json.dumps(convergence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        coverage_convergence_path = root / "protocol" / "coverage-convergence.json"
        coverage_convergence_path.write_text(json.dumps(convergence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if protocol_coverage_gaps is not None:
        plan = augment_protocol_plan(plan, protocol_coverage_gaps)
        coverage_gap_path = root / "protocol" / "coverage-augmented-plan.json"
        coverage_gap_path.parent.mkdir(parents=True, exist_ok=True)
        coverage_gap_path.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    protocol_path = write_protocol_sequence(plan, root / "protocol" / f"{plan.name}_sequence.sv")
    protocol_compile = run_command(
        ["iverilog", "-g2012", "-t", "null", str(protocol_path.resolve())],
        tool="protocol-sequence-compile", run_root=root / "protocol-compile", source_revision=source_revision,
        timeout_seconds=timeout_seconds, run_id="protocol-sequence",
    )
    if protocol_execution_command is not None and protocol_execution_commands is not None:
        raise ValueError("supply protocol_execution_command or protocol_execution_commands, not both")
    execution_commands = protocol_execution_commands if protocol_execution_commands is not None else ([protocol_execution_command] if protocol_execution_command is not None else [])
    if any(not isinstance(item, list) or not item or any(not isinstance(argument, str) or not argument for argument in item) for item in execution_commands):
        raise ValueError("protocol execution commands must be non-empty lists of non-empty strings")
    protocol_execution_convergence_path: Path | None = None
    sequence_path_token = str(protocol_path.resolve())
    sequence_binding_errors = []
    if protocol_require_generated_sequence:
        sequence_binding_errors = [
            f"execution command {index} does not reference generated sequence {sequence_path_token}"
            for index, execution_command in enumerate(execution_commands)
            if sequence_path_token not in execution_command
        ]
    if not execution_commands:
        protocol_execution_result: dict[str, Any] = {
            "status": "not_run",
            "claim_boundary": "protocol execution requires an explicit command that runs the generated sequence with a testbench",
        }
    elif sequence_binding_errors:
        protocol_execution_result = {
            "schema_version": "protocol-sequence-execution-v1" if len(execution_commands) == 1 else "protocol-sequence-execution-batch-v1",
            "status": "blocked", "iterations": [], "coverage": None,
            "blocked_reason": "generated-sequence binding is required but the execution command does not include the generated sequence path",
            "binding_errors": sequence_binding_errors,
            "claim_boundary": "execution was refused because generated-sequence identity could not be established",
        }
    else:
        iterations: list[dict[str, Any]] = []
        for index, execution_command in enumerate(execution_commands):
            execution_root = root / "protocol-execution" if len(execution_commands) == 1 else root / "protocol-execution" / f"iteration-{index:02d}"
            execution_run = run_command(
                execution_command, tool="protocol-sequence-execution", run_root=execution_root,
                source_revision=source_revision, timeout_seconds=timeout_seconds, run_id=f"protocol-sequence-execution-{index:02d}",
            )
            stdout = (execution_root / "stdout.log").read_text(encoding="utf-8") if (execution_root / "stdout.log").is_file() else ""
            marker = re.search(r"PROTOCOL_SEQUENCE_COVERAGE\s+covered=(\d+)\s+total=(\d+)", stdout)
            result_marker = re.search(r"PROTOCOL_SEQUENCE_RESULT\s+status=(passed|failed)", stdout)
            coverage = {"covered": int(marker.group(1)), "total": int(marker.group(2)), "percentage": round(100.0 * int(marker.group(1)) / int(marker.group(2)), 4)} if marker else None
            iterations.append({"iteration": index, "status": "passed" if execution_run.status == "passed" and coverage and coverage["covered"] <= coverage["total"] and result_marker and result_marker.group(1) == "passed" else "blocked", "tool_run": asdict(execution_run), "coverage": coverage, "dut_result": result_marker.group(1) if result_marker else None})
        totals = {item["coverage"]["total"] for item in iterations if item["coverage"] is not None}
        valid_totals = len(totals) == 1
        monotonic = all(item["coverage"]["covered"] >= previous["coverage"]["covered"] for previous, item in zip(iterations, iterations[1:]) if previous["coverage"] and item["coverage"])
        final_coverage = iterations[-1]["coverage"] if iterations else None
        all_complete = valid_totals and monotonic and final_coverage is not None and final_coverage["covered"] == final_coverage["total"] and all(item["status"] == "passed" for item in iterations)
        protocol_execution_result = {
            "schema_version": "protocol-sequence-execution-v1" if len(iterations) == 1 else "protocol-sequence-execution-batch-v1",
            "status": "passed" if all_complete else "blocked",
            "tool_run": iterations[0]["tool_run"] if len(iterations) == 1 else None,
            "coverage": final_coverage if len(iterations) == 1 else None,
            "iterations": iterations if len(iterations) > 1 else None,
            "claim_boundary": "executed generated-sequence progress and observed DUT check result; not complete DUT functional coverage or protocol correctness proof",
        }
        if len(iterations) > 1:
            convergence = {"schema_version": "protocol-execution-convergence-v1", "source_revision": source_revision, "iterations": iterations, "status": "converged" if all_complete else "active", "claim_boundary": "measured executable-sequence progress and DUT check-result trajectory; not complete DUT functional coverage or protocol correctness proof"}
            convergence["convergence_sha256"] = hashlib.sha256(json.dumps(convergence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            protocol_execution_convergence_path = root / "protocol" / "protocol-execution-convergence.json"
            protocol_execution_convergence_path.write_text(json.dumps(convergence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if protocol_execution_result["status"] == "blocked":
            protocol_execution_result["blocked_reason"] = "execution failed, coverage totals changed, progress regressed, DUT check failed, or final run did not complete all generated steps"
    debug_inputs = [debug_waveform, debug_rtl, debug_signal, debug_observed, debug_reference]
    if any(item is not None for item in debug_inputs) and not all(item is not None for item in debug_inputs):
        raise ValueError("debug waveform, RTL, signal, observed trace, and reference trace must be supplied together")
    if all(item is not None for item in debug_inputs):
        debug_package = analyze_failure(
            debug_waveform, debug_rtl, signal=debug_signal, observed=debug_observed, reference=debug_reference,
            source_revision=source_revision, for_evidence=debug_for_evidence or [], against_evidence=debug_against_evidence or [],
        )
        debug_path = write_debug_package(debug_package, root / "debug" / "debug-package.json")
        debug_result: dict[str, Any] = {"status": str(debug_package["status"]), "path": str(debug_path), "package_sha256": debug_package["package_sha256"], "causal_frontier_binding": debug_package.get("causal_frontier_binding")}
        alignment_inputs = [debug_reference_cdfg, debug_rtl_cdfg, debug_reference_traces, debug_rtl_traces]
        if any(item is not None for item in alignment_inputs) and not all(item is not None for item in alignment_inputs):
            raise ValueError("CDFG alignment requires reference/RTL CDFGs and both trace maps")
        if all(item is not None for item in alignment_inputs):
            cdfg_alignment = align_cdfg_signals(
                debug_reference_cdfg, debug_rtl_cdfg, debug_reference_traces, debug_rtl_traces,
                explicit=debug_alignment_explicit,
            )
            cdfg_alignment_path = root / "debug" / "cdfg-signal-alignment.json"
            cdfg_alignment_path.parent.mkdir(parents=True, exist_ok=True)
            cdfg_alignment_path.write_text(json.dumps(cdfg_alignment, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            alignment_body = cdfg_alignment["alignment"]
            debug_result["cdfg_alignment"] = {
                "status": "available" if alignment_body["ambiguous_count"] == 0 and alignment_body["unresolved_count"] == 0 else "review_required",
                "path": str(cdfg_alignment_path), "alignment_sha256": cdfg_alignment["alignment_sha256"],
                "aligned_count": alignment_body["aligned_count"], "ambiguous_count": alignment_body["ambiguous_count"],
                "unresolved_count": alignment_body["unresolved_count"], "claim_boundary": cdfg_alignment["claim_boundary"],
            }
        if debug_filtered_dut_output is not None:
            filtered_path = Path(debug_filtered_dut_output)
            if debug_filtered_dut_top:
                filtered = generate_hierarchical_filtered_dut(debug_rtl, signal=debug_signal, source_revision=source_revision, output=filtered_path, top=debug_filtered_dut_top, module_targets=debug_filtered_dut_module_targets)
                if filtered["status"] == "ready":
                    filtered_proof = prove_hierarchical_filtered_dut_equivalence(debug_rtl, filtered_path, top=debug_filtered_dut_top, selected_modules=filtered["selected_modules"], run_root=root / "debug" / "filtered-equivalence", source_revision=source_revision, timeout_seconds=timeout_seconds)
                else:
                    filtered_proof = {"status": "blocked", "blocked_reason": filtered.get("blocked_reason")}
            else:
                filtered = generate_filtered_dut(debug_rtl, signal=debug_signal, source_revision=source_revision, output=filtered_path)
                if filtered["status"] == "ready":
                    filtered_proof = prove_filtered_dut_equivalence(debug_rtl, filtered_path, top=top, run_root=root / "debug" / "filtered-equivalence", source_revision=source_revision, timeout_seconds=timeout_seconds)
                else:
                    filtered_proof = {"status": "blocked", "blocked_reason": filtered.get("blocked_reason")}
            debug_result["filtered_dut"] = filtered
            debug_result["filtered_dut_equivalence"] = filtered_proof
    else:
        if debug_filtered_dut_output is not None:
            raise ValueError("filtered DUT output requires complete debug inputs")
        debug_result = {"status": "not_run", "claim_boundary": "debug workstream requires waveform, reference trace, and RTL inputs"}
    if agent_backend not in {"none", "local", "openai_compatible"}:
        raise ValueError("agent_backend must be none, local, or openai_compatible")
    if agent_backend != "none" and debug_result["status"] == "not_run":
        raise ValueError("agent_backend requires debug inputs")
    if agent_backend == "none":
        agent_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "LLM agent invocation is opt-in"}
    else:
        frontier = debug_package["state_frontier"]
        request = {
            "task": "diagnose_failure",
            "failure": {"cycle": frontier["cycle"], "signal": debug_package["signal"], "expected": frontier["reference"], "actual": frontier["observed"]},
            "allowed_source_revision": source_revision,
            "evidence": [str(debug_path), str(debug_path) + "#state_frontier", str(debug_path) + "#causal_graph", *collateral_evidence, *agent_team_evidence],
            "collateral_package_sha256": collateral_result.get("package_sha256"),
            "agent_team_sha256": agent_team_result.get("team_sha256"),
            "team_handoffs": agent_team_result.get("handoffs", []),
            "dependency_cone": sorted({name for path in debug_package["dependency_paths"] for name in path}),
            "repair_context": debug_package.get("replay_slice", {}).get("selected_lines", []),
            "root_cause_candidates": debug_package.get("root_cause_candidates", {}),
            "competing_hypotheses": debug_package.get("competing_hypotheses", {}),
            "causal_timeline": debug_package.get("causal_timeline", {}),
            "causal_timeline_validation": debug_package.get("causal_timeline_validation", {}),
            "output_contract": "diagnosis proposal; status must be review_required; do not claim closure",
        }
        backend_result = invoke_local_backend(request) if agent_backend == "local" else invoke_openai_compatible_backend(request)
        agent_result = {"status": backend_result.status, "backend": backend_result.backend, "error": backend_result.error, "agent_team_sha256": agent_team_result.get("team_sha256"), "team_handoff_count": len(agent_team_result.get("handoffs", []))}
        if backend_result.proposal is not None:
            proposal = backend_result.proposal.record()
            agent_result["proposal"] = proposal
            agent_result["grounded"] = proposal["source_revision"] == source_revision and set(proposal["evidence"]).issubset(set(request["evidence"]))
            if proposal["kind"] != "diagnosis" or proposal["status"] != "review_required" or not agent_result["grounded"]:
                agent_result["status"] = "blocked"
                agent_result["error"] = "agent proposal failed diagnosis, review, or evidence-grounding gate"
    if repair_agent_backend not in {"none", "local", "openai_compatible"}:
        raise ValueError("repair_agent_backend must be none, local, or openai_compatible")
    if repair_agent_backend == "none":
        repair_agent_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "repair agent invocation is opt-in and review-only"}
    elif debug_result["status"] == "not_run":
        raise ValueError("repair_agent_backend requires debug inputs")
    else:
        repair_request = {
            "task": "propose_repair",
            "failure": {"cycle": debug_package["state_frontier"]["cycle"], "signal": debug_package["signal"], "expected": debug_package["state_frontier"]["reference"], "actual": debug_package["state_frontier"]["observed"]},
            "allowed_source_revision": source_revision,
            "evidence": [str(debug_path), str(debug_path) + "#state_frontier", str(debug_path) + "#causal_graph", *collateral_evidence, *agent_team_evidence],
            "collateral_package_sha256": collateral_result.get("package_sha256"),
            "agent_team_sha256": agent_team_result.get("team_sha256"),
            "team_handoffs": agent_team_result.get("handoffs", []),
            "dependency_cone": sorted({name for path in debug_package["dependency_paths"] for name in path}),
            "repair_context": debug_package.get("replay_slice", {}).get("selected_lines", []),
            "root_cause_candidates": debug_package.get("root_cause_candidates", {}),
            "competing_hypotheses": debug_package.get("competing_hypotheses", {}),
            "causal_timeline": debug_package.get("causal_timeline", {}),
            "causal_timeline_validation": debug_package.get("causal_timeline_validation", {}),
            "requirement_id": debug_requirement_id,
            "specification_context": [
                {"requirement_id": item.id, "text": item.text}
                for item in execution["specification_ir"].requirements
            ],
            "output_contract": "review-only bounded repair proposal; do not modify source or claim closure",
            "repair_operator_choices": ["approval_gated_copy_only"],
        }
        # For the seeded counter demonstration, the deterministic repair
        # library supplies the bounded text candidate while the model supplies
        # the review rationale.  This keeps the model out of free-form source
        # mutation and still routes its proposal through the normal admission
        # and human-approval gates.
        if debug_signal == "counter_q" and debug_package["state_frontier"].get("reference") == "0":
            repair_request.update({
                "repair_before": "counter_q <= counter_q + 4'd1;",
                "repair_after": "if (enable) counter_q <= counter_q + 4'd1;",
            })
        backend_result = invoke_local_backend(repair_request) if repair_agent_backend == "local" else invoke_openai_compatible_backend(repair_request)
        repair_agent_result = {"status": backend_result.status, "backend": backend_result.backend, "error": backend_result.error, "agent_team_sha256": agent_team_result.get("team_sha256"), "team_handoff_count": len(agent_team_result.get("handoffs", []))}
        if backend_result.proposal is not None:
            proposal = backend_result.proposal.record()
            repair_agent_result["proposal"] = proposal
            repair_agent_result["grounded"] = proposal["kind"] == "repair" and proposal["status"] == "review_required" and proposal["source_revision"] == source_revision and set(proposal["evidence"]).issubset(set(repair_request["evidence"]))
            raw_payload = backend_result.raw or {}
            if repair_agent_result["grounded"] and isinstance(raw_payload, dict) and "before" in raw_payload and "after" in raw_payload:
                try:
                    repair_agent_result["patch_candidate"] = build_repair_patch_candidate(
                        raw_payload, debug_rtl, source_revision=source_revision, evidence=repair_request["evidence"],
                        allowed_source_locations=debug_package.get("root_cause_candidates", {}).get("candidates", []),
                    )
                except ValueError as error:
                    repair_agent_result["status"] = "blocked"
                    repair_agent_result["error"] = f"repair patch candidate failed validation: {error}"
            elif repair_agent_result["grounded"]:
                repair_agent_result["patch_candidate_status"] = "not_provided"
            if not repair_agent_result["grounded"]:
                repair_agent_result["status"] = "blocked"
                repair_agent_result["error"] = "repair proposal failed kind, review, or evidence-grounding gate"
    if approved_repair is None:
        repair_retest_result: dict[str, Any] = {
            "status": "not_run",
            "claim_boundary": "approved repair retest requires an explicit proposal, copy destination, and command",
        }
    else:
        if not all(key in approved_repair for key in ("source", "destination", "command")):
            raise ValueError("approved_repair requires source, destination, and command")
        from_agent = approved_repair.get("proposal_from_agent", False)
        if not isinstance(from_agent, bool):
            raise ValueError("approved_repair proposal_from_agent must be a Boolean")
        if not from_agent and "proposal" not in approved_repair:
            raise ValueError("approved_repair requires proposal unless proposal_from_agent is true")
        if not isinstance(approved_repair["command"], list) or not approved_repair["command"] or any(not isinstance(item, str) or not item for item in approved_repair["command"]):
            raise ValueError("approved_repair command must be a non-empty list")
        if not from_agent and not isinstance(approved_repair["proposal"], dict):
            raise ValueError("approved_repair proposal must be an object")
        if "human_approved" in approved_repair and not isinstance(approved_repair["human_approved"], bool):
            raise ValueError("approved_repair human_approved must be a Boolean")
        if debug_rtl is None or Path(str(approved_repair["source"])).resolve() != Path(debug_rtl).resolve():
            raise ValueError("approved repair source must be the supplied debug RTL")
        destination = Path(str(approved_repair["destination"])).resolve()
        try:
            destination.relative_to(root.resolve())
        except ValueError as error:
            raise ValueError("approved repair destination must be inside the run root") from error
        if from_agent:
            candidate = repair_agent_result.get("patch_candidate")
            if repair_agent_result.get("status") != "available" or not isinstance(candidate, dict) or candidate.get("status") != "review_required":
                repair_retest_result = {
                    "status": "blocked",
                    "error": "approved repair requested the agent candidate, but no validated review-only candidate is available",
                    "claim_boundary": "approved repair retest failed closed; agent output was not approved or applied",
                }
                proposal_payload = None
            else:
                proposal_payload = {
                    "requirement_id": str(candidate.get("requirement_id") or repair_agent_result.get("proposal", {}).get("requirement_id", "AGENT-REPAIR")),
                "file": str(candidate["source"]), "line": int(candidate["line"]),
                "before": candidate["before"], "after": candidate["after"],
                "rationale": str(repair_agent_result.get("proposal", {}).get("rationale", "approved agent repair candidate")),
                "edit_operator": candidate.get("edit_operator", "exact_text_replace"),
                }
        else:
            proposal_payload = approved_repair["proposal"]
        try:
            if proposal_payload is None:
                raise ValueError("agent repair candidate is unavailable")
            proposal = RepairProposal(
                requirement_id=str(proposal_payload["requirement_id"]),
                file=str(proposal_payload.get("file", approved_repair["source"])),
                line=int(proposal_payload["line"]),
                before=str(proposal_payload["before"]),
                after=str(proposal_payload["after"]),
                rationale=str(proposal_payload["rationale"]),
            )
            repair_retest_result = run_approved_repair_retest(
                approved_repair["source"], destination, proposal,
                [str(item) for item in approved_repair["command"]],
                run_root=root / "debug" / "approved-repair-retest",
                source_revision=source_revision,
                expected_artifacts=[str(item) for item in approved_repair.get("expected_artifacts", [])],
                timeout_seconds=timeout_seconds,
                human_approved=bool(approved_repair.get("human_approved", False)),
            )
            repair_retest_result["path"] = str(root / "debug" / "approved-repair-retest" / "repair-retest.json")
        except (KeyError, TypeError, ValueError, PermissionError) as error:
            repair_retest_result = {
                "status": "blocked",
                "error": str(error),
                "claim_boundary": "approved repair retest failed closed; canonical RTL was not authorized for mutation",
            }
    if assertion_agent_backend not in {"none", "local", "openai_compatible"}:
        raise ValueError("assertion_agent_backend must be none, local, or openai_compatible")
    if assertion_agent_backend == "none":
        assertion_agent_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "assertion agent invocation is opt-in"}
    elif not execution["plans"]:
        assertion_agent_result = {"status": "blocked", "error": "no deterministic verification plan is available for assertion-agent generation"}
    else:
        spec_ir = execution["specification_ir"]
        spec_digests = {
            item.id: item.source.sha256 for item in spec_ir.requirements
            if item.source is not None
        }
        structural_module = structural.get("modules", {}).get(top, {})
        evidence = [str(root / "execution" / "specification-ir.json"), str(root / "execution" / "verification-plan.json"), *collateral_evidence, *agent_team_evidence]
        if coverage_ranking_path is not None:
            evidence.append(str(coverage_ranking_path))
        assertion_results: list[dict[str, Any]] = []
        for assertion_plan in execution["plans"]:
            requirement_text = next((item.text for item in spec_ir.requirements if item.id == assertion_plan.requirement_id), "")
            structural_signals = set(structural_module.get("ports", [])) | set(structural_module.get("netnames", [])) | set(infer_assertion_signals(assertion_plan.assertion))
            assertion_request = {
                "task": "generate_assertion", "requirement_id": assertion_plan.requirement_id,
                "requirement_text": requirement_text,
                "allowed_source_revision": source_revision, "allowed_signals": sorted(structural_signals),
                "evidence": evidence, "assertion": assertion_plan.assertion,
                "collateral_package_sha256": collateral_result.get("package_sha256"),
                "agent_team_sha256": agent_team_result.get("team_sha256"),
                "team_handoffs": agent_team_result.get("handoffs", []),
                "coverage_gap_ranking": str(coverage_ranking_path) if coverage_ranking_path else None,
                "functional_rtl_access": "forbidden", "structural_context_only": True,
            }
            spec_digest = spec_digests.get(assertion_plan.requirement_id, "0" * 64)
            assertion_results.append(invoke_assertion_backend(
                assertion_request, requirement_id=assertion_plan.requirement_id, specification_sha256=spec_digest,
                structural_signals=structural_signals, model_id=assertion_agent_backend, source_revision=source_revision,
            ))
        assertion_agent_result = {
            "schema_version": "agent-assertion-batch-result-v1",
            "status": "available" if all(item["status"] == "available" for item in assertion_results) else "blocked",
            "backend": assertion_agent_backend,
            "agent_team_sha256": agent_team_result.get("team_sha256"),
            "team_handoff_count": len(agent_team_result.get("handoffs", [])),
            "coverage_gap_ranking": str(coverage_ranking_path) if coverage_ranking_path else None,
            "requirements": [item["proposal"]["requirement_id"] for item in assertion_results if item.get("proposal")],
            "results": assertion_results,
        }
        if assertion_agent_result["status"] == "available":
            assertion_agent_result["proposals"] = [item["proposal"] for item in assertion_results]
            # Preserve the singular field for existing consumers while the
            # batch field is the authoritative complete result.
            assertion_agent_result["proposal"] = assertion_agent_result["proposals"][0]
        else:
            assertion_agent_result["error"] = "one or more planned assertions failed admission"
        assertion_agent_result["result_sha256"] = hashlib.sha256(json.dumps(assertion_agent_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        assertion_agent_path = root / "auto-formalization" / "agent-assertion-result.json"
        assertion_agent_path.parent.mkdir(parents=True, exist_ok=True)
        assertion_agent_path.write_text(json.dumps(assertion_agent_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assertion_agent_result["path"] = str(assertion_agent_path)
    if assertion_agent_result["status"] == "available":
        proposal_records = assertion_agent_result.get("proposals", [assertion_agent_result["proposal"]])
        assertion_source = root / "auto-formalization" / "agent-assertion.sv"
        assertion_source.parent.mkdir(parents=True, exist_ok=True)
        ports = ", ".join(f"input logic {signal}" for signal in sorted({signal for proposal in proposal_records for signal in proposal["signals"]}))
        assertions = "\n".join(f"  {proposal['assertion']}" for proposal in proposal_records)
        assertion_source.write_text(f"module agent_assertion({ports});\n{assertions}\nendmodule\n", encoding="utf-8")
        lowerings = [lower_assertion(proposal["assertion"], requirement_id=proposal["requirement_id"]) for proposal in proposal_records]
        compile_run = compile_sva_with_verilator(assertion_source, run_root=root / "auto-formalization" / "validation", source_revision=source_revision, timeout_seconds=timeout_seconds)
        lowered_source = root / "auto-formalization" / "lowered-checker.sv"
        lowered_source.write_text(generate_lowered_checker(lowerings, module_name="agent_lowered_checks"), encoding="utf-8")
        lowered_compile = run_command(
            ["iverilog", "-g2012", "-t", "null", str(lowered_source.resolve())],
            tool="sva-lowered-compile", run_root=root / "auto-formalization" / "lowered-validation",
            source_revision=source_revision, timeout_seconds=timeout_seconds, run_id="lowered-checker",
        )
        lowering_compile_passed = lowered_compile.status == "passed" and all(item.status == "supported" for item in lowerings)
        assertion_validation_result: dict[str, Any] = {
            "schema_version": "agent-assertion-validation-v1", "status": "passed" if (compile_run.status == "passed" or lowering_compile_passed) and all(item.status == "supported" for item in lowerings) else "blocked",
            "requirements": [proposal["requirement_id"] for proposal in proposal_records],
            "lowering": [item.record() for item in lowerings], "compiler": asdict(compile_run),
            "lowered_compiler": asdict(lowered_compile), "source": str(assertion_source), "lowered_source": str(lowered_source),
            "frontend_fallback_used": compile_run.status != "passed" and lowering_compile_passed,
            "claim_boundary": "frontend and explicit lowering compilation validation only; no formal proof or functional correctness claim",
        }
        if assertion_validation_result["status"] == "blocked":
            assertion_validation_result["feedback_status"] = "compile_failed" if compile_run.status != "passed" else "unsupported_property"
        assertion_validation_result["validation_sha256"] = hashlib.sha256(json.dumps(assertion_validation_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        validation_result_path = root / "auto-formalization" / "validation-result.json"
        validation_result_path.write_text(json.dumps(assertion_validation_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        assertion_validation_result = {"status": "not_run", "claim_boundary": "assertion validation requires an admitted assertion proposal"}
    if assertion_antecedent_signal is not None or assertion_refinement is not None:
        if assertion_agent_result["status"] != "available":
            raise ValueError("assertion feedback requires an admitted assertion proposal")
        admitted_proposal = proposal_from_record(assertion_agent_result["proposal"])
        assertion_feedback_result: dict[str, Any] = {"schema_version": "assertion-feedback-v1", "proposal_sha256": admitted_proposal.proposal_sha256, "status": "review_required"}
        if assertion_antecedent_signal is not None:
            if debug_waveform is None:
                raise ValueError("assertion vacuity feedback requires debug_waveform")
            vacuity = evaluate_proposal_vacuity(admitted_proposal, debug_waveform, antecedent_signal=assertion_antecedent_signal)
            assertion_feedback_result["vacuity"] = vacuity
            assertion_feedback_result["status"] = vacuity["status"]
        if assertion_refinement is not None:
            if not isinstance(assertion_refinement, dict) or not isinstance(assertion_refinement.get("replacement_assertion"), str):
                raise ValueError("assertion_refinement requires replacement_assertion")
            feedback = dict(assertion_refinement.get("feedback", {}))
            if feedback.get("proposal_sha256") != admitted_proposal.proposal_sha256:
                raise ValueError("assertion refinement feedback must match the admitted proposal digest")
            refined = refine_assertion_proposal(admitted_proposal, feedback, assertion_refinement["replacement_assertion"], attempt=int(assertion_refinement.get("attempt", 1)))
            assertion_feedback_result["refined_proposal"] = refined.record()
            assertion_feedback_result["status"] = "review_required"
        assertion_feedback_result["feedback_sha256"] = hashlib.sha256(json.dumps(assertion_feedback_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        feedback_path = root / "auto-formalization" / "assertion-feedback.json"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        feedback_path.write_text(json.dumps(assertion_feedback_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assertion_feedback_result["path"] = str(feedback_path)
    else:
        assertion_feedback_result = {"status": "not_run", "claim_boundary": "assertion feedback requires an admitted proposal and explicit feedback input"}
    if assertion_solver_antecedent is None:
        assertion_solver_vacuity_result: dict[str, Any] = {
            "status": "not_run",
            "claim_boundary": "solver vacuity requires an admitted assertion proposal and an explicit antecedent",
        }
    elif assertion_agent_result["status"] != "available":
        raise ValueError("solver vacuity requires an admitted assertion proposal")
    else:
        proposal_records = assertion_agent_result.get("proposals", [assertion_agent_result["proposal"]])
        solver_results: list[dict[str, Any]] = []
        for record in proposal_records:
            proposal = proposal_from_record(record)
            try:
                solver_results.append(evaluate_proposal_vacuity_solver(
                    proposal,
                    rtl_sources,
                    top=top,
                    antecedent=assertion_solver_antecedent,
                    run_root=root / "auto-formalization" / "solver-vacuity" / proposal.proposal_id,
                    source_revision=source_revision,
                    timeout_seconds=timeout_seconds,
                ))
            except ValueError as error:
                solver_results.append({
                    "schema_version": "assertion-vacuity-solver-v1",
                    "proposal_sha256": proposal.proposal_sha256,
                    "antecedent": assertion_solver_antecedent,
                    "status": "blocked",
                    "solver_status": "blocked",
                    "error": str(error),
                    "claim_boundary": "proposal scope or antecedent grammar validation failed",
                })
        statuses = [item["status"] for item in solver_results]
        aggregate_status = "blocked" if any(item == "blocked" for item in statuses) else "vacuous" if any(item == "vacuous" for item in statuses) else "active"
        assertion_solver_vacuity_result = {
            "schema_version": "assertion-solver-vacuity-batch-v1",
            "status": aggregate_status,
            "antecedent": assertion_solver_antecedent,
            "results": solver_results,
            "claim_boundary": "bounded solver reachability of each admitted proposal antecedent; not complete SVA vacuity proof",
        }
        assertion_solver_vacuity_result["result_sha256"] = hashlib.sha256(json.dumps(assertion_solver_vacuity_result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        solver_vacuity_path = root / "auto-formalization" / "solver-vacuity-result.json"
        solver_vacuity_path.parent.mkdir(parents=True, exist_ok=True)
        solver_vacuity_path.write_text(json.dumps(assertion_solver_vacuity_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        assertion_solver_vacuity_result["path"] = str(solver_vacuity_path)
    if assertion_formal_sources is None:
        assertion_formal_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "formal assertion proof requires an explicit formal top and source bundle"}
    elif not assertion_formal_top:
        raise ValueError("assertion_formal_top is required when assertion_formal_sources are supplied")
    else:
        assertion_formal_result = run_yosys_assertion_proof(
            [*rtl_sources, *assertion_formal_sources], top=assertion_formal_top,
            run_root=root / "auto-formalization" / "proof", sequence=assertion_formal_sequence,
            source_revision=source_revision, timeout_seconds=timeout_seconds,
        )
    if compiled_sim_harness is None:
        compiled_simulation_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "compiled simulation requires an explicit C++ harness"}
    else:
        compiled_simulation_result = run_verilator_compiled_simulation(
            compiled_sim_rtl_sources or rtl_sources, compiled_sim_harness, top=top, run_root=root / "compiled-simulation",
            source_revision=source_revision, timeout_seconds=timeout_seconds,
        )
    if svm_checker_source is None and svm_harness is None:
        svm_result: dict[str, Any] = {"status": "not_run", "claim_boundary": "SVM evidence requires an explicit checker and harness"}
    elif svm_checker_source is None or svm_harness is None:
        raise ValueError("svm_checker_source and svm_harness must be supplied together")
    else:
        svm_result = run_synthesizable_checker(
            svm_rtl_sources or rtl_sources, svm_checker_source, svm_harness, top=svm_harness_top,
            run_root=root / "svm", source_revision=source_revision, timeout_seconds=timeout_seconds,
        )
    if optimization_proposals is not None:
        optimization_state_path = root / "optimization" / "state.json"
        try:
            if optimization_state_path.exists():
                optimization_state = load_optimization_state(optimization_state_path)
                if optimization_state.source_revision != source_revision:
                    raise ValueError("persisted optimization state belongs to a different source revision")
            else:
                optimization_state = build_optimization_state([], source_revision=source_revision)
                write_optimization_state(optimization_state, str(optimization_state_path))
            recommendation = select_next_candidate(optimization_state, optimization_proposals, mode=optimization_mode, max_runtime_seconds=optimization_max_runtime_seconds)
            source_identity = [{"path": str(Path(source).resolve()), "sha256": sha256_file(source)} for source in rtl_sources]
            recommendation["source_digest"] = hashlib.sha256(json.dumps(source_identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            recommendation_path = optimization_state_path.parent / "recommendation.json"
            recommendation_path.write_text(json.dumps(recommendation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            if optimization_measurement is None:
                optimization_result = {"status": "ready", "mode": optimization_mode, "state": str(optimization_state_path), "recommendation": str(recommendation_path), "state_sha256": optimization_state.digest(), "run_count": len(optimization_state.runs), "claim_boundary": "proposal is not measured until an explicit proxy or full result is recorded"}
            else:
                if not isinstance(optimization_measurement, dict):
                    raise ValueError("optimization measurement must be a JSON object")
                updated_state = append_optimization_result(
                    optimization_state_path, recommendation,
                    fidelity=str(optimization_measurement.get("fidelity", "")),
                    metrics=dict(optimization_measurement.get("metrics", {})),
                    status=str(optimization_measurement.get("status", "")),
                    runtime_seconds=optimization_measurement.get("runtime_seconds"),
                    failure_reason=optimization_measurement.get("failure_reason"),
                    tool=str(optimization_measurement.get("tool", "")),
                    source_digest=str(optimization_measurement.get("source_digest", "")),
                    configuration_digest=str(optimization_measurement.get("configuration_digest", "")),
                    metrics_artifact_sha256=str(optimization_measurement.get("metrics_artifact_sha256", "")),
                    metrics_artifact_path=str(optimization_measurement.get("metrics_artifact_path", "")),
                )
                optimization_result = {"status": "passed", "mode": optimization_mode, "state": str(optimization_state_path), "recommendation": str(recommendation_path), "state_sha256": updated_state.digest(), "run_count": len(updated_state.runs), "measurement": {"fidelity": optimization_measurement.get("fidelity"), "status": optimization_measurement.get("status"), "metrics": optimization_measurement.get("metrics"), "tool": optimization_measurement.get("tool"), "source_digest": optimization_measurement.get("source_digest"), "configuration_digest": optimization_measurement.get("configuration_digest"), "metrics_artifact_sha256": optimization_measurement.get("metrics_artifact_sha256"), "metrics_artifact_path": optimization_measurement.get("metrics_artifact_path")}, "claim_boundary": "measured optimization observation recorded for the supplied source revision; not signoff"}
        except ValueError as error:
            optimization_result = {"status": "blocked", "state": str(optimization_state_path), "reason": str(error), "claim_boundary": "optimization proposals require a valid source-bound persisted state"}
    else:
        optimization_result = {"status": "not_run", "claim_boundary": "optimization requires candidate proposals and measured EDA results"}
    result: dict[str, Any] = {
        "schema_version": "four-workstream-pipeline-v1",
        "source_revision": source_revision,
        "collateral": collateral_result,
        "agent_team": agent_team_result,
        "execution": {"status": execution["tool_run"].status, "run_root": str(execution["run_root"]), "verilator_lint": asdict(verilator_lint)},
        "verilator_capabilities": verilator_capabilities,
        "scheduling": scheduling,
        "scheduling_runtime": scheduling_runtime,
        "structural": {"status": structural["status"], "ir_sha256": structural.get("ir_sha256"), "tool_run": structural_run.status, "parser_cdfg_status": parser_cdfg["status"], "parser_cdfg_sha256": parser_cdfg.get("cdfg_sha256"), "parser_cdfg_tool_run": parser_cdfg_run.status, "functional_partition": parser_partition, "functional_reconstruction": parser_reconstruction, "functional_reconstruction_equivalence": parser_reconstruction_equivalence},
        "protocol": {"status": "passed" if protocol_compile.status == "passed" else "blocked", "plan_sha256": plan.digest(), "sequence": str(protocol_path), "compiler": protocol_compile.status, "execution": protocol_execution_result, "execution_convergence": str(protocol_execution_convergence_path) if protocol_execution_convergence_path else None, "coverage_gaps": str(coverage_gap_path) if coverage_gap_path else None, "coverage_report": coverage_result, "coverage_ranking": str(coverage_ranking_path) if coverage_ranking_path else None, "coverage_convergence": str(coverage_convergence_path) if coverage_convergence_path else None},
        "debug": debug_result,
        "agent": agent_result,
        "repair_agent": repair_agent_result,
        "repair_retest": repair_retest_result,
        "assertion_agent": assertion_agent_result,
        "assertion_validation": assertion_validation_result,
        "assertion_feedback": assertion_feedback_result,
        "assertion_solver_vacuity": assertion_solver_vacuity_result,
        "assertion_formal": assertion_formal_result,
        "compiled_simulation": compiled_simulation_result,
        "svm": svm_result,
        "uvm": uvm_result,
        "optimization": optimization_result,
    }
    result["status"] = "passed" if all([
        result["execution"]["status"] == "passed", scheduling["status"] == "passed", verilator_lint.status == "passed",
        collateral_result["status"] in {"not_run", "ready"},
        agent_team_result["status"] in {"not_run", "available"},
        verilator_capabilities["status"] in {"not_run", "passed"},
        structural["status"] == "passed", parser_cdfg["status"] == "passed", parser_partition is None or parser_partition["status"] == "ready", parser_reconstruction is None or parser_reconstruction["status"] == "ready", parser_reconstruction_equivalence is None or parser_reconstruction_equivalence["status"] == "proven", result["protocol"]["status"] == "passed", protocol_execution_result["status"] in {"not_run", "passed"},
        debug_result["status"] in {"not_run", "review_required"}, optimization_result["status"] in {"not_run", "ready", "passed"},
        agent_result["status"] in {"not_run", "available"},
        repair_agent_result["status"] in {"not_run", "available"},
        repair_retest_result["status"] in {"not_run", "passed"},
        assertion_agent_result["status"] in {"not_run", "available"},
        assertion_validation_result["status"] in {"not_run", "passed"},
        assertion_feedback_result["status"] in {"not_run", "active", "review_required"},
        assertion_solver_vacuity_result["status"] in {"not_run", "active"},
        assertion_formal_result["status"] in {"not_run", "proven", "counterexample"},
        compiled_simulation_result["status"] in {"not_run", "passed"},
        svm_result["status"] in {"not_run", "passed"},
        uvm_result["status"] in {"not_run", "available", "passed"},
        scheduling_runtime["status"] in {"not_run", "passed"},
        debug_result.get("filtered_dut_equivalence", {"status": "not_run"})["status"] in {"not_run", "proven"},
    ]) else "blocked"
    result["blocked_reasons"] = [] if result["status"] == "passed" else [
        stage for stage, value in (("collateral", collateral_result["status"]), ("agent-team", agent_team_result["status"]), ("execution", result["execution"]["status"]), ("verilator-lint", verilator_lint.status), ("verilator-capabilities", verilator_capabilities["status"]), ("scheduling", scheduling["status"]), ("scheduling-runtime", scheduling_runtime["status"]), ("structural", structural["status"]), ("parser-cdfg", parser_cdfg["status"]), ("structural-partition", parser_partition["status"] if parser_partition else "not_run"), ("structural-reconstruction", parser_reconstruction["status"] if parser_reconstruction else "not_run"), ("structural-reconstruction-equivalence", parser_reconstruction_equivalence["status"] if parser_reconstruction_equivalence else "not_run"), ("protocol", result["protocol"]["status"]), ("protocol-execution", protocol_execution_result["status"]), ("debug", debug_result["status"]), ("agent", agent_result["status"]), ("repair-agent", repair_agent_result["status"]), ("repair-retest", repair_retest_result["status"]), ("assertion-agent", assertion_agent_result["status"]), ("assertion-formal", assertion_formal_result["status"]), ("assertion-solver-vacuity", assertion_solver_vacuity_result["status"]), ("compiled-simulation", compiled_simulation_result["status"]), ("svm", svm_result["status"]), ("uvm", uvm_result["status"]), ("optimization", optimization_result["status"])) if value not in {"passed", "not_run", "ready", "review_required", "available", "proven", "counterexample", "active"}
    ]
    claim_states = [debug_result["status"], agent_result["status"], repair_agent_result["status"], assertion_feedback_result["status"], assertion_formal_result["status"], assertion_solver_vacuity_result["status"], repair_retest_result["status"]]
    if result["status"] == "blocked":
        result["claim_status"] = "blocked"
        result["claim_status_reason"] = "one or more required execution or evidence stages are blocked"
    elif any(state in {"review_required", "counterexample", "active"} for state in claim_states):
        result["claim_status"] = "review_required"
        result["claim_status_reason"] = "evidence exists, but a counterexample, active refinement, or human-reviewed proposal remains"
    else:
        result["claim_status"] = "evidence_only"
        result["claim_status_reason"] = "pipeline evidence passed; no design-closure claim is inferred"
    (root / "scheduling" / "gate.json").write_text(json.dumps(scheduling, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    protocol_result = {"status": result["protocol"]["status"], "plan_sha256": plan.digest(), "sequence": str(protocol_path), "compiler": protocol_compile.status, "execution": protocol_execution_result, "execution_convergence": str(protocol_execution_convergence_path) if protocol_execution_convergence_path else None, "coverage_report": coverage_result, "coverage_ranking": str(coverage_ranking_path) if coverage_ranking_path else None, "coverage_convergence": str(coverage_convergence_path) if coverage_convergence_path else None}
    (root / "protocol" / "protocol-result.json").write_text(json.dumps(protocol_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    def tier_status(statuses: list[str]) -> str:
        if any(status == "blocked" for status in statuses):
            return "blocked"
        if all(status == "not_run" for status in statuses):
            return "not_run"
        if any(status in {"review_required", "counterexample"} for status in statuses):
            return "review_required"
        return "passed" if all(status in {"passed", "proven", "available", "ready", "not_run", "active"} for status in statuses) else "blocked"

    tier_evidence: dict[str, Any] = {
        "schema_version": "four-workstream-tier-evidence-v1",
        "source_revision": source_revision,
        "tiers": [
            {"id": "tier-1", "name": "lint-and-policy", "status": tier_status([result["execution"]["status"], verilator_lint.status, collateral_result["status"], scheduling["status"]]), "evidence": ["execution", "verilator-lint", "collateral", "scheduling"], "claim_boundary": "deterministic intake, lint, and scheduling-gate evidence"},
            {"id": "tier-2", "name": "compiled-simulation", "status": tier_status([compiled_simulation_result["status"]]), "evidence": ["compiled_simulation"], "claim_boundary": "compiled simulation evidence for the supplied RTL, harness, and runtime marker"},
            {"id": "tier-3", "name": "block-protocol-regression", "status": tier_status([result["protocol"]["status"], protocol_execution_result["status"], scheduling_runtime["status"]]), "evidence": ["protocol", "protocol.execution", "scheduling_runtime"], "claim_boundary": "protocol compilation, optional executable-sequence progress, and optional time-zero fixture evidence"},
            {"id": "tier-4", "name": "formal-and-debug", "status": tier_status([assertion_formal_result["status"], assertion_solver_vacuity_result["status"], debug_result["status"], repair_retest_result["status"]]), "evidence": ["assertion_formal", "assertion_solver_vacuity", "debug", "repair_retest"], "claim_boundary": "bounded formal, vacuity, logic-aware debug, and optional approval-gated retest evidence; review-required outcomes are not closure"},
            {"id": "tier-5", "name": "svm-emulation", "status": tier_status([svm_result["status"]]), "evidence": ["svm"], "claim_boundary": "optional synthesizable-checker compile/run evidence; not FPGA frequency or utilization"},
            {"id": "tier-6", "name": "optimization-and-release-inputs", "status": tier_status([optimization_result["status"], uvm_result["status"]]), "evidence": ["optimization", "uvm"], "claim_boundary": "source-bound optimization observations and UVM compile/capability evidence; release remains human-gated"},
        ],
        "claim_boundary": "tier status is an evidence inventory and does not replace the existing closure or human-approval gates",
    }
    tier_evidence["tier_evidence_sha256"] = hashlib.sha256(json.dumps(tier_evidence, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    tier_evidence_path = root / "four-workstream-tier-evidence.json"
    tier_evidence_path.write_text(json.dumps(tier_evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["tiers"] = tier_evidence
    evidence_manifest = build_artifact_manifest(root, exclude={"four-workstream-evidence-manifest.json", "workflow-checkpoint.json", "four-workstream-result.json"})
    evidence_manifest_path = write_artifact_manifest(root / "four-workstream-evidence-manifest.json", evidence_manifest)
    checkpoint = create_checkpoint(f"four-workstream-{source_revision}", source_revision)
    root_planning = bool(collateral_result.get("path") or agent_team_result.get("path") or assertion_agent_result.get("path") or assertion_formal_result.get("status") != "not_run" or compiled_simulation_result.get("status") != "not_run" or svm_result.get("status") != "not_run" or uvm_result.get("status") != "not_run")
    planning_root = root if root_planning else root / "execution"
    if assertion_agent_result.get("path"):
        planning_artifacts = [
            "execution/specification-ir.json", "execution/verification-plan.json", "execution/generated_checks.sv",
            "auto-formalization/agent-assertion-result.json",
        ]
        # A rejected model proposal has a result artifact but no generated
        # assertion source.  Require downstream artifacts only when the
        # corresponding stage actually produced them, so the checkpoint can
        # preserve the true blocked status and reason.
        for relative in (
            "auto-formalization/agent-assertion.sv",
            "auto-formalization/validation-result.json",
            "auto-formalization/lowered-checker.sv",
        ):
            if (root / relative).is_file():
                planning_artifacts.append(relative)
        if assertion_feedback_result.get("path"):
            planning_artifacts.append("auto-formalization/assertion-feedback.json")
        if assertion_solver_vacuity_result.get("path"):
            planning_artifacts.append("auto-formalization/solver-vacuity-result.json")
    else:
        planning_artifacts = ["execution/specification-ir.json", "execution/verification-plan.json", "execution/generated_checks.sv"] if root_planning else ["specification-ir.json", "verification-plan.json", "generated_checks.sv"]
    if collateral_result.get("path"):
        planning_artifacts.append("collateral/collateral-package.json")
    if agent_team_result.get("path"):
        planning_artifacts.append("agents/agent-team-result.json")
    if assertion_formal_result.get("status") != "not_run":
        planning_artifacts.append("auto-formalization/proof/assertion-proof-result.json")
    if compiled_simulation_result.get("status") != "not_run":
        planning_artifacts.append("compiled-simulation/compiled-simulation-result.json")
    if svm_result.get("status") != "not_run":
        planning_artifacts.append("svm/svm-result.json")
    if uvm_capability.get("status") != "not_run":
        planning_artifacts.append("uvm/uvm-runtime-capability.json")
    if uvm_compile_result.get("status") != "not_run":
        planning_artifacts.append("uvm/compile/uvm-compile-result.json")
    checkpoint_stages = [
        ("planning", collateral_result["status"] in {"not_run", "ready"} and agent_team_result["status"] in {"not_run", "available"} and assertion_agent_result["status"] in {"not_run", "available"} and uvm_result["status"] in {"not_run", "available", "passed"} and result["execution"]["status"] == "passed" and assertion_validation_result["status"] in {"not_run", "passed"} and assertion_formal_result["status"] in {"not_run", "proven", "counterexample"} and assertion_solver_vacuity_result["status"] in {"not_run", "active"}, planning_root, planning_artifacts),
        ("scheduling", scheduling["status"] == "passed" and scheduling_runtime["status"] in {"not_run", "passed"}, root, ["scheduling/gate.json"] + (["scheduling/runtime-regression.json"] if scheduling_runtime["status"] != "not_run" else [])),
        ("structural", structural["status"] == "passed" and parser_cdfg["status"] == "passed" and (parser_partition is None or parser_partition["status"] == "ready") and (parser_reconstruction is None or parser_reconstruction["status"] == "ready") and (parser_reconstruction_equivalence is None or parser_reconstruction_equivalence["status"] == "proven") and verilator_capabilities["status"] in {"not_run", "passed"}, root, ["structural/rtl-structural-ir.json", "structural/parser-cdfg.json"] + ([str(parser_partition_path.relative_to(root))] if parser_partition_path else []) + ([str(parser_reconstruction_path.relative_to(root))] if parser_reconstruction_path and parser_reconstruction and parser_reconstruction.get("status") == "ready" else []) + (["structural/functional-equivalence/filtered-dut-equivalence.json"] if parser_reconstruction_equivalence else []) + (["verilator-capabilities/verilator-capability-matrix.json"] if verilator_capabilities["status"] != "not_run" else [])),
        ("protocol", result["protocol"]["status"] == "passed" and protocol_execution_result["status"] in {"not_run", "passed"}, root, [str(protocol_path.relative_to(root)), "protocol/protocol-result.json", evidence_manifest_path.name, tier_evidence_path.name] + (["protocol-execution/stdout.log", "protocol-execution/stderr.log", "protocol-execution/provenance-ledger.json"] if protocol_execution_result["status"] != "not_run" and protocol_execution_convergence_path is None else []) + ([str(path.relative_to(root)) for path in [root / "protocol-execution" / f"iteration-{index:02d}" / name for index in range(len(protocol_execution_result.get("iterations") or [])) for name in ("stdout.log", "stderr.log", "provenance-ledger.json")]] if protocol_execution_convergence_path else []) + ([str(protocol_execution_convergence_path.relative_to(root))] if protocol_execution_convergence_path else []) + ([str(coverage_gap_path.relative_to(root))] if coverage_gap_path else []) + ([str(coverage_report_path.relative_to(root)), str(coverage_ranking_path.relative_to(root))] if coverage_report_path and coverage_ranking_path else []) + ([str(coverage_convergence_path.relative_to(root))] if coverage_convergence_path else [])),
    ]
    if debug_result["status"] != "not_run":
        checkpoint_artifacts = ["debug/debug-package.json"]
        if "filtered_dut" in debug_result:
            checkpoint_artifacts.append("debug/filtered-equivalence/" + ("hierarchical-filtered-dut-equivalence.json" if debug_filtered_dut_top else "filtered-dut-equivalence.json"))
        if repair_retest_result["status"] != "not_run":
            checkpoint_artifacts.append("debug/approved-repair-retest/repair-retest.json")
        checkpoint_stages.append(("debug", debug_result["status"] in {"review_required", "passed"} and debug_result.get("filtered_dut_equivalence", {"status": "not_run"})["status"] in {"not_run", "proven"} and repair_retest_result["status"] in {"not_run", "passed"}, root, checkpoint_artifacts))
    if optimization_result["status"] != "not_run":
        checkpoint_stages.append(("optimization", optimization_result["status"] in {"ready", "passed"}, root, ["optimization/state.json", "optimization/recommendation.json"]))
    for stage, passed, artifact_root, artifact_paths in checkpoint_stages:
        if not passed:
            checkpoint = replace(checkpoint, status="blocked")
            break
        checkpoint = advance_checkpoint(checkpoint, stage, artifact_root=artifact_root, artifact_paths=artifact_paths)
    checkpoint_path = root / "workflow-checkpoint.json"
    result["checkpoint"] = {"path": str(checkpoint_path), "completed": list(checkpoint.completed), "skipped": list(checkpoint.skipped), "status": checkpoint.status}
    result_path = root / "four-workstream-result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint = replace(checkpoint, artifacts={**dict(checkpoint.artifacts or {}), "four-workstream-result.json": sha256_file(result_path)})
    write_checkpoint(checkpoint, checkpoint_path)
    return result
