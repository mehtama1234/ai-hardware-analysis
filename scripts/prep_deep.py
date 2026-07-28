#!/usr/bin/env python3
"""Prepare per-paper deep-writeup batches from the theme buckets.

Full-text papers (c==high) -> small batches (deep 'method in detail', agent reads the PDF text).
Abstract-only papers       -> larger batches (plain 'what it does' from the abstract).

Writes analysis/themes/deep/batches/{ft,ab}_NNN.jsonl and prints counts.
Usage: python3 scripts/prep_deep.py
"""
import json, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TDIR = ROOT / "conferences"


def text_path(pid):
    ven = pid.split("-")[0]
    p = TDIR / f"{ven}-2025" / "text" / f"{pid}.txt"
    return str(p) if p.exists() and p.stat().st_size > 2000 else None


def main():
    # gather all papers with their theme + full analysis
    per = {json.load(open(f))["id"]: json.load(open(f))
           for f in glob.glob(str(ROOT / "analysis/per-paper/*.json"))}
    theme_of = {}
    for bf in glob.glob(str(ROOT / "analysis/themes/buckets/T*.jsonl")):
        key = Path(bf).stem
        for l in open(bf):
            theme_of[json.loads(l)["id"]] = key

    ft, ab = [], []
    for pid, d in per.items():
        v = (d.get("venue") or "").strip()
        venue = v.split()[0] if v else pid.split("-")[0].upper()
        row = {"id": pid, "title": d.get("title"), "venue": venue,
               "theme": theme_of.get(pid, "T0_other"), "c": d.get("confidence"),
               "abstract": None, "problem": d.get("problem"), "method": d.get("method"),
               "tp": text_path(pid)}
        if d.get("confidence") == "high" and row["tp"]:
            ft.append(row)
        else:
            ab.append(row)

    bdir = ROOT / "analysis/themes/deep/batches"
    bdir.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(bdir / "*.jsonl")):
        Path(old).unlink()

    def write(rows, per_n, prefix):
        n = 0
        for i in range(0, len(rows), per_n):
            with (bdir / f"{prefix}_{i//per_n:03d}.jsonl").open("w") as fh:
                for r in rows[i:i+per_n]:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
        return n

    n_ft = write(ft, 5, "ft")
    n_ab = write(ab, 16, "ab")
    print(f"full-text papers={len(ft)} -> {n_ft} batches (ft_*)")
    print(f"abstract papers ={len(ab)} -> {n_ab} batches (ab_*)")
    print(f"FT_BATCHES={n_ft} AB_BATCHES={n_ab}")


if __name__ == "__main__":
    main()
