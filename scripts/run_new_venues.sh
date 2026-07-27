#!/bin/bash
# Full pipeline for new venues: DBLP → enrich → arxiv fallback → corpus → batches
# Run from the project root.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY=python3

run_venue() {
  local conf="$1" year="$2"
  echo "=== $conf $year ==="

  # 1. fetch DBLP (skip if already done)
  local dblp="metadata/${conf}-${year}-dblp.jsonl"
  if [ -f "$dblp" ]; then
    echo "  DBLP already fetched: $(wc -l < $dblp) papers"
  else
    echo "  Fetching DBLP..."
    $PY scripts/fetch_dblp.py --conf "$conf" --year "$year"
    echo "  Fetched: $(wc -l < $dblp) papers"
  fi

  # 2. enrich with OpenAlex
  local enr="metadata/${conf}-${year}-enriched.jsonl"
  if [ -f "$enr" ]; then
    echo "  Enriched already: $(wc -l < $enr) papers"
  else
    echo "  Enriching with OpenAlex..."
    $PY scripts/enrich.py --conf "$conf" --year "$year"
    echo "  Enriched: $(wc -l < $enr) papers"
  fi

  # 3. arXiv fallback for title-only papers
  echo "  Running arXiv fallback..."
  $PY scripts/enrich_arxiv.py --conf "$conf" --year "$year" 2>/dev/null || true

  # 4. build corpus
  echo "  Building corpus..."
  $PY scripts/build_corpus.py --conf "$conf" --year "$year"
  echo "  Corpus: $(wc -l < metadata/${conf}-${year}-corpus.jsonl) papers"

  # 5. make batches
  echo "  Making batches..."
  $PY scripts/make_batches.py --conf "$conf" --year "$year"
}

# Run venues sequentially
for arg in "$@"; do
  conf="${arg%:*}"
  year="${arg#*:}"
  run_venue "$conf" "$year"
done

echo ""
echo "All done. Check analysis/per-paper/batches/ for batch files."
echo "Batch counts:"
ls analysis/per-paper/batches/ | grep -oP '^[a-z0-9]+-\d+' | sort | uniq -c
