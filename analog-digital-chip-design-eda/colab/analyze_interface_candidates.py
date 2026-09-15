#!/usr/bin/env python3
"""Rank saved continuous-SAR interface receipts without changing acceptance rules."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def summarize(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    conversions = data.get("conversions", [])
    preamp = [v for row in conversions for v in row.get("preamp_difference_v", [])]
    dac = [v for row in conversions for v in row.get("dac_threshold_before_comparator_v", [])]
    legal_dac = sum(0.0 <= v <= 1.8 for v in dac) / len(dac) if dac else 0.0
    bit_spread = 0.0
    if conversions:
        bit_spread = sum(
            max(row.get("preamp_difference_v", [0.0]))
            - min(row.get("preamp_difference_v", [0.0]))
            for row in conversions
        ) / len(conversions)
    return {
        "receipt": str(path),
        "status": data.get("status", "unknown"),
        "conversions": len(conversions),
        "all_conversions_correct": bool(data.get("all_conversions_correct", False)),
        "legal_dac_fraction": round(legal_dac, 6),
        "mean_preamp_bit_spread_v": round(bit_spread, 6),
        "score": round(bit_spread * legal_dac, 6),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="receipt directory")
    parser.add_argument("--glob", default="local-*.json", help="receipt filename pattern")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [summarize(path) for path in sorted(args.root.glob(args.glob))]
    rows.sort(key=lambda row: (row["score"], row["legal_dac_fraction"], row["conversions"]), reverse=True)
    report = {"result_type": "continuous_sar_interface_candidate_ranking", "candidates": rows}
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
