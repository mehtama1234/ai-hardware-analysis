# Cross-Venue Synthesis — AI Hardware & Systems, 2025

Ten venues, one year: **MLSys, ISCA, MICRO, HPCA, ASPLOS, DAC, ISSCC, Hot Chips, SC, VLSID**.
This file reads the ten per-venue deterministic digests and the MLSys theme taxonomy (its
anchor), samples the per-paper JSON extractions to ground every claim in specific paper ids,
and draws the real contrasts across the full stack — from transistor and circuit up through
supercomputer. Paper ids are cited as `venue-2025-nnn`.

**Corpus:** ~1769 papers analyzed across ten venues (MLSys 61, ISCA 112, MICRO 47, HPCA 119,
ASPLOS 164, DAC 443, ISSCC 258, Hot Chips 38, SC 430, VLSID 97). Only MLSys is fully full-text;
every other venue is dominated by abstract-only (`low` confidence) records, and two of the four
newly added venues (ISSCC, VLSID) are almost entirely circuit-level abstracts. See §6 for the
honest coverage picture before trusting any count.

The four new venues widen the stack in two directions the original six did not reach: **down**
to the transistor/circuit/silicon-measurement layer (ISSCC, VLSID) and **out** to two ends of
the deployment spectrum — the taped-out industrial product (Hot Chips) and the exascale
supercomputer running real science (SC).

---

## 1. The one-paragraph picture

Across all ten venues in 2025 the field is doing one thing above all others: **bending the
entire stack — from the transistor up to the 65,536-GPU supercomputer — around the LLM
transformer, and around attention and the KV-cache in particular.** "LLM-inference" is the
single most common workload at nearly every venue — MLSys (26), ISCA (31), MICRO (16), HPCA
(29), ASPLOS (37), DAC (70), ISSCC (26), Hot Chips (22) — and even the two venues where it is
not #1 are visibly reorganizing around it: SC's top compute theme is LLM-training (37) and
exascale foundation models (`sc-2025-016` ORBIT-2 on 65,536 GPUs), and VLSID's ML/AI cluster
is its single largest technique bucket. The dominant *mechanism* recurs regardless of layer:
fuse an algorithmic idea (a sparsity pattern, a quantization scheme, an attention variant, a
prefill/decode split) directly into the datapath and its scheduler rather than treating them
as separable layers. What changes is the **layer of the stack** each venue attacks. MLSys
optimizes GPU software on NVIDIA A100/H100 silicon it takes as given. The three architecture
venues (ISCA, MICRO, HPCA) build that silicon and carry the body of work MLSys structurally
cannot touch: ASICs and compute-in-memory, memory systems and coherence, on-chip interconnect,
RowHammer/side-channels, reliability, and near-data processing. ASPLOS sits at the boundary,
pairing compilers and OS/runtime with hardware co-design and a heavy security stream. DAC
builds the *tools* that produce the silicon (EDA, RTL simulation, verification, LLM-for-chip).
The four new venues extend this: **ISSCC and VLSID** publish the *measured circuits* — real
chips with mW, GS/s, phase-noise, and TOPS/W numbers, where "AI accelerator" sits alongside
power ICs, ADCs, mm-wave transceivers, and SerDes; **Hot Chips** presents the *shipping
industrial parts* (NPUs, GPUs, CPUs, optical I/O, open-source RISC-V SoCs); and **SC** runs
the *whole machine* — distributed LLM training and inference co-existing with scientific
simulation, and, distinctively, an enormous reproducibility/artifact-evaluation apparatus that
no other venue has. The collective reflex everywhere is **co-design**; the collective blind
spot — inherited from MLSys, only partly repaired — is non-NVIDIA silicon and honest
energy/PPA accounting, though ISSCC/VLSID/Hot Chips supply the per-chip power numbers the
GPU-software venues almost never report.

---

## 2. Per-venue character

**MLSys — systems-for-LLMs on GPUs.** The software-systems venue for the NVIDIA GPU: 42/61
papers name a GPU, A100/H100 are the de-facto harness, non-NVIDIA silicon is nearly absent (one
Huawei NPU, one RISC-V ASIC, no TPU/AMD). Workloads are overwhelmingly LLM-inference (26) and
LLM-training (22); the work is kernels, serving schedulers, quantization-for-serving,
parallelism plans, and offloading — never the silicon. Signature: **mlsys-2025-000**
(FlashInfer attention/KV-layout kernel compiler), **mlsys-2025-003** (QServe W4A8KV4 co-designed
with the Tensor-Core datapath), **mlsys-2025-018** (SOLA per-iteration SLO-aware prefill/decode
scheduling on vLLM). It is the anchor taxonomy (9 themes) and the venue whose gaps the others
exist to fill.

