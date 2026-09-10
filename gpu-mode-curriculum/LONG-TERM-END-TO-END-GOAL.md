# Long-term goal: GPU systems research, kernel engineering, and application performance

Status: **planned program; implementation incomplete**. Written 2026-09-09.

## The goal

Build a reproducible GPU systems engineering laboratory and learning workbench
that takes real workloads from mathematical definitions through kernel design,
compiler decisions, numerical precision, memory management, scheduling, and
distributed execution to measured application outcomes.

Someone using the finished system must be able to choose a model or workload,
reproduce a trusted baseline, identify its limiting resource, implement an
intervention, establish correctness and quality, measure the complete system,
and explain when the intervention helps or hurts. Every accepted result becomes
a usable implementation, a reproducible experiment, and a connected learning
path through GPUMODE lessons, papers, source code, and profiling evidence.

The central research question is:

> Which combinations of algorithms, kernels, numerical formats, compilation,
> memory layouts, and scheduling improve useful application work on a given
> hardware system—and why do those improvements change across workloads?

The end-to-end chain is:

**workload and quality target → mathematical reference → trusted implementation
→ bottleneck measurement → kernel/system change → correctness and quality
validation → application evaluation → independent reproduction → published
decision and curriculum integration.**

This is a sustained program with multiple capstones. Completing one experiment,
one serving endpoint, or the first capstone does not complete this goal.

## Starting point and relationship to earlier goals

The [original meaty goal](MEATY-GOAL.md) supplies the transcript corpus,
curriculum graph, paper bridges, runnable labs, and bottleneck workbench. The
[advanced lab goal](advanced-lab-phase/END-TO-END-GOAL.md) supplies foundational
implementation and evidence requirements. Preserve those assets and their open
requirements; this document defines the overarching program and integrated
acceptance criteria.

The [real-model inference slice](batch1-decode-vertical-slice/END-TO-END-GOAL.md)
has completed its six bounded gates. Its evidence includes pinned GPT-2,
corrected padding/position handling, native/custom comparisons, profiling,
actual HTTP microbatch serving, and a fresh-session source-bundle replay. Across
the two repeated HTTP sessions, all 512 main-load requests matched reference
tokens. Native batching consistently beat serial execution; custom attention
did not establish a reliable advantage over equally batched native execution.

That result is the experimental starting point. The existing endpoint runs
batches to completion. Mixed-batch cancellation retains slots until the batch
ends, and the recorded GPU cancellation probe is singleton. It does not establish
token-level continuous batching, sustained serving capacity, broad language
quality, multi-GPU execution, or cross-vendor portability.

## The finished system

1. A shared experiment foundation: workload manifests, reference oracles,
   correctness suites, measurement protocols, provenance, and reproduction.
2. A kernel engineering spine: primitives, GEMM, attention forward/backward,
   fused training operations, precision, layouts, compiler inspection, and tuning.
3. An inference capstone: a graph-enabled continuously batched model server
   with correct cache lifecycle and workload-dependent scheduling decisions.
4. A training capstone: a trained-model comparison linking custom backward,
   activation memory, precision, and optimizer choices to learning and time.
5. A distributed capstone: real multi-GPU collective and MoE execution with
   topology, routing, communication, and application-level measurements.
6. Two bounded application extensions: a multimodal serving pipeline and a
   GPU-resident simulation-to-policy-learning loop.
7. A portability and hardware study: executed comparisons on a second
   accelerator stack and an architecture-specific kernel investigation.
8. A research and learning workbench: queryable evidence, reproducible
   tutorials, source walkthroughs, and engineering portfolio assessments.

These components share workloads and artifacts. A new kernel should be usable
by a capstone; a capstone regression should produce a focused experiment; an
accepted experiment should update the workbench.

## A. Experimental science and trustworthy optimization

Build a common experiment contract. Each workload manifest specifies pinned
model/tokenizer identities where applicable, data splits, shapes, strides,
layouts, masks, dtype, output semantics, quality targets, hardware requirements,
and the reference implementation.

Correctness covers adversarial shapes, tails, noncontiguous inputs, masks,
non-finite values, tolerances, and nondeterminism where relevant. Serving adds
request identity, cancellation, reuse, and accounting; training adds gradients
and learning behavior. Memory/synchronization analysis supplements numerical
tests. Formal proofs, static checks, sanitizer runs, and empirical tests retain
their distinct scopes.

Record compilation, tuning, graph capture, conversion, and warm-up separately
from steady-state execution. Preserve synchronized raw samples, timing scope,
environment, source hashes, commands, seeds, allocator measurements, and traces.
Counterbalance candidates, measure variability, and evaluate held-out workloads.

