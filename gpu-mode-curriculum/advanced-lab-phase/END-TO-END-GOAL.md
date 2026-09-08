# Advanced GPU systems: the end-to-end goal

Status: **active**. Started 2026-09-06. No final phase is accepted yet.

## North-star outcome

Build a reproducible advanced GPU-systems curriculum and workbench that takes a
learner from a mathematical reference to a correct implementation, a measured
optimization, and an integrated training or inference system.

The finished system must answer, with runnable evidence:

> Given a model, operator, or bottleneck, what is happening, what should I try
> next, how do I run it, and did the change improve the real application?

The required progression is:

**reference → correct kernel → measured optimization → model integration →
profiler explanation → tutorial and workbench recommendation**

The project reuses `gpu-kernels-serving-lab` and `gpu-mode-curriculum` and
preserves the earlier AI-hardware corpus, GPUMODE curriculum, source registry,
and generated site.

## What “done” means

The goal is complete only when all of the following are true:

1. Every handbook topic has an evidence-backed capability record linking its
   source material, prerequisite concepts, implementation, tests, reports, and
   remaining limitations.
2. The experimental foundation can reproduce accepted results from a clean
   checkout and records source identity, environment, command, inputs, timing
   scope, synchronization, raw samples, correctness, and artifact hashes.
3. At least one vertical slice is complete from kernel reference through
   application behavior, including a measured comparison against a trusted
   library or baseline.
4. GPU and CPU evidence are never conflated. Unsupported hardware is reported
   as unavailable, never converted into a pass or a fabricated estimate.
5. Low-precision results jointly report storage, conversion cost, numerical
   error, native compute behavior, and task quality where applicable.
6. Serving results report prefill/decode behavior, batching, cache behavior,
   admission/backpressure, cancellation, throughput, and latency distributions
   with their actual measurement scope.
7. Distributed and portable claims include real multi-GPU or second-platform
   execution, or remain explicitly open.
8. The generated site provides prerequisites, source walkthroughs, tested
   exercises, raw evidence, limitations, and a queryable bottleneck workbench.

## Work packages

### 1. Inventory and source spine

Map the 24 handbook topics to canonical primary sources, GPUMODE lessons,
existing labs, tests, reports, prerequisites, and missing work. Keep evidence
classified per artifact as `implemented`, `executed`, `measured`, `modeled`,
`fixture`, or `proposed`.

Deliverables:

- `CAPABILITY-MATRIX.md`
- `SOURCE-REGISTRY.md` and `source-registry.json`
- topic/prerequisite graph
- source-to-lesson-to-lab links in the generated site

### 2. Experimental foundation

Provide shared provenance and measurement helpers. Every experiment records:

- source revision, dirty state, source hashes, interpreter and platform;
- exact command, seed, shape/layout/dtype, reference and candidate;
- warm-up, repeat count, raw samples, synchronization, and timing scope;
- correctness checks, tolerances, non-finite rejection, and artifact paths;
- compilation/JIT/setup time separately from steady-state timing;
- explicit unavailable/skip reasons when a tool or accelerator is absent.

Host wall-clock completion is not presented as device-event kernel time. Checksums
alone do not establish elementwise correctness. A model output is not promoted
because a verifier happens to pass.

### 3. GEMM and memory vertical slice

Implement and compare scalar/reference, naive, tiled, library, and
architecture-appropriate paths across square, rectangular, small, tail, and
awkward shapes. Explain coalescing, bank conflicts, arithmetic intensity,
resource use, tensor cores, compiler output, and asynchronous copies where
supported.

Acceptance requires numerical adversaries, repeatable timing, library comparison,
source provenance, and profiler evidence that explains the observed result.

### 4. Attention and backward

Implement executable forward and backward references plus a blockwise/recomputed
variant. Cover causal and explicit masks, rectangular alignment, noncontiguous
inputs, tails, dtype/shape sweeps, finite differences, and pinned reference
comparisons.

Measure logical saved tensors separately from allocator peak memory. Distinguish
exact methods from approximations. GPU acceptance requires actual fused-kernel
execution, allocator evidence, synchronized timing, and profiler capture.

### 5. Compilers, layouts, and generated kernels

Use shared workloads across CUDA, Triton, PyTorch compiler, and a bounded set of
advanced DSLs. Connect layouts, fusion, graph breaks, autotuning, generated code,
and compiler decisions to measured observations.

Generated kernels require held-out correctness tests, bounded execution,
reproducible source identity, and a clear distinction between compile time and
steady-state execution.

### 6. Low precision and numerical quality

Separate emulation from native execution and distinguish weight, activation,
and training quantization. Report packed storage, unpack/conversion overhead,
native kernel timing, output drift, rejected configurations, and held-out task
quality.

The digits protocol is a local correctness gate, not an LLM-quality claim. The
final gate requires broader trained workloads and multiple seeds where quality
is used to justify a configuration.

### 7. Application integration

Integrate selected kernels into a real, reproducible training or inference path.
The serving path must cover real autoregressive execution, KV-cache correctness,
prefill/decode separation, batching or microbatching, bounded admission,
backpressure, cancellation semantics, streaming, and tail-load behavior.

The final comparison must trace a kernel-level change into application-level
behavior, including cases where a microbenchmark gain disappears end to end.
Supplied-vector replay, deterministic transport, untrained-model quality, and
production language quality remain separate claims.

### 8. Distributed and portable execution

Run real collectives, overlap, request dispatch, and MoE routing on suitable
multiple GPUs. Add a bounded comparison on a second accelerator stack, such as
ROCm/HIP, for a selected kernel.

