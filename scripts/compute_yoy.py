#!/usr/bin/env python3
"""Compute year-over-year theme distribution: 2024 vs 2025 per-paper JSONs.

Applies same keyword-scoring as bucket_themes.py but separately for each year
and venue. Writes analysis/yoy-comparison.json with all counts, deltas, movers.

Usage: python3 scripts/compute_yoy.py
"""
import json, glob, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# Same theme definitions as bucket_themes.py (order = tie-break priority)
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

THEME_KEYS = [k for k, _, _ in THEMES] + ["T0_other"]
THEME_LABELS = {k: lab for k, lab, _ in THEMES}
THEME_LABELS["T0_other"] = "Systems & infrastructure (scheduling, data, ML-for-systems)"

SHORT_LABELS = {
    "T0_other": "T0: Other/Systems",
    "T1_attention": "T1: Attention/LLM",
    "T2_quantization": "T2: Quantization",
    "T3_memory": "T3: Memory/PIM",
    "T4_interconnect": "T4: Interconnect",
    "T5_sparsity": "T5: Sparsity/MoE",
    "T6_compiler": "T6: Compiler",
    "T7_security": "T7: Security",
    "T8_reliability": "T8: Reliability",
    "T9_specialized": "T9: Specialized",
}


def text_of(d):
    parts = []
    for k in ("technique_category", "tags", "workloads"):
        v = d.get(k)
        parts.append(v if isinstance(v, str) else " ".join(map(str, v or [])))
    parts.append(str(d.get("primary_theme", "")))
    parts.append(str(d.get("title", "")))
    return " ".join(parts).lower()


def classify(d):
    t = text_of(d)
    best, bestscore = None, 0
    for key, _, kws in THEMES:
        score = sum(t.count(kw) for kw in kws)
        if score > bestscore:
            best, bestscore = key, score
    return best if best else "T0_other"


def venue_from_id(paper_id):
    """Extract venue name from paper id like 'asplos-2024-001'."""
    parts = paper_id.split("-")
    return parts[0].upper() if parts else "UNKNOWN"


def load_year(glob_pattern):
    """Load papers, return: (venue_theme_counts, theme_totals, paper_count)."""
    venue_theme = defaultdict(lambda: defaultdict(int))
    theme_totals = defaultdict(int)
    total = 0
    for fpath in sorted(glob.glob(glob_pattern)):
        try:
            d = json.load(open(fpath))
        except Exception:
            continue
        paper_id = d.get("id", "") or Path(fpath).stem
        venue = venue_from_id(paper_id)
        theme = classify(d)
        venue_theme[venue][theme] += 1
        theme_totals[theme] += 1
        total += 1
    return venue_theme, theme_totals, total


def main():
    print("Loading 2024 papers...")
    vt24, tt24, n24 = load_year(str(ROOT / "analysis/per-paper-2024/*.json"))
    print(f"  {n24} papers across {len(vt24)} venues")

    print("Loading 2025 papers...")
    vt25, tt25, n25 = load_year(str(ROOT / "analysis/per-paper/*.json"))
    print(f"  {n25} papers across {len(vt25)} venues")

    # Matched venues: present in both years
    venues_24 = set(vt24.keys())
    venues_25 = set(vt25.keys())
    matched_venues = sorted(venues_24 & venues_25)
    print(f"  Matched venues: {matched_venues}")

    # Per-theme overall delta (matched venues only for apples-to-apples)
    matched_tt24 = defaultdict(int)
    matched_tt25 = defaultdict(int)
    for venue in matched_venues:
        for theme in THEME_KEYS:
            matched_tt24[theme] += vt24[venue].get(theme, 0)
            matched_tt25[theme] += vt25[venue].get(theme, 0)

    # Build per-theme comparison rows
    theme_rows = []
    for theme in THEME_KEYS:
        c24 = matched_tt24[theme]
        c25 = matched_tt25[theme]
        delta = c25 - c24
        if c24 > 0:
            pct_change = round((delta / c24) * 100, 1)
        elif c25 > 0:
            pct_change = None  # new entrant
        else:
            pct_change = 0.0
        theme_rows.append({
            "theme": theme,
            "label": THEME_LABELS[theme],
            "short": SHORT_LABELS[theme],
            "count_2024": c24,
            "count_2025": c25,
            "delta": delta,
            "pct_change": pct_change,
        })

    # Top movers (matched venues, % change among themes with >=3 papers in 2024)
    eligible = [r for r in theme_rows if r["count_2024"] >= 3 and r["pct_change"] is not None]
    top_grower = max(eligible, key=lambda r: r["pct_change"])
    top_shrinker = min(eligible, key=lambda r: r["pct_change"])

    # New entrant: largest 2025 count with essentially zero 2024 presence (<2 papers)
    new_entrant_candidates = [r for r in theme_rows if r["count_2024"] < 2 and r["count_2025"] >= 2]
    new_entrant = max(new_entrant_candidates, key=lambda r: r["count_2025"]) if new_entrant_candidates else None

    # Venue breakdown
    venue_rows = []
    for venue in sorted(venues_24 | venues_25):
        row = {"venue": venue, "themes_2024": {}, "themes_2025": {}}
        for theme in THEME_KEYS:
            c24 = vt24[venue].get(theme, 0) if venue in vt24 else 0
            c25 = vt25[venue].get(theme, 0) if venue in vt25 else 0
            if c24 or c25:
                row["themes_2024"][theme] = c24
                row["themes_2025"][theme] = c25
        row["total_2024"] = sum(row["themes_2024"].values())
        row["total_2025"] = sum(row["themes_2025"].values())
        row["matched"] = venue in matched_venues
        venue_rows.append(row)

    out = {
        "meta": {
            "generated": "2026-07-28",
            "papers_2024": n24,
            "papers_2025": n25,
            "venues_2024": sorted(venues_24),
            "venues_2025": sorted(venues_25),
            "matched_venues": matched_venues,
            "matched_papers_2024": int(sum(matched_tt24.values())),
            "matched_papers_2025": int(sum(matched_tt25.values())),
        },
        "theme_comparison": theme_rows,
        "top_movers": {
            "biggest_grower": top_grower,
            "biggest_shrinker": top_shrinker,
            "new_entrant": new_entrant,
        },
        "venue_breakdown": venue_rows,
        "all_theme_totals_2024": dict(tt24),
        "all_theme_totals_2025": dict(tt25),
    }

    outpath = ROOT / "analysis/yoy-comparison.json"
    outpath.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\nWrote {outpath}")

    print("\n--- Theme comparison (matched venues) ---")
    print(f"{'Theme':<20} {'2024':>6} {'2025':>6} {'delta':>7} {'pct':>7}")
    for r in theme_rows:
        pct = f"{r['pct_change']:+.1f}%" if r["pct_change"] is not None else "NEW"
        print(f"{r['theme']:<20} {r['count_2024']:>6} {r['count_2025']:>6} {r['delta']:>+7} {pct:>7}")

    print(f"\nTop grower:   {top_grower['theme']} ({top_grower['pct_change']:+.1f}%)")
    print(f"Top shrinker: {top_shrinker['theme']} ({top_shrinker['pct_change']:+.1f}%)")
    if new_entrant:
        print(f"New entrant:  {new_entrant['theme']} (2025 count={new_entrant['count_2025']})")


if __name__ == "__main__":
    main()
