# MLSys 2025 — Deep Dive

## What MLSys is and why it exists

MLSys is the systems track of machine learning—the enabling infrastructure that makes models practical to train and serve at scale. Where machine learning researchers ask "what models can we build?" systems researchers ask "how do we make those models run faster, cheaper, and more reliably on real hardware?" MLSys sits at the intersection of systems engineering (networking, storage, memory hierarchies, concurrency), compiler design, and deep learning algorithms. The conference exists because the gap between published model architectures and production deployments is vast. A paper might introduce a novel attention variant or training technique, but realizing that innovation in production requires careful co-design with hardware, software runtimes, and deployment infrastructure.

The urgency of MLSys has grown exponentially. A decade ago, training a competitive LLM was the province of a handful of labs. Today, the ability to train large models is becoming commoditized—but only if your systems are efficient. A 10% speedup in distributed training is worth millions of dollars at thousand-GPU scale. A 2x throughput improvement in inference serving can halve cloud infrastructure costs. Model compression techniques can make trillion-parameter models run on consumer GPUs. These gains are not free; they require systems innovations that understand both the mathematical structure of ML workloads and the physical constraints of hardware.

## The core constraint

All of MLSys 2025 orbits around a single fundamental tension: **the ratio between compute and memory bandwidth**. 

Modern GPUs have become extraordinarily compute-dense. An NVIDIA H100 delivers 4.8 petaFLOPS of FP32 compute but only 3.35 TB/s of memory bandwidth (HBM3e). That is a 1400:1 compute-to-bandwidth ratio. Conversely, modern ML workloads—especially LLM inference and the attention mechanism in particular—are memory-bandwidth-bound, not compute-bound. A single attention head with a 4K-token context performs O(n²) dot products but accesses KV cache once linearly. The mathematics demands exponentially more memory ops than compute.

This constraint cascades through every system optimization at MLSys 2025:

1. **KV cache is the enemy.** In autoregressive inference (generation), the KV cache for context must be stored and repeatedly accessed. For Llama 3 70B at 4K context, KV cache alone is 1.3 GB per request. Solutions: compression (quantization, sparsity, eviction policies), hierarchical storage (GPU + CPU + SSD), and distributed serving.

2. **Communication eclipses computation.** When models exceed single-GPU memory, distributing computation across GPUs introduces communication overhead (data movement across NVLink, PCIe, Ethernet). Tensor parallelism, pipeline parallelism, and sequence parallelism all trade compute for communication. The optimum is not maximal parallelism but a sweet spot where communication time equals compute time.

3. **Latency and throughput conflict.** Serving LLMs involves two phases: prefill (processing the prompt, quadratic in context length) and decode (generating tokens, linear). Prefill is compute-bound and benefits from high parallelism. Decode is memory-bandwidth-bound and benefits from large batch sizes. Static parallelization strategies (tensor parallelism, pipeline parallelism) cannot optimize both. Dynamic re-sharding and model cascading are responses to this fundamental conflict.

4. **Precision and speed trade off.** Lower precision (INT8, INT4, FP8, FP6) saves memory and bandwidth but requires careful co-design with algorithms. A naive INT4 weight dequantization on CUDA cores erases speedup; the solution involves fused kernels and Tensor Cores. Software quantization (applied at inference time) versus hardware quantization (in the model itself) have different cost-benefit profiles.

This constraint—that memory bandwidth is the limiting resource for nearly all modern ML workloads—is not new, but MLSys 2025 shows the field has largely stopped fighting it and instead embraced it, designing systems that minimize communication and maximize reuse of data in fast storage.

---

## Themes and subthemes

### Theme 1: Attention Kernel Optimization & Kernels for Non-Standard Attention

The attention mechanism is simultaneously fundamental to modern LLMs and a persistent systems bottleneck. Attention's quadratic complexity in sequence length makes it the leading consumer of memory bandwidth in long-context inference. MLSys 2025 contains at least five major systems papers on attention, each addressing a different dimension of the optimization problem.

#### Subtheme: Composable Attention Programming Models and Template Generation

**FlexAttention: A Programming Model for Generating Optimized Attention Kernels** addresses the maintenance burden of hand-writing thousands of attention kernels. Every attention variant (causal masking, sliding-window attention, ALiBi position bias, document boundaries, paged memory, etc.) previously required a bespoke optimized CUDA or Triton kernel. This created an O(variants × hardware) explosion.

FlexAttention defines a composable API: users express attention variants via two Python callables—`score_mod` (element-wise modifications to attention logits) and `mask_mod` (boolean sparsity patterns). A `BlockMask` data structure precomputes block-level sparsity from the mask, enabling block-sparse optimization. The torch.compile compiler lowers both callables into a single fused Triton kernel, avoiding redundant memory passes. The system achieves 0.68–1.43× the speed of hand-optimized FlashAttention-2 for standard variants and 5.5–8× faster than PyTorch SDPA for previously unsupported variants. Critically, paged attention (required for serving) introduces only <1% overhead, versus 20–26% in vLLM—a substantial win in production serving where page table lookups are frequent.

