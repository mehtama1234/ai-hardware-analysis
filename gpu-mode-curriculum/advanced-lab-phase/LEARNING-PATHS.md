# Prerequisite paths through executable labs

These paths cover implemented foundations, not all 24 topics at their full
research depth. Start with Python, matrix multiplication, tensor shapes and
basic differentiation. Use the [isolated environment](ENVIRONMENT.md); run
commands from the repository root. Hardware-dependent extensions remain open
even if every CPU exercise passes.

## Common foundation

Read the [evidence contract](END-TO-END-GOAL.md#evidence-contract), then inspect a
report through the [checkpoint walkthrough](EXECUTABLE-CHECKPOINT.md). Before
interpreting timing, identify the operation boundary, synchronization, warmup,
sample aggregation, reference tolerance and source identity. Before interpreting
memory, distinguish logical elements, backing storage, allocator peaks and device
traffic. These are different measurements.

## Core paths

| Path | Prerequisite sequence | Learner deliverable | Acceptance boundary |
|---|---|---|---|
| GEMM and memory | Shape/stride arithmetic → [GEMM references](../../gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/README.md) → [primitive scan/compaction](../parallel-primitives/README.md) → actual profiler capture | Explain a tail-shape bug and verify every output element; derive a tiling experiment | CPU correctness is available; tensor-core/SRAM/profiler explanations need device evidence |
| Attention training | Softmax derivative → [derivative exercise](EXERCISES.md#2-recompute-probabilities-without-losing-the-gradient) → [attention](../flash-attention-backward/README.md) → [transformer integration](../model-integration/README.md) | Compare output, input and parameter gradients, then optimizer states across steps | Synthetic equivalence and timing do not establish trained task quality |
| Compiler inspection | Tensor layouts/autograd → attention training path → [Inductor experiment](../compiler-runtime-inspection/README.md) | Locate generated forward/backward code; explain first-call versus steady-state timing and a measured loss | Captured CPU code does not prove CUDA/Triton/CuTe parity |
| Quantized inference | Binary packing/scales → [storage exercise](EXERCISES.md#1-why-four-bit-storage-is-not-always-an-eightfold-saving) → [packed inference and digits quality](../../gpu-kernels-serving-lab/08-quantized-inference/README.md) | Account for payload/scales/tails; report conversion-inclusive timing and held-out quality across seed pairs | Local integer format is not native INT4 compute, MXFP4 conformance or LLM quality |
| Serving | Causal attention → [cache-offset exercise](EXERCISES.md#3-a-causal-mask-must-follow-the-cache-position) → [paged-cache exercise](EXERCISES.md#4-page-a-kv-cache-without-changing-logical-sequence-order) → [neural backend](../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/NEURAL-BACKEND.md) → [batch/backpressure exercises](EXERCISES.md#5-distinguish-batching-from-backpressure) | Verify every cached logit and request isolation; distinguish vectorized batching, arrival-window grouping, queue rejection, cancellation, page-table ordering, and tail latency | Untrained CPU loopback serving and bounded T4 correctness kernels are not production capacity or language quality |
| Distributed experts | Rank/collective semantics → [collective outputs](../distributed-collectives/CPU-CORRECTNESS.md) → [request ownership exercise](EXERCISES.md#6-preserve-ownership-when-dispatching-requests-across-ranks) → [MoE routing/gradient semantics](../moe-routing-all-to-all/REFERENCE.md) → [sharded dispatch](../moe-routing-all-to-all/DISTRIBUTED.md) | Explain global capacity, preserve rank-major request ownership, handle an empty source rank, reject mismatched contracts and compare full outputs | Two CPU ranks do not establish GPU overlap, multi-host scaling or distributed autograd |

## Exercise review rubric

Each deliverable should include a fixed input contract, an independent expected
result, at least one adversarial case, the exact reproduction command, and a
short statement of what the evidence does not prove. A deliberately incorrect
candidate must fail the stated check. Do not improve a result by changing its
oracle, excluding failed cases or loosening tolerances after seeing outputs.

Performance explanations require repeated measurements of the same workload,
including compilation and conversion costs in separately named scopes. A slower
candidate is a valid result. A passing schema check, source-shaped fixture or
modeled speedup is not a measured optimization.

The written explanations are learner review tasks, not automatically accepted
by unit tests. Existing tests provide executable examples, not complete course
grading or proof that every prerequisite has been taught.

## Specialist extensions

Follow the [elective audit](ELECTIVE-AUDIT.md) after the relevant core path:
layout theory follows indexing/primitives; accelerated RL and physics need a
state-transition oracle; video/multimodal pipelines build on request identity
and staging; consumer platforms and CXL need appropriate hardware. The
[profiling/search audit](PROFILING-SEARCH-AUDIT.md) specifies the missing measured
search/profiler work. Primary-source review and full elective lessons remain
separate required work, not optional substitutions for the original goal.
