#!/usr/bin/env python3
"""Enrich a DBLP JSONL with abstracts from Semantic Scholar via DOI lookup.

Usage: python3 scripts/enrich_s2.py --conf isscc --year 2025
Reads:  metadata/<conf>-<year>-dblp.jsonl
Writes: metadata/<conf>-<year>-enriched.jsonl
"""
import argparse, json, time, urllib.request, urllib.error, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S2_BASE = "https://api.semanticscholar.org/graph/v1/paper"
FIELDS  = "title,abstract,year,venue,openAccessPdf,externalIds"
DELAY   = 0.35   # S2 free tier: ~3 req/s


def doi_from_ee(ee):
    if not ee:
        return None
    m = re.search(r'doi\.org/(.+)', str(ee))
    return m.group(1) if m else None


def fetch_s2(doi):
    url = f"{S2_BASE}/DOI:{urllib.parse.quote(doi, safe='')}?fields={FIELDS}"
    try:
        with urllib.request.urlopen(url, timeout=12) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  429 — backing off 10s")
            time.sleep(10)
        return None
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()

    src = ROOT / f"metadata/{args.conf}-{args.year}-dblp.jsonl"
    out = ROOT / f"metadata/{args.conf}-{args.year}-enriched.jsonl"

    papers = [json.loads(l) for l in src.open()]
    # resume: skip already-done
    done = set()
    existing = []
    if out.exists():
        for l in out.open():
            r = json.loads(l)
            done.add(r.get("doi") or r.get("title"))
            existing.append(r)

    print(f"{len(papers)} papers, {len(done)} already enriched")

    import urllib.parse
    results = list(existing)
    for i, p in enumerate(papers):
        doi = doi_from_ee(p.get("ee", ""))
        key = doi or p.get("title", "")
        if key in done:
            continue

        row = {
            "title":    p.get("title", ""),
            "authors":  p.get("authors", []),
            "doi":      doi or "",
            "ee":       p.get("ee", ""),
            "year":     p.get("year", args.year),
            "venue":    args.conf.upper(),
            "type":     p.get("type", ""),
            "key":      p.get("key", ""),
            "abstract": "",
            "arxiv_id": "",
            "oa_pdf":   "",
        }

        if doi:
            s2 = fetch_s2(doi)
            if s2:
                row["abstract"] = s2.get("abstract") or ""
                pdf = (s2.get("openAccessPdf") or {}).get("url", "")
                row["oa_pdf"]   = pdf or ""
                ext = s2.get("externalIds") or {}
                row["arxiv_id"] = ext.get("ArXiv", "")
            time.sleep(DELAY)

        results.append(row)
        done.add(key)

        # write incrementally every 20 papers so progress survives a kill
        if len(results) % 20 == 0:
            with out.open("w") as fh:
                for r in results:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            has_abs = sum(1 for r in results if r.get("abstract"))
            print(f"  {len(results)}/{len(papers)+len(existing)} — {has_abs} with abstracts", flush=True)

    with out.open("w") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    has_abs = sum(1 for r in results if r.get("abstract"))
    has_pdf = sum(1 for r in results if r.get("oa_pdf"))
    print(f"wrote {len(results)} -> {out} | abstracts:{has_abs} pdfs:{has_pdf}")


if __name__ == "__main__":
    main()