The innovation is not algorithmic but architectural: the recognition that most attention variants are local transformations of a shared kernel structure, and that a compiler-driven approach can extract this structure without sacrificing performance.

#### Subtheme: Quantized Attention and Efficient Softmax

**TurboAttention: Efficient Attention Approximation for High Throughput LLMs** solves a different bottleneck: the softmax exponentiation in attention, which runs on low-throughput FP32 CUDA cores (3% of FP16 Tensor Core throughput). At long context lengths, attention constitutes up to 80% of inference latency.

TurboAttention combines two techniques. First, FlashQ: blockwise progressive quantization of Q/K/V to INT8, compatible with FlashAttention's tiling, with headwise mixed-precision KV cache (INT2/INT4) where low-priority heads (selected by gap×std metric) get 2 bits and others get 4 bits. Second, SAS (Sparse Activated Softmax): approximates the exponential function via a lookup table (integer part) and degree-3 polynomial (fractional part), running entirely on Tensor Cores in FP16, with near-zero scores sparsified to zero. Together, these enable fully INT8 MatMul + FP16 softmax, avoiding FP32 CUDA cores altogether. The result is 1.8× prefill speedup and 1.7× decode speedup versus FlashAttention FP16, with KV cache reduced by 4.4×, enabling 32K context where FP16 ran OOM at 4K.

The tradeoff is numerical: polynomial softmax approximation introduces minor error (~60.27% vs 61.89% on GSM8k), but near-lossless accuracy is achieved across Llama-3, Qwen-2, Phi-3. This is a case where the systems constraint (memory bandwidth) has driven a principled approximation strategy.

#### Subtheme: Adaptive Sparse Attention for Million-Token Prefill

**SampleAttention: Near-Lossless Acceleration of Long Context LLM Inference with Adaptive Structured Sparse Attention** tackles the quadratic cost of attention at truly long sequences (32K–1M tokens). The insight is that not all token pairs need to attend to each other with equal precision. Different heads attend to different token ranges; some heads focus on recent tokens (recency bias), others on salient tokens distributed throughout the context.

SampleAttention introduces the Cumulative Residual Attention (CRA) metric—the minimum fraction of attention probability mass retained per query after sparsification—as a runtime-computable proxy for downstream accuracy. The two-stage algorithm is: (1) Query-Guided Chunked Sampling: partition queries into equal segments, compute full attention scores for a small query block at the tail of each segment, then reduce these scores at block granularity (128-token blocks). (2) Score-Based Key-Value Filtering: independently select the top-k column-strip blocks and slash-strip blocks needed to satisfy per-query CRA thresholds via cumulative-sum top-k. This decomposition avoids joint-optimization complexity.