**ISCA — real silicon, memory systems, the whole non-GPU frontier.** Where hardware gets built:
ASIC dominates (49/112) with CIM (13), FPGA (10), SoC (10), plus photonic/PIM/analog/chiplet and
one TPU. Technique profile: memory-system (47), dataflow (39), near-data-processing (27),
interconnect (17), reliability (12), security (9). Workloads broaden beyond LLM-inference (31) to
HPC (28), GNN (23), database (18). Signature: **isca-2025-079** (LUT Tensor Core bit-serial
low-bit LLM datapath, 4–6× power/area vs MAC), **isca-2025-058** (NMP-PaK channel-level
near-memory genome assembly), **isca-2025-007** (Oaken KV-cache quantization serving engine).
Carries the quantum, ZKP (**isca-2025-025** zkSpeed), FHE, and carbon-accounting work with no
MLSys analogue.

**MICRO — microarchitecture, DRAM security, the memory subsystem (under-sampled).** CPU (19) and
ASIC (17) lead; center of gravity is memory-system (25) plus caches (8), prefetching (6), and a
distinctive deep **DRAM-security** stream — RowHammer attack/defense (**micro-2025-025** ρHammer
revives RowHammer via prefetch on modern Intel). Also where microarchitecture is
*reverse-engineered* (**micro-2025-043** dissecting NVIDIA Ampere SM pipelines — a genre MLSys
would never publish). Signature: **micro-2025-057** (Pimba PIM for post-transformer serving),
**micro-2025-087** (automated RISC-V subset-processor generation for extreme edge). Caveat: 47
records; 76 title-only excluded because IEEE withholds MICRO abstracts — most under-sampled.

**HPCA — the broad architecture slice: memory, reliability, near-data, quantum.** Broadest
architecture corpus (119). Technique histogram: memory-system (61), scheduling (54), dataflow
(40), near-data-processing (24), cache (19), reliability (14), prefetching (13), security (13).
HPC (40) edges out LLM-inference (29) — HPCA keeps a strong non-AI systems core. Owns
coherent-interconnect (**hpca-2025-001** Push Multicast speculative coherent manycore),
spatial-accelerator *generators* (**hpca-2025-002** LEGO affine-representation RTL), SDC modeling,
and a large quantum cluster. Signature also: **hpca-2025-003** (VQ-LLM vector-quantized codegen),
**hpca-2025-082** (DynamoLLM energy-aware cluster reconfiguration — one of few papers measuring
Joules).

**ASPLOS — the cross-layer venue: compilers, OS/runtime, security, co-design.** Second-largest
of the original six (164), deliberately spanning interfaces: CPU (81) and GPU (55) lead;
technique profile is scheduling (81), memory-system (60), **compiler (49)**, parallelism (40),
and a heavy **security (34)** and reliability/verification (18) stream. Home of
confidential-computing (SEV-SNP contention **asplos-2025-134**), RowHammer-to-hypervisor-escape
(**asplos-2025-027**), FHE compilation (**asplos-2025-029/042**), and formal hardware
verification next to LLM serving. Signature: **asplos-2025-105** (FSMoE overlapping inter/intra-
node MoE comm with compute), **asplos-2025-049** (output-length-aware SLA LLM serving),
**asplos-2025-113** (MOAT provably-secure per-row RowHammer mitigation). The bridge between
MLSys systems and ISCA/MICRO/HPCA silicon.

**DAC — the design-automation / EDA venue, at scale.** Categorically about the *tools that build
chips*, not chips as workloads — and by far the largest corpus (443 analyzed). Dominant technique
is **circuit-design (168)** plus compiler (129), with EDA-native tags: physical-design, routing,
placement, IR-drop, verification, timing, logic-synthesis. Signature EDA work: **dac-2025-035**
(iterative clock-skew scheduling), **dac-2025-020** (GPU-accelerated statistical STA),
**dac-2025-042** (GSIM multi-abstraction RTL simulation, 19.9×), **dac-2025-090** (IRGNN
graph-based per-node IR-drop). Fast-growing **AI-for-EDA / LLM-for-chip** sub-stream:
**dac-2025-006** (diffusion transformer for analog sizing), **dac-2025-060** (ChipAlign),
**dac-2025-018** (multi-agent LLM quantum codegen). Also carries AI-accelerator co-design
(**dac-2025-072** SQ-DM 4-bit diffusion, **dac-2025-128/134** attention-on-PIM) but always with
the EDA/tool lens.

**ISSCC — measured silicon: the circuit venue.** The solid-state-circuits venue, and it looks
nothing like the systems venues: **ASIC dominates 236/258**, and its technique profile is
**circuit-design (221) + power (96)** — everything is a taped-out, measured circuit with real
mW/GS/s/phase-noise/TOPS/W numbers. AI accelerators are one cluster among many: mm-wave
transceivers, PLLs/oscillators (phase-noise 9), high-speed I/O/PAM-4 SerDes (`isscc-2025-192`
200Gb/s PAM-4), ADCs (`isscc-2025-050` 12b 3GS/s pipelined), power ICs/GaN drivers, LPDDR5X,
and biomedical/implantable SoCs. The AI work is aggressively low-power and per-chip-measured:
**isscc-2025-020** (3.9mW 200-words/min implantable speech-decoding NSP), **isscc-2025-100**
(monolithic MRAM in-memory-computing DNN microprocessor, 1.1Mb weights, 28nm),
**isscc-2025-186** (IRIS 8.55mJ/frame 3D-Gaussian-Splatting spatial-computing SoC),
**isscc-2025-190** (IBM Telum II 5.5GHz CPU with on-die DPU + AI accelerator). This is the
venue that supplies the energy/area ground-truth the GPU-software venues omit.

