#!/usr/bin/env python3
"""Per-paper Haiku analysis for 2024 corpus — reads from metadata/<conf>-2024-corpus.jsonl,
writes to analysis/per-paper-2024/<conf>-2024-NNN.json.

Usage: python3 scripts/analyze_2024.py --conf asplos
"""
import argparse, json, subprocess, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ODIR = ROOT / "analysis/per-paper-2024"

HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V, DPU, SmartNIC'
TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security, cache, prefetching, reliability, coherence'
WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database, genomics, cryptography'


def analyze_paper(p, pid):
    abstract = p.get('abstract') or '[no abstract — analyze from title only]'
    prompt = f"""Analyze this research paper and output a single JSON object (no markdown, no code blocks, just raw JSON starting with {{ and ending with }}).

Paper:
  id: {pid}
  venue: {p['venue']}
  title: {p['title']}
  abstract: {abstract}

Required JSON fields (exactly these names):
  id: "{pid}"
  title: "{p['title']}"
  venue: "{p['venue']}"
  year: 2024
  problem: 1-2 concrete sentences about the specific technical problem
  motivation: 1 sentence why it matters
  method: 2-4 sentences HOW it works, name actual mechanisms
  key_novelty: 1 sentence the single most novel idea
  contributions: ["contribution1", "contribution2", ...]  (2-4 items)
  hardware_target: array of strings from: {HW_TARGET}
  technique_category: array of strings from: {TECH}
  workloads: array of strings from: {WORK}
  metrics: {{"speedup": "...", "accuracy": "..."}}  (use keys: speedup/energy_or_tops_w/area/ppa/accuracy/other)
  baselines: ["system1", "system2"]
  limitations: "1 sentence, say not discussed if absent"
  tags: ["tag1", "tag2", "tag3"]  (3-6 lowercase tags)
  primary_theme: "short phrase"
  confidence: "low"

Output ONLY the raw JSON object, nothing else."""

    result = subprocess.run(
        ['claude', '--model', 'claude-haiku-4-5-20251001', '--dangerously-skip-permissions',
         '--print', '-p', prompt],
        capture_output=True, text=True, cwd=str(ROOT), env={**os.environ}
    )

    if result.returncode != 0:
        return None

    output = result.stdout.strip()
    if '```' in output:
        lines = output.split('\n')
        output = '\n'.join(l for l in lines if not l.startswith('```'))
    output = output.strip()

    start = output.find('{')
    end = output.rfind('}')
    if start == -1 or end == -1:
        return None

    try:
        return json.loads(output[start:end+1])
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    args = ap.parse_args()

    ODIR.mkdir(exist_ok=True)

    corpus_f = ROOT / f"metadata/{args.conf}-2024-corpus.jsonl"
    if not corpus_f.exists():
        print(f"No corpus: {corpus_f}")
        return

    corpus = [json.loads(l) for l in corpus_f.open()]
    print(f"{args.conf} 2024: {len(corpus)} papers in corpus")

    # Find existing analyzed files to skip
    existing_titles = set()
    existing_files = list(ODIR.glob(f"{args.conf}-2024-*.json"))
    for f in existing_files:
        d = json.load(f.open())
        existing_titles.add(d.get('title', '').lower()[:60])
    print(f"  {len(existing_files)} already analyzed, skipping those")

    # Find next index
    indices = []
    for f in existing_files:
        try:
            idx = int(f.stem.split('-')[-1])
            indices.append(idx)
        except ValueError:
            pass
    next_idx = max(indices) + 1 if indices else 0

    todo = [p for p in corpus if p.get('title', '').lower()[:60] not in existing_titles]
    print(f"  {len(todo)} new papers to analyze with claude-haiku-4-5-20251001")

    written = 0
    failed = 0
    for p in todo:
        pid = f"{args.conf}-2024-{next_idx:03d}"
        d = analyze_paper(p, pid)
        if d:
            d['year'] = 2024
            (ODIR / f"{pid}.json").write_text(json.dumps(d, indent=2))
            written += 1
            next_idx += 1
            if written % 20 == 0:
                print(f"  {written}/{len(todo)} done ({failed} failed)", flush=True)
        else:
            failed += 1
        time.sleep(0.2)

    print(f"\nDone: {written} written, {failed} failed")
    total = list(ODIR.glob(f"{args.conf}-2024-*.json"))
    print(f"Total {args.conf}-2024 files: {len(total)}")


if __name__ == "__main__":
    main()
