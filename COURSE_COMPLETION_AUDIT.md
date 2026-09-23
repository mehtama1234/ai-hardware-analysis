# Course completion audit

Audit date: 2026-09-22. This document evaluates the current frontend against
the user-directed brief in `CONFERENCE_COURSE_GOAL.md`. It is not a claim that
the course is complete.

## What current evidence establishes

| Requirement | Current evidence | Result |
| --- | --- | --- |
| Ordered concept-first course | 16 ordered lessons, 59 key concepts, prerequisites, and named previous/next navigation | Established structurally; focused keyboard checks passed. |
| Developed conference routes | 14 routes; 97 themes; 228 subthemes; every theme has a dedicated worked example and explained exercise | Established as course structure. |
| Practice and transfer | Three cross-lesson checkpoints, seven comparisons, 58 bounded walkthroughs, and a six-step paper audit | Present and linked. |
| Plain-language teaching boundary | Every subtheme has application, failure, evidence, and source blocks; editorial triage found no flagged themes | Heuristic evidence only; it does not prove prose quality. |
| Accurate source scope | Each route has a visible evidence status; the table reports bounded record counts and limited guides explicitly | Established for the stated boundaries, not for every factual claim. |
| Internal navigation | Fresh structural check validates 1,863 course links and 52 generated source pages; focused checks cover lesson navigation and mobile table modes. The checker now parses each file once per run while retaining all link assertions. | Established for the checked local links and interactions; not external URLs or visual layout. |
| Arithmetic | `scripts/check_course_learning.py` checks original teaching calculations | Established for the asserted calculations only. |
| External-link reachability | 2026-09-22 scan covered 212 canonical URLs from 53 generated files: 191 responded, 20 publisher/DOI pages restricted automated access, no URL returned 404/410 or another HTTP error, and PETSc failed local DNS. The earlier PCcheck timeout did not recur on this run. The official PETSc page was opened through the web reader. The stale DVFS author-host link was replaced with the university-hosted copy. | Reachability checked at this date; it does not validate citation relevance or future availability. |
| Latest full desktop and mobile browser regression | The latest recorded 2026-09-22 local Playwright checks passed at both 390px and 1280px after the DATE prose pass: homepage entry, contents, 207 anchors, exercises, theme practices, 58 walkthroughs, 52 source pages, keyboard interactions, and horizontal-overflow checks. Later wording edits were prose-only and have not had a fresh browser run. Screenshot artifacts: `/tmp/conference-course-browser-mmfgq9qa/` (390px) and `/tmp/conference-course-browser-wrohneta/` (1280px). | Established for automated local Chromium at that point in the text history; not a fresh post-edit regression, complete visual review, or cross-browser review. |

## What remains unproven or incomplete

Additional browser evidence (2026-09-22): WebKit 26.6 passed the full 390px
regression, then the process exited 143 before finishing desktop. A resumed
1280px run passed the same complete check set. Both widths cover 175 anchor
positions, exercises, keyboard interactions, and 52 source pages with return
menus. Artifacts are `/tmp/conference-course-browser-ah1j8m0j/` (390px) and
`/tmp/conference-course-browser-ejuu9br6/` (1280px). Sampled latency controls
and source menus at both widths, plus the narrow VLSID evidence table, were
visually inspected and readable. This supplies a second local browser engine,
not actual Safari-device testing or comprehensive visual review. The runner
now supports browser selection and resuming a selected viewport width without
reducing the checks performed at that width.

1. Proceedings-wide source review is intentionally incomplete. Route notices
   show the limit: several venues have one focused walkthrough, and the largest
   bounded synthesis covers only a subset of available papers. A teaching route
   is not evidence that every paper’s mechanism and evaluation were reviewed.

Focused source check (2026-09-22): added the PUSHtap walkthrough after
reviewing its primary publication record and arXiv full-text link. The course
now separates the paper’s two access directions, compact placement and
rotation, main/delta update regions, snapshot visibility, controller
coordination, reported benchmark results, and workload boundary. The transfer
and visibility arithmetic is original teaching material; the reported numbers
remain author-reported and were not independently reproduced.

Focused source check (2026-09-22): added the CoServe walkthrough after
checking the primary arXiv record and publication record. It separates known
expert dependencies from runtime routing, then follows request grouping,
eviction, CPU/GPU allocation, service metrics, and the evaluated manufacturing
workload. The queue and memory arithmetic is original teaching material; the
reported throughput remains author-reported and does not establish the same
result for dynamically routed models.

Focused source check (2026-09-22): added the fine-grained DVFS walkthrough
after reviewing the author-hosted paper and publication record. It separates
operator-level frequency selection, slowdown budgets, measured power, elapsed
time, derived energy, and the Ascend-NPU platform boundary. The energy
calculation from rounded power and time values is labeled as derived rather
than reported by the paper; no hardware result was independently reproduced.

Focused source check (2026-09-22): added the BTrace walkthrough after reviewing
the locally extracted author-hosted primary text, especially sections 3.1–3.4
and the evaluation. It separates buffer utilization, event completeness,
recording latency, resize safety, retained history, and production scope. The
reported loss and latency results remain author-reported; the buffer arithmetic
is original teaching material.

Focused source check (2026-09-22): added the High-Throughput SAT Sampling
walkthrough from the locally extracted arXiv manuscript. It separates a valid
assignment, a distinct assignment, unique-valid throughput, and a sampling
distribution guarantee. The GPU throughput figures remain author-reported; the
batch and rare-answer probability calculations are original teaching models.

Focused source check (2026-09-22): added the VLSID pulse-bit walkthrough from
the locally extracted manuscript and evaluation review. It separates numerical
bit sensitivity, output-distribution change, simulated evidence, invalid-pulse
interpolation, and the assumed stop mechanism. The reported simulator results
remain author-reported; no physical fault rate or detector reliability is
claimed.

2. Claim-by-claim factual accuracy across all route prose is not established.
   The editorial script checks selected high-risk distinctions and block shape;
   it cannot validate every attribution, number, unit, baseline, or source
   interpretation. This requires manual primary-source review of each claim
   used as evidence.

3. External-link reachability is not source validation. The scan cannot show
   that a paper page supports the surrounding claim, and automated restrictions
   mean some publisher pages need an interactive or manual check when they are
   next reviewed.

4. The full browser regression is an automated behavior and width check, not a
   complete human visual review. Sampled screenshots cover contents, a long
   practice, selected walkthroughs, a source page, the final exercise, and recent
   opening and memory lesson additions. The frontend check log records the
   precise inspected portions and widths. A completion claim still needs a
   systematic review of long routes and walkthroughs, plus broader device
   coverage beyond the checked local Chromium and WebKit configurations.

## Next work in order

PowerMove source walkthrough (2026-09-22): added an ASPLOS reading that follows
neutral-atom compilation from gate order through qubit placement, movement,
storage/computation zones, collective movement, fidelity, and execution/compiler
evidence. The walkthrough keeps the paper's execution, compilation, and fidelity
results separate from original movement and error-product arithmetic. The course
now contains 48 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 197
anchors and all source-page menus. Broader ASPLOS paper review remains
unfinished.

Mint source walkthrough (2026-09-22): added an ASPLOS reading that follows
distributed tracing from the keep-or-discard sampling problem through common/
variable representation, agent-side reduction, query fidelity, and end-to-end
overhead evidence. The walkthrough keeps the paper's coverage, storage, network,
request-latency, and query-latency results separate from original storage and
rare-event arithmetic. The course now contains 47 paper walkthroughs. Build,
structural, paper, learning, and editorial checks pass, followed by the 390px
browser regression covering 196 anchors and all source-page menus. Broader
ASPLOS paper review remains unfinished.

Cascade source walkthrough (2026-09-22): added an ASPLOS reading that follows
temporal-graph training from event dependencies and node-memory freshness through
topology-aware batching, stabilized-node handling, adaptive update frequency, and
accuracy/performance evidence. The walkthrough keeps the paper's speedup and
validation-loss results separate from original dependency, batch, and error
arithmetic. The course now contains 46 paper walkthroughs. Build, structural,
paper, learning, and editorial checks pass, followed by the 390px browser
regression covering 195 anchors and all source-page menus. Broader ASPLOS paper
review remains unfinished.

PCcheck source walkthrough (2026-09-22): added an ASPLOS reading that follows
ML-training reliability from checkpoint interval and recomputation through
concurrent snapshots, pipelined persistence, coherent recovery points, storage
capacity, and goodput evidence. The walkthrough keeps the reported 3% steady-
state overhead and 2.86× goodput comparison separate from original interval and
pipeline arithmetic. The course now contains 45 paper walkthroughs. Build,
structural, paper, learning, and editorial checks pass, followed by the 390px
browser regression covering 194 anchors and all source-page menus. Broader
ASPLOS paper review remains unfinished.

