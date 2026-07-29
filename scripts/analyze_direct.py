#!/usr/bin/env python3
"""Direct per-paper Haiku analysis — reads batch files, calls claude-haiku-4-5-20251001 per batch.

Usage: python3 scripts/analyze_direct.py --conf osdi --year 2025
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BDIR = ROOT / "analysis/per-paper/batches"
ODIR = ROOT / "analysis/per-paper"

HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V, DPU, SmartNIC'
TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security, cache, prefetching, reliability, coherence'
WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database, genomics, cryptography'

SYSTEM = """You are a systems/AI-hardware analyst extracting structured records from research papers.
For each paper given, output a JSON object on a single line with EXACTLY these fields:
  id, title, venue (copied from input)
  problem: the specific problem addressed — 1-2 concrete technical sentences
  motivation: why it matters — 1 sentence
  method: HOW it works in technical detail — 2-4 sentences, name the actual mechanism
  key_novelty: the single most novel idea — 1 sentence
  contributions: array of 2-4 concrete contributions
  hardware_target: array from {""" + HW_TARGET + """}
  technique_category: array from {""" + TECH + """}
  workloads: array from {""" + WORK + """}
  metrics: object with any of {speedup, energy_or_tops_w, area, ppa, accuracy, other} as short strings
  baselines: array of systems/hardware compared against
  limitations: 1 sentence (state "not discussed" if absent)
  tags: 3-6 lowercase tags
  primary_theme: one short phrase naming the core theme
  confidence: "low" if abstract-only

Output ONE JSON object per paper, each on its own line. No markdown, no explanation."""


def analyze_batch(conf, year, batch_num):
    batch_file = BDIR / f"{conf}_{year}_batch_{batch_num:03d}.jsonl"
    if not batch_file.exists():
        return 0

    papers = [json.loads(l) for l in batch_file.open()]

    # Check which papers are already done
    todo = []
    for p in papers:
        out = ODIR / f"{p['id']}.json"
        if not out.exists():
            todo.append(p)

    if not todo:
        print(f"  batch {batch_num:03d}: all {len(papers)} already done")
        return 0

    # Build prompt
    papers_text = "\n".join(
        f"PAPER {i+1}: id={p['id']} venue={p['venue']}\ntitle: {p['title']}\nabstract: {p.get('abstract','[no abstract — analyze from title only]')}"
        for i, p in enumerate(todo)
    )
    prompt = f"Analyze these {len(todo)} papers:\n\n{papers_text}"

    # Call claude haiku
    result = subprocess.run(
        ["claude", "--model", "claude-haiku-4-5-20251001", "--dangerously-skip-permissions",
         "--print", "-p", prompt],
        capture_output=True, text=True, cwd=str(ROOT),
        env={"HOME": str(Path.home()), "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/manishmehta/.local/bin"}
    )

    if result.returncode != 0:
        print(f"  batch {batch_num:03d}: ERROR {result.returncode}: {result.stderr[:200]}")
        return 0

    # Strip markdown code fences if present
    output = result.stdout.strip()
    if output.startswith("```"):
        lines = output.split("\n")
        output = "\n".join(l for l in lines if not l.startswith("```"))

    written = 0
    for line in output.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
            pid = d.get("id")
            if not pid:
                continue
            out_json = ODIR / f"{pid}.json"
            out_md = ODIR / f"{pid}.md"
            out_json.write_text(json.dumps(d, indent=2))
            out_md.write_text(f"# {d.get('title','')}\n\n**Problem:** {d.get('problem','')}\n\n**Method:** {d.get('method','')}\n\n**Novelty:** {d.get('key_novelty','')}\n")
            written += 1
        except json.JSONDecodeError:
            pass

    print(f"  batch {batch_num:03d}: {written}/{len(todo)} written")
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    args = ap.parse_args()

    batches = sorted(BDIR.glob(f"{args.conf}_{args.year}_batch_*.jsonl"))
    print(f"{args.conf} {args.year}: {len(batches)} batches")

    total = 0
    for b in batches:
        num = int(b.stem.split("_")[-1])
        total += analyze_batch(args.conf, args.year, num)

    print(f"Total written: {total}")
    existing = list(ODIR.glob(f"{args.conf}-{args.year}-*.json"))
    print(f"Total {args.conf}-{args.year} files: {len(existing)}")


if __name__ == "__main__":
    main()
