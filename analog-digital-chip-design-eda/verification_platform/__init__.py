"""Evidence-backed verification platform primitives."""

from .ir import EvidenceRef, Requirement, VerificationIR
from .ledger import ProvenanceLedger, ToolRun, evidence_for, sha256_file
from .runner import run_command
from .triage import Failure, failure_to_ir, locate_source_marker, parse_failure
from .ingest import ingest_markdown
from .planner import CheckPlan, plan_ir, plan_requirement, planning_summary, write_plan
from .closure import ClosureResult, evaluate_closure, write_closure
from .pov import build_pov_report, verify_pov_digest, write_pov_report
from .coverage import CoverageResult, parse_coverage, rank_coverage_gaps, write_coverage
from .waveform import assess_vacuity, compare_traces, signal_values, waveform_contains
from .formal import counterexample_to_failure, generate_assertion_wrapper, parse_yosys_counterexample, parse_yosys_sat_result, run_yosys_antecedent_reachability, run_yosys_assertion_proof, run_yosys_inductive_proof, run_yosys_signal_reachability, yosys_sat_prove, yosys_syntax_check
from .generator import generate_sva_module, write_sva_module
from .pipeline import run_pipeline
from .clustering import cluster_failures
from .logic import dependency_cdfg, dependency_cone, dependency_graph, dependency_locations, dependency_paths
from .lowering import LoweredProperty, generate_lowered_checker, lower_assertion, lower_plans, write_lowering_manifest
from .registers import Register, RegisterField, RegisterShadow, RegisterSpec, generate_c_header, generate_register_rtl, generate_scoreboard, generate_uvm_ral_model, load_ipxact_spec, load_register_spec, load_systemrdl_spec, verify_register_bundle, write_register_bundle
from .causal import TraceEvent, bind_frontier_to_causal_graph, build_causal_graph, build_causal_timeline, causal_graph_from_vcd, rank_frontier_root_causes, state_frontier, trace_events, verify_causal_graph, verify_causal_timeline, write_causal_graph
from .diagnosis import BalancedDiagnosis, build_balanced_diagnosis, write_balanced_diagnosis
from .hypothesis import build_competing_hypotheses
from .alignment import Alignment, align_signals, aligned_state_frontier, write_alignment
from .alignment import align_cdfg_signals
from .scheduling import SchedulingFinding, lint_time_zero, run_scheduling_gate, run_time_zero_regression, write_time_zero_lint
from .rtl_ast import extract_parser_cdfg, extract_structural_ir, partition_parser_cdfg, partition_structural_ir, reconstruct_functional_partition, run_functional_equivalence, verify_functional_partition_reconstruction, verify_parser_cdfg_partition, verify_structural_ir, verify_structural_partitions
from .autoformalize import AssertionProposal, candidate_from_counterexample, evaluate_proposal_vacuity, evaluate_proposal_vacuity_solver, infer_assertion_signals, invoke_assertion_backend, proposal_from_agent_payload, proposal_from_plan, proposal_from_record, refine_assertion_proposal, write_assertion_proposals
from .sva import compile_sva_with_iverilog, compile_sva_with_verilator
from .uvm import generate_uvm_agent, probe_uvm_runtime, run_uvm_compile, write_uvm_agent
from .agent import AgentProposal, validate_agent_proposal
from .reference_agent import propose_failure_diagnosis
from .policy import Action, authorize
from .repair import build_repair_patch_candidate
from .svm import run_synthesizable_checker
from .coroutine_scheduler import EmitEvent, WaitCycles, WaitEvent, run_cooperative_scheduler
from .cpp_coroutine import run_cpp_coroutine_probe
from .claims import Claim, claim_status
from .regression import run_regression, write_regression_report
from .procedural import generate_procedural_checker, write_procedural_checker
from .repair import RepairProposal, apply_to_copy, propose_enable_guard, run_approved_repair_retest
from .debug import build_replay_slice
from .mixed_signal import CollateralEntry, build_mixed_signal_manifest, write_mixed_signal_manifest
from .session import SessionEvent, VerificationSession
from .capabilities import ToolCapability, discover_capabilities, write_capabilities
from .rtl import ingest_rtl_ports, write_rtl_inventory
from .retrieval import build_retrieval_index, retrieve, write_retrieval_index
from .artifacts import ArtifactRecord, build_artifact_manifest, verify_artifact_manifest, write_artifact_manifest
from .actions import recommend_next_action
from .closure_lab import NextTestPlan, propose_next_test
from .adapter import AdapterSpec, execute_adapter
from .protocol import ProtocolPlan, ProtocolStep, augment_protocol_plan, generate_protocol_sequence, load_protocol_plan, write_protocol_sequence
from .optimization import OptimizationRun, OptimizationState, append_optimization_result, build_optimization_state, decide_fidelity_promotion, load_openlane_metrics, load_optimization_state, record_optimization_result, run_fidelity_command, select_next_candidate, verify_optimization_state, write_optimization_state
from .orchestration import run_four_workstream_pipeline
from .debug import analyze_failure, generate_filtered_dut, generate_hierarchical_filtered_dut, prove_filtered_dut_equivalence, prove_hierarchical_filtered_dut_equivalence, write_debug_package
from .workflow import WorkflowCheckpoint, advance_checkpoint, create_checkpoint, load_checkpoint, promote_checkpoint_to_release, resume_checkpoint, verify_four_workstream_release_inputs, write_checkpoint
from .compiled_sim import run_verilator_compiled_simulation
from .repository_benchmark import RepositoryTaskResult, evaluate_task_result, file_digest, repository_snapshot, run_repository_task, validate_task_manifest
from .mutation import MutationResult, run_mutation, summarize_mutations, validate_mutation_suite
from .coverage_closure import bound_coverage_snapshot, compare_coverage
from .proof_closure import build_assumption_audit, evaluate_proof_closure
from .security_closure import evaluate_security_task, validate_security_suite
from .repository_agent import build_repository_agent_requests, run_repository_agent
from .proof_agent import build_proof_agent_requests, run_proof_agent
from .simulation import probe_verilator_capability_matrix, probe_verilator_options
from .collateral import build_collateral_package, verify_collateral_package, write_collateral_package
from .agent_team import run_agent_team

