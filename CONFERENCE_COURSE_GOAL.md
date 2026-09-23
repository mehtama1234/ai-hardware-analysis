# Conference research as a first-principles course

User-directed working objective, 2026-09-21. This brief governs the conference frontend and writing work. The active tracker has the generic label `resume start with the new goal`; this document records the concrete objective and completion requirements.

## Intended result

Current written-course state (2026-09-22): the generated course contains 16
lessons, 59 concepts, 1,863 course links, 58 paper walkthroughs, and 52 source
pages. The latest recorded Chromium regression passed at both 390px and 1280px
across 207 anchors, exercises, keyboard interactions, source-page return menus,
and horizontal-overflow checks. That browser run predates the later prose-only
editorial passes, so it remains automated layout evidence rather than a fresh
regression after every wording change. Claim-level source review, complete
human visual review, and proceedings-wide paper review remain open.

Historical progress: reran the full local browser regression after the recent
source-backed walkthrough revisions. The generated course passed at 390px and
1280px across homepage entry, contents, 175 anchors, exercises, 26 paper
walkthroughs, 52 source pages and return menus, keyboard interactions, and
overflow checks. A narrow Past-Future screenshot was inspected and readable.
This renews automated local-browser evidence only; it does not replace a
systematic human visual review or claim-level source validation.

Historical progress: reran the complete local-browser regression after the
navigation and coverage-table changes. It passed at 390px and 1280px across
homepage entry, contents, 175 anchors, interactive practices, 26 paper
walkthroughs, 52 source pages and return menus, keyboard interactions, and
overflow checks. Sampled narrow-screen images of contents, a long practice,
QServe, and a source page were readable. This closes the fresh automated
browser-regression gap; it is not a systematic human review of every page or
a claim-level source check.

Historical progress: added a repeatable external-link reachability checker and
ran it across the generated course and 52 source pages. The later audit checked
212 unique URLs across 53 files: 191 responded, 20 publisher pages denied
automated access with 403, no URL was missing, and the PETSc documentation URL
failed twice with temporary DNS resolution errors. These are reachability checks,
not claim-level citation validation.

Progress: replaced generic coverage-table evidence text with a specific source
boundary for every conference. The table now reports bounded counts where the
route has them—for example, 17 of 135 ISCA records adjudicated, 32 of 456 DAC
records source-backed, and one FCCM manuscript inspected outside a local audit
that had no validated PDFs. A structural invariant requires all 14 labels.
Build, learning arithmetic, structural, and focused mobile/desktop table checks
pass. The specific labels make incompleteness legible; they do not broaden the
underlying reviews.

Progress: made core lesson navigation explicit to assistive technology. Each
of the 16 lessons now has a named “Lesson navigation” region with its correct
previous and next lesson where applicable. Structural checks validate every
neighbor mapping. Focused 390px and 1280px browser checks verified all 16
regions, all link labels, keyboard activation from the first lesson forward and
the last lesson backward, and no horizontal overflow. Build and learning
arithmetic checks pass.

Progress: redesigned the revised coverage/evidence table for narrow screens.
The first mobile version avoided overflow but compressed three columns until
the text became unreadable; visual inspection caught that. At 560px and below,
each conference now renders as a labeled card with teaching coverage and
evidence status, while desktop keeps the semantic three-column table. The
first card CSS also collapsed the caption; that was corrected and re-inspected.
Build, learning arithmetic, structural, responsive-layout, and document-width
checks pass. Screenshot evidence is recorded in the frontend check log.

Progress: corrected the conference-coverage table's status model. It now
separates explicit teaching material (themes, subthemes, worked examples,
exercises, walkthroughs) from evidence status. The old wording implied that
routes with all subtheme blocks lacked subtheme coverage; the new wording says
what the counts do and do not establish. Build, learning arithmetic,
structural, and focused mobile/desktop table checks pass. This change improves
scope honesty; it does not turn any route into a full proceedings review.

Progress: removed remaining unexplained hardware shorthand from two paper
walkthroughs. PIMBA now defines a bank row buffer and prompt prefill where they
first matter; QServe defines its QoQ conversion chain, eight-bit integer work,
and Tensor Cores in ordinary language. No paper claim or numerical result was
changed. Build, learning arithmetic, structural, and focused mobile/desktop
checks pass. Broader source review remains incomplete where the route notices
say it is incomplete.

Progress: tightened the Di-PS walkthrough after reading the final NSDI paper's
controlled and production evaluation. It now names the four-cluster LLaMA3.2-1B
emulation, 0–200% performance disparity, loss curves, and BBH/MMLU/DROP scores;
it distinguishes that comparison from a 33-day, nine-cluster production account
that lacks a synchronous counterfactual. Reworded the EMT simulator heading so
it states that simulation guides a later hardware test rather than deciding a
hardware verdict. Build, learning arithmetic, structural, and focused
mobile/desktop checks pass. The course still has incomplete broader source
review, as documented by its route evidence notices.

Progress: strengthened the final paper-reading challenge. It now requires a
measured quantity in place of vague claims such as “faster,” a numerator and
denominator for percentage results, and labels for paper-reported facts,
reader-calculated results, and reader-inferred next questions. The structural
check enforces these prompts. Focused mobile and desktop checks confirmed all
six note fields, the keyboard-opened rubric, and no horizontal overflow.
This improves the transfer exercise; it does not establish that a reader has
completed a paper audit or that every course source has been reviewed.

