# GPUMODE Curriculum Expansion

This track turns GPUMODE's YouTube lectures into a transcript-backed GPU systems
curriculum that can feed deeper runnable labs in `gpu-kernels-serving-lab`. The
original curriculum objective is specified in `MEATY-GOAL.md`.

The [long-term end-to-end goal](LONG-TERM-END-TO-END-GOAL.md) defines the broader
research and engineering program: kernels and compilers through dynamic serving,
training and precision, distributed MoE, portability, multimodal execution, and
GPU simulation. It maps all 24 handbook categories to deliverables and final
acceptance criteria. The completed inference slice below is its starting point.

Execution has started; the [long-term progress ledger](LONG-TERM-PROGRESS.md)
tracks the full program separately from completed slices. Execution progressed
from fixed-cache graph decoding to token-level continuous admission and matched
serving comparisons.
The [graph-decode decision](analysis/graph-decode-decision.md) now records matched
profiles, pretrained correctness, and a verified fresh-session source-bundle
replay for the fixed-batch experiment.
The [slot and HTTP extension](batch1-decode-vertical-slice/SLOT-DECODE.md) now
passes a bounded GPU proof of cancellation, reclaimed-slot reuse, and admission
while a peer remains active. Sustained-load capacity and dynamic-engine replay
remain open; see the [functional decision](analysis/continuous-admission-decision.json).
The [mixed-length arrival measurements](analysis/continuous-load-decision.md)
add per-request budgets, controlled EOS, and repeated bounded load windows with
verified rejection and goodput accounting. Independent replay of the dynamic
engine remains open.
The [matched serving comparison](analysis/matched-serving-decision.md) now
compares compacting native microbatching, graph microbatching, and continuous
graph admission under identical offered workloads. Its bounded measurements
validate; independent replay of this dynamic comparison remains open.
The [training-loss implementation](fused-training-kernels/LINEAR-CROSS-ENTROPY.md)
adds chunked logit recomputation with an analytical backward and CPU derivative/
optimizer checks. A two-seed, 16-update real-data CUDA quality capture now passes
on a T4, and a selected checkpoint has completed a CUDA serving smoke. Multi-request
capacity from that checkpoint also passes the mixed-arrival verifier; matched
baseline comparison also passes with native, graph-group, and continuous controls.
Its dependency-closed source bundle also replays successfully in isolation.
The same load contract now passes on a pinned DistilGPT2 model as well.
A Pythia-70M GPT-NeoX characterization now passes cached-path parity on CUDA
for batch sizes 1, 2, and 4, and the generic `HFSlotDecode` adapter passes the
same mixed-arrival load contract. Its uncached batch-4 numerical divergence
remains documented; its generic dynamic slot load and native-vs-generic
comparison also pass correctness, while optimization and broader workloads remain
the next gates.
Its protocol and evidence are recorded in the
[long-term progress ledger](LONG-TERM-PROGRESS.md).

The [real-model inference decision](site/real-model-inference-decision.html)
now closes one bounded loop from pretrained GPT-2 correctness through GPU
profiling, custom-kernel optimization, actual HTTP serving, and fresh-session
source-bundle reproduction. All 512 main-load requests match the reference;
native microbatching is the selected path. The
[six-gate audit](analysis/real-model-goal-audit.json) records the proof and scope.

## Advanced executable expansion

The active [end-to-end goal](advanced-lab-phase/END-TO-END-GOAL.md) builds on this
curriculum with measured GEMM, attention derivatives/recomputation, packed-weight
quality checks, neural serving, and compiled training integration. Begin with
the [checkpoint walkthrough](advanced-lab-phase/EXECUTABLE-CHECKPOINT.md).
Analytical reports and CPU measurements are not interchangeable with GPU evidence.

The [learning paths](advanced-lab-phase/LEARNING-PATHS.md) order the implemented
labs by prerequisites, learner deliverables and evidence limits.
The [exercises](advanced-lab-phase/EXERCISES.md) link derivations to tested
reference implementations. The [partial source registry](advanced-lab-phase/SOURCE-REGISTRY.md)
records which primary-source claims were reviewed and which remain unverified.
The [capability matrix](advanced-lab-phase/CAPABILITY-MATRIX.md) maps inspected
artifacts to handbook topics, prerequisites, checks and missing evidence.
Use the [remaining-work audit](advanced-lab-phase/REMAINING-WORK.md) to distinguish
the current CPU checkpoint from the full advanced GPU curriculum goal.

## What This Adds

- `scripts/download_gpumode_transcripts.py` captures channel metadata with `yt-dlp`,
  downloads VTT captions when available, cleans them, and writes a transcript index.
- `scripts/build_curriculum.py` classifies lessons into CUDA, Triton, PyTorch compiler,
  profiling, attention, quantization, serving, and hardware topics, then extracts
  deterministic lesson-intelligence records and a prerequisite/topic graph.
- `build_site.py` renders a browsable curriculum site from generated JSON artifacts.
- `scripts/build_workbench.py` joins lessons, labs, paper records, and latest local
  measurement JSON into bottleneck-specific recommendations, including curated
  official CUDA, Triton, ROCm/HIP, JAX Scaling Book, and Hugging Face tutorial
  sources.
- `scripts/query_workbench.py` accepts a model/operator/bottleneck phrase and prints
  the matching lessons, labs, measurements, and papers.
- `scripts/query_curriculum_graph.py` traverses the generated graph from a topic,
  concept, prerequisite, lesson, or lab phrase.
- `scripts/query_corpus_bridge.py` queries the generated bridge between GPUMODE
  lessons and the AI-hardware paper corpus.
- `scripts/query_measurements.py` queries the normalized latest local measurement
  index across all lab artifacts, including runtime skip reasons.
- `scripts/gpu_workbench.py` is the unified programming interface: it diagnoses a
  GPU-systems query, returns lessons/labs/tutorials/papers/measurements, checks
  local runtime readiness, writes generated tutorials, and can run the known
  recommended lab.
- `scripts/gpu_workbench_api.py` exposes the same flow as importable functions
  for notebooks or other programs.
- `scripts/gpu_workbench_programs.py` provides concrete example programs on top
  of the API: batch triage, single-topic roadmaps, and evidence report export.
- `scripts/build_gpu_programming_projects.py` generates concrete project
  directories with starter programs, source files, measurement contracts, and
  README instructions for CUDA, Triton, ROCm/HIP, vLLM-style serving, JAX
  roofline, Hugging Face inference, Nsight evidence, and collectives tracks.
- `scripts/run_gpu_programming_projects.py` executes every generated starter,
  validates each project against its measurement contract, and writes consolidated
  JSON/Markdown run reports.
