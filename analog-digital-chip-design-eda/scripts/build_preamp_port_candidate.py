#!/usr/bin/env python3
"""Build and extract an independently named two-device preamp port cell."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/physical-integrated-clean/sky130_transistor_active_isolation_pair.mag"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    text = SOURCE.read_text(encoding="utf-8")
    # Extend the gate polysilicon into the contact landing, as in the
    # extracted latch cell.  A boundary-only touch leaves the gate escape
    # electrically unnamed after extraction.
    text = text.replace("rect 560 300 620 1200", "rect 560 200 620 1200", 1)
    text = text.replace("rect 1780 300 1840 1200", "rect 1780 200 1840 1200", 1)
    replacements = {
        " iso_tail\n": " preamp_iso_tail_ext\n",
        " iso_p\n": " latch_sense_p_ext\n",
        " iso_n\n": " latch_sense_n_ext\n",
        " sense_p\n": " row_drive\n",
        " sense_n\n": " sar_comparator_input\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Add an explicit p-substrate tie so the extracted cell exposes the same
    # body port required by the parent macro schematic.
    text = text.replace(
        "<< labels >>",
        "<< psubdiff >>\nrect 1000 1800 1200 1900\n"
        "<< psubdiffcont >>\nrect 1000 1800 1200 1900\n"
        "<< viali >>\nrect 1000 1800 1200 1900\n<< labels >>",
        1,
    )
    text = text.replace(
        "<< metal1 >>", "<< metal1 >>\nrect 1000 1800 1200 1900", 1
    )
    text = text.replace(
        "<< metal1 >>\nrect 1000 1800 1200 1900",
        "<< metal1 >>\nrect 1000 1800 1200 1900\n"
        "rect 540 250 640 300\nrect 1760 250 1860 300",
        1,
    )
    text = text.replace(
        "<< mcon >>",
        "<< mcon >>\nrect 560 250 620 300\nrect 1780 250 1840 300",
        1,
    )
    # Turn the existing metal2 gate escapes into real poly contacts.  This is
    # what lets a parent macro reach the child gates without relying on a
    # disconnected label placed on polysilicon.
    text = text.replace(
        "<< metal2 >>",
        "<< pc >>\nrect 560 250 620 300\nrect 1780 250 1840 300\n"
        "<< locali >>\nrect 560 250 620 300\nrect 1780 250 1840 300\n"
        "<< metal2 >>",
        1,
    )
    text = text.replace(
        "rlabel polysilicon 560 300 620 1200 0 row_drive",
        "rlabel metal2 500 250 680 300 0 row_drive",
        1,
    )
    text = text.replace(
        "rlabel polysilicon 1780 300 1840 1200 0 sar_comparator_input",
        "rlabel metal2 1720 250 1900 300 0 sar_comparator_input",
        1,
    )
    text = text.replace("port 5 nsew\n<< end >>", "port 5 nsew\n"
                        "rlabel metal1 1000 1800 1200 1900 0 vss_escape\n"
                        "port 6 nsew\n<< end >>", 1)
    (out / "preamp_port_candidate.mag").write_text(text, encoding="utf-8")
    (out / "reference.spice").write_text(
        "*. Intended extracted preamp topology.\n"
        ".subckt preamp_port_candidate preamp_iso_tail_ext latch_sense_p_ext "
        "latch_sense_n_ext row_drive sar_comparator_input vss_escape\n"
        "Xpreamp_p latch_sense_p_ext row_drive preamp_iso_tail_ext vss_escape "
        "sky130_fd_pr__nfet_01v8 w=1.2 l=0.6\n"
        "Xpreamp_n latch_sense_n_ext sar_comparator_input preamp_iso_tail_ext vss_escape "
        "sky130_fd_pr__nfet_01v8 w=1.2 l=0.6\n"
        ".ends preamp_port_candidate\n",
        encoding="utf-8",
    )
    (out / "extract.tcl").write_text(
        "load preamp_port_candidate -force\n"
        "select top cell\n"
        "drc check\n"
        "drc count\n"
        "extract all\n"
        "ext2spice lvs\n"
        "ext2spice cthresh 0\n"
        "ext2spice rthresh 0\n"
        "ext2spice -o extracted.spice\n"
        "quit -noprompt\n",
        encoding="utf-8",
    )
    report = {"status": "candidate_built", "source": str(SOURCE.relative_to(ROOT)),
              "claim_boundary": "Independent preamp cell only; not integrated converter evidence."}
    (out / "build.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
