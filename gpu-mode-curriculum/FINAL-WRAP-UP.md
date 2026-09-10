# GPU Systems & Kernel Engineering program: final wrap-up

Date: 2026-09-10

## Why this report exists

The original objective was deliberately larger than a single kernel or serving
demo. We set out to build a reproducible GPU systems laboratory and learning
workbench that follows a workload from its mathematical definition through
implementation, profiling, optimization, application behavior, independent
reproduction, and a published engineering decision. The work was organized
around the 24-category GPU Systems & Kernel Engineering research handbook and
the integrated plan in `LONG-TERM-END-TO-END-GOAL.md`.

This report closes the current build at the hardware boundary we actually had.
It records what is proven, what is useful but scoped, what failed, and what
requires a multi-GPU or second-vendor machine. It intentionally does not turn
source files, CPU simulations, or one-rank smoke tests into claims about
hardware that was not available.

## The end-to-end chain we implemented

The work established a repeatable chain:

**pinned workload and quality target → independent reference → trusted
implementation → synchronized measurements → controlled intervention →
correctness and lifecycle checks → serving or training outcome → verifier and
source-bundle replay → decision and curriculum entry.**

The chain is represented in the repository by workload manifests, pinned model
revisions, reference generation, CUDA handoff scripts, raw JSON reports,
standalone verifiers, progress/status ledgers, and teaching notes. A report is
accepted only when its declared checks and evidence agree; a green local test
does not substitute for a missing accelerator measurement.

## What was built and proven

### Shared experiment and provenance foundation

The repository now contains a large runnable curriculum and experiment
workbench: lesson-level labs, comprehensive programs, kernel families,
measurement contracts, promotion logic, provenance reports, GPU handoff
scripts, regression ledgers, and HTML/tutorial outputs. The top-level acceptance
builder and verifier audit these contracts. At the latest audit, 39 of 40
criteria were accepted (390/400 points); the only failed criterion is the GPU
measurement queue because its distributed-collective and ROCm tasks lack valid
hardware completion. That score is a useful inventory, not a claim that the
long-term program is complete.

The most important reproducibility rule we adopted was to keep model identity
and source identity explicit. The main pretrained workload is
`EleutherAI/pythia-70m`, revision
`a39f36b100fe8a5377810d56c3f4789b9c53ac42`. GPT-2 remains the regression anchor;
the trained checkpoint and DistilGPT2 paths have their own pinned evidence.

### Inference and serving capstone

This is the most complete part of the program.

The original GPT-2 serving slice corrected padding, position handling, slot
accounting, continuous admission, graph/fixed-group controls, and HTTP
streaming. A real serving comparison used 4,608 offered requests: 2,256
completed and 2,352 were rejected under the declared overload policy, with zero
request failures. The result did not claim a generic custom-kernel speedup.

The Pythia path then added a generic Hugging Face slot adapter, architecture
characterization, native-versus-generic comparisons, synchronized CUDA timing,
admission and inter-tick profiling, and reusable preparation buffers. The
buffer optimization was measured twice and deliberately not promoted because
run-to-run variance erased the first apparent improvement. That was a useful
negative result: the code changed, the measurement repeated, and the decision
followed the evidence rather than the hoped-for speedup.

`NativeBatchBackend` gained a fixed-capacity Transformers `StaticCache` path
with explicit row compaction. A fixed-shape Pythia decode graph using SDPA
captured and replayed with exact eager token parity. An eager GPT-NeoX masking
path failed during capture because it constructed a CPU scalar; that failure is
recorded as a backend limitation rather than hidden.

The safe lifecycle is now explicit: reset and prefill a new cache, then
recapture. Reusing the same graph after reset and reprefill produced divergent
tokens. Recapture-per-bucket restored parity and was integrated into a bounded
HTTP service.

The final bounded serving implementation routes by tokenized prompt width and
output budget. It supports:

* fixed batch-two CUDA Graph buckets with StaticCache and SDPA;
* mixed prompt widths and mixed output budgets (four and eight tokens);
* bounded per-bucket pending queues and HTTP 429 overload responses;
* streaming token events and clean scheduler drain;
* singleton padding inside a fixed graph bucket;
* explicit `/cancel` handling;
* recapture timing and amortization metrics;
* eager/native fallback paths for cases that cannot use the graph bucket.

The A100 mixed-budget run passed exact parity for eight primary requests. A
12-request overload produced four HTTP 200 responses and eight bounded HTTP
429 responses. Three repeated rounds served 144 primary tokens and reduced
recapture overhead from 0.976 ms per primary token in the one-round run to
0.715 ms per token in the sustained run. These are loopback A100 measurements,
not production capacity numbers.

The cancellation race was tested twice. A controlled local backend regression
found and fixed a real late-row `KeyError` risk: after cancellation, an
in-flight backend may still emit rows for that request. The scheduler now
discards rows for requests no longer live while continuing the peer. The actual
A100 HTTP graph probe then received one token, accepted a separate `/cancel`
request, emitted `cancelled_inflight`, and drained cleanly.

Authoritative serving artifacts:

* `analysis/serving-capstone-decision.md` and `.json`
* `gpu-runs/imports/pythia-mixed-budget-backpressure-20260910T190000/reports/static-graph-http.json`
* `gpu-runs/imports/pythia-mixed-budget-sustained-20260910T200000/reports/static-graph-http.json`
* `gpu-runs/imports/pythia-static-graph-http-cancel-20260910T210000/reports/static-graph-http.json`
* `batch1-decode-vertical-slice/run_static_graph_http.py`
* `batch1-decode-vertical-slice/verify_static_graph_http.py`