**Hot Chips — the shipping industrial part.** The industry-disclosure venue: 38 talks, ASIC (19)
/ SoC (14) / CPU (9) / GPU (8), workloads dominated by LLM-inference (22) and LLM-training (15).
Not peer-reviewed research so much as *presentations of real products and taped-out chips* —
NPUs, datacenter GPUs, CPUs, SmartNICs/IPUs, optical I/O, and open-source RISC-V. Signature:
**hotchips-2025-009** (MEGA.mini heterogeneous fixed+floating-point NPU for generative AI),
**hotchips-2025-028** (Basilisk 34mm² end-to-end open-source Linux-capable RISC-V SoC in 130nm —
production-grade open EDA), **hotchips-2025-033** (Clo-HDnn on-device continual-learning HDC
accelerator), plus co-packaged silicon-photonics interconnect, 400Gbps SmartNICs for AI
collectives, ultra-low-latency Ethernet switches for AI fabrics, and cloud security attestation.
Strong photonic/optical-I/O (4) and chiplet (4) presence — the scale-up interconnect story told
from the product side.

**SC — the whole machine, and reproducibility as a first-class object.** Supercomputing: GPU
dominates (173) with big AMD (MI250X, Frontier) and Aurora/Exascale presence, and it is the one
venue where AI does *not* monopolize — HPC (59) and scientific simulation sit alongside
LLM-training (37) and GNN (29). Two things make SC unique. First, **exascale AI-for-science**:
**sc-2025-016** (ORBIT-2 exascale vision foundation models for climate on 65,536 GPUs),
linear-attention exascale foundation models, N-body/plasma/quantum-chemistry at scale. Second,
and unlike every other venue, a massive **reproducibility / artifact-evaluation apparatus** —
reproducibility (25) and artifact-evaluation (19) are the *top two technique categories*, with a
whole class of "Reproducibility Report for SC25 Paper …" meta-papers (**sc-2025-050**,
**sc-2025-069**–**073**). SC also owns real non-NVIDIA-silicon evaluation the others lack:
**sc-2025-430** (unstructured sparse fine-tuning on Cerebras CS-2 wafer-scale vs A100),
**sc-2025-257** (full-system modeling of superconducting architectures), RISC-V-for-HPC
viability (**sc-2025-024**), and RoCE-vs-InfiniBand LLM training at scale (**sc-2025-058**).

**VLSID — the edge/circuit design venue (India).** The smallest and most heterogeneous new
venue (97): ASIC (16), FPGA (12), SoC (9), mixed-signal, and a spread of CMOS nodes
(180nm→6nm→14nm). Technique buckets are ML/AI (19 combined), neuromorphic (6), hardware-security
(6), FPGA design (6), approximate/low-power computing, formal verification, and analog. It sits
closest to ISSCC/DAC but at a smaller, more academic and edge-focused scale: real measured
low-power circuits (**vlsid-2025-038** 407µW real-time speech denoiser, **vlsid-2025-082**
OwlsEye real-time low-light video instance segmentation on edge with fixed-posit quantization),
in-memory/SRAM Boolean-logic computing (**vlsid-2025-080**), memristor MAGIC adders
(**vlsid-2025-081**), NoC fault-tolerant RL routing (**vlsid-2025-020**), device-level TCAD
(**vlsid-2025-045** 3D-NAND string-current variability), and RISC-V secure processors
(**vlsid-2025-083**). Neuromorphic/SNN and approximate-computing are proportionally more visible
here than at any other venue.

---

## 3. Shared cross-venue themes

Themes recurring **across** venues, with the venues that carry them, the shared mechanism, and
representative ids.

### T1 — LLM attention & KV-cache acceleration
*All ten venues.* The single most universal theme. Shared mechanism: **restructure attention and
the KV-cache to fit the target datapath.** Unify KV layouts and generate kernels (**mlsys-2025-000**
FlashInfer); split prefill/decode and schedule them (**mlsys-2025-018**, ISCA phase-disaggregation,
**sc-2025-018** gLLM global-balanced pipeline with token throttling); compress/quantize KV in
hardware (**isca-2025-007** Oaken, **isca-2025-021** Ecco entropy-aware, **mlsys-2025-025**
TurboAttention). On silicon the same problem becomes a purpose-built engine: **micro-2025-057**
(Pimba post-transformer PIM), **dac-2025-128** (distance-based attention sparsity on hierarchical
PIM), **dac-2025-134** (dual-mode PIM for asymmetric attention GEMV), **hotchips-2025-025**
(bit-separable transformer accelerator exploiting output-activation sparsity for DRAM access). MLSys
writes the kernel; ISCA/MICRO/DAC build the accelerator; Hot Chips ships it; SC scales it; the
bottleneck (attention + KV) is identical.

