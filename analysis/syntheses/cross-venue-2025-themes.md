# Cross-Venue Synthesis — AI Hardware & Systems, 2025

Six top venues, one year: **MLSys, ISCA, MICRO, HPCA, ASPLOS, DAC**. This file reads the
six per-venue deterministic digests and the MLSys theme taxonomy (its anchor), samples the
per-paper JSON extractions to ground every claim in specific paper ids, and draws the real
contrasts across the stack. Paper ids are cited as `venue-2025-nnn`.

**Corpus:** 719 papers total, 603 analyzed (120 full-text/`high`, 483 abstract-only/`low`),
116 title-only NOT analyzed. See §6 for the honest coverage picture — the MICRO and DAC
slices are meaningfully under-sampled and abstract-only records are shallower.

---

## 1. The one-paragraph picture

Across all six venues in 2025 the field is doing one thing above all others: **bending the
entire hardware/software stack around the LLM transformer, and around attention and the
KV-cache in particular.** "LLM-inference" is the single most common workload at *every* venue
— MLSys (26), ISCA (31), MICRO (16), HPCA (29), ASPLOS (37), DAC (14) — and the dominant
mechanisms recur regardless of where the paper lands: fuse an algorithmic idea (a sparsity
pattern, a quantization scheme, an attention variant, a prefill/decode split) directly into
the datapath and its scheduler rather than treating them as separable layers. What changes is
the *layer of the stack* each venue attacks. MLSys optimizes GPU software — kernels, serving
schedulers, parallelism plans — on NVIDIA A100/H100 silicon it takes as given. The three
architecture venues (ISCA, MICRO, HPCA) build the silicon MLSys stands on and carry the entire
body of work MLSys structurally cannot touch: real ASICs and compute-in-memory, memory systems
and cache coherence, on-chip interconnect, RowHammer and side-channel security, reliability
and silent-data-corruption, and near-data/processing-in-memory. ASPLOS sits deliberately at
the boundary, pairing compiler and OS/runtime work with hardware co-design and a heavy
security/verification stream. DAC is the design-automation venue — it is where the *tools*
that build all of the above live: chip generators, EDA (placement, routing, timing, IR-drop),
RTL simulation, verification, and increasingly LLM-for-chip-design. The collective reflex
everywhere is **co-design**, and the collective blind spot — inherited straight from MLSys and
only partly repaired by the architecture venues — is non-NVIDIA silicon and honest energy/PPA
accounting.

---

## 2. Per-venue character

**MLSys — systems-for-LLMs on GPUs.** MLSys is the software-systems venue for the NVIDIA GPU:
42/61 papers name a GPU, A100/H100 are the de-facto harness, and non-NVIDIA silicon is almost
absent (one Huawei DaVinci NPU, one RISC-V ASIC, no TPU, no AMD GPU). Workloads are
overwhelmingly LLM-inference (26) and LLM-training (22). The work is kernels, serving
schedulers, quantization-for-serving, parallelism plans, and offloading — never the silicon
itself. Signature: **mlsys-2025-000** (FlashInfer, a unifying attention/KV-layout kernel
compiler), **mlsys-2025-003** (QServe W4A8KV4 quantization co-designed with the Tensor-Core
datapath), **mlsys-2025-018** (SOLA, per-iteration SLO-aware prefill/decode scheduling on
vLLM). It is the anchor taxonomy (9 themes) the rest of this synthesis is measured against —
and the venue whose gaps (no real silicon, little energy measurement) the architecture venues
exist to fill.

**ISCA — real silicon, memory systems, and the whole non-GPU frontier.** ISCA is where the
hardware actually gets built: ASIC dominates (49/112), with CIM (13), FPGA (10), SoC (10),
plus photonic, PIM, analog, chiplet, and a single TPU. Its technique profile is memory-system
(47), dataflow (39), near-data-processing (27), interconnect (17), reliability (12), and
security (9) — an entire axis MLSys never touches. Workloads are broader too: alongside
LLM-inference (31) sit HPC (28), GNN (23), database (18). Signature: **isca-2025-079** (LUT
Tensor Core, a bit-serial LUT-based low-bit LLM datapath at 4–6× power/area vs MAC Tensor
Cores), **isca-2025-058** (NMP-PaK, channel-level near-memory processing for genome assembly),
**isca-2025-007** (Oaken, an ASIC/NPU KV-cache quantization serving engine). ISCA also carries
the quantum, cryptographic-accelerator (zkSNARK **isca-2025-025**, FHE), and carbon-accounting
work that has no MLSys analogue.

