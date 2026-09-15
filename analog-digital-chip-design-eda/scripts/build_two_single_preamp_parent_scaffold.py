#!/usr/bin/env python3
"""Assemble two verified one-device preamps beside the latch, non-destructively."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/routing-repair-20260913T300000Z"
P_CELL = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/single-preamp-p-20260913T430000Z/preamp_p_nfet.mag"
N_CELL = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/single-preamp-n-20260913T430000Z/preamp_n_nfet.mag"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for item in SOURCE.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)
    shutil.copy2(P_CELL, out / "preamp_p_nfet.mag")
    shutil.copy2(N_CELL, out / "preamp_n_nfet.mag")
    layout = (out / "aimc_converter_macro_active_candidate.mag").read_text(encoding="utf-8")
    old = ("use sky130_transistor_active_isolation_pair physical_preamp_0\n"
           "timestamp 1788727000\ntransform 1 0 32000 0 1 0\n"
           "box 32000 0 34200 1200")
    new = ("use preamp_p_nfet physical_preamp_p\n"
           "timestamp 1789000000\ntransform 1 0 7680 0 1 360\n"
           "box 7680 360 8880 2260\n"
           "use preamp_n_nfet physical_preamp_n\n"
           "timestamp 1789000000\ntransform 1 0 10680 0 1 360\n"
           "box 10680 360 11880 2260")
    if old not in layout:
        raise SystemExit("parent child placement block not found")
    layout = layout.replace(old, new, 1).replace("\n\n", "\n")
    (out / "aimc_converter_macro_active_candidate.mag").write_text(layout, encoding="utf-8")
    (out / "candidate-build.json").write_text(json.dumps({
        "result_type": "two_single_preamp_parent_scaffold",
        "source": str(SOURCE.relative_to(ROOT)),
        "placements": {"p": [7680, 360], "n": [10680, 360]},
        "drain_alignment": "p/n drains overlap latch sense landings by placement; source/gate escapes remain to be validated",
        "accepted_converter": False,
        "claim_boundary": "Assembly scaffold only; requires DRC, extraction, strict binding, LVS, and transient validation."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
