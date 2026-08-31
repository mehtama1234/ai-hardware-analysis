from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "gpu-handoff"
HANDOFF_JSON = OUT / "gpu-host-handoff.json"
HANDOFF_MD = OUT / "reports" / "gpu-host-handoff.md"
HANDOFF_SH = OUT / "bin" / "run-gpu-host-handoff.sh"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bundle_files() -> list[str]:
    return [
        "gpu-promotion/gpu-host-promotion-manifest.json",
        "gpu-handoff/gpu-host-preflight.json",
        "gpu-promotion/suite-run-report.json",
        "compiler-runtime-inspection/compiler-runtime-report.json",
        "tensor-core-gemm/tensor-core-gemm-report.json",
        "persistent-kernels/persistent-kernels-report.json",
        "parallel-primitives/parallel-primitives-report.json",
        "gpu-runs/import-lint-report.json",
        "gpu-runs/gpu-run-report.json",
        "gpu-provenance/gpu-provenance-report.json",
        "serving-engine-comparison/serving-engine-comparison.json",
        "kv-cache-paged-attention/kv-cache-report.json",
        "attention-serving-stack/attention-serving-report.json",
        "flash-attention-backward/flash-attention-backward-report.json",
        "sparse-attention-kernels/sparse-attention-report.json",
        "fused-training-kernels/fused-training-report.json",
        "speculative-decoding-serving/speculative-decoding-report.json",
        "distributed-topology/distributed-topology-plan.json",
        "distributed-collectives/distributed-collectives-report.json",
        "distributed-collectives/reports/collective-benchmark-run.json",
        "distributed-training-optimizer/distributed-training-optimizer-report.json",
        "moe-routing-all-to-all/moe-routing-report.json",
        "hardware-capacity-planning/hardware-capacity-plan.json",
        "quantization-memory-formats/quantization-report.json",
        "numerical-reproducibility/numerical-reproducibility-report.json",
        "cuda-graphs-latency/cuda-graphs-latency-report.json",
        "multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json",
        "gpu-measurement-queue/gpu-measurement-queue.json",
        "gpu-measurement-queue/acceptance-logic-report.json",
        "scripts/run_gpu_promotion_suite.py",
        "scripts/run_gpu_host_preflight.py",
        "scripts/run_compiler_runtime_inspection.py",
        "scripts/verify_compiler_runtime_inspection.py",
        "scripts/run_tensor_core_gemm.py",
        "scripts/verify_tensor_core_gemm.py",
        "scripts/run_persistent_kernels.py",
        "scripts/verify_persistent_kernels.py",
        "scripts/run_parallel_primitives.py",
        "scripts/verify_parallel_primitives.py",
        "scripts/run_serving_engine_comparison.py",
        "scripts/verify_serving_engine_comparison.py",
        "scripts/run_kv_cache_paged_attention.py",
        "scripts/verify_kv_cache_paged_attention.py",
        "scripts/run_attention_serving_stack.py",
        "scripts/verify_attention_serving_stack.py",
        "scripts/run_flash_attention_backward.py",
        "scripts/verify_flash_attention_backward.py",
        "scripts/run_sparse_attention_kernels.py",
        "scripts/verify_sparse_attention_kernels.py",
        "scripts/run_fused_training_kernels.py",
        "scripts/verify_fused_training_kernels.py",
        "scripts/run_speculative_decoding_serving.py",
        "scripts/verify_speculative_decoding_serving.py",
        "scripts/run_distributed_topology.py",
        "scripts/verify_distributed_topology.py",
        "scripts/run_distributed_collectives.py",
        "scripts/verify_distributed_collectives.py",
        "scripts/run_distributed_collectives_benchmark.py",
        "scripts/verify_distributed_collectives_benchmark.py",
        "scripts/run_distributed_training_optimizer.py",
        "scripts/verify_distributed_training_optimizer.py",
        "scripts/run_moe_routing_all_to_all.py",
        "scripts/verify_moe_routing_all_to_all.py",
        "scripts/run_hardware_capacity_plan.py",
        "scripts/verify_hardware_capacity_plan.py",
        "scripts/run_quantization_memory_formats.py",
        "scripts/verify_quantization_memory_formats.py",
        "scripts/run_numerical_reproducibility.py",
        "scripts/verify_numerical_reproducibility.py",
        "scripts/run_cuda_graphs_latency.py",
        "scripts/verify_cuda_graphs_latency.py",
        "scripts/run_multi_tenant_gpu_scheduling.py",
        "scripts/verify_multi_tenant_gpu_scheduling.py",
        "scripts/verify_gpu_host_preflight.py",
        "scripts/collect_gpu_run.py",
        "scripts/lint_gpu_run_imports.py",
        "scripts/build_gpu_runs.py",
        "scripts/build_gpu_provenance.py",
        "scripts/build_gpu_measurement_queue.py",
        "scripts/verify_gpu_runs.py",
        "scripts/verify_gpu_provenance.py",
        "scripts/verify_gpu_measurement_queue.py",
        "scripts/verify_gpu_acceptance_logic.py",
        "scripts/verify_gpu_promotion_suite.py",
        "scripts/verify_capstone_acceptance.py",
    ]


