# MLSYS 2025 — Cross-Corpus Theme Taxonomy

Scope: 61 per-paper records, all `confidence: high` (full-text extractions). This file
clusters the granular `primary_theme` / `technique_category` / `tags` fields from the
deterministic digest into coherent research themes, grounds each in specific papers, and
extracts the headline metric patterns and their baselines.

Nine themes emerged. Several papers legitimately span two themes (e.g. quantized attention,
sparse long-context serving); each is filed under its dominant mechanism and cross-referenced.

---

## Theme 1 — Attention kernels & KV-cache-layout engines

**Shared problem / mechanism.** Attention is the dominant inference bottleneck, and every
attention *variant* (GQA, MLA, sliding-window, ALiBi, paged, tree/prefix-shared) plus every
KV-cache *layout* (ragged, paged, radix-tree) historically demanded a bespoke hand-written
CUDA/Triton kernel. The recurring mechanism is a **unifying abstraction + code
generation/scheduling**: reduce the O(variants × hardware) surface to one templated,
load-balanced kernel path, and restructure work so decode-phase GEMV becomes batched GEMM
with near-100% SM occupancy.

Member papers:
- **mlsys-2025-000 FlashInfer** — Block-Sparse-Row unifies paged/ragged/tree KV layouts; JIT template compiler + CUDAGraph-compatible load-balanced scheduler.
- **mlsys-2025-015 FlexAttention** — `score_mod`/`mask_mod` + BlockMask programming model lowered to Triton via `torch.compile`.
- **mlsys-2025-034 FastTree** — greedy binary edge-assignment on the radix tree converts per-query GEMV into shared-prefix GEMM.
- **mlsys-2025-037 LeanAttention** — Stream-K decomposition exploiting softmax-rescale associativity for full decode-phase SM occupancy.
- **mlsys-2025-038 MAS-Attention** — edge NPU: semi-synchronous MAC/VEC stream pipelining of tiled MatMul + softmax.

Headline metrics: FlashInfer 29–69% inter-token-latency reduction vs Triton/compiler
backends; FlexAttention <1% paged-attention overhead vs 20–26% in vLLM, 0.68–1.43× vs
FlashAttention-2 (up to 8× on unsupported variants); FastTree 2.2× system throughput over
SGLang+FlashInfer (5.1× kernel vs FlashAttention); LeanAttention avg 1.73×/1.52× over
FlashDecoding on A100/H100 (up to 2.53× at 64k); MAS-Attention up to 2.75× (sim) / 1.76×
(real Huawei DaVinci NPU) over FLAT with ~54% energy savings. **Baselines: FlashAttention-2,
FlashDecoding, FlashInfer, vLLM/SGLang.**

## Theme 2 — Quantization & low-precision serving

**Shared problem / mechanism.** INT4-weight methods tuned for single-batch/edge do not
translate into cloud-serving throughput because dequant overhead on CUDA cores erases
bandwidth savings at large batch. The recurring mechanism is **precision co-design with the
Tensor-Core datapath**: progressive/grouped quantization with protective numeric ranges,
outlier absorption, and fast bit-manipulation dequant so both GEMM and (sometimes) softmax
run on Tensor Cores rather than FP32 CUDA cores.

Member papers:
- **mlsys-2025-003 QServe** — W4A8KV4 (QoQ): progressive group quant with protective range, SmoothAttention via RoPE commutativity, compute-aware weight reordering.
- **mlsys-2025-021 MiLo** — INT3 MoE with mixture of low-rank compensators; first W3A16 Tensor-Core kernel showing speedup at batch > 1.
- **mlsys-2025-025 TurboAttention** — fully quantized attention: INT8 MatMul + LUT/polynomial softmax on Tensor Cores (also Theme 1).
- **mlsys-2025-007 (KV-cache compression study)** — critical evaluation: compression speedups vanish/turn negative under PagedAttention+FlashAttention at batch > 4 (also Theme 6).

