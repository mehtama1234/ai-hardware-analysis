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
failure paths.

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

## Per-paper schema

`id, title, authors, venue, problem, motivation, method, key_novelty, contributions[],
hardware_target[], technique_category[], workloads[], metrics{}, baselines[], limitations,
tags[], primary_theme, confidence`. See [GOAL.md](GOAL.md).

## Principles

Resumable scripts; raw (PDF/text, gitignored) separated from interpretation (committed);
per-paper notes before synthesis; every skip/failure logged under `logs/` so gaps are visible.