**MICRO — microarchitecture, security, and the memory subsystem (but under-sampled).** MICRO
is the microarchitecture venue: CPU (19) and ASIC (17) lead, and its center of gravity is the
memory system (25) plus caches (8), prefetching (6), and a distinctive, deep **DRAM-security**
stream — RowHammer attack/defense (**micro-2025-025** ρHammer revives RowHammer via prefetch
instructions on modern Intel; several defense papers). It is also where microarchitecture gets
*reverse-engineered* (**micro-2025-043**, dissecting NVIDIA Ampere SM pipelines — a genre MLSys
would never publish). Signature also: **micro-2025-057** (Pimba, PIM for post-transformer LLM
serving), **micro-2025-087** (automated RISC-V instruction-subset processor generation for
extreme edge). Caveat: only 47 records and 76 title-only papers are excluded because IEEE
withholds MICRO abstracts, so this is the *most* under-sampled venue (see §6).

**HPCA — the largest architecture slice: memory, reliability, near-data, quantum.** HPCA is the
broadest architecture corpus here (119 records). Its technique histogram is memory-system (61),
scheduling (54), dataflow (40), near-data-processing (24), cache (19), reliability (14),
prefetching (13), security (13), interconnect (11). HPC (40) edges out LLM-inference (29) as
the top workload — HPCA keeps a strong non-AI HPC/systems core. It owns coherent-interconnect
work (**hpca-2025-001**, Push Multicast: a speculative coherent manycore interconnect),
spatial-accelerator *generators* (**hpca-2025-002**, LEGO: affine-representation RTL generation
for tensor apps), reliability at the microarchitecture level (silent-data-corruption modeling),
and a large quantum-computing cluster. Signature also: **hpca-2025-003** (VQ-LLM,
vector-quantized LLM code generation on GPU), **hpca-2025-082** (DynamoLLM, energy-aware LLM
cluster reconfiguration — one of the few papers that actually measures Joules).

**ASPLOS — the cross-layer venue: compilers, OS/runtime, security, and co-design.** ASPLOS is
the largest corpus (164) and deliberately spans the interfaces: CPU (81) and GPU (55) lead, and
its technique profile is scheduling (81), memory-system (60), **compiler (49)**, parallelism
(40), and a very heavy **security (34)** and reliability/verification (18) stream that the pure
architecture venues carry more thinly. It is where confidential-computing (TEE/SEV-SNP side
channels **asplos-2025-134**), RowHammer-to-hypervisor-escape (**asplos-2025-027**), FHE
compilation (**asplos-2025-029/042**), and formal hardware verification live next to LLM
serving. Signature: **asplos-2025-105** (FSMoE, overlapping inter- and intra-node MoE
communication with compute), **asplos-2025-049** (Past-Future Scheduler, output-length-aware
SLA-guaranteed LLM serving), **asplos-2025-113** (MOAT, provably secure per-row-activation
RowHammer mitigation). ASPLOS is the bridge between MLSys-style systems and ISCA/MICRO/HPCA
silicon.

