#!/usr/bin/env python3
"""Fetch a hardware/architecture/circuits conference's complete proceedings from DBLP.

Usage: python3 scripts/fetch_dblp.py --conf mlsys --year 2025
       python3 scripts/fetch_dblp.py --stream conf/isca --year 2025   # raw stream override
Writes metadata/<conf>-<year>-dblp.jsonl (one record per paper).
DBLP is the authoritative, complete list. Backs off on 429/500/503.
"""
import argparse, json, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# DBLP stream keys for the target venues.
STREAMS = {
    "isca": "conf/isca",
    "micro": "conf/micro",
    "hpca": "conf/hpca",
    "asplos": "conf/asplos",
    "mlsys": "conf/mlsys",
    "dac": "conf/dac",
    "isscc": "conf/isscc",
    "iccad": "conf/iccad",
    "date": "conf/date",
    "fpga": "conf/fpga",     # ACM/SIGDA FPGA
    "fccm": "conf/fccm",
    "sc": "conf/sc",         # Supercomputing
    "hotchips": "conf/hotchips",
    "vlsi": "conf/vlsic",    # VLSI Circuits symposium
}


def _authors(info):
    a = info.get("authors", {}).get("author", [])
    if isinstance(a, dict):
        a = [a]
    return [x.get("text", "") for x in a if isinstance(x, dict)]


def _get(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "ai-hw-corpus/1.0 (mailto:mehtama1@gmail.com)"})
    delay = 5
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 5:
                print(f"  DBLP {e.code}, backing off {delay}s (try {attempt+1})")
                time.sleep(delay); delay *= 2; continue
            raise


def fetch(stream, year, start_offset=0, existing=None):
    out = list(existing or [])
    f = start_offset
    while True:
        q = f"stream:{stream}: year:{year}"
        url = "https://dblp.dagstuhl.de/search/publ/api?" + urllib.parse.urlencode(
            {"q": q, "h": 100, "f": f, "format": "json"}, quote_via=urllib.parse.quote)
        d = _get(url)
        hits = d.get("result", {}).get("hits", {})
        batch = hits.get("hit", [])
        if isinstance(batch, dict):
            batch = [batch]
        for h in batch:
            info = h.get("info", {})
            out.append({
                "title": (info.get("title") or "").rstrip("."),
                "authors": _authors(info),
                "doi": info.get("doi"),
                "ee": info.get("ee"),
                "year": info.get("year"),
                "venue": info.get("venue"),
                "type": info.get("type"),
                "key": info.get("key"),
            })
        total = int(hits.get("@total", "0")); sent = int(hits.get("@sent", "0")); first = int(hits.get("@first", "0"))
        f = first + sent
        print(f"  fetched {len(out)}/{total}")
        if f >= total or not batch:
            break
        time.sleep(3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", help="short venue name (see STREAMS)")
    ap.add_argument("--stream", help="raw DBLP stream, e.g. conf/isca (overrides --conf lookup)")
    ap.add_argument("--year", required=True)
    a = ap.parse_args()
    conf = a.conf or (a.stream.split("/")[-1] if a.stream else None)
    stream = a.stream or STREAMS.get(a.conf)
    if not stream:
        raise SystemExit(f"unknown conf '{a.conf}'; known: {sorted(STREAMS)} or pass --stream conf/<key>")
    outp = ROOT / "metadata" / f"{conf}-{a.year}-dblp.jsonl"
    # resume: load existing partial results, start from where we left off
    existing, start_off = [], 0
    if outp.exists():
        existing = [json.loads(l) for l in outp.open()]
        start_off = len(existing)
        print(f"  resuming from offset {start_off} ({len(existing)} already saved)")
    recs = fetch(stream, a.year, start_offset=start_off, existing=existing)
    # keep only conference papers (drop editorials/proceedings shells)
    recs = [r for r in recs if r["type"] in ("Conference and Workshop Papers", None)]
    with outp.open("w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"wrote {len(recs)} records -> {outp}")


if __name__ == "__main__":
    main()
