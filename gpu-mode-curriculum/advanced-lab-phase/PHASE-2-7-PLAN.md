# Advanced GPU AI Systems Phase 2-7

Status: `phase-plan-ready`

Execution target: local CPU readiness now, then Google Colab or a remote GPU
host for measured accelerator evidence.

| priority | lane | status | objective |
|---:|---|---|---|
| 2 | `speculative-decoding-serving` | implemented-first-class | `speculative-decoding-serving/`, `scripts/verify_speculative_decoding_serving.py` |
| 3 | `multi-node-training-systems` | implemented-existing-lanes | `distributed-topology/`, `distributed-collectives/`, `distributed-training-optimizer/` |
| 4 | `compiler-stack-deep-dive` | implemented-existing-lanes | `compiler-runtime-inspection/`, `tensor-core-gemm/`, `persistent-kernels/` |
| 5 | `quantized-training-inference-kernels` | implemented-existing-lanes | `quantization-memory-formats/`, `numerical-reproducibility/`, `programming-projects/hf-quant-serving/` |
| 6 | `moe-end-to-end-systems` | implemented-existing-lanes | `moe-routing-all-to-all/`, `distributed-collectives/`, `distributed-training-optimizer/` |
| 7 | `jax-scaling-book-implementation` | implemented-project-lane | `programming-projects/jax-scaling-roofline/`, `programming-projects/jax-scaling-roofline/jax-scaling-roofline.ipynb` |

Colab handoff starts with:

```bash
python3 scripts/verify_advanced_phase.py
python3 scripts/run_gpu_host_preflight.py
python3 scripts/run_gpu_promotion_suite.py --run-id colab-advanced-phase --execute
python3 scripts/collect_gpu_run.py --run-id colab-advanced-phase
python3 scripts/build_gpu_measurement_queue.py
```