- `scripts/build_gpu_project_capstone.py` builds the portfolio-level dependency
  graph, execution order, milestones, runtime caveats, and capstone report across
  all generated programming projects.
- `scripts/build_gpu_project_notebooks.py` writes one runnable Jupyter notebook
  per generated programming project plus a notebook index.
- `scripts/build_lesson_labs.py` performs the 118-lesson lab gap analysis and
  generates one runnable lesson-lab scaffold per GPUMODE lesson under
  `lesson-labs/`.
- `scripts/run_lesson_labs.py` executes every generated lesson lab and validates
  the per-lab measurement contracts.
- `scripts/verify_lesson_labs.py` fails if any GPUMODE lesson lacks a lab,
  starter, measurement harness, task list, contract, or passing local
  measurement artifact.
- `scripts/build_comprehensive_lab_plan.py` maps all 118 lessons into a
  deliberate set of eight hand-written comprehensive labs rather than treating
  every lesson as a separate one-off kernel.
- `comprehensive-labs/gpumode_lab_suite/` contains the actual comprehensive lab
  code for memory hierarchy, tiled attention, compiler/autotune, quantization,
  serving/KV cache, ROCm/HIP portability, distributed collectives, and profiler
  evidence.
- `scripts/run_comprehensive_labs.py` runs those eight comprehensive labs and
  writes durable measurement artifacts under `comprehensive-labs/measurements/`.
- `scripts/verify_comprehensive_labs.py` verifies 118/118 lesson coverage and
  all comprehensive lab measurements.
- `kernel-benchmarks/` adds a real kernel benchmark harness for vector memory,
  reductions, softmax, layernorm, matmul, and fused MLP families, with PyTorch
  local execution plus CUDA/Triton source files for accelerator promotion.
- `scripts/build_kernel_benchmark_plan.py` maps all 118 GPUMODE lessons to the
  benchmark families and writes `kernel-benchmarks/PLAN.md`.
- `scripts/run_kernel_benchmarks.py` runs the benchmark sweep and writes
  `kernel-benchmarks/reports/kernel-benchmark-report.json`.
- `scripts/verify_kernel_benchmarks.py` verifies benchmark results, timing
  fields, CUDA source coverage, and Triton source coverage.
- `compiler-runtime-inspection/` statically inspects CUDA, Triton, ROCm/HIP,
  and custom-op source for launch indexing, masks, shared memory, barriers,
  tensor-core hints, promotion commands, and source-level runtime risks.
- `scripts/run_compiler_runtime_inspection.py` writes the compiler/runtime
  inspection JSON and Markdown report.
- `scripts/verify_compiler_runtime_inspection.py` verifies source coverage,
  feature coverage, promotion commands, and site integration.
- `tensor-core-gemm/` plans CUTLASS/CuTe-style tensor-core GEMM kernels across
  CTA, warp, MMA, pipeline, quantized operand, and fused epilogue choices.
- `scripts/run_tensor_core_gemm.py` writes the tensor-core GEMM JSON and
  Markdown report.
- `scripts/verify_tensor_core_gemm.py` verifies tensor-core eligibility,
  shared-memory budgets, register-pressure proxy, fused epilogue coverage, and
  site integration.
- `serving-traces/` adds vLLM-style request trace fixtures plus a deterministic
  replay simulator for TTFT, TPOT, output-token throughput, prefix-cache block
  savings, and peak live KV-cache pressure.
- `scripts/run_serving_traces.py` compares static batching against continuous
  batching with prefix-cache reuse and writes `serving-traces/reports/`.
- `scripts/verify_serving_traces.py` verifies trace coverage, policy comparison,
  serving metrics, prefix-cache accounting, and site integration.
- `kv-cache-paged-attention/` compares contiguous KV reservation with
  PagedAttention-style block tables for fragmentation, prefix reuse, eviction,
  admission pressure, and GPU-serving promotion.
- `scripts/run_kv_cache_paged_attention.py` writes the KV-cache allocator JSON
  and Markdown report.
- `scripts/verify_kv_cache_paged_attention.py` verifies allocator scenarios,
  block accounting, prefix reuse, source reports, and site integration.
- `attention-serving-stack/` connects FlashAttention online-softmax tiling with
  vLLM-style prefill/decode scheduling, KV reuse, CUDA Graph bucket fit,
  numerical tolerance, and GPU-host profiling promotion.
- `scripts/run_attention_serving_stack.py` writes the attention-serving JSON
  and Markdown report.
- `scripts/verify_attention_serving_stack.py` verifies HBM savings,
  shared-memory tile budgets, scheduler evidence, prefix reuse, and site
  integration.
- `flash-attention-backward/` models FlashAttention backward training kernels
  across dQ, dK, dV, dSoftmax, recompute, activation saving, dropout,
  grouped-query attention, gradient error, and GPU-host profiler promotion.
- `scripts/run_flash_attention_backward.py` writes the FlashAttention backward
  JSON and Markdown report.
- `scripts/verify_flash_attention_backward.py` verifies backward scenario
  coverage, gradient-path coverage, dropout/GQA cases, source reports, and site
  integration.
- `sparse-attention-kernels/` models block-sparse, sliding-window, dilated,
  ragged paged decode, neighborhood, and top-k attention kernels with metadata
  build cost, load balance, sparse backward support, numerical error, and
  GPU-host profiler promotion.
- `scripts/run_sparse_attention_kernels.py` writes the sparse attention JSON and
  Markdown report.
- `scripts/verify_sparse_attention_kernels.py` verifies sparse pattern
  coverage, ragged/decode coverage, backward coverage, load-balance thresholds,
  source reports, and site integration.
- `fused-training-kernels/` models fused LLM training kernels across
  RMSNorm/residual backward, SwiGLU MLP fusion, cross-entropy/z-loss,
  multi-tensor AdamW, grad clipping/unscale, dropout/residual/norm, checkpoint
  safety, launch reduction, HBM reduction, and GPU-host profiler promotion.
- `fused-training-kernels/REAL-DATA-TRAINING.md` documents the pinned corpus,
  full-split evaluator, real-model parity diagnostics, and checkpoint smoke.
- `scripts/run_training_colab.sh` runs the bounded two-seed CUDA training gate
  and imports a report-sized artifact from a fresh T4 session.
- `scripts/run_fused_training_kernels.py` writes the fused training kernel JSON
  and Markdown report.
- `scripts/verify_fused_training_kernels.py` verifies training-kernel family
  coverage, backward coverage, optimizer-state coverage, checkpoint-safe cases,
  source reports, and site integration.
