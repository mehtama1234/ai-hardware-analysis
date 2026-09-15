#!/usr/bin/env python3
"""Rank measured continuous-SAR calibration receipts by code-map quality."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def row(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    conversions = data.get("conversions", [])
    if not conversions:
        return {}
    expected = [item.get("expected_code") for item in conversions]
    actual = [item.get("final_code") for item in conversions]
    correct = sum(a == b for a, b in zip(expected, actual))
    name = path.name.lower()
    corner = next((value.upper() for value in ("ss", "sf", "ff", "fs") if re.search(rf"(?:^|[-_]){value}(?:[-_]|\d)", name)), "TT/unspecified")
    return {
        "artifact": str(path),
        "status": data.get("status"),
        "corner": data.get("corner", corner),
        "bit1_cap_scale": data.get("bit1_cap_scale"),
        "lsb_cap_scale": data.get("lsb_cap_scale"),
        "continuous_switch_width_um": data.get("continuous_switch_width_um"),
        "continuous_pmos_bank": data.get("continuous_pmos_bank"),
        "conversion_count": len(conversions),
        "correct_decisions": correct,
        "decoded_codes": actual,
        "full_map": correct == len(conversions) and bool(data.get("bottom_plate_in_legal_range")),
    }


def build(root: Path, output: Path) -> dict:
    rows = [item for path in sorted(root.glob("*.json")) if (item := row(path))]
    rows.sort(key=lambda item: (-int(item["full_map"]), -item["correct_decisions"], str(item["artifact"])))
    best_by_corner = {}
    for corner in sorted({item["corner"] for item in rows}):
        candidates = [item for item in rows if item["corner"] == corner]
        best_by_corner[corner] = next(iter(candidates), None)
    report = {
        "result_type": "continuous_sar_calibration_ranking",
        "rows": rows,
        "best_by_corner": best_by_corner,
        "recommendation": "Use the best full-map setting per declared corner; do not generalize a setting across PVT or mismatch without a fresh receipt.",
        "claim_boundary": "Ranking of checked-in schematic transient receipts; it is not a statistical yield estimate or analog authorization.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.evidence_root, args.output)
    print(json.dumps({"receipts": len(result["rows"]), "full_map_receipts": sum(item["full_map"] for item in result["rows"])}, sort_keys=True))
