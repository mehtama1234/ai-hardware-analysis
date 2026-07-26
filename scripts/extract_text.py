#!/usr/bin/env python3
"""Extract text from downloaded PDFs with PyMuPDF (fitz) — 10-50x faster than pypdf.

Reads  conferences/<conf>-<year>/pdfs/<id>.pdf
Writes conferences/<conf>-<year>/text/<id>.txt   (skips existing)
Flags  papers whose extracted text is suspiciously short (scanned/figure-only) in the log.

Usage: python3 scripts/extract_text.py --conf mlsys --year 2025
"""
import argparse, json
from pathlib import Path
import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
MIN_CHARS = 2000  # below this => likely scan/extraction failure


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    a = ap.parse_args()
    base = ROOT / "conferences" / f"{a.conf}-{a.year}"
    pdir, tdir = base / "pdfs", base / "text"
    tdir.mkdir(parents=True, exist_ok=True)
    log = (ROOT / "logs" / f"{a.conf}-{a.year}-extract.log").open("a")
    ok = skip = short = err = 0
    stats = []
    for pdf in sorted(pdir.glob("*.pdf")):
        pid = pdf.stem
        dst = tdir / f"{pid}.txt"
        if dst.exists() and dst.stat().st_size > 100:
            skip += 1; continue
        try:
            doc = fitz.open(pdf)
            text = "\n".join(page.get_text() for page in doc)
            npages = doc.page_count
            doc.close()
        except Exception as e:
            err += 1; log.write(f"ERR {pid} {type(e).__name__}: {e}\n"); continue
        dst.write_text(text)
        stats.append((pid, npages, len(text)))
        if len(text) < MIN_CHARS:
            short += 1; log.write(f"SHORT {pid} chars={len(text)} pages={npages}\n")
        ok += 1
    log.close()
    if stats:
        avg = sum(s[2] for s in stats) // len(stats)
        print(f"extracted={ok} skipped={skip} short={short} err={err}  avg_chars={avg}")
    else:
        print(f"extracted={ok} skipped={skip} short={short} err={err}")


if __name__ == "__main__":
    main()