Headline metrics: QServe 1.2–1.4× (Llama-3-8B) and 2.4–3.5× (Qwen1.5-72B) throughput vs
TensorRT-LLM, with L40S beating A100-FP16; MiLo 1.2× over MARLIN for Mixtral-8×7B, +17%
Wikitext2 PPL over GPTQ; TurboAttention up to 1.8× prefill / 1.7× decode and 2.37× max
throughput vs FlashAttention-FP16, KV cache −4.4×. **Baselines: TensorRT-LLM, MARLIN, GPTQ,
FlashAttention-FP16.**

## Theme 3 — Sparsity: structured/unstructured, N:M, and MoE

**Shared problem / mechanism.** Sparse compute is either unexploitable on the target hardware
(RIS-V MCUs, structured-sparse Tensor Cores) or unstructured/dynamic and thus irregular. The
recurring mechanism is **making sparsity hardware-legible**: custom ISA primitives, tensor
decomposition into supported N:M patterns, input-magnitude pruning of whole weight columns,
or block-level structured sparse masks.

Member papers:
- **mlsys-2025-014 N:M Sparse RISC-V** — `xDecimate` custom ISA instruction (N:M select + MAC) + Decimate-Im2col; 22nm PULP SoC.
- **mlsys-2025-022 TASD** — decompose any unstructured sparse tensor into a series of N:M tensors to run on structured-sparse accelerators without fine-tuning.
- **mlsys-2025-017 Dynamic Input Pruning** — predictor-free top-K input-magnitude pruning of all three SwiGLU MLP matrices on mobile (also Theme 5).
- **mlsys-2025-021 MiLo** — INT3 *MoE* sparsity (also Theme 2).
- MoE routing/overlap papers **055 COMET** and **002 TileLink** are filed under Theme 7 (communication).

Headline metrics: xDecimate 3.21× (ResNet-18) / 1.81× (ViT) at 1:16 vs dense, 5% area
overhead; TASD 39% speedup on RTX 3080 2:4 Tensor Cores with EDP −83%/−74% (dense/sparse),
99% quality retained; DIP 40% throughput + 46% DRAM reduction on Apple-A18 sim with <0.1 PPL
increase. **Baselines: dense kernels, VEGETA/STC accelerators.**

## Theme 4 — Parallelism & distributed-training schedules

**Shared problem / mechanism.** A single static parallelization strategy underutilizes GPUs
because different phases/functions have different compute-memory profiles, and pipeline
bubbles, vocabulary-layer imbalance, and heterogeneous stages waste capacity. The recurring
mechanism is **dynamic or finer-grained plan reconfiguration**: reallocate parameters between
RLHF stages, fill bubbles with secondary work, partition vocabulary evenly, or express
arbitrary MPMD pipeline schedules.

Member papers:
- **mlsys-2025-030 ReaL** — parameter reallocation across RLHF actor/critic/reference/reward stages; MCMC plan search.
- **mlsys-2025-010 PipeFill** — schedules independent fill jobs into pipeline bubbles via a Pipeline-Bubble-Instruction abstraction.
- **mlsys-2025-052 Vocabulary Parallelism** — partitions embedding/output layers across all pipeline stages; online softmax cuts comm barriers 3→1.
- **mlsys-2025-045 JaxPP** — JAX-native MPMD pipeline runtime supporting 1F1B / Interleaved-1F1B via `pipeline_yield`.
- **mlsys-2025-026 Lumos** — trace-driven performance model capturing inter-stream compute-comm dependencies (3.3% replay error) for what-if analysis.

Headline metrics: ReaL 3.58× over DeepSpeed-Chat/OpenRLHF/veRL and 81% over Megatron heuristic
(128 H100); PipeFill 1.63× GPU-utilization at 8k GPUs with <2% primary-job slowdown; Vocabulary
Parallelism +5–51% throughput; Lumos 3.3% avg replay error vs 14% for dPRO. **Baselines:
Megatron-LM, DeepSpeed/DeepSpeed-Chat, NeMo, FSDP, dPRO.**

## Theme 5 — Memory hierarchy, offloading & near-data execution

**Shared problem / mechanism.** GPU HBM capacity caps batch size and sequence length; the
common mechanism is **overlapping a slower tier (CPU DRAM, PCIe, SSD, Flash) behind GPU
compute** via asymmetric pipelining, double-buffering, analytical per-layer policy selection,
or memory-efficient optimizer state.

