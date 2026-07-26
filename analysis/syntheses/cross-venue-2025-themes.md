# AI Hardware 2025 — Cross-Venue Synthesis (MLSys · ISCA · MICRO · HPCA · ASPLOS)

Scope: 619 papers across five 2025 venues; 503 analyzed (120 full-text `high`, 383
abstract-only `low`); 116 title-only, not analyzed. This file is a *comparative* read of the
five per-venue digests, anchored to the nine-theme MLSys taxonomy in `mlsys-2025-themes.md`
and grounded in specific paper ids. Paper ids are `<venue>-2025-NNN`. Read the coverage
caveat (§6) before quoting any count — the architecture venues are mostly abstract-only, and
MICRO in particular is under-sampled.

---

## 1. The one-paragraph picture

The 2025 AI-hardware field is collectively **co-designing the transformer inference/training
stack against the memory wall**. The workload has converged — LLM-inference is the single most
common workload in every one of the five venues (MLSys 26, ISCA 31, MICRO 16, HPCA 29, ASPLOS
37), with attention, MoE, and long-context as its sub-specializations — but the *layer* each
venue attacks differs. MLSys optimizes the software serving/training stack on NVIDIA GPUs
(kernels, schedulers, parallelism plans, offload pipelines). The architecture venues (ISCA,
MICRO, HPCA) attack the layers MLSys treats as fixed: they build the silicon (ASIC/CIM/PIM
accelerators for attention, quantized GEMM, FHE, ZKP), redesign the memory system (DRAM
scheduling, near-data processing, cache compression, CXL), the interconnect (NoC, collectives,
multi-GPU/chiplet topologies), and they own the entire security/reliability/side-channel axis
(RowHammer, Spectre, silent-data-corruption, coherence proofs) that MLSys never touches.
ASPLOS sits in the middle — a CPU-and-compiler-heavy systems venue that bridges MLSys-style
serving with architecture-style memory/security work. The unifying mechanism everywhere is the
same one the MLSys taxonomy names: **fuse an algorithmic idea (a sparsity pattern, a
quantization scheme, an attention variant, a data layout) directly into the datapath and its
scheduling, and hide a slow tier behind a fast one.** The novelty in 2025 is that the "datapath"
is no longer just the Tensor Core — it is increasingly the DRAM bank (PIM/NMP), the SRAM array
(CIM), the NoC, and the CXL fabric.

---

## 2. Per-venue character

**MLSys — systems-for-LLMs on GPUs.** 61 papers, *all* full-text/high-confidence, 42/61 mention
GPU with A100/H100 the de-facto platform; workloads are overwhelmingly LLM-inference (26) and
LLM-training (22). MLSys is about the *software* that makes a fixed GPU serve LLMs faster:
attention/KV-cache kernel engines (`mlsys-2025-000` FlashInfer, `mlsys-2025-015`
FlexAttention), phase-aware SLO serving (`mlsys-2025-018` SOLA, `mlsys-2025-023` ThunderServe),
Tensor-Core-aware quantization (`mlsys-2025-003` QServe W4A8KV4), and distributed training
schedules (`mlsys-2025-030` ReaL RLHF reallocation, `mlsys-2025-055` COMET MoE overlap). It
essentially never touches real silicon, memory-system microarchitecture, security, or
reliability. Signature: `mlsys-2025-000`, `mlsys-2025-003`, `mlsys-2025-018`.

