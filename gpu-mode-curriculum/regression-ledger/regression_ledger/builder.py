from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "regression-ledger"
LEDGER_JSON = OUT / "regression-ledger.json"
REPORT_MD = OUT / "reports" / "regression-ledger.md"


REPORT_PATHS = {
    "kernel": ROOT / "kernel-benchmarks" / "reports" / "kernel-benchmark-report.json",
    "custom_op": ROOT / "custom-ops" / "reports" / "custom-op-report.json",
    "tensor_core_gemm": ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json",
    "persistent_kernels": ROOT / "persistent-kernels" / "persistent-kernels-report.json",
    "parallel_primitives": ROOT / "parallel-primitives" / "parallel-primitives-report.json",
    "autotune": ROOT / "autotune-db" / "autotune-db.json",
    "model": ROOT / "model-integration" / "reports" / "tiny-transformer-report.json",
    "serving": ROOT / "serving-traces" / "reports" / "serving-trace-report.json",
    "kv_cache": ROOT / "kv-cache-paged-attention" / "kv-cache-report.json",
    "attention_serving": ROOT / "attention-serving-stack" / "attention-serving-report.json",
    "flash_attention_backward": ROOT / "flash-attention-backward" / "flash-attention-backward-report.json",
    "sparse_attention": ROOT / "sparse-attention-kernels" / "sparse-attention-report.json",
    "fused_training": ROOT / "fused-training-kernels" / "fused-training-report.json",
    "speculative_decoding": ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json",
    "quantization": ROOT / "quantization-memory-formats" / "quantization-report.json",
    "numerical": ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json",
    "cuda_graphs": ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json",
    "distributed_collectives": ROOT / "distributed-collectives" / "distributed-collectives-report.json",
    "distributed_training": ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json",
    "moe_routing": ROOT / "moe-routing-all-to-all" / "moe-routing-report.json",
    "multi_tenant": ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json",
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _status(metric: str, value: float) -> str:
    if metric == "reference_max_abs_error":
        if value <= 0.20:
            return "passed"
        if value <= 5.0:
            return "warning"
        return "failed"
    if metric.endswith("_error"):
        return "passed" if value <= 5e-2 else "failed"
    if metric in {"median_seconds", "fused_median_seconds", "p50_ttft_ms", "mean_tpot_ms"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"tokens_per_second", "output_tokens_per_second", "elements_per_second"}:
        return "passed" if value > 0 else "failed"
    if metric == "estimated_speedup_vs_measured":
        if value >= 1.0:
            return "passed"
        if value >= 0.95:
            return "warning"
        return "failed"
    if metric == "compression_vs_fp32":
        return "passed" if value >= 1.0 else "failed"
    if metric == "cosine_similarity":
        if value >= 0.995:
            return "passed"
        if value >= 0.95:
            return "warning"
        return "failed"
    if metric in {"repeat_max_abs_drift", "reference_max_abs_error", "max_order_delta"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"dequant_tax_ratio", "fused_speedup_proxy"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"p95_latency_reduction", "latency_jitter_reduction"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"transfer_ms", "latency_ms", "exposed_comm_ms", "overlap_gain", "algorithm_steps"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"memory_gb_per_gpu", "optimizer_state_savings", "all_reduce_ms", "reduce_scatter_ms", "all_gather_ms", "comm_ms", "pipeline_bubble_ms", "step_time_ms"}:
        return "passed" if value >= 0 else "failed"
    if metric == "bandwidth_efficiency":
        if value >= 0.45:
            return "passed"
        if value > 0:
            return "warning"
        return "failed"
    if metric == "fairness_index":
        if value >= 0.70:
            return "passed"
        if value >= 0.50:
            return "warning"
        return "failed"
    if metric == "drop_rate":
        if value <= 0.20:
            return "passed"
        if value <= 0.45:
            return "warning"
        return "failed"
    if metric in {"load_imbalance", "all_to_all_payload_gb", "estimated_all_to_all_ms", "accepted_assignments", "dropped_assignments"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"policy_score", "estimated_utilization", "slo_pass_count", "accepted_count", "rejected_count"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"prefix_cache_blocks_saved", "record_count", "passed_count"}:
        return "passed" if value >= 0 else "failed"
    if metric == "waste_ratio_reduction":
        if value >= 0:
            return "passed"
        if value >= -0.02:
            return "warning"
        return "failed"
    if metric in {"hbm_reduction", "arithmetic_intensity", "occupancy_proxy", "shared_memory_bytes"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"register_pressure_proxy", "tensor_core_eligible", "epilogue_fused"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"waste_ratio", "peak_blocks", "eviction_count", "rejected_count", "prefix_blocks_reused", "peak_block_savings", "admission_delta"}:
        return "passed" if value >= 0 else "failed"
    if metric == "speedup_vs_baseline":
        if value >= 1.0:
            return "passed"
        if value >= 0.95:
            return "warning"
        return "failed"
    if metric in {"resident_ctas_per_sm", "launch_savings_ms", "persistent_compute_ms", "baseline_ms"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"work_efficiency", "memory_traffic_mb", "bandwidth_proxy_gbps", "atomic_pressure_millions", "stable_order_required"}:
        return "passed" if value >= 0 else "failed"
    if metric in {"recompute_overhead_ratio", "saved_activation_reduction", "backward_ms"}:
        return "passed" if value >= 0 else "failed"
    return "passed"


def _metric(layer: str, metric_id: str, metric: str, value: float, source: str, labels: dict[str, Any]) -> dict[str, Any]:
    return {
        "layer": layer,
        "id": metric_id,
        "metric": metric,
        "value": value,
        "status": _status(metric, value),
        "source": source,
        "labels": labels,
    }


def _kernel_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for bench in report.get("benchmarks", []):
        rows.append(
            _metric(
                "kernel-benchmarks",
                bench["id"],
                "median_seconds",
                float(bench.get("seconds", {}).get("median", 0.0)),
                "kernel-benchmarks/reports/kernel-benchmark-report.json",
                {"family": bench.get("family"), "shape_class": bench.get("shape_class"), "device": bench.get("result", {}).get("device")},
            )
        )
    rows.append(
        _metric(
            "kernel-benchmarks",
            "kernel-benchmark-pass-count",
            "passed_count",
            float(report.get("passed", 0)),
            "kernel-benchmarks/reports/kernel-benchmark-report.json",
            {"benchmark_count": report.get("benchmark_count", 0)},
        )
    )
    return rows


def _custom_op_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in report.get("cases", []):
        rows.extend(
            [
                _metric(
                    "custom-ops",
                    case["id"],
                    "fused_median_seconds",
                    float(case.get("seconds", {}).get("fused", {}).get("median", 0.0)),
                    "custom-ops/reports/custom-op-report.json",
                    {"dtype": case.get("dtype")},
                ),
                _metric(
                    "custom-ops",
                    case["id"],
                    "max_abs_error",
                    float(case.get("max_abs_error", 1.0)),
                    "custom-ops/reports/custom-op-report.json",
                    {"dtype": case.get("dtype")},
                ),
                _metric(
                    "custom-ops",
                    case["id"],
                    "elements_per_second",
                    float(case.get("elements_per_second", 0.0)),
                    "custom-ops/reports/custom-op-report.json",
                    {"dtype": case.get("dtype")},
                ),
            ]
        )
    return rows


def _tensor_core_gemm_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"scenario": scenario.get("scenario_id"), "dtype": scenario.get("shape", {}).get("dtype"), "epilogue": scenario.get("epilogue")}
        for metric in ["shared_memory_bytes", "register_pressure_proxy", "occupancy_proxy", "arithmetic_intensity"]:
            rows.append(
                _metric(
                    "tensor-core-gemm",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "tensor-core-gemm/tensor-core-gemm-report.json",
                    labels,
                )
            )
        rows.append(
            _metric(
                "tensor-core-gemm",
                f"{scenario['scenario_id']}:tensor-core",
                "tensor_core_eligible",
                1.0 if scenario.get("tensor_core_eligible") else 0.0,
                "tensor-core-gemm/tensor-core-gemm-report.json",
                labels,
            )
        )
        rows.append(
            _metric(
                "tensor-core-gemm",
                f"{scenario['scenario_id']}:epilogue",
                "epilogue_fused",
                1.0 if scenario.get("epilogue_fused") else 0.0,
                "tensor-core-gemm/tensor-core-gemm-report.json",
                labels,
            )
        )
    rows.append(
        _metric(
            "tensor-core-gemm",
            "tensor-core-gemm-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "tensor-core-gemm/tensor-core-gemm-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _autotune_metrics(database: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        _metric(
            "autotune-db",
            "autotune-record-count",
            "record_count",
            float(database.get("record_count", 0)),
            "autotune-db/autotune-db.json",
            {"families": database.get("families", [])},
        )
    ]
    for record in database.get("records", []):
        rows.append(
            _metric(
                "autotune-db",
                record["id"],
                "estimated_speedup_vs_measured",
                float(record.get("selected", {}).get("estimated_speedup_vs_measured", 0.0)),
                "autotune-db/autotune-db.json",
                {"family": record.get("family"), "shape_class": record.get("shape_class"), "config": record.get("selected", {}).get("config", {}).get("id")},
            )
        )
    return rows


def _persistent_kernel_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "family": scenario.get("kernel_family"),
            "strategy": scenario.get("strategy"),
            "producer_consumer": scenario.get("producer_consumer"),
        }
        for metric in [
            "speedup_vs_baseline",
            "occupancy_proxy",
            "resident_ctas_per_sm",
            "hbm_reduction",
            "launch_savings_ms",
            "persistent_compute_ms",
            "baseline_ms",
        ]:
            rows.append(
                _metric(
                    "persistent-kernels",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "persistent-kernels/persistent-kernels-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "persistent-kernels",
            "persistent-kernels-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "persistent-kernels/persistent-kernels-report.json",
            {"scenario_count": report.get("scenario_count", 0), "family_count": report.get("family_count", 0)},
        )
    )
    return rows


def _parallel_primitives_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "primitive": scenario.get("primitive"),
            "algorithm": scenario.get("algorithm"),
        }
        for metric in [
            "work_efficiency",
            "occupancy_proxy",
            "memory_traffic_mb",
            "bandwidth_proxy_gbps",
            "atomic_pressure_millions",
            "baseline_ms",
            "optimized_ms",
        ]:
            rows.append(
                _metric(
                    "parallel-primitives",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "parallel-primitives/parallel-primitives-report.json",
                    labels,
                )
            )
        rows.append(
            _metric(
                "parallel-primitives",
                f"{scenario['scenario_id']}:stable-order",
                "stable_order_required",
                1.0 if scenario.get("stable_order_required") else 0.0,
                "parallel-primitives/parallel-primitives-report.json",
                labels,
            )
        )
    rows.append(
        _metric(
            "parallel-primitives",
            "parallel-primitives-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "parallel-primitives/parallel-primitives-report.json",
            {"scenario_count": report.get("scenario_count", 0), "primitive_count": report.get("primitive_count", 0)},
        )
    )
    return rows