- `speculative-decoding-serving/` models speculative decoding serving across
  draft/target verification, acceptance rate, rollback pressure, wasted draft
  tokens, KV commit accounting, TTFT, TPOT, throughput, scheduler policy, and
  GPU-host or Colab promotion.
- `scripts/run_speculative_decoding_serving.py` writes the speculative decoding
  JSON and Markdown report.
- `scripts/verify_speculative_decoding_serving.py` verifies speculative
  scenarios, engine coverage, scheduler-policy coverage, low-acceptance review
  coverage, source reports, and site integration.
- `advanced-lab-phase/` tracks the phase 2-7 plan: speculative decoding,
  multi-node training systems, compiler stack deep dive, quantized
  training/inference kernels, MoE end-to-end systems, and JAX scaling-book
  implementation for Colab/GPU execution.
- `scripts/verify_advanced_phase.py` verifies that phase 2-7 maps to concrete
  implemented evidence paths and GPU/Colab measurement steps.
- `scripts/bootstrap_colab_cli_auth.sh` installs/checks the Colab CLI and walks
  through OAuth without putting Google credentials in chat.
- `scripts/run_colab_gpu_handoff_local.sh` packages this curriculum, starts a
  Colab GPU session, uploads the bundle, runs `scripts/run_colab_gpu_handoff.py`
  remotely, downloads the GPU-run import JSON, and stops the session.
- `scripts/build_teaching_pages.py` writes first-principles teaching notes under
  `teaching/` and matching HTML pages under `site/`, with each note naming the
  question, code files, measured claim, and claim not proven.
- `scripts/verify_teaching_pages.py` checks that those notes include the required
  teaching sections and avoid stock vague phrases.
- `scripts/build_worked_walkthroughs.py` writes worked walkthroughs under
  `worked-walkthroughs/` and matching HTML pages under `site/`, using a
  predict, run, change, explain structure for the core labs.
- `scripts/verify_worked_walkthroughs.py` checks that walkthroughs reference real
  files, include runnable commands, and avoid stock vague phrases.
- `serving-engine-comparison/` compares vLLM, Hugging Face TGI, SGLang,
  TensorRT-LLM, and HF Transformers baseline across production inference
  scenarios using the serving trace replay metrics.
- `scripts/run_serving_engine_comparison.py` writes the engine comparison JSON
  and Markdown report.
- `scripts/verify_serving_engine_comparison.py` verifies engine coverage,
  scenario coverage, recommendations, metric estimates, and site integration.
- `distributed-topology/` plans tensor, pipeline, and data parallel deployment
  choices across single-GPU, PCIe, NVLink, and InfiniBand-style topologies.
- `scripts/run_distributed_topology.py` writes the topology and parallelism
  planning report.
- `scripts/verify_distributed_topology.py` verifies topology coverage, workload
  coverage, recommendations, memory estimates, collective estimates, and site
  integration.
- `distributed-collectives/` models all-reduce, reduce-scatter, all-gather,
  all-to-all, and broadcast algorithms across NCCL, RCCL, NVSHMEM, rank count,
  payload, topology bandwidth, latency, overlap, and GPU-host promotion.
- `scripts/run_distributed_collectives.py` writes the collective communication
  JSON and Markdown report.
- `scripts/verify_distributed_collectives.py` verifies collective coverage,
  backend coverage, overlap timing, bandwidth efficiency, and site integration.
- `scripts/run_distributed_collectives_benchmark.py` runs a
  `torch.distributed` collective benchmark under `torchrun` on GPU hosts and
  writes a local skip artifact on CPU-only hosts.
- `scripts/verify_distributed_collectives_benchmark.py` verifies the benchmark
  artifact schema and, when measured, requires accelerator-backed collective
  bandwidth rows.
- `distributed-training-optimizer/` models DDP, ZeRO, FSDP, tensor/pipeline
  parallelism, activation checkpointing, optimizer-state sharding,
  reduce-scatter/all-gather exposure, pipeline bubbles, and GPU-host
  promotion.
- `scripts/run_distributed_training_optimizer.py` writes the distributed
  training optimizer JSON and Markdown report.
- `scripts/verify_distributed_training_optimizer.py` verifies strategy
  coverage, checkpointing coverage, memory estimates, communication timing,
  pipeline bubble metrics, throughput, and site integration.
- `moe-routing-all-to-all/` models top-k expert routing for serving and
  training shapes, including load balance, capacity drops, all-to-all payload,
  fabric latency, bottleneck classification, and GPU-host promotion.
- `scripts/run_moe_routing_all_to_all.py` writes the MoE routing JSON and
  Markdown report.
- `scripts/verify_moe_routing_all_to_all.py` verifies scenario coverage,
  tuning-required cases, expert load histograms, all-to-all estimates, and site
  integration.
- `hardware-capacity-planning/` maps kernel, serving, long-context, batch
  inference, and training workloads to modeled GPU hardware classes with memory
  headroom, bottleneck, power, cost, and GPU-host validation commands.
- `scripts/run_hardware_capacity_plan.py` writes the capacity planning JSON and
  Markdown report.
- `scripts/verify_hardware_capacity_plan.py` verifies capacity coverage,
  recommendations, evaluation fields, source reports, and site integration.
- `quantization-memory-formats/` compares BF16, FP8-style, INT8, INT4, and NF4
  formats for compression, numerical drift, dequantization cost, serving fit,
  and GPU-host promotion.
- `scripts/run_quantization_memory_formats.py` writes the format-sweep JSON and
  Markdown report.
- `scripts/verify_quantization_memory_formats.py` verifies format coverage,
  accuracy gates, compression candidates, recommendations, and site integration.
- `numerical-reproducibility/` defines tolerance policy for deterministic,
  fast-math, low-precision, and reduction-order drift across CUDA/Triton/ROCm
  promotion paths.
- `scripts/run_numerical_reproducibility.py` writes the reproducibility JSON and
  Markdown report.
- `scripts/verify_numerical_reproducibility.py` verifies precision-mode
  coverage, repeatability, tolerance-review cases, reduction-order checks, and
  site integration.
- `cuda-graphs-latency/` models CUDA Graph capture eligibility, warmup,
  static-shape constraints, p95 latency reduction, jitter reduction, and
  fallback strategies for dynamic serving paths.
- `scripts/run_cuda_graphs_latency.py` writes the CUDA Graphs latency report.
- `scripts/verify_cuda_graphs_latency.py` verifies capture-ready coverage,
  fallback coverage, p95 latency reduction, source reports, and site integration.
- `multi-tenant-gpu-scheduling/` models MIG/MPS/Kubernetes-style GPU placement
  for serving, batch, CI, and training tenants with memory headroom, isolation,
  fairness, SLO fit, queue fallback, and GPU-host promotion commands.
