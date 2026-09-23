# AI-Hardware / Circuits / Architecture Conference Analysis

Local corpus + per-paper analysis + cross-corpus theme mining for the top AI-hardware,
computer-architecture, and circuits venues. See [GOAL.md](GOAL.md) for the full objective.

Sibling thread owns CVPR 2026 computer-vision papers; this thread owns the hardware side.

## Unified verification and inference product goal

The authoritative cross-repository execution handoff is
[END_TO_END_QUALIFICATION_HANDOFF.md](END_TO_END_QUALIFICATION_HANDOFF.md).
Print the current joined gate state with
`python3 scripts/report_end_to_end_status.py`.
Validate the handoff invariants with
`python3 scripts/validate_end_to_end_handoff.py`.

Run the complete provider-free cross-project acceptance with
`python3 scripts/run_local_unified_release_acceptance.py`. It joins the public
digital verification release with the bounded local transformer/profile/
fallback qualification and synthetic customer-pilot certification, then writes
`.artifacts/local-unified-release-acceptance.json`.
Verify that decision independently with
`python3 scripts/check_local_unified_release_acceptance.py`.
Name the current non-destructive worktree boundary with
`python3 scripts/build_local_checkpoint_manifest.py`.
Verify that checkpoint later with
`python3 scripts/check_local_checkpoint_manifest.py`.

Reproduce the complete local-only model-to-workload qualification, including
the bounded decision and joined manifest, with
`python3 scripts/run_local_end_to_end_qualification.py`. This path uses the
retained local GPT-2 receipts and does not require Colab, a GPU, or physical
hardware; it cannot authorize analog execution.

The resulting [local digital qualification package](evidence/local-digital-qualification-v1/local_digital_qualification_package.json)
and [counterfactual hybrid advantage report](evidence/counterfactual-hybrid-advantage-v2/counterfactual_hybrid_advantage_report.json)
join the 162-vector fallback proof with modeled cost sensitivity. The latter
is explicitly counterfactual: it is not measured energy or latency evidence.
To rebuild these derived artifacts without overwriting the immutable retained
evidence, run the one-command local check
`python3 scripts/run_local_derived_qualification.py`.
It creates fresh temporary outputs automatically. For explicit output paths,
use fresh directories, for example
`python3 scripts/build_local_digital_qualification_package.py --output /tmp/local-digital-qualification-rebuild`
followed by
`python3 scripts/build_counterfactual_hybrid_advantage_report.py --package /tmp/local-digital-qualification-rebuild --output /tmp/counterfactual-hybrid-advantage-rebuild`.
Run the corresponding `check_*.py` scripts as the acceptance gates; the
canonical retained packages remain under `evidence/`.
The same command also exports and checks a portable ZIP evidence bundle.

The cross-repository product objective is documented in
[UNIFIED_END_TO_END_PRODUCT_GOAL.md](UNIFIED_END_TO_END_PRODUCT_GOAL.md). It
connects the agentic digital-verification workbench, public benchmark, AIMC
model-to-hardware qualification, and commercial deployment path into one
evidence-backed ship/no-ship workflow.

The digital verification four-workstream implementation is summarized in
[the current status writeup](docs/roadmaps/four-workstream-implementation-status-2026-09-13.md),
with executable evidence in
`analog-digital-chip-design-eda/.artifacts/` and the detailed plan in
`docs/roadmaps/llm-autoformalization-extension-plan.md`.

## Pipeline

```
fetch_dblp.py   → metadata/<conf>-<year>-dblp.jsonl        # authoritative proceedings spine
enrich.py       → metadata/<conf>-<year>-enriched.jsonl    # abstract, arXiv id, OA PDF (OpenAlex)
scrape_mlsys.py → metadata/<conf>-<year>-fulltext.jsonl    # MLSys open-proceedings PDFs+abstracts
build_corpus.py → metadata/<conf>-<year>-corpus.jsonl      # unified records + chosen PDF + id
download_pdfs.py→ conferences/<conf>-<year>/pdfs/<id>.pdf   # resumable, 429 backoff
extract_text.py → conferences/<conf>-<year>/text/<id>.txt  # PyMuPDF (fitz)
make_batches.py → analysis/per-paper/batches/batch_NNN.jsonl
analyze.workflow.js → analysis/per-paper/<id>.{json,md}    # Sonnet fan-out, full-text deep read
                  → analysis/syntheses/                     # Opus theme synthesis
```

Run venv: `./.venv/bin/python` (Python 3.12; requests, beautifulsoup4, pymupdf).