**DAC — the design-automation / EDA venue.** DAC is categorically different: it is about the
*tools that build the chips*, not the chips as workloads. Its dominant technique is
**circuit-design (38)** plus compiler (25), and its tags are EDA-native — physical-design,
routing, placement, IR-drop, verification, timing, VLSI, logic-synthesis. Signature EDA work:
**dac-2025-035** (iterative clock-skew scheduling with dynamic sequential-graph extraction),
**dac-2025-020** (GPU-accelerated statistical static timing analysis), **dac-2025-042** (GSIM,
multi-abstraction-level RTL simulation, 19.9× speedup), **dac-2025-090** (IRGNN, graph-based
per-node IR-drop prediction). A fast-growing DAC sub-stream is **AI-for-EDA and LLM-for-chip-
design**: **dac-2025-006** (diffusion transformer for push-button analog IC sizing),
**dac-2025-024** (contrastive learning for lithographic hotspot detection), **dac-2025-060**
(ChipAlign, LLM instruction-alignment for chip design), **dac-2025-018** (multi-agent LLM
quantum-code generation). DAC also carries hardware co-design for AI accelerators
(**dac-2025-072** SQ-DM 4-bit diffusion accelerator) but always with the EDA/tool lens. Caveat:
only 100/457 fetched (DBLP instability) — heavily under-sampled (§6).

---

## 3. Shared cross-venue themes

Themes that recur **across** venues, with the venues that carry them, the shared mechanism, and
representative ids.

### T1 — LLM attention & KV-cache acceleration
*All six venues.* The single most universal theme. The shared mechanism is **restructuring
attention and the KV-cache to fit the target datapath**: unify KV layouts and generate kernels
(**mlsys-2025-000** FlashInfer), split prefill/decode as opposite regimes and schedule them
(**mlsys-2025-018**, ISCA dynamic scheduling for phase-disaggregated serving), and compress
or quantize the KV-cache in hardware (**isca-2025-007** Oaken online-offline hybrid KV quant,
**isca-2025-021** Ecco entropy-aware KV compression with a parallel Huffman decoder,
**mlsys-2025-025** TurboAttention). On the silicon side the *same* problem becomes a
purpose-built engine: **micro-2025-057** (Pimba PIM for post-transformer serving),
**dac-2025-128** (distance-based attention sparsity on hierarchical PIM for ultra-long context),
**dac-2025-134** (dual-mode PIM for asymmetric attention GEMV). MLSys writes the kernel; ISCA/
MICRO/DAC build the accelerator; the bottleneck (attention + KV) is identical.

### T2 — Quantization & low-precision
*All six venues.* Everyone drives precision down, but the **co-design partner differs by venue.**
MLSys co-designs precision with the *Tensor-Core datapath* (**mlsys-2025-003** W4A8KV4,
**mlsys-2025-021** INT3 MoE). The architecture venues build *custom low-bit datapaths*:
**isca-2025-079** (LUT Tensor Core), **hpca-2025-003** (VQ-LLM vector quantization),
**micro-2025** outlier-aware MX block-floating-point for 4-bit LLM inference and sub-8-bit SIMD
convolution. HPCA adds per-group/variable-precision GEMM accelerators; ASPLOS contributes
masked vector quantization (**asplos-2025-079** MVQ); DAC pairs quantization with sparsity in
accelerators (**dac-2025-072** SQ-DM 4-bit diffusion, **dac-2025-030** SAGA mixed-precision).
Shared mechanism: protect outliers, group/mix precision, and make the reduced precision
*natively executable* rather than dequantized back to FP32.

### T3 — Memory hierarchy, near-data & processing-in-memory
*ISCA, MICRO, HPCA, ASPLOS, DAC (not MLSys at the silicon level).* This is the theme MLSys can
only approximate in software (offloading a slow tier behind GPU compute — **mlsys-2025-024** NEO,
**mlsys-2025-033** FlexInfer). The architecture venues do the real thing: **near-data /
processing-in-memory** is a first-class category (ISCA NDP 27, HPCA NDP 24, MICRO NDP 11). Shared
mechanism: **move compute to where the data lives** to escape the bandwidth wall.
**isca-2025-058** (channel-level NMP genome assembly), **micro-2025** Mono3D DRAM NMP for MoE
with in-memory tiering and locality-aware PIM-host cooperation for graphs, **hpca-2025** async
host-NMA co-execution in DIMM-based near-memory and PIM for FHE modular arithmetic,
**asplos-2025-170** (PUSHtap PIM-based in-memory HTAP), **dac-2025-141** (retrieval-in-memory
for RAG via hierarchical PIM). Compute-in-memory/CIM appears at every architecture venue
(ISCA 13, HPCA 13, MICRO 6, DAC 6) — and **micro-2025-118** is a rare honest note: a real
commercial compute-in-SRAM device is *still* bandwidth-bound without careful dataflow.