The serving decision is therefore: promote the graph bucket as a bounded,
fixed-shape component on compatible CUDA hardware; retain native batching and
eager dynamic fallback; do not claim a universal graph-serving win.

### Training and numerical precision

The fused linear cross-entropy work includes custom forward/backward behavior,
derivative and quantization tests, and a real-data Tiny Shakespeare training
protocol. A T4 run used two seeds, 16 updates, sequence length 64, chunk size
16, full validation, and a selected checkpoint. Recomputed and standard
validation stayed within the declared tolerance; recomputation cost more time
per step while reducing activation pressure. The selected checkpoint was
loaded and served through the inference machinery, closing a training-to-
serving loop for that bounded workload.

The packed INT4 and quality artifacts separate storage, conversion, numerical
error, and application quality. The repository also contains optimizer,
training-framework, and low-precision experiments. These artifacts establish
the experimental spine; they do not imply that every format in the handbook
has native hardware support on the available machine.

### Kernel, layout, compiler, and profiling spine

The curriculum includes CUDA and Triton source families, reductions, scans,
sorting/compaction, GEMM, attention, fused training operations, layout algebra,
bank-conflict probes, persistent-kernel material, compiler/runtime inspection,
autotune records, and profiler interpretation. CPU contracts and available
CUDA runs are kept separate. The accepted evidence connects source changes to
correctness and measured behavior where hardware exists; unavailable Nsight,
ROCm, or architecture-specific instruction claims remain queued rather than
being inferred from source text.

### Distributed, multimodal, simulation, and portability preparation

The repository has substantial scaffolding and local contracts for collective
communication, MoE routing, topology planning, CXL/disaggregated-memory
questions, multimodal serving, GPU-resident simulation, and cross-vendor
execution. Those assets make the next experiments concrete, but they are not
closed capstones. In particular:

* the collective queue lacks accepted real multi-GPU execution;
* the ROCm/HIP task lacks an AMD runtime and profiler;
* a one-rank or CPU distributed run cannot establish communication benefit;
* source-level portability cannot establish a second-stack performance result;
* multimodal and simulator contracts still need complete application-level
  quality and learning measurements.

This is the central reason for wrapping up now: the available environment could
support single-GPU CUDA experiments, but not the hardware needed to close those
claims honestly.

## Key engineering findings

1. **Native batching was a strong baseline.** In matched Pythia comparisons it
   had lower synchronized model-call cost and better tail latency than the
   generic eager slot path. Continuous admission could still produce more
   useful throughput by keeping slots occupied, so per-call timing alone was
   not enough to choose a serving design.
2. **Graph capture is a lifecycle feature, not just a launch optimization.**
   StaticCache, fixed shapes, recapture policy, memory peak, and admission
   policy have to be designed together. Same-graph cache reuse was unsafe in the
   tested architecture.
3. **Shape and budget bucketing is a correctness boundary.** Isolating prompt
   width and output budget allowed exact graph inputs and explicit queue policy.
   The cost is bucket fragmentation and recapture work.
4. **Backpressure is part of correctness.** A bounded service must account for
   accepted, rejected, canceled, failed, and drained requests. The overload
   probe makes HTTP 429 behavior visible instead of hiding it in latency.
5. **Cancellation must be tested at event boundaries.** The late-row race was
   invisible in a happy-path completion test and only appeared when cancellation
   interleaved with a group stream.
6. **Optimization claims require repeated matched runs.** The reusable-buffer
   change was not promoted because its second run contradicted the first.
7. **Hardware scope changes the meaning of every result.** A100 graph and
   amortization values are recorded separately from T4 values. No T4 claim was
   invented after Colab repeatedly returned HTTP 412 assignment failures.

## What remains intentionally open

The following are handoff items, not hidden defects:

* repeat mixed-budget graph and cancellation measurements on T4 or the target
  deployment GPU;
* compare graph buckets, native batching, and eager fallback under matched
  duration, quality, latency, memory, and rejection targets;
* add prefix reuse, chunked prefill, fragmentation/eviction, fairness, and
  longer recovery tests;
* execute real two-or-more-GPU collectives and a small MoE workload with
  topology, overlap, routing skew, and failure accounting;
* execute a second accelerator stack, including compile/setup and performance;
* finish the multimodal and GPU-resident simulation capstones;
* refresh the GPU measurement queue after those hardware runs and regenerate
  the top-level acceptance audit.

## Reproduction handoff

The latest CUDA serving bundle can be rerun with:

```bash
cd /home/mehtama1/git-repo/ai-hardware-analysis/gpu-mode-curriculum
COLAB_GPU=A100 \
ARCHITECTURE_MODE=http-bucket-sustained \
COLAB_SESSION_NAME=pythia-mixed-budget-sustained-<timestamp> \
bash scripts/run_architecture_colab.sh
```

Use `ARCHITECTURE_MODE=http-bucket-cancel` for the cancellation probe. Set
`COLAB_GPU=T4` for a comparable T4 attempt when the allocator permits it. Each
run packages the dependency-closed source files, records the command log,
downloads the report archive, and runs its standalone verifier. The report
must be interpreted together with its recorded model revision and actual
device.

## Closing position

This build produced a serious, reproducible single-GPU CUDA serving and
training laboratory with real negative results, lifecycle diagnostics,
backpressure, cancellation, provenance, and teaching artifacts. It did not
complete the larger multi-GPU and cross-vendor research program because the
required hardware was unavailable. That boundary is part of the result. The
repository is ready for a future hardware-equipped continuation without
rewriting the experimental foundations or overstating what this environment
proved.
