# Full-goal evidence audit

Reviewed 2026-09-06 against source and reports, not directory names. All nine
goal packages remain partially complete or open. The executable checkpoint is
one progression through GEMM, attention, and a small training/inference block.

| Goal package | Established in current work | Evidence still required |
|---|---|---|
| Baseline inventory | Topic routing, source-level gaps, and the complete 24-topic claim-scoped primary-source registry | Keep the registry current as new labs and hardware claims are added |
| Experimental foundation | Raw samples, correctness checks, provenance helpers, regression runner; pinned and offline hash-locked CPU environments and a clean source-snapshot checkout reproduce the current-worktree checkpoint; native CUDA-event and one Nsight/SASS capture | Independent-host reproduction, complete source dependency closure, broader profiler capture and broader adoption |
| GEMM | CPU reference/edge checks; accepted 14-case eager CUDA suite; CUDA naive/tiled/cuBLAS source, native WMMA, and Triton promotions | Broader compiled CUDA-shape attribution; numerical adversaries, bank-conflict/asynchronous-transfer analysis, and complete profiler explanations |
| Attention | Materialized and recomputed derivatives, gradcheck, saved-tensor instrumentation | Fused accelerator kernels, peak allocator measurements, shape/dtype sweeps, dropout/GQA where supported |
| Compiler/layout/synthesis | CPU Inductor operation and whole-transformer forward/backward execution; generated code, gradient/optimizer checks and raw timings; Triton CUDA matmul plus memory/reduction/softmax/layernorm family promotions, including a fixed tail-mask bug | Broader application shapes, full GPU/DSL comparisons, profiler explanations, autotune breadth, bounded synthesis and broader held-out correctness |
| Low precision | Actual packed INT4 buffers, tail tests, conversion-inclusive timings, transformer storage/drift, three predeclared trained digits seed/split quality checks, accepted native CUDA FP16 plus INT8 GEMM evidence, and one accepted CUDA trained-digits quality run | Native INT4/FP8/MX kernels; broader models/workloads and joint memory/performance/quality evidence; rejected configurations and stronger statistical coverage |
| Application integration | Paired optimizer checks; CPU block benchmarks; cached-vector replay; trained autoregressive HTTP backend; accepted single-T4 CUDA KV-cache decode/HTTP parity; repeated three-seed trained-quality protocol; bounded admission, queue rejection, cancellation, microbatch HTTP controls, accepted single-T4 CUDA graph tail-load sweep, and paged-cache/attention correctness | Production-scale trained quality; kernel-to-application comparisons; production-scale GPU capacity/tail characterization; production cancellation semantics; multi-GPU serving |
| Distributed/portable | CPU two-rank request dispatch with rank ownership, global ordering, unique IDs, output parity, and peer agreement; one-rank NCCL smoke, bounded multi-rank NCCL runner, and bounded multi-rank sharded-MoE runner | Measured multi-GPU/all-to-all performance and second-platform experiments; no local hardware acceptance |
| Publication | Linked walkthroughs, six exercises tied to tested reference solutions, complete 24-topic source registry, regression command, and rendered evidence page with source/test freshness checks | Independent-host reproduction and continued evidence-page expansion |

## Concrete source findings for the next expansion

- `../programming-projects/rocm-hip-port/kernel.hip.cpp` defines vector addition
  but its `main` only prints a source-only message. `starter.py` checks for a
  compiler without building or launching it. The measurement artifact now marks
  numerical correctness `not_executed`, separately from successful metadata
  checks, with `measured: false` and `gpu_execution_accepted: false`. Two targeted
  tests cover both ready/source-only paths and rejection of incomplete metadata.
  A host allocation/copy/launch/validation/timing path has since been added to
  the native source, covering five lengths including block tails, a NaN output
  sentinel, FP64 host sums and seven event batch samples. `hipcc` is absent here,
  so that native path remains uncompiled and unexecuted. The readiness starter
  still does not invoke it; explicit build/run integration and hardware proof
  remain required.

