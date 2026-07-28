# Rethinking Key-Value Cache Compression Techniques for Large Language Model Serving

**Venue:** MLSYS 2025 · **Theme:** KV Cache Compression

## What It Does

KV cache compression algorithms are evaluated on naive transformer library (TRL) benchmarks with fixed response lengths, hiding three critical problems that prevent production deployment: suboptimal throughput under real serving frameworks (FlashAttention + PagedAttention), increased end-to-end latency due to compression-induced response length growth, and per-sample accuracy fragility on specific task types.

Researchers report memory reduction and TRL-based throughput speedup, but production systems use FlashAttention and PagedAttention which already optimize memory access; compression may not compose well with these. Response length is treated as fixed in throughput benchmarks, but lossy compression causes models to generate longer outputs (verbose compensation), eroding throughput gains. Per-sample analysis reveals that even minor average accuracy drops mask large per-instance failures on summarization and QA tasks.

Empirical study evaluating four representative KV cache compression methods (KIVI for quantization, GEAR for quantization with error correction, StreamingLLM for structured sparsity, H2O for dynamic attention-score-based sparsity) under three missing evaluation dimensions: (1) Throughput analysis - benchmarks on LMDeploy (with PagedAttention+FlashAttention) and TRL across batch sizes, prompt lengths, and tensor parallelism degrees for LLaMA-7B and LLaMA-70B; (2) Length distribution analysis - measures response length shift D = (Lun - Lcs)/Lun across 1000 ShareGPT samples; (3) Negative sample analysis - defines negative samples as benign inputs where compression causes >10% accuracy drop on LongBench tasks; categorizes by task type (summarization, QA, code, few-shot, synthetic). Additionally provides three tools: throughput predictor (attention-layer profiling + Vidur runtime), length predictor (BERT-based classifier predicting response length given compression algorithm), and negative sample benchmark dataset.

## The Key Experiment

- **throughput under serving frameworks:** Compression speedup vanishes or turns negative at batch size >4 and KV length >=1024 when PagedAttention+FlashAttention are enabled
- **length increase:** More than 20% of samples show >=1.5x response length increase from lossy compression
- **negative samples kivi:** 400-600 negative samples out of ~2000 evaluated at 10% threshold
- **negative samples h2o:** 600-800 negative samples at 10% threshold
- **throughput predictor accuracy:** >85% across all four compression methods
- **length predictor accuracy:** >85% across all four compression methods
- **tensor parallelism effect:** Compression speedup decreases or goes negative under tensor parallelism (TP=2,4) due to reduced memory bandwidth contention per GPU

**Compared against:** KIVI (INT4 per-channel quantization); GEAR (quantization + low-rank error correction); StreamingLLM (initial + recent token sparsity); H2O (heavy hitter oracle sparsity); FP16 baseline on TRL, LMDeploy

**Hardware:** NVIDIA A6000; NVIDIA H800 · **Workloads:** llm-inference; long-context-inference; production-serving

## Why This Approach

Identification of three overlooked production deployment dimensions (throughput under serving frameworks, response length distribution, per-sample accuracy fragility) for KV compression evaluation; suite of tools (throughput predictor, length predictor, negative sample benchmark) for practical deployment.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: Comprehensive survey of 40+ KV cache compression algorithms (Table 1) with evaluation setting analysis.

## What It Leaves Open

- Only evaluates LLaMA and Mistral families; findings may not generalize to all model architectures
- Throughput analysis restricted to A6000 and H800; results may differ on other GPUs
- Length predictor is BERT-based and requires fine-tuning per compression algorithm
- Negative sample analysis uses threshold-based definition which is heuristic

**Tags:** KV-cache, compression, quantization, sparsity, benchmarking, FlashAttention, PagedAttention, production-serving