## Data-source decisions (important — differs from the brief on purpose)

The brief specified **Semantic Scholar** for enrichment. From this environment the
unauthenticated S2 Graph API returns **HTTP 429 immediately** (no API key). Substituted
**OpenAlex** (proven reachable; same signals: abstract, OA PDF, arXiv id via title or DOI
lookup). This is the same enrichment source the sibling robotics corpus used successfully.

Full-text acquisition, by source reachability (tested):
- **arXiv PDF** — works (200, clean). Primary full-text source for matchable papers.
- **OpenReview PDF** — **403 Forbidden** (the wall the brief warned about). Not used.
- **MLSys open proceedings** (`proceedings.mlsys.org`) — works; index + per-paper PDFs at a
  predictable path. Used to get **100% full text** for the MLSys pilot, closing OpenAlex gaps.

For paywalled venues (ISCA/MICRO/HPCA/ASPLOS/ISSCC/DAC) expect a mix: OpenAlex abstract +
arXiv full text for the matchable subset, **abstract-only** (labeled `confidence: low`) for
the rest. Abstract-only is a first-class, labeled outcome — not a failure.

## Venue status

The project uses the latest complete, source-accessible edition rather than assuming that
a 2026 edition is available. A venue is promoted to 2026 only after its complete official
proceedings spine and source-access boundary have been verified. Until then, the 2025 or
2024 corpus remains the authoritative working edition.

| Venue | Edition | Papers | Analyzed | Full text (high) | Abstract-only (low) | Title-only (gap) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| MLSys | 2025 (pilot) | 61 | 61 | 61 | 0 | 0 |
| ISCA | 2025 | 135 | 112 | 17 | 95 | 23 |
| MICRO | 2025 | 123 | 47 | 20 | 27 | 76 |
| HPCA | 2025 | 121 | 119 | 8 | 111 | 2 |
| ASPLOS | 2025 | 179 | 164 | 14 | 150 | 15 |
| **total** | | **619** | **503** | **120** | **383** | **116** |

Full text is only obtainable where a paper is on arXiv or the venue has open proceedings
(MLSys). ACM/IEEE/doi.org PDF links are paywalled (403). MICRO is materially under-sampled —
IEEE withholds its abstracts from OpenAlex *and* Crossref and many papers aren't on arXiv, so
76/123 are title-only and unanalyzed. Cross-venue synthesis:
[`analysis/syntheses/cross-venue-2025-themes.md`](analysis/syntheses/cross-venue-2025-themes.md).
Big-picture conceptual page: [`mlsys-2025-bigpicture.html`](mlsys-2025-bigpicture.html).
Plain-language course spine: [`course.html`](course.html), covering the first-principles
story across hardware venues, including topology as wiring, placement, network shape, and
failure paths. Its learning sequence, conference coverage, source boundaries, and
remaining review work are recorded in [`CONFERENCE_COURSE_GOAL.md`](CONFERENCE_COURSE_GOAL.md).

