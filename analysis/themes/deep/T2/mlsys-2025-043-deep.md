# HyC-LoRA: Memory Efficient LoRA Fine-tuning with Hybrid Activation Compression

**Venue:** MLSYS · **Theme:** Memory-Efficient Fine-Tuning

## What It Does

LoRA fine-tuning dramatically reduces trainable weight count but the buffered activations needed for backpropagation still dominate memory—69.7% of total in Llama-2-7B—and non-linear operator activations (RMSNorm, RoPE) are the hardest to compress due to outliers.

Existing activation compression methods (quantization, sparsity, recomputation) focus on linear layers; non-linear activations resist uniform quantization due to channel-wise outliers. Achieving near-2-bit average quantization across all operators requires operator-specific hybrid strategies.

HyC-LoRA introduces two compression tiers. Intra-operator: for RMSNorm activations, calibrate which channels contain extreme outliers, store those at full precision (FP16), quantize the rest to INT2; for attention Q/K, quantize before RoPE application (pre-RoPE quantization) where values are smoother. Inter-operator: LoRA Reorder Computing reorders the quantization and LoRA adapter application so that XA (activation times LoRA A matrix) is retained while the main branch quantizes YW separately, allowing YAB to be recomputed during backward pass rather than stored; Triton-based kernel fusion merges quantization and dequantization with adjacent ops to reduce kernel launch overhead.

## The Key Experiment

End-to-end memory reduction (x); Activation memory reduction (x); Accuracy on downstream tasks; Training throughput

**Compared against:** QLoRA; SparseBP; BackRazor; LoRA-FA; QST

**Hardware:** GPU (NVIDIA; Triton-compatible); targets on-device fine-tuning scenarios · **Workloads:** LoRA fine-tuning of LLMs (Llama-2-7B, Llama-3-8B); Downstream NLP tasks (commonsense reasoning, instruction following)

## Why This Approach

Hybrid two-tier compression combining structured per-channel outlier extraction for non-linear activations (intra-operator) with LoRA-aware reordering of quantization to enable recomputation instead of storage (inter-operator), plus kernel fusion—achieving near-2-bit across all operators.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Identification that non-linear buffered activations are 69.7% of LoRA training memory in Llama-2-7B.

## What It Leaves Open

- Triton kernels add engineering complexity and may not generalize to all GPU architectures without retuning
- Pre-RoPE quantization assumes RoPE is applied after Q/K projection; architectures that differ may need separate handling
- Recomputation in inter-operator tier adds compute overhead which may reduce training speed

**Tags:** lora, fine-tuning, activation-compression, quantization, memory-efficiency, kernel-fusion, llm, triton
