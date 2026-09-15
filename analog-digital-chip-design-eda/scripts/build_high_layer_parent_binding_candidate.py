#!/usr/bin/env python3
"""Build a non-destructive metal5 parent-binding experiment."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/routing-repair-20260913T300000Z"


def add_section(text: str, section: str, shapes: str) -> str:
    marker = f"<< {section} >>"
    if marker not in text:
        text = text.replace("<< labels >>", marker + "\n" + shapes + "\n<< labels >>", 1)
    else:
        text = text.replace(marker, marker + "\n" + shapes, 1)
    return text


def build(source: Path, output: Path) -> None:
    if output.exists():
        raise SystemExit(f"output already exists: {output}")
    output.mkdir(parents=True)
    for item in source.iterdir():
        if item.is_file():
            shutil.copy2(item, output / item.name)
    layout_path = output / "aimc_converter_macro_active_candidate.mag"
    layout = layout_path.read_text(encoding="utf-8")
    # Remove prior experimental child trunks and parent-side duplicate labels.
    for shape in (
        "rect 3970 900 32800 960\n", "rect 15970 1040 33600 1100\n",
        "rlabel metal1 32700 620 32900 800 0 latch_sense_p_ext\n",
        "rlabel metal1 33500 620 33700 800 0 latch_sense_n_ext\n",
    ):
        layout = layout.replace(shape, "")
    # Child diffusion endpoints, based on the flattened extraction coordinate
    # audit: left x=32620, right x=33500, gates x=32560/33780.
    layout = add_section(layout, "metal1", "rect 32590 700 32650 960\nrect 33470 700 33530 960")
    layout = add_section(layout, "via1", "rect 32620 940 32680 1000\nrect 33500 940 33560 1000\n"
                         "rect 32530 250 32590 310\nrect 33750 250 33810 310")
    layout = add_section(layout, "via2", "rect 32620 940 32680 1000\nrect 33500 940 33560 1000\n"
                         "rect 32530 250 32590 310\nrect 33750 250 33810 310\n"
                         "rect 1800 20000 1860 20060\nrect 21000 21000 21060 21060")
    layout = add_section(layout, "via3", "rect 32620 940 32680 1000\nrect 33500 940 33560 1000\n"
                         "rect 32530 250 32590 310\nrect 33750 250 33810 310\n"
                         "rect 1800 20000 1860 20060\nrect 21000 21000 21060 21060")
    layout = add_section(layout, "via4", "rect 32620 940 32680 1000\nrect 33500 940 33560 1000\n"
                         "rect 3970 970 4030 1030\nrect 15970 970 16030 1030\n"
                         "rect 1800 20000 1860 20060\nrect 21000 21000 21060 21060\n"
                         "rect 32530 250 32590 310\nrect 33750 250 33810 310")
    # M4 drops connect the existing parent M4 pins to dedicated M5 tracks.
    layout = add_section(layout, "metal4", "rect 32600 970 32640 1800\n"
                         "rect 33480 970 33520 2200\nrect 3950 970 4010 1800\n"
                         "rect 15950 970 16010 2200\nrect 1790 20000 1870 20060\n"
                         "rect 20990 21000 21070 21060\nrect 32520 250 32600 310\n"
                         "rect 33740 250 33820 310")
    layout = add_section(layout, "metal5", "rect 3970 1770 32620 1830\n"
                         "rect 15970 2170 33500 2230\nrect 1800 19970 32560 20030\n"
                         "rect 32530 250 32590 20000\nrect 21000 20970 33780 21030\n"
                         "rect 33750 250 33810 21000")
    layout = layout.replace("\n\n", "\n")
    layout_path.write_text(layout, encoding="utf-8")
    (output / "candidate-build.json").write_text(json.dumps({
        "result_type": "high_layer_parent_binding_candidate",
        "source_candidate": str(source.relative_to(ROOT)),
        "routing": "metal5 separated latch-return and input tracks with explicit via stacks",
        "accepted_converter": False,
        "claim_boundary": "Routing experiment only; requires DRC, extraction, strict binding, LVS, and transient validation."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.source.resolve(), args.output.resolve())
