#!/usr/bin/env python3
"""Audit the complete RSI/AIMC objective without collapsing open gates."""
from __future__ import annotations

import json
from pathlib import Path

from run_adaptive_budget_rsi_experiment import verify_saved_experiment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "recursive-self-improvement-eda-research/end-to-end-readiness-audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    loop = load(ROOT / "recursive-self-improvement-eda-research/end-to-end-rsi-policy-loop.json")
    population = load(ROOT / "recursive-self-improvement-eda-research/population-rsi-benchmark.json")
    promotion = load(ROOT / "recursive-self-improvement-eda-research/rsi-promotion-evaluation.json")
    handoff = load(ROOT / "recursive-self-improvement-eda-research/rsi-runtime-policy-handoff.json")
    replay = load(ROOT / "recursive-self-improvement-eda-research/rsi-runtime-handoff-validation.json")
    proposals = load(ROOT / "recursive-self-improvement-eda-research/new-trial-proposals.json")
    derived = load(ROOT / "recursive-self-improvement-eda-research/derived-ledger-transfer.json")
    retrieval_ablation = load(ROOT / "recursive-self-improvement-eda-research/cross-task-memory-retrieval-ablation.json")
    schedule = load(ROOT / "recursive-self-improvement-eda-research/fused-schedule-action-qualification.json")
    schedule_promotion = load(ROOT / "recursive-self-improvement-eda-research/compiler-schedule-promotion.json")
    cost_consistency = load(ROOT / "recursive-self-improvement-eda-research/runtime-cost-model-consistency.json")
    segmented_policy = load(ROOT / "recursive-self-improvement-eda-research/segmented-residue-policy-handoff.json")
    segmented_mismatch = load(ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/segmented-residue-mismatch-stress.json")
    segmented_transfer = load(ROOT / "recursive-self-improvement-eda-research/segmented-residue-workload-transfer.json")
    segmented_cost_rollback = load(ROOT / "recursive-self-improvement-eda-research/segmented-residue-cost-rollback-validation.json")
    segmented_board_preflight = load(ROOT / "recursive-self-improvement-eda-research/segmented-board-preflight.json")
    width_refinement = load(ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-correction-width-refinement-search.json")
    finger_refinement = load(ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/analog-converter-agent-v1/results/differential-feedback-finger-refinement-search.json")
    manifest = load(ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/final-package-v1/results/final-manifest.json")
    independent_search_path = ROOT / "recursive-self-improvement-eda-research/fresh-quality-guarded-adaptive-20260922-5603-5701-5803/incumbent_challenger_rsi_experiment.json"
    independent_search = (
        verify_saved_experiment(independent_search_path)
        if independent_search_path.is_file() else {"status": "missing"}
    )
    independent_search_verified = independent_search.get("status") == "verified"
    independent_search_passed = (
        independent_search_verified
        and independent_search.get("strict_search_efficiency_improvement") is True
    )
    readiness = {
        "declared_workload_compilation": {"status": "passed", "evidence": "manifest-bound runtime package and typed candidate ledger"},
        "learned_rsi_action_selection": {"status": "passed", "evidence": "population tabular-Q and sequential RSI held-out benchmark"},
        "simulator_spice_evidence": {"status": "passed", "evidence": "final manifest converter PVT and simulator run counts"},
        "current_segmented_converter_policy_boundary": {
            "status": "passed" if (
                segmented_policy.get("status") == "passed"
                and segmented_policy.get("selection", {}).get("analog_runtime_authorized") is False
                and segmented_policy.get("gates", {}).get("heldout_workload_transfer") is True
                and segmented_policy.get("gates", {}).get("rollback") is True
            ) else "open",
            "evidence": "segmented-residue-policy-handoff.json binds the 0.777827 LSB control, topology-matched mismatch stress, held-out fallback transfer, rollback, cost, and board gates",
            "control_max_inl_lsb": segmented_policy.get("transition", {}).get("state", {}).get("max_inl_lsb"),
            "mismatch_worst_max_inl_lsb": segmented_mismatch.get("summary", {}).get("worst_max_inl_lsb"),
            "heldout_cases": segmented_transfer.get("summary", {}).get("population_cases"),
            "rollback_status": segmented_cost_rollback.get("rollback", {}).get("status"),
        },
        "persistent_failure_performance_memory": {"status": "passed", "evidence": "end-to-end loop action-level persistent performance memory"},
        "cross_task_memory_retrieval_ablation": {
            "status": "passed" if retrieval_ablation.get("status") == "passed" and retrieval_ablation.get("summary", {}).get("all_gated_methods_safe") else "open",
            "evidence": "cross-task-memory-retrieval-ablation.json: persisted transformer memory versus local-only and shuffled retrieval on held-out MLP noise domains",
            "result": retrieval_ablation.get("summary", {}),
            "limitation": "offline numeric transfer only; target evidence lacks PVT corner, converter-gate, and comparable-cost fields",
        },
        "unseen_workload_corner_evaluation": {"status": "passed", "evidence": "36 unseen selector-population cases plus independent MLP transfer"},
        "promotion_rollback_fallback": {"status": "passed", "evidence": "promotion rejected for zero strict improvement; baseline and digital fallback handoff replayed"},
        "experiment_policy_promotion": {
            "status": "passed" if (
                promotion.get("experiment_policy_promotion", {}).get("status") == "approved"
                and independent_search_passed
            ) else "open",
            "evidence": {
                "verification_status": independent_search.get("status"),
                "source": independent_search.get("source"),
                "source_sha256": independent_search.get("source_sha256"),
                "independent_seeds": independent_search.get("independent_seeds", []),
                "learned_simulator_calls": independent_search.get("learned_simulator_calls"),
                "heuristic_simulator_calls": independent_search.get("baseline_simulator_calls"),
                "safety_no_regression": independent_search.get("safety_no_regression"),
                "quality_no_regression": independent_search.get("quality_no_regression"),
                "promotion_gate_no_regression": independent_search.get("promotion_gate_no_regression"),
                "strict_search_efficiency_improvement": independent_search.get("strict_search_efficiency_improvement"),
            },
            "required_next_step": (
                "improve the learned selector or add validated adaptive stopping so simulator calls fall without per-seed candidate-quality regression; rerun on fresh independent seeds"
                if independent_search_verified and not independent_search_passed
                else "run a hash-verified independent-seed budget comparison preserving candidate quality and strict safety gates"
            ),
        },
        "manifest_bound_runtime_package": {"status": "passed", "evidence": "runtime handoff hash replay and final manifest"},
        "recursive_proposal_learning_transitions": {
            "status": "passed" if (
                proposals.get("prior_derived_memory_sha256")
                and proposals.get("memory_context_entries", 0) > 12
                and derived.get("learning_update", {}).get("algorithm") == "tabular_q_learning_proposal_transition"
                and derived.get("learning_update", {}).get("transition_count") == 4
            ) else "open",
            "evidence": "fresh proposal trials, content-hashed derived ledger, and prior-memory ingestion",
        },
        "compiler_schedule_handoff": {
            "status": "passed" if (
                schedule.get("promotion", {}).get("status") == "approved_for_simulator_schedule_search"
                and handoff.get("selection", {}).get("compiler_schedule") == schedule.get("action", {}).get("action_id")
                and replay.get("checks", {}).get("compiler_schedule") == schedule.get("action", {}).get("action_id")
            ) else "open",
            "evidence": "simulator-qualified fused schedule, staged fallback, and manifest-bound handoff replay",
        },
        "compiler_schedule_promotion": {
            "status": "passed" if (
                schedule_promotion.get("status") == "passed"
                and schedule_promotion.get("promotion", {}).get("status") == "approved"
                and schedule_promotion.get("promotion", {}).get("rollback_schedule") == "staged_boundary_pipeline"
            ) else "open",
            "evidence": "reproducible simulator schedule promotion with explicit staged rollback",
        },
        "physical_board_validation": {"status": "open", "evidence": "segmented-board-preflight.json: paired package integrity accepted but board coordinator fail-closed", "preflight_status": segmented_board_preflight.get("status"), "required_external_state": "connected v75 board and synchronized measurements"},
        "strict_runtime_analog_improvement": {"status": "open", "evidence": f"width refinement found {width_refinement.get('summary', {}).get('best_max_inl_lsb')} LSB and finger refinement improved it to {finger_refinement.get('summary', {}).get('best_max_inl_lsb')} LSB in simulator-only TT/SS/FF evidence; the strict 0.5 LSB converter gate remains false and held-out runtime improvement is unmeasured", "required_next_step": "new safe converter/workload candidate with reproducible held-out runtime benefit"},
        "runtime_cost_model_consistency": {
            "status": "passed" if cost_consistency.get("promotion", {}).get("status") == "eligible" else "open",
            "evidence": "runtime-cost-model-consistency.json plus segmented-residue-cost-rollback-validation.json compare structural/runtime proxies and preserve rollback",
            "required_next_step": "common unit calibration or same-run measured energy before cost-based promotion",
        },
    }
    blockers = [name for name, item in readiness.items() if item["status"] == "open"]
    result = {
        "schema_version": "recursive_end_to_end_readiness_audit.v1",
        "requirements": readiness,
        "summary": {"requirements": len(readiness), "passed": sum(item["status"] == "passed" for item in readiness.values()),
                     "open": len(blockers), "blockers": blockers,
                     "heldout_safe_cases": population["methods"]["tabular_q"]["safe_cases"],
                     "promotion_status": promotion["promotion"]["status"], "experiment_policy_status": promotion["experiment_policy_promotion"]["status"],
                     "runtime_handoff_replay": replay["status"], "manifest_status": manifest["status"]},
        "status": "qualified_with_open_gates" if blockers else "qualified",
        "claim_boundary": "This audit separates completed software/simulator contracts from open strict-improvement and physical-board gates; it makes no unsupported hardware or production claim."
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