TAPAS source walkthrough (2026-09-22): added an ASPLOS reading that follows
LLM-serving control from phase-specific performance, temperature, and power
behavior through VM placement, request routing, reconfiguration, emergency
handling, and cluster-scale evidence. The walkthrough keeps the paper's thermal,
power, capacity, throttling, and latency results separate from original control
and capacity arithmetic. The course now contains 44 paper walkthroughs. Build,
structural, paper, learning, and editorial checks pass, followed by the 390px
browser regression covering 193 anchors and all source-page menus. Broader
ASPLOS paper review remains unfinished.

PartIR source walkthrough (2026-09-22): added an ASPLOS reading that follows
distributed model execution from separating sharding intent from model code,
through incremental compiler rewrites, explicit collective communication, and
runtime/compiler evidence. The walkthrough keeps the paper's MFU and compilation
results separate from original tensor, collective, and timing arithmetic. The
course now contains 43 paper walkthroughs. Build, structural, paper, learning,
and editorial checks pass, followed by the 390px browser regression covering 192
anchors and all source-page menus. Broader ASPLOS paper review remains
unfinished.

PipeLLM source walkthrough (2026-09-22): added an ASPLOS reading that follows
confidential GPU transfer from encryption overhead through speculative prediction,
ordered-IV validation, recovery with reordering and no-op padding, asynchronous
decryption, and end-to-end H100 evidence. The walkthrough keeps the paper's
reported overhead reductions and bandwidth observations separate from original
pipeline and recovery arithmetic. The course now contains 42 paper walkthroughs.
Build, structural, paper, learning, and editorial checks pass, followed by the
390px browser regression covering 191 anchors and all source-page menus. Broader
ASPLOS paper review remains unfinished.

Micro Blossom source walkthrough (2026-09-22): added an ASPLOS reading that
follows exact quantum-error decoding from its correction-ready latency boundary
through CPU/FPGA partitioning, graph-local parallelism, local conflict handling,
and stream decoding. The walkthrough keeps the reported 0.8-microsecond FPGA
result and 8× prior comparison separate from original critical-path and
partition arithmetic. The course now contains 41 paper walkthroughs. Build,
structural, paper, learning, and editorial checks pass, followed by the 390px
browser regression covering 190 anchors and all source-page menus. Broader
ASPLOS paper review remains unfinished.

COMET source walkthrough (2026-09-22): added an ASPLOS reading that follows
outlier-aware mixed precision from accuracy risk through W4A4/W4A8 data layout,
conversion, GPU scheduling, and serving-level evidence. The walkthrough keeps
the reported 2.88× kernel comparison and 2.02× end-to-end throughput comparison
separate from original error, traffic, and scheduling arithmetic. The course now
contains 40 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 189
anchors and all source-page menus. Broader ASPLOS paper review remains
unfinished.

vAttention source walkthrough (2026-09-22): added an ASPLOS reading that follows
dynamic KV-cache growth from fragmentation through the separation of virtual
address layout and physical page commitment. The walkthrough explains why
PagedAttention can simplify allocation while making kernels and runtimes more
complex, then bounds the paper's phase-specific decode, prefill, offline, and
online results. It keeps the reported speedups and latency reductions separate
from original capacity and address-mapping arithmetic. The course now contains
39 paper walkthroughs. Build, structural, paper, learning, and editorial checks
pass, followed by the 390px browser regression covering 188 anchors and all
source-page menus. Broader ASPLOS paper review remains unfinished.

CIPHERMATCH source walkthrough (2026-09-22): added an ASPLOS reading that follows
encrypted representation through packed, addition-only exact matching, NAND
in-flash bit-serial addition, and the boundary between real CPU measurements and
simulated hardware results. The walkthrough keeps the paper's reported
20.7×–62.2×, 76.6×–216.0×, and 250.1×–295.1× results separate from original
movement and break-even arithmetic. The course now contains 38 paper
walkthroughs. Build, structural, paper, learning, and editorial checks pass,
followed by the 390px browser regression covering 187 anchors and all source-page
menus. Broader ASPLOS paper review remains unfinished.

DynamoLLM source walkthrough (2026-09-22): added a second focused HPCA reading
for request-specific prefill/decode behavior, TTFT and TBT service promises,
energy/carbon/cost accounting, energy-performance profiles, hierarchical
control, reconfiguration overhead, and the paper's cluster-level evaluation.
The walkthrough keeps the paper's reported 52% energy, 38% operational-carbon,
and 61% customer-cost results separate from original teaching arithmetic and
does not claim independent reproduction. The course now contains 31 paper
walkthroughs. Build, structural, paper, learning, and editorial checks pass,
followed by the 390px browser regression covering 180 anchors and all
source-page menus. Broader HPCA paper review remains unfinished.

VQ-LLM source walkthrough (2026-09-22): added a third focused HPCA reading
for vector-quantization representation, codebook hotness, register/shared/global
placement, occupancy and bank conflicts, codebook-centered dataflow, register
fusion, adaptive kernel generation, and end-to-end inference evidence. The
walkthrough keeps the paper's reported kernel and end-to-end results separate
from original traffic arithmetic and does not claim independent reproduction.
The course now contains 32 paper walkthroughs. Build, structural, paper,
learning, and editorial checks pass, followed by the 390px browser regression
covering 181 anchors and all source-page menus. Broader HPCA paper review
remains unfinished.

EXION source walkthrough (2026-09-22): added a fourth focused HPCA reading
for diffusion iteration structure, inter- and intra-iteration output sparsity,
FFN-Reuse, eager prediction, ConMerge compaction, output-quality checks, and
the simulator/RTL/GPU evidence boundary. The walkthrough keeps the paper's
reported performance and energy ranges separate from original sparsity and
cycle arithmetic and does not claim independent reproduction. The course now
contains 33 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 182
anchors and all source-page menus. Broader HPCA paper review remains
unfinished.

IRIS source walkthrough (2026-09-22): added a fifth focused HPCA reading for
region saliency, mixed-resolution capture, ISP/backend cooperation, task-
specific localization and classification paths, and the paper's
measured-versus-modeled evidence boundary. The walkthrough keeps average
latency, tail latency, energy, accuracy, and software-only comparisons as
separate claims and does not claim independent reproduction. The course now
contains 34 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 183
anchors and all source-page menus. Broader HPCA paper review remains
unfinished.

Choco-Q source walkthrough (2026-09-22): added a sixth focused HPCA reading
for constrained binary optimization, legal versus optimal outputs, commute-
Hamiltonian constraint preservation, circuit serialization, equivalent gate
decomposition, variable elimination, and NISQ-scale evaluation. The
walkthrough keeps in-constraints rate, success rate, approximation gap, and
latency as separate claims and does not claim independent reproduction. The
course now contains 35 paper walkthroughs. Build, structural, paper, learning,
and editorial checks pass, followed by the 390px browser regression covering
184 anchors and all source-page menus. Six of the seven locally source-backed
HPCA papers now have full walkthroughs; MVE remains source-reviewed but does
not yet have a full walkthrough, and the broader proceedings review remains
unfinished.

MVE source walkthrough (2026-09-22): added a seventh focused HPCA reading for
multidimensional logical registers, strided and random movement, dimension-
level masking, cache-mode transitions, compiler scheduling, and the paper's
measured-versus-modeled evidence boundary. The walkthrough keeps lane
utilization, transition cost, performance, energy, and area as separate
quantities and does not claim independent reproduction. The course now
contains 36 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 185
anchors and all source-page menus. All seven locally source-backed HPCA papers
now have full walkthroughs; broader HPCA proceedings review remains
unfinished.

Teola source walkthrough (2026-09-22): added a fifth focused ASPLOS reading
for whole-application critical paths, primitive-level workflow graphs, graph
parallelization and pipelining, topology-aware batching, and end-to-end
evaluation limits. The walkthrough keeps per-primitive speed, application
latency, queueing, communication, and engine-coupling costs separate and does
not claim independent reproduction. The course now contains 37 paper
walkthroughs. Build, structural, paper, learning, and editorial checks pass,
followed by the 390px browser regression covering 186 anchors and all
source-page menus. Broader ASPLOS paper review remains unfinished.

