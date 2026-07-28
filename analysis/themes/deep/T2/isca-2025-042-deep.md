# LightNobel: Improving Sequence Length Limitation in Protein Structure Prediction Model via Adaptive Activation Quantization

**Venue:** ISCA · **Theme:** Domain-Specific Quantization

## What It Does

Protein Structure Prediction Models (PPMs) such as AlphaFold2 and ESMFold use a Pair Representation tensor with dimension (Ns, Ns, Hz) that grows quadratically in memory and cubically in attention score computation with sequence length Ns, causing GPU out-of-memory failures beyond ~2000 amino acids and latency dominated (>91%) by Triangular Attention at long sequences. Existing chunking and low-memory attention workarounds do not reduce the fundamental activation size and degrade performance.

Real-world protein analysis increasingly targets sequences exceeding 1000 amino acids (multimers, CASP16 targets up to 6879 aa), but activation size—not weights—is the dominant memory bottleneck in PPMs, requiring a hardware-software co-design approach tailored to PPM-specific activation statistics.

LightNobel applies Token-wise Adaptive Activation Quantization (AAQ) that exploits a distogram pattern unique to PPM: activations in the Pair Representation have large inter-token variance but small inter-channel variance, making token-wise quantization preferable to channel-wise. AAQ classifies Pair Representation activations into three groups based on value range and outlier density, applying INT8 inliers + INT16 outliers (Group A, high-magnitude pre-LayerNorm), INT4 inliers + INT16 outliers (Group B, post-LayerNorm with some outliers), and INT4 inliers without outlier handling (Group C, low-magnitude). Outliers are identified at runtime using a dynamic top-k algorithm on the VVPU via bitonic sorting. The hardware implements a Reconfigurable Matrix Processing Unit (RMPU) with bit-level reconfigurable adder trees and Reconfigurable Data Aligners (RDAs) that partition tokens into 4-bit chunks and dynamically configure PE Lanes (4 or 5 PE Lanes) to handle multi-precision token streams without per-element dequantization. A Versatile Vector Processing Unit (VVPU) with 128 SIMD Lanes and a Local Crossbar Network handles LayerNorm, Softmax, residual connections, and runtime quantization. A token-wise MHA dataflow similar to FlashAttention avoids materializing the full (Ns, Ns, Ns) score matrix. The design is synthesized at 28nm targeting 1 GHz with 5 HBM2E stacks (80 GB).

## The Key Experiment

- **speedup:** 8.44x over A100, 8.41x over H100 (Protein Folding Block); 1.74x end-to-end over ESMFold baseline
- **energy or tops w:** 37.29x power efficiency over A100, 43.35x over H100
- **area:** 28nm synthesis at 1 GHz
- **accuracy:** TM-Score loss <0.001 vs. FP16 baseline across CAMEO, CASP14, CASP15 datasets
- **other:** Peak memory reduced by 120.05x vs. FP16 baseline; activation footprint reduced to 7.90 GB vs. 113.49 GB for sequence length 3364

**Compared against:** NVIDIA A100 80GB PCIe; NVIDIA H100 80GB PCIe; ESMFold (FP16 baseline); AlphaFold2; FastFold; ColabFold; AlphaFold3; MEFold; PTQ4Protein; SmoothQuant; LLM.int8(); Tender

**Hardware:** ASIC · **Workloads:** transformer

## Why This Approach

Token-wise adaptive activation quantization exploiting PPM-specific distogram patterns in Pair Representation, combined with a bit-level reconfigurable matrix unit (RMPU) that dynamically allocates PE Lane groups (4 or 5) to handle mixed INT4/INT8/INT16 precision streams without full dequantization.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Discovery and characterization of token-wise distogram patterns in PPM Pair Representation activations enabling token-wise (vs. channel-wise) quantization without accuracy loss.

## What It Leaves Open

- The RMPU is designed specifically for PPM's small hidden dimension (128) and may not generalize efficiently to standard LLM workloads with large hidden dimensions (e.g., 4096).

**Tags:** protein-structure-prediction, activation-quantization, hardware-accelerator, alphafold, token-wise-quantization, reconfigurable-compute
