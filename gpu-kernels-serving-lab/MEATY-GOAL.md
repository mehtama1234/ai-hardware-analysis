# Meaty End-To-End Goal: GPU Kernels And LLM Serving Lab

## Objective

Build a hands-on tutorial track that connects high-level LLM APIs to the GPU machinery
underneath them. The finished lab should take a reader from a Hugging Face baseline,
through cost modeling and custom kernels, into production-style serving with vLLM/TGI,
then back down to CUDA, Triton, HIP/ROCm, and JAX profiling so they can explain where
latency, memory, bandwidth, and communication cost actually go.

The output should match the style of `kimi-k3-lab`: one session per concept, real code
that produces JSON measurements, a rendered tutorial page per session, and a top-level
site that turns the measurements into a readable path.

## Core Question

When an LLM is slow or expensive to serve, is the limiting factor compute, memory
bandwidth, KV-cache management, kernel launch/data movement overhead, quantization,
batch scheduling, or interconnect communication?

The lab is complete only when a reader can run the experiments and answer that question
with measured evidence rather than generic GPU advice.

## Source Spine

- JAX Scaling Book: https://jax-ml.github.io/scaling-book/
  - roofline analysis
  - transformer FLOPs, parameter counts, and KV-cache sizing
  - training and inference parallelism
  - JAX/XLA profiling and debugging
  - GPU-vs-TPU cost model
- Hugging Face LLM Course, optimized inference deployment:
  https://huggingface.co/learn/llm-course/en/chapter2/8
  - Transformers baseline
  - TGI, vLLM, and llama.cpp deployment choices
  - FlashAttention and PagedAttention framing
- Hugging Face Transformers quantization:
  https://huggingface.co/docs/transformers/en/main_classes/quantization
- Hugging Face bitsandbytes:
  https://huggingface.co/docs/transformers/en/quantization/bitsandbytes
- vLLM docs: https://docs.vllm.ai/
  - PagedAttention
  - continuous batching
  - chunked prefill
  - prefix caching
  - CUDA/HIP graphs
  - quantization
- Triton tutorials: https://triton-lang.org/main/getting-started/tutorials/
  - blocked matmul
  - fused softmax
  - fused attention
  - persistent matmul
- NVIDIA CUDA Programming Guide:
  https://docs.nvidia.com/cuda/cuda-programming-guide/
- AMD ROCm/HIP docs:
  https://rocm.docs.amd.com/projects/HIP/en/latest/

## Deliverable Shape

```
gpu-kernels-serving-lab/
  MEATY-GOAL.md
  README.md
  build_site.py
  common/
    bench.py
    gpu_info.py
    report.py
  00-orientation/
  01-hf-baseline/
  02-roofline/
  03-cuda-vector-reduce/
  04-cuda-tiled-matmul/
  05-cuda-tiny-attention/
  06-triton-matmul/
  07-triton-fused-attention/
  08-quantized-inference/
  09-vllm-serving/
  10-kv-cache-memory-manager/
  11-rocm-hip-port/
  12-jax-scaling-practicum/
  13-capstone-mini-serving-engine/
  14-final-synthesis/
  15-gpumode-coalescing/
  16-gpumode-warp-reductions/
  17-gpumode-triton-autotune/
  18-gpumode-online-softmax/
  19-gpumode-torch-compile/
  20-gpumode-vllm-scheduler/
  21-gpumode-quantized-kernels/
  22-gpumode-nsight-roofline/
  23-gpumode-shared-memory-gemm/
  24-gpumode-tensor-core-cutlass/
  25-gpumode-rocm-hip-portability/
  26-gpumode-distributed-communication/
  site/
```

Each numbered session should contain:

- one or more runnable scripts/notebooks
- a small, repeatable benchmark
- `out_*.json` measurement files
- `build_page.py`
- `out/index.html`
- a short "what this proves / what it does not prove" boundary

Prefer scripts first, notebooks second. Notebooks are useful for reader exploration, but
scripts make the site reproducible and CI-friendly.

## Sessions

### 00 - Orientation: From Model API To GPU Work

Goal: show the whole stack before diving into pieces.

Experiment: run one tiny text-generation request through Transformers, collect tokens/sec,
peak memory, model size, prompt length, output length, and GPU name.

Page should explain the path:

`prompt -> tokenizer -> model weights -> attention/KV cache -> kernels -> scheduler -> response`

Exit artifact:

- `out_orientation.json`
- diagram of the serving stack

