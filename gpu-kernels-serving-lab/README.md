# GPU Kernels And LLM Serving Lab

This is the hands-on implementation track for `MEATY-GOAL.md`.

The lab connects high-level model serving to the hardware work underneath it:
Hugging Face baselines, JAX Scaling Book cost models, CUDA kernels, Triton kernels,
ROCm/HIP portability, quantization, vLLM/TGI serving, KV-cache management, and a
mini serving-engine capstone.

## Current slice

Implemented:

- `00-orientation/run.py` records the local software/GPU inventory.
- `00-orientation/build_page.py` renders the first tutorial page.
- `01-hf-baseline/run.py` runs a real Hugging Face generation baseline when possible,
  with a deterministic local PyTorch fallback.
- `02-roofline/run.py` runs vector add, reduction, matmul, and KV-cache scan
  microbenchmarks.
- `03-cuda-vector-reduce/run.py` compiles and runs beginner CUDA kernels when
  `nvcc` is available, otherwise records a skip artifact.
- `04-cuda-tiled-matmul/run.py` compiles and runs naive and shared-memory CUDA
  matmul kernels when `nvcc` is available, otherwise records a skip artifact.
- `05-cuda-tiny-attention/run.py` measures materialized attention, PyTorch SDPA,
  and causal KV-cache decode scaling.
- `06-triton-matmul/run.py` runs a blocked Triton matmul when a CUDA device is
  visible, otherwise records a skip artifact.
- `07-triton-fused-attention/run.py` runs a single-query fused attention Triton
  kernel when CUDA is visible, otherwise records a skip artifact.
- `08-quantized-inference/run.py` measures simple fp16/int8/int4/MXFP4-like
  weight compression drift.
- `09-vllm-serving/run.py` records vLLM serving readiness and required runtime state.
- `10-kv-cache-memory-manager/run.py` simulates block-based KV-cache allocation
  and prefix reuse.
- `11-rocm-hip-port/run.py` compiles and runs a minimal HIP kernel when ROCm is
  available, otherwise records a skip artifact.
- `12-jax-scaling-practicum/run.py` runs JAX jit timing and KV-cache sizing.
- `13-capstone-mini-serving-engine/server.py` exposes a minimal local completion
  endpoint.
- `13-capstone-mini-serving-engine/load_test.py` measures that endpoint and
  writes serving evidence.
- `13-capstone-mini-serving-engine/run.py` aggregates all current artifacts into
  one serving diagnosis.
- `14-final-synthesis/run.py` reads the generated artifacts and writes the final
  compute/memory/communication and serving synthesis.
- `15-gpumode-coalescing/run.py` turns GPUMODE transcript intelligence into a
  memory coalescing/access-pattern microscope with CPU evidence and CUDA source.
- `16-gpumode-warp-reductions/run.py` turns GPUMODE warp-execution lessons into
  reduction and scan measurements with shared-memory and warp-shuffle CUDA source.
- `17-gpumode-triton-autotune/run.py` turns GPUMODE Triton/autotuning lessons into
  a tile-config model, CPU matmul baseline, and CUDA-gated Triton sweep.
- `18-gpumode-online-softmax/run.py` turns GPUMODE attention lessons into a
  materialized-vs-online softmax lab with correctness and memory estimates.
- `19-gpumode-torch-compile/run.py` turns GPUMODE compiler lessons into eager vs
  compiled PyTorch measurements with graph-break analysis.
- `20-gpumode-vllm-scheduler/run.py` turns GPUMODE serving lessons into a
  continuous-batching and paged-prefix-cache scheduler lab.
- `21-gpumode-quantized-kernels/run.py` turns GPUMODE quantization lessons into
  fp16/int8/int4/MXFP4-like matmul measurements with error and memory accounting.
- `22-gpumode-nsight-roofline/run.py` turns GPUMODE profiling lessons into a
  counter-to-roofline bottleneck classifier with Nsight readiness detection.
- `23-gpumode-shared-memory-gemm/run.py` turns GPUMODE CUDA/CUTLASS tiling
  lessons into naive-vs-tiled GEMM measurements with traffic and correctness evidence.
- `24-gpumode-tensor-core-cutlass/run.py` turns GPUMODE Tensor Core/CUTLASS
  lessons into low-precision drift, MMA tile-eligibility, and readiness evidence.
