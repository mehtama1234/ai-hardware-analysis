#!/usr/bin/env python3
"""Split the corpus into fixed-size batches for the analysis workflow.

Each batch line carries what an agent needs: id, title, abstract, venue, and the path to the
extracted full text (if it exists). The agent reads the text file directly for a deep read.

Usage: python3 scripts/make_batches.py --conf mlsys --year 2025 [--per 15]
Clears old batch_* files; prints batch count (feed to workflow args.n_batches).
"""
import argparse, glob, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--per", type=int, default=15)
    a = ap.parse_args()
    recs = [json.loads(l) for l in (ROOT / "metadata" / f"{a.conf}-{a.year}-corpus.jsonl").open()]
    tdir = ROOT / "conferences" / f"{a.conf}-{a.year}" / "text"
    bdir = ROOT / "analysis" / "per-paper" / "batches"
    bdir.mkdir(parents=True, exist_ok=True)
    for f in glob.glob(str(bdir / "batch_*")):
        os.remove(f)
    n = with_text = 0
    for i in range(0, len(recs), a.per):
        chunk = recs[i:i + a.per]
        with (bdir / f"batch_{i // a.per:03d}.jsonl").open("w") as f:
            for r in chunk:
                tpath = tdir / f"{r['id']}.txt"
                has = tpath.exists() and tpath.stat().st_size > 2000
                with_text += has
                f.write(json.dumps({
                    "id": r["id"], "title": r["title"], "venue": r["venue"],
                    "authors": (r.get("authors") or [])[:8],
                    "abstract": r.get("abstract"),
                    "text_path": str(tpath) if has else None,
                }) + "\n")
        n += 1
    print(f"batches={n} papers={len(recs)} with_full_text={with_text}")


if __name__ == "__main__":
    main()
