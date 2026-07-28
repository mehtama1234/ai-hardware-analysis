# Ironwood: Delivering Best in Class perf, perf/TCO and perf/Watt for Reasoning Model Training and Serving

**Venue:** HOTCHIPS  
**Confidence:** low (abstract-only)

## Problem
Reasoning models (e.g., OpenAI o1, DeepSeek-R1) require massive compute for both training and inference with long-horizon thinking patterns; Ironwood targets optimal performance, TCO, and energy efficiency for this emerging workload class.

## Motivation
Reasoning models fundamentally change workload characteristics (longer token sequences, more compute per token, novel memory access patterns); existing GPUs/TPUs may not be optimized for reasoning-specific compute and memory requirements.

## Method
Ironwood likely combines enhanced memory bandwidth for extended compute/token reasoning traces, optimized matrix multiplication for reasoning compute patterns, and possibly novel interconnect/collective operation support tailored to reasoning model parallelization strategies.

## Key Novelty
Hardware architecture specifically optimized for reasoning model training and serving, balancing performance, cost, and energy efficiency.

## Contributions
- Hardware optimized for reasoning model compute and memory patterns
- Best-in-class performance/TCO ratio for reasoning model deployment
- Optimized energy efficiency for reasoning model training
- Demonstrated scalability for multi-chip reasoning model systems

## Hardware Targets
GPU, ASIC, TPU

## Techniques
memory-system, dataflow, circuit-design

## Workloads
LLM-training, LLM-inference, transformer

## Metrics
- Speedup: best-in-class reasoning model performance
- Energy: optimized energy efficiency vs. x86/GPU alternatives

## Baselines
H100/H200 GPUs, Google TPUv5, other AI accelerators

## Limitations
Not discussed.

## Tags
reasoning-models, training, serving, performance, tco, efficiency
