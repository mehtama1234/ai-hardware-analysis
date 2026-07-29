#!/usr/bin/env python3
"""Per-paper Haiku analysis for MLSys 2024 — reads batch files, one paper at a time.

Usage: python3 scripts/analyze_haiku_2024.py
"""
import argparse, json, subprocess, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BDIR = ROOT / "analysis/per-paper/batches"
ODIR = ROOT / "analysis/per-paper-2024"

HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V, DPU, SmartNIC'
TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security, cache, prefetching, reliability, coherence'
WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database, genomics, cryptography'

ODIR.mkdir(parents=True, exist_ok=True)

def analyze_paper(p):
    abstract = p.get('abstract') or '[no abstract — analyze from title only]'
    prompt = f"""Analyze this research paper and output a single JSON object (no markdown, no code blocks, just raw JSON starting with {{ and ending with }}).

Paper:
  id: {p['id']}
  venue: {p['venue']}
  title: {p['title']}
  abstract: {abstract}

Required JSON fields (exactly these names):
  id: "{p['id']}"
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
        print(f"      ERROR: returncode={result.returncode}")
        return None

    output = result.stdout.strip()
    # Strip markdown code fences if present
    if '```' in output:
        lines = output.split('\n')
        output = '\n'.join(l for l in lines if not l.startswith('```'))
    output = output.strip()

    # Find the JSON object
    start = output.find('{')
    end = output.rfind('}')
    if start == -1 or end == -1:
        print(f"      ERROR: no JSON found in output")
        return None

    try:
        return json.loads(output[start:end+1])
    except json.JSONDecodeError as e:
        print(f"      ERROR: JSON parse failed: {e}")
        return None


def main():
    batches = sorted(BDIR.glob(f"mlsys_2024_batch_*.jsonl"))
    print(f"mlsys 2024: {len(batches)} batch files")

    total_written = 0
    for batch_file in batches:
        all_papers = [json.loads(l) for l in batch_file.open()]
        todo = [p for p in all_papers if not (ODIR / f"{p['id']}.json").exists()]

        if not todo:
            print(f"  {batch_file.name}: all {len(all_papers)} done, skipping")
            continue

        print(f"  {batch_file.name}: {len(todo)} papers to analyze...", flush=True)

        for p in todo:
            d = analyze_paper(p)
            if d:
                pid = d.get('id', p['id'])
                (ODIR / f"{pid}.json").write_text(json.dumps(d, indent=2))
                (ODIR / f"{pid}.md").write_text(
                    f"# {d.get('title','')}\n\n**Problem:** {d.get('problem','')}\n\n"
                    f"**Method:** {d.get('method','')}\n\n**Novelty:** {d.get('key_novelty','')}\n"
                )
                total_written += 1
                print(f"    {pid}: ok", flush=True)
            else:
                print(f"    {p['id']}: FAILED", flush=True)
            time.sleep(0.5)

    print(f"\nTotal written: {total_written}")
    existing = list(ODIR.glob("mlsys-2024-*.json"))
    print(f"Total mlsys-2024 files: {len(existing)}")


if __name__ == "__main__":
    main()