**Acceptance:** accepted experiments reproduce from captured source and
dependency closures. Independent execution reproduces correctness and a
predeclared performance tolerance, or produces a resolved discrepancy report.
Validators reject stale sources, mismatched workloads, missing measurements,
and invalid outputs. Hash equality alone does not prove an experiment correct.

## B. Kernel, memory, layout, and compiler engineering

Develop a progression from reductions, scans, sorting/compaction, and tiled
GEMM to attention and fused model blocks. Compare simple references, trusted
libraries, and engineered implementations across small, large, rectangular,
and awkward workloads.

Investigate coalescing, bank conflicts, register pressure, occupancy, cache
behavior, arithmetic intensity, and synchronization. Connect generated code
and profiler observations to execution. Include a modern architecture study
of asynchronous movement and tensor-core pipelines on hardware supporting the
selected instructions. Source files for unavailable hardware do not close a gate.

Express selected common workloads in CUDA, Triton, and at least one additional
layout-oriented or scheduling-oriented DSL. Study explicit layout mappings and
invariants, fusion, graph breaks, conversion, specialization, and compile/runtime
tradeoffs. Implement a bounded autotuner with actual candidate execution and
held-out evaluation. Extend it to generated candidates after correctness and
benchmark controls exist; account for the cost of finding the best candidate.

**Acceptance:** GEMM, attention, and at least one parallel primitive have GPU
correctness, library comparisons, shape-dependent performance maps, and profiler
explanations. At least one engineered operation is evaluated inside a capstone.
DSL and generated-kernel comparisons retain source, compile results, rejected
candidates, and held-out outcomes. Include a reproducible fixed-budget tuning
challenge suitable for independent engineering assessment.

## C. Inference execution and serving capstone

Evolve the pinned baseline into an engine with persistent KV storage,
graph-based decode for supported shape buckets, and a documented fallback.
Measure setup cost, graph memory, bucket waste, launch overhead, and cache
movement before combining graphs with dynamic scheduling.

Implement token-level continuous batching: new requests enter between decode
steps; completed, EOS-terminated, and canceled requests release resources;
reused slots cannot expose another request's state. Add variable generation
lengths, bounded admission, backpressure, streaming, and mixed-request
cancellation. Investigate chunked prefill, prefix reuse, fragmentation, eviction,
and fairness as separate controlled interventions.

Preserve GPT-2 as the regression anchor and add a pinned pretrained workload
using the attention/cache architecture needed for the next experiment. Declare
its fit within the available hardware. Exercise short/long prompts, varied
outputs, bursts, steady arrivals, shared prefixes, memory pressure, overload,
and recovery. Compare with the native microbatch baseline and an established
compatible serving implementation under matched workload semantics.

**Acceptance:** GPU reference checks pass under slot reuse and mixed
cancellation. Repeated actual HTTP runs report TTFT, inter-token latency,
completion distributions, throughput, memory, rejections, cancellations, and
complete request accounting. Define goodput as requests meeting declared
latency and correctness targets per unit time. Publish its measured operating
envelope. Isolate kernel, graph, batching, and scheduling effects with ablations.
Independently replay the accepted experiment.

## D. Numerical precision and training capstone

Follow quantization through calibration or training, packed representation,
conversion/dequantization, native GPU execution, and application quality.
Separate weight-only and activation precision. Investigate sensitive operations,
accumulation, scaling, rounding, and error growth; use supported formats for
measured native execution claims.

Implement a meaningful custom forward/backward operation, such as fused linear
cross-entropy, normalization, or attention. Derive gradients, compare saving
activations with recomputation, and validate derivatives and model learning.
Evaluate at least one optimizer/update-rule alternative with meaningful matrix
operation costs under matched training budgets.

Run a pinned real-data training or fine-tuning workload. Record splits,
tokens/examples processed, seeds, initialization, optimizer state, failures,
evaluation quality, peak memory, and step time. Compare time to a declared
quality target and fixed-budget quality. If faster steps require more steps,
that must appear in the decision.

**Acceptance:** packed storage and actual execution are demonstrated;
conversion cost, error, held-out quality, and application throughput are reported
together. Custom backward passes derivative checks and multi-seed learning
comparisons. Evaluate at least one selected trained or quantized checkpoint
through the inference capstone, closing the training-to-serving loop.

## E. Distributed communication, MoE, and memory placement

Start with single-device routing/dispatch/combine references. Execute a small
real MoE workload on at least two GPUs. Record topology, link properties,
expert placement, routing skew, batch sizes, capacity, and overflow policy.
Compare sequential communication/computation with attempted overlap and explain
both with timelines and application measurements.