### T2 — Quantization & low-precision
*All ten venues.* Everyone drives precision down; the **co-design partner differs by layer.** MLSys
co-designs precision with the *Tensor-Core datapath* (**mlsys-2025-003** W4A8KV4, **mlsys-2025-021**
INT3 MoE). Architecture venues build *custom low-bit datapaths*: **isca-2025-079** (LUT Tensor
Core), **hpca-2025-003** (VQ-LLM), MICRO outlier-aware MX block-floating-point for 4-bit inference
and sub-8-bit SIMD conv. DAC pairs quantization with sparsity (**dac-2025-072** SQ-DM,
**dac-2025-030** SAGA mixed-precision; 46 quantization papers). At the circuit layer it becomes a
*measured* mixed-precision chip: **hotchips-2025-009** (MEGA.mini heterogeneous fixed+floating-point
NPU with outlier handling), Hot Chips "ultra-low-power LLM inference via extreme quantization,"
ISSCC hybrid-CIM with sign-bit processing and cooperative quantization, **vlsid-2025-082**
(fixed-posit quantization on edge). Shared mechanism: protect outliers, group/mix precision, and
make reduced precision *natively executable* rather than dequantized to FP32.

### T3 — Memory hierarchy, near-data & processing-in-memory
*ISCA, MICRO, HPCA, ASPLOS, DAC, ISSCC, Hot Chips, SC (approximated in software by MLSys/SC).*
The theme MLSys can only approximate in software (offload a slow tier behind GPU compute —
**mlsys-2025-024** NEO, **sc-2025-050** MLP-Offload multi-level offloading to break the GPU memory
wall). Architecture venues do the real thing: NDP is first-class (ISCA 27, HPCA 24, MICRO 11, DAC
57). Shared mechanism: **move compute to where the data lives.** **isca-2025-058** (channel-level
NMP genome assembly), **micro-2025** Mono3D DRAM NMP for MoE, **asplos-2025-170** (PUSHtap in-memory
HTAP), **dac-2025-141** (retrieval-in-memory for RAG). CIM/in-memory computing spans every silicon
venue (ISCA 13, HPCA 13, DAC 31, ISSCC 9, VLSID 3): **isscc-2025-100** (monolithic MRAM IMC
microprocessor), **vlsid-2025-080** (SRAM in-periphery Boolean computing), **hotchips-2025**
(chiplet-based in-memory computing for inference; memory-centric datacenter architecture).
**micro-2025-118** stays honest: a real commercial compute-in-SRAM device is *still* bandwidth-bound
without careful dataflow.

### T4 — Interconnect, collectives & communication overlap
*MLSys, ISCA, HPCA, ASPLOS, DAC, ISSCC, Hot Chips, SC.* Distributed AI spends a large fraction of
time in collectives; shared mechanism: **hide communication behind compute, or redesign the
network.** MLSys/ASPLOS overlap in software at tile/MoE granularity (**mlsys-2025-002** TileLink,
**mlsys-2025-055** COMET, **asplos-2025-105** FSMoE). SC scales it to the machine: **sc-2025-051**
(universal one-sided distributed matmul), **sc-2025-058** (RoCE-vs-InfiniBand for LLM training),
communication-minimizing trace analysis. Architecture venues build the *network*: **hpca-2025-001**
(Push Multicast), ISCA flexible non-blocking AI/HPC topology and multi-GPU traffic shaping.
**Optical/photonic scale-up interconnect** is a distinct Hot Chips/ISSCC signature: co-packaged
silicon photonics for AI clusters, photonic interposers/chiplets, monolithic optical-I/O SoCs
(**hotchips-2025** cluster), and ISSCC 100Gbaud LPO drivers / 200Gb/s PAM-4 transceivers
(**isscc-2025-192**) — the *physical* AI-fabric layer the systems venues only consume.

### T5 — Sparsity & MoE
*All ten venues.* Shared mechanism: **make irregular sparsity hardware-legible** — decompose to
N:M, prune columns/tokens, or exploit output/temporal redundancy. MLSys: **mlsys-2025-022** (TASD
unstructured→N:M), **mlsys-2025-014** (RISC-V N:M ISA). Architecture venues build sparse
accelerators with adaptive on-chip memory (MICRO reconfigurable sparse accelerator; ISCA SpMM cache
optimization; HPCA joint input-weight bit-slice sparsity). Output/temporal sparsity is an
architecture move: **hpca-2025-035** (EXION diffusion output sparsity), **dac-2025-072** (temporal
sparsity in diffusion), **hotchips-2025** (sparse-activation-aware transformer accelerator). SC
pushes sparsity to wafer-scale: **sc-2025-430** (unstructured sparse fine-tuning on Cerebras CS-2).
MoE recurs everywhere (**asplos-2025-105/133**, MICRO Mono3D-for-MoE, MLSys COMET/MiLo, SC MoE
inference, DAC MoE).