### T4 — Interconnect, collectives & communication overlap
*MLSys, ISCA, HPCA, ASPLOS, DAC.* Distributed AI spends a large fraction of time in collectives;
the shared mechanism is **hide communication behind compute, or redesign the network.** MLSys
does it in software at tile granularity (**mlsys-2025-002** TileLink, **mlsys-2025-055** COMET
MoE all-to-all overlap); ASPLOS does the same for MoE training (**asplos-2025-105** FSMoE dual
inter/intra-node overlap) and auto-schedules the overlap. The architecture venues instead build
the *network*: **hpca-2025-001** (Push Multicast speculative coherent interconnect),
**isca-2025** flexible non-blocking topology for large-scale AI/HPC interconnects, traffic
shaping for non-uniform multi-GPU links, and topology-aware NPU virtualization.
Collective-communication-driven fault detection for distributed training appears at both HPCA
and MLSys.

### T5 — Sparsity & MoE
*All six venues.* Shared mechanism: **make irregular sparsity hardware-legible** — decompose to
supported N:M patterns, prune whole columns/tokens, or exploit temporal/output redundancy.
MLSys: **mlsys-2025-022** (TASD unstructured→N:M), **mlsys-2025-014** (RISC-V N:M ISA). The
architecture venues build sparse accelerators with on-chip memory adaptation: MICRO
reconfigurable sparse accelerator with distributed on-chip memory and adaptive caching for
sparse tensor accelerators; ISCA on-chip cache optimization for SpMM; HPCA joint input-weight
bit-slice sparsity. Output/temporal sparsity is a distinct architecture-venue move:
**hpca-2025-035** (EXION inter/intra-iteration diffusion output sparsity), **dac-2025-072**
(temporal sparsity in diffusion). MoE-specific systems recur too (**asplos-2025-105/133**,
MICRO Mono3D DRAM for MoE, MLSys COMET/MiLo).

### T6 — Compilation, programming models & accelerator generation
*MLSys, ISCA, MICRO, HPCA, ASPLOS, DAC.* Shared mechanism: **raise the abstraction so one
description targets many datapaths.** MLSys: programmable attention (**mlsys-2025-015**
FlexAttention), tile-centric comm (TileLink), MPMD pipelines (JaxPP). The architecture venues
generate the *hardware itself*: **hpca-2025-002** (LEGO affine-representation spatial-accelerator
RTL generation), **isca-2025-003** (RSN circuit-switched streaming ISA for FPGA overlays),
**micro-2025-087** (automated RISC-V subset-processor generation), **micro-2025-021**
(LLMulator generalizable cost modeling for dataflow accelerators). ASPLOS carries the deepest
compiler stream (49 papers: einsum-tree layout IR, differentiable e-graph extraction,
inter-operator DNN compilers). DAC owns the RTL/EDA-tool end (**dac-2025-042** GSIM RTL
simulation, logic-synthesis via equality saturation, **dac-2025-060** LLM-for-chip-design).

### T7 — Security, side-channels & reliability
*ISCA, MICRO, HPCA, ASPLOS, DAC (essentially absent from MLSys).* This is a defining
architecture/systems theme with no real MLSys presence. Shared sub-streams: **RowHammer**
attack-and-defense at every architecture venue (**micro-2025-025** ρHammer prefetch revival,
**asplos-2025-113** MOAT per-row-counter mitigation, **asplos-2025-027** RowHammer hypervisor
escape, on-DRAM-die mitigations at HPCA); **microarchitectural side channels**
(**asplos-2025-124** SMaCk self-modifying-code I-cache attack, transient-execution mitigation via
memory tagging at ISCA, secure BTB at MICRO); **confidential computing** (SEV-SNP contention
channels **asplos-2025-134**, CXL-memory encryption for TEEs); and **reliability**
(silent-data-corruption modeling at HPCA and ASPLOS, low-voltage CIM error correction).
DAC adds hardware-root-of-trust/PUF and backdoor work (**dac-2025-107** concealed backdoor via
unlearning, PUF security). MLSys touches security only as ML-supply-chain/robustness, never as
hardware side-channels.