Member papers:
- **mlsys-2025-024 NEO** — asymmetric GPU-CPU sub-batch pipelining; CPU attention (ISPC/SPMD) hidden behind GPU linear stage.
- **mlsys-2025-033 FlexInfer** — analytical per-layer policy (CPU-only / GPU-offload / SplitGen) for CPU-GPU DNN inference.
- **mlsys-2025-051 FPDT** — double-buffered PCIe prefetch enabling 2M-token training on 4 GPUs at >55% MFU.
- **mlsys-2025-059 APOLLO** — random-projection low-rank optimizer giving SGD-level memory at AdamW performance (JL-lemma proof).
- **mlsys-2025-043 HyC-LoRA** — hybrid activation compression (outlier-aware INT2 + LoRA-reorder recompute) for LoRA fine-tuning.
- **mlsys-2025-017 DIP** — mobile SwiGLU DRAM reduction (also Theme 3); **mlsys-2025-031 MEADOW** — sub-10W FPGA TPHS dataflow + weight packing (also Theme 8).

Headline metrics: NEO up to 7.5× throughput on T4 (14–26% on H100/A10G) vs GPU-only;
FlexInfer 75–76% latency reduction vs FlexGen (PCIe was 96–98% of FlexGen time); FPDT 16×
longer sequences at >55% MFU; APOLLO ~3× throughput on LLaMA-7B via 4× batch, optimizer memory
1.6 GB vs 28 GB AdamW; HyC-LoRA near-2-bit activations (activations were 69.7% of Llama-2-7B
memory). **Baselines: FlexGen, DeepSpeed-Ulysses, AdamW/GaLore, vLLM.**

## Theme 6 — LLM serving: SLO scheduling, prefill/decode disaggregation & caching

**Shared problem / mechanism.** Production serving must hit TTFT/TPOT SLOs under fluctuating,
heterogeneous demand where prefill and decode have opposite resource profiles. The recurring
mechanism is **phase-aware scheduling and prefix reuse**: formalize scheduling as constrained
optimization, disaggregate prefill/decode onto different GPUs/parallelism, re-shard mid-
inference, and maximize KV-cache prefix hits — plus honest evaluation of what actually holds
up in production.

Member papers:
- **mlsys-2025-018 SOLA** — per-iteration constrained optimization over exec order / batch / tokens; state-aware TTFT↔TPOT switching (on vLLM).
- **mlsys-2025-023 ThunderServe** — prefill/decode phase-splitting across heterogeneous cloud GPUs (tabu search + LP routing, 4-bit KV transfer).
- **mlsys-2025-040 Seesaw** — dynamic mid-inference re-shard between TP (prefill) and PP (decode) with tiered KV buffering.
- **mlsys-2025-004 Marconi** — prefix caching for hybrid Attention+SSM LLMs; FLOP-aware eviction (FLOPs-saved-per-byte).
- **mlsys-2025-029 (LLM queries in relational analytics)** — row/field reordering to maximize KV prefix-hit count in batch analytics.
- **mlsys-2025-016 XGrammar** — context-independent/dependent token split precomputes >99% of grammar masks (constrained decoding).
- **mlsys-2025-007 (KV-cache compression evaluation)** — shows compression gains vanish under real serving frameworks (critical study).
- **mlsys-2025-008 DiffServe** — query-aware diffusion model cascade with MILP resource allocation (also Theme 9).
- **mlsys-2025-046 AI Metropolis** — out-of-order execution for LLM multi-agent simulation via spatiotemporal dependency graph.

Headline metrics: SOLA raises SLO attainment 45.5%→99.4% (Llama3-70B, 4×A100) at 0.4% overhead;
ThunderServe up to 2.1× throughput / 2.5× latency on heterogeneous clusters; Marconi 71.1%
lower P95 TTFT and up to 34.4× token-hit-rate vs vLLM+; relational reordering 1.5–3.4× latency
and 32% GPT-4o-mini cost savings; XGrammar up to 100× per-token / 80× end-to-end vs
vLLM+Outlines. **Baselines: vLLM (+Outlines), SGLang, TensorRT-LLM.**

