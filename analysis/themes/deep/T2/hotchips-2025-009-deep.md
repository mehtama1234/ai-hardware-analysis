# MEGA.mini: A NPU with Novel Heterogeneous AI Processing Architecture Balancing Efficiency, Performance, and Intelligence for the Era of Generative AI

**Venue:** HOTCHIPS · **Theme:** Mixed-Precision Hardware

## What It Does

AI accelerators must balance low-precision compute efficiency against accuracy preservation for outlier values; MEGA.mini proposes a heterogeneous NPU architecture supporting both fixed-point and floating-point computation dynamically.

Generative AI requires both massive compute efficiency (>95% quantized operations) and numerical precision for activation outliers; hybrid precision enables accuracy without sacrificing efficiency.

MEGA.mini combines a large fixed-point compute fabric (FXP, >95% operations) with a smaller floating-point unit handling outlier values (<5%), using a big.LITTLE heterogeneous core design that switches between execution modes based on data characteristics. Three hierarchical solutions (MEGA, median, mini) scale across deployment targets.

## The Key Experiment

- **energy or tops w:** high efficiency through FXP, preserved accuracy via hybrid precision
- **accuracy:** >95% computation in low-precision; FP for <5% outliers

**Compared against:** Pure quantized NPUs; Full-precision AI accelerators; contemporary mobile NPUs

**Hardware:** NPU; ASIC · **Workloads:** LLM-inference; transformer; diffusion

## Why This Approach

Heterogeneous big.LITTLE architecture intelligently routing quantized vs. outlier data to specialized compute units, enabling adaptive precision with high efficiency.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Heterogeneous NPU architecture with integrated FXP + FP compute.

## What It Leaves Open

- Scalability to very large models and training phase support not discussed.

**Tags:** npu, hybrid-precision, quantization, big-little, generative-ai, adaptive
