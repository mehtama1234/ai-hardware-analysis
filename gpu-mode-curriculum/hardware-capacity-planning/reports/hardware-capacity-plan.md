# GPUMODE Hardware Capacity Plan

Generated: `2026-08-31T01:53:15.573891+00:00`
Status: `capacity-plan-ready`

## Recommendations

| workload | profile | bottleneck | memory GB | headroom GB | power W | cost/hr |
|---|---|---|---:|---:|---:|---:|
| kernel-dev-smoke | single-24gb-dev-gpu | mixed | 2.0 | 22.0 | 320 | 0.6 |
| interactive-7b-chat | datacenter-80gb-training-gpu | memory-bandwidth | 22.64 | 57.36 | 700 | 3.4 |
| long-context-13b-rag | large-memory-192gb-inference-gpu | kv-cache-capacity | 97.26 | 94.74 | 760 | 4.2 |
| batch-70b-inference | multi-node-cluster-slice | communication | 42.97 | 37.03 | 5600 | 24.0 |
| dense-70b-sft | large-memory-training-slice | communication | 155.16 | 36.84 | 6080 | 34.0 |

## Evidence Commands

### kernel-dev-smoke
- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute`
- `nsys profile -o capacity-plan python3 <workload.py>`
- `ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>`
### interactive-7b-chat
- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute`
- `vllm serve <model> --tensor-parallel-size <tp> --max-model-len <tokens>`
- `nsys profile -o capacity-plan python3 <workload.py>`
- `ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>`
### long-context-13b-rag
- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute`
- `nsys profile -o capacity-plan python3 <workload.py>`
- `ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>`
### batch-70b-inference
- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute`
- `vllm serve <model> --tensor-parallel-size <tp> --max-model-len <tokens>`
- `nsys profile -o capacity-plan python3 <workload.py>`
- `ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>`
### dense-70b-sft
- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.limit --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id capacity-plan --execute`
- `torchrun --nproc-per-node=<gpus> <training_script.py>`
- `nsys profile -o capacity-plan python3 <workload.py>`
- `ncu --set full -o capacity-plan python3 <kernel_or_serving_probe.py>`

## Source Reports

- `kernel-benchmarks/reports/kernel-benchmark-report.json`
- `profiler-evidence/reports/profiler-evidence-report.json`
- `serving-engine-comparison/serving-engine-comparison.json`
- `distributed-topology/distributed-topology-plan.json`
