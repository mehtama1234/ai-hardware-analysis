#!/usr/bin/env python3
"""Build a parent macro from verified cells with no inherited exploratory rails."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-wired-20260913T503000Z"


def section(name: str, body: str) -> str:
    return f"<< {name} >>\n{body.rstrip()}\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for item in SOURCE.iterdir():
        if item.is_file():
            shutil.copy2(item, out / item.name)

    source_layout = (out / "aimc_converter_macro_active_candidate.mag").read_text(encoding="utf-8")
    # Retain only the latch and two parent-bound preamp placements. All
    # top-level exploratory cells, metal, and labels are discarded and
    # rebuilt below from explicit net ownership.
    cell_header = source_layout.split("use escaped_input_latch", 1)[1].split("<< metal1 >>", 1)[0]
    header = "magic\ntech sky130A\nuse escaped_input_latch" + cell_header
    via1 = "\n".join([
        "rect 22530 18220 22590 18280", "rect 25530 18220 25590 18280",
        "rect 22400 18670 22460 18730", "rect 22800 18670 22860 18730",
        "rect 25400 18670 25460 18730", "rect 25800 18970 25860 19030",
        "rect 8480 980 8540 1040", "rect 11480 980 11540 1040",
    ])
    via2 = via1 + "\n" + "\n".join([
        "rect 22400 18670 22460 18730", "rect 22800 18670 22860 18730",
        "rect 25400 18670 25460 18730", "rect 25800 18970 25860 19030",
        "rect 22530 18220 22590 18280", "rect 25530 18220 25590 18280",
        "rect 8480 980 8540 1040", "rect 11480 980 11540 1040",
        "rect 22400 19470 22460 19530", "rect 25400 19470 25460 19530",
        "rect 1800 20000 1860 20060", "rect 21000 20500 21060 20560",
    ])
    via3 = via2 + "\n" + "\n".join([
        "rect 22800 18670 22860 18730", "rect 25800 18970 25860 19030",
        "rect 8480 980 8540 1040", "rect 11480 980 11540 1040",
        "rect 22530 18220 22590 18280", "rect 25530 18220 25590 18280",
        "rect 22400 19470 22460 19530", "rect 25400 19470 25460 19530",
        "rect 1800 20000 1860 20060", "rect 21000 20500 21060 20560",
    ])
    via4 = "\n".join([
        "rect 25800 18970 25860 19030", "rect 11480 980 11540 1040",
    ])
    metal2 = "\n".join([
        "rect 1800 0 1860 20030", "rect 21000 0 21060 20530",
    ])
    metal3 = "\n".join([
        # Separate input-control routes.
        "rect 1800 20000 22560 20060", "rect 22530 18250 22590 20030",
        "rect 21000 20500 25560 20560", "rect 25530 18250 25590 20530",
        # Shared preamp-tail route on a third layer.
        "rect 22400 18670 22460 19470", "rect 25400 18670 25460 19470",
        "rect 22400 19440 25400 19500",
    ])
    metal4 = "\n".join([
        # P output: latch P port to P drain, isolated from N M5 output.
        "rect 8480 980 8540 18670", "rect 8480 18640 22800 18700",
    ])
    metal5 = "\n".join([
        # N output: latch N port to N drain, isolated from P M4 output.
        "rect 11480 980 11540 18970", "rect 11480 18940 25800 19000",
        "rect 23900 23970 24100 24030",
    ])
    labels = "\n".join([
        "rlabel metal2 1800 0 1860 20000 0 row_drive",
        "rlabel metal2 21000 0 21060 20500 0 sar_comparator_input",
        "rlabel metal4 8480 980 8540 1040 0 latch_sense_p_ext",
        "rlabel metal5 11480 980 11540 1040 0 latch_sense_n_ext",
        "rlabel metal3 23900 23970 24100 24030 0 preamp_iso_tail_ext",
        "rlabel metal1 23000 19800 23200 19900 0 vss_escape",
        "rlabel metal1 26000 19800 26200 19900 0 vss_escape",
    ])
    layout = header + section("metal2", metal2)
    for name, body in (("via1", via1), ("via2", via2), ("via3", via3), ("via4", via4),
                       ("metal3", metal3), ("metal4", metal4), ("metal5", metal5),
                       ("labels", labels)):
        layout += section(name, body)
    layout += "<< end >>\n"
    (out / "aimc_converter_macro_active_candidate.mag").write_text(layout, encoding="utf-8")
    (out / "extract-active-converter-macro.tcl").write_text(
        "drc on\n" f"path search +{out}\n"
        "load aimc_converter_macro_active_candidate -force\nselect top cell\n"
        "flatten aimc_converter_macro_active_candidate_flat\n"
        "load aimc_converter_macro_active_candidate_flat -force\nselect top cell\n"
        "drc check\ndrc count\nextract all\next2spice lvs\n"
        "ext2spice cthresh 0\next2spice rthresh 0\n"
        "ext2spice -o aimc_converter_macro_active_candidate_extracted.spice\n"
        "quit -noprompt\n", encoding="utf-8")
    (out / "candidate-build.json").write_text(json.dumps({
        "result_type": "clean_parent_route_experiment",
        "source": str(SOURCE.relative_to(ROOT)),
        "routing": "P output M4; N output M5; shared preamp tail M3; controls M2/M3",
        "accepted_converter": False,
        "claim_boundary": "Clean parent routing experiment; requires DRC, extraction, strict binding, LVS, and electrical qualification.",
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