- `../../gpu-kernels-serving-lab/09-vllm-serving/run.py` explicitly reports
  readiness when CUDA/vLLM exist; it does not start or benchmark a serving engine.
- `../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/server.py`
  uses `TinyGenerator` to produce deterministic word-based strings. Its prefix
  cache stores tokenized words, not a transformer's KV tensors. Existing HTTP
  measurements are useful transport exercises, not model inference throughput.
  A new opt-in `--backend neural` executes an untrained character transformer
  with actual autoregression and request-local KV tensors. Cached/full logits,
  request isolation and both HTTP endpoints are tested. Trained
  synthetic-character quality, repeated three-seed quality, bounded admission,
  queue rejection, cancellation, microbatch controls, and a CPU tail-load sweep
  are now recorded; production-scale quality, GPU tail latency, and production
  cancellation remain open.
- `../model-integration/run_serving_tail_load_cuda.py` now has an executable
  report contract: every accepted GPU report must include synchronized
  per-wave CUDA-event timing, p95 wall latency, exact output parity, observed
  vectorized batching, backend labels, and scheduler accounting. The local run
  remains `unavailable:cuda-runtime` with `measured: false`, while
  `colab-t4-serving-tail-graphs-20260908-r2` is an accepted single-T4 run of
  the CUDA-graph microbatch mode: 12 requests at concurrency 1/2/4/8, all
  accepted, parity-preserving, with graph-vectorized batches at concurrent
  levels and zero scheduler rejection/cancellation. This is bounded loopback
  evidence, not production capacity or cancellation proof.
- `../../gpu-kernels-serving-lab/08-quantized-inference/run.py` simulates
  quantization and returns dequantized floating values. Its memory estimates are
  bit-budget models, not measured packed storage. Original block helpers truncated
  partial blocks; tests now require all values to survive. This fix does not make
  MXFP4-like emulation a native MXFP4 implementation.
- `../distributed-collectives/reports/collective-benchmark-run.json` records
  `skipped:missing-accelerator`, `measured: false`, and an empty benchmark list.
  Its modeled overlap metrics cannot establish measured collective overlap.

## Next sequence

1. Extend the now-passing hash-locked CPU environment and clean source-snapshot
   reproduction to an independent host boundary; complete source
   dependency capture. Keep current hardware checks explicit.
2. Extend the implemented packed-buffer and trained digits checks to broader
   trained models and multiple seeds. Storage reduction is established for the
   recorded cases; native low-precision compute throughput is not.
3. Extend the implemented trained autoregressive serving backend with
   production-scale quality, GPU tail-load evidence, and production cancellation
   semantics; keep the deterministic transport exercise and supplied-vector
   replay explicitly separate.
4. On approved suitable hardware, compile GEMM and collect training/attention
   allocator/profiler evidence, then develop fused architecture-specific kernels.
5. Complete distributed/portable experiments and publish the measured progression.

No paid infrastructure, remote job, model download, commit, or push is implied
by this audit. Missing hardware does not block the remaining local implementation
and source-quality work, but it does block hardware acceptance.

## Latest verified checkpoint

The hash-locked CPU environment rerun completed at 2026-09-07 02:26 UTC
(2026-09-06 locally): 58 tests and eight CPU experiments passed; the CUDA
experiment reported unavailable. All 25 environment/reproduction checks passed.
The checkpoint checksum matches its wrapper report, test sources remained
unchanged, and the regenerated evidence page reports `checkpoint_current: true`.
Imported local helper files are now hashed alongside explicitly named sources.
This remains current-worktree/hash-locked reproduction, not an independent host
or GPU result. The clean source-snapshot gate is recorded separately in
`fresh-checkout-reproduction.json`.

Subsequent expanded checkpoint: 63 tests and nine CPU experiments passed in the
same hash-locked environment, including `neural-serving-cpu`. All 24 HTTP outputs
matched direct generation at client concurrency 1, 2 and 4. The wrapper checksum
matches the checkpoint and serving source hashes include the model adapter,
HTTP server and load runner. CUDA is still unavailable. The refreshed evidence
page displays raw-sample-derived serving metrics and reports a current checkpoint.
The eight samples per load level and shared client/server process do not establish
production tail latency or capacity.

