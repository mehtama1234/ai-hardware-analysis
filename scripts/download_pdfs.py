#!/usr/bin/env python3
"""Download obtainable PDFs for a corpus. Resumable, polite, backs off on 429.

Reads  metadata/<conf>-<year>-corpus.jsonl
Writes conferences/<conf>-<year>/pdfs/<id>.pdf   (skips existing, validates %PDF header)
Logs   logs/<conf>-<year>-download.log           (every skip/failure, so gaps are visible)

Usage: python3 scripts/download_pdfs.py --conf mlsys --year 2025 [--limit N]
"""
import argparse, json, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (ai-hw-corpus; mailto:mehtama1@gmail.com)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    delay = 3
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(delay); delay = min(delay * 2, 40); continue
            return f"HTTP {e.code}"
        except Exception as e:
            if attempt < 4:
                time.sleep(delay); delay = min(delay * 2, 40); continue
            return f"{type(e).__name__}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    recs = [json.loads(l) for l in (ROOT / "metadata" / f"{a.conf}-{a.year}-corpus.jsonl").open()]
    if a.limit:
        recs = recs[: a.limit]
    pdir = ROOT / "conferences" / f"{a.conf}-{a.year}" / "pdfs"
    pdir.mkdir(parents=True, exist_ok=True)
    log = (ROOT / "logs" / f"{a.conf}-{a.year}-download.log").open("a")
    ok = skip = fail = nopdf = 0
    for i, r in enumerate(recs):
        dst = pdir / f"{r['id']}.pdf"
        if dst.exists() and dst.stat().st_size > 1000:
            skip += 1; continue
        if not r.get("pdf_url"):
            nopdf += 1; log.write(f"NOPDF {r['id']} {r['title'][:80]}\n"); continue
        data = fetch(r["pdf_url"])
        if isinstance(data, bytes) and data[:5] == b"%PDF-":
            dst.write_bytes(data); ok += 1
        else:
            fail += 1
            log.write(f"FAIL {r['id']} [{data if isinstance(data,str) else 'not-pdf'}] {r['pdf_url']}\n")
        if i % 10 == 0:
            print(f"  {i}/{len(recs)} ok={ok} skip={skip} fail={fail} nopdf={nopdf}")
        time.sleep(0.4)
    log.close()
    print(f"done. downloaded={ok} skipped={skip} failed={fail} no-pdf={nopdf}")


if __name__ == "__main__":
    main()