__all__ = [
    "EvidenceRef",
    "Requirement",
    "VerificationIR",
    "ProvenanceLedger",
    "ToolRun",
    "evidence_for",
    "sha256_file",
    "run_command",
    "Failure",
    "failure_to_ir",
    "parse_failure",
    "locate_source_marker",
    "ingest_markdown",
    "CheckPlan",
    "plan_ir",
    "plan_requirement",
    "write_plan",
    "planning_summary",
    "ClosureResult",
    "evaluate_closure",
    "write_closure",
    "build_pov_report",
    "write_pov_report",
    "verify_pov_digest",
    "CoverageResult",
    "parse_coverage",
    "write_coverage",
    "rank_coverage_gaps",
    "signal_values",
    "waveform_contains",
    "assess_vacuity",
    "compare_traces",
    "yosys_syntax_check",
    "yosys_sat_prove",
    "parse_yosys_sat_result",
    "parse_yosys_counterexample",
    "counterexample_to_failure",
    "generate_sva_module",
    "write_sva_module",
    "run_pipeline",
    "cluster_failures",
    "dependency_cone",
    "dependency_cdfg",
    "dependency_graph",
    "dependency_locations",
    "dependency_paths",
    "LoweredProperty",
    "lower_assertion",
    "lower_plans",
    "generate_lowered_checker",
    "write_lowering_manifest",
    "Register",
    "RegisterField",
    "RegisterSpec",
    "load_register_spec",
    "load_ipxact_spec",
    "generate_register_rtl",
    "generate_c_header",
    "generate_uvm_ral_model",
    "write_register_bundle",
    "verify_register_bundle",
    "TraceEvent",
    "trace_events",
    "build_causal_graph",
    "causal_graph_from_vcd",
    "bind_frontier_to_causal_graph",
    "rank_frontier_root_causes",
    "build_causal_timeline",
    "verify_causal_timeline",
    "state_frontier",
    "write_causal_graph",
    "verify_causal_graph",
    "BalancedDiagnosis",
    "build_balanced_diagnosis",
    "write_balanced_diagnosis",
    "build_competing_hypotheses",
    "Alignment",
    "align_signals",
    "aligned_state_frontier",
    "write_alignment",
    "SchedulingFinding",
    "lint_time_zero",
    "write_time_zero_lint",
    "run_scheduling_gate",
    "run_time_zero_regression",
    "extract_structural_ir",
    "extract_parser_cdfg",
    "partition_structural_ir",
    "reconstruct_functional_partition",
    "run_functional_equivalence",
    "verify_functional_partition_reconstruction",
    "verify_parser_cdfg_partition",
    "verify_structural_ir",
    "verify_structural_partitions",
    "AssertionProposal",
    "infer_assertion_signals",
    "proposal_from_plan",
    "proposal_from_agent_payload",
    "invoke_assertion_backend",
    "proposal_from_record",
    "write_assertion_proposals",
    "refine_assertion_proposal",
    "evaluate_proposal_vacuity",
    "evaluate_proposal_vacuity_solver",
    "candidate_from_counterexample",
    "compile_sva_with_iverilog",
    "compile_sva_with_verilator",
    "generate_uvm_agent",
    "write_uvm_agent",
    "AgentProposal",
    "validate_agent_proposal",
    "propose_failure_diagnosis",
    "Action",
    "authorize",
    "Claim",
    "claim_status",
    "run_regression",
    "write_regression_report",
    "generate_procedural_checker",
    "write_procedural_checker",
    "RepairProposal",
    "propose_enable_guard",
    "apply_to_copy",
    "run_approved_repair_retest",
    "build_replay_slice",
    "generate_filtered_dut",
    "generate_hierarchical_filtered_dut",
    "prove_filtered_dut_equivalence",
    "prove_hierarchical_filtered_dut_equivalence",
    "CollateralEntry",
    "build_mixed_signal_manifest",
    "write_mixed_signal_manifest",
    "SessionEvent",
    "VerificationSession",
    "ToolCapability",
    "discover_capabilities",
    "write_capabilities",
    "ingest_rtl_ports",
    "write_rtl_inventory",
    "build_retrieval_index",
    "retrieve",
    "write_retrieval_index",
    "ArtifactRecord",
    "build_artifact_manifest",
    "write_artifact_manifest",
    "verify_artifact_manifest",
    "recommend_next_action",
    "NextTestPlan",
    "propose_next_test",
    "AdapterSpec",
    "execute_adapter",
    "ProtocolPlan",
    "ProtocolStep",
    "augment_protocol_plan",
    "generate_protocol_sequence",
    "load_protocol_plan",
    "write_protocol_sequence",
    "build_collateral_package",
    "verify_collateral_package",
    "write_collateral_package",
    "run_agent_team",
    "OptimizationRun",
    "OptimizationState",
    "append_optimization_result",
    "build_optimization_state",
    "select_next_candidate",
    "decide_fidelity_promotion",
    "record_optimization_result",
    "run_fidelity_command",
    "load_openlane_metrics",
    "load_optimization_state",
    "verify_optimization_state",
    "write_optimization_state",
    "run_four_workstream_pipeline",
    "analyze_failure",
    "write_debug_package",
    "WorkflowCheckpoint",
    "create_checkpoint",
    "advance_checkpoint",
    "load_checkpoint",
    "resume_checkpoint",
    "promote_checkpoint_to_release",
    "verify_four_workstream_release_inputs",
    "write_checkpoint",
    "run_yosys_assertion_proof",
    "run_yosys_inductive_proof",
    "generate_assertion_wrapper",
    "run_yosys_signal_reachability",
    "run_yosys_antecedent_reachability",
    "run_verilator_compiled_simulation",
    "probe_verilator_options",
    "RepositoryTaskResult",
    "file_digest",
    "repository_snapshot",
    "validate_task_manifest",
    "evaluate_task_result",
    "run_repository_task",
    "MutationResult",
    "run_mutation",
    "summarize_mutations",
    "validate_mutation_suite",
    "bound_coverage_snapshot",
    "compare_coverage",
    "evaluate_proof_closure",
    "build_assumption_audit",
    "evaluate_security_task",
    "validate_security_suite",
    "build_repository_agent_requests",
    "run_repository_agent",
    "build_proof_agent_requests",
    "run_proof_agent",
]
