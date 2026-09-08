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

For the currently missing serving-tail GPU artifact, use the claim-scoped
handoff mode after authentication:

```bash
COLAB_HANDOFF_MODE=serving-tail \
COLAB_RUN_ID=colab-t4-serving-tail-$(date -u +%Y%m%dT%H%M%SZ) \
scripts/run_colab_gpu_handoff_local.sh
python3 scripts/verify_colab_handoff.py
```

The local report remains `unavailable` until the Colab artifact is downloaded;
the handoff verifier checks that boundary and does not promote a CPU fallback.
The local dry-run plan is recorded in
`gpu-promotion/suite-run-report.json` with run ID
`colab-serving-tail-plan`.