- `scripts/run_multi_tenant_gpu_scheduling.py` writes the scheduling JSON and
  Markdown report.
- `scripts/verify_multi_tenant_gpu_scheduling.py` verifies policy coverage,
  tenant coverage, MIG/MPS coverage, placement schema, fairness, and site
  integration.
- `custom-ops/` adds a PyTorch custom operator lab for fused bias, GELU, and
  residual addition with CPU autograd fallback plus source-ready C++/CUDA
  extension files.
- `scripts/run_custom_ops.py` runs randomized forward/backward correctness cases
  and local timing for the custom operator.
- `scripts/verify_custom_ops.py` verifies custom-op reports, source files,
  accelerator readiness, and site integration.
- `persistent-kernels/` models persistent Triton/CUDA kernel design for
  softmax, matmul, grouped GEMM, normalization, and attention with occupancy,
  resident CTA, register pressure, shared memory, L2 reuse, launch amortization,
  and producer/consumer checks.
- `scripts/run_persistent_kernels.py` writes the persistent-kernel JSON and
  Markdown reports.
- `scripts/verify_persistent_kernels.py` verifies scenario coverage, design
  checks, profiler evidence requirements, GPU promotion, and site integration.
- `parallel-primitives/` models reduction, scan, compaction, radix sort,
  histogram, and segmented reduction with memory traffic, atomics, stable-order
  checks, occupancy, and profiler promotion requirements.
- `scripts/run_parallel_primitives.py` writes the primitive JSON and Markdown
  reports.
- `scripts/verify_parallel_primitives.py` verifies primitive coverage,
  stable-order coverage, GPU promotion, and site integration.
- `autotune-db/` converts kernel benchmark and custom-op reports into reusable
  tuning records with candidate configs, selected starting configs, estimated
  speedups, and CUDA/Triton/extension promotion targets.
- `scripts/build_autotune_db.py` builds the tuning database and can select a
  config by operator family and shape class.
- `scripts/verify_autotune_db.py` verifies autotune record coverage, selector
  invariants, non-regression estimates, and site integration.
- `model-integration/` adds a tiny causal transformer block that connects
  layernorm, QKV matmul, causal attention, the fused custom op, and autotune
  selections into a model-shaped benchmark.
- `scripts/run_model_integration.py` runs forward/backward correctness and
  timing cases for the tiny transformer block.
- `scripts/verify_model_integration.py` verifies model cases, gradient
  agreement, custom-op usage, autotune selections, and site integration.
- `regression-ledger/` collects stable metrics from kernel benchmarks, custom
  ops, autotune, model integration, and serving traces into one regression
  ledger.
- `scripts/build_regression_ledger.py` builds the ledger from current generated
  reports.
- `scripts/verify_regression_ledger.py` verifies metric coverage, thresholds,
  source links, and site integration.
- `gpu-promotion/` generates the ordered GPU-host promotion manifest for CUDA,
  Triton, custom-op extension, model integration, vLLM-style serving, profiler,
  ROCm/HIP, distributed, and full-regression runs.
- `scripts/build_gpu_promotion.py` writes the machine-readable manifest and
  Markdown runbook.
- `scripts/verify_gpu_promotion.py` verifies promotion steps, required
  capabilities, expected evidence, validations, and site integration.
- `scripts/run_gpu_promotion_suite.py` turns the GPU promotion manifest into a
  dry-run-safe command plan, or executes selected steps on a GPU host with
  `--execute`.
- `scripts/verify_gpu_promotion_suite.py` verifies the command plan, step
  coverage, expected evidence, placeholder handling, and suite report.
- `gpu-runs/` defines the import contract for real accelerator-host validation
  rows from NVIDIA and AMD GPU machines.
- `scripts/build_gpu_runs.py` consolidates GPU-host run JSON fixtures into a
  promotion-step-linked report.
- `scripts/collect_gpu_run.py` writes the same GPU-run import JSON shape from
  the current host after promotion commands have been run.
- `scripts/lint_gpu_run_imports.py` lints sample fixtures and collected imports
  for schema, provenance, measured flags, metrics, and evidence paths.
- `scripts/verify_gpu_runs.py` verifies imported run coverage, vendors, metrics,
  evidence links, promotion-step IDs, and site integration.
- `gpu-provenance/` separates sample fixtures, host-collected smoke data, and
  true measured accelerator-host evidence.
- `scripts/build_gpu_provenance.py` writes the GPU evidence provenance report.
- `scripts/verify_gpu_provenance.py` verifies provenance kinds, measured flags,
  sample accounting, host-collected accounting, and site integration.
- `gpu-measurement-queue/` turns GPU promotion steps into per-step measurement
  contracts with host class, required metrics, acceptance thresholds, and
  queued/measured status.
- `scripts/build_gpu_measurement_queue.py` writes the GPU measurement queue
  report.
- `scripts/verify_gpu_measurement_queue.py` verifies task coverage, metric
  contracts, executable threshold checks, evidence, and site integration.
- `scripts/verify_gpu_acceptance_logic.py` regression-tests every GPU
  measurement threshold against canonical accepted and rejected metric rows.
- `scripts/run_gpu_host_preflight.py` snapshots local accelerator tooling and
  classifies each GPU promotion step as runnable or blocked on this host.
- `scripts/verify_gpu_host_preflight.py` verifies the preflight report, blocked
  capability accounting, Markdown report, and site integration.
- `gpu-handoff/` packages the promotion suite, collector, bundle file list, and
  validation commands for accelerator-host execution.
- `scripts/build_gpu_handoff.py` writes the portable GPU-host handoff JSON,
  Markdown checklist, and shell entrypoint.
- `scripts/verify_gpu_handoff.py` verifies the handoff entrypoint, bundle files,
  validation commands, and site integration.
- `assessment/` turns the GPUMODE lesson map, official tutorial sources, and
  implemented lab evidence into a concept exam plus practical task bank.
- `scripts/build_assessment.py` writes `assessment/question-bank.json` and
  `assessment/reports/assessment-report.md`.
- `scripts/verify_assessment.py` verifies question coverage, tutorial-source
  coverage, practical task layers, grading checks, and site integration.
- `scripts/grade_assessment.py` scores concept-check readiness and practical
  task evidence against current generated artifacts.
- `scripts/verify_assessment_grading.py` verifies the grading report, full
  score, practical-layer coverage, and site integration.
- `capstone-acceptance/` grades the complete curriculum stack as a
  portfolio-grade end-to-end systems project with a scored rubric.
