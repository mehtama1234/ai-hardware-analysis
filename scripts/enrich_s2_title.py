#!/usr/bin/env python3
"""Enrich DBLP JSONL using Semantic Scholar title search (for venues without DOIs like USENIX).

Usage: python3 scripts/enrich_s2_title.py --conf osdi --year 2025
Reads:  metadata/<conf>-<year>-dblp.jsonl
Writes: metadata/<conf>-<year>-enriched.jsonl
"""
import argparse, json, time, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,abstract,year,venue,openAccessPdf,externalIds,citationCount"
DELAY = 1.0


def search_s2(title):
    params = urllib.parse.urlencode({"query": title, "fields": FIELDS, "limit": 3})
    url = f"{S2_SEARCH}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ai-hw-corpus/1.0 (mailto:mehtama1@gmail.com)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        results = data.get("data", [])
        if not results:
            return None
        # Find best match: exact title match preferred, then first result
        title_lower = title.lower().strip().rstrip(".")
        for r in results:
            if r.get("title", "").lower().strip().rstrip(".") == title_lower:
                return r
        # Return first if no exact match
        return results[0]
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  429 — backing off 30s")
            time.sleep(30)
        return None
    except Exception as e:
        print(f"  error: {e}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()

    src = ROOT / f"metadata/{args.conf}-{args.year}-dblp.jsonl"
    out = ROOT / f"metadata/{args.conf}-{args.year}-enriched.jsonl"

    papers = [json.loads(l) for l in src.open()]
    done = set()
    existing = []
    if out.exists():
        for l in out.open():
            r = json.loads(l)
            done.add(r.get("title", ""))
            existing.append(r)

    print(f"{len(papers)} papers, {len(done)} already enriched")
    results = list(existing)

    for i, p in enumerate(papers):
        title = p.get("title", "")
        if title in done:
            continue

        row = {
            "title":       title,
            "authors":     p.get("authors", []),
            "doi":         "",
            "ee":          p.get("ee", ""),
            "year":        p.get("year", args.year),
            "venue":       args.conf.upper(),
            "type":        p.get("type", ""),
            "key":         p.get("key", ""),
            "abstract":    "",
            "arxiv_id":    "",
            "oa_pdf":      "",
            "citationCount": 0,
        }

        s2 = search_s2(title)
        if s2:
            row["abstract"] = s2.get("abstract") or ""
            pdf = (s2.get("openAccessPdf") or {}).get("url", "")
            row["oa_pdf"] = pdf or ""
            ext = s2.get("externalIds") or {}
            row["arxiv_id"] = ext.get("ArXiv", "")
            row["doi"] = ext.get("DOI", "")
            row["citationCount"] = s2.get("citationCount", 0) or 0

        results.append(row)
        done.add(title)
        time.sleep(DELAY)

        if len(results) % 10 == 0:
            with out.open("w") as fh:
                for r in results:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            has_abs = sum(1 for r in results if r.get("abstract"))
            print(f"  {len(results)}/{len(papers)} — {has_abs} with abstracts", flush=True)

    with out.open("w") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    has_abs = sum(1 for r in results if r.get("abstract"))
    has_pdf = sum(1 for r in results if r.get("oa_pdf"))
    print(f"wrote {len(results)} -> {out} | abstracts:{has_abs} pdfs:{has_pdf}")


if __name__ == "__main__":
    main()