Progress: expanded the cross-conference success comparison with a 100-request
example distinguishing separate pass rates from passing both checks. Two 90%
rates permit 80–90 joint successes; four overlapping failures give 84. The
explanation distinguishes an independence-based probability prediction from
an observed count and shows how dropping unanswered requests changes the claim.
Arithmetic checks enumerate every possible overlap. Build, structural, and
focused mobile/desktop keyboard checks pass. This is a teaching example, not
a newly attributed result for any of the linked papers.

Progress: clarified the opening's starting points and connected all 16 lessons
in order, with an automated sequence check. A full browser regression found
and prompted a repair to the VLSID table on narrow screens. The regression
subsequently passed at 390px and 1280px, covering 175 anchor positions and 52
source pages at each width. Final table refinements passed separate all-table
width checks; the opening and revised table were visually inspected at both
widths. Broader paragraph-by-paragraph and source review remains unfinished.

Progress: revised the four ICCAD lessons around requirements, estimates, behavior,
and search time. Defined constraint/objective and counter wraparound in context;
replaced unexplained subtheme labels. Corrected the prediction example so it
actually demonstrates both accepting a failing design and rejecting a passing
one, with arithmetic checks for the error and both decisions. Clarified that
exhaustive counter checks cover the next-value calculation, not reset or timing.
Build, structural, learning, editorial-heuristic, and focused browser checks
passed. The broader source and course review is still unfinished.

Progress: revised all three FCCM section introductions and titles for plain-language
reading, defined banks and padding where first needed, and separated read-start
counts from result-delivery time. Rechecked the controller explanation against
the author manuscript, sections III.A–B. Build, learning, structural, and focused
mobile/desktop browser checks passed. FCCM remains a limited guide based on one
inspected manuscript; this pass does not complete the wider editorial goal.

Build a professionally written, accessible frontend course that teaches people how computer systems produce useful results. Use the conference research to explain why a problem exists, how different mechanisms address it, which assumptions they require, and when those mechanisms stop helping. Readers should finish able to reason through an unfamiliar paper rather than merely recognize its vocabulary.

The course begins with time, storage space, movement, dependencies, shared resources, numerical error, and failure. Derive larger concepts from those constraints. Define necessary technical language after explaining the concrete idea. Write in everyday words without stock praise, slogans, unexplained abbreviations, or claims whose cause is unspecified.

## Scope and sources

Use the existing MLSys 2025, OSDI 2025, ASPLOS 2025, NSDI 2026, ISCA 2025, HPCA 2025, MICRO 2025, SC 2025, DAC 2025, DATE 2025, and VLSID 2025 analyses. Include ISSCC, ICCAD, and FCCM with their current evidence limits explicitly recorded. Audit other editions already linked by the site before relying on them. Conference years and paper identities must remain visible.

Read authoritative external sources wherever the local writing lacks an explanation or adequate evidence: original papers, author-hosted books, university teaching material, specifications, and official documentation. Cite the passage relevant to the claim. A retrieved document is not automatically a reviewed document. Abstracts can support what they actually say; they cannot support invented implementation details or numerical comparisons.

Preserve the distinction between paper-reported findings, original teaching examples, and deductions made across papers. Verify units, assumptions, baselines, and measurement scope. Never multiply unrelated speedups or imply that different papers were tested together.

## Learning sequence

1. Follow one request from arrival to delivery. Explain elapsed time, work, waiting, and the rate at which requests finish.
2. Explain dependencies and shared resources. Derive when parallel work and pipelines help, including startup, draining, and contention.
3. Follow data through memory and storage. Explain capacity, transfer rate, access delay, locality, caching, ownership, and invalidation.
4. Change how numbers and work are represented. Explain precision, compression, sparsity, conversion costs, and accumulated error.
5. Translate a program into execution. Explain compiler choices, layouts, specialized hardware, and preservation of program meaning.
6. Share machines among users. Explain queues, batching, fairness, deadlines, interference, and unusually slow requests.
7. Coordinate machines. Explain communication, agreement, replication, delayed information, failure detection, and recovery.
8. Make the design physical. Explain wires, power, heat, device variation, chip design checks, and what simulation versus measurement establishes.
9. Evaluate complete workloads. Trace model serving, distributed training, durable updates, and scientific computation from input to accepted output.
10. Compare conference papers using the concepts already learned. Explain competing mechanisms, conflicting assumptions, missing measurements, and unanswered questions.

Conference-specific reading routes supplement this concept-first route. Each conference needs an introduction, developed theme and subtheme explanations, representative paper walkthroughs, comparisons, and links back to the common lessons. Maintain a coverage table so a broad survey does not silently substitute for an unfinished conference route.

## Lesson requirements

Each substantive lesson needs a concrete question, prerequisites, a connected explanation, a worked example with explicit quantities, a failure case, connections to neighboring concepts, and exercises with explained answers. Paper references should show what the mechanism changes and what the evaluation establishes. Use diagrams or small interactive examples where changing a parameter helps readers understand cause and effect.

Keep the main prose readable without opening citations. Define concepts at first use and provide a linked glossary. Label teaching numbers clearly. Avoid repeating an identical template across papers without discussing their differences.

## Frontend requirements

Extend the existing site and reproducible course build. Provide a clear starting point, ordered lessons, prerequisites, previous/next navigation, conference routes, concept lookup, source links, and return links from paper discussions. Support narrow screens, keyboard use, visible focus, readable contrast, stable section links, and readable mathematical examples. Exercises must remain understandable without animation or pointer interaction.

## Completion test

