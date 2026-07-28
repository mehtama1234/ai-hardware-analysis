# QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving

**Venue:** MLSYS 2025 · **Theme:** W4A8KV4 System Co-Design

## What It Does

INT4 weight quantization methods targeting edge/single-batch inference do not translate to throughput gains in cloud LLM serving because dequantizing INT4 weights or partial sums on CUDA cores introduces 20-90% runtime overhead that erases memory bandwidth savings at large batch sizes.

Cloud LLM serving is bottlenecked by low-throughput CUDA core operations during dequantization, not solely by memory bandwidth. W8A8 kernels using Tensor Cores are efficient at large batch, but 8-bit KV cache is still memory-heavy. W4A8KV4 could combine the best of both, but requires careful algorithm and system co-design to avoid dequantization overhead on CUDA cores.

QoQ (quattuor-octo-quattuor, 4-8-4) algorithm with three components: (1) Progressive group quantization: first applies INT8 per-channel quantization to weights, then applies INT4 per-group quantization with a protective range of [-119, 119] that guarantees INT4 values, when scaled back to INT8, remain within safe INT8 range for Tensor Core matmul without overflow. (2) SmoothAttention: applies a per-channel scale lambda to Key tensors to suppress outliers, then absorbs this scale into the preceding linear layer weights; exploits RoPE commutativity to apply the scale before positional encoding, enabling 4-bit KV quantization without accuracy loss. (3) Compute-aware weight reordering: stores INT4 weights in the order they are accessed during GEMM computation (not the order of the weight matrix), enabling 128-bit/thread memory transactions rather than scattered accesses. Fast dequantization: performs subtraction before multiplication (reverses typical order) to keep values in INT8 range, uses 4-way register-level parallelism via vadd4 instruction to dequantize 4 weights per instruction. KV4 attention: replaces FP32 CUDA core accumulation in attention decoding with FP16 Tensor Core ops; bit manipulation tricks reduce dequantization from 5 to 2 ops per element.

## The Key Experiment

- **llama3 8b throughput a100:** 1.2x Llama-3-8B max serving throughput on A100 vs TensorRT-LLM
- **llama3 8b throughput l40s:** 1.4x Llama-3-8B max serving throughput on L40S vs TensorRT-LLM
- **qwen15 72b throughput a100:** 2.4x Qwen1.5-72B throughput on A100 vs TensorRT-LLM
- **qwen15 72b throughput l40s:** 3.5x Qwen1.5-72B throughput on L40S vs TensorRT-LLM
- **l40s vs a100:** QServe on L40S achieves higher throughput than TensorRT-LLM FP16 on A100

**Compared against:** TensorRT-LLM W8A8; TensorRT-LLM W4A16; AWQ INT4; SmoothQuant W8A8

**Hardware:** NVIDIA A100; NVIDIA L40S · **Workloads:** llm-inference; cloud-serving; large-batch-inference

## Why This Approach

Progressive group quantization with protective range enabling W4A8 Tensor Core GEMM without overflow; SmoothAttention absorbing per-channel Key scales into weights via RoPE commutativity; compute-aware weight reordering enabling 128-bit/thread memory access patterns.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: QoQ W4A8KV4 quantization algorithm with protective range [-119,119] for safe INT8 Tensor Core use.

## What It Leaves Open

- Protective range [-119,119] for INT8 reduces effective quantization range slightly vs naive INT8
- SmoothAttention requires per-layer calibration to determine per-channel Key scales
- Compute-aware weight reordering is non-trivial to implement and hardware-specific
- KV4 accuracy on tasks with high attention score variance not fully characterized
- Only demonstrated on dense transformer models; MoE and hybrid models not evaluated

**Tags:** quantization, W4A8KV4, QoQ, SmoothAttention, progressive-quantization, GEMM, vadd4, LLM-serving
