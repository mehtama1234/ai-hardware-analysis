# PIM Is All You Need: A CXL-Enabled GPU-Free System for Large Language Model Inference

**Venue:** ASPLOS · **Theme:** Processing-in-Memory (PIM)

## What It Does

LLM inference is memory-bound (GEMV-dominated decoding stage with ~21% GPU compute utilization on Llama2-70B), yet modern GPU/TPU systems are optimized for compute throughput; simultaneously, large KV-cache requirements per user limit batch sizes, and CXL- or DRAM-density-reduced PIM architectures individually lack sufficient memory capacity or scalability for trillion-parameter LLMs.

Running Llama2-70B on 4x A100 GPUs costs ~$694K/day for ChatGPT-scale inference while compute utilization remains below 25%, driving the need for memory-bandwidth-optimized, cost-efficient alternatives as LLM parameter sizes scale toward trillion parameters.

CENT (CXL-ENabled GPU-Free sysTem) uses a hierarchical PIM-PNM architecture deployed across 32 CXL devices interconnected via a CXL 3.0 switch. Each CXL device contains 16 GDDR6-PIM memory chips (two PIM channels each) housing near-bank MAC reduction-tree processing units (16 MAC units/PU, BF16, 32 GFLOPS/PIM channel), plus PNM units including 32 accumulators, 32 reduction trees, 32 Taylor-series exponent accelerators, and 8 BOOM-2-wide RISC-V cores for non-MAC operations. MAC operations (>99% of arithmetic) execute near-bank; Softmax, RMSNorm, square root, and RoPE are handled by PNM. A custom CXL ISA (MAC_ABK, WR_GB, SEND_CXL, BCAST_CXL, etc.) orchestrates computation and data movement. LLM parallelism is implemented via pipeline parallel (PP: each transformer block to one CXL device, multiple prompts pipelined) and tensor parallel (TP: transformer block partitioned across all devices using broadcast/gather over CXL) mappings, with hybrid TP-PP for QoS balance. The CXL protocol is extended with a broadcast primitive via a reserved H-slot header code in port-based routing flits.

## The Key Experiment

- **speedup:** 2.3x end-to-end throughput over 4x A100 80GB GPUs (throughput-critical); 4.6x latency reduction (batch=1); 3.3x decoding throughput at 32K context
- **energy or tops w:** 2.9x energy efficiency (tokens/joule) over 4x A100
- **area:** CXL controller: 19.0 mm2 at 7nm; custom logic: 7.85 mm2 at 28nm
- **ppa:** None
- **accuracy:** None
- **other:** 5.2x tokens per dollar (TCO); CENT owned TCO $0.73/hr vs GPU $1.76/hr; rental TCO $1.05/hr vs $5.45/hr

**Compared against:** 4x NVIDIA A100 80GB GPU with NVLink 3.0 running vLLM (batch=128)

**Hardware:** PIM (processing-in-memory); RISC-V; SoC · **Workloads:** LLM-inference; attention

## Why This Approach

A GPU-free hierarchical PIM-PNM architecture scaled via CXL 3.0 that exploits GDDR6-PIM internal bandwidth (512 TB/s aggregate) to achieve 2.3x higher LLM inference throughput than 4x A100 GPUs at 2.9x lower energy and 5.2x better TCO, with a novel CXL broadcast primitive enabling scalable collective communication across PIM devices.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: CENT: a GPU-free hierarchical PIM-PNM architecture over 32 CXL devices supporting full transformer block computation with 512 TB/s aggregate internal memory bandwidth..

## What It Leaves Open

- CENT underperforms GPU by 2x in the compute-intensive prefill stage due to lower peak FLOPS
- current evaluation limited to Llama2 (7B/13B/70B) at up to 32K context
- near-bank PIM memory density reduced to ~75% of standard GDDR6.

**Tags:** PIM, CXL, LLM-inference, GPU-free, memory-bandwidth