## Theme 7 — Compute–communication overlap & interconnect

**Shared problem / mechanism.** Distributed training/inference spends up to ~47% of time in
collectives (all-reduce, all-to-all, all-gather) that must be hidden behind compute. The
recurring mechanism is **fine-grained fused kernels that interleave communication and compute
at tile/tensor granularity**, via tile-centric primitives, shared-tensor dependency
decomposition + SM specialization, or gradient sparsification that swaps all-gather for
all-reduce.

Member papers:
- **mlsys-2025-002 TileLink** — tile-centric primitives (notify/wait/push/pull) compiled to fused overlapping kernels via Triton+NVSHMEM.
- **mlsys-2025-055 COMET** — MoE all-to-all overlap via shared-tensor decomposition + adaptive thread-block (SM) specialization.
- **mlsys-2025-049 ScaleFusion** — intra/inter-layer pipelined all-to-all for ST-DiT video inference exploiting spatial-temporal independence.
- **mlsys-2025-057 Radius** — range-based gradient sparsity exploiting top-k index temporal stability; dense all-reduce instead of all-gather, AdamW-compatible.
- **mlsys-2025-050 Context Parallelism** — pass-KV / pass-Q ring attention with load-balanced 2N-chunk sharding (also Theme 8).

Headline metrics: TileLink 1.17–20.76× vs non-overlapping, matching FLUX with ~10× less code;
COMET 1.71× end-to-end (1.96× single MoE layer), hiding 86.5% of comm, 31.8–44.4% latency
reduction vs Megatron-cutlass/TE/FasterMoE/Tutel; ScaleFusion removes 34–44% cross-machine
comm overhead; Radius 19% training speedup, 89.7% comm reduction at d=0.4, 42.5% vs 32.8%
scaling efficiency at 128 GPUs. **Baselines: FLUX, Megatron/TE, FasterMoE, Tutel, PowerSGD,
DeepSpeed-Ulysses/RingAttention.**

## Theme 8 — Long-context inference & training (sequence/context parallelism + sparse attention)

**Shared problem / mechanism.** Prefill cost is quadratic and KV memory linear in sequence
length, breaking single-GPU limits at 64k–2M tokens. Two complementary mechanisms recur:
**adaptive/structured sparse attention** (skip unimportant KV blocks per head/input) and
**sequence/context parallelism** (shard the sequence dimension across GPUs with ring-attention
communication and CPU offload).

Member papers:
- **mlsys-2025-047 LServe** — unified static streaming-head + dynamic hierarchical page sparsity in fused kernels with W4A8KV4.
- **mlsys-2025-060 SampleAttention** — Cumulative-Residual-Attention proxy drives per-head/per-input adaptive block-sparse prefill.
- **mlsys-2025-050 Context Parallelism** — pass-KV/pass-Q ring attention for 1M-token prefill (also Theme 7).
- **mlsys-2025-051 FPDT** — fully-pipelined distributed transformer for 2M-token training (also Theme 5).
- **mlsys-2025-031 MEADOW** — sub-10W FPGA long-context dataflow (also Theme 5/9).
- Adjacent: **000 FlashInfer**, **037 LeanAttention** (long-context decode), **004 Marconi** (long-context caching).

Headline metrics: SampleAttention 5.29× TTFT vs FlashAttention2 at 1M tokens (>99% score
retained); Context Parallelism 77 s for 1M-token prefill on 128 H100, 93% parallel efficiency,
near-linear 1→128 GPU scaling; FPDT 16× longer sequences at >55% MFU; LServe multiplicative
speedup in both prefill and decode. **Baselines: FlashAttention-2, DeepSpeed-Ulysses,
RingAttention.**

## Theme 9 — Edge / on-device ML & specialized hardware

**Shared problem / mechanism.** Sub-10W SoCs, MCUs, FPGAs, and mobile NPUs are memory-
bandwidth- and SRAM-bound and cannot afford backprop-scale memory. The recurring mechanism is
**co-design at the ISA/dataflow/algorithm level** for the tight energy and memory envelope:
custom instructions, memory-aware tiling/dataflow, forward-only training, and LUT-based
inference.