HydraServe source walkthrough (2026-09-22): added a third focused NSDI reading
for HydraServe's cold-start dependency chain, pipeline workers, stage overlap,
network-aware placement, worker consolidation, and SLO evaluation. The
walkthrough keeps TTFT, TPOT, temporary-resource cost, and production/testbed
boundaries separate and does not claim independent reproduction. The course now
contains 30 paper walkthroughs. Build, structural, paper, learning, and
editorial checks pass, followed by the 390px browser regression covering 179
anchors and all source-page menus. Broader NSDI paper review remains unfinished.

Tigon source walkthrough (2026-09-22): added a sixth focused OSDI reading for
Tigon's cross-host active tuple (CAT) working set, CXL placement, limited
hardware-coherent region, transaction and durability boundaries, and emulated
CXL-pod evaluation. The walkthrough keeps the paper's latency, bandwidth,
baseline, and throughput conditions attached to its claims and does not claim
independent reproduction. The course now contains 29 paper walkthroughs.
Build, structural, paper, learning, and editorial checks pass, followed by the
390px browser regression covering 178 anchors and all source-page menus. Broader
OSDI paper review remains unfinished.

Mirage source walkthrough (2026-09-22): added a fifth focused OSDI reading for
Mirage's multi-level GPU graph, abstract-expression pruning, probabilistic
equivalence checking, generated-code preparation cost, and benchmark boundary.
The walkthrough explicitly preserves the verifier's LAX/operator limits and
the paper's batch-size and GPU-dependent results; it does not claim independent
reproduction. The course now contains 28 paper walkthroughs. Build, structural,
paper, learning, and editorial checks pass, followed by the 390px browser
regression covering 177 anchors and all source-page menus. Broader OSDI paper
review remains unfinished.

MiLo source walkthrough (2026-09-22): added a fifth focused MLSys reading for
MiLo's quantize-then-compensate method. The walkthrough separates three-bit
storage from output quality, low-rank correction from exact restoration,
offline preparation from serving latency, and the fused INT3 kernel from the
paper's A100 end-to-end comparison. It preserves the paper-reported boundary
and does not claim independent reproduction. The course now contains 27 paper
walkthroughs; build, structural, learning, and editorial checks pass. Broader
MLSys paper review remains unfinished.

Final MiLo rebuild verification (2026-09-22): the regenerated course contains
16 lessons, 52 concepts, 1,376 links, 27 walkthroughs, and 52 source pages.
The complete local structural, walkthrough, learning, and editorial checks
pass. Chromium at 390px passed 176 anchor positions, exercises, keyboard
interaction, source-page return menus, and overflow checks. Artifact:
`/tmp/conference-course-browser-bl62wbuu/`. This remains automated narrow-width
evidence, not a complete human visual review.

MLSys route coverage notice (2026-09-22): clarified that the route has four
focused learner walkthroughs—FlashInfer, QServe, SOLA, and Photon—within the
broader synthesis. It now reconciles the 61 extracted-source records with the
56 full-text catalog entries and five additional text-bearing acquisition
records, while stating that source availability is not independent reproduction.
Added an editorial regression check. This improves the evidence boundary for
the strongest existing route; broader MLSys paper walkthroughs and full-corpus
claim review remain unfinished.

Small-sample route coverage notices (2026-09-22): clarified VLSID, ISSCC,
FCCM, and ICCAD. VLSID now distinguishes the full TimeFloats walkthrough from
two other locally reviewed papers and its larger abstract/title sample. ISSCC
now distinguishes ConvFormer from its discovery-only population. FCCM marks
the Banked Memories walkthrough as based on an externally inspected manuscript
that is not part of local PDF coverage. ICCAD marks RSizing as one separately
inspected walkthrough within a structured-abstract discovery audit. Added
editorial regression checks. Build, structural, learning, and editorial checks
passed; the narrow 390px Chromium regression passed all 175 anchor positions,
exercises, source pages, keyboard checks, and overflow checks. This improves
scope clarity but does not complete any of the four proceedings reviews.

DAC and DATE route coverage notices (2026-09-22): made the one full GSIM
walkthrough explicit within DAC's 32 source-backed records and the one full
CorrectBench walkthrough explicit within DATE's 15 source-backed records.
Both notices now distinguish those records from their respective
discovery-level populations and retain the no-independent-reproduction
boundary. Added editorial regression checks. Build, structural, learning, and
editorial checks passed; one narrow 390px browser regression passed all 175
anchor positions, exercises, source pages, keyboard checks, and overflow
checks. This clarifies scope but does not complete either proceedings review.

SC route coverage notice (2026-09-22): made the one full cuSZ-Hi walkthrough
explicit within the reconciled 433-record inventory. The notice now states
that 119 records have extracted text and reviews, while the remaining 314 are
312 abstract-only and two title-only records; the three failed PDF downloads
remain identified within the abstract count. Added an editorial regression
check. Build, structural, learning, and editorial checks passed; the narrow
390px browser regression passed all 175 anchor positions, exercises, source
pages, keyboard checks, and overflow checks. This improves coverage clarity,
not paper-wide verification.

HPCA route coverage notice (2026-09-22): clarified that the route has one
full LEGO walkthrough within seven source-backed reviews across 121 records.
The remaining 114 records are not equivalent evidence, and the four failed
acquisitions, 108 abstract records, and 110 unusable-PDF records are explicitly
non-additive because they overlap. Added an editorial regression check. Build,
structural, learning, and editorial checks passed; the narrow 390px browser
regression passed all 175 anchor positions, exercises, source pages, keyboard
checks, and overflow checks. This resolves the learner-facing count ambiguity,
not the broader HPCA review gap.

ISCA route coverage notice (2026-09-22): tightened the learner-facing status
to distinguish the two full walkthroughs, LUT Tensor Core and Oaken, from the
17 source-backed papers in the local synthesis. It now states that the other
95 records have abstracts and 23 have no source text, while keeping results
author-reported. Added an editorial regression check. Build, structural,
learning, and editorial checks passed; the narrow 390px browser regression
passed all 175 anchor positions, exercises, source pages, keyboard checks, and
overflow checks. This clarifies coverage without expanding the underlying
paper review.

MICRO route coverage notice (2026-09-22): tightened the learner-facing status
to distinguish the two full walkthroughs, TRRIP and Pimba, from the 20 total
source-backed evaluation reviews. It now states that the other 103 records
remain abstract/title-only and keeps all results author-reported. Added an
editorial regression check. Build, structural, learning, and editorial checks
passed; the narrow 390px browser regression passed all 175 anchor positions,
exercises, source pages, keyboard checks, and overflow checks. This improves
coverage honesty but does not expand the underlying paper review.

Pimba source review (2026-09-22): checked the final MICRO paper's generalized
state-update operation, two-bank shared SPU, MX8 and stochastic-rounding
choice, GPU/PIM division of work, dependency bubbles, baselines, and simulator
method. The reported 4.1×/2.1× maxima remain separate from the 1.9×/1.4×
averages and the 2.2× energy comparison. The walkthrough correctly labels the
40-HBM2E, Ramulator2-based results as modeled and the area/power results as
scaled RTL synthesis rather than measured Pimba silicon. Added an editorial
regression check. This is one MICRO paper review, not broader MICRO coverage.

TRRIP source review (2026-09-22): checked the author manuscript's compiler,
loader/OS page-attribute handoff, replacement policy, Sniper configuration,
proxy benchmarks, fixed 400-million-instruction comparison, and omitted
wrong-path execution/prefetching. The course correctly explains that hot means
expected code use rather than temperature, and that a profile is a prediction
rather than a capacity reservation. It keeps the 3.9% geometric-mean result
attached to the SRRIP baseline and simulated PGO workloads. Added an editorial
regression check. This is one MICRO paper review, not broader MICRO coverage.

LUT Tensor Core source review (2026-09-22): checked the arXiv manuscript's
software table preparation and fusion, symmetric weight reinterpretation,
bit-serial lookup, elongated tiling, LMMA instructions, compiler path, and
evaluation stages. The walkthrough's exact examples remain explicitly
original. The source separates 28-nm synthesis/PPA estimates, Accel-Sim
kernel comparisons, and tile-based model simulation; the course does not turn
those into manufactured-chip measurements. Added an editorial regression
check. This is one ISCA paper review, not broader ISCA coverage.

Oaken source review (2026-09-22): checked the final author-hosted ISCA paper
against its abstract, quantization sections, hardware layout, and evaluation
method. The walkthrough correctly keeps the 1.58× A100 statement separate from
the 1.79× vLLM and 1.58× QServe comparisons, and keeps the 0.87% FP16,
0.54% KVQuant, and 0.32% KIVI quality references separate. The source confirms
that end-to-end Oaken results come from an extended LPU hardware simulator and
that area comes from 28-nm synthesis, not fabricated silicon. Added an
editorial regression check. This is one ISCA paper review, not broader ISCA
coverage.