- `25-gpumode-rocm-hip-portability/run.py` turns GPUMODE CUDA kernels into a
  HIP portability report with translated sources, semantic checks, and ROCm readiness.
- `26-gpumode-distributed-communication/run.py` turns GPUMODE NCCL/NVSHMEM and
  distributed GEMM lessons into all-reduce modeling, semantic checks, and runtime readiness.
- `build_site.py` assembles `site/`.

Planned next:

- `09-vllm-serving`: replace readiness-only mode with a real vLLM server and load
  generator once a supported GPU environment is available.
- `13-capstone-mini-serving-engine`: replace the deterministic local endpoint
  with an optimized vLLM-backed path once a supported GPU environment is available.

## Run

```bash
cd gpu-kernels-serving-lab
python3 run_all.py
```

Or run the individual steps:

```bash
python3 00-orientation/run.py
python3 01-hf-baseline/run.py
python3 02-roofline/run.py
python3 03-cuda-vector-reduce/run.py
python3 04-cuda-tiled-matmul/run.py
python3 05-cuda-tiny-attention/run.py
python3 06-triton-matmul/run.py
python3 07-triton-fused-attention/run.py
python3 08-quantized-inference/run.py
python3 09-vllm-serving/run.py
python3 10-kv-cache-memory-manager/run.py
python3 11-rocm-hip-port/run.py
python3 12-jax-scaling-practicum/run.py
python3 15-gpumode-coalescing/run.py
python3 16-gpumode-warp-reductions/run.py
python3 17-gpumode-triton-autotune/run.py
python3 18-gpumode-online-softmax/run.py
python3 19-gpumode-torch-compile/run.py
python3 20-gpumode-vllm-scheduler/run.py
python3 21-gpumode-quantized-kernels/run.py
python3 22-gpumode-nsight-roofline/run.py
python3 23-gpumode-shared-memory-gemm/run.py
python3 24-gpumode-tensor-core-cutlass/run.py
python3 25-gpumode-rocm-hip-portability/run.py
python3 26-gpumode-distributed-communication/run.py
python3 13-capstone-mini-serving-engine/load_test.py
python3 13-capstone-mini-serving-engine/run.py
python3 14-final-synthesis/run.py
(cd 00-orientation && python3 build_page.py)
(cd 01-hf-baseline && python3 build_page.py)
(cd 02-roofline && python3 build_page.py)
(cd 03-cuda-vector-reduce && python3 build_page.py)
(cd 04-cuda-tiled-matmul && python3 build_page.py)
(cd 05-cuda-tiny-attention && python3 build_page.py)
(cd 06-triton-matmul && python3 build_page.py)
(cd 07-triton-fused-attention && python3 build_page.py)
(cd 08-quantized-inference && python3 build_page.py)
(cd 09-vllm-serving && python3 build_page.py)
(cd 10-kv-cache-memory-manager && python3 build_page.py)
(cd 11-rocm-hip-port && python3 build_page.py)
(cd 12-jax-scaling-practicum && python3 build_page.py)
(cd 13-capstone-mini-serving-engine && python3 build_page.py)
(cd 14-final-synthesis && python3 build_page.py)
(cd 15-gpumode-coalescing && python3 build_page.py)
(cd 16-gpumode-warp-reductions && python3 build_page.py)
(cd 17-gpumode-triton-autotune && python3 build_page.py)
(cd 18-gpumode-online-softmax && python3 build_page.py)
(cd 19-gpumode-torch-compile && python3 build_page.py)
(cd 20-gpumode-vllm-scheduler && python3 build_page.py)
(cd 21-gpumode-quantized-kernels && python3 build_page.py)
(cd 22-gpumode-nsight-roofline && python3 build_page.py)
(cd 23-gpumode-shared-memory-gemm && python3 build_page.py)
(cd 24-gpumode-tensor-core-cutlass && python3 build_page.py)
(cd 25-gpumode-rocm-hip-portability && python3 build_page.py)
(cd 26-gpumode-distributed-communication && python3 build_page.py)
python3 build_site.py
```

Open `site/index.html` in a browser.

## Evidence rule

Every session should write `out_*.json` first. Tutorial pages must read those JSON
files and explain the measured result. If a GPU or package is missing, the session
should write a skip/status artifact instead of silently failing.