The current first-principles integration across the source-backed MLSys, OSDI, ASPLOS, and
NSDI atlases is [`analysis/four-atlas-first-principles-integration.md`](analysis/four-atlas-first-principles-integration.md).
NSDI 2026 is an additional corpus and synthesis; it does not change the three existing
composition protocols, which remain explicitly specified-but-unrun.
The requirement-by-requirement state is recorded in
[`analysis/end-to-end-goal-audit-2026-09-21.md`](analysis/end-to-end-goal-audit-2026-09-21.md).
The next-corpus selection rule and ranked available venues are recorded in
[`analysis/next-corpus-selection-2026-09-21.md`](analysis/next-corpus-selection-2026-09-21.md).
The initial ISCA 2025 first-principles evidence boundary and conceptual seed are in
[`analysis/isca-2025-first-principles-seed.md`](analysis/isca-2025-first-principles-seed.md).
The completed source-backed ISCA adjudication is indexed in
[`analysis/isca-2025-full-evaluation-adjudication-011-017.md`](analysis/isca-2025-full-evaluation-adjudication-011-017.md)
and the preceding batches linked from that index.
Its evidence-bounded conceptual synthesis is
[`analysis/isca-2025-first-principles-synthesis.md`](analysis/isca-2025-first-principles-synthesis.md).
The source-backed ISCA bridge into the existing systems atlas is
[`analysis/isca-2025-cross-atlas-bridge.md`](analysis/isca-2025-cross-atlas-bridge.md).
HPCA 2025 is the next available architecture corpus; its evidence boundary and initial
source-backed anchor review are in
[`analysis/hpca-2025-first-principles-seed.md`](analysis/hpca-2025-first-principles-seed.md)
and [`analysis/hpca-2025-source-backed-anchor-review.md`](analysis/hpca-2025-source-backed-anchor-review.md).
The completed HPCA evaluation adjudication is in
[`analysis/hpca-2025-full-evaluation-adjudication.md`](analysis/hpca-2025-full-evaluation-adjudication.md).
The evidence-bounded HPCA synthesis is in
[`analysis/hpca-2025-first-principles-synthesis.md`](analysis/hpca-2025-first-principles-synthesis.md).
MICRO 2025 follows with a materially under-sampled but source-partitioned corpus; its seed
and anchor review are in
[`analysis/micro-2025-first-principles-seed.md`](analysis/micro-2025-first-principles-seed.md)
and [`analysis/micro-2025-source-backed-anchor-review.md`](analysis/micro-2025-source-backed-anchor-review.md).
All 20 locally extracted MICRO records now have full evaluation adjudications, indexed in
the four batch documents; the synthesis is in
[`analysis/micro-2025-first-principles-synthesis.md`](analysis/micro-2025-first-principles-synthesis.md)
and its cross-atlas bridge is in
[`analysis/micro-2025-cross-atlas-bridge.md`](analysis/micro-2025-cross-atlas-bridge.md).
The unified seven-atlas conceptual integration is
[`analysis/seven-atlas-first-principles-integration.md`](analysis/seven-atlas-first-principles-integration.md).
SC 2025 is the next large-scale-systems corpus: its initial source partition and
first-principles seed are in
[`metadata/sc-2025-source-acquisition-audit.json`](metadata/sc-2025-source-acquisition-audit.json)
and [`analysis/sc-2025-first-principles-seed.md`](analysis/sc-2025-first-principles-seed.md).
DAC 2025 is the next hardware/EDA layer. Its source boundary is recorded in
[`metadata/dac-2025-source-acquisition-audit.json`](metadata/dac-2025-source-acquisition-audit.json),
and its provisional first-principles conceptual seed is in
[`analysis/dac-2025-first-principles-seed.md`](analysis/dac-2025-first-principles-seed.md).
The first DAC source-backed adjudication batch is
[`analysis/dac-2025-full-evaluation-adjudication-001-008.md`](analysis/dac-2025-full-evaluation-adjudication-001-008.md).
The second DAC source-backed adjudication batch is
[`analysis/dac-2025-full-evaluation-adjudication-009-016.md`](analysis/dac-2025-full-evaluation-adjudication-009-016.md).
The third DAC source-backed adjudication batch is
[`analysis/dac-2025-full-evaluation-adjudication-017-024.md`](analysis/dac-2025-full-evaluation-adjudication-017-024.md).
The completed DAC source-backed synthesis is
[`analysis/dac-2025-first-principles-synthesis.md`](analysis/dac-2025-first-principles-synthesis.md),
with its bounded release state in
[`metadata/dac-2025-first-principles-synthesis.json`](metadata/dac-2025-first-principles-synthesis.json).
ISSCC 2025 is the next circuits-layer corpus; its abstract-heavy source boundary is
recorded in [`metadata/isscc-2025-source-acquisition-audit.json`](metadata/isscc-2025-source-acquisition-audit.json)
and [`analysis/isscc-2025-source-acquisition-audit.md`](analysis/isscc-2025-source-acquisition-audit.md).
The one ISSCC primary-source adjudication is
[`analysis/isscc-2025-source-backed-adjudication-001.md`](analysis/isscc-2025-source-backed-adjudication-001.md);
ISSCC has not yet been promoted to a corpus-wide synthesis because 257 records remain
abstract/title-only.
ICCAD 2025 is also source-partitioned as an abstract-only EDA corpus in
[`metadata/iccad-2025-source-acquisition-audit.json`](metadata/iccad-2025-source-acquisition-audit.json)
and [`analysis/iccad-2025-source-acquisition-audit.md`](analysis/iccad-2025-source-acquisition-audit.md).
DATE 2025 is the next source-backed EDA/systems bridge, with its acquisition boundary in
[`metadata/date-2025-source-acquisition-audit.json`](metadata/date-2025-source-acquisition-audit.json)
and [`analysis/date-2025-source-acquisition-audit.md`](analysis/date-2025-source-acquisition-audit.md).
The first DATE source-backed adjudication batch is
[`analysis/date-2025-full-evaluation-adjudication-001-008.md`](analysis/date-2025-full-evaluation-adjudication-001-008.md).
The completed DATE source-backed synthesis is
[`analysis/date-2025-first-principles-synthesis.md`](analysis/date-2025-first-principles-synthesis.md),
with its bounded release state in
[`metadata/date-2025-first-principles-synthesis.json`](metadata/date-2025-first-principles-synthesis.json).
VLSID 2025 is now source-partitioned and synthesized for its three local texts in
[`analysis/vlsid-2025-first-principles-synthesis.md`](analysis/vlsid-2025-first-principles-synthesis.md).
FCCM 2025 is source-partitioned as an abstract-heavy reconfigurable-computing corpus in
[`metadata/fccm-2025-source-acquisition-audit.json`](metadata/fccm-2025-source-acquisition-audit.json)
and [`analysis/fccm-2025-source-acquisition-audit.md`](analysis/fccm-2025-source-acquisition-audit.md);
its three advertised repository links are not yet validated as local primary-text sources.