Latest expansion verified: 64 tests and ten CPU experiments passed, now including
Inductor forward/backward compilation. Each of its three cases captured two
training modules and passed FP64 output/gradient comparisons. All 25 isolated
environment checks passed and the wrapper/checkpoint checksum agrees. The evidence
page is current under the stronger check that verifies implementation-source
hashes inside every required artifact, not just the artifact files themselves.
No CUDA execution, fresh source checkout or full-goal acceptance follows from
this CPU checkpoint.

Latest compiled-application expansion: 65 tests and eleven CPU experiments passed
in the isolated hash-locked environment. The compiled transformer experiment
passed three paired optimizer steps, captured two generated modules and recorded
ten timing samples per backend. All 25 environment checks passed; the checkpoint
checksum matches its wrapper and the rendered evidence page is current. CUDA
remains unavailable. The earlier checkpoint counts above are historical milestones,
not the current test or experiment count.

## Current verified expansion (2026-09-07)

The current hash-locked Python 3.10 environment passed all 25 isolation,
dependency, and execution checks. The expanded checkpoint passed 116 tests
across ten suites and 23 CPU experiments, including profiler evidence, the Colab handoff contract, admission, backpressure
and
cancellation, microbatching, streaming, tail-load, two-rank serving dispatch,
and the top-level source-hash provenance schema. The current clean source-snapshot
reproduction passed at revision `6a9946ee58090b70083d814ae7c9ed9c42d6b029`.

The evidence page reports `checkpoint_current: true`, and the GPU host preflight
reports one locally runnable step plus 31 steps ready for an accelerator host.
CUDA, HIP, Nsight, and independent-host execution remain open where not covered
by the accepted imported or local evidence.

## Current continuation state (2026-09-08)

The serving acceptance lane now has a measured GPU tail-load artifact:
`gpu-runs/imports/colab-t4-serving-tail-graphs-20260908-r2/serving-tail-load-cuda.json`.
The first run exposed and then fixed a verifier bug that failed to recognize
the explicit `cuda-graph-vectorized` batch label; the corrected rerun passed
the report contract. The handoff supports both the original eager microbatch
mode and the graph-microbatch mode.

The speculative-decoding lane now also has a measured CUDA control artifact:
`gpu-runs/imports/colab-t4-speculative-20260908-r8/speculative-decoding-cuda.json`.
Five draft/target scenarios passed exact greedy-output parity, acceptance and
rollback accounting, logical KV-commit accounting, and synchronized CUDA
timing. Trace calibration raised held-out small-draft acceptance to 0.80 from
0.00 for the random draft, while preserving parity. The cached block verifier
is numerically correct, but the calibrated decode path measured about 0.63x
baseline and adaptive fallback about 0.85x. The remaining performance gate is
a fused/persistent target-verification path and lower launch overhead, not
merely draft quality.

The current evidence ledger contains 32 measured GPU promotion tasks, of which
30 are accepted. The native WMMA probe was expanded to nine independent
launches; a fresh T4 Nsight Compute capture recorded nine tensor-pipe metric
values and is now accepted as the `profiler-capture` claim. CPU isolation and
clean-checkout reproduction also pass, and the generated site reports
`checkpoint_current: true`.

The two remaining measured-failed tasks are intentionally hardware-specific:

- `rocm-hip-port`: requires an AMD ROCm host with `hipcc` and `rocprof`.
- `distributed-collectives`: requires a physical multi-GPU host with
  `torchrun`, NCCL/RCCL, and at least two accelerator ranks. A single Colab
  T4/A100/L4 session cannot establish this claim.

The next handoff should run the commands already listed in
`gpu-promotion/gpu-host-promotion-manifest.json` for those two step IDs, then
import the resulting reports with `build_gpu_runs.py`,
`build_gpu_provenance.py`, and `build_gpu_measurement_queue.py`. Do not convert
the current source-ready or world-size-one rows into measured acceptance.
