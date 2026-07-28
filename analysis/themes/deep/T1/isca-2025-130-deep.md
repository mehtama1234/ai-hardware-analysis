# Insights into DeepSeek-V3: Scaling Challenges and Reflections on Hardware for AI Architectures

**Venue:** ISCA · **Theme:** KV Cache Scheduling

## What It Does

Training and serving 671B-parameter MoE LLMs at scale exposes critical hardware bottlenecks: HBM memory capacity growing <50%/year versus >1000%/year model memory demand, FP8 Tensor Core accumulation precision limited to 13 mantissa bits (FP22) causing numerical instability in large-scale training, NVLink bandwidth halved in H800 vs H100 (400 vs 900 GB/s) constraining tensor parallelism, and all-to-all expert parallelism (EP) communication consuming up to 20 GPU SMs for control-plane operations.

DeepSeek-V3, trained on only 2,048 H800 GPUs to state-of-the-art performance, demonstrates that hardware-software co-design can dramatically reduce the cost of frontier LLM training and inference, offering concrete lessons for next-generation hardware architects about where current GPU/network designs impose avoidable constraints.

The paper presents DeepSeek-V3's production architecture and infrastructure as a case study, covering: (1) Multi-head Latent Attention (MLA) that compresses KV cache from 516 KB/token (LLaMA-3.1-405B) to 70 KB/token via low-rank KV projection; (2) DeepSeekMoE with Node-Limited Routing constraining expert token dispatch to at most 4 of 8 nodes to exploit the 4:1 NVLink/IB bandwidth ratio, reducing inter-node IB traffic; (3) FP8 mixed-precision training with tile-wise 1x128 activation quantization and block-wise 128x128 weight quantization using DeepGEMM, requiring workarounds for FP22 accumulation precision on Hopper; (4) DualPipe overlapping MLA and MoE computation with all-to-all EP dispatch/combine via InfiniBand GPUDirect Async (IBGDA); (5) a Multi-Plane Two-Layer Fat-Tree (MPFT) network replacing a standard three-layer fat-tree, using 8 independent IB planes per node to support up to 16,384 GPUs at the same cost-per-endpoint as a two-layer topology. Experimental data includes real cluster training throughput (272.8B tokens/day, MFU 43.7%), EP bandwidth (>40 GB/s per GPU), and network latency comparisons (IB at 2.8 us same-leaf vs RoCE at 3.6 us).

## The Key Experiment

- **speedup:** MTP module achieves 1.8x generation TPS vs. no MTP; EP dispatch/combine >40 GB/s per GPU on MPFT; TPOT theoretical upper bound 67 tokens/s on H800 IB vs ~1200 tokens/s on GB200 NVL72
- **energy or tops w:** MFU 43.73% (non-causal) on 2048 H800 GPUs; 250 GFLOPS/token for 671B MoE vs 2448 for LLaMA-405B dense
- **area:** None
- **ppa:** None
- **accuracy:** FP8 training relative accuracy loss <0.25% vs BF16
- **other:** KV cache: 70 KB/token (MLA) vs 516 KB/token (LLaMA-405B GQA); training throughput 272.8B tokens/day; 2,048 H800 GPUs for full DeepSeek-V3 training

**Compared against:** NVIDIA H800 GPU cluster (standard three-layer fat-tree / MRFT); LLaMA-3.1-405B (GQA KV cache); Qwen-2.5-72B; Dense model training (full-parameter activation)

**Hardware:** GPU · **Workloads:** LLM-training; LLM-inference; MoE; attention

## Why This Approach

Systematic hardware-software co-design analysis from a production 671B MoE LLM system that quantifies the bottlenecks in FP8 accumulation precision, NVLink/IB bandwidth asymmetry, and EP control-plane SM consumption, and proposes the Multi-Plane Fat-Tree topology as a cost-equivalent path to 8x scale-out beyond single-plane two-layer fat trees.

This paper sits in the **attention efficiency** subtheme. The core constraint: generating one token requires reading all past key-value vectors from memory — O(n) bandwidth per step. This paper's angle: MLA: low-rank KV projection reducing KV cache 7.4x vs. LLaMA-3.1-405B (70 KB vs 516 KB per token), enabling memory-efficient inference on constrained hardware..

## What It Leaves Open

- Hardware suggestions (FP32 accumulators, native group-scaling Tensor Cores, unified NVLink/IB NIC) are forward-looking design recommendations not yet validated in silicon
- regulatory constraints capped deployment at ~2,048 GPUs, preventing full characterization of MPFT at 16K+ GPU scale.

**Tags:** llm-training, moe, fp8, interconnect, kv-cache, multi-plane-network
