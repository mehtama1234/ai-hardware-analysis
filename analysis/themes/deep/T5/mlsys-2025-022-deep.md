# Enabling Unstructured Sparse Acceleration on Structured Sparse Accelerators

**Venue:** MLSYS 2025 · **Subtheme:** Bridging Unstructured and Structured Sparsity

## What It Does

TASD (Tensor Approximation via Structured Decomposition) decomposes any unstructured sparse tensor into a series of N:M structured sparse tensors, enabling unstructured sparse models (from conventional pruning pipelines) to run on structured sparse accelerators (e.g., NVIDIA 2:4 Tensor Cores) without fine-tuning. The method exploits the distributive property of tensor algebra: any weight matrix W can be approximated as a sum W ≈ W₁ + W₂ + ... + Wₖ where each Wᵢ is N:M structured.

TASD-W performs offline weight decomposition via greedy layer-wise search: for each layer, it iteratively extracts N:M patterns that maximize the sum of absolute values (keeping high-impact weights) while dropping low-value elements, maintaining 99% model quality. The algorithm is greedy within each layer and quality-constrained (stops when 99% quality is reached).

TASD-A handles dynamic runtime activation decomposition: as activations flow through the network, the system detects sparsity patterns and selects which N:M structured forms to apply, with pattern selection driven by sparsity degree (if activations have 50% zeros, select 2:4; if 75%, select 1:4).

TTC (TASD Tensor Core) extends existing structured sparse accelerators (VEGETA, STC) to support multiple N:M patterns simultaneously via hardware modifications. A decomposition-aware dataflow keeps B/C tiles stationary while multiple A tile passes occur, amortizing the decomposition overhead across multiple structured sparse operations.

## The Key Result

On NVIDIA RTX 3080 GPU (2:4 sparse Tensor Cores), TASD achieves 39% speedup over dense Tensor Core execution on unstructured sparse DNNs. Energy-delay product (EDP) improves up to 83% (dense DNNs) and 74% (sparse DNNs). Computation reduction reaches 40% while maintaining 99% model quality.

## Why This Approach

State-of-the-art sparse accelerators support only fixed N:M patterns (2:4, 1:2, etc.) for hardware efficiency; unstructured sparse models from magnitude pruning are incompatible and require fine-tuning for each target hardware. Fine-tuning adds delay, cost, and per-hardware testing overhead. TASD's key insight is the distributive property: instead of forcing unstructured sparsity into one N:M pattern (lossy), decompose it into multiple patterns and sum them. Each pattern individually fits structured accelerator execution, so the hardware need not handle irregular sparsity at all—it just runs multiple structured operations and adds results. This preserves sparsity structure while remaining hardware-agnostic.

## Why This Approach

Greedy decomposition is efficient: at each iteration, the algorithm selects N:M weights that maximize value sum, leaving low-value elements in the residual for the next iteration. This maximizes information retention per decomposition step, requiring fewer total patterns (typically 2-4 patterns suffice for 99% quality).

## What It Leaves Open

- Decomposition introduces multiple passes over structured sparse hardware; each additional pattern multiplies the memory access cost, and decomposition overhead (tile reads/writes/adds) is not explicitly characterized.
- Quality guarantee (99%) is a heuristic threshold, not a formal bound; deeper analysis of why 99% is sufficient or when it is insufficient missing.
- TASD-A runtime overhead (pattern detection latency) depends on sparsity pattern detection algorithms not fully specified; could add meaningful overhead if done in software.
- Evaluation focused on 2:4 Tensor Cores; applicability to other structured patterns (2:8, 1:4 block sparsity) or non-N:M structured accelerators (block sparsity, row sparsity) unclear.
- Comparison baseline limited to dense and DSTC (dual-side sparse tensor core); other decomposition-based sparsity methods not compared.