TimeFloats source recheck (2026-09-22): compared the walkthrough with the
August 2024 arXiv preprint, including the five-stage floating-point path,
15-nm synthesis/HSPICE evidence, Table I, and section IV-B. The source itself
lists 21 fJ and 1.23 pJ in Table I but gives 2.421 pJ and 1.32 pJ in the
prose; the stated 5.8 pJ total does not reconcile with either complete set of
listed components. The course correctly leaves this unresolved and does not
turn the 22.1 TOPS/W model result into measured-chip or full-training energy.
Added an editorial regression check. This is one VLSID preprint review, not
broader VLSID coverage.

CorrectBench source and terminology review (2026-09-22): checked the DATE
manuscript’s scenario-based validator, 70%-wrong rule, greater-than-25%
whole-design override, repair loop, and Eval2 definition. The walkthrough
already preserved the key evidence limits; it now defines a scenario as one
concrete input sequence and expected observation before using the thresholds.
Build, structural, learning, and editorial checks passed. The revised opening
was inspected at 390px and readable without overflow. This is one DATE paper
review, not broader DATE coverage.

GSIM source review (2026-09-22): checked the manuscript’s model of simulator
work, three optimization levels, evaluation setup, correctness outcomes, and
runtime comparisons. The walkthrough now states the selected-design result
that GSIM and Verilator successfully simulate XiangShan while ESSENT and
Arcilator fail on some designs, and keeps that result separate from speed and
from physical-chip claims. Build, structural, learning, and editorial checks
passed. The revised paragraph was inspected at 390px; a desktop capture was
not completed in this focused pass. This is one DAC paper review, not broader
DAC coverage.

ISSCC ConvFormer source review (2026-09-22): checked the three-page digest
against the walkthrough’s attention, layer-fusion, pruning, fabricated-28-nm
chip, workload, and comparison statements. The lesson correctly treats the
digest’s chip and model results as author-reported, keeps prior accelerators'
peak-efficiency assumptions visible, and separates changed arithmetic from
answer-quality evidence. Added an editorial regression check for these
boundaries. This is one digest review, not broader ISSCC coverage.

FCCM Banked Memories source review (2026-09-22): checked the author manuscript
sections on bank mapping, issue control, arbitration, latency, and results.
The walkthrough correctly separates its four-bank teaching model from the
paper’s 16-bank design, lower-address-bit mapping, and reported control and
memory pipeline delays. The paper’s broader multi-architecture benchmark
claims remain outside this focused lesson. Existing structure and editorial
checks pass; this is one FCCM manuscript review, not conference-wide coverage.

FCCM metadata boundary (2026-09-22): checked the official accepted-paper list,
program, DOI record, and available abstract for High Throughput Matrix
Transposition on HBM-Enabled FPGAs. The full paper was not available in the
review environment, so its layout and performance details remain a reading
lead rather than a source-adjudicated walkthrough. The FCCM route now exposes
that distinction instead of treating the abstract as full-text evidence.

NSDI route notice update (2026-09-22): the learner-facing status now says
that FastServe and Di-PS are based on final USENIX papers, while selected
theme discussions and the wider 150-paper synthesis remain abstract-based or
otherwise bounded. It explicitly says the two focused reviews do not make the
route a paper-by-paper review. Build, structural, learning, and editorial
checks passed; focused 390px/1280px screenshots were inspected and readable.

Di-PS source review (2026-09-22): checked the final NSDI PDF’s abstract and
sections covering the two-stage training setting, centralized parameter
server, pseudo-gradient penalty, failure handling, controlled experiments,
and production report. The walkthrough’s two speed ranges and the two forms
of the roughly six-percent overhead statement are kept as separate
denominators. Added an editorial regression check for those distinctions.
No reader-facing numerical claim was broadened; this is one additional
source review, not completion of NSDI coverage.

FastServe source and terminology review (2026-09-22): checked the final USENIX
paper text for the prefill/decoding distinction, key–value-cache pressure,
skip-join queue placement, starvation prevention, and the evaluation metric.
The walkthrough now defines prefill, decoding, and the saved keys and values
before using those terms, and explains P95 as a separate slow-request measure.
The A100/model/workload/baseline boundary remains attached to the reported
result; no new headline number was added. Build, structural, learning, and
editorial checks passed. Focused 390px/1280px captures of the walkthrough
were generated and showed no document overflow. This is one paper review,
not completion of the NSDI corpus review.

Full regression after capstone update (2026-09-22): Chromium 153 passed at
390px and 1280px, including 175 anchor positions, keyboard entry, all core
exercises, theme practices, 26 walkthroughs, 52 source pages and return menus,
and overflow checks. Screenshots are in
`/tmp/conference-course-browser-i6332vcs/`. This verifies the current local
frontend behavior; it does not complete the source-accuracy or human visual
review.

Abstract-only capstone path (2026-09-22): added a bounded three-note exercise
for routes whose records provide only an abstract. It asks learners to state
the abstract's problem and proposed change, name one evaluation fact that is
unknown, and avoid turning “improves performance” into a speedup or baseline.
The full six-step audit still requires a paper. Build, structural, learning,
and editorial checks passed. Focused Chromium checks passed at 390px and
1280px after narrowing the browser test to the rubric details element; the
expanded abstract-only panel was inspected on mobile and had no overflow.
This improves transfer instruction and does not promote abstract evidence to
full-paper evidence.

OSDI coverage notice review (2026-09-22): changed the route notice to say
which four featured walkthroughs have local primary-source evidence maps and
which remaining records still need manual confirmation. The notice now also
states that reported measurements were not independently reproduced. Build,
structural, learning, and editorial checks passed; a focused responsive check
at 390px and 1280px found no document overflow. This improves the evidence
boundary shown to learners but does not expand OSDI paper coverage.

Opening cross-conference explanation (2026-09-22): added one connected example
of smaller stored numbers to explain concepts, themes, and subthemes. The
opening distinguishes course reading groups from official venue categories
and comparing causes from comparing numerical results. Build, structural,
learning, and editorial checks passed. Focused orientation/capstone browser
checks passed at 390px and 1280px. Desktop panel and three normally scrolled
mobile paragraph views were inspected; this is not a full-course visual audit
or an expansion of reviewed paper coverage.

QServe terminology review (2026-09-22): defined weights, activations, and stored
attention history before introducing W4A8KV4. Defined the output-channel
grouping at the point where its shared scale is used. The numerical results
and source limits are unchanged. Build and structural checks passed; editorial
and learning checks passed after updating old exact-wording assertions.
Focused 390px/1280px screenshots of both explanations were inspected and
readable without document overflow. This is a terminology pass, not an
additional empirical or source-coverage claim.

Coverage-notice language review (2026-09-22): replaced internal adjudication
terminology in ISCA, HPCA, MICRO, and VLSID route notices and coverage labels
with descriptions of source text and written evaluation reviews. Checked the
unchanged review counts against their local syntheses. HPCA's overlapping
source categories remain explicitly non-additive. No paper-review coverage
was expanded. Build, learning, structural, and editorial checks passed.
Focused mobile/desktop checks covered all four labels and notices; HPCA's
notice and coverage row were visually inspected at both widths and readable.

MapReduce source review (2026-09-22): checked the historical OSDI 2004 paper's
sections 3.3 and 3.6. The core distributed-work lesson now separates inaccessible
worker-local intermediate files from completed final output in shared storage,
and makes the described implementation's coordinator-failure abort explicit.
The deterministic-task condition remains separate from backup attempts for
slow workers. Updated old exact-wording tests and added checks for the stated
failure boundaries. Build, learning, structural, and editorial checks passed.
Focused mobile/desktop screenshots of both paragraphs were inspected and
readable. This checks one historical teaching connection, not all distributed
systems sources or current implementations.

Detection-example arithmetic review (2026-09-22): inspected both privacy-lesson
examples and retained their correct prose. Expanded the learning check to
derive all four outcomes from each population and the stated conditional
rates, including correctly ignored ordinary events. The outcomes sum to
10,000 and 20,000 respectively. The checks explicitly distinguish false
alarms divided by ordinary events from false alarms divided by all alerts.
Learning and structural checks passed. No reader-facing content changed, so
no fresh rendering claim is made. This verifies the invented arithmetic,
not a detector's measured accuracy or the lesson's separate paper claims.

