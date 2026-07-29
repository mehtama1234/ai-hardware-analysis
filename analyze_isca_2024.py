#!/usr/bin/env python3
"""Analyze ISCA 2024 papers with claude-haiku-4-5-20251001.

Usage: python3 analyze_isca_2024.py
"""
import json
import subprocess
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS_PATH = ROOT / "analysis/raw/isca-2024-corpus.json"
ODIR = ROOT / "analysis/per-paper-2024"

HW_TARGET = 'GPU, ASIC, FPGA, CIM (compute-in-memory), CPU, chiplet, photonic, analog, NPU, TPU, PIM (processing-in-memory), SoC, RISC-V, DPU, SmartNIC'
TECH = 'dataflow, quantization, sparsity, memory-system, interconnect, compiler, circuit-design, packaging, power, scheduling, near-data-processing, approximation, pruning, kernel-fusion, parallelism, virtualization, security, cache, prefetching, reliability, coherence'
WORK = 'LLM-inference, LLM-training, CNN, transformer, recommendation, GNN, diffusion, attention, MoE, graph-analytics, HPC, DLRM, RL, vision, speech, database, genomics, cryptography'


def analyze_paper_haiku(p):
    """Analyze paper with claude-haiku-4-5-20251001 via CLI"""
    abstract = p.get('abstract') or '[no abstract]'
    
    prompt = f"""Analyze this research paper and output ONLY a single JSON object (no markdown, no code blocks, just raw JSON).

Paper:
  id: {p['id']}
  venue: {p['venue']}
  year: {p.get('year', 2024)}
  title: {p['title']}
  abstract: {abstract}

Required JSON fields (use exactly these names):
  "id": "{p['id']}",
  "title": "{p['title']}",
  "venue": "{p['venue']}",
  "year": {p.get('year', 2024)},
  "problem": "1-2 sentences on the specific technical problem",
  "motivation": "1 sentence why it matters",
  "method": "2-4 sentences HOW it works",
  "key_novelty": "1 sentence most novel idea",
  "contributions": ["item1", "item2", "item3"],
  "hardware_target": ["option1", "option2"],
  "technique_category": ["option1", "option2"],
  "workloads": ["option1", "option2"],
  "metrics": {{"speedup": "value", "accuracy": "value"}},
  "baselines": ["baseline1"],
  "limitations": "1 sentence or 'not discussed'",
  "tags": ["tag1", "tag2", "tag3"],
  "primary_theme": "short phrase",
  "confidence": "high"

Output ONLY the raw JSON object starting with {{ and ending with }}, nothing else."""

    try:
        result = subprocess.run(
            ['claude', '--model', 'claude-haiku-4-5-20251001', 
             '--print', '-p', prompt],
            capture_output=True, text=True, cwd=str(ROOT),
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"    ERROR: {result.stderr[:100]}", flush=True)
            return None
        
        output = result.stdout.strip()
        
        # Find JSON object
        start = output.find('{')
        end = output.rfind('}')
        if start == -1 or end == -1:
            print(f"    ERROR: No JSON found in output", flush=True)
            return None
        
        json_str = output[start:end+1]
        data = json.loads(json_str)
        
        # Ensure required fields
        data['year'] = p.get('year', 2024)
        data['venue'] = p.get('venue', 'ISCA')
        
        return data
        
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT", flush=True)
        return None
    except json.JSONDecodeError as e:
        print(f"    JSON ERROR: {str(e)[:80]}", flush=True)
        return None
    except Exception as e:
        print(f"    EXCEPTION: {str(e)[:80]}", flush=True)
        return None


def main():
    ODIR.mkdir(parents=True, exist_ok=True)
    
    # Load corpus
    corpus_text = CORPUS_PATH.read_text()
    try:
        corpus = json.loads(corpus_text)
    except json.JSONDecodeError:
        corpus = [json.loads(l) for l in corpus_text.split('\n') if l]
    
    print(f"Loading {len(corpus)} papers from {CORPUS_PATH}")
    
    # Find papers to analyze
    todo = []
    for p in corpus:
        pid = p.get('id') or p.get('title', '').replace(' ', '_')[:30]
        p['id'] = pid
        output_file = ODIR / f"isca-2024-{str(len(todo)).zfill(3)}.json"
        if not output_file.exists():
            todo.append((p, output_file))
    
    print(f"Analyzing {len(todo)} papers...")
    
    total_written = 0
    for i, (paper, output_file) in enumerate(todo):
        print(f"  [{i+1}/{len(todo)}] {paper['title'][:60]}...", flush=True)
        
        analysis = analyze_paper_haiku(paper)
        
        if analysis:
            # Write JSON
            output_file.write_text(json.dumps(analysis, indent=2))
            total_written += 1
            print(f"      -> {output_file.name}", flush=True)
        else:
            print(f"      SKIPPED", flush=True)
        
        # Gentle rate limiting
        time.sleep(0.5)
    
    print(f"\nTotal analyzed: {total_written}/{len(corpus)}")
    existing = list(ODIR.glob("isca-2024-*.json"))
    print(f"Total ISCA 2024 files: {len(existing)}")


if __name__ == "__main__":
    main()