def _script() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${1:-gpu-host-handoff-run}"
MODE="${2:---dry-run}"

if [[ "$MODE" == "--execute" ]]; then
  python3 scripts/run_gpu_host_preflight.py
  python3 scripts/run_gpu_promotion_suite.py --run-id "$RUN_ID" --execute
else
  python3 scripts/run_gpu_host_preflight.py
  python3 scripts/run_gpu_promotion_suite.py --run-id "$RUN_ID"
fi

python3 scripts/collect_gpu_run.py --run-id "$RUN_ID"
python3 scripts/lint_gpu_run_imports.py
python3 scripts/build_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/verify_gpu_promotion_suite.py
python3 scripts/verify_gpu_runs.py
python3 scripts/verify_gpu_provenance.py
python3 scripts/verify_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/run_compiler_runtime_inspection.py
python3 scripts/verify_compiler_runtime_inspection.py
python3 scripts/run_tensor_core_gemm.py
python3 scripts/verify_tensor_core_gemm.py
python3 scripts/run_persistent_kernels.py
python3 scripts/verify_persistent_kernels.py
python3 scripts/run_parallel_primitives.py
python3 scripts/verify_parallel_primitives.py
python3 scripts/run_serving_engine_comparison.py
python3 scripts/verify_serving_engine_comparison.py
python3 scripts/run_kv_cache_paged_attention.py
python3 scripts/verify_kv_cache_paged_attention.py
python3 scripts/run_attention_serving_stack.py
python3 scripts/verify_attention_serving_stack.py
python3 scripts/run_flash_attention_backward.py
python3 scripts/verify_flash_attention_backward.py
python3 scripts/run_sparse_attention_kernels.py
python3 scripts/verify_sparse_attention_kernels.py
python3 scripts/run_fused_training_kernels.py
python3 scripts/verify_fused_training_kernels.py
python3 scripts/run_speculative_decoding_serving.py
python3 scripts/verify_speculative_decoding_serving.py
python3 scripts/run_distributed_topology.py
python3 scripts/verify_distributed_topology.py
python3 scripts/run_distributed_collectives.py
python3 scripts/verify_distributed_collectives.py
python3 scripts/verify_distributed_collectives_benchmark.py
python3 scripts/run_distributed_training_optimizer.py
python3 scripts/verify_distributed_training_optimizer.py
python3 scripts/run_moe_routing_all_to_all.py
python3 scripts/verify_moe_routing_all_to_all.py
python3 scripts/run_hardware_capacity_plan.py
python3 scripts/verify_hardware_capacity_plan.py
python3 scripts/run_quantization_memory_formats.py
python3 scripts/verify_quantization_memory_formats.py
python3 scripts/run_numerical_reproducibility.py
python3 scripts/verify_numerical_reproducibility.py
python3 scripts/run_cuda_graphs_latency.py
python3 scripts/verify_cuda_graphs_latency.py
python3 scripts/run_multi_tenant_gpu_scheduling.py
python3 scripts/verify_multi_tenant_gpu_scheduling.py
python3 scripts/build_runtime_matrix.py
python3 build_site.py
python3 scripts/build_end_to_end_audit.py
python3 scripts/build_capstone_acceptance.py
python3 scripts/verify_capstone_acceptance.py
"""


def render_markdown(handoff: dict[str, Any]) -> str:
    lines = [
        "# GPU Host Handoff",
        "",
        f"Generated: `{handoff['generated_at']}`",
        f"Status: `{handoff['status']}`",
        f"Promotion commands: `{handoff['suite_summary']['command_count']}`",
        "",
        "## Run On GPU Host",
        "",
        "```bash",
        "bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --dry-run",
        "bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --execute",
        "```",
        "",
        "## Bundle Files",
        "",
    ]
    for path in handoff["bundle_files"]:
        lines.append(f"- `{path}`")
    lines.extend(["", "## Validation Gates", ""])
    for command in handoff["validation_commands"]:
        lines.append(f"- `{command}`")
    return "\n".join(lines).rstrip() + "\n"


def build_handoff() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    HANDOFF_MD.parent.mkdir(parents=True, exist_ok=True)
    HANDOFF_SH.parent.mkdir(parents=True, exist_ok=True)
    promotion = load_json(ROOT / "gpu-promotion" / "gpu-host-promotion-manifest.json", {})
    suite = load_json(ROOT / "gpu-promotion" / "suite-run-report.json", {})
    preflight = load_json(ROOT / "gpu-handoff" / "gpu-host-preflight.json", {})
    compiler_runtime = load_json(ROOT / "compiler-runtime-inspection" / "compiler-runtime-report.json", {})
    gpu_runs = load_json(ROOT / "gpu-runs" / "gpu-run-report.json", {})
    tensor_core_gemm = load_json(ROOT / "tensor-core-gemm" / "tensor-core-gemm-report.json", {})
    persistent_kernels = load_json(ROOT / "persistent-kernels" / "persistent-kernels-report.json", {})
    parallel_primitives = load_json(ROOT / "parallel-primitives" / "parallel-primitives-report.json", {})
    serving_engine_comparison = load_json(ROOT / "serving-engine-comparison" / "serving-engine-comparison.json", {})
    kv_cache = load_json(ROOT / "kv-cache-paged-attention" / "kv-cache-report.json", {})
    attention_serving = load_json(ROOT / "attention-serving-stack" / "attention-serving-report.json", {})
    flash_attention_backward = load_json(ROOT / "flash-attention-backward" / "flash-attention-backward-report.json", {})
    sparse_attention = load_json(ROOT / "sparse-attention-kernels" / "sparse-attention-report.json", {})
    fused_training = load_json(ROOT / "fused-training-kernels" / "fused-training-report.json", {})
    speculative_decoding = load_json(ROOT / "speculative-decoding-serving" / "speculative-decoding-report.json", {})
    distributed_topology = load_json(ROOT / "distributed-topology" / "distributed-topology-plan.json", {})
    distributed_collectives = load_json(ROOT / "distributed-collectives" / "distributed-collectives-report.json", {})
    distributed_training = load_json(ROOT / "distributed-training-optimizer" / "distributed-training-optimizer-report.json", {})
    moe_routing = load_json(ROOT / "moe-routing-all-to-all" / "moe-routing-report.json", {})
    hardware_capacity = load_json(ROOT / "hardware-capacity-planning" / "hardware-capacity-plan.json", {})
    quantization = load_json(ROOT / "quantization-memory-formats" / "quantization-report.json", {})
    numerical = load_json(ROOT / "numerical-reproducibility" / "numerical-reproducibility-report.json", {})
    cuda_graphs = load_json(ROOT / "cuda-graphs-latency" / "cuda-graphs-latency-report.json", {})
    multi_tenant_scheduling = load_json(ROOT / "multi-tenant-gpu-scheduling" / "multi-tenant-scheduling-report.json", {})
    measurement_queue = load_json(ROOT / "gpu-measurement-queue" / "gpu-measurement-queue.json", {})
    acceptance_logic = load_json(ROOT / "gpu-measurement-queue" / "acceptance-logic-report.json", {})
    handoff = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready" if promotion.get("step_count", 0) >= 9 and preflight.get("status") == "preflight-complete" and compiler_runtime.get("status") == "inspection-ready" and tensor_core_gemm.get("status") == "tensor-core-gemm-ready" and persistent_kernels.get("status") == "persistent-kernels-ready" and parallel_primitives.get("status") == "parallel-primitives-ready" and suite.get("command_count", 0) >= 20 and gpu_runs.get("status") == "import-ready" and serving_engine_comparison.get("status") == "comparison-ready" and kv_cache.get("status") == "kv-cache-ready" and attention_serving.get("status") == "attention-serving-ready" and flash_attention_backward.get("status") == "flash-attention-backward-ready" and sparse_attention.get("status") == "sparse-attention-ready" and fused_training.get("status") == "fused-training-ready" and speculative_decoding.get("status") == "speculative-decoding-ready" and distributed_topology.get("status") == "topology-plan-ready" and distributed_collectives.get("status") == "distributed-collectives-ready" and distributed_training.get("status") == "training-optimizer-ready" and moe_routing.get("status") == "moe-routing-ready" and hardware_capacity.get("status") == "capacity-plan-ready" and quantization.get("status") == "quantization-ready" and numerical.get("status") == "reproducibility-ready" and cuda_graphs.get("status") == "cuda-graphs-ready" and multi_tenant_scheduling.get("status") == "scheduling-ready" and measurement_queue.get("status") == "queue-ready" else "incomplete",
        "purpose": "Portable command and evidence handoff for running the GPUMODE GPU curriculum validation suite on an accelerator host.",
        "entrypoint": "gpu-handoff/bin/run-gpu-host-handoff.sh",
        "dry_run_command": "bash gpu-handoff/bin/run-gpu-host-handoff.sh gpu-host-handoff-run --dry-run",
        "execute_command": "bash gpu-handoff/bin/run-gpu-host-handoff.sh gpu-host-handoff-run --execute",
        "suite_summary": {
            "command_count": suite.get("command_count", 0),
            "step_count": suite.get("step_count", 0),
            "status": suite.get("status", "missing"),
        },
        "preflight_summary": {
            "status": preflight.get("status", "missing"),
            "accelerator_ready": preflight.get("accelerator_ready", False),
            "step_count": preflight.get("step_count", 0),
            "runnable_step_count": preflight.get("runnable_step_count", 0),
            "blocked_step_count": preflight.get("blocked_step_count", 0),
        },
        "compiler_runtime_summary": {
            "status": compiler_runtime.get("status", "missing"),
            "source_count": compiler_runtime.get("source_count", 0),
            "groups": compiler_runtime.get("groups", []),
            "risk_counts": compiler_runtime.get("risk_counts", {}),
        },
        "tensor_core_gemm_summary": {
            "status": tensor_core_gemm.get("status", "missing"),
            "scenario_count": tensor_core_gemm.get("scenario_count", 0),
            "tensor_core_eligible_scenarios": tensor_core_gemm.get("tensor_core_eligible_scenarios", 0),
            "fused_epilogue_scenarios": tensor_core_gemm.get("fused_epilogue_scenarios", 0),
        },
        "persistent_kernels_summary": {
            "status": persistent_kernels.get("status", "missing"),
            "scenario_count": persistent_kernels.get("scenario_count", 0),
            "passed_scenarios": persistent_kernels.get("passed_scenarios", 0),
            "family_count": persistent_kernels.get("family_count", 0),
            "producer_consumer_scenarios": persistent_kernels.get("producer_consumer_scenarios", 0),
        },
        "parallel_primitives_summary": {
            "status": parallel_primitives.get("status", "missing"),
            "scenario_count": parallel_primitives.get("scenario_count", 0),
            "passed_scenarios": parallel_primitives.get("passed_scenarios", 0),
            "primitive_count": parallel_primitives.get("primitive_count", 0),
            "stable_order_scenarios": parallel_primitives.get("stable_order_scenarios", 0),
        },
        "gpu_run_summary": {
            "run_count": gpu_runs.get("coverage", {}).get("run_count", 0),
            "vendors": gpu_runs.get("coverage", {}).get("vendors", []),
            "promotion_steps": gpu_runs.get("coverage", {}).get("promotion_step_count", 0),
        },
        "serving_engine_summary": {
            "status": serving_engine_comparison.get("status", "missing"),
            "engine_count": serving_engine_comparison.get("engine_count", 0),
            "scenario_count": serving_engine_comparison.get("scenario_count", 0),
            "engine_wins": serving_engine_comparison.get("engine_wins", {}),
        },
        "kv_cache_summary": {
            "status": kv_cache.get("status", "missing"),
            "scenario_count": kv_cache.get("scenario_count", 0),
            "passed_scenarios": kv_cache.get("passed_scenarios", 0),
            "total_prefix_blocks_reused": kv_cache.get("total_prefix_blocks_reused", 0),
        },
        "attention_serving_summary": {
            "status": attention_serving.get("status", "missing"),
            "scenario_count": attention_serving.get("scenario_count", 0),
            "passed_scenarios": attention_serving.get("passed_scenarios", 0),
            "total_prefix_blocks_reused": attention_serving.get("total_prefix_blocks_reused", 0),
        },
        "flash_attention_backward_summary": {
            "status": flash_attention_backward.get("status", "missing"),
            "scenario_count": flash_attention_backward.get("scenario_count", 0),
            "passed_scenarios": flash_attention_backward.get("passed_scenarios", 0),
            "dropout_scenarios": flash_attention_backward.get("dropout_scenarios", 0),
            "grouped_query_scenarios": flash_attention_backward.get("grouped_query_scenarios", 0),
        },
        "sparse_attention_summary": {
            "status": sparse_attention.get("status", "missing"),
            "scenario_count": sparse_attention.get("scenario_count", 0),
            "passed_scenarios": sparse_attention.get("passed_scenarios", 0),
            "pattern_count": sparse_attention.get("pattern_count", 0),
            "ragged_scenarios": sparse_attention.get("ragged_scenarios", 0),
            "backward_scenarios": sparse_attention.get("backward_scenarios", 0),
        },
        "fused_training_summary": {
            "status": fused_training.get("status", "missing"),
            "scenario_count": fused_training.get("scenario_count", 0),
            "passed_scenarios": fused_training.get("passed_scenarios", 0),
            "family_count": fused_training.get("family_count", 0),
            "backward_scenarios": fused_training.get("backward_scenarios", 0),
            "optimizer_state_scenarios": fused_training.get("optimizer_state_scenarios", 0),
        },
        "speculative_decoding_summary": {
            "status": speculative_decoding.get("status", "missing"),
            "scenario_count": speculative_decoding.get("scenario_count", 0),
            "passed_scenarios": speculative_decoding.get("passed_scenarios", 0),
            "review_scenarios": speculative_decoding.get("review_scenarios", 0),
            "engine_count": speculative_decoding.get("engine_count", 0),
            "scheduler_policy_count": speculative_decoding.get("scheduler_policy_count", 0),
        },
        "distributed_topology_summary": {
            "status": distributed_topology.get("status", "missing"),
            "topology_count": distributed_topology.get("topology_count", 0),
            "workload_count": distributed_topology.get("workload_count", 0),
            "candidate_count": distributed_topology.get("candidate_count", 0),
        },
        "distributed_collectives_summary": {
            "status": distributed_collectives.get("status", "missing"),
            "scenario_count": distributed_collectives.get("scenario_count", 0),
            "collective_count": distributed_collectives.get("collective_count", 0),
            "passed_scenarios": distributed_collectives.get("passed_scenarios", 0),
            "backends": distributed_collectives.get("backends", []),
        },
        "distributed_training_summary": {
            "status": distributed_training.get("status", "missing"),
            "scenario_count": distributed_training.get("scenario_count", 0),
            "passed_scenarios": distributed_training.get("passed_scenarios", 0),
            "strategy_count": distributed_training.get("strategy_count", 0),
            "checkpointed_scenarios": distributed_training.get("checkpointed_scenarios", 0),
        },
        "moe_routing_summary": {
            "status": moe_routing.get("status", "missing"),
            "scenario_count": moe_routing.get("scenario_count", 0),
            "passed_scenarios": moe_routing.get("passed_scenarios", 0),
            "tuning_required_scenarios": moe_routing.get("tuning_required_scenarios", 0),
        },
        "hardware_capacity_summary": {
            "status": hardware_capacity.get("status", "missing"),
            "profile_count": hardware_capacity.get("profile_count", 0),
            "workload_count": hardware_capacity.get("workload_count", 0),
            "recommendation_count": hardware_capacity.get("recommendation_count", 0),
        },
        "quantization_summary": {
            "status": quantization.get("status", "missing"),
            "format_count": quantization.get("format_count", 0),
            "passed_format_count": quantization.get("passed_format_count", 0),
            "calibration_needed_count": quantization.get("calibration_needed_count", 0),
        },
        "numerical_reproducibility_summary": {
            "status": numerical.get("status", "missing"),
            "scenario_count": numerical.get("scenario_count", 0),
            "passed_scenarios": numerical.get("passed_scenarios", 0),
            "tolerance_review_scenarios": numerical.get("tolerance_review_scenarios", 0),
        },
        "cuda_graphs_summary": {
            "status": cuda_graphs.get("status", "missing"),
            "scenario_count": cuda_graphs.get("scenario_count", 0),
            "capture_ready_count": cuda_graphs.get("capture_ready_count", 0),
            "fallback_required_count": cuda_graphs.get("fallback_required_count", 0),
        },
        "multi_tenant_scheduling_summary": {
            "status": multi_tenant_scheduling.get("status", "missing"),
            "policy_count": multi_tenant_scheduling.get("policy_count", 0),
            "tenant_count": multi_tenant_scheduling.get("tenant_count", 0),
            "accepted_count": multi_tenant_scheduling.get("accepted_count", 0),
            "recommended_policy": multi_tenant_scheduling.get("recommended_policy", "missing"),
        },
        "measurement_queue_summary": {
            "task_count": measurement_queue.get("task_count", 0),
            "queued_task_count": measurement_queue.get("queued_task_count", 0),
            "measured_task_count": measurement_queue.get("measured_task_count", 0),
            "accepted_task_count": measurement_queue.get("accepted_task_count", 0),
            "failed_measured_task_count": measurement_queue.get("failed_measured_task_count", 0),
            "real_measured_completion": measurement_queue.get("real_measured_completion", False),
        },
        "acceptance_logic_summary": {
            "status": acceptance_logic.get("status", "missing"),
            "case_count": acceptance_logic.get("case_count", 0),
            "accepted_good_cases": acceptance_logic.get("accepted_good_cases", 0),
            "rejected_bad_cases": acceptance_logic.get("rejected_bad_cases", 0),
        },
        "bundle_files": _bundle_files(),
        "validation_commands": [
            "python3 scripts/verify_gpu_promotion_suite.py",
            "python3 scripts/verify_gpu_host_preflight.py",
            "python3 scripts/verify_compiler_runtime_inspection.py",
            "python3 scripts/verify_tensor_core_gemm.py",
            "python3 scripts/verify_persistent_kernels.py",
            "python3 scripts/verify_parallel_primitives.py",
            "python3 scripts/verify_serving_engine_comparison.py",
            "python3 scripts/verify_kv_cache_paged_attention.py",
            "python3 scripts/verify_attention_serving_stack.py",
            "python3 scripts/verify_flash_attention_backward.py",
            "python3 scripts/verify_sparse_attention_kernels.py",
            "python3 scripts/verify_fused_training_kernels.py",
            "python3 scripts/verify_speculative_decoding_serving.py",
            "python3 scripts/verify_distributed_topology.py",
            "python3 scripts/verify_distributed_collectives.py",
            "python3 scripts/verify_distributed_collectives_benchmark.py",
            "python3 scripts/verify_distributed_training_optimizer.py",
            "python3 scripts/verify_moe_routing_all_to_all.py",
            "python3 scripts/verify_hardware_capacity_plan.py",
            "python3 scripts/verify_quantization_memory_formats.py",
            "python3 scripts/verify_numerical_reproducibility.py",
            "python3 scripts/verify_cuda_graphs_latency.py",
            "python3 scripts/verify_multi_tenant_gpu_scheduling.py",
            "python3 scripts/lint_gpu_run_imports.py",
            "python3 scripts/verify_gpu_runs.py",
            "python3 scripts/verify_gpu_provenance.py",
            "python3 scripts/verify_gpu_measurement_queue.py",
            "python3 scripts/verify_gpu_acceptance_logic.py",
            "python3 scripts/verify_runtime_matrix.py",
            "python3 scripts/verify_capstone_acceptance.py",
        ],
        "operator_notes": [
            "Run dry-run first to inspect placeholder commands.",
            "Replace placeholder model and run-id values before execute mode.",
            "After execute mode, keep the collected gpu-runs/imports/<run-id>.json artifact.",
        ],
    }
    write_json(HANDOFF_JSON, handoff)
    HANDOFF_MD.write_text(render_markdown(handoff), encoding="utf-8")
    HANDOFF_SH.write_text(_script(), encoding="utf-8")
    HANDOFF_SH.chmod(0o755)
    return handoff
