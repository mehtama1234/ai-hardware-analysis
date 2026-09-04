# Memory Is All You Need

## Bibliographic Identity

- Title: Memory Is All You Need: An Overview of Compute-in-Memory Architectures for Accelerating Large Language Model Inference
- Year: 2024
- Venue or source: arXiv
- Link: https://arxiv.org/abs/2406.08413
- Track: digital-design-and-architecture
- Subtheme: compute-in-memory taxonomy for LLM inference

## First-Principles Reading

The object being controlled is the whole LLM inference workload: weights, activations, KV cache, operators, memory traffic, and accelerator boundaries. The survey is useful because it separates compute-in-memory choices instead of treating memory-side compute as one idea.

The constraint is that LLM inference is not uniformly matrix multiplication. Prefill, decode, long context, batch size, attention, MLP projections, cache reads, and output decisions stress different parts of the machine. A compute-in-memory design can help one part while leaving another as the bottleneck.

The mathematical form is a taxonomy over operators and memory movement. For each operator, ask where the data lives, how often it moves, whether the operation is dense or control-heavy, and whether analog or digital CIM is a good fit.

The concrete method is survey and classification. The evidence artifact is the mapping of transformer operators to CIM architectures and the discussion of open challenges. The failure boundary is that a taxonomy is not a measured chip; every proposed path still needs accuracy, energy, latency, and peripheral-circuit evidence.

## Concept Links

Related concept articles:

- hybrid-foundation-model-accelerators-are-partitioning-problems
- adc-dac-boundaries-set-analog-compute-cost
- power-is-switching-leakage-and-delivery-loss
- area-is-a-physical-budget
- where-analog-compute-actually-helps
- attention-is-changing-memory-not-fixed-weights
- softmax-turns-score-error-into-selection-error
- transformer-block-error-is-state-drift
- analog-serving-policy-decides-when-to-use-the-array
- hybrid-analog-digital-accelerators-need-a-control-plane

Related labs:

- labs/analog/analog-in-memory-foundation-model-hardware

## What The Paper Teaches

The lesson is that the right unit of analysis is the workload, not the array. A crossbar may be excellent at one projection, while decode remains limited by KV-cache movement or peripheral conversion.
