#!/usr/bin/env python3
"""Merge DBLP spine + OpenAlex enrichment + (venue) full-text mapping into one corpus file.

Assigns a stable id (<conf>-<year>-NNN), chooses the best PDF source and abstract, and marks
which papers have obtainable full text. Writes metadata/<conf>-<year>-corpus.jsonl.

PDF source preference: venue open-proceedings PDF > arXiv > OpenAlex OA PDF.
Abstract preference:   venue proceedings abstract > OpenAlex abstract.

Usage: python3 scripts/build_corpus.py --conf mlsys --year 2025
"""
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_jsonl(p):
    return [json.loads(l) for l in p.open()] if p.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    a = ap.parse_args()
    md = ROOT / "metadata"
    dblp = load_jsonl(md / f"{a.conf}-{a.year}-dblp.jsonl")
    enr = {r["key"]: r for r in load_jsonl(md / f"{a.conf}-{a.year}-enriched.jsonl")}
    ft = {r["key"]: r for r in load_jsonl(md / f"{a.conf}-{a.year}-fulltext.jsonl") if r.get("key")}

    out = md / f"{a.conf}-{a.year}-corpus.jsonl"
    n_full = n_abs = 0
    with out.open("w") as fh:
        for i, d in enumerate(dblp):
            key = d["key"]
            e = enr.get(key, {})
            f = ft.get(key, {})
            pid = f"{a.conf}-{a.year}-{i:03d}"

            # choose pdf url + source. Only mark a PDF as obtainable if it is GENUINELY open:
            # publisher landing pages (ACM/IEEE/doi.org/Springer) are paywalled (403) and don't count.
            PAYWALLED = ("dl.acm.org", "doi.org", "ieeexplore.ieee.org", "link.springer.com",
                         "dial.uclouvain.be", "sciencedirect.com")
            pdf_url, src = None, None
            oa = e.get("oa_pdf") or ""
            oa_host = oa.split("/")[2] if "//" in oa else ""
            if f.get("pdf_url"):
                pdf_url, src = f["pdf_url"], "proceedings"
            elif e.get("arxiv_id"):
                pdf_url, src = f"https://arxiv.org/pdf/{e['arxiv_id']}", "arxiv"
            elif oa and oa_host not in PAYWALLED:
                pdf_url, src = oa, "openalex-oa"

            abstract = f.get("abstract") or e.get("abstract")
            rec = {
                "id": pid,
                "key": key,
                "title": d["title"],
                "authors": d.get("authors"),
                "venue": a.conf.upper(),
                "year": a.year,
                "doi": d.get("doi") or e.get("oa_doi"),
                "arxiv_id": e.get("arxiv_id"),
                "abstract": abstract,
                "pdf_url": pdf_url,
                "pdf_source": src,
                "cited_by_count": e.get("cited_by_count"),
                "concepts": e.get("concepts"),
                # confidence is upgraded to "high" after full text is actually extracted
                "expected_confidence": "high" if pdf_url else ("low" if abstract else "none"),
            }
            n_full += bool(pdf_url)
            n_abs += bool(abstract)
            fh.write(json.dumps(rec) + "\n")
    print(f"corpus={len(dblp)}  pdf_obtainable={n_full}  abstract={n_abs}  -> {out}")


if __name__ == "__main__":
    main()