### T8 — Cryptographic & quantum acceleration
*ISCA, MICRO, HPCA, ASPLOS, DAC.* Two clusters with no MLSys footprint. **FHE / ZKP / PQC
accelerators**: **isca-2025-025** (zkSpeed HyperPlonk ZKP ASIC), **isca-2025-086** (Finesse
pairing-based crypto co-design), FHE accelerators and GPU-FHE kernels at HPCA/ASPLOS
(**asplos-2025-029/042**, **hpca-2025-027/037/070**), loop-aware FHE bootstrapping compilation.
**Quantum computing** is a substantial recurring stream at ISCA (synchronization for
fault-tolerant QC **isca-2025-077**), MICRO (distributed quantum control **micro-2025-007**,
leakage speculation for QEC **micro-2025-078**), HPCA (Choco-Q constrained optimization
**hpca-2025-101**, Clifford extraction), ASPLOS (Micro Blossom MWPM decoder **asplos-2025-148**,
Fat-Tree QRAM **asplos-2025-154**), and DAC (qubit routing, LLM quantum-code generation
**dac-2025-018**). Entirely outside the MLSys scope.

### T9 — Serving scheduling, SLOs & cluster energy
*MLSys, ISCA, HPCA, ASPLOS, DAC.* Production LLM serving under SLOs recurs as its own theme.
Shared mechanism: **phase-aware / demand-aware reconfiguration.** MLSys owns the software depth
(**mlsys-2025-018** SOLA, **mlsys-2025-023** ThunderServe heterogeneous disaggregation);
ASPLOS adds output-length-aware scheduling (**asplos-2025-049**) and CoE serving under memory
limits (**asplos-2025-133**); HPCA adds the energy dimension the others omit (**hpca-2025-082**
DynamoLLM multi-knob energy-aware cluster reconfiguration); ISCA formalizes phase-disaggregated
scheduling in hardware terms; DAC contributes real-time oversubscribed GPU DNN scheduling
(**dac-2025-007** DARIS).

### T10 — Edge / on-device co-design
*MLSys, ISCA, MICRO, HPCA, DAC.* A distinct low-power frontier. Shared mechanism: **co-design at
the ISA/dataflow/algorithm level for a tight energy/SRAM envelope.** MLSys: forward-only
on-device training (**mlsys-2025-019**), FPGA long-context dataflow (**mlsys-2025-031**). The
architecture venues push into real edge silicon: **isca-2025-047** (Dadu-Corki robotic-
manipulation co-design), **micro-2025-087** (extreme-edge RISC-V generation), **micro-2025-069**
(RTGS real-time 3DGS SLAM on edge), **hpca-2025-045** (multi-dimensional vector ISA for mobile
in-cache computing), **hpca-2025-084** (IRIS ISP-software co-design for machine vision). DAC adds
edge deployment (**dac-2025-016** EEG-driven prosthetic edge ML, SNN pruning). 3D Gaussian
Splatting SLAM on edge independently appears at ISCA, MICRO, and HPCA — a notable convergence.

---

## 4. What differs by venue

**What ISCA / MICRO / HPCA / DAC do that MLSys never touches:**
- **Real silicon and custom datapaths.** ASIC is the #1 target at ISCA (49), HPCA (48), DAC (38)
  and #2 at MICRO; CIM/PIM/analog/photonic/chiplet appear across all four. MLSys has essentially
  one ASIC and one FPGA result — it optimizes *for* the GPU it is handed.
- **The memory subsystem as a first-class object.** Cache-replacement policy
  (**micro-2025-054** temperature-aware, **isca-2025-060** pairwise instruction-data LLC),
  coherence protocols, DRAM microarchitecture, near-data/PIM (T3), and prefetching are a huge
  fraction of the architecture corpus and have no MLSys analogue (MLSys "memory" means GPU-HBM
  offloading in software).