- `scripts/build_capstone_acceptance.py` writes the scored acceptance report.
- `scripts/verify_capstone_acceptance.py` verifies the rubric, score, evidence,
  status, and site integration.
- `scripts/build_runtime_matrix.py` classifies CPU, CUDA, Triton, ROCm/HIP,
  custom-op, autotune, model integration, serving, regression, GPU promotion, capstone acceptance, profiler, and distributed machine profiles with required capabilities,
  commands, evidence artifacts, and local fallback status.
- `scripts/verify_runtime_matrix.py` verifies the runtime matrix and the
  CPU-local evidence on this machine.
- `profiler-evidence/` adds Nsight Compute, Nsight Systems, and rocprof-shaped
  fixtures plus a parser that normalizes profiler rows into bottleneck classes
  and remediation actions.
- `scripts/run_profiler_evidence.py` writes the normalized profiler report.
- `scripts/verify_profiler_evidence.py` verifies profiler fixtures, parsed
  classifications, remediation actions, and site integration.
- `scripts/verify_gpu_workbench_program.py` verifies the programming layer.
- `scripts/verify_gpu_programming_projects.py` verifies generated project files
  and runs each starter harness.
- `scripts/verify_workbench.py` audits the generated corpus, lesson pages, bridge
  pages, lab artifacts, imported profiler/collective evidence, and workbench
  coverage as an end-to-end acceptance gate.
- `analysis/tutorial-exercise-paths.json` turns each bottleneck profile into a
  source-to-GPUMODE-to-lab-to-measurement exercise path.
- `scripts/build_end_to_end_audit.py` emits a requirement-to-evidence audit for
  the full GPUMODE workbench goal.
- The generated site includes one page per GPUMODE lesson, profile bridge pages,
  a one-lab-per-lesson coverage page, profile bridge pages, and paper-to-lesson
  links in the GPU systems workbench.
- `gpu-kernels-serving-lab/15-gpumode-coalescing` and
  `gpu-kernels-serving-lab/16-gpumode-warp-reductions` and
  `gpu-kernels-serving-lab/17-gpumode-triton-autotune` and
  `gpu-kernels-serving-lab/18-gpumode-online-softmax` and
  `gpu-kernels-serving-lab/19-gpumode-torch-compile` and
  `gpu-kernels-serving-lab/20-gpumode-vllm-scheduler` and
  `gpu-kernels-serving-lab/21-gpumode-quantized-kernels` and
  `gpu-kernels-serving-lab/22-gpumode-nsight-roofline` and
  `gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm` and
  `gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass` and
  `gpu-kernels-serving-lab/25-gpumode-rocm-hip-portability` and
  `gpu-kernels-serving-lab/26-gpumode-distributed-communication` are the first
  implemented GPUMODE-derived deep labs.
- `DEEP-BUILD-PLAN.md` lays out the deeper projects to build from the lesson map.
- `LESSON-LAB-GOAL.md` specifies the full one-lab-per-lesson implementation goal.

## Run

```bash
cd gpu-mode-curriculum
python3 scripts/download_gpumode_transcripts.py --metadata-only
python3 scripts/build_curriculum.py
python3 scripts/build_workbench.py
python3 scripts/build_gpu_programming_projects.py
python3 scripts/run_gpu_programming_projects.py
python3 scripts/build_gpu_project_notebooks.py
python3 scripts/build_gpu_project_capstone.py
python3 scripts/build_lesson_labs.py
python3 scripts/run_lesson_labs.py
python3 scripts/build_comprehensive_lab_plan.py
python3 scripts/run_comprehensive_labs.py
python3 scripts/build_kernel_benchmark_plan.py
python3 scripts/run_kernel_benchmarks.py
python3 scripts/run_compiler_runtime_inspection.py
python3 scripts/run_tensor_core_gemm.py
python3 scripts/run_persistent_kernels.py
python3 scripts/run_parallel_primitives.py
python3 scripts/run_custom_ops.py
python3 scripts/build_autotune_db.py
python3 scripts/run_model_integration.py
python3 scripts/run_serving_traces.py
python3 scripts/run_serving_engine_comparison.py
python3 scripts/run_distributed_topology.py
python3 scripts/run_distributed_collectives.py
python3 scripts/run_distributed_collectives_benchmark.py
python3 scripts/run_distributed_training_optimizer.py
python3 scripts/build_regression_ledger.py
python3 scripts/build_gpu_promotion.py
python3 scripts/run_gpu_promotion_suite.py --run-id local-suite-dry-run
python3 scripts/lint_gpu_run_imports.py
python3 scripts/build_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/run_gpu_host_preflight.py
python3 scripts/build_gpu_handoff.py
python3 scripts/build_assessment.py
python3 scripts/grade_assessment.py
python3 scripts/run_profiler_evidence.py
python3 scripts/build_teaching_pages.py
python3 scripts/build_worked_walkthroughs.py
python3 build_site.py
python3 scripts/build_end_to_end_audit.py
python3 scripts/build_capstone_acceptance.py
python3 scripts/build_runtime_matrix.py
python3 build_site.py
python3 scripts/build_end_to_end_audit.py
python3 scripts/build_capstone_acceptance.py
python3 scripts/build_runtime_matrix.py
python3 build_site.py
python3 scripts/verify_workbench.py
python3 scripts/verify_gpu_workbench_program.py
python3 scripts/verify_gpu_programming_projects.py
python3 scripts/verify_lesson_labs.py
python3 scripts/verify_comprehensive_labs.py
python3 scripts/verify_kernel_benchmarks.py
python3 scripts/verify_compiler_runtime_inspection.py
python3 scripts/verify_tensor_core_gemm.py
python3 scripts/verify_persistent_kernels.py
python3 scripts/verify_parallel_primitives.py
python3 scripts/verify_custom_ops.py
python3 scripts/verify_autotune_db.py
python3 scripts/verify_model_integration.py
python3 scripts/verify_serving_traces.py
python3 scripts/verify_kv_cache_paged_attention.py
python3 scripts/verify_attention_serving_stack.py
python3 scripts/verify_serving_engine_comparison.py
python3 scripts/verify_distributed_topology.py
python3 scripts/verify_distributed_collectives.py
python3 scripts/verify_distributed_collectives_benchmark.py
python3 scripts/verify_distributed_training_optimizer.py
python3 scripts/verify_moe_routing_all_to_all.py
python3 scripts/verify_hardware_capacity_plan.py
python3 scripts/verify_quantization_memory_formats.py
python3 scripts/verify_numerical_reproducibility.py
python3 scripts/verify_cuda_graphs_latency.py
python3 scripts/verify_multi_tenant_gpu_scheduling.py
python3 scripts/verify_regression_ledger.py
python3 scripts/verify_gpu_promotion.py
python3 scripts/verify_gpu_promotion_suite.py
python3 scripts/lint_gpu_run_imports.py
python3 scripts/verify_gpu_runs.py
python3 scripts/verify_gpu_provenance.py
python3 scripts/verify_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/verify_gpu_host_preflight.py
python3 scripts/verify_gpu_handoff.py
python3 scripts/verify_runtime_matrix.py
python3 scripts/verify_profiler_evidence.py
python3 scripts/verify_teaching_pages.py
python3 scripts/verify_worked_walkthroughs.py
python3 scripts/verify_assessment.py
python3 scripts/verify_assessment_grading.py
python3 scripts/verify_capstone_acceptance.py
```

