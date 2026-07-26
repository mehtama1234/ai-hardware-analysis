#!/usr/bin/env python3
"""MLSys-specific full-text booster: the open proceedings site gives free PDFs + abstracts
for EVERY paper, closing the gaps OpenAlex leaves (and avoiding the OpenReview 403 wall).

Index:    https://proceedings.mlsys.org/paper_files/paper/<year>
Abstract: .../hash/<hash>-Abstract-Conference.html   (title + abstract)
PDF:      .../file/<hash>-Paper-Conference.pdf

Matches each proceedings entry to a DBLP record by title similarity and writes
metadata/mlsys-<year>-fulltext.jsonl with {key, title, hash, pdf_url, abstract, source}.
Resumable: re-run safe (rewrites the mapping).

Usage: python3 scripts/scrape_mlsys.py --year 2025
"""
import argparse, json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (ai-hw-corpus; mailto:mehtama1@gmail.com)"
BASE = "https://proceedings.mlsys.org/paper_files/paper"


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _sim(a, b):
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception:
            time.sleep(3 * (attempt + 1))
    return ""


def _abstract(hash_, year):
    html = _get(f"{BASE}/{year}/hash/{hash_}-Abstract-Conference.html")
    i = html.find(">Abstract<")
    if i < 0:
        return None
    frag = html[i + 10:i + 4000]
    # cut at the next section heading if present
    frag = re.split(r"</?h[1-5]", frag)[0]
    text = re.sub(r"<[^>]+>", " ", frag)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", required=True)
    a = ap.parse_args()
    year = a.year
    index = _get(f"{BASE}/{year}")
    pairs = re.findall(
        r'href="[^"]*/hash/([0-9a-f]+)-Abstract-Conference\.html"[^>]*>(.*?)</a>',
        index, re.S)
    pairs = [(h, re.sub(r"<[^>]+>", "", t).strip()) for h, t in pairs]
    print(f"proceedings entries: {len(pairs)}")

    dblp = [json.loads(l) for l in (ROOT / "metadata" / f"mlsys-{year}-dblp.jsonl").open()]

    out = ROOT / "metadata" / f"mlsys-{year}-fulltext.jsonl"
    matched = 0
    with out.open("w") as fh:
        for i, (hash_, title) in enumerate(pairs):
            # best DBLP key by title similarity
            best, bestsim = None, 0.0
            for d in dblp:
                s = _sim(title, d["title"])
                if s > bestsim:
                    best, bestsim = d, s
            key = best["key"] if best and bestsim >= 0.6 else None
            matched += bool(key)
            rec = {
                "key": key,
                "title": title,
                "hash": hash_,
                "pdf_url": f"{BASE}/{year}/file/{hash_}-Paper-Conference.pdf",
                "abstract": _abstract(hash_, year),
                "source": "mlsys-proceedings",
                "match_sim": round(bestsim, 3),
            }
            fh.write(json.dumps(rec) + "\n")
            if i % 10 == 0:
                print(f"  {i}/{len(pairs)} matched={matched}")
            time.sleep(0.4)
    print(f"done. matched {matched}/{len(pairs)} to DBLP -> {out}")


if __name__ == "__main__":
    main()
