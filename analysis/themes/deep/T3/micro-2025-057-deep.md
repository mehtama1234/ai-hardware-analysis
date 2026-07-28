# Pimba: A Processing-in-Memory Acceleration for Post-Transformer Large Language Model Serving

**Venue:** MICRO · **Theme:** Post-Transformer PIM

## What It Does

Post-transformer LLMs (SSMs such as Mamba-2, linear attention, RNNs) and transformer-based LLMs both become memory-bandwidth-bound during batched inference due to state update and attention operations respectively, but the diverse primitives in state updates (element-wise multiply, outer product, GEMV) make per-bank PIM acceleration area-prohibitive, and existing LLM quantization formats degrade accuracy severely on SU-LLMs due to the swamping effect.

Hyperscalers are exploring post-transformer architectures as bandwidth-efficient complements to transformers for long-context serving; a unified hardware solution supporting both model families does not yet exist.

Pimba implements a PIM accelerator array where each State-update Processing Unit (SPU) is shared between two DRAM banks via access interleaving: while one bank is being read, the paired bank writes its result, enabling continuous utilization of a single pipelined SPU without throughput loss. Each SPU contains a State-update Processing Engine (SPE) with custom MX8 multipliers and adders (MX format with 8-bit shared exponent and 1-bit microexponents, 16 elements per group, using stochastic rounding). The four-stage SPE pipeline executes: (1) state fetch, (2) state decay plus outer product in parallel, (3) accumulate, (4) GEMV output and write-back. KV-cache attention is accelerated by reusing the same SPU logic in an attention mode dataflow. The system offloads state update and attention to PIM during the generation phase while the GPU handles prefill and other operations.

## The Key Experiment

- **speedup:** up to 4.1x token generation throughput over LLM-optimized GPU; up to 2.1x over GPU+PIM baseline; 14.6x lower state-update latency vs GPU
- **other:** Area overhead described as minimal on DRAM device; MX8 achieves near fp16 perplexity on Mamba-2/RetNet/GLA/HGRN2

**Compared against:** A100 GPU (LLM-optimized); GPU+PIM systems (per-bank time-multiplexed and pipelined PIM designs)

**Hardware:** PIM (processing-in-memory); GPU · **Workloads:** LLM-inference; attention; MoE

## Why This Approach

Sharing one pipelined SPU between two DRAM banks via access interleaving halves PIM area overhead compared to per-bank designs while maintaining the same throughput.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Systematic workload characterization showing state update operations in SU-LLMs are memory-bandwidth-bound and dominate generation latency at large batch sizes.

## What It Leaves Open

- Evaluation is simulation-based
- real DRAM integration with SPUs has not been taped out, and full system energy is not reported.

**Tags:** pim, llm-inference, ssm, mamba, quantization, mx8, post-transformer