## Current three-atlas end-to-end track

The active release-candidate track is narrower than the broad corpus pipeline above. It
follows the causal path from a requested result to dependable service behavior across:

| Atlas | Corpus | Current evidence boundary | Release state |
| --- | ---: | --- | --- |
| MLSys 2025 | 61 | 61/61 source-backed semantic-adjudication decisions; paper-reported evidence | `source-backed-semantic-adjudication-complete` |
| OSDI 2025 | 53 | 53/53 primary-PDF section and result-anchor confirmations; no independent reproduction | `primary-pdf-adjudication-complete` |
| ASPLOS 2025 | 179 | 60 local source-text records (59 paper-level adjudications plus 1 presentation-text record), with separately bounded abstract, artifact, and external-abstract evidence | `bounded-evidence-release-boundary-verified` |

The three atlases are connected through specified-but-unrun composition protocols for
distributed training, LLM serving, and durable/recoverable state. The top-level release
audit has one blocker: execute those protocols in a common pinned runtime. Passing audits
must not be read as independent reproduction or as evidence that paper-local speedups
compose automatically. See [the end-to-end review](END_TO_END_GOAL_REVIEW_2026-09-20.md),
[the closure index](analysis/osdi-asplos-mlsys-2025-cross-atlas-closure-index.md), and
[the machine-readable release audit](metadata/three-atlas-release-readiness-audit-2026-09-20.json).

## Hands-on GPU / serving lab goal

The next meaty end-to-end tutorial track is specified in
[`gpu-kernels-serving-lab/MEATY-GOAL.md`](gpu-kernels-serving-lab/MEATY-GOAL.md). It extends
the existing Kimi K3 lab style into Hugging Face baselines, JAX Scaling Book cost models,
CUDA kernels, Triton kernels, ROCm/HIP portability, quantization, vLLM/TGI serving, and a
mini LLM serving-engine capstone.

The next source-backed expansion starts from GPUMODE lectures:
[`gpu-mode-curriculum/MEATY-GOAL.md`](gpu-mode-curriculum/MEATY-GOAL.md). It captures
YouTube metadata/transcripts, maps lessons into GPU-systems topics, extracts lesson
intelligence, and proposes deeper runnable labs that extend the kernel/serving track.

For the AI-hardware product, the next goal that can be completed without Colab
or hardware is the [replayable model-to-chip qualification package](docs/roadmaps/next-local-meaty-goal-replayable-model-to-chip-package.md).

(2026 editions of most venues are not yet indexed on DBLP — scale on the latest complete
editions, upgrading a venue once DBLP shows its full list.)

The broad venue table above is a legacy acquisition snapshot, not the current release
boundary. For the end-to-end atlas, use the audited 2025 corpora and only add a 2026
venue after its complete official corpus and source-access boundary are verified. If a
2026 edition is unavailable, continue with the latest complete edition already present
 in the repository; no downstream analysis or composition protocol depends on a 2026
 edition.

## Per-paper schema

`id, title, authors, venue, problem, motivation, method, key_novelty, contributions[],
hardware_target[], technique_category[], workloads[], metrics{}, baselines[], limitations,
tags[], primary_theme, confidence`. See [GOAL.md](GOAL.md).

## Principles

Resumable scripts; raw (PDF/text, gitignored) separated from interpretation (committed);
per-paper notes before synthesis; every skip/failure logged under `logs/` so gaps are visible.