def _model_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in report.get("cases", []):
        rows.extend(
            [
                _metric(
                    "model-integration",
                    case["id"],
                    "tokens_per_second",
                    float(case.get("tokens_per_second", 0.0)),
                    "model-integration/reports/tiny-transformer-report.json",
                    case.get("shape", {}),
                ),
                _metric(
                    "model-integration",
                    case["id"],
                    "max_abs_error",
                    float(case.get("max_abs_error", 1.0)),
                    "model-integration/reports/tiny-transformer-report.json",
                    case.get("shape", {}),
                ),
                _metric(
                    "model-integration",
                    case["id"],
                    "grad_max_abs_error",
                    float(case.get("grad_max_abs_error", 1.0)),
                    "model-integration/reports/tiny-transformer-report.json",
                    case.get("shape", {}),
                ),
            ]
        )
    return rows


def _serving_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for trace in report.get("traces", []):
        for policy in trace.get("policies", []):
            summary = policy.get("summary", {})
            metric_id = f"{trace['trace_id']}:{summary.get('policy')}"
            for metric in ["output_tokens_per_second", "p50_ttft_ms", "mean_tpot_ms", "prefix_cache_blocks_saved"]:
                rows.append(
                    _metric(
                        "serving-traces",
                        metric_id,
                        metric,
                        float(summary.get(metric, 0.0)),
                        "serving-traces/reports/serving-trace-report.json",
                        {"trace": trace.get("trace_id"), "policy": summary.get("policy")},
                    )
                )
    return rows


