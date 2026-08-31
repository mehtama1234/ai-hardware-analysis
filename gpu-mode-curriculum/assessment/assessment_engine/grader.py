from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
QUESTION_BANK = ROOT / "assessment" / "question-bank.json"
REPORT_JSON = ROOT / "assessment" / "grading-report.json"
REPORT_MD = ROOT / "assessment" / "reports" / "grading-report.md"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _concept_result(question: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "has_source_lessons": bool(question.get("source_lessons")),
        "has_tutorial_sources": bool(question.get("related_tutorial_sources")),
        "has_answer_key": len(question.get("expected_answer_points", [])) >= 3,
        "has_prompt": bool(question.get("prompt")),
    }
    passed = all(checks.values())
    return {
        "id": question.get("id"),
        "type": "concept-check",
        "topic": question.get("topic"),
        "points": question.get("points", 0),
        "earned": question.get("points", 0) if passed else 0,
        "status": "passed" if passed else "failed",
        "checks": checks,
    }


def _practical_checks() -> dict[str, Callable[[], tuple[bool, dict[str, Any]]]]:
    return {
        "lesson-labs": lambda: _check(
            lambda data: data.get("passed_contracts") == 118,
            ROOT / "lesson-labs" / "run-report.json",
            "passed_contracts",
        ),
        "comprehensive-labs": lambda: _check_pair(
            ROOT / "comprehensive-labs" / "plan.json",
            ROOT / "comprehensive-labs" / "run-report.json",
            lambda plan, run: plan.get("coverage", {}).get("covered_lessons") == 118 and run.get("passed") == len(plan.get("labs", [])),
            {"plan_lessons": ("plan", ["coverage", "covered_lessons"]), "passed": ("run", ["passed"])},
        ),
        "kernel-benchmarks": lambda: _check(
            lambda data: data.get("passed", 0) >= 14 and data.get("failed") == 0,
            ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json",
            "passed",
        ),
        "compiler-runtime-inspection": lambda: _check(
            lambda data: data.get("status") == "inspection-ready"
            and data.get("source_count", 0) >= 10
            and {"cuda", "triton", "custom-op", "hip"}.issubset(set(data.get("groups", []))),
            ROOT / "compiler-runtime-inspection" / "compiler-runtime-report.json",
            "status",
        ),
        "tensor-core-gemm": lambda: _check(
            lambda data: data.get("status") == "tensor-core-gemm-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("tensor_core_eligible_scenarios", 0) >= 5
            and data.get("fused_epilogue_scenarios", 0) >= 4
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json",
            "status",
        ),
        "persistent-kernels": lambda: _check(
            lambda data: data.get("status") == "persistent-kernels-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 5
            and data.get("family_count", 0) >= 5
            and data.get("producer_consumer_scenarios", 0) >= 3
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "persistent-kernels" / "persistent-kernels-report.json",
            "status",
        ),
        "parallel-primitives": lambda: _check(
            lambda data: data.get("status") == "parallel-primitives-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 5
            and data.get("primitive_count", 0) >= 6
            and data.get("stable_order_scenarios", 0) >= 3
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "parallel-primitives" / "parallel-primitives-report.json",
            "status",
        ),
        "custom-ops": lambda: _check(
            lambda data: data.get("passed", 0) >= 4 and data.get("failed") == 0,
            ROOT / "custom-ops" / "reports" / "custom-op-report.json",
            "passed",
        ),
        "autotune-db": lambda: _check(
            lambda data: data.get("record_count", 0) >= 18,
            ROOT / "autotune-db" / "autotune-db.json",
            "record_count",
        ),
        "model-integration": lambda: _check(
            lambda data: data.get("passed", 0) >= 3 and data.get("failed") == 0,
            ROOT / "model-integration" / "reports" / "tiny-transformer-report.json",
            "passed",
        ),
        "serving-traces": lambda: _check(
            lambda data: data.get("passed_traces", 0) >= 3 and data.get("failed_traces") == 0,
            ROOT / "serving-traces" / "reports" / "serving-trace-report.json",
            "passed_traces",
        ),
        "kv-cache-paged-attention": lambda: _check(
            lambda data: data.get("status") == "kv-cache-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("passed_scenarios", 0) >= 4
            and data.get("total_prefix_blocks_reused", 0) > 0
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "kv-cache-paged-attention" / "kv-cache-report.json",
            "status",
        ),
        "attention-serving-stack": lambda: _check(
            lambda data: data.get("status") == "attention-serving-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("passed_scenarios", 0) >= 4
            and data.get("total_prefix_blocks_reused", 0) > 0
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "attention-serving-stack" / "attention-serving-report.json",
            "status",
        ),
        "flash-attention-backward": lambda: _check(
            lambda data: data.get("status") == "flash-attention-backward-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 5
            and data.get("dropout_scenarios", 0) >= 1
            and data.get("grouped_query_scenarios", 0) >= 1
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "flash-attention-backward" / "flash-attention-backward-report.json",
            "status",
        ),
        "sparse-attention-kernels": lambda: _check(
            lambda data: data.get("status") == "sparse-attention-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 5
            and data.get("pattern_count", 0) >= 6
            and data.get("ragged_scenarios", 0) >= 1
            and data.get("backward_scenarios", 0) >= 4
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "sparse-attention-kernels" / "sparse-attention-report.json",
            "status",
        ),
        "fused-training-kernels": lambda: _check(
            lambda data: data.get("status") == "fused-training-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 5
            and data.get("family_count", 0) >= 5
            and data.get("backward_scenarios", 0) >= 4
            and data.get("optimizer_state_scenarios", 0) >= 2
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "fused-training-kernels" / "fused-training-report.json",
            "status",
        ),
        "serving-engine-comparison": lambda: _check(
            lambda data: data.get("status") == "comparison-ready"
            and data.get("engine_count", 0) >= 5
            and data.get("scenario_count", 0) >= 5
            and len(data.get("scenario_recommendations", [])) >= 5,
            ROOT / "serving-engine-comparison" / "serving-engine-comparison.json",
            "status",
        ),
        "speculative-decoding-serving": lambda: _check(
            lambda data: data.get("status") == "speculative-decoding-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("passed_scenarios", 0) >= 4
            and data.get("engine_count", 0) >= 4
            and data.get("scheduler_policy_count", 0) >= 2
            and data.get("min_acceptance_rate", 1.0) < 0.50
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json",
            "status",
        ),
        "distributed-topology": lambda: _check(
            lambda data: data.get("status") == "topology-plan-ready"
            and data.get("topology_count", 0) >= 5
            and data.get("workload_count", 0) >= 5
            and data.get("candidate_count", 0) > 0,
            ROOT / "distributed-topology" / "distributed-topology-plan.json",
            "status",
        ),
        "distributed-collectives": lambda: _check(
            lambda data: data.get("status") == "distributed-collectives-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("collective_count", 0) >= 5
            and data.get("passed_scenarios", 0) >= 5
            and {"nccl", "rccl"}.issubset({backend.split("/")[0] for backend in data.get("backends", [])}),
            ROOT / "distributed-collectives" / "distributed-collectives-report.json",
            "status",
        ),
        "distributed-training-optimizer": lambda: _check(
            lambda data: data.get("status") == "training-optimizer-ready"
            and data.get("scenario_count", 0) >= 6
            and data.get("strategy_count", 0) >= 5
            and data.get("checkpointed_scenarios", 0) >= 3
            and data.get("passed_scenarios", 0) >= 4,
            ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json",
            "status",
        ),
        "moe-routing-all-to-all": lambda: _check(
            lambda data: data.get("status") == "moe-routing-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("passed_scenarios", 0) >= 3
            and data.get("tuning_required_scenarios", 0) >= 1
            and all(row.get("all_to_all_payload_gb", 0) > 0 and row.get("fairness_index", 0) > 0 for row in data.get("scenarios", [])),
            ROOT / "moe-routing-all-to-all" / "moe-routing-report.json",
            "status",
        ),
        "hardware-capacity": lambda: _check(
            lambda data: data.get("status") == "capacity-plan-ready"
            and data.get("profile_count", 0) >= 5
            and data.get("workload_count", 0) >= 5
            and data.get("recommendation_count") == data.get("workload_count")
            and any(row.get("recommended_profile") != "local-cpu-fallback" for row in data.get("recommendations", [])),
            ROOT / "hardware-capacity-planning" / "hardware-capacity-plan.json",
            "status",
        ),
        "quantization-memory-formats": lambda: _check(
            lambda data: data.get("status") == "quantization-ready"
            and data.get("format_count", 0) >= 7
            and data.get("passed_format_count", 0) >= 4
            and any(row.get("compression_vs_fp32", 0) >= 4 for row in data.get("formats", []))
            and data.get("gpu_host_promotion", {}).get("required") is True,
            ROOT / "quantization-memory-formats" / "quantization-report.json",
            "status",
        ),
        "numerical-reproducibility": lambda: _check(
            lambda data: data.get("status") == "reproducibility-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("passed_scenarios", 0) >= 4
            and data.get("tolerance_review_scenarios", 0) >= 1
            and data.get("reduction_order", {}).get("status") == "passed",
            ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json",
            "status",
        ),
        "cuda-graphs-latency": lambda: _check(
            lambda data: data.get("status") == "cuda-graphs-ready"
            and data.get("scenario_count", 0) >= 5
            and data.get("capture_ready_count", 0) >= 3
            and data.get("fallback_required_count", 0) >= 2
            and data.get("passed_reduction_count", 0) >= 3,
            ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json",
            "status",
        ),
        "multi-tenant-gpu-scheduling": lambda: _check(
            lambda data: data.get("status") == "scheduling-ready"
            and data.get("policy_count", 0) >= 4
            and data.get("tenant_count", 0) >= 5
            and data.get("accepted_count", 0) >= 4
            and {"mig-pack", "mps-fair-share"}.issubset({row.get("id") for row in data.get("policies", [])})
            and any(plan.get("fairness_index", 0) >= 0.60 for plan in data.get("plans", [])),
            ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json",
            "status",
        ),
        "profiler-evidence": lambda: _check(
            lambda data: data.get("row_count", 0) >= 9 and data.get("source_count", 0) >= 3,
            ROOT / "profiler-evidence" / "reports" / "profiler-evidence-report.json",
            "row_count",
        ),
        "gpu-promotion": lambda: _check(
            lambda data: data.get("step_count", 0) >= 9 and data.get("ready_on_gpu_host", 0) >= 4,
            ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json",
            "step_count",
        ),
        "gpu-promotion-suite": lambda: _check(
            lambda data: data.get("status") == "dry-run-ready" and data.get("command_count", 0) >= 20,
            ROOT / "gpu-promotion" / "suite-run-report.json",
            "command_count",
        ),
        "gpu-runs": lambda: _check(
            lambda data: data.get("status") == "import-ready" and data.get("coverage", {}).get("promotion_step_count", 0) >= 9,
            ROOT / "gpu-runs" / "gpu-run-report.json",
            "status",
        ),
        "gpu-import-lint": lambda: _check(
            lambda data: data.get("status") == "lint-clean" and data.get("error_count") == 0,
            ROOT / "gpu-runs" / "import-lint-report.json",
            "status",
        ),
        "gpu-provenance": lambda: _check(
            lambda data: data.get("status") == "provenance-clear" and data.get("sample_run_count", 0) >= 2 and data.get("host_collected_run_count", 0) >= 1,
            ROOT / "gpu-provenance" / "gpu-provenance-report.json",
            "status",
        ),
        "gpu-measurement-queue": lambda: _check(
            lambda data: data.get("status") == "queue-ready"
            and data.get("task_count", 0) >= 9
            and data.get("failed_measured_task_count", 0) == 0
            and all(task.get("has_metric_contract") for task in data.get("tasks", [])),
            ROOT / "gpu-measurement-queue" / "gpu-measurement-queue.json",
            "status",
        ),
        "gpu-acceptance-logic": lambda: _check(
            lambda data: data.get("status") == "passed"
            and data.get("accepted_good_cases") == data.get("case_count")
            and data.get("rejected_bad_cases") == data.get("case_count"),
            ROOT / "gpu-measurement-queue" / "acceptance-logic-report.json",
            "status",
        ),
        "gpu-host-preflight": lambda: _check(
            lambda data: data.get("status") == "preflight-complete"
            and data.get("step_count", 0) >= 9
            and data.get("runnable_step_count", 0) + data.get("blocked_step_count", 0) == data.get("step_count", -1),
            ROOT / "gpu-handoff" / "gpu-host-preflight.json",
            "status",
        ),
        "gpu-handoff": lambda: _check(
            lambda data: data.get("status") == "ready" and data.get("suite_summary", {}).get("command_count", 0) >= 20,
            ROOT / "gpu-handoff" / "gpu-host-handoff.json",
            "status",
        ),
        "regression-ledger": lambda: _check(
            lambda data: data.get("metric_count", 0) >= 95 and data.get("failed") == 0,
            ROOT / "regression-ledger" / "regression-ledger.json",
            "metric_count",
        ),
    }