### T6 — Compilation, programming models & accelerator/chip generation
*All ten venues.* Shared mechanism: **raise the abstraction so one description targets many
datapaths.** MLSys: programmable attention (**mlsys-2025-015** FlexAttention), tile-centric comm.
Architecture venues generate the *hardware itself*: **hpca-2025-002** (LEGO spatial-accelerator RTL),
**isca-2025-003** (RSN circuit-switched streaming ISA), **micro-2025-087** (RISC-V subset-processor
generation), **micro-2025-021** (LLMulator cost modeling). ASPLOS carries the deepest compiler
stream (49). DAC owns the RTL/EDA-tool end at scale (compiler 129: **dac-2025-042** GSIM, logic
synthesis via equality saturation, **dac-2025-060** LLM-for-chip). Two new venues extend the
*generation* story to real tape-outs: **hotchips-2025-028** (Basilisk end-to-end open-source EDA
producing a 34mm² Linux-capable RISC-V SoC), Hot Chips "large-scale open-source RISC-V via optimized
EDA" and "rapid academic chip-design workflow." SC contributes compiler-for-science: sample-free
compilation for dynamic tensor workloads, Fortran GPU-offload modernization, mapping generation for
distributed Fourier ops.

### T7 — Security, side-channels & reliability
*ISCA, MICRO, HPCA, ASPLOS, DAC, ISSCC, VLSID, Hot Chips (essentially absent from MLSys).* A
defining architecture/systems/circuits theme with no real MLSys presence. Sub-streams: **RowHammer**
(**micro-2025-025** ρHammer, **asplos-2025-113** MOAT, **asplos-2025-027** hypervisor escape, on-DRAM
mitigations at HPCA); **microarchitectural side channels** (**asplos-2025-124** SMaCk,
**asplos-2025-134** SEV-SNP, secure BTB at MICRO); **confidential computing** (CXL-memory encryption
for TEEs, **hotchips-2025-015** Azure secure hardware attestation, **vlsid-2025** memory-verification
for TEEs); and **reliability/SDC** (silent-data-corruption modeling at HPCA/ASPLOS, low-voltage CIM
error correction, SC RedSan GPU memory sanitizer **sc-2025-427** and redundant-instruction
fault-tolerance). DAC adds hardware-root-of-trust/PUF and backdoor work (**dac-2025-107**; 47
security papers). ISSCC/VLSID add *physical-attack* security absent elsewhere: **isscc-2025-240**
(sensor-less laser-voltage-probing-attack detection), PUF error-detection, CAN-bus reverse
engineering. VLSID carries a proportionally large hardware-security/trust cluster (6).

### T8 — Cryptographic & quantum acceleration
*ISCA, MICRO, HPCA, ASPLOS, DAC, Hot Chips, SC, VLSID.* Two clusters with no MLSys footprint.
**FHE/ZKP/PQC accelerators**: **isca-2025-025** (zkSpeed HyperPlonk ASIC), **isca-2025-086**
(Finesse pairing crypto), FHE at HPCA/ASPLOS (**asplos-2025-029/042**, **hpca-2025-027/037/070**),
**hotchips-2025** (RISC-V SoC for multi-scheme FHE), VLSID SHA-256/quantum-safe hardware. **Quantum
computing** is a substantial recurring stream: ISCA fault-tolerant-QC sync (**isca-2025-077**), MICRO
distributed quantum control (**micro-2025-007**) and QEC leakage speculation (**micro-2025-078**),
HPCA Choco-Q (**hpca-2025-101**) and Clifford extraction, ASPLOS Micro-Blossom MWPM decoder
(**asplos-2025-148**), DAC qubit routing and LLM quantum codegen (**dac-2025-018**). SC adds the
*infrastructure* end: quantum-computing infrastructure and quantum-classical hybrid clusters are a
distinct SC theme (**sc-2025-262** augmenting simulated noisy quantum data, **sc-2025-422** exascale
quantum many-body GW). Entirely outside MLSys scope.