Timing-unit review (2026-09-22): the FCCM comparison now defines hertz and
megahertz and derives nanoseconds per cycle before multiplying by cycle count.
The existing 40/60 ns comparison and 150 MHz tie remain unchanged, with
exact-rational unit-conversion checks. Build, learning, structural, and
editorial checks passed. Both revised paragraphs were inspected at 390px and
1280px and readable without document overflow. These remain invented designs,
not new clock-rate claims for the cited paper.

QServe primary-source check (2026-09-22): inspected final conference PDF pages
4–7 for progressive quantization, protective range, SmoothAttention, and
weight reordering. Added the paper's concrete 120-to-128 reconstruction example
and recalculated it. The walkthrough distinguishes intermediate range safety
from answer quality and now links pages 5 and 7, rather than citing only the
introduction for mechanism details. The arithmetic test does not verify the
general range proof or reproduce the system. Build, learning, structural, and
editorial checks passed.

Walkthrough prose-structure review (2026-09-22): inspected the six longest
walkthrough paragraphs and split them where setup, mechanism, or reported
results change subject. Affected QServe, BlitzScale, Banked Memories, EMT,
Pimba, and FlashInfer. Verified that all six original passages retain their
exact words and order across seven new breaks. Build, learning, structural,
and editorial checks passed. This improves reading structure; it is not a
new verification of the unchanged paper claims.

Subtheme alignment review (2026-09-22): rewrote the two SC measurement
subtheme notes with concrete 12-second recording and 2/10/18-second prediction
examples. They now explain the failure mechanism directly instead of only
instructing the reader to compare measurements. Their evidence blocks retain
the previously checked MT4G and CGSim limits and link to the primary sections.
Build, arithmetic, structural, and editorial checks passed. This completes
the selected two-note review, not an audit of all 228 subtheme explanations.

Training-workflow teaching check (2026-09-22): added an unequal-partition
example showing why averaging worker means can change the intended update.
Three one-example workers and one nine-example worker yield a worker-mean
average of 4 but an equal-example average of 8. The lesson states the shared
model-version and equal-weight assumptions; it does not impose that rule on
all training algorithms. Exact-fraction tests check the weighted calculation
against an explicit twelve-value list. Build, arithmetic, structural, and
editorial checks passed. This is original teaching arithmetic, not a finding
about any named training system.

Final-exercise review (2026-09-22): step four now asks whether compared systems
used the same inputs, quality requirement, and included costs, and whether a
number represents one run or a repeated-run summary. Missing variation is
recorded as missing evidence. The rubric and worked explanation distinguish
unequal work from uncertain timing, without inventing repeated measurements.
Build, arithmetic, structural, and editorial checks passed. Focused mobile
and desktop checks verified note entry and keyboard rubric access; all four
prompt/explanation screenshots were inspected and readable. This improves
the reader's audit task, not the evidence available for any paper.

Growth-notation correction (2026-09-22): the O(1) lookup entry now explains a
fixed bound with respect to a named size, rather than requiring exactly equal
costs. The BlitzScale walkthrough distinguishes its fixed host-copy rule from
the general notation and uses an original storage example to separate worker
count from model count. The example excludes other memory and traffic and is
not a paper measurement. Build, learning, structural, and editorial checks
passed; focused 390px/1280px definition/example screenshots were inspected
and readable, with no document-width overflow.

Concept-lookup review (2026-09-22): replaced abstract definitions of bottleneck,
checkpoint, and quorum with concrete examples. The quorum entry separates
three-of-five overlap from the protocol rules needed to make it useful, and
does not define all quorums as majorities. An exhaustive set check verifies
the overlap example. Build, arithmetic, structural, and editorial checks
passed after updating a stale exact-wording assertion. Focused 390px/1280px
checks verified the three entries and keyboard links to their lessons; all
six entry screenshots were inspected and readable. This is a selected glossary
review, not proof that every technical term in the course is sufficiently clear.

Cross-conference teaching review (2026-09-22): the representation comparison
now keeps stored sizes and decoding/copying work fixed while varying only
connection speed. It derives the rate at which compression stops saving
elapsed time, while explicitly excluding earlier creation of the stored forms.
Exact-fraction checks validate all three rates and the tie. Build, arithmetic,
structural, and editorial checks passed. Focused 390px/1280px browser checks
covered the example and keyboard-opened answer; all four screenshots were
inspected. These are original teaching assumptions, not new paper claims.

MT4G primary-source review (2026-09-22): checked section V against the local
paper text. The course distinguishes tests blocked by virtualized access from
the specifically reported incorrect P6000 sharing indication. It also names
the missing-reference limit on some latency comparisons and identifies the
SC Workshops venue. Updated the local review to retain the paper's specific
exception rather than treating every problematic case as abstention. Added
and verified the direct source anchor. Build, arithmetic, structural, and
editorial checks passed; these checks do not independently verify the tool.

CGSim primary-source review (2026-09-22): read the author manuscript's
calibration section against the local extracted text. The SC lesson now names
the historical period and the site-specific processor-speed tuning. It states
that section 4.2 does not describe a held-out job set, without claiming that no
unreported test occurred. It separates the proposed frozen-settings check
from the paper's experiments and identifies the SC Workshops venue. Added a
direct section citation and updated the local evaluation review. Build,
arithmetic, structural, and editorial checks passed. This narrows one source
claim; it does not complete the course-wide claim review.

SC teaching addition (2026-09-22): the measurement lesson now derives why
averaging worker times before calculating job completion gives the wrong
answer when the job waits for both workers. Three original paired-delay
models preserve each worker's 2/18-second distribution and 10-second mean,
but yield job means of 14, 10, and 18 seconds. Exact-fraction checks enumerate
the cases. The exercise asks the reader to derive the third case. These are
not new claims about CGSim. Build, learning, structural, and editorial checks
passed; focused mobile/desktop keyboard and width checks passed, with all
four new paragraph screenshots inspected. Broader source review remains open.

SC inventory reconciliation (2026-09-22): checked all 433 unique corpus records
against the local text filenames and acquisition audit. The three failed PDF
acquisitions have abstracts, so the complete partition is 119 local texts,
312 abstract-only records, and two title-only records. The older audit's 309
abstract-only count excludes those three failed acquisitions. The route,
coverage table, and synthesis now state the reconciled counts; a dedicated
`scripts/check_sc_course_coverage.py` checks the partition and frontend counts.
This resolves an inventory discrepancy, not the remaining source-review work.
The route also explains why abstracts cannot support a detailed experiment review.

Foundational source check (2026-09-22): the privacy lesson now distinguishes
encrypted contents from visible message sizes, using an original two-response
example and a checked padding cost. RFC 8446 appendix E.3 was inspected for
the length/timing exposure and limits of padding; the lesson links that exact
section. Equalized sizes establish only the stated observation boundary, not
protection against timing, message-count, or destination observations.

Source-alignment correction (2026-09-22): the core correctness lesson now names
PMVerify's robustness property explicitly, matching the detailed walkthrough
and the author paper's introduction (pages 2–3). It no longer describes the
tool as a general checker of the application's rule. The benchmark outcomes
retain their robust/violation/unknown scope, with regression assertions for
both the definition and the limit of the claim.

Foundational teaching check (2026-09-22): added an early-arrival/hold example
to the physical-design lesson, complementing its late-arrival calculation.
Checked the distinction against MIT 6.004's Sequential Logic annotated slides
(D-register timing and timing in a single-clock system). The numerical example
is original and assumes simultaneous clock arrival and a fixed added delay;
it explicitly requires separate earliest/latest checks for real delay ranges.
Exact-rational tests cover the missed hold interval and the hypothetical repair.

Foundational teaching check (2026-09-22): the compiler lesson now traces an
overlapping-storage example through two passes, incorrect left-to-right fusion,
and valid right-to-left fusion under its stated assumptions. Executable checks
compare all four final storage positions. The example establishes why the
last use of an input constrains order; it does not prescribe reverse traversal
for arbitrary overlapping arrays or programs with other observable effects.

Foundational correction (2026-09-22): fixed the signed error in the skipping
lesson. Omitting contributions +0.10 and −0.08 lowers the result by 0.02;
the example now shows original 1.02, retained 1, signed error −0.02, and the
separate absolute-error bound. Exact-fraction assertions check that distinction.
Split the SparseTransX, Radius, and TASD discussion into separate paragraphs
without changing their reported results or treating them as a common benchmark.