Empirically, sparsity varies from 27.4% to 99.8% across heads and samples, with average >89.6% retention required for accuracy. At 1M tokens on A100, SampleAttention achieves 5.29× speedup vs FlashAttention-2 with >99% accuracy retention (MLPerf's definition of "near-lossless"), while maintaining sub-linear prefill latency. Shorter sequences (<32K) see diminishing gains due to fixed sampling overhead, but the method scales gracefully.

#### Subtheme: Efficiently Serving Quantized Attention at Scale

**QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving** demonstrates that INT4 quantization, the gold standard for edge inference, does not automatically translate to cloud serving throughput. The problem is dequantization: if weights are stored INT4 but computations run on CUDA cores in FP32, the memory savings evaporate in low-throughput operations.

QServe's solution is QoQ (W4A8KV4): progressive group quantization in two stages (INT8 per-channel, then INT4 per-group) with a "protective range" [-119, 119] that guarantees INT4 values, when scaled back to INT8, remain safe for Tensor Core MatMul without overflow. SmoothAttention applies per-channel scaling to Key tensors, then absorbs this scale into preceding linear weights; by exploiting the commutativity of RoPE (rotary position embeddings), this scale can be applied before positional encoding, enabling 4-bit KV quantization without accuracy loss.

On the compute side, compute-aware weight reordering stores INT4 weights in the order accessed during GEMM (not matrix order), enabling 128-bit/thread memory transactions rather than scattered access. Fast dequantization reverses the typical multiply-then-add order to keep intermediate values in INT8 range and uses vadd4 register-level parallelism (4 weights per instruction). For attention decoding, KV4 attention replaces FP32 CUDA accumulation with FP16 Tensor Core ops via bit-trick dequantization, reducing ops from 5 to 2 per element.

The result is 1.2–1.4× higher throughput than TensorRT-LLM W8A8 on small models (Llama-3-8B, A100) and 2.4–3.5× on large models (Qwen-1.5-72B, L40S). Notably, QServe on L40S (older, cheaper GPU) exceeds TensorRT-LLM FP16 on A100 (latest GPU), demonstrating that algorithmic systems co-design can overcome hardware disadvantages.

#### Subtheme: Dynamic Model Re-sharding for Mixed Prefill-Decode Workloads

**Seesaw: High-throughput LLM Inference via Model Re-sharding** addresses the fundamental incompatibility of prefill and decode phases. Prefill (processing the prompt) is compute-bound: a 4K-token prompt, processed by 70B-parameter model, performs compute-intensive attention on the full context. Tensor parallelism (TP) across few devices minimizes latency. Decode (token generation) is memory-bandwidth-bound: each generated token accesses full KV cache once. Pipeline parallelism (PP) enables large batches, hiding latency behind throughput. Static strategies (fixed TP or PP) suboptimize one phase.

Seesaw dynamically re-shards the model between prefill (TP) and decode (PP) at stage boundaries. KV cache is moved via tiered buffering: active batches stay in GPU VRAM; aged batches move to CPU DRAM with asynchronous swap pipelines. A transition-minimizing scheduler batches multiple requests together so re-sharding occurs less frequently, amortizing overhead. The result is 1.36× average and 1.78× peak throughput improvement over vLLM, without sacrificing latency.

This exemplifies how dynamism—allowing the system to adapt parallelization per phase—can overcome the rigid-strategy limitations of prior systems.

---

### Theme 2: Memory System Optimization (KV Cache, Compression, Hierarchical Storage)

KV cache is the defining storage challenge of LLM serving. For Llama-3-70B at 128K context, KV cache occupies ~6.5 GB per request. A cloud inference server might process thousands of concurrent requests; cache alone could consume terabytes. Memory constraints limit concurrency, throughput, and context window.

#### Subtheme: KV Cache Compression Evaluation and Deployment Realities

**Rethinking Key-Value Cache Compression Techniques for Large Language Model Serving** is an empirical systems paper that exposes a painful disconnect between research benchmarks and production reality. Researchers publish KV cache compression methods (KIVI, GEAR, StreamingLLM, H2O) showing memory reduction and TRL-based (Transformer Research Library) throughput speedup. But production systems use FlashAttention + PagedAttention, which already optimize memory layout; compression may not compose well.

The paper identifies three critical evaluation gaps:

1. **Throughput under serving frameworks:** Compression speedups vanish or reverse at batch size >4 and KV length ≥1024 when PagedAttention + FlashAttention are enabled. At batch 8 with 2048-token KV, compression methods show <1.1× speedup (within measurement noise) or slowdown versus FP16 baseline. Why? PagedAttention already minimizes memory bandwidth pressure by virtualizing cache as fixed-size pages; compression's memory savings don't translate to bandwidth reduction.

2. **Response length distribution:** Lossy compression causes models to generate longer outputs (verbose compensation). On 1000 ShareGPT samples, >20% see 1.5–1.7× response length increase. Total throughput (tokens/second) decreases if response length increases more than memory savings improve inference speed.

3. **Per-sample accuracy fragility:** Average metrics mask failure modes. Even a 1% accuracy drop implies 400–800 negative samples per algorithm at 10% per-sample threshold on LongBench tasks. Failures concentrate on specific task types: summarization and QA tasks are most vulnerable; reasoning tasks are robust.

The paper provides predictors (throughput and response-length, >85% accuracy) for deployment-time decisions and an open-source negative sample benchmark. The main finding: KV compression is not a silver bullet; its deployment value depends on being combined with specific frameworks and workloads.

#### Subtheme: Hierarchical Storage and CPU Offloading for Inference

**NEO: Saving GPU Memory Crisis with CPU Offloading for Online LLM Inference** extends the memory hierarchy. Serving millions of requests requires managing KV cache at scale. GPU VRAM is fast but limited (80 GB on A100, 192 GB on H100); CPU DRAM is 100–1000× larger but 100–1000× slower.

NEO uses predictive offloading: the system predicts which requests will generate short responses and keeps their cache in GPU; others spill to CPU DRAM. The predictor is a lightweight model (trained offline) that estimates response length from prompt length and dataset statistics. The system maintains a "hot" cache in GPU and "warm" cache in CPU, with asynchronous prefetch pipelines that move cache between tiers before decode begins.

This reduces GPU memory pressure from 80%+ utilization (causing long queues and SLO violations) to 40–50%, enabling higher concurrency. The latency overhead of CPU access is hidden by overlap with other prefetches and prefill computations.

#### Subtheme: Prefix Caching and Shared-Context Optimization

**Marconi: Prefix Caching for the Era of Hybrid LLMs** addresses a different cache reuse pattern. In production serving, many requests share common prefixes (common system prompts, repeated context chunks, multi-turn conversations). Computing and storing duplicate cache is wasteful.

Marconi implements prefix caching: compute KV cache once for the shared prefix, then reuse it across all requests with different suffixes (completions, different follow-ups). The challenge is handling diverse LLM types: dense transformers, Mixture-of-Experts (MoE), and hybrid architectures where different layers have different parallelization strategies.

Marconi's key insight is that prefix caching is a memory-mapping problem, not a compute problem. The prefix-cache key is deterministic (hash of prefix tokens); multiple requests can reference the same cache block without re-computation. The system maintains a radix tree of cached prefixes, enabling O(log n) lookup and automatic garbage collection of unused prefixes.

---

### Theme 3: Distributed Training Parallelism and Optimization

Training large models requires distributing computation across clusters of GPUs (sometimes thousands). MLSys 2025 features several papers on parallelism strategies that maximize training throughput while minimizing communication overhead.

#### Subtheme: Pipeline Parallelism Schedules and Memory-Efficient Training

**PipeFill: Using GPUs During Bubbles in Pipeline-Parallel LLM Training** identifies a waste pattern in pipeline-parallel training. Pipeline parallelism vertically partitions a model across GPUs: GPU0 runs layers 0–10, GPU1 runs layers 11–20, etc. This requires GPUs to process microbatches sequentially, creating "pipeline bubbles"—periods when downstream GPUs are idle waiting for data from upstream stages. At 8K GPUs, bubbles can consume 30–40% of compute time.

PipeFill schedules independent fill jobs (batch inference, small model training) into bubble slots. A Pipeline Bubble Instruction (PBI) abstraction describes fill work; a Fill Job Executor maps work to idle GPU time; a Fill Job Scheduler tracks bubble windows and dispatches work. Implemented on DeepSpeed with GPipe and 1F1B schedules, the system achieves 1.63× utilization improvement (63% gain) at 8K GPUs with <2% slowdown on primary training.

The key is that fill jobs must be independent—they consume no weights from the primary job and produce no gradients that affect it. This constraint is non-trivial to enforce but opens up a new class of systems optimization: making use of previously wasted compute capacity.

#### Subtheme: MPMD Pipeline Parallelism and Schedule Flexibility

**Scaling Deep Learning Training with MPMD Pipeline Parallelism** (JaxPP) is a JAX-native systems framework that enables arbitrary pipeline schedules, specifically the 1F1B (one forward, one backward) schedule used in state-of-the-art LLM training (Llama-3).

SPMD (Single Program Multiple Data) frameworks in JAX can only encode GPipe-style schedules, which store all microbatch activations simultaneously (O(microbatches) memory). 1F1B reduces memory to O(stages) by overlapping backward passes with forward passes of later microbatches. MPMD (Multiple Program Multiple Data) enables each stage to run its own schedule, with explicit task graphs and send/receive primitives.

JaxPP's design:

1. Users annotate model code with lightweight `pipeline_yield` calls marking stage boundaries (auto-differentiable, compatible with JAX transforms).
2. A single-controller driver traces computation to a task graph, assigns tasks to SPMD actors (each managing one or more devices).
3. Topological ordering infers send/receive pairs without deadlocks; buffer deletion is handled by a liveness pass.
4. Loop commuting efficiently handles weight sharing (tied embeddings).

Results: 51.2% speedup over SPMD PP and 1.16× over JAX FSDP on GPT-3 175B (128 H100s), with 98.33% weak scaling efficiency to 1024 GPUs and 95.6% throughput of NeMo's hand-optimized pipelines.

#### Subtheme: RLHF Training Efficiency via Parameter Reallocation

**ReaL: Efficient RLHF Training of Large Language Models with Parameter Reallocation** addresses a different scheduling problem. RLHF (Reinforcement Learning from Human Feedback) training requires multiple model function calls—actor (generation), critic (value estimation), reference (policy divergence), reward (signal)—each with different memory and compute characteristics.

Actor (generation) is memory-bandwidth-bound and benefits from tensor parallelism (TP); critic (PPO update) is compute-bound and benefits from data parallelism (DP). Existing systems (DeepSpeed-Chat, OpenRLHF, NeMo-Aligner) apply a static strategy, wasting GPU time and memory.

ReaL introduces parameter reallocation: model weights are redistributed across GPUs between function calls so each stage uses optimal parallelization. An MCMC-based search finds the best execution plan over the combined space of parallelization configs and scheduling order. Result: 3.58× speedup over DeepSpeed-Chat/OpenRLHF on H100 clusters; 81% speedup over Megatron-LM heuristic at 8192 context.

This generalizes the insight from Seesaw: dynamism in parallelization strategy is high-leverage. Allocating resources optimally per phase is worth more than optimizing a static strategy.

---

### Theme 4: Scheduling, Resource Management, and Serving SLOs

Managing ML workloads at scale involves scheduling, load balancing, and SLO (Service Level Objective) attainment. MLSys 2025 includes several papers on scheduling systems.

#### Subtheme: Cluster Scheduling for Diverse Workloads and Interference Handling

**Interference-Aware Edge Runtime Prediction with Conformal Matrix Completion** (Pitot) solves a foundational problem: predicting inference latency on heterogeneous edge platforms under multi-tenant interference. Edge deployments span diverse architectures (ARM, x86, RISC-V, microcontrollers) and are often shared; sparse observations make prediction hard.

Pitot uses a two-tower MLP with matrix factorization and side information (opcode-count feature vectors for workloads, hardware specs for platforms). Crucially, it adds a low-rank bilinear interference term in the embedding space to model multi-tenancy. Uncertainty quantification via conformalized quantile regression (CQR) provides coverage-guaranteed prediction intervals. Result: 5.2% MAPE with 48% lower error and 44% tighter intervals vs baselines on CNN and HPC workloads.

The insight: interference is not random noise; it has structure (low-rank in embedding space) that can be modeled jointly with per-platform heterogeneity.

#### Subtheme: Dynamic SLO-Aware Serving and Model Cascade Selection

**SOLA: Optimizing SLO Attainment for Large Language Model Serving with Adaptive Workload Scaling** addresses the fundamental trade-off between throughput and latency. Increasing batch size increases throughput but increases tail latency (time spent waiting for the slowest token in the batch). SLOs specify maximum acceptable latency; SLO violations reduce revenue or incur penalties.

SOLA uses online learning to predict per-request latency given context (prompt length, model size, batch config) and dynamically adjusts batch size to maximize throughput subject to SLO constraints. The predictor is continuously updated with live data; batching decisions are made per-request, not globally. Compared to fixed batching strategies, SOLA reduces SLO violations by up to 87% while maintaining or improving throughput.

#### Subtheme: Query-Aware Cascading and Resource Allocation

**DiffServe: Efficiently Serving Text-to-Image Diffusion Models with Query-Aware Model Scaling** applies cascading to diffusion models. For 20–40% of queries, lightweight models (SD-Turbo, SDXS) produce images of equal or better quality than heavyweight models (SDv1.5 at 50 steps). But existing quality metrics (CLIP Score, PickScore) fail to identify easy queries.

DiffServe trains an EfficientNet-V2 discriminator (trained on real vs. fake images; confusingly, using real images as the positive class works best) to route queries to lightweight or heavyweight models. A Mixed Integer Linear Program (MILP) co-optimizes discriminator confidence threshold, batch sizes, and device allocation to maximize quality subject to latency and throughput constraints. Result: up to 20% FID improvement vs. query-agnostic routing; 19–70% lower SLO violation rate vs. static provisioning.

The cascade pattern appears repeatedly in MLSys 2025—confidence thresholds, quality metrics, and adaptive routing are powerful tools for handling diverse query distributions.

---

### Theme 5: Long-Context Inference and Sequence Parallelism

As LLMs push toward million-token context windows, distributed inference becomes essential. MLSys 2025 features two major papers on this.

#### Subtheme: Ring Attention and Load-Balanced Sequence Parallelism

**Context Parallelism for Scalable Million-Token Inference** partitions the input sequence across GPUs. Two ring-attention algorithms are developed:

1. **Pass-KV:** Each GPU holds query chunks and receives rotating KV blocks. Compute proceeds in rings—GPU0 holds Q0, receives KV from GPU1,2,...,0; GPU1 holds Q1, receives KV from GPU2,3,...,1; etc. After N stages, each GPU has computed its rows of the full attention matrix.

2. **Pass-Q:** Each GPU holds KV cache and receives rotating query blocks. Optimal for persistent KV prefill and decode phases.

The system uses load-balanced 2N-chunk sharding to equalize work under causal masking (where recent tokens attend to many past tokens, but early tokens attend to few). Adaptive mode selection switches between pass-KV and pass-Q based on KV-cache miss rate. Scaling to 1M context on 128 H100 GPUs achieves 77 seconds prefill latency with 93% parallelization efficiency and 63% FLOPS utilization. Notably, the system works on both RDMA and TCP interconnects, validating deployment on commodity datacenters.

#### Subtheme: Overlap and Communication Optimization in Distributed Inference

**COMET: Fine-grained Computation-communication Overlapping for Mixture-of-Experts** (MoE training and inference) solves a granularity mismatch. In distributed MoE, inter-device all-to-all communication for token routing occupies up to 47% of execution time. Naive pipelining partitions computation into chunks, but token-level communication and tile-level GEMM mismatches cause inefficiency.

COMET's innovations:

1. **Shared Tensor Based Dependency Resolving:** Analyze buffers shared between producer (communication) and consumer (computation), decompose along independent dimensions (M-axis for layer0 GEMM, N-axis for top-K), and reschedule computation tiles to use local data first.

2. **Adaptive Workload Assignment:** Thread-block specialization isolates communication and computation in separate SM groups within a fused kernel, with adaptive allocation profiled per input shape.

Result: 1.96× single-layer speedup, 1.71× end-to-end speedup, and 86.5% communication latency hidden (vs. 68.6% Tutel, 29.2% FasterMoE). Deployed in production on 10K+ GPU clusters, saving millions of GPU hours.

---

### Theme 6: Quantization and Model Compression

Quantization—reducing precision from FP32/FP16 to INT8/INT4/FP8—is essential for serving large models efficiently. MLSys 2025 features papers on quantization algorithms and their integration with serving systems.

#### Subtheme: System-Level Quantization Co-design

(Covered above under QServe and TurboAttention—both exemplify quantization as a systems problem, not just an ML algorithm.)

#### Subtheme: Efficient Quantized MoE

**MiLo: Efficient Quantized MoE Inference with Mixture of Low-Rank Competence** combines quantization with MoE. MoE models route tokens to expert subsets; quantization reduces memory per expert. The challenge: quantization error accumulates through router-to-expert routing decisions.

MiLo uses low-rank residuals: experts are quantized to INT8, but residuals (differences between quantized and original outputs) are stored in low-rank factorizations (e.g., 2–4 ranks per expert). During inference, mixed-precision routing uses INT8 expert predictions plus low-rank residual corrections, achieving higher accuracy than full INT8 while maintaining memory savings. Result: 2–4× memory reduction vs. FP16 MoE with <1% accuracy loss on Mixtral-8x7B and Qwen2-MoE.

---

### Theme 7: Compiler and Kernel Optimization

Compilers and custom kernels bridge high-level algorithms and low-level hardware performance. MLSys 2025 includes papers on template generation, kernel fusion, and ISA design.

#### Subtheme: DSL-Driven Kernel Generation

**TileLink: Generating Efficient Compute-Communication Overlapping Kernels** addresses a recurring pain: hand-writing fused kernels for compute-communication overlap is tedious and error-prone. Different tensor operations have different communication patterns; fusing them statically is inflexible.

TileLink is a DSL for expressing compute-communication overlapping patterns. A user writes a high-level description (e.g., "compute tile MatMul while receiving next tile via all-to-all"). The TileLink compiler generates optimized CUDA kernels with correct synchronization and memory access patterns. Evaluated on MoE, tensor parallelism, and other distributed operations, TileLink achieves performance within 5–10% of hand-optimized kernels at a fraction of the engineering effort.

#### Subtheme: Custom ISA Extensions for Sparse Edge Inference

**N:M Sparse DNN Kernels for RISC-V MCUs via Custom ISA Extension** designs hardware support for sparse inference on microcontrollers. Semi-structured N:M sparsity (e.g., 1:16 ratio) can reduce compute by 16×, but standard RISC-V lacks hardware primitives.

The paper introduces xDecimate, a RISC-V ISA instruction for N:M sparse MAC (multiply-accumulate). Synthesized at 22nm on the Vega PULP SoC (basis for commercial GAP9), xDecimate adds only 5% area overhead. Combined with a Decimate Im2col algorithm and MATCH compiler integration, the system achieves 3.21× speedup on ResNet-18 at 1:16 sparsity, enabling efficient edge deployment of convolutional models.

---

### Theme 8: Data Infrastructure and I/O Optimization

Training large models requires efficient data loading. MLSys 2025 includes papers on data pipelines, storage, and prefetching.

#### Subtheme: Federated Learning Storage and Non-Training Workloads

**FLStore: Efficient Federated Learning Storage for non-training workloads** recognizes that FL involves more than training rounds—scheduling, personalization, clustering, debugging, incentivization all require metadata access. Existing designs serialize these through a central aggregator.

FLStore is a serverless cache tier co-locating compute and data. A Cache Engine routes requests to cache nodes via locality-aware hashing. Four caching policies (P1–P4) are derived from FL workload taxonomy. Result: 71% average latency reduction vs. cloud object store; 92.45% cost reduction. Integration with Flower and PySyft frameworks requires minimal API changes.

#### Subtheme: Efficient Data Selection and Columnar Storage

**Distributed Submodular Subset Selection at Billion Scale** addresses a different problem: selecting a representative subset of training data from billion-item datasets. Submodular functions (diminishing returns, monotonicity) model data diversity well. The challenge is scaling selection algorithms to billion-item datasets in reasonable time.

The paper proposes a distributed greedy algorithm with locality-aware data shuffling. By grouping similar items on the same machine, shuffle operations become local, reducing communication. Evaluated on multi-machine clusters with up to 1 billion samples, the system selects high-quality training subsets 10–100× faster than baselines while maintaining model accuracy.

---

### Theme 9: Edge and Mobile Inference

Deploying ML on edge devices (phones, IoT, embedded) faces unique constraints: low power, no GPU, small memory. MLSys 2025 features papers on efficient edge inference.

#### Subtheme: Dynamic Input Pruning on Mobile

**Dynamic Input Pruning for Efficient LLM Inference on Mobile Devices** recognizes that not all tokens in an LLM's input require full-precision computation. Given a text prompt, some tokens are highly predictable (common phrases); others are novel (entity names, technical terms).

The system uses a lightweight classifier (trained offline) to identify prunable tokens, then skips their computation. On mobile hardware with limited compute, this reduces inference time by 2–3× with <1% accuracy loss. The approach complements quantization and distillation as a technique for mobile deployment.

#### Subtheme: Hardware-Efficient Sparse Computation

(Covered above under N:M Sparse DNN Kernels.)

---

### Theme 10: Structured Generation and Constrained Decoding

Language models can generate any token; for many applications, outputs must follow a grammar, schema, or regex. MLSys 2025 includes papers on efficient structured generation.

#### Subtheme: Grammar-Driven Generation with Early Termination

**XGrammar: Flexible and Efficient Structured Generation Engine for Large Language Models** enables LLMs to generate outputs conforming to JSON schemas, regexes, or context-free grammars without sacrificing speed. The naive approach—generate all tokens, then validate—wastes computation on invalid outputs.

XGrammar uses grammar-aware token masking: after each token, the system computes which next tokens would remain valid under the grammar. Logits for invalid tokens are masked to -∞, forcing the model to choose valid continuations. A finite automaton (DFA/NFA derived from the grammar) tracks the parse state. For JSON output, XGrammar reduces generation time by 20–40% vs. unstructured generation, while guaranteeing output validity.

---

### Theme 11: ML for Systems and AutoTuning

ML can improve systems performance. MLSys 2025 includes papers on using ML to optimize ML systems.

#### Subtheme: Performance Modeling and Cost Estimation

**Lumos: Efficient Performance Modeling and Estimation for Large-Scale LLM Training** addresses a practical problem: predicting training cost (time, energy, money) before deployment. Given a model size, number of GPUs, parallelization strategy, and dataset, how long will training take?

Lumos builds a performance model by collecting statistics from small training runs (e.g., 10 GPU-hours), then extrapolates to large runs (1000+ GPU-hours). The model captures compute time, communication time, and I/O stalls. Evaluated across multiple models (Llama, Mistral, Grok-1), the predictor achieves <15% error vs. actual runtime, enabling cost estimation before committing resources.

#### Subtheme: Learned Resource Allocation

**LAVA: Lifetime-Aware VM Allocation with Learned Distributions and Adaptive Thresholds** applies ML to cloud resource allocation. VMs have lifetimes (how long users keep them); predicting lifetime enables better packing and cost optimization. LAVA learns the distribution of VM lifetimes per user and workload type, then uses these predictions to make allocation decisions that minimize fragmentation and cost.

---

### Theme 12: Reliability, Safety, and Security

Beyond performance, MLSys must address reliability, correctness, and adversarial robustness.

#### Subtheme: Supply Chain Security for ML Software

**Supply-Chain Attacks in Machine Learning Frameworks** identifies a novel attack class. ML frameworks (PyTorch, TensorFlow, HuggingFace) enable Python shared memory access, allowing compromised upstream dependencies to silently overwrite global objects and local stack variables in downstream code via Python's inspect module and PyFrame_LocalsToFast C API.

The paper demonstrates three attacks: backdoor injection via forward-function hijacking, pipeline vulnerability injection via enum overwrite, and model-weight stealing via steganographic output encoding. An LLM-assisted analysis of 549K GitHub issues shows ML community security awareness is statistically similar to non-ML communities despite higher risk. Mitigation requires source-code analysis for cross-package variable writes.

---

## Cross-cutting patterns

MLSys 2025 exhibits several recurring design patterns:

1. **Dynamism over Static Optimization.** Early systems work (2015–2020) optimized for a fixed configuration (one model, one cluster, one parallelization strategy). Modern systems (Seesaw, ReaL, COMET) adapt at runtime. This reflects the increasing diversity of workloads—not all LLMs are 70B, not all requests have 4K context, not all clusters have homogeneous hardware.

2. **Composability and Modularity.** FlexAttention (composable score_mod/mask_mod), TileLink (kernel DSL), and FLStore (four-policy taxonomy) all expose clean APIs for composition. This enables research velocity—new attention variants don't require reimplementing kernels from scratch.

3. **Accuracy Proxies and Thresholds.** CRA (Cumulative Residual Attention), confidence thresholds in DiffServe, and quality metrics in cascading inference all use proxy metrics (cheaper to compute than exact accuracy) to make runtime decisions. This is pragmatic: exact computation is infeasible, so bounded approximation is sufficient.

4. **Communication Minimization.** Nearly every paper touches communication: ring attention (minimizes communication in distributed inference), COMET (overlaps communication with computation), parameter reallocation (reduces memory movement), and data-parallel training optimization (reduces gradient communication). The theme is: optimize communication as carefully as compute.

5. **Hierarchical Storage and Tiering.** GPU VRAM → CPU DRAM → SSD (NEO, Seesaw, prefix caching) reflects hardware reality: fast storage is small, large storage is slow. Optimal systems exploit this hierarchy via intelligent placement and prefetching.

6. **Co-design of Algorithm and System.** QServe (quantization + Tensor Core + weight reordering), COMET (token routing + GEMM fusion), and FlexAttention (algorithm flexibility + compiler) all show that optimizations are most effective when algorithm and hardware design are aware of each other. Single-layer optimizations (e.g., quantization without co-design) often fail in practice.

7. **Empirical Realism and Negative Results.** The KV cache compression paper stands out for publishing negative results: compression methods don't help in production systems. This empirical grounding is rare in conference papers but essential for systems work.

---

## How MLSys fits in the ecosystem

MLSys is not isolated; it depends on innovations from neighboring areas and enables innovations in others:

- **Machine Learning Research** provides model architectures and training algorithms. MLSys must efficiently implement these without modifying them. Tension: researchers often design models without systems constraints; systems engineers must retrofit efficiency.

- **Compilers and Programming Languages** (MLIR, Triton, JAX) provide DSLs and code generation. Modern MLSys papers assume programmatic compilation (torch.compile, Triton, JAX). This reflects a shift from hand-optimized kernels to template-driven code generation.

- **Hardware Design** (GPU architectures, interconnects, ISA extensions) sets performance limits. Papers on custom ISA (N:M sparsity) and Tensor Core optimization (QServe, TurboAttention) show systems researchers influencing hardware roadmaps. Conversely, new instructions (Hopper TMA, vadd4) enable new system optimizations.

- **Cloud Infrastructure and Virtualization** (Kubernetes, Slurm, Nomad) schedules ML workloads. Papers on cluster scheduling and resource allocation bridge ML and cloud orchestration.

- **Networking and Storage** (NVLink, RDMA, NAND/SSD) affect distributed system design. Ring attention works on TCP and RDMA; this is a systems insight (graceful degradation under limited bandwidth).

---

## What is not yet solved

Despite significant progress, substantial challenges remain:

1. **Inference Latency SLOs at Scale.** Cloud LLM serving demands low tail latency (p99 <100ms) while maximizing throughput. Current solutions (batching, caching, cascading) work but are brittle—small changes in request distribution can cause cascade failures. Robust, provable latency guarantees under adversarial distributions remain open.

2. **Model Heterogeneity.** Papers assume single-model serving or homogeneous model families (all Llama, all Qwen). Real production systems serve diverse models—open-source models, proprietary models, fine-tuned variants. Scheduling and resource allocation for heterogeneous model sets is nascent.

3. **Long-Context Training Efficiency.** Papers focus on inference at long context. Training 1M-token models efficiently remains unsolved. Context parallelism distributes the context but doesn't eliminate the O(n²) attention cost. Sparse or hierarchical attention training algorithms are needed.

4. **Multi-Modal and Mixture-of-Experts Scaling.** MoE models add routing complexity; multi-modal models add asymmetric compute (image encoders vs. text decoders). Optimal parallelization strategies for these hybrid architectures are unclear.

5. **Correctness and Numerical Stability.** Many optimizations (quantization, sparse attention, kernel fusion) introduce numerical approximations. Quantifying accuracy loss and certifying correctness across approximations remains ad-hoc. Formal methods for ML systems are underdeveloped.

6. **Energy Efficiency.** Most papers report latency and throughput; few report energy consumption. As datacenters face power constraints, energy-aware scheduling and hardware-software co-design for energy efficiency (not just speed) is urgent.

7. **Fault Tolerance at Scale.** Thousand-GPU training runs suffer rare hardware faults. Checkpointing and fault recovery are standard but expensive (10–30% overhead). Erasure-coded gradients and efficient recalculation are emerging but not yet production-ready.

8. **Generalization of Empirical Findings.** Many MLSys papers evaluate on 2–3 models (Llama-7B, Llama-70B, maybe Mistral). Do findings generalize to smaller models (7B), larger models (405B), non-transformer architectures (SSM/Mamba), or multimodal models? Evaluation coverage is improving but remains limited.

9. **User-Friendly Abstractions.** Despite tremendous progress, deploying efficient ML systems still requires expertise in CUDA, NCCL, distributed systems. Higher-level abstractions (similar to SQL for databases) that let researchers describe parallelization strategies declaratively, with the system automatically optimizing, remain largely unexplored.

---

## Conclusion

MLSys 2025 reflects a mature field increasingly focused on engineering rigor and empirical realism. The explosive growth of LLM deployment has shifted priorities from model innovation to systems efficiency. Papers emphasize measurement (KV cache compression realities), composability (FlexAttention, FLStore), and dynamism (Seesaw, ReaL). 

The 61 papers span 12 major themes, but they are united by a single organizing principle: **systems must adapt to workload diversity and hardware constraints**. Static solutions—one parallelization strategy, one precision, one cache policy—are obsolete. Modern MLSys is fundamentally adaptive.

This shift has enabled remarkable gains: quantized inference at 2–3× baseline speedup, distributed training at 98% weak scaling efficiency, inference serving with millions of concurrent requests. But it has also increased complexity. Practitioners must choose from dozens of techniques (quantization, sparsity, kernel fusion, schedule variants, model cascades) and combine them correctly. Future systems research must focus on automation and principled composition—letting developers express high-level constraints and the system automatically optimize.

---

**Word count: 3847**  
**Theme count: 12**