Or run the whole refresh plus verification gate:

```bash
python3 run_all.py
```

Query the generated workbench:

```bash
python3 scripts/gpu_workbench.py "kv cache decode latency"
python3 scripts/gpu_workbench.py "triton fused softmax" --json
python3 scripts/gpu_workbench.py "nccl all reduce bandwidth" --run-lab --dry-run
python3 scripts/gpu_workbench.py "tensor core quantization" --tutorial
python3 scripts/gpu_workbench.py --doctor
python3 scripts/gpu_workbench_programs.py batch-triage
python3 scripts/gpu_workbench_programs.py roadmap "triton fused softmax"
python3 scripts/gpu_workbench_programs.py evidence-report "nsight roofline dram counters"
python3 scripts/build_gpu_programming_projects.py
python3 scripts/run_gpu_programming_projects.py
python3 scripts/build_gpu_project_notebooks.py
python3 scripts/build_gpu_project_capstone.py
python3 scripts/verify_gpu_programming_projects.py
python3 scripts/build_lesson_labs.py
python3 scripts/run_lesson_labs.py
python3 scripts/verify_lesson_labs.py
python3 scripts/build_comprehensive_lab_plan.py
python3 scripts/run_comprehensive_labs.py
python3 scripts/verify_comprehensive_labs.py
python3 scripts/build_kernel_benchmark_plan.py
python3 scripts/run_kernel_benchmarks.py
python3 scripts/verify_kernel_benchmarks.py
python3 scripts/run_compiler_runtime_inspection.py
python3 scripts/verify_compiler_runtime_inspection.py
python3 scripts/run_custom_ops.py
python3 scripts/verify_custom_ops.py
python3 scripts/build_autotune_db.py
python3 scripts/build_autotune_db.py --select-family matmul --select-shape medium-square
python3 scripts/verify_autotune_db.py
python3 scripts/run_model_integration.py
python3 scripts/verify_model_integration.py
python3 scripts/run_serving_traces.py
python3 scripts/verify_serving_traces.py
python3 scripts/run_attention_serving_stack.py
python3 scripts/verify_attention_serving_stack.py
python3 scripts/run_flash_attention_backward.py
python3 scripts/verify_flash_attention_backward.py
python3 scripts/run_sparse_attention_kernels.py
python3 scripts/verify_sparse_attention_kernels.py
python3 scripts/run_fused_training_kernels.py
python3 scripts/verify_fused_training_kernels.py
python3 scripts/run_speculative_decoding_serving.py
python3 scripts/verify_speculative_decoding_serving.py
python3 scripts/run_serving_engine_comparison.py
python3 scripts/verify_serving_engine_comparison.py
python3 scripts/run_distributed_topology.py
python3 scripts/verify_distributed_topology.py
python3 scripts/run_distributed_collectives.py
python3 scripts/verify_distributed_collectives.py
torchrun --nproc_per_node=2 scripts/run_distributed_collectives_benchmark.py
python3 scripts/verify_distributed_collectives_benchmark.py
python3 scripts/run_distributed_training_optimizer.py
python3 scripts/verify_distributed_training_optimizer.py
python3 scripts/build_regression_ledger.py
python3 scripts/verify_regression_ledger.py
python3 scripts/build_gpu_promotion.py
python3 scripts/verify_gpu_promotion.py
python3 scripts/run_gpu_promotion_suite.py --run-id local-suite-dry-run
python3 scripts/verify_gpu_promotion_suite.py
python3 scripts/lint_gpu_run_imports.py
python3 scripts/build_gpu_runs.py
python3 scripts/verify_gpu_runs.py
python3 scripts/build_gpu_provenance.py
python3 scripts/verify_gpu_provenance.py
python3 scripts/build_gpu_measurement_queue.py
python3 scripts/verify_gpu_measurement_queue.py
python3 scripts/verify_gpu_acceptance_logic.py
python3 scripts/run_gpu_host_preflight.py
python3 scripts/verify_gpu_host_preflight.py
python3 scripts/build_gpu_handoff.py
python3 scripts/verify_gpu_handoff.py
python3 scripts/build_assessment.py
python3 scripts/verify_assessment.py
python3 scripts/grade_assessment.py
python3 scripts/verify_assessment_grading.py
python3 scripts/build_capstone_acceptance.py
python3 scripts/verify_capstone_acceptance.py
python3 scripts/verify_advanced_phase.py
python3 scripts/build_runtime_matrix.py
python3 scripts/verify_runtime_matrix.py
python3 scripts/run_profiler_evidence.py
python3 scripts/verify_profiler_evidence.py
python3 scripts/build_teaching_pages.py
python3 scripts/verify_teaching_pages.py
python3 scripts/build_worked_walkthroughs.py
python3 scripts/verify_worked_walkthroughs.py
python3 scripts/query_workbench.py "kv cache decode latency"
python3 scripts/query_workbench.py "triton matmul autotune" --json
python3 scripts/query_workbench.py "vllm scheduler ttft kv cache"
python3 scripts/query_workbench.py "int4 quantized matmul error"
python3 scripts/query_workbench.py "nsight roofline dram sm stall counters"
python3 scripts/query_workbench.py "rocm hip cuda portability wmma"
python3 scripts/query_workbench.py "nccl nvshmem all-reduce distributed communication"
python3 scripts/query_workbench.py "jax scaling roofline gpu hbm"
python3 scripts/query_workbench.py "hugging face tgi vllm continuous batching"
```

Query the generated prerequisite/topic graph:

```bash
python3 scripts/query_curriculum_graph.py "cuda memory coalescing"
python3 scripts/query_curriculum_graph.py "triton fused softmax lab" --json
python3 scripts/query_curriculum_graph.py "multi gpu collectives prerequisites"
```

Query lesson-to-corpus links:

```bash
python3 scripts/query_corpus_bridge.py "llm inference gpu memory"
python3 scripts/query_corpus_bridge.py "tensor core quantization" --json
```

Query latest local measurements:

```bash
python3 scripts/query_measurements.py "cuda skipped triton vllm"
python3 scripts/query_measurements.py "nsight imported collective correctness" --json
```

Generated pages are under `site/`:

- `index.html`: topic map, lab backlog, workbench summary, and GPUMODE lesson list.
- `analysis/curriculum-graph.json`: generated lesson/topic/concept/prerequisite/lab
  graph with practical topic order.
- `workbench.html`: searchable bottleneck-to-lessons/labs/papers/measurements view.
- `analysis/tutorial-sources.json`: curated CUDA, Triton, ROCm/HIP, JAX Scaling
  Book, and Hugging Face tutorial registry used by the generated workbench.
- `analysis/tutorial-exercise-paths.json`: generated end-to-end exercise paths
  for each bottleneck profile.
- `analysis/lesson-corpus-bridges.json`: generated bidirectional links between
  GPU-relevant corpus papers and GPUMODE lessons.
- `analysis/latest-measurements-index.json`: normalized status, correctness,
  runtime-readiness, skip, summary, and page rows for lab artifacts.
- `analysis/end-to-end-audit.json` and `analysis/end-to-end-audit.md`:
  requirement-to-evidence audit with explicit runtime caveats.
- `compiler-runtime-inspection/compiler-runtime-report.json` and
  `compiler-runtime-inspection/reports/compiler-runtime-report.md`: source-level
  compiler/runtime inspection across CUDA, Triton, ROCm/HIP, and custom-op code.
- `tensor-core-gemm/tensor-core-gemm-report.json` and
  `tensor-core-gemm/reports/tensor-core-gemm-report.md`: CUTLASS/CuTe-style
  tensor-core GEMM planner with CTA/warp/MMA tiling, pipeline staging,
  quantized operands, fused epilogues, and profiler promotion.
- `serving-engine-comparison/serving-engine-comparison.json` and
  `serving-engine-comparison/reports/serving-engine-comparison.md`:
  scenario-weighted production inference comparison across vLLM, TGI, SGLang,
  TensorRT-LLM, and HF Transformers baseline.
- `kv-cache-paged-attention/kv-cache-report.json` and
  `kv-cache-paged-attention/reports/kv-cache-report.md`: KV-cache allocator
  analysis for PagedAttention block tables, fragmentation, prefix reuse,
  eviction, and admission pressure.
- `attention-serving-stack/attention-serving-report.json` and
  `attention-serving-stack/reports/attention-serving-report.md`:
  FlashAttention-to-vLLM serving stack analysis for tiled online softmax,
  prefill/decode scheduling, KV reuse, graph bucket fit, and profiling
  promotion.
- `flash-attention-backward/flash-attention-backward-report.json` and
  `flash-attention-backward/reports/flash-attention-backward-report.md`:
  FlashAttention backward training-kernel model with dQ/dK/dV/dSoftmax paths,
  recompute overhead, saved-activation reduction, dropout/GQA cases, gradient
  error checks, and GPU-host profiling promotion.
- `sparse-attention-kernels/sparse-attention-report.json` and
  `sparse-attention-kernels/reports/sparse-attention-report.md`: sparse
  attention kernel model for block-sparse, sliding-window, dilated,
  ragged-paged, neighborhood, and top-k attention with metadata overhead,
  load-balance, HBM reduction, decode, backward, and profiler promotion.
- `fused-training-kernels/fused-training-report.json` and
  `fused-training-kernels/reports/fused-training-report.md`: fused LLM
  training-kernel model for norm, MLP, loss, optimizer, grad-scale, and
  checkpoint-safe fusion with launch/HBM reduction and profiler promotion.
- `speculative-decoding-serving/speculative-decoding-report.json` and
  `speculative-decoding-serving/reports/speculative-decoding-report.md`:
  speculative decoding serving model for draft/target verification, acceptance
  rate, rollback pressure, wasted draft tokens, KV commits, scheduler policy,
  TTFT/TPOT, throughput, and Colab/GPU-host promotion.
- `advanced-lab-phase/phase-2-7-plan.json` and
  `advanced-lab-phase/PHASE-2-7-PLAN.md`: explicit implementation plan for the
  remaining advanced lanes and their Colab measurement handoff.
- `distributed-topology/distributed-topology-plan.json` and
  `distributed-topology/reports/distributed-topology-plan.md`: topology and
  parallelism plan for serving/training workloads across PCIe, NVLink, and
  InfiniBand-style GPU fabrics.
- `distributed-collectives/distributed-collectives-report.json` and
  `distributed-collectives/reports/distributed-collectives-report.md`:
  algorithm-level collective communication model for NCCL/RCCL/NVSHMEM
  bandwidth, latency, overlap, and GPU-host promotion.
- `distributed-collectives/reports/collective-benchmark-run.json`: local or
  GPU-host `torch.distributed` benchmark artifact for measured collectives.
- `distributed-training-optimizer/distributed-training-optimizer-report.json`
  and
  `distributed-training-optimizer/reports/distributed-training-optimizer-report.md`:
  distributed training optimizer model for DDP, ZeRO, FSDP, checkpointing,
  communication exposure, and pipeline bubble tradeoffs.
- `persistent-kernels/persistent-kernels-report.json` and
  `persistent-kernels/reports/persistent-kernels-report.md`: persistent
  Triton/CUDA kernel design model with occupancy, residency, launch
  amortization, L2 reuse, HBM reduction, and profiler promotion requirements.
- `parallel-primitives/parallel-primitives-report.json` and
  `parallel-primitives/reports/parallel-primitives-report.md`: parallel
  primitive design model for scan, reduction, compaction, radix sort,
  histogram, and segmented reduction.
- `moe-routing-all-to-all/moe-routing-report.json` and
  `moe-routing-all-to-all/reports/moe-routing-report.md`: MoE expert routing
  and all-to-all communication model with imbalance, drop-rate, payload, and
  bottleneck evidence.
- `hardware-capacity-planning/hardware-capacity-plan.json` and
  `hardware-capacity-planning/reports/hardware-capacity-plan.md`: modeled GPU
  capacity plan for workload memory, KV cache, bottlenecks, power/cost, and
  validation commands.
- `quantization-memory-formats/quantization-report.json` and
  `quantization-memory-formats/reports/quantization-report.md`: quantization
  and memory-format sweep with compression, accuracy drift, dequant tax,
  serving fit, and promotion commands.
- `numerical-reproducibility/numerical-reproducibility-report.json` and
  `numerical-reproducibility/reports/numerical-reproducibility-report.md`:
  deterministic seed, precision-mode tolerance, and reduction-order drift
  checks for GPU promotion.