### 01 - Hugging Face Baseline

Goal: establish the high-level reference behavior.

Experiments:

- load a small instruct model with Transformers
- run single-prompt decode
- run batched decode
- sweep prompt length and generated tokens
- record time-to-first-token, tokens/sec, peak GPU memory, and KV-cache estimate

Question answered: what does the normal Python/model API hide?

### 02 - Roofline For AI Operations

Goal: make the JAX Scaling Book's cost model concrete on the local GPU.

Experiments:

- vector add: bandwidth-bound
- reduction: synchronization and memory traffic
- GEMM: compute-bound when large enough
- attention score and KV-cache scan: memory pressure with growing context

Outputs:

- effective GB/s
- effective TFLOP/s
- arithmetic intensity
- roofline chart

Question answered: which operations are limited by math, memory, or communication?

### 03 - CUDA Vector Add, Reduction, And Memory Coalescing

Goal: teach CUDA from the smallest AI-relevant kernels.

Experiments:

- naive vector add
- coalesced vector add
- block reduction
- compare against PyTorch
- use CUDA events for timing

Concepts:

- thread/block hierarchy
- global memory
- occupancy
- coalesced access
- synchronization

Question answered: why does memory layout matter before the math changes?

### 04 - CUDA Tiled Matmul

Goal: build the foundation for Tensor Core and attention kernels.

Experiments:

- naive CUDA matmul
- shared-memory tiled matmul
- optional WMMA/Tensor Core variant when hardware supports it
- compare against `torch.matmul`/cuBLAS

Outputs:

- runtime
- effective TFLOP/s
- gap to cuBLAS
- shared-memory tile visualization

Question answered: how does keeping data close to compute change throughput?

### 05 - CUDA Tiny Attention

Goal: expose why naive attention is expensive.

Experiments:

- materialized attention: QK^T, mask, softmax, PV
- causal decode with growing KV cache
- memory footprint as sequence length grows

Outputs:

- full attention matrix memory
- per-token decode latency by context length
- correctness comparison against PyTorch SDPA

Question answered: why is attention often a memory system problem?

### 06 - Triton Matmul

Goal: show why Triton is the practical bridge between PyTorch and CUDA.

Experiments:

- blocked Triton matmul
- autotuned block sizes
- compare PyTorch eager, `torch.compile`, Triton, and cuBLAS

Concepts:

- program IDs
- blocks
- masks
- SRAM reuse
- autotuning

Question answered: when is custom kernel work worthwhile without writing CUDA C++?

### 07 - Triton Fused Attention

Goal: reproduce the FlashAttention-shaped insight at tutorial scale.

Experiments:

- naive attention that writes the full attention matrix
- fused/tiled attention that keeps partial state local
- sequence-length sweep

Outputs:

- HBM bytes avoided
- runtime by sequence length
- correctness error against PyTorch

Question answered: why does fusion beat materialization?

### 08 - Quantized Inference With Hugging Face

Goal: connect model compression to hardware behavior.

Experiments:

- fp16/bf16 baseline
- 8-bit load with bitsandbytes
- 4-bit NF4/FP4 load with bitsandbytes
- optional GPTQ/AWQ model if small enough
- compare memory, latency, and output drift

Reuse/extend the existing Kimi K3 serving quantization idea, but use real HF model loading.

Question answered: when does quantization save memory, and when does it actually speed up?

### 09 - vLLM And TGI Serving Baseline

Goal: compare serving runtimes under controlled load.

Experiments:

- serve the same small model with vLLM
- serve it with Hugging Face TGI if Docker/GPU environment allows it
- run a local load generator
- sweep concurrency, prompt length, generated tokens

Outputs:

- throughput
- time-to-first-token
- inter-token latency
- P50/P95/P99 latency
- GPU memory

Question answered: what does a serving engine add beyond `model.generate()`?

### 10 - KV Cache As A Memory Manager

Goal: make PagedAttention and prefix caching visible.

Experiments:

- requests with no shared prefix
- requests with shared prefix
- long prompts with low concurrency
- short prompts with high concurrency
- vary vLLM memory/block-related knobs where exposed and stable

Outputs:

- prefix-cache hit effect
- throughput improvement
- latency distribution
- memory pressure boundary

Question answered: why is LLM serving an operating-system-style memory problem?

### 11 - ROCm/HIP Port

Goal: make the CUDA kernels cross-vendor.

Experiments:

- port vector add
- port reduction
- port tiled matmul
- use HIP events and rocprof where available
- compare source differences against CUDA

