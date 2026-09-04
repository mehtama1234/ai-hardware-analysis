#!/usr/bin/env python3
"""Add reproducibility metadata to a completed long-acquisition SAR artifact."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-calibrated-physical-sar.json"
OUT_MD = EVIDENCE / "sky130-calibrated-physical-sar.md"


def main() -> int:
    report = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    report.update({
        "acquisition_candidate": "long_source_acquisition",
        "source_switch_width_um": {"nfet": 32.0, "pfet": 64.0},
        "source_acquisition_end_ns": 4.0,
        "bottom_plate_transition_ns": 5.0,
        "comparator_sampling_ns": "9.1-9.6",
        "preamp_enable_ns": 9.7,
        "latch_ns": 11.7,
    })
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    text = OUT_MD.read_text(encoding="utf-8")
    marker = "- acquisition candidate:"
    if marker not in text:
        text = text.replace("- correct conversions: `5` of `5`\n", "- correct conversions: `5` of `5`\n- acquisition candidate: `32/64 um source switch with 4.0 ns acquisition and 5.0 ns redistribution`\n")
    OUT_MD.write_text(text, encoding="utf-8")
    print("annotated,long_acquisition")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
