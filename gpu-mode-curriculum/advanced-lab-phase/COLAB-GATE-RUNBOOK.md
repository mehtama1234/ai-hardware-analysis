# Colab gate runbook

This is the execution handoff for the six open end-to-end gates. It uses the
existing Colab CLI wrapper and keeps GPU results claim-scoped. A Colab run is
not a production-capacity claim, a multi-GPU result, or an AMD portability
result.

## Launch contract

From the repository root, choose a unique session and run one mode at a time:

```bash
COLAB_SESSION_NAME=advanced-serving-t4-<date> \
COLAB_RUN_ID=colab-t4-trained-serving-<date> \
COLAB_GPU_TYPE=T4 \
COLAB_HANDOFF_MODE=trained-serving \
bash gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh
```

The wrapper packages the source, creates a new Colab session, uploads the
archive, runs the mode, downloads the report, and stops the session by default.
Do not reuse a session owned by another project. Starting a session requires
explicit compute authorization.

## Gate matrix

### 1. Trained GPU serving and bounded capacity

Run the trained serving bridge and tail-load modes:

```bash
COLAB_HANDOFF_MODE=trained-serving \
COLAB_RUN_ID=colab-t4-trained-serving-<date> \
bash gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh

COLAB_HANDOFF_MODE=trained-tail \
COLAB_RUN_ID=colab-t4-trained-tail-<date> \
bash gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh
```

Expected artifacts are `serving-bridge.json` and
`serving-tail-load-cuda.json`. Accept only if output parity, synchronized
CUDA-event timing, graph-vectorized batching, and p50/p95/max latency checks
pass. The result remains bounded single-device capacity evidence.

### 2. Accelerator cancellation and accounting

The trained tail report records scheduler rejection/cancellation accounting.
The serving adapter checks cancellation between per-token graph replays. This
can establish cooperative cancellation at replay boundaries, not interruption
of an arbitrary captured graph or kernel. Keep
`inflight_interruption_proven` false unless a separate kernel-level experiment
actually proves interruption and resource reclamation.

### 3. CUDA allocator and profiler attribution

Run the batch-1 end-to-end and profiler lanes:

```bash
COLAB_HANDOFF_MODE=batch1-decode \
COLAB_RUN_ID=colab-t4-batch1-e2e-<date> \
bash gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh

COLAB_HANDOFF_MODE=wmma-profiler \
COLAB_RUN_ID=colab-t4-wmma-<date> \
bash gpu-mode-curriculum/scripts/run_colab_gpu_handoff_local.sh
```

Require CUDA-event timing, exact output/logit parity, allocator scope, kernel
labels, and profiler/SASS evidence. Host wall time must not be presented as
device-kernel time.

### 4. Multi-GPU collectives, MoE, and serving

Standard Colab/T4 is insufficient. The existing `distributed-collectives`
handoff may run a world-size-one smoke, but it must remain marked partial. Do
not promote it to multi-GPU acceptance. Use a host with at least two physical
accelerators, NCCL/RCCL, and `torchrun` for this gate.

### 5. ROCm/HIP portability

Colab's NVIDIA runtime cannot close this gate. Run
`programming-projects/rocm-hip-port/run_native.py` on an AMD ROCm host with
`hipcc` and `rocprof`; preserve the unavailable status when those tools are
absent.

### 6. Independent reproduction and publication audit

After importing accepted artifacts, run locally:

```bash
python3 gpu-mode-curriculum/scripts/build_gpu_runs.py
python3 gpu-mode-curriculum/scripts/build_gpu_provenance.py
python3 gpu-mode-curriculum/scripts/build_gpu_measurement_queue.py
python3 gpu-mode-curriculum/scripts/verify_gpu_runs.py
python3 gpu-mode-curriculum/scripts/verify_gpu_provenance.py
python3 gpu-mode-curriculum/scripts/verify_gpu_measurement_queue.py
python3 gpu-mode-curriculum/scripts/build_executable_evidence_page.py
```

A fresh Colab runtime can provide a second-host clean-checkout reproduction,
but the report must retain the runtime identity, source revision, commands,
raw samples, and unavailable-tool declarations. The generated site audit is a
separate publication check.

## Current boundary

The repository already contains accepted bounded T4 artifacts for several of
these lanes. This runbook does not promote old artifacts or infer missing
hardware evidence; each new run must be imported and verified by its own
report contract.
