#!/usr/bin/env python3
"""Fetch conference papers from OpenAlex when DBLP is unavailable.

Usage: python3 scripts/fetch_openalex.py --conf iccad --year 2024 --source S4393919173
Writes metadata/<conf>-<year>-dblp.jsonl (same format as fetch_dblp.py output).
"""
import argparse, json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "ai-hw-corpus/1.0 (mailto:mehtama1@gmail.com)"

# Known OpenAlex source IDs for our venues
SOURCES = {
    "iccad:2024": "S4393919173",   # Proceedings of the International Conference on Computer-Aided Design
    "iccad:2025": "S4393919173",
    "sc:2024": "S4393919173",      # placeholder — needs verification
}


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    delay = 3
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 4:
                print(f"  OpenAlex {e.code}, backoff {delay}s (try {attempt+1})")
                time.sleep(delay); delay *= 2; continue
            raise


def fetch(source_id, year, conf):
    out = []
    cursor = "*"
    while True:
        params = {
            "filter": f"primary_location.source.id:{source_id},publication_year:{year}",
            "per-page": 100,
            "cursor": cursor,
            "select": "id,title,doi,authorships,publication_year,primary_location,abstract_inverted_index,open_access",
        }
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        d = _get(url)
        meta = d.get("meta", {})
        total = meta.get("count", 0)
        results = d.get("results", [])
        if not results:
            break
        for r in results:
            # reconstruct abstract from inverted index
            inv = r.get("abstract_inverted_index") or {}
            if inv:
                words = [""] * (max(max(v) for v in inv.values()) + 1)
                for word, positions in inv.items():
                    for pos in positions:
                        words[pos] = word
                abstract = " ".join(w for w in words if w)
            else:
                abstract = None

            authors_raw = r.get("authorships", [])
            authors = [a.get("author", {}).get("display_name", "") for a in authors_raw]

            loc = r.get("primary_location") or {}
            venue_name = (loc.get("source") or {}).get("display_name", conf.upper())

            doi = r.get("doi", "")
            if doi:
                doi = doi.replace("https://doi.org/", "")

            out.append({
                "title": (r.get("title") or "").strip(),
                "authors": authors,
                "doi": doi or None,
                "ee": r.get("doi"),
                "year": str(year),
                "venue": venue_name,
                "type": "Conference and Workshop Papers",
                "key": r.get("id", "").replace("https://openalex.org/", ""),
                "abstract": abstract,
            })
        print(f"  fetched {len(out)}/{total}")
        cursor = meta.get("next_cursor")
        if not cursor or len(out) >= total:
            break
        time.sleep(0.15)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True, type=int)
    ap.add_argument("--source", help="OpenAlex source ID (e.g. S4393919173)")
    a = ap.parse_args()

    source_id = a.source or SOURCES.get(f"{a.conf}:{a.year}")
    if not source_id:
        raise SystemExit(f"No source ID for {a.conf}:{a.year}. Pass --source <OA_SOURCE_ID>.")

    print(f"Fetching {a.conf} {a.year} from OpenAlex source {source_id}...")
    recs = fetch(source_id, a.year, a.conf)

    outp = ROOT / "metadata" / f"{a.conf}-{a.year}-dblp.jsonl"
    with outp.open("w") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(recs)} records -> {outp}")


if __name__ == "__main__":
    main()