The course is complete when every declared route contains developed lessons; every major theme and subtheme has an explanation, example, failure condition, and evidence; readers can follow the complete worked workflows; source strength is stated accurately; and the generated frontend works on desktop and mobile. Check calculations, citations, internal links, navigation, and rendered layout. Editorial review must remove vague claims, unsupported conclusions, and unnecessary jargon. File existence and successful build scripts alone do not establish completion.

Hardware simulation campaigns, converter repairs, fabrication, and conference submission strategy are outside this writing goal. Examples may explain such work, but completing an experiment is not a prerequisite for teaching a sourced concept.

## Current implementation status

`COURSE_COMPLETION_AUDIT.md` records the current requirement-by-requirement
completion assessment. It confirms broad teaching structure and bounded source
scope, while keeping proceedings-wide review, claim-level source validation,
fresh full-browser regression, and complete visual review explicitly open.
External-link reachability has been checked separately: 191 of 212 URLs
responded, 20 publisher/DOI pages returned automated-access 403 responses, no
URL was missing, and the PETSc checker error was a transient DNS failure
confirmed against the official page through another source path. Reachability
is not claim validation. Do not use structural counts as a completion claim.

The frontend is `course.html`, generated by `scripts/build_course.py` from the
course content modules. It contains 16 core lessons, 14 conference routes, 59
glossary entries, seven cross-topic comparisons, three checkpoints, and 58
focused paper walkthroughs. Fifty-two linked research notes have generated
HTML reading pages with return navigation. The existing conference essays and
review records remain under `analysis/` and `metadata/`.

All fourteen routes now have dedicated worked examples and explained exercises
for every top-level theme. All 228 subthemes also have explicit application,
failure, evidence, and source blocks. This establishes teaching coverage, not
full proceedings review or independent reproduction of every paper result.

Focused paper walkthroughs cover MLSys, OSDI, ASPLOS, NSDI, ISCA, HPCA, MICRO,
SC, DAC, DATE, VLSID, ISSCC, ICCAD, and FCCM. Coverage is uneven: the DAC
route now has five full walkthroughs (GSIM, DARIS, CaMDN, Tropical, and
VersaSlot), while
several routes have one. The source and paper coverage remains intentionally
bounded by each route's evidence notice; a walkthrough is not a full proceedings
review.

The next editorial pass is claim-by-claim: review the complete reading sequence
for unexplained terms, repetition, missing prerequisites, unsupported claims, and
gaps between examples and the mechanisms described in the papers. Keep original
teaching models visibly separate from paper-reported measurements.

Structural checks currently pass for 1,863 course links and the generated source
navigation. Browser-check scope and limitations are recorded separately in
`COURSE_FRONTEND_CHECK.md`. Neither passing checks nor these component counts
establishes completion of the writing goal.

The editorial triage currently sees 97 route themes and 228 subtheme entries.
Every theme has a connected explanation, worked reasoning, practice answer, and
reading boundary under the current schema. All 228 subthemes now have explicit
application, failure, evidence, and source blocks. `scripts/check_course_editorial.py`
verifies their presence and valid route mapping. It also rejects the recurring
empty promotional phrases and the phrase-level vague teaching patterns removed
during the latest editorial pass. The repository README links the course to
this tracker so readers can find both the tutorial and its evidence limits. The
final bounded audit also checked source reachability, evidence wording,
repetition, and the separation of original teaching models from paper-reported
results; its limits are recorded below. The latest external-link run is
recorded in `COURSE_COMPLETION_AUDIT.md`.

## Historical bounded completion audit — superseded by the continuing goal below

The bounded course-writing objective was completed on 2026-09-21. The final audit
verified the following against the generated frontend and current source modules:

- 16 ordered lessons, 40 glossary concepts, six comparisons, three checkpoints,
  14 conference routes, 97 themes, and 228 subthemes.
- Every theme has an explanation, worked quantities, an explained exercise, and
  an evidence boundary. Every subtheme has an application, failure condition,
  evidence boundary, and source link, with 228 matching blocks in generated HTML.
- Fourteen focused walkthroughs identify the inspected paper, scope, source
  passages, original teaching calculations, and measurement limits. Conference
  routes state where their corpus review is limited; no paper result is presented
  as independently reproduced.
- Structural, arithmetic, source-navigation, table, keyboard, mobile, and desktop
  checks pass. The 14 unique external source URL families used by the course were
  reachable during the final audit. Reachability is not citation proof, so source
  limits remain visible in the course.

This completion claim is for the bounded tutorial and its stated evidence limits,
not for a complete review of every paper in every conference or for new hardware
experiments. Such work is outside this writing goal.

## Continuing end-to-end course goal — 2026-09-22

The orientation and final unfamiliar-paper challenge are now part of the
generated frontend. The full Playwright browser regression passes at 390px and
1280px, including 175 course targets, all 21 source pages, and the new keyboard-
operable request-latency model. See
`COURSE_FRONTEND_CHECK.md` for commands, screenshot locations, and limits.

The first lesson's latency example now has a small interactive model. Readers can
vary calculation time while queue waiting, input reading, and answer delivery
remain fixed; the display recalculates elapsed time and makes the fixed-stage floor
visible. Browser checks exercise the control from the keyboard at both viewport
sizes. The example explicitly does not predict throughput for concurrent requests.

