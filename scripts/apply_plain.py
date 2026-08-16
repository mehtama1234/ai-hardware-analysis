#!/usr/bin/env python3
"""Fold the plain-language patch back into the canonical per-paper records.

For every id in analysis/deep_plain_patch.json:
  - overwrite `method` and `key_novelty` in the per-paper .json (per-paper/ or per-paper-2024/)
  - surgically replace the matching sections in the companion .md (both formats),
    leaving every other field/section untouched.

Non-destructive source of truth stays the patch JSON; re-runnable.

Usage: python3 scripts/apply_plain.py [--dry-run]
"""
import argparse, json, re, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "analysis/deep_plain_patch.json"


def json_path(pid):
    for sub in ("per-paper", "per-paper-2024"):
        p = ROOT / "analysis" / sub / f"{pid}.json"
        if p.exists():
            return p
    return None


def patch_md(md_path, method, novelty):
    """Return updated .md text or None if nothing changed / file missing."""
    if not md_path.exists():
        return None
    t = md_path.read_text(encoding="utf-8")
    orig = t
    # "## Method" heading format: body runs until the next markdown heading or EOF.
    t = re.sub(r"(## Method\s*\n+)(.*?)(?=\n#{1,6} |\Z)",
               lambda m: m.group(1) + method + "\n", t, count=1, flags=re.DOTALL)
    t = re.sub(r"(## Key Novelty\s*\n+)(.*?)(?=\n#{1,6} |\Z)",
               lambda m: m.group(1) + novelty + "\n", t, count=1, flags=re.DOTALL)
    # "**Method:**" inline format: body runs until the next "**Label:**" block or EOF.
    t = re.sub(r"(\*\*Method:\*\* )(.*?)(?=\n\n\*\*|\Z)",
               lambda m: m.group(1) + method, t, count=1, flags=re.DOTALL)
    t = re.sub(r"(\*\*Novelty:\*\* )(.*?)(?=\n\n\*\*|\Z)",
               lambda m: m.group(1) + novelty, t, count=1, flags=re.DOTALL)
    return t if t != orig else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    patch = json.loads(PATCH.read_text())
    j_ok = j_miss = md_ok = md_skip = 0
    for pid, v in patch.items():
        method, novelty = v.get("method", "").strip(), v.get("key_novelty", "").strip()
        if not method or not novelty:
            continue
        jp = json_path(pid)
        if not jp:
            j_miss += 1
            continue
        d = json.loads(jp.read_text())
        d["method"] = method
        d["key_novelty"] = novelty
        if not a.dry_run:
            jp.write_text(json.dumps(d, indent=2, ensure_ascii=False))
        j_ok += 1
        md_new = patch_md(jp.with_suffix(".md"), method, novelty)
        if md_new is not None:
            if not a.dry_run:
                jp.with_suffix(".md").write_text(md_new, encoding="utf-8")
            md_ok += 1
        else:
            md_skip += 1
    print(f"{'DRY-RUN ' if a.dry_run else ''}json updated: {j_ok}  json missing: {j_miss}  "
          f"md patched: {md_ok}  md unchanged/skipped: {md_skip}")


if __name__ == "__main__":
    main()