**ISCA — the flagship silicon-and-memory-systems venue.** 112 papers (17 high / 95 low); the
hardware-target distribution inverts MLSys: **ASIC 49, CPU 28, GPU 23, CIM 13, FPGA 10**, with
analog/photonic/PIM/chiplet/TPU all present. Workloads spread far past LLMs into HPC (28), GNN
(23), database (18), CNN/vision, and cryptography. This is where the *real accelerators* live:
compute-in-memory transformer engines (`isca-2025-098` hybrid SLC-MLC RRAM PIM, `isca-2025-126`
AIM IR-drop mitigation for SRAM PIM), LUT-based low-bit Tensor Cores (`isca-2025-079` LUT
Tensor Core, 4–6× power/area reduction), near-data/indirection accelerators (`isca-2025-055`
DX100, `isca-2025-058` NMP-PaK genome assembly), interconnect topologies (`isca-2025-027`
non-blocking network, `isca-2025-032` multi-GPU traffic shaping, `isca-2025-093`
network-on-wafer), plus a large quantum/crypto cohort (`isca-2025-025` zkSpeed, `isca-2025-077`
FT-quantum sync, `isca-2025-132` transversal atom arrays). It also carries the honest
"industrial reflection" paper `isca-2025-130` (DeepSeek-V3 hardware co-design). Signature:
`isca-2025-079`, `isca-2025-055`, `isca-2025-098`.

**MICRO — microarchitecture, memory, and security (under-sampled).** 47 papers (20 high / 27
low), and **76 further papers title-only and NOT analyzed** because IEEE withholds abstracts and
many are not on arXiv — so MICRO's picture here is the least complete of the five. What we can
see is textbook MICRO: CPU-heavy (19 CPU, 17 ASIC, 9 GPU), `memory-system` is the top technique
(25), and it owns the *microarchitectural security* corner — RowHammer revival and defenses
(`micro-2025-025` ρHammer prefetch-based hammering, plus rowhammer-defense side-channels), secure
BTB/speculation, and reverse-engineering (`micro-2025-043` dissecting NVIDIA GPU SM pipelines).
Its AI-hardware core is memory-centric: Mono3D-DRAM NMP for MoE (`micro-2025-012` Stratum),
near-core decompression for compressed LLMs (`micro-2025-035` DECA), PIM for post-transformer
LLMs, and NPU power-gating (`micro-2025-104` ReGate). Signature: `micro-2025-012`,
`micro-2025-035`, `micro-2025-025`.

**HPCA — memory-system and accelerator architecture at scale.** 119 papers (8 high / 111 low),
the most memory-dominated venue of all: `memory-system` is the top technique by a wide margin
(61), then `scheduling` (54) and `dataflow` (40). Hardware is ASIC 48 / CPU 36 / GPU 32 / CIM
13; workloads lead with HPC (40) ahead of LLM-inference (29). HPCA is where accelerators meet
DRAM physics and datacenter energy: spatial-accelerator RTL generation (`hpca-2025-002` LEGO),
VQ-LLM GPU codegen (`hpca-2025-003`), diffusion output-sparsity ASICs (`hpca-2025-035` EXION),
in-cache/near-memory compute (`hpca-2025-045` mobile in-SRAM vector ISA), on-DRAM-die RowHammer
mitigation, silent-data-corruption modeling, collective-comm fault detection for distributed
LLM training (`hpca-2025-024`), and datacenter energy management (`hpca-2025-082` DynamoLLM).
Signature: `hpca-2025-002`, `hpca-2025-035`, `hpca-2025-082`.

**ASPLOS — the CPU/compiler/systems bridge with a strong security axis.** The largest corpus
(164 papers, 14 high / 150 low) and the most CPU-centric (**CPU 81, GPU 55, ASIC 21**);
`scheduling` (81) and `compiler` (49) lead, and `security` (34) is a first-class pillar.
Workloads are the broadest of any venue: LLM-inference (37) but also database (32), HPC (28),
GNN/CNN/transformer each in the 20s. ASPLOS spans MLSys-style serving (`asplos-2025-049`
Past-Future SLA scheduler, `asplos-2025-073` network-accelerated KV paging, `asplos-2025-105`
FSMoE, `asplos-2025-133` CoServe) *and* deep architecture/systems work MLSys never does:
GPU-free PIM+CXL LLM inference (`asplos-2025-051`), provably-secure RowHammer counters
(`asplos-2025-113` MOAT), TEE/side-channel attacks (`asplos-2025-124` SMaCk, `asplos-2025-008`
PipeLLM confidential serving), formal coherence verification (`asplos-2025-134` CXL SWMR proof),
cloud oversubscription (`asplos-2025-116` Coach), and QEC decoders (`asplos-2025-148` Micro
Blossom). Signature: `asplos-2025-051`, `asplos-2025-113`, `asplos-2025-134`.

