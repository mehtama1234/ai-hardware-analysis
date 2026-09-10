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
from .formal import counterexample_to_failure, parse_yosys_counterexample, parse_yosys_sat_result, yosys_sat_prove, yosys_syntax_check
from .generator import generate_sva_module, write_sva_module
from .pipeline import run_pipeline
from .clustering import cluster_failures
from .logic import dependency_cone
from .sva import compile_sva_with_iverilog, compile_sva_with_verilator
from .uvm import generate_uvm_agent, write_uvm_agent
from .policy import Action, authorize
from .claims import Claim, claim_status
from .regression import run_regression, write_regression_report
from .procedural import generate_procedural_checker, write_procedural_checker
from .repair import RepairProposal, apply_to_copy, propose_enable_guard
from .mixed_signal import CollateralEntry, build_mixed_signal_manifest, write_mixed_signal_manifest
from .session import SessionEvent, VerificationSession
from .capabilities import ToolCapability, discover_capabilities, write_capabilities
from .rtl import ingest_rtl_ports, write_rtl_inventory
from .retrieval import build_retrieval_index, retrieve, write_retrieval_index
from .artifacts import ArtifactRecord, build_artifact_manifest, verify_artifact_manifest, write_artifact_manifest
from .actions import recommend_next_action
from .adapter import AdapterSpec, execute_adapter

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
    "compile_sva_with_iverilog",
    "compile_sva_with_verilator",
    "generate_uvm_agent",
    "write_uvm_agent",
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
    "AdapterSpec",
    "execute_adapter",
]