- `cuda-graphs-latency/cuda-graphs-latency-report.json` and
  `cuda-graphs-latency/reports/cuda-graphs-latency-report.md`: launch-overhead
  stabilization model for CUDA Graph capture-ready and fallback serving paths.
- `multi-tenant-gpu-scheduling/multi-tenant-scheduling-report.json` and
  `multi-tenant-gpu-scheduling/reports/multi-tenant-scheduling-report.md`:
  scheduling model for MIG/MPS/Kubernetes-style placement, fairness, isolation,
  SLO fit, and queue fallback.
- `gpu-runs/gpu-run-report.json` and `gpu-runs/reports/gpu-run-report.md`:
  imported accelerator-host validation rows linked to the GPU promotion manifest.
- `gpu-runs/import-lint-report.json` and
  `gpu-runs/reports/import-lint-report.md`: schema and provenance linting for
  sample fixtures and collected GPU-run imports.
- `gpu-provenance/gpu-provenance-report.json` and
  `gpu-provenance/reports/gpu-provenance-report.md`: provenance accounting for
  sample fixtures, host-collected smoke imports, and real measured GPU runs.
- `gpu-measurement-queue/gpu-measurement-queue.json` and
  `gpu-measurement-queue/reports/gpu-measurement-queue.md`: per-step GPU-host
  measurement contracts, required metrics, executable threshold results, and
  measured/queued/accepted status.
- `gpu-measurement-queue/acceptance-logic-report.json` and
  `gpu-measurement-queue/reports/acceptance-logic-report.md`: regression report
  proving GPU measurement thresholds accept good rows and reject bad rows.
- `gpu-handoff/gpu-host-preflight.json` and
  `gpu-handoff/reports/gpu-host-preflight.md`: local accelerator-host capability
  snapshot and per-promotion-step runnable/blocked classification.
- `gpu-promotion/suite-run-report.json` and
  `gpu-promotion/reports/suite-run-report.md`: dry-run or execute-mode command
  plan generated from the GPU promotion manifest.
- `gpu-handoff/gpu-host-handoff.json`,
  `gpu-handoff/reports/gpu-host-handoff.md`, and
  `gpu-handoff/bin/run-gpu-host-handoff.sh`: portable GPU-host handoff bundle.
- `assessment/question-bank.json` and `assessment/reports/assessment-report.md`:
  concept questions, practical tasks, grading checks, lesson evidence, and
  tutorial-source links.
- `assessment/grading-report.json` and `assessment/reports/grading-report.md`:
  artifact-backed scores for assessment concept checks and practical tasks.
- `programming-projects/`: generated end-to-end programming projects with
  starter source, `measure.py` experiment harnesses, `tasks.json` milestones,
  per-project `measurements.json`, measurement contracts, and links back to labs,
  lessons, tutorial sources, and paper evidence.
- `programming-projects/project-run-report.json` and
  `programming-projects/project-run-report.md`: consolidated starter execution
  and measurement-contract validation report.
- `programming-projects/capstone-portfolio.json` and
  `programming-projects/capstone-portfolio.md`: portfolio dependency graph,
  ordered milestones, runtime caveats, and capstone build path.
- `programming-projects/notebook-index.json` and per-project `*.ipynb`: runnable
  notebook tutorials for each generated programming project.
- `program-outputs/`: generated batch triage, roadmap, and evidence-report
  outputs from the API example programs.
- `projects.html` and `project-*.html`: generated programming project dashboard
  and per-project site pages.
- `capstone.html`: generated portfolio page for the end-to-end GPU programming
  project layer.
- `compiler-runtime-inspection.html`: generated CUDA/Triton/HIP/custom-op
  compiler/runtime inspection dashboard.
- `tensor-core-gemm.html`: generated CUTLASS/CuTe tensor-core GEMM dashboard.
- `persistent-kernels.html`: generated persistent Triton/CUDA kernel dashboard.
- `parallel-primitives.html`: generated parallel primitive kernel dashboard.
- `gpu-runs.html`: generated accelerator-host run import dashboard.
- `gpu-import-lint.html`: generated GPU-run import lint dashboard.
- `gpu-provenance.html`: generated GPU evidence provenance dashboard.
- `gpu-measurement-queue.html`: generated GPU-host measurement contract
  dashboard.
- `gpu-acceptance-logic.html`: generated GPU measurement threshold regression
  dashboard.
- `serving-engine-comparison.html`: generated production inference engine
  comparison dashboard.
- `kv-cache-paged-attention.html`: generated KV-cache and PagedAttention
  allocator dashboard.
- `attention-serving-stack.html`: generated FlashAttention-to-vLLM serving
  stack dashboard.
- `flash-attention-backward.html`: generated FlashAttention backward training
  kernel dashboard.
- `sparse-attention-kernels.html`: generated sparse and ragged attention kernel
  dashboard.
- `fused-training-kernels.html`: generated fused LLM training kernel dashboard.
- `speculative-decoding-serving.html`: generated speculative decoding serving
  scheduler dashboard.
- `distributed-topology.html`: generated multi-GPU topology and parallelism
  planning dashboard.
- `distributed-collectives.html`: generated collective communication dashboard.
- `distributed-training-optimizer.html`: generated distributed training
  optimizer dashboard.
- `moe-routing-all-to-all.html`: generated MoE routing and all-to-all
  dashboard.
- `hardware-capacity.html`: generated GPU hardware capacity planning dashboard.
- `quantization-memory-formats.html`: generated quantization and memory-format
  dashboard.
- `numerical-reproducibility.html`: generated numerical reproducibility and
  precision drift dashboard.
- `cuda-graphs-latency.html`: generated CUDA Graphs latency stabilization
  dashboard.
- `multi-tenant-scheduling.html`: generated multi-tenant GPU scheduling
  dashboard.
- `gpu-host-preflight.html`: generated local accelerator-host readiness page.
- `gpu-promotion-suite.html`: generated GPU promotion command-plan dashboard.
- `gpu-handoff.html`: generated GPU-host handoff bundle dashboard.
- `assessment.html`: generated concept exam and practical task dashboard.
- `assessment-grading.html`: generated artifact-backed assessment score page.
- `lesson-001.html` through `lesson-118.html`: per-lesson tutorial pages.
- `bridge-*.html`: profile pages connecting lessons, labs, measurements, and papers.

To attempt transcript downloads:

```bash
python3 scripts/download_gpumode_transcripts.py
python3 scripts/build_curriculum.py
python3 scripts/build_workbench.py
python3 build_site.py
```

Raw VTT and clean transcript files are generated under `raw-material/youtube/`.
The committed artifacts are the indexes and generated site pages.