---

## 3. Shared cross-venue themes

Eight themes recur across venues. Each names the venues that carry it, the shared mechanism, and
representative ids.

### T1 — LLM/attention & KV-cache acceleration
*Venues: all five.* The single most universal theme. Mechanism: restructure attention and its
KV cache so the dominant inference bottleneck becomes hardware-legible — as fused kernels on
GPUs, or as purpose-built accelerators/memory paths elsewhere.
- MLSys (kernels/serving): `mlsys-2025-000` FlashInfer, `mlsys-2025-047` LServe.
- ISCA: `isca-2025-007` Oaken hybrid KV quantization (ASIC/NPU), `isca-2025-021` Ecco entropy-aware KV cache compression (GPU), `isca-2025-129` phase-disaggregated serving.
- MICRO: `micro-2025-012` Stratum Mono3D-DRAM for MoE serving, PIM for post-transformer LLM serving.
- HPCA: `hpca-2025-003` VQ-LLM codegen, `hpca-2025-082` DynamoLLM cluster energy.
- ASPLOS: `asplos-2025-049` Past-Future scheduler, `asplos-2025-073` network-accelerated KV paging, `asplos-2025-133` CoServe.

### T2 — Quantization & low-precision datapaths
*Venues: all five.* Mechanism: co-design precision with the compute datapath so low-bit weights/
activations/KV actually yield throughput, not just capacity. In MLSys this is a Tensor-Core
kernel; in the architecture venues it is a *new datapath* (bit-serial, LUT, RRAM, block-FP).
- MLSys: `mlsys-2025-003` QServe (W4A8KV4), `mlsys-2025-021` MiLo (INT3 MoE).
- ISCA: `isca-2025-079` LUT Tensor Core (bit-serial low-bit), `isca-2025-007` Oaken KV quant, `isca-2025-042` LightNobel adaptive activation quant.
- MICRO: `micro-2025-063`/outlier-aware MX block-FP for 4-bit LLMs (per digest), `micro-2025-035` DECA compressed-weight decompression.
- HPCA: `hpca-2025-000` mixed-datatype bit-serial weight quant accelerator, `hpca-2025-003` VQ-LLM, per-group adaptive quant.
- ASPLOS: `asplos-2025-079` MVQ masked vector quantization (systolic).

### T3 — Memory hierarchy, near-data & processing-in-memory
*Venues: all five, dominant in ISCA/MICRO/HPCA.* Mechanism in MLSys: hide a slow tier (CPU DRAM,
PCIe, SSD) behind GPU compute via double-buffered pipelines. Mechanism in the architecture
venues: **move compute into the memory** — PIM/NMP in DRAM banks, CIM in SRAM/RRAM arrays,
near-core accelerators — because HBM bandwidth, not FLOPs, is the wall.
- MLSys (offload): `mlsys-2025-024` NEO, `mlsys-2025-033` FlexInfer, `mlsys-2025-051` FPDT.
- ISCA: `isca-2025-058` NMP-PaK (genomics PIM), `isca-2025-055` DX100 indirection accelerator, `isca-2025-098`/`isca-2025-126` RRAM/SRAM PIM.
- MICRO: `micro-2025-012` Stratum in-memory tiering, `micro-2025-118` real compute-in-SRAM (GSI APU) characterization, `micro-2025-035` DECA.
- HPCA: `hpca-2025-045` mobile in-cache vector ISA, DIMM-based near-memory co-execution, `hpca-2025-080` PIM collective interconnect.
- ASPLOS: `asplos-2025-051` GPU-free CXL-scaled PIM inference, `asplos-2025-170` PUSHtap in-memory HTAP.

