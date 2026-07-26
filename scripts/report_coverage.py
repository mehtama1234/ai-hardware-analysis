#!/usr/bin/env python3
"""Honest coverage report per venue: how many papers, how much full text vs abstract-only,
and how many were actually analyzed. Writes COVERAGE.md at repo root (regenerated each run).

Reads metadata/*-corpus.jsonl and analysis/per-paper/*.json.
Usage: python3 scripts/report_coverage.py
"""
import glob, json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    rows = []
    for corpus in sorted(glob.glob(str(ROOT / "metadata" / "*-corpus.jsonl"))):
        name = Path(corpus).stem.replace("-corpus", "")   # e.g. mlsys-2025
        recs = [json.loads(l) for l in open(corpus)]
        n = len(recs)
        pdf = sum(1 for r in recs if r.get("pdf_url"))
        abs_only = sum(1 for r in recs if not r.get("pdf_url") and r.get("abstract"))
        title_only = sum(1 for r in recs if not r.get("pdf_url") and not r.get("abstract"))
        # analyzed
        adir = ROOT / "analysis" / "per-paper"
        analyzed = [json.load(open(f)) for f in glob.glob(str(adir / f"{name}-*.json"))]
        hi = sum(1 for a in analyzed if a.get("confidence") == "high")
        lo = sum(1 for a in analyzed if a.get("confidence") == "low")
        rows.append((name, n, pdf, abs_only, title_only, len(analyzed), hi, lo))

    lines = ["# Coverage report", "",
             "Honest split of what was actually obtained per venue. `full_text` = PDF obtained and",
             "extracted (analyzed at `high` confidence); `abstract_only` = abstract but no PDF",
             "(`low`); `title_only` = neither (paywalled, logged as a gap — not silently dropped).",
             "",
             "| venue-year | papers | full_text | abstract_only | title_only | analyzed | high | low |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} |")
    tot = [sum(r[i] for r in rows) for i in range(1, 8)]
    lines.append(f"| **total** | {tot[0]} | {tot[1]} | {tot[2]} | {tot[3]} | {tot[4]} | {tot[5]} | {tot[6]} |")
    out = "\n".join(lines) + "\n"
    (ROOT / "COVERAGE.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
