# Clo-HDnn: Continual On-Device Learning Accelerator with Hyperdimensional Computing via Progressive Search (hotchips-2025-033)

## Summary
Specialized accelerator for gradient-free on-device continual learning using hyperdimensional computing with progressive query optimization.

## Analysis
- **Problem**: On-device continual learning requires efficient gradient-free training under strict power/memory constraints
- **Method**: HDC with Kronecker encoding + weight clustering feature extraction; progressive search encodes/compares only partial query hypervectors, reducing complexity by 61%
- **Key Novelty**: Progressive search mechanism for partial hypervector encoding in HDC-based continual learning
- **Hardware**: ASIC, NPU
- **Techniques**: Circuit design, approximation, near-data processing
- **Workloads**: CNN, recommendation systems
- **Energy**: 4.66 TFLOPS/W (FE), 3.78 TOPS/W (classifier)
- **Speedup**: 7.77x (FE), 4.85x (classifier) vs SOTA
- **Confidence**: High (abstract provided)

## Tags
hyperdimensional-computing, on-device-learning, continual-learning, edge-ai, gradient-free
