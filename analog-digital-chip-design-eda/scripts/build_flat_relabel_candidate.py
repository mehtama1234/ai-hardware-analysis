#!/usr/bin/env python3
"""Relabel a Magic-flattened macro at the parent boundary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    text = args.source.read_text(encoding="utf-8")
    replacements = {
        "physical_preamp_0.preamp_iso_tail_ext": "preamp_iso_tail_ext",
        "physical_preamp_0.latch_sense_p_ext": "latch_sense_p_ext",
        "physical_preamp_0.latch_sense_n_ext": "latch_sense_n_ext",
        "physical_preamp_0.row_drive": "row_drive",
        "physical_preamp_0.sar_comparator_input": "sar_comparator_input",
        "physical_preamp_0.vss_escape": "vss_escape",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    layout = output / "aimc_converter_macro_active_candidate.mag"
    layout.write_text(text.replace("\n\n", "\n"), encoding="utf-8")
    (output / "extract.tcl").write_text(
        "load aimc_converter_macro_active_candidate -force\n"
        "select top cell\n"
        "drc check\n"
        "drc count\n"
        "extract all\n"
        "ext2spice lvs\n"
        "ext2spice cthresh 0\n"
        "ext2spice rthresh 0\n"
        "ext2spice -o aimc_converter_macro_active_candidate_extracted.spice\n"
        "quit -noprompt\n",
        encoding="utf-8",
    )
    (output / "candidate-build.json").write_text(json.dumps({
        "result_type": "flat_parent_relabel_candidate",
        "source": str(args.source.resolve()),
        "accepted_converter": False,
        "claim_boundary": "Flattened relabel experiment only; requires DRC, extraction, strict binding, LVS, and transient validation."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
