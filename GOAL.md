# Goal: AI-Hardware / Circuits / Architecture Conference Theme Mining

## Objective

Build a local corpus of papers from the top AI-hardware, computer-architecture, and
circuits conferences, and analyze every paper to extract — for each — (1) the problem it
solves, (2) the method/design in technical detail, (3) the contribution. Then mine common
themes across the corpus: recurring mechanisms, design patterns, workloads, and metrics
(speedup / energy / area / PPA).

Sibling thread owns CVPR 2026 computer-vision papers; this thread owns the hardware side.
Different folders — no collision.

## Target venues (latest complete edition available)

Flagship: **ISCA, MICRO, HPCA, ASPLOS** (architecture), **ISSCC** (circuits), **DAC**, **MLSys**.
Optional: VLSI Symposium, ICCAD, DATE, Hot Chips, SC, FPGA/FCCM.
~90–300 papers each; ~1,000–1,500 total.

As of the project start most **2026** proceedings are not yet indexed on DBLP (conferences
not yet held / published). Pilot + scale on the **latest complete editions** (2025 for most),
upgrading a venue to its 2026 edition once DBLP shows a full list.

**Pilot:** MLSys 2025 — fully open proceedings (proceedings.mlsys.org) → validates the
hardest path end-to-end (full-text → PyMuPDF → high-confidence deep read).

## Sources (hybrid — most hardware venues are paywalled)

- **DBLP** — authoritative complete proceedings list per venue/year. The spine
  (title/authors/DOI/ee).
- **Semantic Scholar Graph API** (primary) / **OpenAlex** (proven fallback) — abstracts,
  open-access PDF links, arXiv external IDs, by DOI.
- **arXiv (cs.AR)** — full text for the matchable subset.
- **MLSys open proceedings** — free full text for the pilot venue.
- ISSCC / VLSI / Hot Chips are industry → many abstract-only; that is a labeled, first-class
  outcome, not a failure.

## Depth policy (hybrid)

- Full-text deep read where a PDF is obtainable; else abstract-only.
- Every analysis carries a **confidence** field: `high` = full text, `low` = abstract-only.
- Report the full-text vs abstract-only split honestly. Do NOT scrape OpenReview/arXiv to
  force full text (403/429 walls) — treat abstract-only as a labeled outcome.

## Pipeline

1. `fetch_dblp.py`   → `metadata/<venue>-<year>-dblp.jsonl`
2. `enrich.py`       → `+abstract, +arxiv_id, +oa_pdf` (Semantic Scholar / OpenAlex)
3. `download_pdfs.py`→ resumable, ~0.4s delay, 429 backoff; only obtainable PDFs
4. `extract_text.py` → PyMuPDF (fitz), NOT pypdf
5. `analyze.workflow.js` → per-paper JSON + MD via Sonnet fan-out (~15 papers/agent)
6. theme synthesis   → cluster tags, normalize themes, cross-corpus write-up on Opus

## Per-paper schema

`id, title, authors, venue, problem, motivation, method (detailed how), key_novelty,
contributions[], hardware_target[] (GPU/ASIC/FPGA/CIM/CPU/chiplet/photonic/analog),
technique_category[] (dataflow/quantization/sparsity/memory-system/interconnect/compiler/
circuit-design/packaging/power), workloads[] (LLM inference/training/CNN/…),
metrics (speedup/TOPS-W/area/PPA), baselines[], limitations, tags[], primary_theme, confidence`

## Principles

- Resumable scripts (safe to re-run; skip papers whose `<id>.json` exists).
- Separate raw (PDF/text) from interpretation (analyses/themes).
- Per-paper notes before synthesis.
- `.gitignore` the PDFs/text; commit metadata + analyses.
- Log everything skipped (paywalled / no-PDF / failed-match) so gaps aren't mistaken for coverage.