Foundational teaching check (2026-09-22): the pipeline lesson now demonstrates
an attainable shared-processor schedule, including startup: ten images require
82 ms with 5-ms resize/3-ms classify work, or 52 ms with 2-ms resize/3-ms classify
work. Both retain the separate 2-ms reader. Event-sequence assertions verify
all ten completion times. The exercise contrasts these resource-sharing
assumptions with the separate-stage case instead of inferring finite-batch
time from a steady completion rate.

Foundational correction (2026-09-22): removed the queue lesson's overly broad
claim that arrivals strictly below capacity are necessary for stability in its
simple model. Explicit deterministic schedules now distinguish no waiting at
exactly matched rates, persistent but bounded waiting after a one-time delay,
and recovery when arrivals leave spare service time. Regression checks simulate
each arrival/start/finish sequence. No general claim about random-arrival queue
stability is inferred from these finite teaching schedules.

Foundational teaching check (2026-09-22): the memory lesson now derives the
independent-read requirement from bytes per read and read delay. Its original
64-byte/100-ns model gives 0.64 GB/s for one read in flight, 5.12 GB/s for eight,
and a necessary average of 100 reads in flight to sustain 64 GB/s. Exact-rational
checks cover the arithmetic. The prose keeps fixed-delay, independence,
hardware-service, and startup limits explicit; these are model bounds, not
measured hardware rates.

Focused source check (2026-09-22): VLSID pulse-bit manuscript
arXiv:2405.05511v1, sections 3.2 and 4.1, discloses invalid pulses, graph values
filled from neighboring points, and assumed detection/stopping. Themes 1 and 4
now retain those distinctions and propose a separate safeguard test. This
narrows the graph's evidentiary scope; it does not verify the safeguard or
resolve other claims in the study. Added a direct versioned source link.

Focused source check (2026-09-22): DATE theme 1 now separates valid answers,
distinct answers, and their selection probabilities. Inspected manuscript
arXiv:2502.08673v1 in `conferences/date-2025/text/date-2025-024.txt`, especially
lines 610–637, 795–872, and 981–988: retained answers are valid/nonredundant,
the throughput measure counts unique valid solutions, and related work names
UNIGEN3's approximate-uniformity guarantee. Added a direct primary-source link
and an explicitly invented two-answer example, with a checked 36.6% chance of
missing the rare answer in 100 independent draws. This does not attribute that
bias to the paper or establish its sampler's selection distribution.

Focused source check (2026-09-22): inspected RSizing pages 5–7 directly from
the author-hosted PDF. Section IV.B and table IV distinguish one PVTSizing run
per target from one RSizing run producing several alternatives. ICCAD theme 4
now explains this output boundary using the amplifier T1 entries and preserves
their different sampled passing rates. The walkthrough now carries the same
distinction and a direct page-7 citation. No runtime or yield experiment was
reproduced; no broader ICCAD source-coverage claim follows from this check.

Focused source check (2026-09-22): FCCM theme 2 now works through the 32-by-32
transpose in manuscript arXiv:2503.24132v1, section V, table II, comparing its
two 16-bank columns. Read/write/total counts were checked directly, and the
derived percentage calculations have regression assertions. The text separates
the paper's bank-selection change from the invented padding example and does
not label these reported counts as independently measured board results. This
closes that specific attribution and arithmetic check, not the route-wide
source audit or proceedings review.

1. Read and verify primary sources for the routes with the thinnest evidence:
   FCCM, ICCAD, ISSCC, VLSID, DATE, DAC, and SC. Preserve the current limits
   until a source has actually been inspected.
2. Review paper-backed statements route by route, recording source location,
   workload, comparison, unit, and evidence type. Correct or narrow any claim
   that lacks direct support.
3. Perform a final prose and visual review across the complete reading sequence,
   including long routes and walkthroughs at desktop and narrow widths. Remove
   unexplained terms, repeated templates, vague comparisons, and conclusions
   that outrun their stated evidence.

The active goal must remain open until these gaps are resolved or the user
changes its required scope.

Focused source check (2026-09-22): inspected the local ISSCC 2025 digest for
record 038, ConvFormer, line by line across the mechanism and measurement
sections. The adjudication now points to lines 19–37 for the workload and
three stated design problems, lines 39–57 for hybrid attention, reuse, and
pruning, lines 74–108 for the tile and fusion limits, and lines 131–143 for
the fabricated-chip operating range, named models, Cityscapes workload,
reported results, and peak-efficiency assumption in prior-system comparisons.
The course keeps the 0.22 μJ/token and speed/energy figures as author-reported
measurements, distinguishes them from the original teaching arithmetic, and
does not generalize one digest to all ISSCC papers. This strengthens one
paper-level attribution; the 257 other ISSCC records remain discovery-only.

Editorial pass (2026-09-22): tightened HPCA route and walkthrough wording
where “useful,” “efficient,” or “better” could hide the condition being
described. The prose now names supplied independent rows, recurring table
costs, implementable data arrival and lifetime requirements, request counts,
consumer timing rules, cache availability, and the traffic/synchronization
trade required for fusion. Build, learning, structural, and editorial checks
passed; fresh 390px and 1280px Chromium runs passed 207 anchors, keyboard
entry, exercises, 52 source-page return menus, and overflow checks. Artifacts:
`/tmp/conference-course-browser-8dldk87i/` (390px) and
`/tmp/conference-course-browser-j__2kenn/` (1280px). This improves wording
precision for HPCA; it does not complete the route's broader source review.

Editorial pass (2026-09-22): tightened FCCM's bank-layout example so the
converted layout's validity window is tied to changes in the original array,
and so extra padding is judged by complete storage and service cost rather than
by its size alone. The existing manuscript-backed table-II arithmetic and the
simulation-versus-board boundary remain unchanged. Build, learning,
structural, and editorial checks passed. This improves the FCCM teaching
wording without expanding its one-manuscript evidence boundary.

Editorial pass (2026-09-22): tightened OSDI route wording around contention,
complete device assignments, overlap, and efficiency. The route now names the
work or fairness cost of an intervention, asks readers to judge the complete
assignment rather than a peak unit, states the resource and dependency
conditions under which overlap lowers elapsed time, and defines the boundary
needed for an efficiency ratio. Build, learning, structural, and editorial
checks passed. This improves the OSDI teaching prose without turning the
route's six focused walkthroughs into a paper-by-paper proceedings review.

Editorial pass (2026-09-22): extended the OSDI prose review across the route's
work division, service change, training supply, model/runtime interface,
placement, pipelining, and cost themes. Replaced broad terms with explicit
conditions: dependency- and connection-respecting divisions, delay/fairness
costs, calculation rate versus waiting, consumer and eviction costs, startup
and drain, and cost per accepted result. Build, learning, structural, and
editorial checks passed. This advances the written OSDI route; its six
walkthroughs and source boundaries remain bounded rather than a full
proceedings review.

Editorial pass (2026-09-22): tightened ASPLOS explanations around modeled
proofs, layout assumptions, pipeline work, and cost per accepted result. The
prose now states that a proof guides only within its modeled guarantee, names
the no-retention assumption as a calculation condition, counts per-piece
handling as work, and distinguishes a lower resource ratio from eligibility
under the required quality and deadline rule. Build, learning, structural, and
editorial checks passed. This improves the ASPLOS writeup while preserving the
separate boundaries for source passages, abstract-only records, and paper-
reported measurements.

Editorial pass (2026-09-22): tightened SC's workflow and scientific-result
prose. The route now distinguishes a faster kernel from a faster path to an
accepted result, separates transport timing from scientific quality, names
the connection between a bound and the final quantity, and states that
iteration timing on a large problem does not establish complete-job timing.
It also replaces broad wording around scaling, recovery work, and prediction
validation with explicit measured quantities and conditions. Build, learning,
structural, and editorial checks passed. The 119-paper source-backed synthesis
and one cuSZ-Hi walkthrough remain bounded evidence, not a full proceedings
review.

Editorial pass (2026-09-22): tightened DATE route wording where broad words
could hide the actual condition. The route now names modeled timing targets,
distinct SAT answers and selection probabilities, loss/delay limits after
manufacturing variation, signal distinguishability, evidence requirements for
generated tests, access-cost consequences of layouts, and partial delivery as
a different service. Build, learning, structural, and editorial checks passed;
current Chromium checks passed at 390px and 1280px with 207 anchors and 52
source-page return menus. Artifacts are `/tmp/conference-course-browser-mmfgq9qa/`
and `/tmp/conference-course-browser-wrohneta/`. This improves prose precision
for DATE; it does not complete the route's broader source review.