### T9 — Serving scheduling, SLOs & cluster/GPU energy
*MLSys, ISCA, HPCA, ASPLOS, DAC, ISSCC, Hot Chips, SC.* Production LLM serving under SLOs recurs as
its own theme. Shared mechanism: **phase-aware / demand-aware reconfiguration.** MLSys owns software
depth (**mlsys-2025-018** SOLA, **mlsys-2025-023** ThunderServe); ASPLOS adds output-length-aware
scheduling (**asplos-2025-049**); ISCA formalizes phase-disaggregation in hardware; DAC adds
oversubscribed real-time GPU DNN scheduling (**dac-2025-007** DARIS); SC adds pipeline-balanced and
token-aware serving (**sc-2025-018** gLLM, **sc-2025-423** BOER hybrid inference). **Energy is the
axis the new venues sharpen**: HPCA (**hpca-2025-082** DynamoLLM) and now SC make GPU energy a
first-class object — **sc-2025-029** (benchmark-driven GPU energy attribution to functional
units/memory levels), **sc-2025-429** (adaptive uncore scaling to cut power waste), energy-aware
OpenMP portability (**sc-2025-220**), HPC environmental-sustainability assessment — while ISSCC
reports per-chip mJ/frame and TOPS/W directly (**isscc-2025-186** 8.55mJ/frame). Hot Chips presents
"hardware for reasoning-model training and serving."

### T10 — Edge / on-device co-design
*MLSys, ISCA, MICRO, HPCA, DAC, ISSCC, Hot Chips, VLSID.* A distinct low-power frontier — and the
one where the four new circuit/product venues are strongest. Shared mechanism: **co-design at the
ISA/dataflow/algorithm level for a tight energy/SRAM envelope.** Architecture: **isca-2025-047**
(Dadu-Corki robotic manipulation), **micro-2025-069** (RTGS real-time 3DGS SLAM on edge),
**hpca-2025-084** (IRIS ISP-software co-design). The circuit/product venues push into *measured*
edge silicon: **isscc-2025-020** (3.9mW implantable speech decoding), ISSCC via-programmable
low-mask-cost DNN processor (**isscc-2025-180**), MRAM-IMC always-on sensor inference,
**vlsid-2025-038** (407µW speech denoiser), **vlsid-2025-082** (OwlsEye low-light edge segmentation),
**hotchips-2025-033** (Clo-HDnn on-device continual learning), **hotchips-2025-005** (self-powered
energy-harvesting SoC). **3D-Gaussian-Splatting on edge silicon** independently appears at ISCA,
MICRO, HPCA, ISSCC (**isscc-2025-186** IRIS SoC), and Hot Chips (spatial-computing SoC) — a striking
five-venue convergence. **Neuromorphic/SNN and approximate computing** are a VLSID/DAC specialty
(VLSID neuromorphic 6, DAC SNN pruning **dac-2025**).

---

## 4. What differs by venue

**What ISCA / MICRO / HPCA / DAC / ISSCC / VLSID do that MLSys never touches:**
- **Real, and now *measured*, silicon.** ASIC is #1 at ISCA (49), HPCA (48), DAC (171), ISSCC
  (236). ISSCC/VLSID go further than any research venue: papers are *fabricated, measured* chips
  with mW, GS/s, phase-noise, and mJ/frame numbers. MLSys has one ASIC result.
- **The memory subsystem as a first-class object** — cache-replacement policy (**micro-2025-054**),
  coherence, DRAM microarchitecture, NDP/PIM (T3), prefetching. No MLSys analogue.
- **On-chip interconnect and coherence** (**hpca-2025-001**, ISCA NoC) — MLSys uses NVLink, never
  designs a network.
- **Hardware security and reliability** (T7), including **physical/side-channel attacks measured on
  real chips** (ISSCC laser-probing detection, VLSID PUF/CAN) — MLSys is silent.
- **Cryptographic and quantum acceleration** (T8) — no MLSys presence.
- **Microarchitecture reverse-engineering** (**micro-2025-043** Ampere SM) — architecture-only genre.
- **EDA / design automation (DAC, with VLSID/Hot Chips satellites)** — placement, routing, timing,
  IR-drop, RTL simulation, logic synthesis, verification, AI-for-EDA, and end-to-end open-source
  chip generation (**hotchips-2025-028** Basilisk). MLSys does no chip-design tooling.
- **The analog/RF/power/circuit world entirely** (ISSCC, VLSID) — ADCs, PLLs, mm-wave transceivers,
  SerDes, GaN power ICs, energy harvesting. Adjacent to AI silicon (they build the I/O and power
  delivery for AI chips) but a universe MLSys and the systems venues never enter.

**What MLSys / ASPLOS / SC do that the silicon and circuit venues barely touch:**
- **Large-scale distributed *training* systems** — RLHF reallocation (**mlsys-2025-030**),
  pipeline-bubble filling (**mlsys-2025-010**), 1M–2M-token sequence parallelism
  (**mlsys-2025-050/051**), and at the machine scale **SC** (fault-tolerance for LLM training at
  scale, high-dimensional parallelization-strategy optimization, exascale foundation models
  **sc-2025-016**). Silicon venues touch training mainly via interconnect/fault-detection.
- **Production serving software depth** — SLO-constrained per-iteration scheduling, prefix-cache
  reuse, constrained decoding (**mlsys-2025-016** XGrammar), heterogeneous disaggregation. ISCA/HPCA
  touch serving only at hardware-config granularity.
