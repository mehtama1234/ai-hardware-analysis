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


def _as_author_list(authors):
    if not authors:
        return []
    if isinstance(authors, list):
        return [a.get("text", a) if isinstance(a, dict) else str(a) for a in authors]
    if isinstance(authors, dict):
        inner = authors.get("author", [])
        if isinstance(inner, list):
            return [a.get("text", "") for a in inner]
        if isinstance(inner, dict):
            return [inner.get("text", "")]
    return []


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
    for f in glob.glob(str(bdir / f"{a.conf}_{a.year}_batch_*")) + glob.glob(str(bdir / "batch_*")):
        os.remove(f)
    # analyze only papers with real content (full text OR abstract); title-only papers are
    # logged as a gap, not force-analyzed from a bare title.
    analyzable = []
    skipped_title_only = 0
    for r in recs:
        tpath = tdir / f"{r['id']}.txt"
        has = tpath.exists() and tpath.stat().st_size > 2000
        if not has and not r.get("abstract"):
            skipped_title_only += 1
            continue
        analyzable.append((r, tpath, has))

    n = with_text = 0
    for i in range(0, len(analyzable), a.per):
        chunk = analyzable[i:i + a.per]
        with (bdir / f"{a.conf}_{a.year}_batch_{i // a.per:03d}.jsonl").open("w") as f:
            for r, tpath, has in chunk:
                with_text += has
                f.write(json.dumps({
                    "id": r["id"], "title": r["title"], "venue": r["venue"],
                    "authors": _as_author_list(r.get("authors"))[:8],
                    "abstract": r.get("abstract"),
                    "text_path": str(tpath) if has else None,
                }) + "\n")
        n += 1
    if skipped_title_only:
        (ROOT / "logs" / f"{a.conf}-{a.year}-titleonly.log").write_text(
            "\n".join(r["id"] + "\t" + r["title"] for r in recs
                      if not (tdir / f"{r['id']}.txt").exists() and not r.get("abstract")))
    print(f"batches={n} analyzable={len(analyzable)} with_full_text={with_text} "
          f"skipped_title_only={skipped_title_only}")


if __name__ == "__main__":
    main()