Topology estimates, CPU simulations, one-rank smoke tests, and imported fixtures
are useful preparation but do not close this package. Hardware or paid
infrastructure requires explicit approval.

### 9. Publication and workbench

Generate the site from JSON artifacts. Publish navigable prerequisites, source
walkthroughs, derivations, tested exercises, reproduction commands, raw
evidence, limitations, and primary-source links.

The workbench must query by bottleneck, topic, concept, prerequisite, lesson,
paper, technique, hardware, or workload and return connected lessons, labs,
measurements, and next actions.

## Evidence contract

Every report declares one of:

`measured_cpu`, `measured_gpu`, `analytical`, `simulation`, `fixture`, or
`unavailable`.

Mixed reports label each row. A measured result must identify its reference,
candidate, inputs, correctness criteria, environment, command, timestamp,
warm-up, repeats, synchronization, timing scope, raw samples, and source
hashes. Reports must not silently promote modeled metrics, source-only compile
checks, imported samples, or unavailable hardware.

## Execution order

1. Keep the inventory and source registry current.
2. Maintain the CPU correctness/provenance checkpoint and reproduce it from a
   clean checkout.
3. Finish GEMM and attention evidence foundations.
4. Expand compiler/layout and low-precision experiments.
5. Connect selected kernels to trained quality and serving behavior.
6. Run approved CUDA/HIP, profiler, multi-GPU, and second-platform experiments.
7. Regenerate the site and perform the publication audit.

Research and implementation proceed within each package; a missing GPU does not
block local correctness, documentation, or source-quality work, but it does
block hardware acceptance.

## Current checkpoint and open gates

The current worktree has a passing hash-locked CPU checkpoint with 126 tests
across ten tracked suites and 27 experiment tasks (25 passed, two explicitly
unavailable). The evidence page is fresh,
and the GPUMODE workbench verifier passes. The checkpoint includes GEMM,
attention references, training/inference blocks, packed storage, neural serving
contracts, compiler execution, collective contracts, and MoE reference checks.

The repository also contains imported, hash-checked bounded T4 evidence. The
accepted GPU artifacts include a CUDA-graph decode candidate search with
profiler capture, trained synthetic-model serving, and trained graph-microbatch
tail-load waves. The corrected combined run
`colab-t4-trained-e2e-20260908` contains all three measured GPU reports under
one source/run identity. Together they form a real CUDA optimization-to-serving
vertical slice for the bounded teaching workload. They are not production
language-quality, production-capacity, multi-GPU, or second-platform evidence.

The imported `colab-full-20260908` T4 run also contains accepted bounded
attention-serving, FlashAttention-backward, and fused-training reports with
CUDA execution, numerical checks, memory/launch metrics, and profiler rows.
Those reports close the corresponding bounded teaching experiments; they do not
close broader architecture coverage, independent-host reproduction, or
production-scale claims.

Current accepted results are not final-goal acceptance. The current worktree
snapshot also passed the clean-snapshot reproduction gate; the authoritative
snapshot revision is recorded in `fresh-checkout-reproduction.json`. That proves
reproducibility of that captured source snapshot, not independent-host or GPU
execution. The
following remain open:

- independent-host reproduction beyond the local package/clean-snapshot gates;
- production-scale trained-model quality beyond the expanded synthetic matrix,
  local digits protocols, and the new local real-model CPU serving boundary;
- broader CUDA attention/training shapes, allocator attribution, and profiler
  explanations beyond the accepted bounded T4 reports;
- production-scale GPU capacity and allocator characterization beyond the
  accepted single-device tail-load waves;
- in-flight accelerator cancellation and resource accounting; the local
  cooperative CPU backend probe does not establish this accelerator claim;
- real multi-GPU collectives, MoE routing, and distributed serving;
- executed ROCm/HIP portability on a second accelerator stack;
- complete primary-source/prerequisite audit and final publication review.

The local environment currently lacks CUDA/HIP execution. That local absence is
recorded as unavailable; it is not a waiver of the remaining hardware gates and
does not invalidate the separately imported, accepted T4 artifacts.

## Final acceptance checklist

- [ ] All 24 topics have current capability and source records.
- [x] A clean-checkout reproduction retains raw logs, hashes, and commands.
- [x] At least one bounded CUDA vertical slice is numerically and profiler
      validated; broader attention/training coverage remains open.
- [x] Bounded attention forward/backward and memory claims are executed and
      scoped; broader shapes and attribution remain open.
- [ ] Compiler/layout/generated-kernel claims have held-out correctness.
- [ ] Low-precision claims combine storage, speed, drift, and quality.
- [x] Serving claims include bounded trained-model behavior and tail-load
      evidence; production-scale quality/capacity remains open.
- [ ] Multi-GPU collective/MoE behavior is measured, not modeled.
- [ ] A second accelerator stack has one executed portability comparison.
- [ ] The generated site and workbench pass freshness and coverage audits.
- [ ] Every remaining limitation is visible beside the relevant claim.

## Non-goals

This goal does not promise universal hardware support, production readiness,
state-of-the-art model quality, a specific accelerator vendor, or a benchmark
win for every optimization. It does not authorize remote jobs, paid
infrastructure, model downloads, commits, or pushes. Those require an explicit
decision and separate evidence.

## Navigation

- [Executable checkpoint](EXECUTABLE-CHECKPOINT.md)
- [Capability matrix](CAPABILITY-MATRIX.md)
- [Remaining-work audit](REMAINING-WORK.md)
- [Colab gate runbook](COLAB-GATE-RUNBOOK.md)
- [Exercises](EXERCISES.md)
- [Environment and reproduction notes](ENVIRONMENT.md)
