#!/usr/bin/env python3
"""Add extraction-aligned drain endpoint contacts to a flat macro candidate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def add(text: str, section: str, shapes: str) -> str:
    marker = f"<< {section} >>"
    return text.replace(marker, marker + "\n" + shapes, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    text = args.source.read_text(encoding="utf-8")
    # Centers of the extracted child diffusion windows are x=32800 and
    # x=33600.  The prior route landed at their edges (32620/33500).
    text = add(text, "metal1", "rect 32770 620 32830 940\nrect 33570 620 33630 940")
    for section in ("via1", "via2", "via3", "via4"):
        text = add(text, section, "rect 32800 900 32860 960\nrect 33600 900 33660 960")
    text = add(text, "metal5", "rect 32620 1770 32800 1830\n"
              "rect 32800 900 32860 1800\n"
              "rect 33500 2170 33600 2230\n"
              "rect 33600 900 33660 2200")
    layout = out / "aimc_converter_macro_active_candidate.mag"
    layout.write_text(text.replace("\n\n", "\n"), encoding="utf-8")
    (out / "extract.tcl").write_text(
        "load aimc_converter_macro_active_candidate -force\n"
        "select top cell\n"
        "drc check\n"
        "drc count\n"
        "extract all\n"
        "ext2spice lvs\n"
        "ext2spice cthresh 0\n"
        "ext2spice rthresh 0\n"
        "ext2spice -o aimc_converter_macro_active_candidate_extracted.spice\n"
        "quit -noprompt\n", encoding="utf-8")
    (out / "candidate-build.json").write_text(json.dumps({
        "result_type": "flat_drain_endpoint_repair",
        "source": str(args.source.resolve()),
        "routing": "centered child diffusion contacts joined to existing metal5 latch returns",
        "accepted_converter": False,
        "claim_boundary": "Drain-binding experiment only; requires DRC, strict boundary, LVS, and transient validation."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