def _nested(data: dict[str, Any], keys: list[str]) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _check(predicate: Callable[[dict[str, Any]], bool], path: Path, fact_key: str) -> tuple[bool, dict[str, Any]]:
    data = load_json(path, {})
    return predicate(data), {"artifact": str(path.relative_to(ROOT)), fact_key: data.get(fact_key)}


def _check_pair(
    plan_path: Path,
    run_path: Path,
    predicate: Callable[[dict[str, Any], dict[str, Any]], bool],
    fact_spec: dict[str, tuple[str, list[str]]],
) -> tuple[bool, dict[str, Any]]:
    plan = load_json(plan_path, {})
    run = load_json(run_path, {})
    sources = {"plan": plan, "run": run}
    facts: dict[str, Any] = {
        "plan_artifact": str(plan_path.relative_to(ROOT)),
        "run_artifact": str(run_path.relative_to(ROOT)),
    }
    for key, (source, path) in fact_spec.items():
        facts[key] = _nested(sources[source], path)
    return predicate(plan, run), facts


def _practical_result(task: dict[str, Any], checkers: dict[str, Callable[[], tuple[bool, dict[str, Any]]]]) -> dict[str, Any]:
    checker = checkers.get(task.get("layer"))
    passed, facts = checker() if checker else (False, {"reason": "no checker for layer"})
    return {
        "id": task.get("id"),
        "type": "practical-task",
        "layer": task.get("layer"),
        "points": task.get("points", 0),
        "earned": task.get("points", 0) if passed else 0,
        "status": "passed" if passed else "failed",
        "command": task.get("command"),
        "facts": facts,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GPUMODE Assessment Grading Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: `{report['status']}`",
        f"Score: `{report['score']}/{report['max_score']}` ({report['percent']}%)",
        "",
        "| item | type | layer/topic | status | points |",
        "|---|---|---|---|---:|",
    ]
    for row in report["results"]:
        label = row.get("layer") or row.get("topic")
        lines.append(f"| `{row['id']}` | {row['type']} | {label} | {row['status']} | {row['earned']}/{row['points']} |")
    return "\n".join(lines).rstrip() + "\n"


def grade_assessment() -> dict[str, Any]:
    bank = load_json(QUESTION_BANK, {})
    concept_results = [_concept_result(question) for question in bank.get("questions", [])]
    checkers = _practical_checks()
    practical_results = [_practical_result(task, checkers) for task in bank.get("practical_tasks", [])]
    results = concept_results + practical_results
    max_score = sum(row.get("points", 0) for row in results)
    score = sum(row.get("earned", 0) for row in results)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if score == max_score and max_score > 0 else "failed",
        "score": score,
        "max_score": max_score,
        "percent": round(score / max(max_score, 1) * 100, 2),
        "concept_score": sum(row["earned"] for row in concept_results),
        "practical_score": sum(row["earned"] for row in practical_results),
        "concept_count": len(concept_results),
        "practical_count": len(practical_results),
        "failed_count": sum(1 for row in results if row["status"] != "passed"),
        "results": results,
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    return report