The dependency lesson now states the general pipeline fill-and-drain calculation,
`first-item time + (item count − 1) × slowest-stage time`, and uses source-backed
OSDI 2025 WLB-LLM and ASPLOS 2025 FSMoE examples to distinguish load balancing
from communication/computation overlap. Their reported speedups, experimental
baselines, and non-reproduction boundary are explicit. Arithmetic, editorial,
structural, and 390px/1280px browser checks pass; screenshots were visually
reviewed. This is one lesson's editorial pass, not course-wide source or teaching
validation.

This verifies that the pages and interactions work under those tested
conditions. It does not verify every explanation against its source, establish
screen-reader accessibility, or show that a learner can use the course
independently. The content still needs a deliberate claim-by-claim source and
editorial review, and the planned pilot with Propel has not happened. Do not
claim learning transfer until the pilot is run, observed, and the course revised
from the evidence.

The memory lesson now defines capacity as a peak of values that must coexist and
works a clearly invented 24 GB example. Its APOLLO (MLSys 2025) connection
explains the optimizer-state mechanism in plain terms and labels the reported
28 GB footprint and throughput result as paper evidence, not a course
reproduction. It also distinguishes volatile working memory from persistent
storage and notes that an SSD write needs the right durability rules. The
learning checker now guards these explanations alongside the existing cache
arithmetic. Structural checks report 16 lessons, 46 concepts, 1,241 course
links, 22 source pages, and 26 paper walkthroughs; the full browser regression
passes at 390px and 1280px across 175 anchors and all 22 source pages. This is a
focused review of one foundational lesson, not the remaining claim-by-claim
source review or the planned Propel learner pilot.

The numbers lesson now grounds its precision theme in the distinct MLSys 2025
cases QServe and MiLo. QServe illustrates that low-bit values can impose
conversion overhead unless the GPU path is redesigned; MiLo illustrates
recovering some detail with compact correction state and a matching kernel. The
lesson defines its necessary terms, keeps reported speedups tied to each
paper's own model/device/baseline, and says explicitly not to compare the two as
a head-to-head result. The QServe 20–90% figure is phrased as reported runtime
overhead associated with dequantization, not as a percentage of total runtime.
The checker protects the new explanation and evidence boundaries. The final
build has 16 lessons, 46 concepts, 1,245 links, 24 source pages, and 26 paper
walkthroughs; structural, learning, and full 390px/1280px browser checks pass.
This remains a focused second-lesson review, not the required course-wide
claim-by-claim source audit or the learner pilot with Propel.

The skipping-work lesson now distinguishes three MLSys 2025 meanings of
sparsity: SparseTransX reorganizes naturally sparse graph updates without
discarding small values; Radius omits selected gradient entries from
communication and carries leftover error forward, with a specific AdamW
correction limit; TASD/TASDER decomposes irregular sparse work into patterns
supported by the target accelerator, trading approximation accuracy against
additional operations. The prose explains gradient, optimizer history, and the
graph example in plain language, and ties each result to its own system and
workload rather than ranking incomparable speedups. Exact arithmetic and
source-boundary checks now cover the lesson. The current build passes structural,
learning, paper, editorial, table, science, route-coverage, resizing, and browser
checks: 16 lessons, 46 concepts, 1,251 links, 27 source pages, 26 walkthroughs,
175 anchors at both 390px and 1280px. This is a focused third lesson review; the
required course-wide claim-by-claim review and Propel learner pilot remain open.

The compiler lesson now explains how an optimizer can change an execution plan
while preserving the program's meaning, with concrete examples of array fusion,
floating-point reassociation, tiling, and the cost of preparing an optimized
version for repeated use. Its ASPLOS 2025 example uses Relax to show why keeping
symbolic input-size relationships such as n and 4n can preserve optimization
opportunities across a model's computation graph and lower-level loops. The
course links the author-hosted conference paper and labels its reported results
as evidence for the tested models and targets, not a universal speedup claim.
Structural, learning, walkthrough, editorial, table, science, coverage, resizing,
and browser checks pass: 16 lessons, 46 concepts, 1,253 links, 28 source pages,
and 26 walkthroughs; the browser visited all source pages and checked 175 course
targets at 390px and 1280px. This is the fourth focused lesson review, not a
claim-by-claim review of every course source or validation with Propel. Those
remain part of the active end-to-end goal.

The distributed-work lesson now makes checkpoint design a source-grounded
cross-conference comparison. Checkmate (NSDI 2026) reuses gradients already
crossing the network to keep a CPU shadow model current each training step;
the explanation names the extra network, shadow-cluster, and exactly-once
delivery requirements behind its tested throughput result. LLMTailor (SC
Workshops '25 / PDSW '25) merges selected layers and optimizer state from partial
checkpoints; the lesson distinguishes a loadable checkpoint from an identical
recovery and notes the lower benchmark scores reported for its filtered
Qwen2.5-7B fine-tuning example. The distinction between the SC workshop and the
main SC conference is explicit. The learning checker now protects these scope
and failure-boundary claims. Structural, learning, paper, editorial, table,
science, coverage, resizing, and browser checks pass: 16 lessons, 46 concepts,
1,258 links, 30 source pages, and 26 walkthroughs. The responsive test covers
all 30 source pages and 175 course targets at 390px and 1280px; a new dedicated
check confirms the distributed-work exercise opens by keyboard without
horizontal overflow. This is a focused lesson review. It does not close the
course-wide claim audit or the learner pilot with Propel.

