# LUT Tensor Core: A Software-Hardware Co-Design for LUT-Based Low-Bit LLM Inference

**Venue:** ISCA · **Theme:** LUT-Based Low-Precision Compute

## What It Does

Low-bit LLM inference (INT4/2/1 weights × FP16/INT8 activations) requires mixed-precision GEMM (mpGEMM), an operation not natively supported by existing GPU Tensor Cores, forcing inefficient dequantization-based workarounds. Lookup-table (LUT) approaches can in principle replace multiplications with table lookups, but conventional LUT hardware incurs prohibitive table precomputation and storage overhead that negates the area and efficiency gains.

Weight quantization to 1–4 bits is a primary strategy for reducing LLM memory footprint and inference cost, but without native hardware support for mpGEMM, dequantization overhead becomes a significant bottleneck, particularly at large batch sizes.

LUT Tensor Core is a software-hardware co-design: on the software side, table precomputation is extracted into an independent kernel via dataflow graph (DFG) transformation and fused with the preceding element-wise operator to eliminate redundant computation; weight values are reinterpreted from {0,1} to {-1,+1} to exploit lookup table symmetry and halve storage. On the hardware side, a bit-serial LUT Tensor Core microarchitecture with an elongated MNK tiling shape (M=2, N=64, K=4 optimal) maximizes table reuse across the N dimension while keeping table size bounded; a dedicated LMMA instruction set extends existing MMA ISA and integrates with TVM/Roller/Welder compilation stacks for end-to-end kernel generation.

## The Key Experiment

- **speedup:** 1.42x GEMV and 72.2x GEMM over LUT-GEMM software; 2.06–5.51x end-to-end LLM inference speedup
- **energy or tops w:** 1.44x compute density and energy efficiency over UNPU (SOTA LUT accelerator); 33.65 TOPs/W at 28nm
- **area:** LUT TC occupies 16% area of conventional FP16 Tensor Core; 4–6x area reduction for 1-bit weights
- **ppa:** 61.84 TOPs/mm2 compute density vs. 2.96 TFLOPs/mm2 for FP16 MAC (>20x at same 28nm node)

**Compared against:** NVIDIA A100 GPU with cuBLAS (FP16); CUTLASS dequantization-based INT4 kernel; LUT-GEMM (software LUT); UNPU (LUT-based ASIC accelerator)

**Hardware:** GPU; ASIC · **Workloads:** LLM-inference

## Why This Approach

Co-designing software-level LUT symmetrization and operator fusion with a hardware bit-serial elongated-tiling Tensor Core achieves 4–6x power/area reduction over MAC-based Tensor Cores while outperforming prior LUT hardware by 1.44x in compute density and energy efficiency.

This paper sits in the **quantization** subtheme. The core tension: lower precision = smaller model = less memory bandwidth, but at the cost of rounding error that compounds across layers. This paper's bet: Identification that conventional LUT hardware fails to deliver area/power gains due to precomputation and storage overhead, motivating a software-hardware co-design..

## What It Leaves Open

- Full hardware validation requires tape-out
- results rely on Accel-Sim simulation and an analytical tile-based simulator with ~5.21% mean error
- register file capacity is a practical bottleneck limiting large tiling benefits on real GPUs.

**Tags:** lut, mpgemm, low-bit-llm, quantization, tensor-core, software-hardware-codesign