Outputs:

- CUDA/HIP API translation table
- AMD run results if ROCm hardware is available
- compile/run status if no AMD GPU is available

Question answered: what is portable, and what is vendor-specific?

### 12 - JAX Scaling Practicum

Goal: turn the JAX Scaling Book from reading material into executable exercises.

Experiments:

- JAX matmul and attention cost estimates
- `jit` vs eager
- sharded matrix multiplication where multiple devices are available
- profiler trace capture
- communication-cost estimate for all-reduce/all-gather

Outputs:

- profiler screenshots or trace summaries
- predicted vs measured runtime
- model-size/KV-cache calculators

Question answered: how do scaling laws and sharding plans meet profiler reality?

### 13 - Capstone: Mini LLM Serving Engine

Goal: connect every layer into one working system.

Build:

- a tiny OpenAI-compatible local endpoint, or a minimal batch decode server
- Hugging Face model loading
- explicit KV-cache accounting
- optional custom Triton attention path for a toy model
- quantized model option
- vLLM comparison mode
- load generator
- report generator

Final report must show:

- model and hardware inventory
- prompt/output workload
- memory footprint
- TTFT and tokens/sec
- P50/P95/P99 latency
- roofline classification
- what bottleneck dominated
- what optimization moved the bottleneck

Question answered: if this were a real serving system, what would we optimize next?

## Measurement Schema

Every benchmark JSON should include:

```json
{
  "session": "02-roofline",
  "timestamp": "ISO-8601",
  "host": "...",
  "device": {
    "backend": "cuda | rocm | cpu | tpu | unknown",
    "name": "...",
    "driver": "...",
    "runtime": "..."
  },
  "software": {
    "python": "...",
    "torch": "...",
    "triton": "...",
    "transformers": "...",
    "vllm": "...",
    "jax": "..."
  },
  "workload": {
    "model": "...",
    "batch_size": 1,
    "prompt_tokens": 1024,
    "generated_tokens": 128,
    "dtype": "fp16"
  },
  "metrics": {
    "latency_ms": 0.0,
    "tokens_per_sec": 0.0,
    "ttft_ms": 0.0,
    "peak_memory_mb": 0.0,
    "effective_gbps": 0.0,
    "effective_tflops": 0.0
  },
  "boundary": "what this run proves and what it does not prove"
}
```

## Build Order

1. Scaffold `gpu-kernels-serving-lab/README.md`, `common/`, and `build_site.py`.
2. Build Sessions 00-02 first: HF baseline, roofline, and stack orientation.
3. Add CUDA Sessions 03-05.
4. Add Triton Sessions 06-07.
5. Add quantization and serving Sessions 08-10.
6. Add HIP and JAX Sessions 11-12.
7. Build the capstone server and report in Session 13.
8. Add a synthesis page tying the lab back to the existing conference corpus.

## Acceptance Criteria

- Every session has runnable code and generated measurements.
- Every page is generated from measurements, not hand-entered results.
- Every benchmark records hardware/software versions.
- GPU absence is handled cleanly with a documented skip result.
- CUDA, Triton, vLLM, Hugging Face, JAX, and HIP each have at least one concrete artifact.
- The capstone compares at least two serving paths, one high-level and one optimized.
- The final synthesis explains bottlenecks in the language of the JAX Scaling Book:
  compute, memory, and communication.
- The final synthesis explains serving in the language of vLLM/HF:
  KV cache, batching, prefix reuse, quantization, and deployment runtime.

## Non-Goals

- Do not attempt to beat vendor libraries in absolute performance.
- Do not require a giant model or multi-GPU cluster for the core path.
- Do not hide failed GPU availability; record skip artifacts.
- Do not make this a generic CUDA course. Every kernel must connect to an AI serving
  bottleneck.
- Do not make this a generic Hugging Face usage guide. Every high-level API must be
  traced down to memory, kernels, scheduling, or quantization.

## First Concrete Slice

The first slice should be small but end-to-end:

1. `00-orientation`: detect GPU/software stack and render the system map.
2. `01-hf-baseline`: run a small HF model or record a clean skip if model/GPU is missing.
3. `02-roofline`: run vector add, reduction, and matmul microbenchmarks.
4. `build_site.py`: publish those three pages into `site/`.
5. `README.md`: explain how to run the slice and what evidence it produces.

That gives the project a runnable spine before adding custom CUDA/Triton/vLLM depth.