def _kv_cache_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"scenario": scenario.get("scenario_id")}
        for policy_name in ["contiguous", "paged"]:
            policy = scenario.get(policy_name, {})
            policy_labels = {**labels, "policy": policy.get("policy", policy_name)}
            for metric in ["peak_blocks", "waste_ratio", "eviction_count", "rejected_count", "prefix_blocks_reused"]:
                rows.append(
                    _metric(
                        "kv-cache-paged-attention",
                        f"{scenario['scenario_id']}:{policy_name}",
                        metric,
                        float(policy.get(metric, 0.0)),
                        "kv-cache-paged-attention/kv-cache-report.json",
                        policy_labels,
                    )
                )
        for metric in ["peak_block_savings", "waste_ratio_reduction", "admission_delta"]:
            rows.append(
                _metric(
                    "kv-cache-paged-attention",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "kv-cache-paged-attention/kv-cache-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "kv-cache-paged-attention",
            "kv-cache-prefix-blocks-reused",
            "prefix_blocks_reused",
            float(report.get("total_prefix_blocks_reused", 0)),
            "kv-cache-paged-attention/kv-cache-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _attention_serving_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"scenario": scenario.get("scenario_id"), "status": scenario.get("status"), "scheduler": scenario.get("scheduler", {}).get("policy")}
        for metric in ["hbm_reduction", "arithmetic_intensity", "occupancy_proxy"]:
            rows.append(
                _metric(
                    "attention-serving-stack",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "attention-serving-stack/attention-serving-report.json",
                    labels,
                )
            )
        rows.append(
            _metric(
                "attention-serving-stack",
                scenario["scenario_id"],
                "shared_memory_bytes",
                float(scenario.get("tiles", {}).get("shared_memory_bytes", 0.0)),
                "attention-serving-stack/attention-serving-report.json",
                labels,
            )
        )
        rows.append(
            _metric(
                "attention-serving-stack",
                f"{scenario['scenario_id']}:prefix-reuse",
                "prefix_blocks_reused",
                float(scenario.get("scheduler", {}).get("prefix_blocks_reused", 0.0)),
                "attention-serving-stack/attention-serving-report.json",
                labels,
            )
        )
    rows.append(
        _metric(
            "attention-serving-stack",
            "attention-serving-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "attention-serving-stack/attention-serving-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _flash_attention_backward_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "dtype": scenario.get("shape", {}).get("dtype"),
            "dropout": scenario.get("dropout"),
            "grouped_query": scenario.get("grouped_query"),
        }
        for metric in [
            "speedup_vs_baseline",
            "hbm_reduction",
            "recompute_overhead_ratio",
            "saved_activation_reduction",
            "occupancy_proxy",
            "max_abs_error",
            "baseline_ms",
            "backward_ms",
        ]:
            rows.append(
                _metric(
                    "flash-attention-backward",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "flash-attention-backward/flash-attention-backward-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "flash-attention-backward",
            "flash-attention-backward-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "flash-attention-backward/flash-attention-backward-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _sparse_attention_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "pattern": scenario.get("pattern"),
            "ragged": scenario.get("requires_ragged"),
            "backward": scenario.get("supports_backward"),
        }
        for metric in [
            "density",
            "speedup_vs_dense",
            "hbm_reduction",
            "metadata_overhead",
            "occupancy_proxy",
            "load_balance_proxy",
            "max_abs_error",
            "baseline_ms",
            "sparse_ms",
        ]:
            rows.append(
                _metric(
                    "sparse-attention-kernels",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "sparse-attention-kernels/sparse-attention-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "sparse-attention-kernels",
            "sparse-attention-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "sparse-attention-kernels/sparse-attention-report.json",
            {"scenario_count": report.get("scenario_count", 0), "pattern_count": report.get("pattern_count", 0)},
        )
    )
    return rows


def _fused_training_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "family": scenario.get("kernel_family"),
            "backward": scenario.get("supports_backward"),
            "optimizer_state": scenario.get("optimizer_state"),
        }
        for metric in [
            "speedup_vs_unfused",
            "hbm_reduction",
            "launch_reduction",
            "occupancy_proxy",
            "register_pressure_proxy",
            "max_abs_error",
            "baseline_ms",
            "fused_ms",
            "baseline_hbm_mb",
            "fused_hbm_mb",
        ]:
            rows.append(
                _metric(
                    "fused-training-kernels",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "fused-training-kernels/fused-training-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "fused-training-kernels",
            "fused-training-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "fused-training-kernels/fused-training-report.json",
            {"scenario_count": report.get("scenario_count", 0), "family_count": report.get("family_count", 0)},
        )
    )
    return rows


def _speculative_decoding_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "workload": scenario.get("workload"),
            "engine": scenario.get("engine_hint"),
            "scheduler": scenario.get("scheduler_policy"),
        }
        for metric in [
            "acceptance_rate",
            "accepted_tokens_per_verify",
            "speedup_vs_baseline",
            "speculative_tpot_ms",
            "estimated_ttft_ms",
            "estimated_output_tokens_per_second",
            "wasted_draft_ratio",
            "rollback_pressure",
            "prefix_reuse_blocks",
            "memory_headroom_gb",
        ]:
            rows.append(
                _metric(
                    "speculative-decoding-serving",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "speculative-decoding-serving/speculative-decoding-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "speculative-decoding-serving",
            "speculative-decoding-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "speculative-decoding-serving/speculative-decoding-report.json",
            {"scenario_count": report.get("scenario_count", 0), "engine_count": report.get("engine_count", 0)},
        )
    )
    return rows


def _quantization_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for fmt in report.get("formats", []):
        labels = {"format": fmt.get("format_id"), "bits": fmt.get("bits"), "fit": fmt.get("serving_fit")}
        for metric in ["compression_vs_fp32", "cosine_similarity", "dequant_tax_ratio", "fused_speedup_proxy"]:
            rows.append(
                _metric(
                    "quantization-memory-formats",
                    fmt["format_id"],
                    metric,
                    float(fmt.get(metric, 0.0)),
                    "quantization-memory-formats/quantization-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "quantization-memory-formats",
            "quantization-passed-format-count",
            "passed_count",
            float(report.get("passed_format_count", 0)),
            "quantization-memory-formats/quantization-report.json",
            {"format_count": report.get("format_count", 0)},
        )
    )
    return rows


def _numerical_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"mode": scenario.get("mode"), "category": scenario.get("category"), "status": scenario.get("status")}
        for metric in ["repeat_max_abs_drift", "reference_max_abs_error", "cosine_similarity"]:
            rows.append(
                _metric(
                    "numerical-reproducibility",
                    scenario["mode"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "numerical-reproducibility/numerical-reproducibility-report.json",
                    labels,
                )
            )
    reduction = report.get("reduction_order", {})
    rows.append(
        _metric(
            "numerical-reproducibility",
            "parallel-reduction-order",
            "max_order_delta",
            float(reduction.get("max_order_delta", 0.0)),
            "numerical-reproducibility/numerical-reproducibility-report.json",
            {"status": reduction.get("status")},
        )
    )
    rows.append(
        _metric(
            "numerical-reproducibility",
            "numerical-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "numerical-reproducibility/numerical-reproducibility-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _cuda_graphs_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"scenario": scenario.get("scenario_id"), "status": scenario.get("status")}
        for metric in ["eager_p95_ms", "graph_p95_ms", "p95_latency_reduction", "latency_jitter_reduction"]:
            rows.append(
                _metric(
                    "cuda-graphs-latency",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "cuda-graphs-latency/cuda-graphs-latency-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "cuda-graphs-latency",
            "cuda-graphs-capture-ready-count",
            "passed_count",
            float(report.get("capture_ready_count", 0)),
            "cuda-graphs-latency/cuda-graphs-latency-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _moe_routing_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {"scenario": scenario.get("scenario_id"), "status": scenario.get("status"), "bottleneck": scenario.get("bottleneck")}
        for metric in ["drop_rate", "fairness_index", "load_imbalance", "all_to_all_payload_gb", "estimated_all_to_all_ms", "accepted_assignments", "dropped_assignments"]:
            rows.append(
                _metric(
                    "moe-routing-all-to-all",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "moe-routing-all-to-all/moe-routing-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "moe-routing-all-to-all",
            "moe-routing-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "moe-routing-all-to-all/moe-routing-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _distributed_collectives_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "status": scenario.get("status"),
            "collective": scenario.get("collective"),
            "backend": scenario.get("backend"),
        }
        for metric in ["transfer_ms", "latency_ms", "exposed_comm_ms", "overlap_gain", "bandwidth_efficiency", "algorithm_steps"]:
            rows.append(
                _metric(
                    "distributed-collectives",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "distributed-collectives/distributed-collectives-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "distributed-collectives",
            "distributed-collectives-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "distributed-collectives/distributed-collectives-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _distributed_training_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for scenario in report.get("scenarios", []):
        labels = {
            "scenario": scenario.get("scenario_id"),
            "status": scenario.get("status"),
            "strategy": scenario.get("strategy"),
            "topology": scenario.get("topology"),
        }
        for metric in ["memory_gb_per_gpu", "optimizer_state_savings", "all_reduce_ms", "reduce_scatter_ms", "all_gather_ms", "comm_ms", "exposed_comm_ms", "pipeline_bubble_ms", "step_time_ms", "tokens_per_second"]:
            rows.append(
                _metric(
                    "distributed-training-optimizer",
                    scenario["scenario_id"],
                    metric,
                    float(scenario.get(metric, 0.0)),
                    "distributed-training-optimizer/distributed-training-optimizer-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "distributed-training-optimizer",
            "distributed-training-passed-scenarios",
            "passed_count",
            float(report.get("passed_scenarios", 0)),
            "distributed-training-optimizer/distributed-training-optimizer-report.json",
            {"scenario_count": report.get("scenario_count", 0)},
        )
    )
    return rows


def _multi_tenant_metrics(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for plan in report.get("plans", []):
        labels = {"policy": plan.get("policy_id"), "recommended": plan.get("policy_id") == report.get("recommended_policy")}
        for metric in ["fairness_index", "policy_score", "accepted_count", "rejected_count", "estimated_utilization", "slo_pass_count"]:
            rows.append(
                _metric(
                    "multi-tenant-gpu-scheduling",
                    plan["policy_id"],
                    metric,
                    float(plan.get(metric, 0.0)),
                    "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
                    labels,
                )
            )
    rows.append(
        _metric(
            "multi-tenant-gpu-scheduling",
            "recommended-accepted-count",
            "accepted_count",
            float(report.get("accepted_count", 0)),
            "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
            {"recommended_policy": report.get("recommended_policy")},
        )
    )
    return rows


def render_markdown(ledger: dict[str, Any]) -> str:
    lines = [
        "# Performance Regression Ledger",
        "",
        f"Generated: `{ledger['generated_at']}`",
        f"Metrics: `{ledger['metric_count']}`",
        f"Passed: `{ledger['passed']}`",
        f"Warnings: `{ledger['warnings']}`",
        f"Failed: `{ledger['failed']}`",
        "",
        "| layer | id | metric | value | status | source |",
        "|---|---|---|---:|---|---|",
    ]
    for row in ledger["metrics"]:
        lines.append(
            "| "
            f"{row['layer']} | {row['id']} | {row['metric']} | {row['value']:.8g} | {row['status']} | {row['source']} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_ledger() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    reports = {name: load_json(path, {}) for name, path in REPORT_PATHS.items()}
    metrics = []
    metrics.extend(_kernel_metrics(reports["kernel"]))
    metrics.extend(_custom_op_metrics(reports["custom_op"]))
    metrics.extend(_tensor_core_gemm_metrics(reports["tensor_core_gemm"]))
    metrics.extend(_persistent_kernel_metrics(reports["persistent_kernels"]))
    metrics.extend(_parallel_primitives_metrics(reports["parallel_primitives"]))
    metrics.extend(_autotune_metrics(reports["autotune"]))
    metrics.extend(_model_metrics(reports["model"]))
    metrics.extend(_serving_metrics(reports["serving"]))
    metrics.extend(_kv_cache_metrics(reports["kv_cache"]))
    metrics.extend(_attention_serving_metrics(reports["attention_serving"]))
    metrics.extend(_flash_attention_backward_metrics(reports["flash_attention_backward"]))
    metrics.extend(_sparse_attention_metrics(reports["sparse_attention"]))
    metrics.extend(_fused_training_metrics(reports["fused_training"]))
    metrics.extend(_speculative_decoding_metrics(reports["speculative_decoding"]))
    metrics.extend(_quantization_metrics(reports["quantization"]))
    metrics.extend(_numerical_metrics(reports["numerical"]))
    metrics.extend(_cuda_graphs_metrics(reports["cuda_graphs"]))
    metrics.extend(_distributed_collectives_metrics(reports["distributed_collectives"]))
    metrics.extend(_distributed_training_metrics(reports["distributed_training"]))
    metrics.extend(_moe_routing_metrics(reports["moe_routing"]))
    metrics.extend(_multi_tenant_metrics(reports["multi_tenant"]))
    status_counts = {
        "passed": sum(1 for row in metrics if row["status"] == "passed"),
        "warnings": sum(1 for row in metrics if row["status"] == "warning"),
        "failed": sum(1 for row in metrics if row["status"] == "failed"),
    }
    ledger = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_count": len(metrics),
        **status_counts,
        "source_reports": {name: str(path.relative_to(ROOT)) for name, path in REPORT_PATHS.items()},
        "thresholds": {
            "error_max": 0.05,
            "speedup_min": 1.0,
            "throughput_min": "greater-than-zero",
            "latency_min": "non-negative",
            "fairness_index_warning_min": 0.50,
        },
        "metrics": metrics,
    }
    LEDGER_JSON.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_markdown(ledger), encoding="utf-8")
    return ledger