### T4 — Interconnect, collectives & communication overlap
*Venues: MLSys, ISCA, HPCA, ASPLOS (MICRO lightly).* Mechanism in MLSys: fuse collectives into
compute at tile granularity so all-reduce/all-to-all hide behind GEMM. Mechanism in
architecture venues: redesign the *fabric* — NoC multicast, mesh-native AllReduce, chiplet/wafer
topologies, in-network aggregation.
- MLSys: `mlsys-2025-002` TileLink, `mlsys-2025-055` COMET, `mlsys-2025-057` Radius.
- ISCA: `isca-2025-027` non-blocking topology, `isca-2025-032` multi-GPU traffic shaping, `isca-2025-048` in-network DLRM aggregation, `isca-2025-090` communication fusion, `isca-2025-093` network-on-wafer.
- HPCA: `hpca-2025-001` LLC-to-sharer multicast, `hpca-2025-058` topology-native AllReduce (2D mesh), `hpca-2025-024` collective-comm fault detection, `hpca-2025-041` RL-guided network-on-active-interposer.
- ASPLOS: `asplos-2025-105` FSMoE dual-level overlap, `asplos-2025-063` topology-aware pipeline parallelism, `asplos-2025-132` auto comm-compute overlap.

### T5 — Sparsity & MoE
*Venues: all five.* Mechanism: make dynamic/unstructured sparsity hardware-legible (N:M
patterns, block masks, output-sparsity reuse, expert routing).
- MLSys: `mlsys-2025-022` TASD (N:M decomposition), `mlsys-2025-017` DIP, `mlsys-2025-055` COMET (MoE).
- ISCA: `isca-2025-109` hierarchical SNN sparsity; MoE in `isca-2025-130` DeepSeek-V3.
- MICRO: reconfigurable sparse accelerator with distributed on-chip memory, `micro-2025-012` MoE tiering, probabilistic sparse-tensor tiling.
- HPCA: `hpca-2025-035` EXION diffusion output sparsity, `hpca-2025-023` bit-slice sparsity, output-sparsity graph conversion.
- ASPLOS: `asplos-2025-105` FSMoE, `asplos-2025-042` sparse-activation-aware MoE fault tolerance, `asplos-2025-079` MVQ pruning.

### T6 — Compilation, programming models & accelerator generation
*Venues: all five, deepest in ISCA/MICRO/ASPLOS.* Mechanism: raise a hardware-legible
abstraction and lower it — attention DSLs and tile primitives in MLSys; **RTL/accelerator
generation and retargetable compilers** in the architecture venues.
- MLSys: `mlsys-2025-015` FlexAttention, `mlsys-2025-002` TileLink, `mlsys-2025-045` JaxPP.
- ISCA: `isca-2025-014` HPVM-HDC retargetable compiler, `isca-2025-003` circuit-switched streaming ISA, `isca-2025-086` Finesse crypto co-design.
- MICRO: `micro-2025-021` LLMulator LLM cost model, `micro-2025-089` OmniSim HLS simulation.
- HPCA: `hpca-2025-002` LEGO spatial-accelerator RTL generation.
- ASPLOS: `asplos-2025-077` motif-based CGRA compiler, einsum-tree data-layout IR, differentiable e-graph extraction.

### T7 — Security, side-channels & confidentiality
*Venues: ISCA, MICRO, HPCA, ASPLOS — essentially ABSENT from MLSys.* This is the clearest
"architecture venues carry what MLSys lacks" theme. Mechanism: attack or defend the memory/
speculation/coherence substrate, and add confidential-compute paths.
- ISCA: `isca-2025-101` DREAM RowHammer mitigation, transient-execution mitigation via memory tagging, CHERI-to-accelerator capabilities, constant-time enforcement.
- MICRO: `micro-2025-025` ρHammer prefetch RowHammer, secure BTB, secure-speculation cost, CXL-TEE encryption, rowhammer-defense-induced side channels.
- HPCA: on-DRAM-die RowHammer mitigation, embedding-lookup side-channel protection, speculative MPK isolation, DPU intrusion detection.
- ASPLOS: `asplos-2025-113` MOAT provably-secure counters, `asplos-2025-124` SMaCk i-cache attack, `asplos-2025-008` PipeLLM confidential serving, SEV-SNP contention attacks, RowHammer hypervisor escape.