Editorial pass (2026-09-22): tightened the VLSID and ICCAD-adjacent paper
writeups. VLSID now distinguishes physical-error consequences, queue evidence,
simulation, and measurement without calling them interchangeable; pulse-bit
risk wording separates consequence from occurrence probability; and RSizing
asks about passing yield and complete search cost directly. Build, learning,
structural, and editorial checks passed. The small VLSID sample and single
inspected RSizing paper remain explicitly bounded evidence.

Editorial pass (2026-09-22): tightened the NSDI route's remaining broad
phrases. The writeup now names service state by the result it is meant to
predict, asks how much of a transfer still produces accepted output after
probing, identifies the first response the user can accept, and replaces a
generic privacy-work claim with the answers that remain possible. It also
states representation reuse as a validity condition and requires answer
correctness, not only retrieval speed, in the comparison. Build, learning,
structural, and editorial checks passed. The NSDI route remains bounded by its
official-abstract summaries, three focused final-paper walkthroughs, and the
stated 150-paper synthesis boundary.

Editorial pass (2026-09-22): tightened ISCA and MICRO wording around complete
path cost and evidence. ISCA now calls out a complete stored-input-to-result
comparison, a legal schedule, and a bounded result statement; MICRO now states
that task grouping depends on legal placement choices and distinguishes its
event-model evidence from a generic preference for smaller events. Build,
learning, structural, and editorial checks passed. Their stated source and
walkthrough boundaries remain unchanged.

Editorial pass (2026-09-22): tightened ISSCC's opening and stage-cost language.
The route now asks for an accepted result rather than a generic useful result,
describes whole-path costs in terms of preparation and delivery, and replaces
an unqualified arithmetic label with the number of operations in the reviewed
segmentation stages. Build, learning, structural, and editorial checks passed.
The single ConvFormer source-backed record and limited conference coverage
remain explicitly bounded.

Editorial pass (2026-09-22): revised the opening of the cross-conference grand
synthesis. Arithmetic intensity is now presented as a starting lens with an
explicit roofline assumption, not a universal explanation. The inference and
KV-cache discussion states the conditions behind its estimates, and the route
distinguishes direct data-movement work from papers about deadlines, security,
correctness, manufacturing, and failure. Attention, interconnect, sparsity,
and security sections now separate reported mechanisms from common rankings or
guarantees. The grand-synthesis page rebuilt successfully at 3,319 words; the
course build, learning, structural, and editorial checks also passed.

Editorial pass (2026-09-22): extended the grand-synthesis review through the
eleven responses, tensions, field bets, and open problem. Quantization,
near-data processing, compilers, reliability, specialized hardware, systems
software, and reconfigurable computing now state their required conditions and
measurement boundaries. The tensions section names added work and trust or
ordering costs instead of using broad “wall” or “arms race” language. The open
problem now asks for a stated workload and acceptance rule rather than claiming
one universal equivalence guarantee. The page rebuilt successfully at 2,670
words; all course checks passed.

Editorial pass (2026-09-22): added an evidence-reading guide to the grand
synthesis. It now separates full-paper support, abstract-level support, local
review/theme-map support, and invented teaching calculations, and warns that
cross-venue counts and results are not automatically additive. The page rebuilt
successfully at 2,848 words; all course checks passed.

Editorial pass (2026-09-22): tightened the cross-venue 2025 synthesis. Its
opening now calls itself a map and reading guide, adds an evidence and venue
boundary, and replaces claims that a venue never crosses a layer with statements
about the sampled records. Shared-theme and venue-difference sections now say
when a pattern recurs without treating different metrics as one ranking. The
course and grand-synthesis builds, learning, structural, and editorial checks
passed.

Editorial pass (2026-09-22): reviewed the cross-venue coverage and confidence
section. Venue labels now describe sampled emphasis rather than absolute venue
boundaries; the table notes source depth, title-only exclusions, vendor framing,
and the difference between circuit metrics and serving results. The repository-
wide whitespace check remains noisy because of unrelated generated artifacts,
but the course-specific builds, learning, structural, and editorial checks
passed.

Editorial pass (2026-09-22): tightened the shared frontend teaching spine,
capstone, and comparison prompts. The course now asks for accepted results,
explicit task rules, concrete next checks, and usable capacity instead of broad
“useful” wording. The capstone's whole-cost step now defines a unit of work by
whether its result can be accepted. Build, learning, structural, and editorial
checks passed.

Editorial pass (2026-09-22): tightened the scientific-workflow lesson's
explanation of model adequacy. It now names changes that affect the reported
quantity instead of calling variation important in the abstract. Build,
learning, structural, and editorial checks passed.

Coverage audit (2026-09-22): course coverage, paper walkthrough, science,
table, permissions, and cross-topic checks passed. The current course contains
14 venue routes with 97 themes, 228 subthemes, 58 walkthroughs, and 16 lessons;
each declared subtheme has a teaching block, boundary, and source link. An
external-link audit found 184 reachable URLs, 20 publisher-restricted 403 URLs,
no missing URLs, and one repeatable DNS failure for the PETSc documentation
link. Restricted or transient link status does not change the written evidence
boundaries already stated in the affected lessons.

Editorial pass (2026-09-22): made a final targeted route pass where broad words
still changed the reader's interpretation. DATE now says a schedule must be
executable, MICRO names the shared-scale dependency and complete-system evidence,
ISCA reports the measured timing comparison without “better,” and NSDI names
accepted results and measurements to examine. Build, learning, structural, and
editorial checks passed.

Tracker consistency pass (2026-09-22): updated `CONFERENCE_COURSE_GOAL.md` so
its current-state section no longer presents the older browser and 166-URL
figures as fresh evidence. It now labels those browser runs historical,
records the later 205-URL audit and its 184/20/0/1 outcome, and keeps the open
claim-review and visual-review limits explicit. The generated course checks
passed after the tracker update.

Evidence-audit correction (2026-09-22): the three-atlas prose verifier was
expecting 60 locally passing ASPLOS numeric-claim rows, while the release
boundary correctly describes 59 local paper-text adjudications plus one
separately reviewed author-hosted full paper whose text is not in the local
extraction corpus. The verifier now checks 59 pass + 1 bounded review + 119
source-unavailable rows, matching the release boundary instead of masking that
distinction. The three-atlas prose audit, ASPLOS release-boundary audit, and
substantive-writing verifier now all pass.

Editorial pass (2026-09-22): corrected the VQ-LLM placement break-even example.
Its first version called a 100-unit placed path a loss while calculating a
100-unit saving; the revised text states both totals and the 40-unit loss when
setup rises to 200. Course build, learning, structural, and editorial checks
passed after the correction.

Editorial pass (2026-09-22): clarified the MVE transition example. Two jobs do
not merely “break even”: their 8 ms saving has paid back the 7 ms transition
and leaves 1 ms net savings. The example now reserves “first positive saving”
for the three-job case after the added dirty-line flush. Course checks were
rerun after the correction.

Editorial pass (2026-09-22): replaced several broad evaluative phrases in the
orientation, AFaaS, CIPHERMATCH, and comparison lessons with the condition or
measurement they meant: accepted result, complete measurement, isolated cost,
representation effect, and candidates that satisfy mandatory constraints.

Editorial pass (2026-09-22): tightened additional walkthrough wording in
BlitzScale, Picsou, VQ-LLM, VersaSlot, vAttention, and TRRIP. Broad words now
point to request-serving capacity, recipient-group evidence, separate measured
questions, named placement choices, arithmetic work, or an explicit failure
case. The paper boundaries and reported claims were not expanded.

Editorial pass (2026-09-22): replaced more generic “useful” and “important”
phrases in BTrace, cuSZ-Hi, SOLA, Mirage, Oaken, Past-Future, and the shared
route reading. The revised wording names diagnosis, deployment checks,
accepted service, or model reconciliation directly.

Editorial guardrail (2026-09-22): added a phrase-level vague-teaching check to
`scripts/check_course_editorial.py` for the cleaned patterns. It deliberately
does not ban technical uses of individual words; it rejects only phrases that
evaluate a result without naming its evidence, condition, or purpose.

Current evidence rerun (2026-09-22): source-boundary verifiers, four-atlas
theme mapping and coverage, cross-atlas evidence sources, and the execution
bundle contract all pass. The external-link audit remains bounded at 184
reachable, 20 publisher-restricted 403, 0 missing, and one PETSc DNS failure.
The cross-atlas status remains release-candidate-incomplete because its three
composition protocols are specified but not run; no composed-system claim is
made.

