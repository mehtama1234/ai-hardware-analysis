#!/usr/bin/env python3
"""Deterministic roll-up of per-paper analyses -> raw material for theme synthesis.

Normalizes the high-value axes (hardware_target, workloads) via keyword maps, and reports
raw frequencies for the fuzzier axes (technique_category, primary_theme, tags) so the LLM
synthesis step can do the semantic clustering. Writes analysis/syntheses/<conf>-<year>-aggregate.json
and a readable _digest.md.

Usage: python3 scripts/aggregate.py --conf mlsys --year 2025
"""
import argparse, glob, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HW_MAP = [
    ("cim", "CIM"), ("compute-in-memory", "CIM"), ("in-memory", "CIM"),
    ("pim", "PIM"), ("processing-in-memory", "PIM"), ("near-memory", "PIM"), ("near-data", "PIM"),
    ("fpga", "FPGA"), ("photonic", "photonic"), ("analog", "analog"),
    ("chiplet", "chiplet"), ("interposer", "chiplet"),
    ("gpu", "GPU"), ("tpu", "TPU"), ("npu", "NPU"),
    ("asic", "ASIC"), ("accelerator", "ASIC"), ("systolic", "ASIC"),
    ("risc", "CPU"), ("cpu", "CPU"), ("soc", "SoC"),
]
WORK_MAP = [
    ("llm-inference", "LLM-inference"), ("inference-serving", "LLM-inference"), ("serving", "LLM-inference"),
    ("llm-training", "LLM-training"), ("training", "LLM-training"),
    ("attention", "attention"), ("moe", "MoE"), ("mixture-of-experts", "MoE"),
    ("recommendation", "recommendation"), ("dlrm", "recommendation"),
    ("gnn", "GNN"), ("graph", "GNN"), ("diffusion", "diffusion"),
    ("cnn", "CNN"), ("transformer", "transformer"), ("vision", "vision"),
    ("rl", "RL"), ("speech", "speech"), ("database", "database"), ("hpc", "HPC"),
]


def aslist(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str) and x.strip():
        return re.split(r"[;,/]", x) if re.search(r"[;,/]", x) else [x]
    return []


def normalize(values, mapping):
    out = set()
    for v in aslist(values):
        s = str(v).lower()
        hit = None
        for kw, canon in mapping:
            if kw in s:
                hit = canon
                break
        out.add(hit or str(v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", required=True)
    ap.add_argument("--year", required=True)
    a = ap.parse_args()
    files = sorted(glob.glob(str(ROOT / "analysis" / "per-paper" / f"{a.conf}-{a.year}-*.json")))
    recs = [json.load(open(f)) for f in files]

    hw = Counter(); wk = Counter(); tech = Counter(); theme = Counter(); tags = Counter()
    conf_split = Counter()
    metrics_present = 0
    for r in recs:
        for h in normalize(r.get("hardware_target"), HW_MAP): hw[h] += 1
        for w in normalize(r.get("workloads"), WORK_MAP): wk[w] += 1
        for t in aslist(r.get("technique_category")): tech[str(t).lower()] += 1
        theme[str(r.get("primary_theme", "?")).lower()] += 1
        for tg in aslist(r.get("tags")): tags[str(tg).lower()] += 1
        conf_split[r.get("confidence", "?")] += 1
        m = r.get("metrics")
        if isinstance(m, dict) and any(v for v in m.values()):
            metrics_present += 1

    agg = {
        "conf": a.conf, "year": a.year, "n_papers": len(recs),
        "confidence_split": dict(conf_split),
        "papers_with_metrics": metrics_present,
        "hardware_target": hw.most_common(),
        "workloads": wk.most_common(),
        "technique_category": tech.most_common(),
        "primary_theme_raw": theme.most_common(),
        "top_tags": tags.most_common(40),
    }
    sdir = ROOT / "analysis" / "syntheses"
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / f"{a.conf}-{a.year}-aggregate.json").write_text(json.dumps(agg, indent=2))

    def fmt(pairs, n=20):
        return "\n".join(f"  {c:>3}  {k}" for k, c in pairs[:n])
    digest = f"""# {a.conf.upper()} {a.year} — aggregate ({len(recs)} papers)

confidence: {dict(conf_split)}   papers_with_metrics: {metrics_present}

## hardware_target (normalized)
{fmt(hw.most_common())}

## workloads (normalized)
{fmt(wk.most_common())}

## technique_category (raw — cluster at synthesis)
{fmt(tech.most_common(), 30)}

## top tags
{fmt(tags.most_common(40), 40)}

## primary_theme (raw — cluster at synthesis)
{fmt(theme.most_common(), 40)}
"""
    (sdir / f"{a.conf}-{a.year}-digest.md").write_text(digest)
    print(f"aggregated {len(recs)} papers -> analysis/syntheses/{a.conf}-{a.year}-aggregate.json")
    print(digest[:1200])


if __name__ == "__main__":
    main()