The correctness lesson now explains its central question in direct language:
write down the required behavior and the failures the design must handle before
calling an answer correct. It distinguishes tests on chosen runs, proofs under
stated assumptions, and searches that can return an undecided result. The
conference examples now make those limits concrete: PMVerify (ASPLOS 2025)
reported 12 violations, one case meeting its rule, and 13 undecided among 26
example programs; PoWER (OSDI 2025) uses proof obligations for recovery and a
separate rule for detecting damaged stored data. The lesson states that these
are bounded findings, not guarantees for all storage or all failures. I also
reconciled the PMVerify note's stale "abstract-only" statement with its focused
author-PDF review, while retaining the fact that the PDF was not imported into
the local extracted-text corpus. The note's bare long PDF address is now a
clickable link, fixing a 390px horizontal overflow in its rendered page.

The learning, structural, paper, editorial, table, science, conference
coverage, and resizing checks pass: 16 lessons, 46 concepts, 1,262 links, 32
source pages, and 26 walkthroughs. Chromium passes at 390px and 1280px across
175 course targets and all 32 source pages; the correctness exercise opens by
keyboard without overflow. This is a focused content and source review, not a
complete audit of every conference claim or the planned learner pilot with
Propel.

The physical-design lesson now starts with an addition moving through circuits,
wires, and storage. It explains capacitance, leakage, the clock cycle, setup,
hold, and floorplanning at their first use. An original energy example shows
why a reduction from 100 J to 64 J in switching can still raise task energy
from 120 J to 124 J when supporting components stay powered for a longer run.
The longer duration is an explicit assumption, not a prediction from voltage.
MIT's circuit and sequential-logic teaching material supports the electrical
and capture explanations; OpenROAD documentation supports the implementation
sequence. Build, learning, structural, and focused mobile/desktop browser checks
pass. The full course source review remains open.

NSDI's first theme now explains the information a controller needs before
choosing a worker or a network sending rate. UNUM and PolicyCache replace
generic reading leads with a bounded comparison of history learned across
network settings and learning within an ongoing transfer. Their official
USENIX abstracts support the mechanism summaries; the text claims no common
benchmark or numerical superiority. The three subtheme notes now cite these
relevant sources instead of FastServe. Queue and probe calculations remain
explicit teaching examples. Build, learning, editorial, structural, and focused
390px/1280px browser checks pass; the course-wide review remains open.

NSDI's recovery theme now distinguishes Checkmate's maintained model copy,
Fractal's dependency and progress tracking, and PILOT's simulated recovery
actions. Each mechanism summary is bounded to its official USENIX abstract;
the text keeps PILOT's 17-of-20 result attached to its evaluated failures.
The three recovery subtheme notes now use relevant recovery sources instead
of FastServe. The shared-spare and script examples remain explicitly original.
Build, learning, editorial, structural, and focused browser checks pass.
The wider source and editorial review remains unfinished.

NSDI's slow-request theme now distinguishes worker preparation from wireless
transmission waiting, using HydraServe and BLADE's official abstracts. It
defines tail, cold start, and contention window in context and replaces the
startup and fairness notes' generic FastServe citations with relevant sources.
The remaining-work note retains FastServe where its scheduling scope applies.
The teaching arithmetic remains separate from paper results. Build, learning,
editorial, structural, and focused 390px/1280px browser checks pass. The wider
conference review remains open.

NSDI's evidence theme now connects missing-event diagnosis to μView's compact
measurement processing, MirrorNet's historical reconstruction, and CrossCheck's
input validation. Three generic FastServe notes were replaced with these
topic-relevant sources. The prose defines trace, sketch, emulation, and
wide-area network in context. CrossCheck's four-week deployment with one
detected incident is kept separate from simulation coverage and from any claim
of a zero future false-alert probability. Build, learning, editorial,
structural, and focused responsive browser checks pass. This is another
bounded theme review; the full source and editorial review remains open.

NSDI's hardware-boundary theme now explains HybridMesh's network-card/host
division and FENIX's switch/FPGA division using their official abstracts.
It defines host, proxy, ingress gateway, feature, and FPGA in context. Three
generic FastServe subtheme notes were replaced with relevant primary sources.
An original 200-versus-150-records-per-second example explains why buffering
cannot remove sustained overload. Its arithmetic and the existing exception
path arithmetic were checked exactly. The full conference review remains open.

NSDI's state-movement theme now explains SYMI's separation of parameters and
optimizer history and ZipLLM's shared bases and lossless model differences.
Three generic FastServe source notes were replaced with relevant official
abstracts. The new storage example distinguishes bytes stored from the data,
reconstruction time, and working space a reader needs. Its 40 GB versus 13 GB
arithmetic and the XOR reconstruction rule were checked. Full source and
editorial review across the course remains unfinished.

NSDI's representation theme now explains task-oriented reconstruction through
KDC and candidate selection followed by reuse judgment through Cortex. Three
generic FastServe notes were replaced with the papers' official abstracts.
The prose separates plausible reconstruction from exact recovery and related
queries from valid answer reuse. Sensor and software-version examples are
explicit teaching cases; the indistinguishable-summary calculations pass.
The course-wide editorial and source review remains open.

NSDI's scheduling theme now explains FastServe's token-level preemption and
Libra's cooperating request segments. The text defines scheduler, token,
preemption, batch, and cached attention state in context. Two subtheme notes
now use Libra's official abstract for cross-worker dependencies and local
batching; FastServe remains the relevant stopping-point source. The original
schedule preserves the costs to both requests and distinguishes three possible
timing targets. Build, learning, editorial, and structural checks pass.
The full browser regression also passes on the accumulated course changes:
175 targets and all 32 source pages at 390px and 1280px. The full writing goal
remains active; these checks verify frontend behavior, not all source claims.

