#!/usr/bin/env python3
"""arXiv title-search fallback for papers OpenAlex left without an abstract/PDF.

Many architecture papers are on arXiv but not linked by OpenAlex (esp. IEEE venues like
MICRO/HPCA whose abstracts are withheld). This searches arXiv by title, verifies the match by
title similarity, and attaches arxiv_id + abstract — which build_corpus then upgrades to a
downloadable full-text PDF. arXiv's API has no 403/429 wall (unlike IEEE Xplore / OpenReview).

Targets records in the enriched file that currently have NO arxiv_id (optionally only those
also missing an abstract). Updates the enriched jsonl in place. Resumable.

Usage: python3 scripts/enrich_arxiv.py --conf micro --year 2025 [--only-titleonly]
Then re-run build_corpus.py.
"""
import argparse, json, re, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "ai-hw-corpus/1.0 (mailto:mehtama1@gmail.com)"
ATOM = "{http://www.w3.org/2005/Atom}"


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _sim(a, b):
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def arxiv_search(title):
    # search by title terms; arXiv wants a light query
    q = 'ti:"%s"' % re.sub(r'["\\]', " ", title)[:230]
    url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "start": 0, "max_results": 3})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                xml = r.read().decode("utf-8", "ignore")
            break
        except Exception:
            time.sleep(4 * (attempt + 1))
    else:
        return None
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml)
    except Exception:
        return None
    best, bestsim = None, 0.0
    for e in root.findall(f"{ATOM}entry"):
        t = (e.findtext(f"{ATOM}title") or "").strip()
        s = _sim(title, t)
        if s > bestsim:
            aid = (e.findtext(f"{ATOM}id") or "")
            m = re.search(r"arxiv\.org/abs/([\d.]+)", aid)
            summ = (e.findtext(f"{ATOM}summary") or "").strip()
            best = {"arxiv_id": m.group(1) if m else None,
                    "abstract": re.sub(r"\s+", " ", summ)}
            bestsim = s
    return best if (best and bestsim >= 0.75 and best["arxiv_id"]) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--only-titleonly", action="store_true",
                    help="only papers missing BOTH arxiv_id and abstract")
    a = ap.parse_args()
    path = ROOT / "metadata" / f"{a.conf}-{a.year}-enriched.jsonl"
    recs = [json.loads(l) for l in path.open()]
    hits = 0
    tried = 0
    for r in recs:
        if r.get("arxiv_id"):
            continue
        if a.only_titleonly and r.get("abstract"):
            continue
        if not r.get("title"):
            continue
        tried += 1
        res = arxiv_search(r["title"])
        if res:
            r["arxiv_id"] = res["arxiv_id"]
            if not r.get("abstract") and res["abstract"]:
                r["abstract"] = res["abstract"]
            r["evidence"] = "abstract"
            hits += 1
        if tried % 10 == 0:
            print(f"  tried={tried} hits={hits}")
        time.sleep(1.5)  # arXiv politeness
    with path.open("w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"done. arXiv matches added: {hits}/{tried} attempted -> {path}")


if __name__ == "__main__":
    main()
