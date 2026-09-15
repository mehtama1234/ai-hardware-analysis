#!/usr/bin/env python3
"""Build a non-destructive active-macro routing candidate."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/physical-integrated-clean"
DEFAULT_PARENT = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate"
PREAMP_SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/preamp-port-candidate-20260913T290000Z/preamp_port_candidate.mag"

CHILD_MCON = """
rect 560 1340 620 1400
rect 1780 1540 1840 1600
"""
CHILD_POLY = """
rect 560 1200 620 1400
rect 1780 1200 1840 1600
"""
CHILD_METAL1 = """
rect 540 1340 2040 1400
rect 1760 1540 2200 1600
"""
METAL1 = """
<< metal1 >>
rect 32770 620 32830 960
rect 33570 620 33630 1100
rect 32770 700 32830 960
rect 33570 700 33630 1040
"""
VIA1 = """
<< via1 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
rect 33950 1340 34030 1400
rect 34150 1540 34230 1600
"""
METAL2 = """
<< metal2 >>
rect 33950 1340 34030 1400
rect 34150 1540 34230 1600
"""
VIA2 = """
<< via2 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
rect 33950 1340 34030 1400
rect 34150 1540 34230 1600
rect 1770 1340 1830 1400
"""
VIA3 = """
<< via3 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
rect 2170 1340 2230 1400
rect 2370 1340 2430 1400
"""
METAL3 = """
<< metal3 >>
rect 1800 1340 2200 1400
rect 2400 1340 34000 1400
rect 21000 1540 34200 1600
rect 33750 270 33810 500
"""
METAL4 = """
<< metal4 >>
rect 2200 1340 2400 1400
rect 21030 440 33780 500
rect 33750 270 33810 500
"""
CLEAN_METAL1 = """
<< metal1 >>
rect 32770 700 32830 960
rect 33570 700 33630 1040
"""
CLEAN_VIA1 = """
<< via1 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
"""
CLEAN_VIA2 = """
<< via2 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
"""
CLEAN_VIA3 = """
<< via3 >>
rect 32770 900 32830 960
rect 33570 1040 33630 1100
rect 32530 270 32590 330
rect 33750 270 33810 330
"""
CLEAN_METAL3 = """
<< metal3 >>
rect 33750 270 33810 500
"""
CLEAN_METAL4 = """
<< metal4 >>
rect 21030 440 33780 500
rect 33750 270 33810 500
"""
DRAIN_METAL1 = """
<< metal1 >>
rect 32590 700 32650 960
rect 33470 700 33530 1040
"""
DRAIN_VIA1 = """
<< via1 >>
rect 32590 900 32650 960
rect 33470 1040 33530 1100
"""
DRAIN_VIA2 = """
<< via2 >>
rect 32590 900 32650 960
rect 33470 1040 33530 1100
"""
DRAIN_VIA3 = """
<< via3 >>
rect 32590 900 32650 960
rect 33470 1040 33530 1100
"""


def build(source: Path, output: Path) -> dict[str, object]:
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.mkdir(parents=True)
    for item in source.iterdir():
        if item.is_file() and item.name != "aimc_converter_macro_active_candidate.mag":
            shutil.copy2(item, output / item.name)
    child = output / "sky130_transistor_active_isolation_pair.mag"
    # Use the separately verified port/body candidate as the parent child.
    shutil.copy2(PREAMP_SOURCE, child)
    child_text = child.read_text(encoding="utf-8")
    # Keep the child gate labels private; parent-level labels below own the
    # binding to the macro's row and comparator nets.
    child_text = child_text.replace("0 row_drive", "0 child_row_drive", 1)
    child_text = child_text.replace("0 sar_comparator_input", "0 child_sar_input", 1)
    # Child labels are namespaced during flattening even when they overlap a
    # parent landing.  Remove them and let the parent own every integration
    # net name; the underlying geometry and contacts remain unchanged.
    child_text = re.sub(r"rlabel [^\n]+\nport \d+ nsew\n", "", child_text)
    child.write_text(child_text, encoding="utf-8")
    original = source / "aimc_converter_macro_active_candidate.mag"
    text = original.read_text(encoding="utf-8")
    if text.count("<< end >>") != 1:
        raise SystemExit("unexpected Magic source structure")
    text = text.replace(
        "<< end >>",
        "rlabel metal2 32500 250 32680 300 0 row_drive\nport 16 nsew\n"
        "rlabel metal2 33720 250 33900 300 0 sar_comparator_input\nport 17 nsew\n"
        "rlabel metal1 32300 620 32500 800 0 preamp_iso_tail_ext\nport 18 nsew\n"
        "rlabel metal1 33000 1800 33200 1900 0 vss_escape\nport 19 nsew\n"
        "<< end >>",
        1,
    )
    # Add shapes to existing sections; Magic expects each section once and in
    # technology order.  The top-level source has no mcon section.
    layout = text
    if False:
        for section, addition in (("<< metal1 >>", METAL1), ("<< metal2 >>", METAL2),
                                  ("<< via1 >>", VIA1), ("<< via2 >>", VIA2),
                                  ("<< via3 >>", VIA3), ("<< metal3 >>", METAL3),
                                  ("<< metal4 >>", METAL4)):
            layout = layout.replace(section, section + "\n" + addition.split(section, 1)[1].strip(), 1)
    for section, addition in (
        ("<< metal1 >>", DRAIN_METAL1), ("<< via1 >>", DRAIN_VIA1),
        ("<< via2 >>", DRAIN_VIA2), ("<< via3 >>", DRAIN_VIA3),
    ):
        layout = layout.replace(section, section + "\n" + addition.split(section, 1)[1].strip(), 1)
    # The right-hand preamp drain must remain separate from the shared source.
    # The prior routing repair accidentally bridged the two on metal1.
    layout = layout.replace("rect 32770 620 32830 960\n", "")
    layout = layout.replace("rect 33570 620 33630 1100\n", "")
    # The child drain labels already land on the parent latch nets.  Remove
    # the experimental via/metal escape stacks as well; they were the source
    # of the accidental supply and drain/source merges.
    for shape in (
        "rect 32770 900 32830 960\n", "rect 33570 1040 33630 1100\n",
        "rect 32770 1770 32830 1830\n", "rect 33570 2170 33630 2230\n",
        "rect 32770 900 32830 1830\n", "rect 33570 1040 33630 2230\n",
    ):
        layout = layout.replace(shape, "")
    # Replace the stale nominal child trunks with extraction-aligned routes.
    # The flattened device nodes place the left/right child drains at roughly
    # x=32620/33500 and the gates at x=32560/33780 in parent coordinates.
    for shape in (
        "rect 3970 900 32800 960\n", "rect 15970 1040 33600 1100\n",
        "rlabel metal1 32700 620 32900 800 0 latch_sense_p_ext\n",
        "rlabel metal1 33500 620 33700 800 0 latch_sense_n_ext\n",
    ):
        layout = layout.replace(shape, "")
    parent_routes = {
        "<< metal1 >>": "rect 32590 700 32650 1040\nrect 33470 700 33530 970",
        "<< via1 >>": "rect 32620 1040 32680 1100\nrect 33500 970 33560 1030",
        "<< via2 >>": "rect 32620 1040 32680 1100\nrect 33500 970 33560 1030\n"
                       "rect 1800 400 1860 460\nrect 32530 250 32590 310\n"
                       "rect 21000 500 21060 560\nrect 33750 250 33810 310",
        "<< via3 >>": "rect 33500 970 33560 1030\n",
        "<< metal3 >>": "rect 3970 1040 32620 1100\n"
                        "rect 1800 400 32560 460\nrect 32530 250 32590 460\n"
                        "rect 21000 500 33780 560\nrect 33750 250 33810 560",
        "<< metal4 >>": "rect 15970 970 33500 1030\nrect 3940 970 4000 1040",
    }
    for section, shapes in parent_routes.items():
        layout = layout.replace(section, section + "\n" + shapes, 1)
    # Leave the parent-level label-only binding candidate isolated from the
    # experimental long bridges; those bridges are evaluated separately.
    if False:
        for section, addition in (
            ("<< metal1 >>", CLEAN_METAL1), ("<< via1 >>", CLEAN_VIA1),
            ("<< via2 >>", CLEAN_VIA2), ("<< via3 >>", CLEAN_VIA3),
            ("<< metal3 >>", CLEAN_METAL3), ("<< metal4 >>", CLEAN_METAL4),
        ):
            layout = layout.replace(section, section + "\n" + addition.split(section, 1)[1].strip(), 1)
    layout_path = output / original.name
    layout_path.write_text(layout.replace("\n\n", "\n"), encoding="utf-8")
    (output / "extract-active-converter-macro.tcl").write_text(
        "drc on\n"
        f"path search +{output}\n"
        "load aimc_converter_macro_active_candidate -force\n"
        "select top cell\n"
        "flatten aimc_converter_macro_active_candidate_flat\n"
        "load aimc_converter_macro_active_candidate_flat -force\n"
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
    report = {
        "result_type": "active_macro_signal_path_candidate",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_candidate": str(source.relative_to(ROOT)),
        "output_candidate": str(output.relative_to(ROOT)),
        "layout": str(layout_path.relative_to(ROOT)),
        "routing_change": "integrate independently DRC/LVS-verified two-device preamp port candidate",
        "source_preserved": True,
        "accepted_converter": False,
        "requires_validation": ["Magic DRC/extraction", "extracted boundary audit", "ngspice decision transient"],
        "claim_boundary": "Routing candidate only; no connectivity, electrical, LVS, or converter claim until downstream validators pass.",
    }
    (output / "candidate-build.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("routing-repair-%Y%m%dT%H%M%SZ")
    report = build(args.source.resolve(), (args.output or DEFAULT_PARENT / stamp).resolve())
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