The NSDI route introduction now follows one request through the ten themes,
giving readers an explicit sequence from observation and assignment to recovery
and evidence. Its status and source notice distinguish the synthesis, selected
abstract checks, focused walkthroughs, and original teaching quantities. Six
misleading directional references were corrected to match the generated reading
order. Build, learning, venue-coverage, editorial, and whitespace checks pass.

A prerequisite pass through the early lessons now derives bit-pattern counts
before quantization, defines byte and decimal GB, explains the time units used
in memory examples, and introduces weights, gradients, and optimizer state
before the training-memory calculation. The topology lesson now defines link,
switch, packet, and route before its transfer example. The actual generated
lesson order was inspected. Build, learning, structural, and whitespace checks
pass; the broader prerequisite and source review remains open.

The dependency lesson's long conference-results paragraph is now five connected
paragraphs: WLB-LLM's work assignment, its comparisons, FSMoE's overlap mechanism,
its evaluation scope, and the shared reasoning. Batch, sharding, token,
mixture-of-experts model, GPU, and layer are explained in context. Reported
numbers and comparison names are retained. The misleading phrase about
"reducing the worker" now identifies the waiting time being reduced, and the
existing wording check was updated accordingly. The broader review continues.

The course opening now states the concrete problem of a faster component that
does not shorten a request. Learner guidance asks readers to predict, calculate,
and change one assumption. The starting delay question uses one late request
per hundred instead of an unexplained percentile. Arithmetic prerequisites now
include division and percentages. Build, learning, structural, and focused
mobile/desktop orientation checks pass; the mobile opening was inspected.

The final paper challenge now includes an invented worked explanation that
separates reported measurements, derived arithmetic, and an open question.
Its 12-to-8 ms example includes 20 ms of reusable preparation: five requests
tie and six yield a net saving. The explanation states the assumptions and
shows how to cite the real paper's corresponding facts. This strengthens the
self-review guidance; it does not substitute for observing learners use it.

Five glossary entries now include short numerical examples: energy, latency,
throughput, false positives, and percentiles. They clarify interval boundaries,
the population used to calculate a rate, and the chosen percentile convention.
The arithmetic and indexing were checked; build, learning, and structural
checks pass. This is part of the continuing plain-language review.

ISCA's representation theme now explains lookup preparation, validity, and
reuse through a four-product teaching table and a separate break-even example.
The LUT Tensor Core author summary supports the mechanism connection, and a
newly linked local evaluation note preserves the synthesis/simulation boundary.
Build, learning, editorial, structural, arithmetic, and focused browser checks
pass; the broader conference review remains unfinished.

ISCA's near-memory theme now uses NMP-PaK to explain local working storage,
CPU/accelerator work division, and the need to distinguish software gains
from hardware-placement gains. Two mismatched LUT-source notes were replaced.
The new source page records the modeled evaluation and the fitting-input
GPU comparison. The broader source and editorial review remains open.

ISCA's scheduling theme now explains data readiness, shared hardware, and
storage through a concrete two-input timeline. RSN provides the paper connection;
the writeup separates measured execution, reported comparison times, and
estimated power. Two unrelated source notes were replaced. This is an
incremental writing improvement, not completion of the cross-conference review.

ISCA's shared-connections theme now explains network interfaces, shared capacity,
and arrival order. The DeepSeek section distinguishes the actual deployment,
proposed interface features, and measured comparison. Two mismatched citations
were replaced. Content checks and focused narrow/wide keyboard and width checks
pass; the broader writing and source review remains open.

ISCA's preparation theme now connects HPVM-HDC to unsupported operations and
device-specific code generation. Input shape, compiler, and reuse conditions
are explained in ordinary language. An original example counts both the
accelerated operation and the work and transfers that remain. The broader
cross-conference editorial and source audit is still unfinished.

ISCA's correctness theme now distinguishes preserving memory-access behavior
from permitting numerical approximation. DX100 supplies the compiler legality
example; HyFlexPIM supplies a qualified model/hardware preparation connection.
The invented ranking example explicitly separates assumed error limits from
tested quality. Content, arithmetic, and focused browser checks pass. Remaining
conference writing and source review are still open.

ISCA themes 7 and 8 now explain mixed measured/modeled evidence and complete-job
comparisons with concrete RSN, Oaken, and NMP-PaK review connections. All eight
ISCA themes have received this plain-language/source-relevance pass, but this
does not establish full-paper coverage or completion of the broader course.
The next conference route still needs equivalent source and prose review.

The HPCA review has begun with memory execution. Theme 1 now connects MVE's
multidimensional instructions to a concrete row-grouping example, defines
cache and vector instruction, and distinguishes simulation from device tests.
The local evaluation review is available as a linked source page. The remaining
HPCA themes and broader course audit are unfinished.

HPCA theme 2 now explains codebook lookup through VQ-LLM and selected-result
reuse and work packing through EXION. An original worker timeline shows why
fewer operations need not shorten execution. Source notes now match the
subthemes; modeled accelerator timing remains distinct from quality tests
and measured GPU results. The remaining HPCA review is still open.

HPCA theme 3 now connects supply, calculation, and storage timing to LEGO's
generated hardware arrangements. A row-sum example distinguishes independent
work from a cross-row dependency. The evaluation discussion preserves the
memory-limited workload and excluded CPU communication. The wider writing
review remains unfinished.

HPCA theme 4 now connects device-count and frequency choices to DynamoLLM.
A changed-request example distinguishes arrival count from work per request,
and the source discussion preserves the tested hardware/trace limits. The
remaining HPCA themes and broader course review remain open.