- **On-chip interconnect and coherence** (**hpca-2025-001**, ISCA topology/NoC work) — MLSys
  interconnect is NVLink/InfiniBand *usage*, never *design*.
- **Hardware security and reliability** (T7) — RowHammer, side channels, TEEs, silent-data-
  corruption. MLSys is silent here.
- **Cryptographic and quantum acceleration** (T8) — no MLSys presence at all.
- **Microarchitecture reverse-engineering** (**micro-2025-043** Ampere SM) — a genre unique to
  the architecture venues.
- **EDA / design automation (DAC only)** — placement, routing, timing, IR-drop, RTL simulation,
  logic synthesis, verification, and AI-for-EDA. None of the other five venues do chip-design
  *tooling*; this is DAC's exclusive territory.

**What MLSys (and to a degree ASPLOS) do that the architecture venues barely touch:**
- **Large-scale distributed *training* systems** — RLHF parameter reallocation
  (**mlsys-2025-030** ReaL), pipeline-bubble filling (**mlsys-2025-010**), vocabulary
  parallelism, 1M–2M-token context/sequence parallelism (**mlsys-2025-050/051**). The
  architecture venues touch distributed training mainly via interconnect/fault-detection, not
  the parallelization plan.
- **Production serving software depth** — SLO-constrained per-iteration scheduling, prefix-cache
  reuse, constrained decoding (**mlsys-2025-016** XGrammar), heterogeneous-cloud disaggregation.
  ISCA/HPCA touch serving but at coarser (hardware-config) granularity.
- **Framework-level honesty checks** — **mlsys-2025-007** shows KV-compression speedups vanish
  under real PagedAttention+FlashAttention at batch > 4; this "does it survive a real serving
  stack" critique is a MLSys-native genre. HPCA's analogue is methodological (correct statistical
  methodology for aggregate speedup reporting).

**The through-line:** MLSys optimizes the *software above* fixed NVIDIA silicon; the architecture
venues build (and secure, and verify) the silicon *below*; DAC builds the *tools* that produce
that silicon. The same LLM/attention/quantization/sparsity problems appear at every layer — each
venue attacks them with the degrees of freedom available at its layer.

---

## 5. Cross-cutting observations

**The co-design reflex is universal.** Nearly every high-confidence paper fuses an algorithmic
idea into a datapath/schedule: quantization × Tensor-Core (**mlsys-2025-003**), LUT × bit-serial
Tensor Core (**isca-2025-079**), gradient redistribution × RRAM PIM (**isca-2025-098**),
trajectory prediction × robotic-control ASIC (**isca-2025-047**), sparsity × diffusion
accelerator (**hpca-2025-035**, **dac-2025-072**). "Algorithm-hardware co-design" or
"software-hardware co-design" is the most common phrase in the corpus.

**Recurring baselines and harnesses.** MLSys/serving work benchmarks against a near-standard
harness: **vLLM (+Outlines) / SGLang / TensorRT-LLM on A100/H100 with FlashAttention-2**;
quantization against GPTQ/MARLIN; training against Megatron-LM/DeepSpeed/FSDP. The architecture
venues compare against **their own prior accelerators** and, tellingly, against **an A100/H100
GPU as the "to beat" reference** even for ASIC/FPGA work (e.g. RSN-XNN vs A100/T4 in
**isca-2025-003**) — the GPU is the field's universal yardstick across all six venues.

**Consistent framings.** *Prefill vs decode as opposite regimes* recurs from MLSys serving into
ISCA phase-disaggregation. *Hide a slow tier behind a fast one* generalizes from MLSys
PCIe/CPU-offload to architecture-venue near-data/PIM. *Dynamic/adaptive over static* appears as
adaptive sparsity budgets, SLO-aware scheduling, and multi-knob cluster reconfiguration.