- **Framework-level honesty checks** — **mlsys-2025-007** (KV-compression speedups vanish under real
  PagedAttention+FlashAttention at batch > 4). This "does it survive a real stack" critique is
  MLSys-native; HPCA's analogue is statistical-methodology correctness (**hpca-2025**).

**What SC does that *no other venue* does:**
- **Reproducibility and artifact evaluation as first-class research output** — reproducibility (25)
  and artifact-evaluation (19) are SC's top two technique categories, plus a whole genre of
  "Reproducibility Report for SC25 Paper …" meta-papers (**sc-2025-050**, **sc-2025-069**–**073**).
  No other venue publishes reproduction studies at all.
- **AI *for* science at exascale** — climate/weather foundation models (**sc-2025-016**), plasma/
  N-body/quantum-chemistry, scientific data streaming and compression at supercomputer scale.
- **Honest non-NVIDIA-silicon evaluation** — Cerebras wafer-scale (**sc-2025-430**), superconducting
  full-system modeling (**sc-2025-257**), RISC-V-for-HPC viability (**sc-2025-024**), AMD-GPU exascale
  porting (**sc-2025-225**), RoCE-vs-InfiniBand (**sc-2025-058**). SC is the one venue that routinely
  benchmarks on parts other than an NVIDIA GPU.

**What Hot Chips does that the peer-reviewed venues do not:**
- **Disclose shipping industrial products** — datacenter GPUs, NPUs, CPUs, SmartNICs/IPUs, optical
  I/O, and reasoning-model training/serving hardware, presented by vendors rather than as research.
  The **optical/photonic AI-fabric** story (co-packaged silicon photonics, photonic interposers,
  monolithic optical-I/O SoCs) is proportionally strongest here.

**The through-line:** MLSys optimizes software above fixed NVIDIA silicon; ISCA/MICRO/HPCA build and
secure the silicon below; DAC builds the tools that produce it; **ISSCC/VLSID measure the circuits
those tools tape out**; **Hot Chips ships the product**; **SC runs the whole machine and audits
whether the result reproduces.** The same LLM/attention/quantization/sparsity problems appear at
every layer — each venue attacks them with the degrees of freedom available at its layer.

---

## 5. Cross-cutting observations

**The co-design reflex is universal.** Nearly every high-confidence paper fuses an algorithmic idea
into a datapath/schedule: quantization × Tensor-Core (**mlsys-2025-003**), LUT × bit-serial Tensor
Core (**isca-2025-079**), heterogeneous fixed+float × outlier handling (**hotchips-2025-009**),
sparsity × diffusion accelerator (**hpca-2025-035**, **dac-2025-072**), 3DGS × spatial-computing SoC
(**isscc-2025-186**), sparse fine-tuning × wafer-scale engine (**sc-2025-430**). "Algorithm-hardware
co-design" is the most common phrase in the corpus.

**Recurring baselines and harnesses.** MLSys/serving work benchmarks against a near-standard harness:
**vLLM / SGLang / TensorRT-LLM on A100/H100 with FlashAttention-2**; quantization against
GPTQ/MARLIN; training against Megatron-LM/DeepSpeed/FSDP. The architecture venues compare against
their own prior accelerators *and* against **an A100/H100 GPU as the "to beat" reference** even for
ASIC/FPGA work (**sc-2025-430** Cerebras vs A100; RSN-XNN vs A100/T4). The GPU is the field's
universal yardstick across all ten venues — including at ISSCC/VLSID where a per-chip TOPS/W is then
reported that the GPU-software venues never produce.

**Consistent framings.** *Prefill vs decode as opposite regimes* recurs from MLSys serving into ISCA
phase-disaggregation and SC pipeline balancing. *Hide a slow tier behind a fast one* generalizes from
MLSys PCIe/CPU-offload to architecture-venue NDP/PIM to SC multi-level offloading. *Dynamic/adaptive
over static* appears as adaptive sparsity budgets, SLO-aware scheduling, multi-knob cluster
reconfiguration, and adaptive uncore scaling.

**Tensions.** (1) *Reported vs realized speedup* — **mlsys-2025-007** is the cautionary tale for the
whole quantization/compression cluster; **micro-2025-118** is its silicon analogue (real
compute-in-SRAM is bandwidth-bound); **SC's entire reproducibility apparatus** is the field
institutionalizing this skepticism. (2) *Generality vs peak performance* — programming-model and
generator papers (FlexAttention, TileLink, LEGO, RSN, Basilisk open-EDA) trade peak throughput for
portability/openness. (3) *Accuracy vs efficiency* — negotiated everywhere; "near-lossless" and
explicit quality floors are ubiquitous. (4) *Openness vs performance* — new with Hot Chips/SC:
open-source RISC-V SoCs and open EDA flows (**hotchips-2025-028**) and RISC-V-for-HPC
(**sc-2025-024**) trade peak performance for supply-chain independence.

