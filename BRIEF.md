# Task Brief: AI-Hardware / Circuits / GPU Conference Analysis

## Objective

Build a local corpus of papers from the top **AI-hardware, computer-architecture,
and circuits** conferences, then analyze **every** paper to extract, for each:

1. **The problem** it addresses (and why it matters / the gap).
2. **The method / design — in technical detail** (architecture, circuit/dataflow, key
   idea, what's actually built, how evaluated).
3. **The contribution** (core novelty + enumerated claims).

Then mine **common themes** across the corpus: recurring problems, mechanisms,
design patterns, workloads, and metrics (speedup / energy / area / PPA).

Do it in its own folder: `~/ui-projects/ai-hardware-analysis/` (create it; `git init`).

## Scope — target conferences (use 2026 editions, or latest available by now)

Core set (AI accelerators, architecture, circuits):
- **ISCA 2026** (Int'l Symposium on Computer Architecture) — ~June
- **MICRO 2026** (Microarchitecture) — ~Oct (may NOT be published yet; check)
- **HPCA 2026** (High-Performance Computer Architecture) — ~Feb/Mar
- **ASPLOS 2026** (Arch. Support for PL & OS) — ~spring
- **ISSCC 2026** (Int'l Solid-State Circuits Conf) — ~Feb — the top *circuits* venue
- **DAC 2026** (Design Automation Conf) — ~June
- **MLSys 2026** (ML & Systems) — ~May — open proceedings, ML-HW co-design

Optional add-ons: VLSI Symposium, ICCAD, DATE, Hot Chips, SC, FPGA/FCCM.

**Recommended first pass:** one flagship venue end-to-end as a pilot (suggest **ISCA
2026** or **MLSys 2026** since MLSys has free full-text), prove the pipeline, then scale
to the rest. These venues are far smaller than CV conferences (~90–300 papers each), so
the *whole set* is ~1,000–1,500 papers — more tractable than a single CVPR.

## CRITICAL: data-source reality (this is the main difference from CV work)

Unlike CVF (which serves CVPR/ICCV PDFs freely), most of these venues are on **IEEE
Xplore / ACM Digital Library and are PAYWALLED**. Plan for a **hybrid**:

- **Metadata (all papers):** use **DBLP** — `https://dblp.org/db/conf/<venue>/<venue><year>.html`
  (e.g. `.../conf/isca/isca2026.html`). DBLP has complete, clean title/author/DOI lists.
  There is also a DBLP API returning XML/JSON. This is your spine.
- **Abstracts + open-access PDFs:** the **Semantic Scholar Graph API**
  (`https://api.semanticscholar.org/graph/v1/paper/...`, free; ~1 req/sec unauthenticated —
  be polite, add a key if you have one). Fields: `abstract`, `openAccessPdf`, `externalIds`
  (arXiv/DOI). Great for matching each DBLP paper to an abstract and an OA PDF when one exists.
- **Full text (subset):** **arXiv** (many architecture papers, category `cs.AR`, are here).
  Download the PDF when Semantic Scholar/arXiv gives a confident match.
- **MLSys** has **open proceedings** (`https://proceedings.mlsys.org`) with free PDFs —
  scrape like CVF.
- **ISSCC / VLSI / Hot Chips** are largely industry and rarely on arXiv → expect
  **abstract-only** for many. That's fine — record it.

**Depth policy:** full-text deep read where a PDF is obtainable (arXiv/OA/MLSys);
**abstract-only** otherwise. Put a `confidence` field on every analysis
(`high` = full text, `low` = abstract-only). Be honest in the final report about
what fraction was full-text vs abstract-only. (A prior sibling project stalled by
trying to force full-text via OpenReview/arXiv and hitting 403/429 walls — don't
repeat that; treat abstract-only as a first-class, labeled outcome.)

## Folder structure

```
~/ui-projects/ai-hardware-analysis/
  GOAL.md  README.md  .gitignore
  scripts/            # fetch_dblp.py, enrich_semanticscholar.py, download_pdfs.py, extract_text_fast.py
  metadata/           # <venue>-<year>.jsonl  (id, title, authors, doi, arxiv_id, pdf_url, abstract)
  conferences/<venue>-<year>/pdfs/   # git-ignored (large)
  conferences/<venue>-<year>/text/   # git-ignored
  analysis/per-paper/ # <id>.json + <id>.md  (one per paper)
  analysis/themes/    # theme taxonomy + evidence
  analysis/syntheses/ # cross-venue narrative
  logs/
```
`.gitignore`: `.venv/`, `conferences/*/pdfs/`, `conferences/*/text/`, `logs/*.log`, `__pycache__/`.
Track metadata + analysis; NOT the PDFs/text.

## Pipeline

1. **Metadata** — scrape DBLP per venue/year → `metadata/<venue>-<year>.jsonl`
   (`id`, `title`, `authors`, `doi`).
2. **Enrich** — for each paper, query Semantic Scholar → add `abstract`, `arxiv_id`,
   `openAccessPdf`. Rate-limit ~1 req/sec; cache; make it resumable.
3. **Download** — fetch PDFs for papers with an arXiv/OA URL → `pdfs/<id>.pdf`.
   Resumable (skip existing); polite delay (~0.4s); retry on 429 with backoff.
4. **Extract text** — use **PyMuPDF (`fitz`)**, NOT pypdf (pypdf is ~10–50× slower and
   will take many hours). `pip install pymupdf`. Resumable.
5. **Per-paper analysis** — fan out with a Workflow (see below). Each agent reads the
   paper text (or abstract if no PDF) and writes `analysis/per-paper/<id>.json` + `.md`.
6. **Theme synthesis** — cluster on `tags`, normalize `primary_theme` into a fixed
   taxonomy, write `analysis/themes/` + `analysis/syntheses/` with paper-level evidence.

## Per-paper schema (JSON; write `<id>.json` + a readable `<id>.md`)

```json
{
  "id": "...", "title": "...", "authors": ["..."], "venue": "ISCA 2026",
  "problem": "2-4 sentences: the problem addressed",
  "motivation": "the gap / why it matters",
  "method": "HOW it works, in technical detail (4-8 sentences): architecture, dataflow / circuit / microarchitecture, key idea, what is built, how evaluated",
  "key_novelty": "one crisp sentence",
  "contributions": ["..."],
  "hardware_target": ["GPU","ASIC","FPGA","CIM/PIM","CPU","chiplet","photonic","analog","other"],
  "technique_category": ["dataflow","quantization","sparsity","memory-system","interconnect/NoC","compiler/mapping","circuit-design","packaging","cooling/power","other"],
  "workloads": ["LLM inference","training","CNN","recommendation","graph","other"],
  "metrics": "headline quantitative results (speedup, energy/efficiency TOPS/W, area, PPA, accuracy)",
  "baselines": ["what it is compared against"],
  "limitations": "stated or clearly-inferred",
  "tags": ["topical keywords for theme mining"],
  "primary_theme": "high-level bucket",
  "confidence": "high | low"   // high = full text, low = abstract-only
}
```

## Orchestration (Workflow) — bake in these lessons

- Use the **Workflow** tool to fan out per-paper analysis. **Batch ~15 papers per agent**
  (an agent reads each text file and writes each JSON+MD, returns a small summary).
- **Total agents per workflow are capped at 1,000**, and concurrent agents at ~16. With
  ~1,500 papers / 15 = ~100 agents, one workflow run suffices. (If you ever exceed 1,000
  agents, split across multiple runs — it's resumable if agents skip papers whose
  `<id>.json` already exists, or if you pass only the unanalyzed id list.)
- **GOTCHA — `args` arrives as a STRING:** if you pass an id array via Workflow `args`,
  guard with `const ids = Array.isArray(args) ? args : JSON.parse(args)`. (Passing a
  stringified list otherwise makes `ids.slice()` chop the *string*, spawning garbage.)
- **Models:** bulk per-paper analysis on **Claude Sonnet 4.6** (`model: 'sonnet'` in the
  agent opts) — good quality for structured extraction at ~1/5 the cost of Opus.
  Reserve **Claude Opus 4.8** (`model: 'opus'`) for the theme-synthesis pass.
- Validate on ~20 papers first, eyeball quality, THEN run the full corpus.
- Note: `primary_theme` tends to come out too granular (near-unique per paper). Cluster
  on the repeated **`tags`** and normalize themes into a fixed taxonomy at synthesis time.

## Operating principles

- **Resumable**: every script skips completed work; safe to re-run.
- **Separate raw from interpretation** (PDFs/text vs analysis).
- **Per-paper notes before global synthesis.**
- **Record uncertainty** (the `confidence` field) and **log anything skipped** (paywalled,
  no PDF, failed match) — don't let silent gaps read as full coverage.
- Commit metadata + analyses to git; keep PDFs/text git-ignored.

## First concrete steps for the new thread

1. Create the folder + `git init` + a venv (`python -m venv .venv`; `pip install requests
   beautifulsoup4 pymupdf`).
2. Write `fetch_dblp.py`, run it for the pilot venue (ISCA 2026 or MLSys 2026) →
   inspect the metadata JSONL.
3. Enrich with Semantic Scholar; download the obtainable PDFs; extract text.
4. Run a 20-paper validation of the analysis workflow; show the schema output.
5. Report back with counts (papers, full-text vs abstract-only) before the full run.
```
```
```
```
(End of brief.)