Editorial pass (2026-09-22): jargon review replaced “useful execution level,”
“useful interface,” and “cannot be useful” in the Mirage, EMT, and DVFS
walkthroughs with the concrete criteria those phrases meant. Build, learning,
structural, and editorial checks pass.

Handoff pass (2026-09-22): the repository README now links the generated course
and its learning sequence directly to `CONFERENCE_COURSE_GOAL.md`, where source
boundaries and remaining review work are stated. Course build, structural,
editorial, and learning checks pass after the README change.

Tracker-alignment pass (2026-09-22): updated `CONFERENCE_COURSE_GOAL.md` to
record the phrase-level editorial guardrail and the README handoff. Structural,
editorial, and learning checks pass; the tracker continues to keep claim-level
source review and full visual review open.

Jargon pass (2026-09-22): defined AICore, HBM, AICPU, and SoC at first use in
the fine-grained DVFS walkthrough, and stated why that platform boundary matters
for interpreting power. Course build, structural, editorial, and learning
checks pass.

Jargon guardrail (2026-09-22): `scripts/check_course_editorial.py` now checks
that those four DVFS platform terms retain their plain-language first-use
definitions. The guardrail passes alongside the existing structural and
vague-phrase checks.

Jargon pass (2026-09-22): defined MWPM, PEFT, RDMA, GQA, and LoRA at first use
in the Micro Blossom, PipeLLM, Tigon, and Mirage walkthroughs. The editorial
guardrail now checks these definitions as well; build, structural, editorial,
and learning checks pass.

Jargon pass (2026-09-22): defined DNN, TPC-C, YCSB, NISQ, and AOD in the
CaMDN, Tigon, Choco-Q, and PowerMove walkthroughs. The first-use definition
guardrail now checks these terms too; the current build and all course checks
pass.

Jargon pass (2026-09-22): defined HTAP, MVCC, OLAP, and OLTP in the PUSHtap
walkthrough, including the distinction between transaction updates, analytical
scans, and versioned reader views. The first-use definition guardrail and all
course checks pass.

Jargon pass (2026-09-22): defined PIM and QAOA at first use in the PUSHtap and
Choco-Q walkthroughs. QFT, VQE, and related names remain paper workload labels
rather than being expanded without teaching value. Build, structural,
editorial, and learning checks pass.

Jargon pass (2026-09-22): clarified ORB-SLAM3 as a visual-tracking and mapping
system in IRIS and expanded RTL as register-transfer-level in MVE. The editorial
guardrail checks both definitions; the current build and course checks pass.

Substantive evidence rerun (2026-09-22): the OSDI/ASPLOS first-principles
writing verifier, three-atlas prose evidence audit, and ASPLOS release-boundary
audit all pass. Their own warning remains in force: structural passage counts
and resolved paper IDs do not by themselves prove source accuracy or taxonomy
quality.

Plain-language pass (2026-09-22): replaced generic wording in the EMT, LUT,
EXIST, IRIS, and shared course-spine text with concrete terms: minimal
interface, stored-answer set, diagnostic event, decision unit, and complete
experiment. The build, editorial, structural, and learning checks pass.

Verification repair (2026-09-22): the paper checker had retained exact
substring assertions for `3.4× OLAP throughput` and `4.4× OLTP throughput`.
The newly required first-use definitions place the expansions between each
metric name and `throughput`, so the assertions were split into strict checks
for the values, defined terms, and metric. All 58 walkthrough checks now pass;
no teaching claim was weakened.

Plain-language pass (2026-09-22): replaced several remaining generic words in
the EXIST, CorrectBench, Micro Blossom, VersaSlot, ISCA, and shared-spine text
with explicit descriptions of the evidence, result states, fixed slot size,
calculation assumptions, and evaluation contents. Build, editorial, paper,
structural, and learning checks pass after the edits.

Browser rerun attempt (2026-09-22): the current environment could not launch
Playwright's bundled Chromium because the host lacks `libnspr4.so`, and no
system Chromium executable is installed. This is an environment failure before
page loading, not a course failure. The latest successful browser artifacts
remain the historical Chromium runs listed above; the post-edit prose pass has
been checked with the build, editorial, paper, structural, and learning suites
but not with a newly launched browser.

Focused source check (2026-09-22): reviewed the VersaSlot walkthrough against
the primary arXiv manuscript and the official DAC 2025 publication record.
The source supports the serial partial-reconfiguration limit, Big/Little slot
layout, 3-in-1 bundling, dual-core scheduling, live migration, ZCU216 testbed,
four comparison systems, and reported response-time and LUT/FF results. The
walkthrough keeps its schedules and break-even arithmetic as original teaching
models and now links both the full manuscript and publication record.

Focused source check (2026-09-22): reviewed the DARIS walkthrough against the
primary arXiv manuscript and DAC publication record. The source supports the
MPS/CUDA-stream sharing model, staged scheduling, MRET estimates, proportional
virtual deadlines, oversubscription, and the reported 15% and 11.5% throughput
comparisons. The walkthrough now also states the paper's reported high- and
low-priority deadline results while keeping them bounded to the tested setup;
its deadline and stage arithmetic remains original teaching material.

Focused source check (2026-09-22): reviewed the GSIM walkthrough against the
primary arXiv HTML and author-hosted conference paper. The source supports the
four simulation-cost factors, supernode/node/bit-level transformations, state
dependency examples, Verilator/ESSENT/Arcilator comparisons, XiangShan and
SPEC CPU2006 measurements, and the distinction between simulator runtime and
chip performance. The official DAC DOI was verified and added; teaching cost
models remain separate from the reported measurements.

Focused source check (2026-09-22): reviewed the CaMDN walkthrough against the
primary arXiv HTML and verified its DAC DOI. The source supports the motivation
numbers, model-exclusive NPU cache regions, bypass and multicast operations,
32 KB pages in the 16 MB modeled cache, mapping candidates, layer blocks,
prediction and fallback, cycle-accurate simulation, synthesis, QoS measures,
and area results. The course keeps its cache counts and timing examples as
teaching models and keeps simulated/synthesized evidence separate from a chip
measurement.

Focused source check (2026-09-22): reviewed the Tropical walkthrough against
the primary arXiv HTML and IEEE publication record. The source supports the
TTFT/TPOT definitions, joint SLO-attainment rule, queueing-versus-interference
tradeoff, slack checks, worker-state and memory thresholds, Mooncake trace,
InternLM-20B, eight A100 GPUs, and the reported 2.09×, 9×, 15%, and 2.8×
comparisons. The walkthrough now states those phase-specific results directly
and keeps them bounded to the tested setup; its queue arithmetic remains a
teaching model.

Focused source check (2026-09-22): reviewed the ConvFormer walkthrough against
the current arXiv record and the related ISSCC DOI. The record confirms the
28 nm accelerator, semantic-segmentation scope, hybrid attention, layer fusion,
cascaded pruning, 52.90 TOPS/W peak, and ISSCC paper identity. The walkthrough
keeps its digest-level source boundary, prior-accelerator peak assumptions, and
invented storage/energy calculations explicit; no chip result was reproduced.

Focused source check (2026-09-22): reviewed the RSizing walkthrough against
the author-hosted paper and the verified ICCAD publication record. The source
supports the three-stage nominal/variation-aware/refinement workflow, sampled
yield results, separate-requirement versus joint-yield issue, remaining
distribution-approximation error, Spectre/TSMC-40-nm simulation boundary, and
the different runtime outputs in Table IV. The DOI is now linked in the
walkthrough; no manufactured-chip result or circuit experiment is claimed.

Focused source check (2026-09-22): reviewed the FCCM Banked Memories
walkthrough against the author manuscript and the official FCCM program and
accepted-paper list. The manuscript supports the 16-lane banked-memory
controller, bank-request counting, arbitration, return routing, 16-bank
address mapping, reported control/memory delays, and the matrix-transpose and
FFT evaluation context. The abstract reports 51 benchmark combinations while
section V reports 52; the route keeps that discrepancy visible. The four-bank
schedule, padding break-even, return-path extension, and clock-rate examples
remain explicitly invented teaching models rather than claims about the
implemented processor. The source check also confirms the official program's
placement in the Memories session.

External-link audit rerun (2026-09-22): checked 212 unique URLs across 53
course files. 191 responded, 20 publisher/DOI pages returned access-denied
403 responses, no URL was missing, and the only transient error was DNS
resolution for the PETSc manual page. Direct access to the official PETSc
release and main documentation pages succeeds; no citation was removed or
weakened because of the checker-side DNS failure.