HPCA theme 5 now explains when selecting a fallback avoids wasted work and
distinguishes unsupported requests from unavailable optimizations and untested
settings. The VQ-LLM/EXION evaluation review supplies concrete evidence limits;
all fallback timings remain labeled teaching examples. Remaining HPCA themes
and the broader course review are unfinished.

HPCA themes 6–8 now explain transition work, evidence by component, task-specific
acceptance, and why changed workloads or hardware need another comparison.
All eight HPCA themes have received this source-relevance and plain-language
pass. That does not establish full-paper coverage or complete the course;
remaining conference routes and overall editorial/browser review are open.

The MICRO pass has begun. Theme 1 now explains TRRIP's code-use labels and
separates replacement prediction, value validity, and occupied fetch capacity.
The new examples are explicitly not reconstructions of TRRIP's policy. A local
evaluation note is exported with simulation and workload limits. The remaining
MICRO themes and broader review are unfinished.

MICRO theme 2 now explains Pimba's combined placement, sharing, and precision
changes, with simulated timing kept distinct from measured hardware. An
original subtotal example makes result identity and arrival order explicit.
Remaining MICRO themes and the wider course review remain open.

MICRO theme 3 now explains shared-scale rounding and MX+'s changed bit meaning,
with a concrete original example and relevant subtheme references. Quality,
software timing, and modeled hardware remain separate. The remaining MICRO
themes and overall course review are still unfinished.

MICRO theme 4 now connects scheduling costs to Task-LP and event-level storage
checks to OmniSim. The local review is exported with hardware, precomputed
grouping, and simulation boundaries intact. The next MICRO themes and broader
course review remain unfinished.

MICRO theme 5 now explains whole-request fallback versus separate remainder
handling, and connects restricted hardware support to RISSP's evaluation.
Timing predictions remain separate from evidence that the generated program
preserves behavior. The remaining MICRO themes and overall review stay open.

MICRO theme 6 now separates attack outcomes, numerical closeness, image quality,
and camera-estimation requirements with relevant evaluation sources and an
original combined acceptance test. Narrow-screen source-note overflow was
found and corrected in the shared source-page template. Remaining MICRO
themes and the overall course audit are unfinished.

MICRO themes 7/8 now connect physical-cost accounting to ReGate and controlled
comparisons to the commercial compute-in-SRAM study. All eight MICRO themes
have received this plain-language and source-relevance pass. This is not
full-paper coverage or completion of the broader course; remaining conference
routes and overall editorial/frontend verification remain open.

The SC review has begun with theme 1. A weighted-concentration example shows
how executable code can answer the wrong scientific question. InferA and
SimAI-Bench provide separate interpretation and workflow-timing connections,
with two local source reviews exported. Remaining SC themes and the broader
course review are unfinished.

SC theme 2 now explains cMPI shared-memory costs, LCI asynchronous transfers,
and D-CHAG memory/aggregation tradeoffs. Source reviews preserve simulation
and workload boundaries. The remaining SC themes and whole-course review
remain unfinished.

SC theme 3 now separates compression, numerical rounding, and joining
calculation stages, with concrete cuSZ-Hi/TurboFNO review connections.
An original subtraction example shows why per-input error bounds do not
guarantee the sign of a later result. Remaining SC themes and the wider
course audit remain open.

SC themes 4–6 now explain transfer overlap and buffer reuse, numerical
requirements when moving programs between devices, and why adding workers
can increase completion time. AGILE, FFTMatvec, and QuaTrEx replace generic
paper references. FFTMatvec is explicitly identified as an SC Workshops
paper; QuaTrEx's input/output exclusion remains visible. Themes 7–8 and
the broader conference writing and whole-course verification remain open.

SC theme 7 now separates numerical disagreement, invalid answers, and lost
work. LLM4FP supplies the false-positive boundary; LLMTailor supplies checks
on resumed training, with its SC Workshops status explicit. Recovery timing
states that completed saves must survive the specified failure. Theme 8 and
the broader conference writing and whole-course verification remain open.

SC theme 8 now explains measurement overhead, checking inferred hardware
properties, and calibrating a simulation, using MT4G and CGSim. An original
example separates matching the average from accurate individual predictions.
All eight SC themes have received this editorial/source-connection pass;
that is not a full-paper coverage claim or completed whole-course audit.
The remaining conference routes and whole-course verification remain open.

DAC theme 1 now separates skipped simulation work from predicted circuit
properties, using the local GSIM and NetTAG evaluation review. The adder
example explains why equal arithmetic and operation counts do not establish
equal delay. Remaining DAC themes and the wider course audit remain open.

DAC theme 2 now connects cache competition to CaMDN and module placement
to HH-PIM. The prose distinguishes simulated/modelled evidence from chip
measurements and replaces unrelated GSIM subtheme citations. Remaining DAC
themes and whole-course editorial and frontend verification remain open.

DAC theme 3 now connects stopping points and recent timing estimates to
DARIS, and inserted-work deadline checks to Tropical. An original example
counts switching in both directions before deciding whether added work fits.
Remaining DAC themes and the broader course review remain unfinished.

DAC theme 4 now separates repeated error amplification from interactions
between simultaneous changes, with CLADO and SQ-DM source connections.
Replaced stale carry/simulator subtheme notes with the actual worked examples.
Quality tests and simulated performance remain separate evidence claims.
DAC themes 5–8 and the broader course review remain unfinished.