Member papers:
- **mlsys-2025-014 xDecimate** — RISC-V N:M ISA extension on 22nm PULP SoC (also Theme 3).
- **mlsys-2025-031 MEADOW** — Token-Parallel Head-Sequential dataflow + weight packing on Xilinx ZCU102 FPGA, W8A8.
- **mlsys-2025-038 MAS-Attention** — MAC/VEC stream processing on Huawei DaVinci NPU (also Theme 1).
- **mlsys-2025-019 Bio-FO** — forward-only, biologically-plausible on-device training (3× memory, up to 19.8× energy reduction on Jetson Nano).
- **mlsys-2025-044 VoLUT** — offline NN-to-LUT 3D super-resolution at line-rate on commodity mobile.
- **mlsys-2025-017 DIP** — mobile SwiGLU pruning (also Theme 3/5); **mlsys-2025-041 FedProphet** — memory-efficient federated adversarial cascade training on edge.

Headline metrics: Bio-FO up to 19.8× energy reduction vs Forward-Forward (37.9 Wh vs 753.5 Wh
CIFAR-100) with 3× memory reduction; MEADOW 1.5×/2.5× decode/prefill vs GEMM baseline at
sub-10W; xDecimate 5% area overhead; VoLUT line-rate mobile SR with bandwidth reduction.
**Baselines: dense/GEMM kernels, Forward-Forward/PEPITA/DRTP, FLAT, YuZu.**

---

## Themes not about hardware/kernels (context)

Roughly a fifth of the corpus is **systems-for-ML / ML-for-systems infrastructure** rather
than accelerator/kernel work, and is not force-fit into the themes above:
- Cloud resource management & scheduling: **006 ProtoRAIL** (vCPU oversubscription), **027 LAVA**
  (VM lifetime allocation, Google Borg), **056 Rubick** (DL cluster reconfigurability), **028 Venn**
  / **001 FLStore** (federated-learning resource/storage), **048 BYOM** (SSD/HDD tiering).
- Data infrastructure: **039 AdaParse** (PDF parsing), **058 Youmu** (columnar Parquet pipeline),
  **012 submodular subset selection**, **053 PP-GNN I/O**, **009 SparseTransX** (KGE SpMM), **035 GSplit** (GNN split parallelism).
- Reliability / security / evaluation / RL: **005 supply-chain attacks**, **011 uncertainty
  disentanglement**, **013 AIOpsLab**, **054 hidden bloat / debloating**, **032 SwiftVI** (value iteration),
  **042 self-data distillation pruning**.

---

## Workloads & targets

From the normalized digest counts (61 papers):

**Hardware targets.** GPU dominates completely — 42/61 mention GPU, with NVIDIA A100 and H100
the de-facto experimental platform (A100 explicitly in 000, 003, 004, 018, 047, 049, 057, 059
and more; H100 in 026, 034, 037, 050, 051, 045). CPU appears in 18 papers, almost always as a
**secondary offload/host tier** (024, 033, 051, 058) or as the target for systems/scheduling
work (006, 027, 028). Interconnect is a first-class concern in a meaningful minority: NVLink
(6), InfiniBand (2), plus RDMA/Ethernet/PCIe in the overlap and heterogeneous-serving papers.
A small but distinct edge/specialized tail: SoC (3), edge (3), MCU (2), NPU (2), FPGA (031),
RISC-V ASIC (014), NVMe SSD (2, for data pipelines). Vendor accelerators beyond NVIDIA are
nearly absent — no TPU, one Huawei DaVinci NPU (038), no AMD GPU (one AMD EPYC CPU in 009).

**AI workloads.** The venue is overwhelmingly LLM-centric: LLM-inference (26) and LLM-training
(22) together account for the bulk, with attention (7), long-context-inference (3), and MoE (3)
as sub-specializations. Non-LLM workloads are a distinct minority: CNN (3), GNN (2), federated
learning (2), diffusion/video generation (008, 049), knowledge-graph embedding (009),
reinforcement learning (032), and multi-agent simulation (046).

## Cross-cutting observations