Measure relevant collectives across message sizes. Add distributed request
accounting, explicit failure/timeout semantics, and a controlled fault experiment
demonstrating termination or recovery without silent output loss.

Investigate prefill/decode or KV-memory disaggregation after establishing the
local baseline. Build a trace-driven movement/capacity model, then validate its
predictions against an actual available placement experiment. CXL or specialized
fabric claims require that hardware; an analytical study cannot establish a
measured fabric benefit.

**Acceptance:** real multi-GPU execution matches the reference within declared
tolerances; communication, routing imbalance, overlap, memory, and application
latency are measured. Publish when distribution helps and when overhead dominates.
CPU simulations and one-rank smoke tests do not close this package.

## F. Multimodal and GPU-resident application extensions

Build one bounded multimodal pipeline with actual encoder and generation work.
Exercise variable input sizes and separate encoder, transfer, prefill, and
decode costs. Compare coupled execution with staged scheduling, including
cross-modal request alignment and a defined output-quality check. Use real GPU
preprocessing or an analytics primitive from B where it serves the workload;
measure its contribution separately.

Build one small GPU-resident simulator with explicit transition semantics,
a CPU reference, reset/termination behavior, and batched environments. Integrate
policy inference, rollout storage, and learning. Measure host/device movement,
simulation throughput, full iteration time, and learning quality across seeds.
Choose an environment whose transitions can actually execute on GPU; a framework
name does not establish GPU residency.

**Acceptance:** the multimodal experiment demonstrates encoder-to-output
execution with scheduling and quality measurements. The simulator matches its
reference and produces reproducible learning; environment steps per second alone
do not establish a faster learning system.

## G. Portability and hardware/software tradeoffs

Execute at least one kernel family on a second accelerator software stack.
Preserve mathematical semantics and workloads while allowing architecture-specific
schedules. Compare correctness, compilation/setup, performance, memory, and
engineering changes. Explain differences with measured evidence.

Include one consumer/edge workload, possibly on the same second platform.
Bound its memory, startup, and latency targets; compare relevant precision and
execution options. Measure energy only with suitable telemetry and disclose its
sampling scope.

**Acceptance:** executed portability results, reproducible environments on both
platforms, and a workload-dependent performance explanation. Translation or a
source-only port is preparatory evidence. Missing hardware leaves the gate open.

## H. Research, teaching, and engineering portfolio

Maintain primary-source records for all 24 handbook categories. Search queries
are discovery inputs, not verified claims. Record source identity, access date,
supported claims, code/version links, prerequisites, and unresolved questions.
The supplied source/audio counts remain context until their underlying collection
is inventoried; do not imply every item was reviewed.

Generate tutorials containing derivations, source walkthroughs, runnable
exercises, reference checks, raw data, profile interpretation, failed hypotheses,
reproduction, and limits. Preserve bidirectional navigation among lessons,
papers, implementations, and results.

The workbench must answer queries such as “decode is slow at batch 4 on this
GPU” with measured regimes, competing hypotheses, runnable next experiments,
and hardware requirements. Distinguish locally established evidence, published
results, and untested proposals.

Map artifacts to kernel, compiler, numerics, serving, and distributed-systems
competencies. Include code walkthroughs, debugging exercises, system-design
reviews, and assessment rubrics. Hiring-market claims require dated sources;
interview lore does not establish engineering capability.

**Acceptance:** every category has source/capability records, every required
capstone has a complete learning path, and workbench freshness and navigation
pass validation. Another reader can reproduce a selected path without the
conversation history.

## Coverage of the 24 handbook categories

Coverage requires the deliverable and evidence specified above, not a keyword
match or empty starter.