### T8 — Reliability, correctness & honest evaluation
*Venues: ISCA, MICRO, HPCA, ASPLOS — thin in MLSys.* Mechanism: model/detect faults (SDC,
low-voltage CIM errors, QEC), formally verify protocols, and correct evaluation methodology.
- HPCA: microarchitectural SDC modeling in x86 arithmetic units, run-time MAC-level error correction for low-voltage CIM, `hpca-2025-024` collective-comm fault detection, **statistical methodology for reporting aggregate speedup**.
- ASPLOS: `asplos-2025-134` CXL coherence formal proof (Isabelle), production-fleet SDC detection, `asplos-2025-042` MoE fault tolerance, `asplos-2025-148` QEC decoder, large-hardware formal-verification invariant learning.
- ISCA/MICRO: FT-quantum synchronization (`isca-2025-077`), leakage speculation for QEC, memory-integrity protection.
- MLSys counterpart is limited to `mlsys-2025-007` (the KV-compression honesty check) and `mlsys-2025-011` uncertainty — no silicon-fault or protocol-verification work.

### T9 — Non-NVIDIA & specialized silicon (edge, quantum, crypto, robotics)
*Venues: ISCA, MICRO, HPCA, ASPLOS; only a tail in MLSys.* Mechanism: co-design ISA/dataflow/
circuit for a tight envelope or a non-transformer domain. The architecture venues carry an
entire **quantum + FHE/ZKP + robotics/embodied-AI** cohort that has essentially no MLSys
presence: `isca-2025-025` zkSpeed, `isca-2025-047` Dadu-Corki robotic manipulation, `isca-2025-132`
/`micro-2025-099`/`asplos-2025-148`/`asplos-2025-154` quantum, `hpca-2025-101` QAOA, and
CIM/FPGA/RISC-V edge parts throughout. MLSys's only comparable entries are the edge tail
(`mlsys-2025-014` RISC-V N:M, `mlsys-2025-031` FPGA, `mlsys-2025-038` Huawei NPU).

---

## 4. What differs by venue

**What ISCA / MICRO / HPCA do that MLSys never touches.**
- **Real silicon and non-NVIDIA datapaths.** ASIC is the *top* hardware target at ISCA (49),
  MICRO (17), and HPCA (48); CIM/PIM/analog/photonic appear throughout. MLSys is 42/61 GPU with
  essentially one edge NPU and one FPGA. The architecture venues tape out or simulate LUT Tensor
  Cores (`isca-2025-079`), RRAM/SRAM PIM (`isca-2025-098`, `isca-2025-126`), bit-serial quant
  accelerators (`hpca-2025-000`), and spatial-accelerator generators (`hpca-2025-002`).
- **Memory-system microarchitecture & coherence.** `memory-system` is the #1 or #2 technique in
  ISCA/MICRO/HPCA (47/25/61) — DRAM bank folding, in-DRAM tag comparison, near-core/near-memory
  processing, cache-compression circuits, CXL coherence. MLSys treats DRAM/HBM as a fixed tier
  to overlap, never to redesign. Coherence appears as `coherence`/formal-proof work
  (`micro-2025-081`, `asplos-2025-134`, `asplos-2025-140`); MLSys has zero coherence papers.
- **Interconnect/NoC as first-class silicon.** NoC multicast, mesh-native AllReduce, chiplet AMO
  coherence, wafer-scale networks (`hpca-2025-001`, `hpca-2025-058`, `micro-2025-081`,
  `isca-2025-093`). MLSys treats NVLink/IB as a bandwidth number to overlap.
- **Security & side-channels.** ~9 ISCA / 6 MICRO / 13 HPCA / 34 ASPLOS security papers vs
  effectively zero at MLSys. RowHammer, Spectre/transient execution, TEE/confidential compute,
  side-channels — an entire axis MLSys does not engage.
- **Reliability at the device/protocol level.** SDC modeling, low-voltage CIM error correction,
  formal coherence proofs, QEC decoders. MLSys reliability is limited to serving-SLO robustness.
- **Whole non-LLM domains.** HPC (top-2 workload at ISCA/MICRO/HPCA), databases, genomics,
  quantum, FHE/ZKP, ray-tracing, robotics. MLSys is ~80% dense-transformer LLM.

