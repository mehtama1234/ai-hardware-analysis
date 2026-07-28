# Clo-HDnn: Continual On-Device Learning Accelerator with Hyperdimensional Computing via Progressive Search

**Venue:** HOTCHIPS · **Theme:** On-Device HDC Learning

## What It Does

On-device continual learning requires efficient gradient-free training for edge devices with strict power and memory constraints.

Emerging edge AI applications demand continual learning without cloud connectivity; hyperdimensional computing offers a gradient-free alternative enabling efficient incremental model updates.

Clo-HDnn integrates hyperdimensional computing (HDC) with low-cost Kronecker encoding and weight clustering feature extraction (WCFE); progressive search reduces query complexity by 61% by encoding/comparing only partial query hypervectors in a gradient-free learning paradigm.

## The Key Experiment

- **energy efficiency fe:** 4.66 TFLOPS/W
- **energy efficiency classifier:** 3.78 TOPS/W
- **speedup vs sota:** 7.77x (FE), 4.85x (classifier)

**Compared against:** SOTA ODL accelerators

**Hardware:** ASIC; NPU · **Workloads:** CNN; recommendation

## Why This Approach

Progressive search mechanism reducing HDC query complexity by partial hypervector encoding for efficient on-device continual learning.

This paper sits in the **memory hierarchy** subtheme. The core constraint: compute starves waiting for data — arithmetic throughput far outpaces DRAM bandwidth. This paper's solution: Specialized accelerator for hyperdimensional computing and on-device continual learning.

## What It Leaves Open

- Progressive search applicability limited to datasets where partial queries maintain classification confidence.

**Tags:** hyperdimensional-computing, on-device-learning, continual-learning, edge-ai
