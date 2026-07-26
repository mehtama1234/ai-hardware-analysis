#!/usr/bin/env python3
"""Assign each analyzed paper to one of the 9 cross-venue themes (+ an 'other systems' bucket)
by keyword-scoring its technique_category / tags / primary_theme / workloads / title.

Writes analysis/themes/buckets/<theme>.jsonl (compact per-paper records) for the writeup workflow.
Usage: python3 scripts/bucket_themes.py
"""
import json, glob, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# theme key -> (label, keyword list). Order = tie-break priority (distinctive themes first).
THEMES = [
    ("T7_security", "Security, side-channels & confidentiality",
     ["security", "side-channel", "side channel", "rowhammer", "spectre", "meltdown", "tee",
      "confidential", "encryption", "secure", "attack", "isolation", "sev-snp", "cheri", "constant-time"]),
    ("T8_reliability", "Reliability, correctness & verification",
     ["reliability", "fault", "sdc", "silent-data", "silent data", "error-correction", "resilience",
      "coherence", "formal", "verification", "verify", "qec", "quantum-error", "correctness", "integrity"]),
    ("T2_quantization", "Quantization & low-precision datapaths",
     ["quantization", "quantiz", "low-precision", "low precision", "int4", "int8", "int3", "fp8",
      "w4a8", "bit-serial", "lut ", "block-fp", "mxfp", "precision", "dequant", "outlier"]),
    ("T5_sparsity", "Sparsity & mixture-of-experts",
     ["sparsity", "sparse", "moe", "mixture-of-experts", "mixture of experts", "pruning", "prune",
      "n:m", "2:4", "expert"]),
    ("T4_interconnect", "Interconnect, collectives & communication",
     ["interconnect", "noc", "network-on-chip", "network on chip", "collective", "all-reduce",
      "allreduce", "all-to-all", "communication", "chiplet", "nvlink", "infiniband", "fabric",
      "multicast", "topology", "in-network", "wafer"]),
    ("T3_memory", "Memory hierarchy, near-data & processing-in-memory",
     ["memory-system", "memory system", "near-data", "near data", "near-memory", "near memory",
      "pim", "cim", "compute-in-memory", "processing-in-memory", "in-memory", "dram", "hbm",
      "cxl", "offload", "prefetch", "ssd", "tiering", "kv-cache", "kv cache", "cache"]),
    ("T6_compiler", "Compilation, programming models & accelerator generation",
     ["compiler", "codegen", "code-generation", "code generation", "programming-model",
      "programming model", "dsl", "rtl", "hls", "accelerator-generation", "compilation",
      "autotuning", "auto-tuning", "e-graph", "simulator", "cost-model", "cost model"]),
    ("T9_specialized", "Non-NVIDIA & specialized silicon (edge, quantum, crypto, robotics)",
     ["fpga", "risc-v", "risc v", "analog", "photonic", "quantum", "cryptography", "crypto",
      "fhe", "zkp", "genomic", "robotic", "edge", "mcu", "ray-tracing", "ray tracing", "snn",
      "spiking", "homomorphic", "zero-knowledge"]),
    ("T1_attention", "LLM serving, attention & KV-cache acceleration",
     ["attention", "kv-cache", "kv cache", "serving", "decode", "prefill", "flashattention",
      "paged", "scheduler", "scheduling", "slo", "llm-inference", "llm inference", "long-context",
      "speculative", "batching", "prefix"]),
]


def text_of(d):
    parts = []
    for k in ("technique_category", "tags", "workloads"):
        v = d.get(k)
        parts.append(v if isinstance(v, str) else " ".join(map(str, v or [])))
    parts.append(str(d.get("primary_theme", "")))
    parts.append(str(d.get("title", "")))
    return " ".join(parts).lower()


def main():
    recs = [json.load(open(f)) for f in sorted(glob.glob(str(ROOT / "analysis/per-paper/*.json")))]
    buckets = {k: [] for k, _, _ in THEMES}
    buckets["T0_other"] = []
    labels = {k: lab for k, lab, _ in THEMES}
    labels["T0_other"] = "Systems & infrastructure (scheduling, data, ML-for-systems)"

    for d in recs:
        t = text_of(d)
        best, bestscore = None, 0
        for key, _, kws in THEMES:
            score = sum(t.count(kw) for kw in kws)
            if score > bestscore:
                best, bestscore = key, score
        key = best if best else "T0_other"
        buckets[key].append({
            "id": d.get("id"), "t": d.get("title"), "v": (d.get("id") or "").split("-")[0].upper(),
            "c": d.get("confidence"), "pb": d.get("problem"), "me": d.get("method"),
            "nv": d.get("key_novelty"),
            "hw": d.get("hardware_target"), "wl": d.get("workloads"),
            "mx": d.get("metrics"), "th": d.get("primary_theme"),
        })

    bdir = ROOT / "analysis/themes/buckets"
    bdir.mkdir(parents=True, exist_ok=True)
    order = [k for k, _, _ in THEMES] + ["T0_other"]
    idx = []
    for key in order:
        rows = buckets[key]
        with (bdir / f"{key}.jsonl").open("w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        idx.append((key, labels[key], len(rows)))
        print(f"  {key:16} {len(rows):3}  {labels[key]}")
    (bdir / "_index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=2))
    print("total:", sum(n for _, _, n in idx))


if __name__ == "__main__":
    main()