| # | Handbook category | Required contribution |
| --- | --- | --- |
| 1 | Attention and long context | B/C: attention, cache, and context-length experiments |
| 2 | Quantization and low precision | D: storage-to-quality-to-serving comparison |
| 3 | GPU DSLs | B: shared workloads and compiler comparison |
| 4 | Distributed systems and collectives | E: topology-aware multi-GPU execution |
| 5 | Compiler tuning and fusion | B/C: tuning, graphs, application ablations |
| 6 | LLM serving | C: dynamic engine and measured load envelope |
| 7 | Profiling and microarchitecture | A/B: traces, counters, generated code, explanation |
| 8 | GPU reinforcement learning | F: rollout-to-learning measurements |
| 9 | Cross-vendor acceleration | G: executed second-stack comparison |
| 10 | Formal layouts and functional DSLs | B: mappings, invariants, tested schedules/lowering |
| 11 | Analytics, video, multimodal | B/F: GPU data primitive and actual multimodal pipeline |
| 12 | Correctness and observability | A/C: adversarial validation and execution/accounting |
| 13 | Optimizers and training | D: matched-budget update and learning comparison |
| 14 | Microarchitectural memory plumbing | B: architecture-specific movement/pipeline study |
| 15 | MoE and sparse computation | E: dispatch, expert compute, combine, skew |
| 16 | Automated kernel synthesis | B: generated-candidate search and held-out results |
| 17 | Disaggregated memory and co-design | E: placement model and measured validation |
| 18 | Parallel primitives | B: GPU scan/reduction/sort or compaction comparison |
| 19 | Consumer and edge hardware | G: bounded workload on consumer/edge hardware |
| 20 | Competitive kernel engineering | B/H: fixed-budget challenge and reproducible evaluation |
| 21 | Analytical autograd | D: derived backward and memory/learning evidence |
| 22 | Cross-modal routing | F: alignment and staged multimodal scheduling |
| 23 | GPU world simulation | F: resident transitions, parity, resets, learning |
| 24 | Engineering roles and interviews | H: evidence-backed portfolio and assessment |

Named papers, formats, and DSLs within categories are candidates, not a mandate
to implement every technology. Choose bounded representatives and document why
they answer the research question. Preserve this table's required contributions.

## Execution sequence and decision gates

1. **Consolidate foundations:** inventory accepted artifacts and outstanding
   advanced-lab requirements; establish shared workload/evidence contracts.
2. **Explain graph execution:** persistent decode state, capture/replay, buckets,
   and reference checks. Compare with native execution before changing scheduling.
3. **Complete dynamic serving:** token-level admission, reclamation, cancellation,
   sustained load, ablations, and independent replay.
4. **Complete training and precision:** connect backward, quality, memory, and
   time; deploy a selected checkpoint through serving.
5. **Complete distributed and hardware studies:** MoE/collectives, placement,
   architecture-specific kernels, and second-stack execution. Schedule according
   to suitable hardware availability; missing gates remain open.
6. **Complete application extensions and synthesis:** reuse primitives and
   runtime in multimodal/simulation work; evaluate generated kernels with the
   established correctness and application harnesses.
7. **Audit and publish:** independently reproduce capstones, reconcile coverage
   and earlier requirements, regenerate the site, and validate reader workflows.

Research and teaching proceed throughout. At each gate **retain, revise, or
reject** an intervention based on correctness, quality, total application cost,
and reproducibility. A reliable negative result completes an experiment; it
does not waive a missing system or required hardware execution.

## Final completion audit

- [ ] A–H meet their acceptance requirements with artifact paths and commands.
- [ ] All 24 categories have their required contributions and current sources.
- [ ] GPU GEMM, attention, and primitives explain library-relative behavior.
- [ ] Compiler/DSL and generated-kernel experiments include held-out evaluation.
- [ ] Inference runs token-level admission and safe resource reclamation.
- [ ] Mixed cancellation, EOS, overload, and slot reuse are validated on GPU.
- [ ] Sustained serving establishes a bounded latency/goodput operating envelope.
- [ ] Training/backward and precision link memory, speed, and held-out quality.
- [ ] A selected trained/quantized checkpoint passes through serving evaluation.
- [ ] Real multi-GPU MoE/collectives and placement are measured and explained.
- [ ] Second-stack and consumer/edge workloads have executed evidence.
- [ ] Multimodal and simulation-to-learning extensions are reproduced.
- [ ] Independent inference and training runs reproduce conclusions within
      declared tolerances, or resolved discrepancy reports explain differences.
- [ ] Tutorials, assessments, recommendations, and evidence are navigable and fresh.
- [ ] Earlier foundation requirements remain accounted for; no unfinished
      requirement disappeared through completion of a narrower slice.

Each checkpoint distinguishes **implemented**, **executed**, **measured**,
**independently reproduced**, and **still open**. Simulations, unavailable runs,
and estimates retain their labels beside claims. Inspect what tests and verifiers
actually prove; a green summary cannot establish a broader requirement.

## Boundaries and working rules

This program does not promise universal benchmark wins, every named handbook
technology, production readiness, or hardware-independent performance. It does
require the bounded systems, hardware comparisons, and evidence above.
Specialized fabric extensions beyond measured placement can remain future
research with explicit limits.

Preserve existing artifacts and unrelated work. Keep costs, hardware requirements,
and external actions visible. Writing this goal does not provision hardware or
publish changes; existing user authorization governs subsequent execution.

The first implementation milestone is real-model graph execution in C,
supported by A/B. The long-term goal remains the complete A–H program.
