#!/usr/bin/env python3
"""Add labels at extracted preamp terminal coordinates for a flat-binding test."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T480000Z"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for item in SOURCE.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)

    layout_path = out / "aimc_converter_macro_active_candidate.mag"
    layout = layout_path.read_text(encoding="utf-8")
    # Coordinates are taken from the fresh flattened extraction, not from the
    # nominal child boxes.  These labels touch the existing terminal metal1
    # or gate metal2 shapes and do not add any new conductor geometry.
    labels = (
        "rlabel ndiffusion 15880 2040 16120 2160 0 preamp_iso_tail_ext\n"
        "rlabel ndiffusion 16520 2040 16700 2160 0 latch_sense_p_ext\n"
        "rlabel polysilicon 16380 1060 16580 1180 0 row_drive\n"
        "rlabel ndiffusion 21880 2040 22120 2160 0 preamp_iso_tail_ext\n"
        "rlabel ndiffusion 22420 2040 22600 2160 0 latch_sense_n_ext\n"
        "rlabel polysilicon 22380 1060 22580 1180 0 sar_comparator_input\n"
    )
    if "<< labels >>" not in layout:
        raise SystemExit("layout has no labels section")
    layout = layout.replace("<< labels >>\n", "<< labels >>\n" + labels, 1)
    layout_path.write_text(layout, encoding="utf-8")
    extract_path = out / "extract-active-converter-macro.tcl"
    extract = extract_path.read_text(encoding="utf-8")
    extract_path.write_text(extract.replace(str(SOURCE), str(out)), encoding="utf-8")
    (out / "candidate-build.json").write_text(json.dumps({
        "result_type": "flat_endpoint_label_binding_experiment",
        "source": str(SOURCE.relative_to(ROOT)),
        "endpoint_basis": "fresh flattened extraction coordinates",
        "accepted_converter": False,
        "claim_boundary": "Label-only flat-binding experiment; requires DRC, extraction, strict binding, parent LVS, and electrical qualification.",
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