**What the field is collectively pushing on.**
1. **Everything is co-design.** The dominant move across Themes 1–3 and 8 is fusing an
   algorithmic idea (sparsity pattern, quantization scheme, attention variant) directly into
   the Tensor-Core/SM datapath and its scheduling, rather than treating them as separable layers.
2. **Prefill vs decode as separate regimes.** A remarkably consistent framing (003, 018, 023,
   037, 040, 047, 050, 060): the two phases have opposite compute/memory profiles and are
   optimized, disaggregated, re-sharded, or scheduled independently.
3. **Hiding a slow tier behind a fast one.** Whether it is PCIe/CPU-DRAM (024, 033, 051, 058),
   SSD (053, 058), or the network (002, 049, 055, 057), the template is double-buffered
   overlap of transfer with compute.
4. **Dynamic/adaptive over static.** Adaptive sparsity budgets (060), state-aware SLO
   scheduling (018), reconfigurable execution plans (030, 056), and lifetime reprediction
   (027) all argue explicitly against fixed heuristics.

**Recurring baselines.** vLLM (and vLLM+Outlines/vLLM+) and FlashAttention-2/FlashInfer are
the reference points for essentially all serving/attention work; TensorRT-LLM and GPTQ/MARLIN
for quantization; Megatron-LM, DeepSpeed(-Chat/-Ulysses), FSDP, and NeMo for training/
parallelism; FlexGen for offloading; FLUX/FasterMoE/Tutel for MoE communication. A vLLM +
A100/H100 + FlashAttention comparison is close to a venue-wide standard harness.

**Tensions / trade-offs.**
- *Accuracy vs efficiency* is negotiated everywhere but rarely eliminated: quantization/sparsity
  papers report "near-lossless" (025, 060) or explicit quality floors (022's 99% target),
  while 007 documents per-sample fragility that aggregate metrics hide.
- *Reported vs realized speedup.* Paper **007** is the honesty check for the whole quantization/
  compression cluster: KV-compression speedups vanish or go negative under real serving
  frameworks (PagedAttention+FlashAttention) at batch > 4 and under tensor parallelism —
  a direct caution against the single-batch benchmarks many Theme-2/3 papers rely on.
- *Generality vs peak performance.* Programming-model papers (015 FlexAttention, 002 TileLink,
  045 JaxPP) trade a little peak throughput for large code-reduction/portability wins.

**Visible gaps (what is *not* being worked on).**
- **Non-NVIDIA silicon is almost untouched:** no TPU, no AMD-GPU, essentially one edge-NPU
  and one FPGA/RISC-V result. Portability claims are made mostly against other CUDA backends.
- **Energy/PPA is rarely measured.** Only the edge papers (014, 019, 038) and TASD (022) report
  energy/EDP/area; datacenter GPU work reports speedup/throughput but almost never Joules or
  TOPS/W, despite energy being the stated motivation for many.
- **Training numerics / correctness at scale** is thin — most training papers optimize
  throughput/memory (010, 030, 045, 051, 057, 059) but few (026 Lumos is an exception)
  address convergence/accuracy verification of the optimized system.
- **MoE and hybrid/SSM architectures are early:** only 3 MoE papers (021, 055, plus 002's MoE
  overlap) and a single hybrid-Attention+SSM caching paper (004), versus the deluge of dense-
  transformer attention work.
- **End-to-end multimodal / diffusion / video** is a small frontier (008, 049, 044, 011)
  relative to text LLMs.

## Coverage & confidence

n = 61 papers. **All 61 are full-text extractions (`confidence: high`); there are no
abstract-only records** in this corpus. 51/61 report quantitative metrics; the 10 without a
clean speedup/energy number are largely the systems/evaluation/security papers (005, 011, 012,
013, 020, 027, 032, 048 and similar) whose contributions are accuracy-, benchmark-, or
production-deployment-based rather than kernel-speedup-based. The main confidence caveat is not
extraction quality but comparability: baselines, hardware (A100 vs H100 vs L40S vs edge), batch
sizes, and sequence lengths differ across papers, so the headline multipliers above are
directional within a theme, not cross-theme commensurable.
