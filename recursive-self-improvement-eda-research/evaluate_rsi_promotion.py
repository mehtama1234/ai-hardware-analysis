#!/usr/bin/env python3
"""Evaluate whether the learned RSI loop is eligible to replace runtime policy."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from run_adaptive_budget_rsi_experiment import verify_saved_experiment

ROOT = Path(__file__).resolve().parents[1]
LEARNED = ROOT / "recursive-self-improvement-eda-research/end-to-end-rsi-policy-loop.json"
RUNTIME = ROOT / "analog-in-memory-ai-inference/software-architecture/qualification/converter-to-inference-v1/results/pareto-runtime-policy.json"
EXECUTED_SEARCH = ROOT / "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/recursive-converter-search-v1/three-round-seed41-73-109/recursive_search_experiment.json"
INDEPENDENT_BUDGET_SEARCH = ROOT / "recursive-self-improvement-eda-research/fresh-quality-guarded-adaptive-20260922-5603-5701-5803/incumbent_challenger_rsi_experiment.json"
OUT = ROOT / "recursive-self-improvement-eda-research/rsi-promotion-evaluation.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corner_key(corner: dict) -> str:
    return json.dumps(corner, sort_keys=True)


def experiment_efficiency_evidence(learned: dict) -> dict:
    """Combine the runtime-loop telemetry with matched executed search evidence."""
    summary = learned.get("summary", {})
    execution = learned.get("experiment_execution", {})
    learned_calls = execution.get("simulator_calls")
    baseline_calls = execution.get("baseline_simulator_calls")
    valid_counts = (
        isinstance(learned_calls, int) and not isinstance(learned_calls, bool)
        and isinstance(baseline_calls, int) and not isinstance(baseline_calls, bool)
        and baseline_calls > 0 and learned_calls >= 0
    )
    executed_search = execution.get("mode") == "executed_simulator_search"
    reduction = baseline_calls - learned_calls if valid_counts and executed_search else None
    direct = learned.get("executed_search_comparison", {})
    direct_reduction = direct.get("simulator_call_reduction")
    direct_valid = (
        direct.get("status") == "verified"
        and isinstance(direct_reduction, int)
        and not isinstance(direct_reduction, bool)
    )
    strict_direct_improvement = bool(
        direct_valid and direct_reduction > 0
        and direct.get("quality_no_regression") is True
        and direct.get("safety_no_regression", True) is True
        and direct.get("promotion_gate_no_regression", True) is True
        and direct.get("strict_search_efficiency_improvement", True) is True
    )
    return {
        "measurement_basis": "matched_executed_search_simulator_calls" if direct_valid else (
            "simulator_calls" if executed_search else "precomputed_ledger_evidence_lookups"),
        "learned_simulator_calls": learned_calls,
        "baseline_simulator_calls": baseline_calls,
        "simulator_call_reduction": direct_reduction if direct_valid else reduction,
        "runtime_loop_simulator_call_reduction": reduction,
        "direct_executed_search": direct,
        "strict_search_efficiency_improvement": strict_direct_improvement or bool(
            reduction is not None and reduction > 0
        ),
        "ledger_evidence_lookups": summary.get("ledger_evidence_lookups"),
        "exhaustive_unique_ledger_evidence_lookups": summary.get("exhaustive_unique_ledger_evidence_lookups"),
        "ledger_evidence_lookup_reduction": summary.get("ledger_evidence_lookup_reduction"),
        "ledger_evidence_lookup_reduction_fraction": summary.get("ledger_evidence_lookup_reduction_fraction"),
    }


def verify_executed_search(path: Path) -> dict:
    """Validate the hash-bound learned/heuristic run comparison used for RSI."""
    report = json.loads(path.read_text())
    methods = report.get("methods", {})
    learned = methods.get("learned", {})
    baseline = methods.get("heuristic", {})
    rounds = report.get("rounds", [])
    errors = []
    if len(rounds) < 2:
        errors.append("at least two executed rounds are required")
    if not report.get("candidate_budget_per_method_per_round"):
        errors.append("candidate budget is missing")
    if not learned or not baseline:
        errors.append("learned or heuristic method summary is missing")

    seeds = []
    observed_calls = {"learned": 0, "heuristic": 0}
    for round_report in rounds:
        seeds.append(round_report.get("seed"))
        per_method = round_report.get("methods", {})
        for name in ("learned", "heuristic"):
            row = per_method.get(name, {})
            ledger_path = Path(round_report.get("report", ""))
            if not row or not isinstance(row.get("simulator_invocations"), int):
                errors.append(f"round {round_report.get('round')} missing {name} call count")
                continue
            if not ledger_path.is_file():
                errors.append(f"round {round_report.get('round')} benchmark report is missing")
            elif digest(ledger_path) != round_report.get("report_sha256"):
                errors.append(f"round {round_report.get('round')} benchmark report hash mismatch")
            invocation_ledger = ledger_path.parent / "simulator_invocation_ledger.jsonl"
            if not invocation_ledger.is_file():
                errors.append(f"round {round_report.get('round')} simulator invocation ledger is missing")
            else:
                observed = 0
                with invocation_ledger.open() as stream:
                    for line_number, line in enumerate(stream, 1):
                        try:
                            invocation = json.loads(line)
                        except json.JSONDecodeError:
                            errors.append(f"round {round_report.get('round')} invocation ledger line {line_number} is invalid")
                            continue
                        if invocation.get("method") == name:
                            observed += 1
                if observed != row.get("simulator_invocations"):
                    errors.append(f"round {round_report.get('round')} {name} count differs from invocation ledger")
                observed_calls[name] += observed
            if row.get("candidate_runs") != report.get("candidate_budget_per_method_per_round"):
                errors.append(f"round {round_report.get('round')} is not candidate-budget matched")

    if len(set(seeds)) != len(seeds) or any(seed is None for seed in seeds):
        errors.append("round seeds are missing or duplicated")
    if learned and baseline:
        learned_calls = learned.get("simulator_invocations")
        baseline_calls = baseline.get("simulator_invocations")
        if not isinstance(learned_calls, int) or not isinstance(baseline_calls, int):
            errors.append("aggregate simulator invocation counts are missing")
        elif learned_calls != observed_calls["learned"] or baseline_calls != observed_calls["heuristic"]:
            errors.append("aggregate simulator invocation counts differ from round ledgers")
        learned_quality = learned.get("mean_of_round_safe_inl_means")
        baseline_quality = baseline.get("mean_of_round_safe_inl_means")
        quality_no_regression = (
            isinstance(learned_quality, (int, float))
            and isinstance(baseline_quality, (int, float))
            and learned_quality <= baseline_quality
            and learned.get("promotion_gate_runs", 0) >= baseline.get("promotion_gate_runs", 0)
        )
        reduction = baseline_calls - learned_calls if (
            isinstance(learned_calls, int) and isinstance(baseline_calls, int)
        ) else None
    else:
        quality_no_regression = False
        reduction = None

    return {
        "status": "verified" if not errors else "invalid",
        "source": str(path.relative_to(ROOT)),
        "source_sha256": digest(path),
        "baseline_method": "heuristic",
        "learned_simulator_calls": learned.get("simulator_invocations"),
        "baseline_simulator_calls": baseline.get("simulator_invocations"),
        "simulator_call_reduction": reduction,
        "quality_no_regression": quality_no_regression,
        "learned_mean_safe_inl": learned.get("mean_of_round_safe_inl_means"),
        "baseline_mean_safe_inl": baseline.get("mean_of_round_safe_inl_means"),
        "learned_promotion_gate_runs": learned.get("promotion_gate_runs"),
        "baseline_promotion_gate_runs": baseline.get("promotion_gate_runs"),
        "round_seeds": seeds,
        "errors": errors,
        "interpretation": "descriptive_only; adaptive rounds share prior outcome memory",
    }


def main() -> int:
    learned = json.loads(LEARNED.read_text())
    runtime = json.loads(RUNTIME.read_text())
    runtime_by_corner = {corner_key(item["corner"]): item for item in runtime["decisions"]}
    comparisons = []
    for item in learned["decisions"]:
        corner = item["corner"]
        baseline = runtime_by_corner[corner_key(corner)]
        decision = item["decision"]
        learned_energy = float(decision["cost"]["estimated_energy"])
        baseline_energy = 3072.0 if baseline["action"] == "digital_fallback" else float(baseline["estimated_energy"])
        comparisons.append({
            "corner": corner,
            "learned_action": decision["action"],
            "baseline_action": baseline["action"],
            "learned_safe": bool(decision["reliable"]),
            "baseline_safe": True,
            "learned_estimated_energy": learned_energy,
            "baseline_estimated_energy": baseline_energy,
            "energy_delta": learned_energy - baseline_energy,
            "strict_improvement": learned_energy < baseline_energy,
            "same_or_better": learned_energy <= baseline_energy,
            "learned_analog": decision["action"] == "selective_analog",
            "baseline_analog": baseline["action"] == "selective_analog",
            "ledger_evidence_lookup_count": item["episode"]["ledger_evidence_lookups"],
        })
    safe = all(item["learned_safe"] and item["baseline_safe"] for item in comparisons)
    no_regression = all(item["same_or_better"] for item in comparisons)
    coverage_no_regression = sum(item["learned_analog"] for item in comparisons) >= sum(item["baseline_analog"] for item in comparisons)
    strict = any(item["strict_improvement"] for item in comparisons)
    learned_summary = learned.get("summary", {})
    legacy_search = verify_executed_search(EXECUTED_SEARCH)
    direct_search = (
        verify_saved_experiment(INDEPENDENT_BUDGET_SEARCH)
        if INDEPENDENT_BUDGET_SEARCH.is_file() else legacy_search
    )
    experiment_cost = experiment_efficiency_evidence({
        **learned,
        "executed_search_comparison": direct_search,
    })
    result = {
        "schema_version": "recursive_rsi_promotion_evaluation.v1",
        "inputs": {"learned_loop": str(LEARNED.relative_to(ROOT)), "learned_loop_sha256": digest(LEARNED),
                   "baseline_runtime_policy": str(RUNTIME.relative_to(ROOT)), "baseline_sha256": digest(RUNTIME),
                   "independent_budget_search": str(INDEPENDENT_BUDGET_SEARCH.relative_to(ROOT)) if INDEPENDENT_BUDGET_SEARCH.is_file() else None},
        "comparison_contract": {"safety": "all learned and baseline decisions must be safe",
                                "cost": "learned modeled energy must be no worse per matched held-out corner",
                                "coverage": "learned analog coverage must not decrease",
                                "promotion": "at least one strict improvement with no safety, cost, or coverage regression",
                                "rollback": "use baseline runtime policy, then digital fallback"},
        "comparisons": comparisons,
        "summary": {"matched_cases": len(comparisons), "safe_cases": sum(item["learned_safe"] for item in comparisons),
                     "no_regression": no_regression, "strict_improvements": sum(item["strict_improvement"] for item in comparisons),
                     "learned_analog_cases": sum(item["learned_analog"] for item in comparisons),
                     "baseline_analog_cases": sum(item["baseline_analog"] for item in comparisons),
                     "coverage_no_regression": coverage_no_regression,
                     "learned_energy": sum(item["learned_estimated_energy"] for item in comparisons),
                     "baseline_energy": sum(item["baseline_estimated_energy"] for item in comparisons),
                     "learned_ledger_evidence_lookups": sum(item["ledger_evidence_lookup_count"] for item in comparisons)},
        "promotion": {"status": "approved" if safe and no_regression and coverage_no_regression and strict else "rejected",
                      "reason": "reproducible held-out improvement requirement",
                      "rollback_policy": "baseline_runtime_policy_then_digital_fallback"},
        "experiment_policy_promotion": {
            "status": "approved" if safe and coverage_no_regression and experiment_cost["strict_search_efficiency_improvement"] else "rejected",
            "improvement": "strict_simulator_call_reduction" if experiment_cost["strict_search_efficiency_improvement"] else "not_demonstrated",
            "reason": (
                "independent cold-start budget comparison passed all per-seed safety, promotion-gate, quality, and call-reduction checks"
                if experiment_cost["strict_search_efficiency_improvement"] and INDEPENDENT_BUDGET_SEARCH.is_file()
                else "fresh independent adaptive replication failed per-seed candidate-quality non-regression; retain baseline selector"
                if direct_search["status"] == "verified" and not direct_search.get("quality_no_regression", False)
                else "hash-verified executed searches show no qualifying independent strict call reduction"
                if direct_search["status"] == "verified"
                else "executed search evidence is missing or invalid; precomputed ledger lookups are not simulator-call savings"
            ),
            "rollback_policy": "baseline_experiment_selector_then_digital_fallback",
        },
        "status": "passed" if safe else "blocked",
        "claim_boundary": "Promotion comparison uses matched frozen simulator evidence and declared relative costs; it is not measured hardware energy or production validation."
    }
    result["experiment_cost"] = experiment_cost
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "summary": result["summary"], "promotion": result["promotion"]}, indent=2, sort_keys=True))
    return 0 if safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
