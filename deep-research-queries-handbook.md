# GPU Systems & Kernel Engineering: Deep Research Queries Handbook

This handbook compiles **all 24 advanced technical and hiring categories** discussed across your 145 sources and 74 audio overview artifacts. These queries are specifically structured to find state-of-the-art (SOTA) research publications, academic papers (via arXiv and Google Scholar), and industry engineering practices.

---

## How to Use These Queries
- **Exact Phrases:** Double quotes (e.g., `"FlashAttention-3"`) force search engines to find exact matches.
- **Boolean Operators:** Use `AND` to combine concepts and `OR` to search for alternative terminology.
- **Academic Filters:** Append `site:arxiv.org` or `arXiv` to target preprints, or use Google Scholar for peer-reviewed citations.
- **Github Repositories:** Append `site:github.com` or `"GitHub"` to find open-source source code and developer documentation.

---

## Table of Contents
1. [High-Performance Attention Mechanisms & Long-Context Scaling](#1-high-performance-attention-mechanisms--long-context-scaling)
2. [Extreme Quantization & Low-Precision Numerics](#2-extreme-quantization--low-precision-numerics)
3. [GPU Domain-Specific Languages (DSLs) & Kernel Frameworks](#3-gpu-domain-specific-languages-dsls--kernel-frameworks)
4. [Distributed Systems, Interconnects, & Low-Latency Collectives](#4-distributed-systems-interconnects--low-latency-collectives)
5. [Compiler Auto-Tuning, Kernel Fusion, & Automated Optimization](#5-compiler-auto-tuning-kernel-fusion--automated-optimization)
6. [High-Throughput & Low-Latency LLM Serving Systems](#6-high-throughput--low-latency-llm-serving-systems)
7. [Modern GPU Profiling, Microarchitecture, & Hardware Plumbing](#7-modern-gpu-profiling-microarchitecture--hardware-plumbing)
8. [Hardware-Accelerated Reinforcement Learning & Simulation](#8-hardware-accelerated-reinforcement-learning--simulation)
9. [Cross-Vendor Hardware Acceleration & Portable Runtimes](#9-cross-vendor-hardware-acceleration--portable-runtimes)
10. [Formal DSL Theory, Category-Theoretic Layouts & Functional Languages](#10-formal-dsl-theory-category-theoretic-layouts--functional-languages)
11. [GPU-Accelerated Data Analytics, Video Generation & Multimodal Serving](#11-gpu-accelerated-data-analytics-video-generation--multimodal-serving)
12. [Kernel Correctness, Automated Benchmarking & GPU Observability](#12-kernel-correctness-automated-benchmarking--gpu-observability)
13. [Novel Training Optimizers & Custom Training Frameworks](#13-novel-training-optimizers--custom-training-frameworks)
14. [Microarchitectural Memory Plumbing (TMA, SRAM Swizzling & Bank Conflicts)](#14-microarchitectural-memory-plumbing-tma-sram-swizzling--bank-conflicts)
15. [Mixture-of-Experts (MoE) & Sparse Matrix Computations](#15-mixture-of-experts-moe--sparse-matrix-computations)
16. [AI-Driven Automated Kernel Synthesis & Verification](#16-ai-driven-automated-kernel-synthesis--verification)
17. [Hardware-Software Co-Design for Disaggregated Memory & CXL](#17-hardware-software-co-design-for-disaggregated-memory--cxl)
18. [Parallel Algorithmic Primitives at "Speed-of-Light"](#18-parallel-algorithmic-primitives-at-speed-of-light)
19. [Edge Compute & Consumer Hardware Frontiers](#19-edge-compute--consumer-hardware-frontiers)
20. [Grassroots Performance Hacking & Competitive Kernel Design](#20-grassroots-performance-hacking--competitive-kernel-design)
21. [Symbolic Autograd Hacking & Analytical Derivative Simplification](#21-symbolic-autograd-hacking--analytical-derivative-simplification)
22. [Dynamic Multimodal Pipelines & Cross-Modal Routing](#22-dynamic-multimodal-pipelines--cross-modal-routing)
23. [On-GPU World Simulators & Massively Parallel Physics Engines](#23-on-gpu-world-simulators--massively-parallel-physics-engines)
24. [Tech Industry Job Profiles & Interview Loops](#24-tech-industry-job-profiles--interview-loops)

---

### 1. High-Performance Attention Mechanisms & Long-Context Scaling
Focuses on sequence-length scaling barriers, FlashAttention iterations, Ring Attention, and PageAttention orchestration.

```text
"FlashAttention-4" OR "FlashAttention-3" "warp specialization" "TMA" "WGMMA" arXiv
"Ring Attention" OR "Sequence Parallelism" long-context LLM communication overlap
"FlashInfer" OR "Block-Sparse Attention" "KV cache" PagedAttention benchmarking 2024..2026
"PaTH Attention" OR "Positional Encodings" relative position householder transform arXiv
"Attention Sinks" OR "StreamingLLM" streaming inference KV-cache eviction policies
```

### 2. Extreme Quantization & Low-Precision Numerics
Focuses on microscaling formats (MX), sub-8-bit training mechanics, stochastic rounding, and loss-scaling stability.

```text
"NVFP4" OR "MXFP4" "microscaling formats" OCP specification LLM pre-training
"Quartet" "unbiased quantization" "random rotations" "Hadamard transform" FP4 LLM
"BitBLAS" OR "BitNet" 1.58-bit weight-only quantization GPU GEMM kernels
"stochastic rounding" "low precision training" NVFP4 RL stability
"scaling laws for precision" quantization loss degradation LLM empirical bounds
```

### 3. GPU Domain-Specific Languages (DSLs) & Kernel Frameworks
Focuses on writing portable and non-portable custom kernels utilizing layouts, tile algebras, and template-driven DSLs.

```text
"CuTe DSL" "Layout Algebra" tile-based GEMM CUTLASS 3 Hopper Blackwell
"Gluon" "Linear Layouts" Triton compiler multi-CTA MMA optimization
"ThunderKittens" OR "HipKittens" embedded C++ DSL GPU kernel templates
"Helion DSL" OR "TLX" user-defined tile layouts Triton optimization
"WebGPU" OR "gpu.cpp" portable GPU compute LLM inference performance
```

### 4. Distributed Systems, Interconnects, & Low-Latency Collectives
Focuses on node-synchronization structures, direct device-to-device communication, and high-performance fabric collectives.

```text
"low-latency all-reduce" NVSHMEM "symmetric memory" device-initiated collectives
"Disaggregated LLM Inference" "prefill decode disaggregation" Mooncake Nixon
"PCCL" OR "fault-tolerant collectives" bitwise deterministic distributed GPU
"NVLink" peer-to-peer direct memory access LLM tensor parallelism latency
"Monarch" "single controller programming" multi-GPU async RL distributed training
```

### 5. Compiler Auto-Tuning, Kernel Fusion, & Automated Optimization
Focuses on deep compiler graph rewrites, mathematical optimizations, and multi-level superoptimizers searching the structural assembly space.

```text
"Mirage" "multi-level superoptimizer" "mega-kernel" LLM compilation
"torch.compile" Inductor custom Triton operator functionalization autotuning
"KernelBench" OR "BackendBench" LLM kernel correctness evaluation benchmark
"search-based deep learning compiler" graph rewrite rules kernel fusion
"Luminal" OR "production megakernels" real-world LLM serving pipeline fusion
```

### 6. High-Throughput & Low-Latency LLM Serving Systems
Focuses on operational serving infrastructure, speculative token generation architectures, prefix matching, and multi-token generation.

```text
"SGLang" "RadixAttention" prefix caching LLM serving benchmark
"vLLM" "speculative decoding" continuous batching latency throughput trade-offs
"Multi-Token Prediction" OR "Medusa decoding" draft-model-free speculative inference
"Cornserve" multimodal LLM serving disaggregated encoder pipeline
"InferenceX" open-source LLM inference continuous benchmarking best practices
```

### 7. Modern GPU Profiling, Microarchitecture, & Hardware Plumbing
Focuses on decoding hardware latency, memory hierarchies, Nsight analytics, and raw machine instruction (SASS) profiling.

```text
"SASS assembly" NVIDIA GPU microarchitecture stall reasons profiling
"2:4 structured sparsity" cuSPARSELt fused dynamic quantization GEMM
"speed-of-light" GPU memory bandwidth warp occupancy Roofline model
"Nsight Compute" NCU profiling CUDA kernel memory scoreboard stalls
"int8 tensor core" Turing matrix multiplication manual assembly optimization
```

### 8. Hardware-Accelerated Reinforcement Learning & Simulation
Focuses on vectorized game loops, on-GPU simulators, and zero-copy RL step execution.

```text
"LeanRL" OR "GPU-accelerated environment" RL rollout throughput zero-copy
"Factorio Learning Environment" OR "OpenEnv" parallel agent environment GPU
"NVFP4" "reinforcement learning" policy gradient numerics stability FP4
"GPU parallel RL environments" Isaac Gym CUDA vectorized state transition
```

### 9. Cross-Vendor Hardware Acceleration & Portable Runtimes
Focuses on compiling and executing neural workloads outside NVIDIA's proprietary CUDA stack.

```text
"Composable Kernel" AMD ROCm GEMM tile matrix instruction tuning
"Spectral Compute" CUDA compilation non-NVIDIA GPU ISA binary translation
"gpu.cpp" WebGPU cross-platform tensor compute embedded LLM
"Metal Performance Shaders" low-bit quantization Apple Silicon SIMDGroup
"SYCL" Intel OneAPI GPU kernel optimization LLM inference benchmark
```

### 10. Formal DSL Theory, Category-Theoretic Layouts & Functional Languages
Focuses on formal layout definitions, category-theoretic bijections, and provably bank-conflict-free GPU array compilation.

```text
"CuTe Layout Algebra" category theory functor bijection GPU memory layout
"formal kernel derivation" functional array programming GPU compiler
"Futhark" OR "Dex" functional data-parallel compiler high-performance GPU
"Exo language" user-directed schedule rewrite rules sparse matrix GEMM
```

### 11. GPU-Accelerated Data Analytics, Video Generation & Multimodal Serving
Focuses on spatial-temporal attention, high-throughput media synthesis, and disaggregated cross-modal execution.

```text
"FastVideo" OR "video diffusion GPU acceleration" dynamic sequence length pipeline
"Cornserve" multimodal LLM serving vision encoder disaggregation
"cuDF" OR "GPU dataframe" parallel scan join filter memory throughput
"spatial-temporal attention" GPU kernel optimization video generation
```

### 12. Kernel Correctness, Automated Benchmarking & GPU Observability
Focuses on debugging silent numerical errors, structural verification pipelines, and hardware execution tracking.

```text
"BackendBench" LLM kernel correctness evaluation framework
"GPU Observability" kernel execution tracing memory fragmentation profiling
"InferenceX" open-source LLM serving throughput latency benchmark suite
"automated GPU kernel benchmarking" fuzzing numerical accuracy evaluation
```

### 13. Novel Training Optimizers & Custom Training Frameworks
Focuses on second-order preconditioning, Newton-Schulz matrix iterations, and memory-efficient training mechanics.

```text
"Muon optimizer" OR "Soap optimizer" matrix orthogonalization LLM training
"Liger Kernel" fused cross-entropy RMSNorm Triton LLM training memory reduction
"Torchtitan" PyTorch 3D parallelism distributed LLM training benchmark
"llm.cpp" pure CUDA C++ LLM training zero-overhead runtime
```

### 14. Microarchitectural Memory Plumbing (TMA, SRAM Swizzling & Bank Conflicts)
Focuses on Hopper/Blackwell hardware properties, asynchronous data transit, and SRAM memory access patterns.

```text
"Tensor Memory Accelerator" TMA async copy "shared memory swizzling" Hopper
"bank conflict avoidance" GPU matrix transposition shared memory indexing
"register spill mitigation" CUDA occupancy warp allocation SASS optimization
"L2 cache residency" persistence control NVIDIA H100 memory hierarchy
"tcgen05.mma" OR "Blackwell TMEM" Tensor Memory CUTLASS 3.x
```

### 15. Mixture-of-Experts (MoE) & Sparse Matrix Computations
Focuses on communication-computation overlaps, RDMA engines, and adaptive fine-grained expert routing.

```text
"MoE token routing" All-to-All communication overlap GPU kernel
"DeepSeek-V3" OR "DeepSeek-R1" fine-grained expert routing latency
"2:4 structured sparsity" cuSPARSELt GEMM performance benchmark 2024..2026
"sparse MoE inference" dynamic load balancing disaggregated expert parallelism
```

### 16. AI-Driven Automated Kernel Synthesis & Verification
Focuses on programmatic generation of CUDA/Triton kernels using neural models, static linting, and formal equivalence proofs.

```text
"LLM CUDA generation" automated GPU kernel synthesis formal verification
"kernel superoptimization" search-based compilation Triton CUDA assembly
"automated regression testing" GPU numerical precision floating point equivalence
"RL agent GPU kernel tuning" search space exploration matrix multiplication
"Gimlet" OR "ProofWright" separation logic SMT equivalence checking GPU
```

### 17. Hardware-Software Co-Design for Disaggregated Memory & CXL
Focuses on CXL architectures, rack-scale KV cache disaggregation, and memory fabrics.

```text
"TraCT" OR "Beluga-KVCache" CXL disaggregated KV cache rack-scale TTFT
"Sparse Attention on CXL" SAC HiSparse "Lightning Indexer" DeepSeek
"Photonic Fabric Memory Appliance" PFMA optical CXL switchless crossbar
"NVIDIA IMEX" Internode Memory Exchange fabric address translation multi-node NVLink
"TurboBus" PCIe bandwidth pooling NVLink scale-up multi-tenant LLM
```

### 18. Parallel Algorithmic Primitives at "Speed-of-Light"
Focuses on single-pass decoupled look-back prefix scans, Onesweep sorting, and matrix identity scan decompositions.

```text
"decoupled look-back" parallel prefix scan CUDA speed-of-light
"GPU Radix Sort" memory bandwidth limit thread-block synchronization
"ScanUL1" Huawei Ascend 910B AIC matrix scan identity vector core
"parallel reduction tree" warp shuffle primitives latency optimization
"Onesweep" RADIX_RANK_MATCH_EARLY_COUNTS_ANY CUB radix rank
```

### 19. Edge Compute & Consumer Hardware Frontiers
Focuses on running high-performance workloads on consumer chips, Apple Silicon, and WebGPU configurations.

```text
"Metal tile shaders" Apple Silicon unified memory matrix multiplication
"consumer GPU LLM inference" PCIe bottleneck RTX 4090 memory bandwidth
"WGSL compilation latency" WebGPU compute pipeline optimization
"ARM NEON" low-bit SIMD group quantization mobile LLM execution
```

### 20. Grassroots Performance Hacking & Competitive Kernel Design
Focuses on open-source community communities, Discord automated performance loops, and rapid-turnaround algorithmic competitions.

```text
"GPU MODE" OR "One Layer Deeper" competitive kernel optimization CUDA
"Discord bot benchmark" community GPU compiler profiling real-time feedback
"collaborative systems engineering" open-source machine learning systems compiler
"crowdsourced CUDA optimization" hackathons performance profiling
```

### 21. Symbolic Autograd Hacking & Analytical Derivative Simplification
Focuses on manual backprop optimizations, analytically deriving gradients, and cutting forward activation footprints.

```text
"Unsloth" "analytical gradients" LLM training memory reduction
"manual autograd CUDA" fused backward pass activation memory savings
"symbolic derivative simplification" custom backward kernel backpropagation
"fused autograd Triton" loss function backprop memory optimization
```

### 22. Dynamic Multimodal Pipelines & Cross-Modal Routing
Focuses on disaggregated visual/audio architectures, cross-modal alignments, and heterogeneous pipeline orchestration.

```text
"Cornserve" OR "multimodal serving system" disaggregated vision encoder
"dynamic token granularity" vision language model serving GPU orchestration
"cross-modal synchronization" audio text model pipeline pipeline parallel
"heterogeneous hardware serving" multimodal LLM prefill decode alignment
```

### 23. On-GPU World Simulators & Massively Parallel Physics Engines
Focuses on running RL environments directly on-chip to eliminate PCIe memory transit stalls.

```text
"Factorio Learning Environment" OR "on-GPU simulation" RL environment throughput
"parallel physics engine" CUDA thread block environment rollout execution
"massively parallel state transition" GPU vectorized game engine execution
"zero-copy RL simulation" GPU-bound environment steps rollout policy
```

### 24. Tech Industry Job Profiles & Interview Loops
Focuses on modern engineering hiring loops, compensation benchmarks, and deep-technical examination expectations for kernel/systems roles.

```text
"GPU Kernel Engineer" job description "Blackwell" "TMEM" "TMA" OR "WGMMA"
"AI Kernel Engineer" interview questions "bank conflict swizzling" "CUTLASS 3"
"NVIDIA" "Kernel Architect" "SASS assembly" "Nsight Compute" optimization
"Distributed Systems Engineer" "ML Infrastructure" "NCCL" OR "NVSHMEM" "RDMA"
"OpenAI" OR "Anthropic" "Distributed Training Engineer" interview loop "pipeline parallelism"
"Systems Engineer" "InfiniBand" OR "RoCEv2" "GPUDirect" debugging hang packet loss
"Compiler Engineer" "Triton" "MLIR" pass optimization Triton-MLIR lowering
"Quantization Engineer" "FP8" OR "FP4" pre-training framework implementation OCP
"vLLM" OR "SGLang" "speculative decoding" SLA throughput
"Metal GPU Engineer" "Apple Silicon" "Metal Shaders" "matrix multiplication"
```
