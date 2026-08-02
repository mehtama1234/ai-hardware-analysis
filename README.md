# AI-Hardware / Circuits / Architecture Conference Analysis

Local corpus + per-paper analysis + cross-corpus theme mining for the top AI-hardware,
computer-architecture, and circuits venues. See [GOAL.md](GOAL.md) for the full objective.

Sibling thread owns CVPR 2026 computer-vision papers; this thread owns the hardware side.

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

(2026 editions of most venues are not yet indexed on DBLP — scale on the latest complete
editions, upgrading a venue once DBLP shows its full list.)

## Per-paper schema

`id, title, authors, venue, problem, motivation, method, key_novelty, contributions[],
hardware_target[], technique_category[], workloads[], metrics{}, baselines[], limitations,
tags[], primary_theme, confidence`. See [GOAL.md](GOAL.md).

## Principles

Resumable scripts; raw (PDF/text, gitignored) separated from interpretation (committed);
per-paper notes before synthesis; every skip/failure logged under `logs/` so gaps are visible.
