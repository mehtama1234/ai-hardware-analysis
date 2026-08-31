# Meaty Goal: GPUMODE To Runnable GPU Systems Labs

Build an end-to-end GPUMODE-powered GPU systems curriculum that ingests YouTube
transcripts, extracts a structured topic and prerequisite map, connects lessons
to the existing AI-hardware corpus, and produces runnable CUDA/Triton/PyTorch/vLLM
labs with measurement-backed generated pages and a final GPU systems workbench.

## Source Spine

- GPUMODE YouTube channel: `https://www.youtube.com/@GPUMODE/videos`
- GPUMODE code/resource ecosystem: `https://github.com/gpu-mode`
- Existing runnable lab: `gpu-kernels-serving-lab/`
- Existing AI-hardware corpus: top-level `synthesis.html`, venue big-picture pages,
  and `analysis/per-paper/*.json`
- JAX Scaling Book: `https://jax-ml.github.io/scaling-book/`
- Hugging Face inference and serving tutorials
- vLLM, Triton, CUDA, ROCm/HIP, CUTLASS, Nsight, PyTorch compiler documentation

## Target End State

1. Transcript corpus
   - capture all GPUMODE video metadata
   - download captions where available
   - clean transcripts and cue files
   - record missing/unusable transcripts explicitly

2. Lesson intelligence
   - extract concepts, kernels, tools, prerequisite signals, paper/repo mentions,
     and candidate exercises from each lesson
   - produce `analysis/lesson-intelligence.json`
   - keep the extraction deterministic and rerunnable before adding LLM-assisted
     deep summaries

3. Curriculum graph
   - build a topic graph across CUDA, Triton, PyTorch compiler, profiling,
     attention, quantization, serving, distributed training, and hardware
   - infer a practical prerequisite order
   - link lessons to existing runnable labs and proposed next labs

4. Runnable lab expansion
   - add deeper labs to `gpu-kernels-serving-lab` or a sibling lab package
   - each lab must include runnable code, correctness checks, measurement JSON,
     generated tutorial pages, and clean skip artifacts when local GPU tooling is
     unavailable

5. Workbench capstone
   - given a model/operator/bottleneck, recommend:
     - likely bottleneck class
     - relevant GPUMODE lessons
     - relevant repo papers/pages
     - runnable lab to execute next
     - latest measured local result

## Deep Lab Spine

1. CUDA memory coalescing microscope
2. Warp reductions and prefix scans
3. Triton matmul autotuning workbench
4. FlashAttention-style online softmax
5. `torch.compile` graph-break and fusion lab
6. vLLM scheduler and KV-cache load lab
7. Low-bit quantized matmul and numerical drift lab
8. Nsight/profiler counter to roofline triage lab
9. Shared-memory tiled GEMM with arithmetic-intensity accounting
10. Tensor Core matmul via WMMA or CUTLASS
11. ROCm/HIP portability path for selected kernels
12. Distributed communication and collectives follow-up

## Acceptance Criteria

- The GPUMODE channel index is generated from current YouTube metadata.
- Available transcripts are downloaded, cleaned, indexed, and counted.
- Missing transcripts are visible in the generated artifacts and site.
- Every lesson has deterministic topic labels and at least one structured
  intelligence record.
- The site is generated from JSON artifacts, not hand-entered result tables.
- The site exposes topic counts, lesson search targets, proposed labs, and the
  connection to `gpu-kernels-serving-lab`.
- Multiple deeper runnable labs are implemented after the curriculum map is in
  place.
- Every lesson gets a generated local page linking video, transcript status,
  topic/concept extraction, candidate labs, and workbench bridge matches.
- Workbench paper recommendations include lesson links so papers, talks, and
  local measurements can be traversed in both directions.
- CUDA, Triton, ROCm/HIP, JAX Scaling Book, and Hugging Face tutorial sources
  are structured, generated, and surfaced in the bottleneck workbench rather
  than remaining only source notes.
- Each bottleneck profile has a generated end-to-end exercise path linking an
  external tutorial source, GPUMODE lesson, runnable lab command, measurement
  artifact, corpus paper cross-check, and success criteria.
- The prerequisite/topic graph is queryable from the command line so a topic,
  concept, prerequisite, lesson, or lab phrase returns connected lessons, labs,
  concepts, and workbench profiles.
- Lesson-to-corpus paper bridges are generated as a bidirectional artifact and
  queryable by paper, lesson, topic, technique, hardware, or workload phrase.
- Latest local measurements are normalized into a generated index that records
  status, correctness, runtime readiness, skip reasons, summary, and page path
  for every lab artifact.
- A generated end-to-end audit maps the goal requirements to concrete evidence
  artifacts and names remaining runtime caveats.
- GPU absence is handled with skip artifacts rather than hidden assumptions.
- The final workbench uses measured local results plus GPUMODE/corpus links.
- `scripts/verify_workbench.py` passes and verifies corpus counts, generated
  lesson/bridge pages, lab correctness artifacts, imported Nsight/NCCL/NVSHMEM
  evidence, paper lesson links, and workbench profile coverage.

## Current Slice

The current slice now goes past indexing and basic labs: it builds the transcript
corpus, deterministic topic map, lesson-intelligence artifact, proposed lab
backlog, generated curriculum site, per-lesson tutorial pages, bottleneck
workbench, paper-to-lesson links, profile bridge pages, and the first full
GPUMODE-derived runnable lab wave plus first-class external tutorial links:

- `gpu-kernels-serving-lab/15-gpumode-coalescing`
- `gpu-kernels-serving-lab/16-gpumode-warp-reductions`
- `gpu-kernels-serving-lab/17-gpumode-triton-autotune`
- `gpu-kernels-serving-lab/18-gpumode-online-softmax`
- `gpu-kernels-serving-lab/19-gpumode-torch-compile`
- `gpu-kernels-serving-lab/20-gpumode-vllm-scheduler`
- `gpu-kernels-serving-lab/21-gpumode-quantized-kernels`
- `gpu-kernels-serving-lab/22-gpumode-nsight-roofline`
- `gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm`
- `gpu-kernels-serving-lab/24-gpumode-tensor-core-cutlass`
- `gpu-kernels-serving-lab/25-gpumode-rocm-hip-portability`
- `gpu-kernels-serving-lab/26-gpumode-distributed-communication`
- `analysis/curriculum-graph.json`
- `analysis/gpu-systems-workbench.json`
- `analysis/tutorial-sources.json`
- `analysis/tutorial-exercise-paths.json`
- `analysis/lesson-corpus-bridges.json`
- `analysis/latest-measurements-index.json`
- `analysis/end-to-end-audit.json`
- `analysis/end-to-end-audit.md`
- `scripts/build_end_to_end_audit.py`
- `scripts/query_corpus_bridge.py`
- `scripts/query_measurements.py`
- `scripts/query_curriculum_graph.py`
- `scripts/verify_workbench.py`
- `site/lesson-001.html` through `site/lesson-118.html`
- `site/bridge-*.html`
- `site/workbench.html`

The generated workbench now recommends NVIDIA CUDA programming/performance
references, Triton tutorials, AMD ROCm/HIP programming references, JAX Scaling
Book chapters for roofline, inference, training, profiling, JAX programming,
and GPU hardware reasoning, and Hugging Face sources for LLM deployment,
Transformers inference, quantization, and Text Generation Inference.

The current slice also includes imported Nsight-shaped reports for session 22
and NCCL/NVSHMEM benchmark ingestion for session 26. The next slice should run
the CUDA/HIP/Nsight/NCCL paths on suitable multi-GPU hardware and compare those
real measurements against the imported samples and CPU proxy artifacts.
