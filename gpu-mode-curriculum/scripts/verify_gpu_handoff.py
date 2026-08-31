#!/usr/bin/env python3
"""Verify the GPU-host handoff bundle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "gpu-handoff" / "gpu-host-handoff.json"
HANDOFF_MD = ROOT / "gpu-handoff" / "reports" / "gpu-host-handoff.md"
HANDOFF_SH = ROOT / "gpu-handoff" / "bin" / "run-gpu-host-handoff.sh"
SITE_PAGE = ROOT / "site" / "gpu-handoff.html"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not HANDOFF.exists():
        subprocess.run([sys.executable, "scripts/build_gpu_handoff.py"], cwd=ROOT, check=True)
    handoff = load_json(HANDOFF)
    require(handoff.get("status") == "ready", "GPU handoff is not ready")
    require(handoff.get("suite_summary", {}).get("command_count", 0) >= 20, "handoff lacks suite command coverage")
    require(handoff.get("preflight_summary", {}).get("status") == "preflight-complete", "handoff lacks preflight completion")
    require(handoff.get("compiler_runtime_summary", {}).get("status") == "inspection-ready", "handoff lacks compiler runtime inspection")
    require(handoff.get("tensor_core_gemm_summary", {}).get("status") == "tensor-core-gemm-ready", "handoff lacks tensor-core GEMM report")
    require(handoff.get("persistent_kernels_summary", {}).get("status") == "persistent-kernels-ready", "handoff lacks persistent kernels report")
    require(handoff.get("parallel_primitives_summary", {}).get("status") == "parallel-primitives-ready", "handoff lacks parallel primitives report")
    require(handoff.get("serving_engine_summary", {}).get("status") == "comparison-ready", "handoff lacks serving engine comparison")
    require(handoff.get("kv_cache_summary", {}).get("status") == "kv-cache-ready", "handoff lacks KV-cache report")
    require(handoff.get("attention_serving_summary", {}).get("status") == "attention-serving-ready", "handoff lacks attention serving report")
    require(handoff.get("flash_attention_backward_summary", {}).get("status") == "flash-attention-backward-ready", "handoff lacks FlashAttention backward report")
    require(handoff.get("sparse_attention_summary", {}).get("status") == "sparse-attention-ready", "handoff lacks sparse attention report")
    require(handoff.get("fused_training_summary", {}).get("status") == "fused-training-ready", "handoff lacks fused training kernels report")
    require(handoff.get("speculative_decoding_summary", {}).get("status") == "speculative-decoding-ready", "handoff lacks speculative decoding report")
    require(handoff.get("distributed_topology_summary", {}).get("status") == "topology-plan-ready", "handoff lacks distributed topology plan")
    require(handoff.get("distributed_collectives_summary", {}).get("status") == "distributed-collectives-ready", "handoff lacks distributed collectives report")
    require(handoff.get("distributed_training_summary", {}).get("status") == "training-optimizer-ready", "handoff lacks distributed training optimizer report")
    require(handoff.get("moe_routing_summary", {}).get("status") == "moe-routing-ready", "handoff lacks MoE routing report")
    require(handoff.get("hardware_capacity_summary", {}).get("status") == "capacity-plan-ready", "handoff lacks hardware capacity plan")
    require(handoff.get("quantization_summary", {}).get("status") == "quantization-ready", "handoff lacks quantization memory-format report")
    require(handoff.get("numerical_reproducibility_summary", {}).get("status") == "reproducibility-ready", "handoff lacks numerical reproducibility report")
    require(handoff.get("cuda_graphs_summary", {}).get("status") == "cuda-graphs-ready", "handoff lacks CUDA Graphs latency report")
    require(handoff.get("multi_tenant_scheduling_summary", {}).get("status") == "scheduling-ready", "handoff lacks multi-tenant scheduling report")
    require(handoff.get("gpu_run_summary", {}).get("promotion_steps", 0) >= 9, "handoff lacks GPU-run promotion coverage")
    require("scripts/run_gpu_promotion_suite.py" in handoff.get("bundle_files", []), "handoff missing suite runner")
    require("scripts/run_gpu_host_preflight.py" in handoff.get("bundle_files", []), "handoff missing preflight runner")
    require("scripts/run_compiler_runtime_inspection.py" in handoff.get("bundle_files", []), "handoff missing compiler runtime runner")
    require("scripts/verify_compiler_runtime_inspection.py" in handoff.get("bundle_files", []), "handoff missing compiler runtime verifier")
    require("scripts/run_tensor_core_gemm.py" in handoff.get("bundle_files", []), "handoff missing tensor-core GEMM runner")
    require("scripts/verify_tensor_core_gemm.py" in handoff.get("bundle_files", []), "handoff missing tensor-core GEMM verifier")
    require("scripts/run_persistent_kernels.py" in handoff.get("bundle_files", []), "handoff missing persistent kernels runner")
    require("scripts/verify_persistent_kernels.py" in handoff.get("bundle_files", []), "handoff missing persistent kernels verifier")
    require("scripts/run_parallel_primitives.py" in handoff.get("bundle_files", []), "handoff missing parallel primitives runner")
    require("scripts/verify_parallel_primitives.py" in handoff.get("bundle_files", []), "handoff missing parallel primitives verifier")
    require("scripts/run_serving_engine_comparison.py" in handoff.get("bundle_files", []), "handoff missing serving engine runner")
    require("scripts/verify_serving_engine_comparison.py" in handoff.get("bundle_files", []), "handoff missing serving engine verifier")
    require("scripts/run_kv_cache_paged_attention.py" in handoff.get("bundle_files", []), "handoff missing KV-cache runner")
    require("scripts/verify_kv_cache_paged_attention.py" in handoff.get("bundle_files", []), "handoff missing KV-cache verifier")
    require("scripts/run_attention_serving_stack.py" in handoff.get("bundle_files", []), "handoff missing attention serving runner")
    require("scripts/verify_attention_serving_stack.py" in handoff.get("bundle_files", []), "handoff missing attention serving verifier")
    require("scripts/run_flash_attention_backward.py" in handoff.get("bundle_files", []), "handoff missing FlashAttention backward runner")
    require("scripts/verify_flash_attention_backward.py" in handoff.get("bundle_files", []), "handoff missing FlashAttention backward verifier")
    require("scripts/run_sparse_attention_kernels.py" in handoff.get("bundle_files", []), "handoff missing sparse attention runner")
    require("scripts/verify_sparse_attention_kernels.py" in handoff.get("bundle_files", []), "handoff missing sparse attention verifier")
    require("scripts/run_fused_training_kernels.py" in handoff.get("bundle_files", []), "handoff missing fused training runner")
    require("scripts/verify_fused_training_kernels.py" in handoff.get("bundle_files", []), "handoff missing fused training verifier")
    require("scripts/run_speculative_decoding_serving.py" in handoff.get("bundle_files", []), "handoff missing speculative decoding runner")
    require("scripts/verify_speculative_decoding_serving.py" in handoff.get("bundle_files", []), "handoff missing speculative decoding verifier")
    require("scripts/run_distributed_topology.py" in handoff.get("bundle_files", []), "handoff missing distributed topology runner")
    require("scripts/verify_distributed_topology.py" in handoff.get("bundle_files", []), "handoff missing distributed topology verifier")
    require("scripts/run_distributed_collectives.py" in handoff.get("bundle_files", []), "handoff missing distributed collectives runner")
    require("scripts/verify_distributed_collectives.py" in handoff.get("bundle_files", []), "handoff missing distributed collectives verifier")
    require("scripts/run_distributed_collectives_benchmark.py" in handoff.get("bundle_files", []), "handoff missing distributed collectives benchmark runner")
    require("scripts/verify_distributed_collectives_benchmark.py" in handoff.get("bundle_files", []), "handoff missing distributed collectives benchmark verifier")
    require("scripts/run_distributed_training_optimizer.py" in handoff.get("bundle_files", []), "handoff missing distributed training optimizer runner")
    require("scripts/verify_distributed_training_optimizer.py" in handoff.get("bundle_files", []), "handoff missing distributed training optimizer verifier")
    require("scripts/run_moe_routing_all_to_all.py" in handoff.get("bundle_files", []), "handoff missing MoE runner")
    require("scripts/verify_moe_routing_all_to_all.py" in handoff.get("bundle_files", []), "handoff missing MoE verifier")
    require("scripts/run_hardware_capacity_plan.py" in handoff.get("bundle_files", []), "handoff missing hardware capacity runner")
    require("scripts/verify_hardware_capacity_plan.py" in handoff.get("bundle_files", []), "handoff missing hardware capacity verifier")
    require("scripts/run_quantization_memory_formats.py" in handoff.get("bundle_files", []), "handoff missing quantization runner")
    require("scripts/verify_quantization_memory_formats.py" in handoff.get("bundle_files", []), "handoff missing quantization verifier")
    require("scripts/run_numerical_reproducibility.py" in handoff.get("bundle_files", []), "handoff missing numerical reproducibility runner")
    require("scripts/verify_numerical_reproducibility.py" in handoff.get("bundle_files", []), "handoff missing numerical reproducibility verifier")
    require("scripts/run_cuda_graphs_latency.py" in handoff.get("bundle_files", []), "handoff missing CUDA Graphs runner")
    require("scripts/verify_cuda_graphs_latency.py" in handoff.get("bundle_files", []), "handoff missing CUDA Graphs verifier")
    require("scripts/run_multi_tenant_gpu_scheduling.py" in handoff.get("bundle_files", []), "handoff missing multi-tenant scheduling runner")
    require("scripts/verify_multi_tenant_gpu_scheduling.py" in handoff.get("bundle_files", []), "handoff missing multi-tenant scheduling verifier")
    require("scripts/verify_gpu_host_preflight.py" in handoff.get("bundle_files", []), "handoff missing preflight verifier")
    require("scripts/collect_gpu_run.py" in handoff.get("bundle_files", []), "handoff missing collector")
    require("python3 scripts/verify_gpu_runs.py" in handoff.get("validation_commands", []), "handoff missing GPU-run validation")
    require("python3 scripts/verify_gpu_host_preflight.py" in handoff.get("validation_commands", []), "handoff missing preflight validation")
    require("python3 scripts/verify_compiler_runtime_inspection.py" in handoff.get("validation_commands", []), "handoff missing compiler runtime validation")
    require("python3 scripts/verify_tensor_core_gemm.py" in handoff.get("validation_commands", []), "handoff missing tensor-core GEMM validation")
    require("python3 scripts/verify_persistent_kernels.py" in handoff.get("validation_commands", []), "handoff missing persistent kernels validation")
    require("python3 scripts/verify_parallel_primitives.py" in handoff.get("validation_commands", []), "handoff missing parallel primitives validation")
    require("python3 scripts/verify_serving_engine_comparison.py" in handoff.get("validation_commands", []), "handoff missing serving engine validation")
    require("python3 scripts/verify_kv_cache_paged_attention.py" in handoff.get("validation_commands", []), "handoff missing KV-cache validation")
    require("python3 scripts/verify_attention_serving_stack.py" in handoff.get("validation_commands", []), "handoff missing attention serving validation")
    require("python3 scripts/verify_flash_attention_backward.py" in handoff.get("validation_commands", []), "handoff missing FlashAttention backward validation")
    require("python3 scripts/verify_sparse_attention_kernels.py" in handoff.get("validation_commands", []), "handoff missing sparse attention validation")
    require("python3 scripts/verify_fused_training_kernels.py" in handoff.get("validation_commands", []), "handoff missing fused training validation")
    require("python3 scripts/verify_speculative_decoding_serving.py" in handoff.get("validation_commands", []), "handoff missing speculative decoding validation")
    require("python3 scripts/verify_distributed_topology.py" in handoff.get("validation_commands", []), "handoff missing distributed topology validation")
    require("python3 scripts/verify_distributed_collectives.py" in handoff.get("validation_commands", []), "handoff missing distributed collectives validation")
    require("python3 scripts/verify_distributed_collectives_benchmark.py" in handoff.get("validation_commands", []), "handoff missing distributed collectives benchmark validation")
    require("python3 scripts/verify_distributed_training_optimizer.py" in handoff.get("validation_commands", []), "handoff missing distributed training optimizer validation")
    require("python3 scripts/verify_moe_routing_all_to_all.py" in handoff.get("validation_commands", []), "handoff missing MoE validation")
    require("python3 scripts/verify_hardware_capacity_plan.py" in handoff.get("validation_commands", []), "handoff missing hardware capacity validation")
    require("python3 scripts/verify_quantization_memory_formats.py" in handoff.get("validation_commands", []), "handoff missing quantization validation")
    require("python3 scripts/verify_numerical_reproducibility.py" in handoff.get("validation_commands", []), "handoff missing numerical reproducibility validation")
    require("python3 scripts/verify_cuda_graphs_latency.py" in handoff.get("validation_commands", []), "handoff missing CUDA Graphs validation")
    require("python3 scripts/verify_multi_tenant_gpu_scheduling.py" in handoff.get("validation_commands", []), "handoff missing multi-tenant scheduling validation")
    require(HANDOFF_MD.exists(), "handoff markdown missing")
    require(HANDOFF_SH.exists(), "handoff shell entrypoint missing")
    script = HANDOFF_SH.read_text(encoding="utf-8")
    require("run_gpu_host_preflight.py" in script and "run_gpu_promotion_suite.py" in script and "run_compiler_runtime_inspection.py" in script and "run_tensor_core_gemm.py" in script and "run_persistent_kernels.py" in script and "run_parallel_primitives.py" in script and "run_serving_engine_comparison.py" in script and "run_kv_cache_paged_attention.py" in script and "run_attention_serving_stack.py" in script and "run_flash_attention_backward.py" in script and "run_sparse_attention_kernels.py" in script and "run_fused_training_kernels.py" in script and "run_speculative_decoding_serving.py" in script and "run_distributed_topology.py" in script and "run_moe_routing_all_to_all.py" in script and "run_hardware_capacity_plan.py" in script and "run_quantization_memory_formats.py" in script and "run_numerical_reproducibility.py" in script and "run_cuda_graphs_latency.py" in script and "run_multi_tenant_gpu_scheduling.py" in script and "collect_gpu_run.py" in script, "handoff script missing key commands")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE GPU host handoff" in page, "handoff site page missing title")
        require("run-gpu-host-handoff.sh" in page, "handoff site page missing entrypoint")
    facts = {
        "status": handoff["status"],
        "commands": handoff["suite_summary"]["command_count"],
        "bundle_files": len(handoff["bundle_files"]),
        "entrypoint": handoff["entrypoint"],
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE GPU handoff verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
