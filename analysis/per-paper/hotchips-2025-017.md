# EdgeDiff: Multi-modal Few-step Diffusion Model Accelerator with Mixed-Precision and Reordered Group-Quantization for On-device Generative AI

**Venue:** HOTCHIPS
**Authors:** Sangjin Kim, Jungjun Oh, Jeonggyu So, Yuseon Choi, Sangyeob Kim, Dongseo Kim, Gwangtae Park, Hoi-Jun Yoo
**ID:** hotchips-2025-017
**Confidence:** low

## Problem
Diffusion models for image/video generation require iterative inference passes, causing prohibitive latency and energy on edge devices; reducing inference steps while maintaining quality is challenging.

## Motivation
On-device diffusion enables real-time content creation (image/video) without cloud connectivity, but multi-step diffusion is too expensive for edge hardware.

## Method
EdgeDiff accelerates diffusion image generation with three techniques: mixed-precision arithmetic (lower-precision math in layers where quality doesn't matter), reordered group quantization (compression that groups similar weights to minimize error), and few-step distillation (training the model to produce good results in fewer steps). The hardware exploits temporal coherence—since each step is similar to the previous one—to reuse computation results instead of recalculating them.

## Key Novelty
EdgeDiff enables real-time image generation on edge devices by jointly optimizing model compression and hardware execution.

## Contributions
- Mixed-precision quantization strategy for diffusion models
- Reordered group quantization reducing quantization error
- Few-step distillation accelerating convergence
- Hardware-efficient multi-modal inference (image + text/audio)

## Hardware Target
- ASIC
- NPU

## Technique Categories
- quantization
- kernel-fusion
- scheduling

## Workloads
- diffusion
- vision

## Metrics
- **latency:** real-time inference
- **energy:** <W

## Baselines
- Full-precision diffusion
- Standard quantization methods

## Limitations
Quantitative energy/latency numbers and comparison with other edge diffusion accelerators not provided.

## Tags
diffusion, edge, quantization, generative-ai, accelerator

## Primary Theme
Efficient edge diffusion via mixed-precision acceleration