**What MLSys (and ASPLOS's serving corner) do that the architecture venues barely touch.**
- **Production LLM-serving scheduling under SLOs.** Constrained-optimization schedulers, prefill/
  decode disaggregation, prefix-cache reuse, heterogeneous-cluster routing (`mlsys-2025-018`,
  `mlsys-2025-023`, `mlsys-2025-040`, `asplos-2025-049`). ISCA/HPCA touch this only as a
  hardware-scheduling or energy problem (`isca-2025-129`, `hpca-2025-082`).
- **Distributed-training parallelism plans.** RLHF stage reallocation, pipeline-bubble filling,
  vocabulary parallelism, MPMD runtimes (`mlsys-2025-030`, `-010`, `-052`, `-045`). The
  architecture venues engage training mainly via the interconnect/fault axis.
- **Attention/KV kernel engineering as software.** JIT-templated kernels for every attention
  variant on stock CUDA (`mlsys-2025-000`, `-015`, `-037`) — a level the architecture venues
  either bypass (build an accelerator) or reverse-engineer (`micro-2025-043`).
- **Depth of full-text grounding.** Every MLSys claim is a high-confidence full-text extraction;
  the architecture venues are mostly abstract-only (see §6).

**ASPLOS is the genuine bridge.** It is the one venue that carries both sides at scale —
GPU LLM serving/MoE/training (`asplos-2025-049`, `-073`, `-105`, `-133`) *and* CPU/memory/
security/coherence architecture (`asplos-2025-051`, `-113`, `-124`, `-134`, `-116`) — which is
exactly why its CPU (81) and GPU (55) counts are both large and its security pillar (34) is the
biggest of any venue.

---

## 5. Cross-cutting observations

**The co-design reflex is universal — but the seam moves by venue.** Every venue's dominant move
is "fuse an algorithmic idea into the datapath and its scheduling." MLSys fuses into the
Tensor-Core/SM (quantization ⋈ GEMM, sparsity ⋈ kernel). The architecture venues push the seam
lower: quantization ⋈ *circuit* (`isca-2025-079` LUT, `isca-2025-126` IR-drop), sparsity ⋈
*dataflow array* (`asplos-2025-079`, `hpca-2025-035`), attention ⋈ *DRAM/PIM* (`micro-2025-012`,
`asplos-2025-051`). The phrase "hardware-software co-design" appears in the primary theme of
dozens of architecture papers explicitly.

**Recurring baselines diverge sharply.** MLSys has a near-standard harness: vLLM (+Outlines),
FlashAttention-2/FlashInfer, TensorRT-LLM, GPTQ/MARLIN, Megatron/DeepSpeed on A100/H100. The
architecture venues have *no* comparable shared harness — baselines are prior accelerators
(VEGETA/STC, MARLIN as a GPU point), A100/H100 as an upper-bound reference (`asplos-2025-051`
beats 4×A100), and each subfield's own simulator. This makes cross-paper comparison inside the
architecture venues weaker than inside MLSys, a point `hpca-2025`'s own "statistical methodology
for aggregate speedup" paper raises directly.

**Shared framings that cross the venue boundary.** (1) *Prefill vs decode as opposite regimes* —
MLSys (`-018`, `-023`, `-040`, `-047`), ISCA (`isca-2025-129`), HPCA (`hpca-2025-082`). (2)
*Bandwidth-bound, not compute-bound* — the explicit motivation for near-data work everywhere, and
notably confirmed even for real compute-in-SRAM silicon (`micro-2025-118`: "even compute-in-SRAM
can be bandwidth-bound"). (3) *Dynamic/adaptive over static* — adaptive quant/sparsity budgets,
reconfigurable execution, dynamic energy knobs (`hpca-2025-082`, `isca-2025-042`).

**Tensions.** *Reported vs realized speedup*: `mlsys-2025-007` shows KV-compression gains vanish
under real serving frameworks — a caution the many single-batch/simulator-based quantization and
PIM accelerator papers in ISCA/HPCA/MICRO inherit but rarely address. *Generality vs peak*:
programming-model/generator papers (`mlsys-2025-015`, `hpca-2025-002` LEGO, `micro-2025-021`)
trade peak performance for retargetability. *Accuracy vs efficiency*: negotiated everywhere via
"near-lossless"/quality-floor claims, seldom eliminated.

**Honest gaps.**
- **Energy/PPA still under-reported outside edge/PIM.** Datacenter GPU work reports throughput,
  rarely Joules or TOPS/W; the architecture venues report energy/area more often, but carbon/
  lifecycle metrics (`hpca-2025` carbon-aware DSE, `isca-2025` carbon attribution) are a small
  frontier.
- **Training numerics/convergence at scale is thin** in every venue; most training work optimizes
  throughput/memory, not correctness (MoE fault-tolerance `asplos-2025-042` and SDC modeling are
  the exceptions).
- **The GPU-free premise is barely explored** — `asplos-2025-051` (PIM+CXL beats 4×A100) is
  nearly alone in seriously proposing a non-GPU datacenter LLM path; almost everything else still
  benchmarks against, or runs on, NVIDIA.
- **Cross-layer integration is asserted, not demonstrated.** Architecture papers propose new
  silicon; MLSys papers optimize existing silicon; almost no 2025 paper closes the loop by
  running a real production serving stack on a novel accelerator.

---

## 6. Coverage & confidence (read this before quoting counts)

**Corpus.** 619 papers across MLSys, ISCA, MICRO, HPCA, ASPLOS. **503 analyzed**; **116
title-only, NOT analyzed.**

**Confidence split (analyzed):** 120 full-text/high, 383 abstract-only/low.
- MLSys 61: **61 high, 0 low** — the only fully full-text corpus; its taxonomy is the reliable anchor.
- ISCA 112: 17 high, 95 low.
- MICRO 47 analyzed: 20 high, 27 low — **plus 76 further papers title-only and excluded**, because IEEE withholds MICRO abstracts and many are not on arXiv. **MICRO is materially under-sampled**: the 47 analyzed are the arXiv-available minority, likely skewed toward authors who self-post (systems/security/quantum), so MICRO's thematic mix here is the least trustworthy of the five and its true totals are larger than shown.
- HPCA 119: 8 high, 111 low.
- ASPLOS 164: 14 high, 150 low.

**What this means for the claims above.**
- **Abstract-only (`low`) analyses are shallower.** For ISCA/MICRO/HPCA/ASPLOS the technique/
  workload/theme tags are inferred from abstracts, not full text — mechanism details, baselines,
  and quantitative metrics are less reliable than the MLSys records. Treat every non-MLSys
  headline number as directional.
- **Counts are lower bounds, unevenly.** Because 116 papers (mostly MICRO) are unanalyzed, and
  the architecture venues are dominated by abstract-only records, the normalized hardware/workload
  tallies undercount and mis-weight — especially for MICRO. The *qualitative* contrasts in §4
  (silicon/memory/interconnect/security at the architecture venues vs GPU-serving at MLSys) are
  robust because they are structural and visible even from abstracts; the *precise* per-venue
  numbers are not.
- **No cross-venue metric commensurability.** Baselines, hardware (A100/H100 vs ASIC vs CIM vs
  simulator), batch sizes, and sequence lengths differ within and across venues. Speedups are
  comparable *within a theme in one venue* at best, never across venues.
- **High-confidence anchors used for grounding.** ISCA (`003,007,014,021,025,042,047,055,058,079,086,098,126,130,132`), MICRO (`007,012,021,025,035,043,054,069,077,081,089,099,104,118`), HPCA (`002,003,010,035,045,082,084,101`), ASPLOS (`049,051,077,079,105,113,116,117,124,133,134,148,154,170`), MLSys (full corpus). Ids cited from `low` records (e.g. RowHammer/NoC/interconnect papers) are abstract-grounded and flagged by context.

Bottom line: the field-level story — **transformer inference against the memory wall, co-designed
at whatever layer each venue owns** — is well supported. The per-venue *numbers*, and MICRO's
picture in particular, are under-sampled; do not overclaim precision.