**Tensions.** (1) *Reported vs realized speedup* — **mlsys-2025-007** is the cautionary tale for
the whole quantization/compression cluster; **micro-2025-118** is its silicon analogue (real
compute-in-SRAM is still bandwidth-bound). (2) *Generality vs peak performance* — programming-
model and accelerator-generator papers (FlexAttention, TileLink, LEGO, RSN) trade peak
throughput for portability. (3) *Accuracy vs efficiency* — negotiated everywhere, rarely
eliminated; "near-lossless" and explicit quality floors are ubiquitous.

**Honest gaps.**
- **Non-NVIDIA silicon is under-represented even where it should not be.** MLSys is
  GPU-monoculture; the architecture venues build ASIC/CIM but still benchmark against NVIDIA GPUs
  and rarely against each other's or vendor (TPU/AMD/Groq/Cerebras) parts. TPU appears just once
  or twice per architecture venue.
- **Energy/PPA is unevenly measured.** ISCA/MICRO/HPCA/DAC report area/power/EDP for ASIC/CIM
  work, but datacenter-GPU papers (most of MLSys, much of ASPLOS) report speedup/throughput and
  almost never Joules or TOPS/W. **hpca-2025-082** (DynamoLLM) and the edge papers are the
  exceptions that prove the rule.
- **Training numerics / convergence verification at scale is thin** across all venues — systems
  are optimized for throughput/memory far more than their effect on convergence is validated.
- **MoE, hybrid/SSM, diffusion, and multimodal remain frontier** relative to the deluge of
  dense-transformer attention work, though MoE is clearly growing at every venue.
- **Cross-venue commensurability is poor.** Baselines, hardware, batch sizes, and sequence
  lengths differ so widely that headline multipliers are directional within a theme, not
  comparable across venues.

---

## 6. Coverage & confidence — read this before trusting any count

**719 papers total; 603 analyzed; 116 title-only NOT analyzed.** Of the 603 analyzed, **120 are
full-text (`confidence: high`)** and **483 are abstract-only (`confidence: low`)**. Per-venue:

| Venue  | Analyzed | high | low | Notes |
|--------|---------:|-----:|----:|-------|
| MLSys  | 61  | 61 |   0 | Fully full-text; the reliable anchor. |
| ISCA   | 112 | 17 |  95 | Mostly abstract-only. |
| MICRO  | 47  | 20 |  27 | **76 title-only excluded** — IEEE withholds MICRO abstracts. Most under-sampled. |
| HPCA   | 119 |  8 | 111 | Almost entirely abstract-only. |
| ASPLOS | 164 | 14 | 150 | Largest corpus, mostly abstract-only. |
| DAC    | 100 |  0 | 100 | **Only ~100/457 fetched** (DBLP instability); zero full-text. Heavily under-sampled. |

**What this means, stated plainly:**
- **Only MLSys is fully full-text.** Its 9-theme taxonomy is high-confidence; everything cited
  from MLSys is grounded in a full extraction.
- **Abstract-only (`low`) analyses are shallower.** For ISCA/HPCA/ASPLOS the *distributions*
  (hardware targets, workloads, technique categories) are trustworthy in aggregate, but any
  individual `low` paper's mechanism/metrics are read from an abstract, not the full text.
  High-confidence ids were preferred for every grounded claim above.
- **The MICRO picture is under-sampled.** 76 MICRO papers are title-only (no abstract available),
  so 47 records is a partial view — MICRO's true theme balance (especially its security and
  memory-system depth) is likely *understated* here.
- **The DAC picture is the most under-sampled.** Roughly 100 of ~457 DAC papers were fetched
  due to DBLP instability, and **none** are full-text. DAC's EDA/design-automation character is
  clear from those 100, but counts should be treated as a lower bound, not a census.
- **Do not overclaim.** Cross-venue counts mix full-text and abstract-only records of uneven
  depth, and two venues are partial samples. The qualitative contrasts in §2–§4 are robust; the
  precise numeric shares (e.g. "31 LLM-inference papers at ISCA") are directional, and the
  MICRO/DAC totals in particular under-count their true corpora.