DAC theme 5 now defines power versus energy, separates energy to completion
from energy over a fixed window, and connects phase-specific choices to
EdgeMM and HH-PIM. An original idle-power example explains reversed rankings.
DAC themes 6–8 and the broader course review remain unfinished.

DAC theme 6 now explains observer access through DeepPUFSCA power traces
and GNNVault's public/protected computation split. It distinguishes physical
measurement access from remote observation and replaces unrelated GSIM
security citations. DAC themes 7–8 and the broader course review remain open.

DAC theme 7 now separates numerical error from mistaken design acceptance,
using an equal-error threshold example and local LMM-IR evidence. Average
error is explicitly not a verified bound; benchmark and failed-comparison
limits remain visible. DAC theme 8 and the wider course review remain open.

DAC theme 8 now separates logical behavior, simulated circuit behavior,
implementation-tool results, and hardware measurements using WISEDRAM and
KLiNQ. All eight DAC themes have received this writing/source-connection
pass; this does not establish full proceedings coverage or whole-course
completion. Remaining conference routes and broad verification remain open.

DATE theme 1 now explains old/new-value dependencies and logical rewriting
through the SAT-sampling paper. The text distinguishes an equisatisfiable
transformation from valid returned assignments and sample variety. Added
the local evaluation review and replaced unrelated CorrectBench citations.
Remaining DATE themes and the broader course review remain open.

DATE theme 2 now connects manufacturing restrictions and sampled variation
to BOSON-1. An original feature-width example explains why repairing an
ideal winner can lose to selecting a buildable candidate. Conditional bounds
remain distinct from sampled performance. Remaining DATE themes and the
broader course review remain open.

DATE theme 3 now connects shared-memory delay to MC3's cooperating sender
and receiver, distinct from victim inference or data corruption. Fixed-slot
examples explicitly assume splittable transfers and prohibit borrowing;
the text explains why borrowing changes the observation. Remaining DATE
themes and the broader course review remain unfinished.

DATE theme 4 now explains CorrectBench's bounded repair loop and Eval2's
eight-of-ten report-agreement threshold, distinct from rejecting every fault.
Corrected stale counter notes to match the queue-order example. Remaining
DATE themes and the broader course review remain unfinished.

DATE theme 5 now connects selective precision to Cocktail, including its
higher-precision output and remainder exceptions and selection overhead.
Derived linear error bounds remain separate from model-quality tests and
invented fallback timing. DATE themes 6–8 and the wider review remain open.

DATE theme 6 now explains the CGRA paper's time-first, placement-second
search, its neighbor-register assumption, and timeout exclusions. Corrected
the reversed stage order in the local evaluation review as well as the course.
Compilation speed remains distinct from application execution speed.
DATE themes 7–8 and the broader review remain unfinished.

DATE theme 7 now distinguishes physical corruption, unwanted generated
behavior, and runtime control checks through EILID and RTL-Breaker. The
lesson states the allowed-target limitation and separates detection from
release ordering and recovery. DATE theme 8 and the wider review remain open.

DATE theme 8 now connects acceptance rules, partial versus full delivery,
compilation scope, and cache precision exceptions across the route. All eight
DATE themes have received this writing/source-connection pass; that does not
establish full proceedings coverage or whole-course completion. Remaining
conference routes and broad editorial/frontend verification remain open.

VLSID theme 1 now explains duration/error tradeoffs and connects control-bit
faults to simulated quantum outputs through the local three-paper review.
Occurrence rates remain separate from sensitivity, and the small source
sample remains explicit. Remaining VLSID themes and broader review remain open.

VLSID theme 2 now explains TimeFloats' alignment/conversion work and brings
the unresolved component-energy discrepancy into both the lesson and local
evaluation review. The numerical total was checked, not reconciled. Remaining
VLSID themes and the broader course review remain unfinished.

VLSID theme 3 now separates QuaLITi's noisy-simulator accuracy from real
queue observations and extrapolated whole-inference waits. Corrected the
local evaluation review's mixed-evidence description against the primary
setup and queue sections. Added an original changing-queue example.
VLSID theme 4 and the broader course review remain unfinished.

VLSID theme 4 now summarizes all three reviewed records in a bounded evidence
table and states the missing checks without claiming they were performed.
All four VLSID themes have received this editorial/source-connection pass;
energy discrepancies, broader paper coverage, remaining conference routes,
and whole-course verification remain unresolved or unfinished.

ISSCC theme 1 now connects its phase timing examples to the ConvFormer
digest's distinct storage, reuse, and sparse-work problems. Corrected the
local review to distinguish changed linear attention from exact reassociation.
The one-record coverage limit remains explicit. Remaining ISSCC lessons and
the broader review remain unfinished.

ISSCC theme 2 now separates storage lifetime, combined-stage execution,
and trained pruning, with a concrete ConvFormer scheduling connection.
The neighbor-value example shows why fusion does not remove dependencies.
Remaining ISSCC lessons and broad course verification remain unfinished.

ISSCC theme 3 now defines operations-per-energy accounting, contrasts
executed and dense-equivalent work, and locates the measured peak at its
stated voltage/frequency. Prior-device assumptions remain separate from
new chip measurements. ISSCC theme 4 and the broader review remain open.

ISSCC theme 4 now distinguishes tested combinations from missing conditions
and explicitly names the ConvFormer workload evidence and course-review
limits. All four ISSCC lessons have received this writing pass, not a full
conference synthesis. Remaining routes and whole-course checks remain open.