**Honest gaps.**
- **Non-NVIDIA silicon is under-represented even where it should not be.** MLSys is GPU-monoculture;
  architecture venues build ASIC/CIM but still benchmark against NVIDIA GPUs. **SC is the exception**
  — it routinely evaluates AMD, Cerebras, superconducting, and RISC-V parts — and ISSCC/Hot Chips
  disclose non-NVIDIA product silicon, but TPU still appears only once or twice per venue.
- **Energy/PPA is unevenly measured — but the gap is now visibly closing.** GPU-software papers (most
  of MLSys, much of ASPLOS) still report speedup/throughput and almost never Joules. But **ISSCC/VLSID
  report per-chip mW/mJ/TOPS/W by construction**, and **SC has made GPU energy attribution a research
  topic** (**sc-2025-029**, **sc-2025-429**, **sc-2025-220**). The four new venues materially improve
  the field's energy honesty relative to the six-venue picture.
- **Training numerics / convergence verification at scale is thin** across all venues — systems are
  optimized for throughput/memory far more than their convergence effect is validated (SC's
  fault-tolerance-for-LLM-training work is the partial exception).
- **MoE, hybrid/SSM, diffusion, and multimodal remain frontier** relative to dense-transformer
  attention, though all are clearly growing (diffusion now has dedicated accelerators at HPCA/DAC/Hot
  Chips/ISSCC; MoE recurs at every venue).
- **Cross-venue commensurability is poor.** Baselines, hardware, batch sizes, and sequence lengths
  differ so widely that headline multipliers are directional within a theme, not comparable across
  venues — and the newly added circuit venues (mW/GS/s) and SC (node-hours, reproducibility) use
  metric systems that do not compare to the systems venues at all.

---

## 6. Coverage & confidence — read this before trusting any count

**~1769 papers analyzed across ten venues.** Only MLSys is fully full-text; every other venue is
dominated by abstract-only (`low` confidence) records, and the two circuit venues are almost entirely
so. Per-venue:

| Venue     | Analyzed | high | med | low | Notes |
|-----------|---------:|-----:|----:|----:|-------|
| MLSys     | 61  | 61 | 0 |   0 | Fully full-text; the reliable anchor. |
| ISCA      | 112 | 17 | 0 |  95 | Mostly abstract-only. |
| MICRO     | 47  | 20 | 0 |  27 | 76 title-only excluded (IEEE withholds abstracts). Most under-sampled of the original six. |
| HPCA      | 119 |  8 | 0 | 111 | Almost entirely abstract-only. |
| ASPLOS    | 164 | 14 | 0 | 150 | Mostly abstract-only. |
| DAC       | 443 |  0 | 0 | 443 | Large corpus now fetched, but **zero full-text** — all abstract-only. |
| ISSCC     | 258 |  3 | 0 | 255 | Circuit abstracts; **only 3 full-text.** Metrics-rich but mechanism read from abstracts. |
| Hot Chips | 38  |  4 | 0 |  34 | Industry talks, not papers; abstracts summarize disclosed products, not methods. |
| SC        | 430 | 42 | 2 | 386 | Best-sampled of the new venues (42 full-text); includes reproduction meta-papers. |
| VLSID     | 97  |  4 | 3 |  90 | Small, heterogeneous; mostly abstract-only. |

**What this means, stated plainly:**
- **Only MLSys is fully full-text.** Its 9-theme taxonomy is high-confidence.
- **Abstract-only (`low`) analyses are shallower.** For ISCA/HPCA/ASPLOS/DAC the *distributions*
  (hardware targets, workloads, technique categories) are trustworthy in aggregate, but any individual
  `low` paper's mechanism/metrics are read from an abstract. High-confidence ids were preferred for
  every grounded claim above.
- **ISSCC and VLSID are metrics-rich but full-text-poor.** ISSCC abstracts *do* carry hard numbers
  (mW, GS/s, mJ/frame, TOPS/W) that make the circuit character reliable, but with only 3/258 full-text
  the mechanism details are abstract-level. VLSID is small (97) and 4/97 full-text.
- **Hot Chips is not peer-reviewed research.** Its 38 records summarize *disclosed products*; treat
  them as evidence of what industry shipped/announced, not as method papers. The optical-I/O, NPU, and
  open-RISC-V signals are real but vendor-framed.
- **SC is the best-sampled new venue** (42 full-text) and the most methodologically self-aware — but
  note its counts include ~40 reproduction/artifact meta-papers that are *about* other papers, so
  SC's "technique" histogram over-weights reproducibility relative to novel systems contributions.
- **DAC is now large but flat.** All 443 records are abstract-only; the EDA/design-automation
  character and the LLM-for-chip growth are clear, but no DAC mechanism claim is full-text-grounded.
- **Do not overclaim.** Cross-venue counts mix full-text and abstract-only records of very uneven
  depth across ten venues that use incompatible metric systems (throughput vs mW vs node-hours vs
  reproducibility rate). The qualitative contrasts in §2–§4 are robust; precise numeric shares are
  directional, and ISSCC/VLSID/DAC mechanism-level claims in particular rest on abstracts.
