#!/usr/bin/env python3
"""Plain-language rewrite of per-paper deep records via Haiku.

Rewrites the `method` (2-4 sentences) and `key_novelty` (1 sentence) fields of every
per-paper record into everyday, first-principles language while keeping every number,
named mechanism, and hardware detail. No invented facts. Output goes to a patch JSON
keyed by paper id so the pass is non-destructive and resumable; apply_plain.py folds it
back into the canonical records.

Reads:  analysis/per-paper/*.json  +  analysis/per-paper-2024/*.json
Writes: analysis/deep_plain_patch.json   { id: {"method": ..., "key_novelty": ...} }

Usage: python3 scripts/plainify_deep.py [--workers 10] [--limit N]
Resumable: ids already in the patch file are skipped.
"""
import argparse, json, subprocess, os, glob, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATCH = ROOT / "analysis/deep_plain_patch.json"
MODEL = "claude-haiku-4-5-20251001"

PROMPT = """You are rewriting two fields of a computer-architecture research paper summary so a smart non-specialist can understand them, WITHOUT losing any technical precision.

Rewrite rules:
- Plain, everyday language. Explain any unavoidable jargon in the same sentence (e.g. "equality saturation (trying every equivalent form of the code and keeping the best)").
- First-principles: say what the thing actually does and why it works, in cause-and-effect terms.
- KEEP every concrete fact from the source: all numbers, speedups, hardware names (GPU/FPGA/ASIC/etc.), and named mechanisms. Do NOT invent facts not present in the source.
- No hype words ("novel", "state-of-the-art", "revolutionary"). Just say what it is.
- method: 2-4 sentences on HOW it works.
- key_novelty: exactly 1 sentence naming the single core idea.

Source paper:
  title: {title}
  problem: {problem}
  method (rewrite this): {method}
  key_novelty (rewrite this): {key_novelty}

Output ONLY a raw JSON object (no markdown, no code fences), starting with {{ and ending with }}, with exactly these keys:
{{"method": "...", "key_novelty": "..."}}"""

_lock = threading.Lock()


def call_haiku(rec):
    prompt = PROMPT.format(
        title=rec.get("title", ""),
        problem=(rec.get("problem") or "")[:1200],
        method=(rec.get("method") or "")[:1500],
        key_novelty=(rec.get("key_novelty") or "")[:800],
    )
    try:
        r = subprocess.run(
            ["claude", "--model", MODEL, "--dangerously-skip-permissions", "--print", "-p", prompt],
            capture_output=True, text=True, cwd=str(ROOT), env={**os.environ}, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    out = r.stdout.strip()
    if "```" in out:
        out = "\n".join(l for l in out.split("\n") if not l.startswith("```"))
    a, b = out.find("{"), out.rfind("}")
    if a == -1 or b == -1:
        return None
    try:
        d = json.loads(out[a:b + 1])
    except json.JSONDecodeError:
        return None
    m, k = (d.get("method") or "").strip(), (d.get("key_novelty") or "").strip()
    if not m or not k:
        return None
    return {"method": m, "key_novelty": k}


def load_patch():
    if PATCH.exists():
        return json.loads(PATCH.read_text())
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    files = sorted(glob.glob(str(ROOT / "analysis/per-paper/*.json"))) + \
        sorted(glob.glob(str(ROOT / "analysis/per-paper-2024/*.json")))
    recs = []
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if (d.get("method") or "").strip() and (d.get("key_novelty") or "").strip():
            recs.append(d)

    patch = load_patch()
    todo = [r for r in recs if r["id"] not in patch]
    if a.limit:
        todo = todo[:a.limit]
    print(f"records: {len(recs)}  already done: {len(patch)}  to do: {len(todo)}", flush=True)

    done = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(call_haiku, r): r for r in todo}
        for fut in as_completed(futs):
            r = futs[fut]
            res = fut.result()
            if res:
                with _lock:
                    patch[r["id"]] = res
                    done += 1
                    if done % 25 == 0:
                        PATCH.write_text(json.dumps(patch, indent=1, ensure_ascii=False))
                        print(f"  {done}/{len(todo)} done ({fail} fail)", flush=True)
            else:
                fail += 1
    PATCH.write_text(json.dumps(patch, indent=1, ensure_ascii=False))
    print(f"DONE. patch entries: {len(patch)}  new: {done}  fail: {fail}", flush=True)


if __name__ == "__main__":
    main()
