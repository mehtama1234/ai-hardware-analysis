# Executable advanced checkpoint

Latest verified hash-locked checkpoint: **118 tests across ten suites and 23
CPU experiments passed**. All 25 isolation/dependency/execution checks passed;
the 35 checkpoint steps either passed or were explicitly classified unavailable
(CUDA and HIP), so requested accelerator execution remains unaccepted. The
evidence page verifies checkpoint freshness against source, test, and artifact
hashes, and the isolated reproduction report accepts this same checkpoint.

These totals now include profiler evidence, collective contracts and MoE tests, plus two-process
collective correctness and [sharded MoE](../moe-routing-all-to-all/DISTRIBUTED.md).
The latter checks twenty-four rank/scenario outputs and coordinated rejection
of invalid rank data and mismatched capacity. These are CPU correctness results,
not distributed performance, trained quality or GPU acceptance.

Run from the repository root using the [documented CPU environment](ENVIRONMENT.md)
and a working `g++` toolchain for the compiler experiment:

```bash
python3 gpu-mode-curriculum/scripts/run_advanced_evidence_regression.py
```

This runs ten test suites (including profiler evidence, CPU primitives, collective contracts and
MoE reference/contracts) and regenerates 23 CPU experiments: GEMM, packed
INT4 operations, single-protocol and repeated trained digits quality, attention saved-tensor/timing, paired
training, training-block timing, cached-vector decode, packed transformer storage,
neural HTTP load, Inductor forward/backward compilation, and compiled transformer
training correctness/timing, two-process collective correctness and sharded MoE
dispatch/return. Separate requested CUDA training-block and native
HIP experiments record availability; their skips are not hardware passes. Subprocess logs, return
codes, artifact hashes, and source-freshness checks are captured in
`executable-checkpoint.json`. Existing experiment reports are regenerated in
place; no packages are installed and no remote hosts or paid resources are used.
A missing CUDA runtime is unavailable, not passed, and never falls back to CPU.

## Follow the implementation

1. [GEMM](../../gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/README.md):
   scalar/tiled/library CPU comparisons; CUDA naive/tiled/cuBLAS paths awaiting
   compilation and execution on suitable hardware.
2. [Attention](../flash-attention-backward/README.md): derive dQ/dK/dV, check
   finite differences, and recompute probability tiles. Measure saved logical
   tensor bytes, without calling them allocator peak memory.
3. [Training block](../model-integration/README.md): compare full parameter
   gradients and SGD momentum across consecutive steps, then benchmark the
   complete forward/loss/backward path and expose a CUDA peak-allocation path.
4. [Low precision](../../gpu-kernels-serving-lab/08-quantized-inference/README.md):
   distinguish packed storage from native low-precision compute; evaluate a
   trained digits holdout alongside memory and conversion-inclusive timings.
5. [Neural serving](../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/NEURAL-BACKEND.md):
   execute autoregression with real KV tensors, check cached/full logits, and
   measure a bounded loopback concurrency sweep without claiming language quality.
6. [Compiler execution](../compiler-runtime-inspection/README.md): inspect actual
   generated forward/backward code, compare FP64 outputs and gradients, and keep
   compilation cost separate from steady-state calls—including measured losses.

The CPU experiment has shown that saving attention tensors need not make the
application faster: Python blockwise recomputation can cost more than SDPA.
Reproduce results on your own machine; do not treat recorded timings as universal.

## What this does not accept

`checkpoint_passed` means these commands and freshness checks succeeded. It does
not mean a pinned fresh environment was reproduced, every handbook topic was
implemented, CUDA source compiled, GPU speedups were demonstrated, or serving,
distributed/portable execution, quantization quality, and publication were
completed. Those remain in the full goal. The report always leaves
`full_goal_accepted` false.

The environment recipe pins Python packages; the compiler report records the
host C++ compiler version, which is not supplied by the Python wheel lock. Source hashes
do not replace package locks, dependency closure, raw profiler captures, or
independent reproduction; those are remaining experimental-foundation work.

See [the full-goal evidence audit](REMAINING-WORK.md) for remaining requirements
and concrete distinctions between real model execution and existing placeholders.

## Browsable evidence

Use the [exercises and tested reference solutions](EXERCISES.md) to work through
packed storage, attention derivatives, and cached autoregressive decoding.

```bash
python3 gpu-mode-curriculum/scripts/build_executable_evidence_page.py
```

Open [advanced executable evidence](../site/advanced-executable-evidence.html).
The full curriculum site builder also generates this page and links it from the
index. It checks individual report source hashes before displaying their metrics;
stale/missing reports produce a warning instead. The aggregate checkpoint is
current only when its task roster, runner hash, test-source hashes and recorded
artifact hashes match.
It also requires every expected experiment artifact and checks the source hashes
inside those artifacts. An unchanged JSON file cannot keep the aggregate current
after its implementation changes.
This freshness check is not an independent reproduction or full-goal acceptance.

The [environment audit](ENVIRONMENT.md) records the current interpreter's core
dependency closure and the remaining clean-environment reproduction gate.

Source provenance includes explicitly listed files plus local Python modules
already imported when a report is captured. This catches changes in shared
helpers such as the transformer feed-forward implementation. It does not claim
coverage of unexecuted branches, non-Python extensions or arbitrary data inputs.
Those require their own recorded identities.

The checkpoint also hashes its discovered test files, checks that they remain
unchanged during execution, and exposes those hashes to the evidence page.
Adding, deleting or editing a test makes the previous checkpoint stale rather
than silently retaining its old validation claim.
