#!/usr/bin/env python3
"""Enrich a DBLP JSONL with abstracts using Semantic Scholar's batch endpoint.

Sends up to 500 DOIs in a single POST — much better than per-paper rate limits.
Usage: python3 scripts/enrich_s2_batch.py --conf isscc --year 2025
"""
import argparse, json, time, re, urllib.request, urllib.error
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
S2_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch"
FIELDS  = "title,abstract,openAccessPdf,externalIds"
BATCH_N = 490   # stay safely under 500


def doi_from_ee(ee):
    m = re.search(r'doi\.org/(.+)', str(ee or ""))
    return m.group(1).strip() if m else None


def s2_batch(ids, fields=FIELDS):
    """POST to S2 batch endpoint. Returns list matching input order (None on miss)."""
    body = json.dumps({"ids": ids, "fields": fields}).encode()
    req  = urllib.request.Request(
        f"{S2_BATCH}?fields={fields}", data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("  429 batch — wait 30s"); time.sleep(30)
            return s2_batch(ids, fields)   # retry once
        print(f"  HTTP {e.code} on batch"); return [None] * len(ids)
    except Exception as ex:
        print(f"  batch error: {ex}"); return [None] * len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()

    src = ROOT / f"metadata/{args.conf}-{args.year}-dblp.jsonl"
    out = ROOT / f"metadata/{args.conf}-{args.year}-enriched.jsonl"

    papers = [json.loads(l) for l in src.open()]
    print(f"{len(papers)} papers from DBLP")

    # build DOI list
    dois = [doi_from_ee(p.get("ee", "")) for p in papers]
    ids  = [f"DOI:{d}" if d else f"TITLE:{p.get('title','')[:60]}"
            for d, p in zip(dois, papers)]

    # batch fetch — only papers that have a DOI
    doi_ids   = [(i, iid) for i, iid in enumerate(ids) if iid.startswith("DOI:")]
    abstracts = {}   # index -> s2 record

    for start in range(0, len(doi_ids), BATCH_N):
        chunk = doi_ids[start:start+BATCH_N]
        print(f"  batch {start//BATCH_N + 1}: {len(chunk)} DOIs")
        results = s2_batch([iid for _, iid in chunk])
        for (orig_i, _), s2r in zip(chunk, results):
            if s2r:
                abstracts[orig_i] = s2r
        time.sleep(1)   # polite pause between batches

    # merge
    rows = []
    for i, p in enumerate(papers):
        s2r = abstracts.get(i, {}) or {}
        pdf = (s2r.get("openAccessPdf") or {}).get("url", "")
        ext = s2r.get("externalIds") or {}
        rows.append({
            "title":    p.get("title", ""),
            "authors":  p.get("authors", []),
            "doi":      dois[i] or "",
            "ee":       p.get("ee", ""),
            "year":     p.get("year", args.year),
            "venue":    args.conf.upper(),
            "type":     p.get("type", ""),
            "key":      p.get("key", ""),
            "abstract": s2r.get("abstract") or "",
            "arxiv_id": ext.get("ArXiv", ""),
            "oa_pdf":   pdf or "",
        })

    with out.open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    has_abs = sum(1 for r in rows if r.get("abstract"))
    has_pdf = sum(1 for r in rows if r.get("oa_pdf"))
    print(f"wrote {len(rows)} -> {out}")
    print(f"  abstracts: {has_abs}/{len(rows)}")
    print(f"  open PDFs: {has_pdf}/{len(rows)}")


if __name__ == "__main__":
    main()
