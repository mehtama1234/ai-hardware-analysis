#!/usr/bin/env python3
"""Wire the two verified one-device preamps into the latch scaffold."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/two-single-preamp-parent-20260913T440000Z/aimc_converter_macro_active_candidate.mag"
PRIMITIVE_P = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/single-preamp-p-20260913T456000Z/preamp_p_nfet.mag"
PRIMITIVE_N = ROOT / "evidence/aimc-simulator-adapters/active-converter-macro-candidate/single-preamp-n-20260913T456000Z/preamp_n_nfet.mag"
BALANCED_LATCH = ROOT / "evidence/aimc-simulator-adapters/balanced-latch-layout/20260913T150749183044Z/sky130_isolated_frontend_active_load_latch_v2.mag"


def add_section(text: str, section: str, shapes: str) -> str:
    marker = f"<< {section} >>"
    if marker in text:
        return text.replace(marker, marker + "\n" + shapes, 1)
    return text.replace("<< labels >>", marker + "\n" + shapes + "\n<< labels >>", 1)


def add_parallel_finger(text: str) -> str:
    """Add a second matched NFET finger while retaining the original ports."""
    text = add_section(text, "ndiffusion", "rect 1100 690 1700 810")
    text = add_section(text, "polysilicon", "rect 1360 200 1420 1200")
    text = add_section(text, "ndc", "rect 1140 700 1260 760\nrect 1540 700 1660 760")
    text = add_section(text, "mcon", "rect 1140 700 1260 760\nrect 1540 700 1660 760")
    text = add_section(
        text, "metal1",
        "rect 1100 620 1300 800\nrect 1500 620 1700 800\n"
        "rect 400 500 460 740\nrect 1200 500 1260 740\n"
        "rect 400 500 1260 560\n"
        "rect 740 740 860 1440\nrect 1540 740 1660 1440\n"
        "rect 740 1400 1660 1460",
    )
    text = add_section(text, "metal2", "rect 500 250 1480 300")
    text = add_section(text, "via1", "rect 1300 250 1420 300")
    text = add_section(text, "pc", "rect 1360 250 1420 300")
    text = add_section(text, "locali", "rect 1360 250 1420 300")
    return text


def add_vertical_parallel_finger(text: str) -> str:
    """Add a second matched finger within the original cell footprint."""
    text = text.replace("rect 560 200 620 1200", "rect 560 200 620 1800")
    text = add_section(text, "ndiffusion", "rect 300 1290 900 1410")
    text = add_section(text, "ndc", "rect 340 1300 460 1360\nrect 740 1300 860 1360")
    text = add_section(text, "mcon", "rect 340 1300 460 1360\nrect 740 1300 860 1360")
    text = add_section(text, "metal1",
                       "rect 300 1220 500 1400\nrect 700 1220 900 1400\n"
                       "rect 400 740 460 1320\nrect 740 740 800 1320")
    return text


def add_flat_parallel_devices(text: str, short_channel: bool = False,
                              finger_count: int = 2) -> str:
    """Add directly placed, parallel NFET pairs in the parent channel."""
    sections = {
        "ndiffusion": (
            "rect 22300 18690 22900 18810\nrect 23100 18690 23700 18810\n"
            "rect 25300 18690 25900 18810\nrect 26100 18690 26700 18810"
        ),
        "polysilicon": (
            "rect 22575 18200 22605 19200\nrect 23375 18200 23405 19200\n"
            "rect 25575 18200 25605 19200\nrect 26375 18200 26405 19200"
            if short_channel else
            "rect 22560 18200 22620 19200\nrect 23360 18200 23420 19200\n"
            "rect 25560 18200 25620 19200\nrect 26360 18200 26420 19200"
        ),
        "ndc": (
            "rect 22340 18700 22460 18760\nrect 22740 18700 22860 18760\n"
            "rect 23140 18700 23260 18760\nrect 23540 18700 23660 18760\n"
            "rect 25340 18700 25460 18760\nrect 25740 18700 25860 18760\n"
            "rect 26140 18700 26260 18760\nrect 26540 18700 26660 18760"
        ),
        "mcon": (
            "rect 22340 18700 22460 18760\nrect 22740 18700 22860 18760\n"
            "rect 23140 18700 23260 18760\nrect 23540 18700 23660 18760\n"
            "rect 25340 18700 25460 18760\nrect 25740 18700 25860 18760\n"
            "rect 26140 18700 26260 18760\nrect 26540 18700 26660 18760\n"
            "rect 22560 18250 22620 18300\nrect 23360 18250 23420 18300\n"
            "rect 25560 18250 25620 18300\nrect 26360 18250 26420 18300"
        ),
        "metal1": (
            "rect 22300 18620 22500 18800\nrect 22700 18620 22900 18800\n"
            "rect 23100 18620 23300 18800\nrect 23500 18620 23700 18800\n"
            "rect 22400 18500 22460 18740\nrect 23200 18500 23260 18740\n"
            "rect 22400 18500 23260 18560\n"
            "rect 22800 18740 22860 19340\nrect 23600 18740 23660 19340\n"
            "rect 22800 19300 23660 19360\n"
            "rect 25300 18620 25500 18800\nrect 25700 18620 25900 18800\n"
            "rect 26100 18620 26300 18800\nrect 26500 18620 26700 18800\n"
            "rect 25400 18500 25460 18740\nrect 26200 18500 26260 18740\n"
            "rect 25400 18500 26260 18560\n"
            "rect 25800 18740 25860 19340\nrect 26600 18740 26660 19340\n"
            "rect 25800 19300 26660 19360\n"
            "rect 22540 18250 22640 18300\nrect 23340 18250 23440 18300\n"
            "rect 25540 18250 25640 18300\nrect 26340 18250 26440 18300\n"
            "rect 23000 19800 23200 19900\nrect 26000 19800 26200 19900"
        ),
        "metal2": (
            "rect 22500 18250 23480 18300\nrect 25500 18250 26480 18300"
        ),
        "via1": (
            "rect 22560 18250 22620 18300\nrect 23360 18250 23420 18300\n"
            "rect 25560 18250 25620 18300\nrect 26360 18250 26420 18300"
        ),
        "pc": (
            "rect 22560 18250 22620 18300\nrect 23360 18250 23420 18300\n"
            "rect 25560 18250 25620 18300\nrect 26360 18250 26420 18300"
        ),
        "locali": (
            "rect 22560 18250 22620 18300\nrect 23360 18250 23420 18300\n"
            "rect 25560 18250 25620 18300\nrect 26360 18250 26420 18300"
        ),
        "psubdiff": "rect 23000 19800 23200 19900\nrect 26000 19800 26200 19900",
        "psubdiffcont": "rect 23000 19800 23200 19900\nrect 26000 19800 26200 19900",
        "viali": "rect 23000 19800 23200 19900\nrect 26000 19800 26200 19900",
    }
    if finger_count > 2:
        for index in range(2, finger_count):
            for base in (22300 + index * 800, 25300 + index * 800):
                gate_left = base + 260
                gate_right = base + (290 if short_channel else 320)
                source_left, source_right = base, base + 200
                drain_left, drain_right = base + 400, base + 600
                contact_source_left, contact_source_right = base + 40, base + 160
                contact_drain_left, contact_drain_right = base + 440, base + 560
                sections["ndiffusion"] += f"\nrect {base} 18690 {base + 600} 18810"
                sections["polysilicon"] += f"\nrect {gate_left} 18200 {gate_right} 19200"
                sections["ndc"] += (f"\nrect {contact_source_left} 18700 {contact_source_right} 18760"
                                    f"\nrect {contact_drain_left} 18700 {contact_drain_right} 18760")
                sections["mcon"] += (f"\nrect {contact_source_left} 18700 {contact_source_right} 18760"
                                     f"\nrect {contact_drain_left} 18700 {contact_drain_right} 18760"
                                     f"\nrect {gate_left} 18250 {gate_right} 18300")
                sections["metal1"] += (f"\nrect {source_left} 18620 {source_right} 18800"
                                        f"\nrect {drain_left} 18620 {drain_right} 18800"
                                        f"\nrect {base + 100} 18500 {base + 160} 18740"
                                        f"\nrect {base + 100} 18500 {base + 960} 18560"
                                        f"\nrect {base + 500} 18740 {base + 560} 19340"
                                        f"\nrect {base + 500} 19300 {base + 1060} 19360"
                                        f"\nrect {gate_left - 20} 18250 {gate_right + 20} 18300")
                sections["metal2"] += f"\nrect {gate_left - 60} 18250 {gate_right + 60} 18300"
                sections["via1"] += f"\nrect {gate_left} 18250 {gate_right} 18300"
                sections["pc"] += f"\nrect {gate_left} 18250 {gate_right} 18300"
                sections["locali"] += f"\nrect {gate_left} 18250 {gate_right} 18300"
        # Extend each control and common source/drain corridor to the last
        # finger; the first-finger parent contacts remain unchanged.
        p_last = 22300 + (finger_count - 1) * 800
        n_last = 25300 + (finger_count - 1) * 800
        sections["metal1"] = sections["metal1"].replace("23260 18560", f"{p_last + 960} 18560")
        sections["metal1"] = sections["metal1"].replace("23660 19360", f"{p_last + 1060} 19360")
        sections["metal1"] = sections["metal1"].replace("26260 18560", f"{n_last + 960} 18560")
        sections["metal1"] = sections["metal1"].replace("26660 19360", f"{n_last + 1060} 19360")
        sections["metal2"] = sections["metal2"].replace("23480 18300", f"{p_last + 780} 18300")
        sections["metal2"] = sections["metal2"].replace("26480 18300", f"{n_last + 780} 18300")
    for section, shapes in sections.items():
        text = add_section(text, section, shapes)
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--omit-drain-escapes", action="store_true")
    parser.add_argument("--omit-preamp-cells", action="store_true")
    parser.add_argument("--move-preamp-cells-only", action="store_true")
    parser.add_argument("--outer-routes", action="store_true")
    parser.add_argument("--wide-preamp", action="store_true",
                        help="Use a wider diffusion window for both parent-bound input devices.")
    parser.add_argument("--parallel-preamp", action="store_true",
                        help="Add a matched parallel NFET finger to both parent-bound input devices.")
    parser.add_argument("--vertical-parallel-preamp", action="store_true",
                        help="Add a matched parallel finger within the original child footprint.")
    parser.add_argument("--flat-parallel-preamp", action="store_true",
                        help="Place the matched parallel preamps directly in the parent layout.")
    parser.add_argument("--short-channel-preamp", action="store_true",
                        help="Use a narrower gate for the flat parallel preamp fingers.")
    parser.add_argument("--flat-finger-count", type=int, default=2,
                        help="Number of directly placed matched fingers per input (2 or 3).")
    args = parser.parse_args()
    if args.flat_finger_count not in (2, 3):
        raise SystemExit("--flat-finger-count must be 2 or 3")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    for item in SOURCE.parent.iterdir():
        # Layout sources and JSON metadata are inputs.  Never copy prior
        # extraction products into a new candidate: Magic may reuse them and
        # silently make the resulting SPICE stale.
        if item.is_file() and item.suffix in {".mag", ".json"}:
            (out / item.name).write_bytes(item.read_bytes())
    # Replace the scaffold's earlier exploratory primitives with the
    # regenerated cells whose source/drain separation was independently
    # extracted and checked.
    (out / "preamp_p_nfet.mag").write_bytes(PRIMITIVE_P.read_bytes())
    (out / "preamp_n_nfet.mag").write_bytes(PRIMITIVE_N.read_bytes())
    # This regenerated latch has the same escape-coordinate contract as the
    # parent wrapper, but its extracted 11-device topology passes sub-block
    # LVS at the nominal 1.2-um widths.
    (out / "escaped_input_latch.mag").write_bytes(BALANCED_LATCH.read_bytes())
    layout = (out / "aimc_converter_macro_active_candidate.mag").read_text(encoding="utf-8")
    if args.outer_routes:
        # Keep the balanced latch in its own footprint.  The two preamps sit
        # in the open outer channel; all following routes are deliberately
        # on layers/channels that do not cross latch geometry.
        layout = layout.replace("transform 1 0 7680 0 1 360", "transform 1 0 22000 0 1 18000")
        layout = layout.replace("box 7680 360 8880 2260", "box 22000 18000 23200 19900")
        layout = layout.replace("transform 1 0 10680 0 1 360", "transform 1 0 25000 0 1 18000")
        layout = layout.replace("box 10680 360 11880 2260", "box 25000 18000 26200 19900")
        if args.parallel_preamp:
            layout = layout.replace("box 22000 18000 23200 19900", "box 22000 18000 23700 19900")
            layout = layout.replace("box 25000 18000 26200 19900", "box 25000 18000 26700 19900")
        # Give each placed primitive an explicit parent-facing interface.
        # Magic otherwise keeps the child ports as physical_preamp_*/source,
        # which cannot be renamed by a label on the parent geometry.
        p_bound = PRIMITIVE_P.read_text(encoding="utf-8")
        if args.wide_preamp:
            p_bound = p_bound.replace("rect 300 690 900 810", "rect 300 540 900 960")
        if args.parallel_preamp:
            p_bound = add_parallel_finger(p_bound)
        if args.vertical_parallel_preamp:
            p_bound = add_vertical_parallel_finger(p_bound)
        p_bound = p_bound.replace("preamp_p_nfet", "preamp_p_parent_bound", 1)
        p_bound = p_bound.replace("0 source", "0 preamp_iso_tail_ext")
        p_bound = p_bound.replace("0 drain", "0 latch_sense_p_ext")
        p_bound = p_bound.replace("0 gate", "0 row_drive")
        p_bound = p_bound.replace("0 body", "0 vss_escape")
        n_bound = PRIMITIVE_N.read_text(encoding="utf-8")
        if args.wide_preamp:
            n_bound = n_bound.replace("rect 300 690 900 810", "rect 300 540 900 960")
        if args.parallel_preamp:
            n_bound = add_parallel_finger(n_bound)
        if args.vertical_parallel_preamp:
            n_bound = add_vertical_parallel_finger(n_bound)
        n_bound = n_bound.replace("preamp_n_nfet", "preamp_n_parent_bound", 1)
        n_bound = n_bound.replace("0 source", "0 preamp_iso_tail_ext")
        n_bound = n_bound.replace("0 drain", "0 latch_sense_n_ext")
        n_bound = n_bound.replace("0 gate", "0 sar_comparator_input")
        n_bound = n_bound.replace("0 body", "0 vss_escape")
        (out / "preamp_p_parent_bound.mag").write_text(p_bound, encoding="utf-8")
        (out / "preamp_n_parent_bound.mag").write_text(n_bound, encoding="utf-8")
        layout = layout.replace("use preamp_p_nfet physical_preamp_p", "use preamp_p_parent_bound physical_preamp_p")
        layout = layout.replace("use preamp_n_nfet physical_preamp_n", "use preamp_n_parent_bound physical_preamp_n")
        if args.flat_parallel_preamp:
            for block in (
                "use preamp_p_parent_bound physical_preamp_p\ntimestamp 1789000000\n"
                "transform 1 0 22000 0 1 18000\nbox 22000 18000 23200 19900\n",
                "use preamp_n_parent_bound physical_preamp_n\ntimestamp 1789000000\n"
                "transform 1 0 25000 0 1 18000\nbox 25000 18000 26200 19900\n",
            ):
                layout = layout.replace(block, "")
            layout = add_flat_parallel_devices(layout, args.short_channel_preamp,
                                                args.flat_finger_count)
        # The scaffold already contains an exploratory N-output escape at
        # this coordinate. Remove it before adding the corrected source/drain
        # trunks below; otherwise the inherited escape reconnects the output
        # to the shared tail even after the new route is fixed.
        layout = layout.replace("rect 27000 19000 27060 24000\n", "")
        for label in (
            "rlabel metal1 32300 620 32500 800 0 physical_preamp_p.source\n",
            "rlabel metal1 32700 620 32900 800 0 physical_preamp_p.drain\n",
            "rlabel metal2 8180 610 8360 660 0 physical_preamp_p.gate\n",
            "rlabel metal1 8680 2160 8880 2260 0 physical_preamp_p.body\n",
            "rlabel metal1 10980 620 11180 800 0 physical_preamp_n.source\n",
            "rlabel metal1 11380 620 11580 800 0 physical_preamp_n.drain\n",
            "rlabel metal2 11180 610 11360 660 0 physical_preamp_n.gate\n",
            "rlabel metal1 11680 2160 11880 2260 0 physical_preamp_n.body\n",
        ):
            layout = layout.replace(label, "")
        via1 = "rect 22400 18670 22460 18730\nrect 22800 18670 22860 18730\nrect 25400 18670 25460 18730\nrect 25800 18670 25860 18730"
        via2 = "rect 22400 18670 22460 18730\nrect 22800 18670 22860 18730\nrect 25400 18670 25460 18730\nrect 25800 18670 25860 18730\nrect 22530 18220 22590 18280\nrect 25530 18220 25590 18280\nrect 1800 20470 1860 20530\nrect 21000 20970 21060 21030"
        via3 = "rect 22800 18670 22860 18730\nrect 25800 18670 25860 18730"
        # Only drain/output endpoints receive the M4/M5 transition. Source
        # endpoints stop at M3 so an output rail cannot short into the tail.
        via4 = "rect 22800 18670 22860 18730\nrect 25800 18670 25860 18730\nrect 25800 18970 25860 19030\nrect 22530 18220 22590 18280\nrect 25530 18220 25590 18280\nrect 4000 18670 4060 18730\nrect 4000 970 4060 1030\nrect 16000 19470 16060 19530\nrect 16000 970 16060 1030"
        layout = add_section(layout, "via1", via1)
        layout = add_section(layout, "via2", via2)
        layout = add_section(layout, "via3", via3)
        layout = add_section(layout, "via4", via4)
        layout = add_section(layout, "metal3",
                             "rect 1800 20470 22560 20530\nrect 22530 18250 22590 20500\n"
                             "rect 21000 20970 25560 21030\nrect 25530 18250 25590 21000")
        # Shared tail uses the lower routing layer. The source vias stop at
        # M3, and the explicit label is placed on this same conductor.
        layout = add_section(layout, "metal3",
                             "rect 22400 18670 22460 19470\n"
                             "rect 25400 18670 25460 19470\n"
                             "rect 22400 19440 25400 19500")
        # The scaffold's old N-output vertical escape meets the shared-tail
        # rail below. Remove it before emitting the isolated parent routes;
        # otherwise the N latch net and preamp tail are physically merged.
        layout = layout.replace("rect 15970 1000 16030 19500\n", "")
        # Remove inherited full-stack source contacts. The source terminals
        # must stop at M3; the via1-via3 copies emitted below reconnect them
        # to the shared tail without reaching either output layer.
        layout = layout.replace("rect 22400 18670 22460 18730\n", "")
        layout = layout.replace("rect 25400 18670 25460 18730\n", "")
        for old_route in (
            "rect 22400 17970 22460 24000\n",
            "rect 22400 23970 27000 24030\n",
            "rect 25400 18670 25460 19500\n",
        ):
            layout = layout.replace(old_route, "")
        # The source-tail route occupies M3. Remove the inherited M3 gate
        # trunks that crossed it, then route the gates directly on M2 from
        # their child contacts to their existing parent control rails.
        layout = layout.replace("rect 22530 18250 22590 20500\n", "")
        layout = layout.replace("rect 25530 18250 25590 21000\n", "")
        layout = layout.replace("rect 21000 18320 25560 18380\n", "")
        layout = layout.replace("rect 25530 18220 25590 18350\n", "")
        layout = add_section(
            layout, "metal2",
            "rect 1800 18220 22590 18280",
        )
        # The N control crosses the P control corridor on M5, then drops
        # through one complete via stack to the existing parent M2 rail.
        layout = add_section(
            layout, "metal5",
            "rect 21000 500 21060 18350\n"
            "rect 21000 18320 25560 18380\n"
            "rect 25530 18220 25590 18350",
        )
        layout = add_section(
            layout, "via1",
            "rect 21000 500 21060 560\nrect 25530 18220 25590 18280",
        )
        layout = add_section(
            layout, "via2",
            "rect 21000 500 21060 560\nrect 25530 18220 25590 18280",
        )
        layout = add_section(
            layout, "via3",
            "rect 21000 500 21060 560\nrect 25530 18220 25590 18280",
        )
        layout = add_section(
            layout, "via4",
            "rect 21000 500 21060 560\nrect 25530 18220 25590 18280",
        )
        # Restore only the lower-layer contacts removed by the cleanup. These
        # connect both sources to the M3 tail while keeping them isolated from
        # the M4/M5 output layers.
        for layer in ("via1", "via2"):
            layout = add_section(
                layout, layer,
                "rect 22400 18670 22460 18730\nrect 25400 18670 25460 18730",
            )
        # Isolated P-drain-to-latch-output experiment. The N output remains
        # untouched so any new failure is attributable to this one route.
        layout = add_section(layout, "metal4", "rect 4000 18670 22800 18730")
        layout = add_section(layout, "metal5",
                             "rect 3970 1000 4030 18670\n"
                             "rect 15970 1000 16030 18970\n"
                             "rect 15970 18940 25800 19000\n"
                             "rect 25800 18670 25860 19000\nrect 25800 18970 27000 19030")
        layout = add_section(layout, "labels",
                             "rlabel metal1 22340 18640 22460 18800 0 preamp_iso_tail_ext\n"
                             "rlabel metal1 22740 18640 22860 18800 0 latch_sense_p_ext\n"
                             "rlabel metal2 22530 18220 22590 18280 0 row_drive\n"
                             "rlabel metal1 25340 18640 25460 18800 0 preamp_iso_tail_ext\n"
                             "rlabel metal1 25740 18640 25860 18800 0 latch_sense_n_ext\n"
                             "rlabel metal2 25530 18220 25590 18280 0 sar_comparator_input\n"
                             "rlabel metal3 23900 19440 24100 19500 0 preamp_iso_tail_ext\n"
                             "port 16 nsew\n"
                             "rlabel metal1 22000 19800 22200 19900 0 vss_escape\n"
                             "rlabel metal1 25000 19800 25200 19900 0 vss_escape")
        (out / "aimc_converter_macro_active_candidate.mag").write_text(layout.replace("\n\n", "\n"), encoding="utf-8")
        flat_cell = ("aimc_converter_macro_active_candidate_flat_parallel"
                     if args.flat_parallel_preamp else
                     "aimc_converter_macro_active_candidate_flat")
        flatten_commands = (f"flatten {flat_cell}\nload {flat_cell} -force\nselect top cell\n")
        (out / "extract-active-converter-macro.tcl").write_text(
            f"drc on\npath search +{out}\n"
            "load aimc_converter_macro_active_candidate -force\nselect top cell\n"
            + flatten_commands
            + "drc check\ndrc count\nextract all\next2spice lvs\n"
            + "writeall\n"
            "ext2spice cthresh 0\next2spice rthresh 0\n"
            "ext2spice -o aimc_converter_macro_active_candidate_extracted.spice\nquit -noprompt\n",
            encoding="utf-8")
        (out / "candidate-build.json").write_text(json.dumps({
            "result_type": "two_single_preamp_parent_outer_routed",
            "routing": "non-overlapping preamps; M3 controls, M5 P output, M4 N output, M5 shared tail",
            "preamp_geometry": ("flat_parallel_short_channel" if args.short_channel_preamp else
                                "flat_parallel_devices" if args.flat_parallel_preamp else
                                "vertical_parallel_finger" if args.vertical_parallel_preamp else
                                "parallel_finger" if args.parallel_preamp else
                                "wide_diffusion_window" if args.wide_preamp else
                                "nominal_diffusion_window"),
            "flat_finger_count": args.flat_finger_count,
            "accepted_converter": False,
            "claim_boundary": "Parent routing experiment; requires DRC, extraction, strict binding, LVS, and electrical qualification."
        }, indent=2) + "\n", encoding="utf-8")
        return
    if args.move_preamp_cells_only:
        layout = layout.replace("transform 1 0 7680 0 1 360", "transform 1 0 22000 0 1 18000")
        layout = layout.replace("box 7680 360 8880 2260", "box 22000 18000 23200 19900")
        layout = layout.replace("transform 1 0 10680 0 1 360", "transform 1 0 25000 0 1 18000")
        layout = layout.replace("box 10680 360 11880 2260", "box 25000 18000 26200 19900")
    if args.omit_preamp_cells:
        for cell, instance in (("preamp_p_nfet", "physical_preamp_p"), ("preamp_n_nfet", "physical_preamp_n")):
            lines = layout.splitlines()
            kept = []
            skip = False
            for line in lines:
                if line == f"use {cell} {instance}":
                    skip = True
                    continue
                if skip and line.startswith("box "):
                    skip = False
                    continue
                if not skip:
                    kept.append(line)
            layout = "\n".join(kept) + "\n"
    # Remove the placement-only child labels. Parent labels below own the
    # integrated net names after flattening.
    for label in (
        "rlabel metal1 32300 620 32500 800 0 physical_preamp_p.source\n",
        "rlabel metal1 32700 620 32900 800 0 physical_preamp_p.drain\n",
        "rlabel metal2 8180 610 8360 660 0 physical_preamp_p.gate\n",
        "rlabel metal1 8680 2160 8880 2260 0 physical_preamp_p.body\n",
        "rlabel metal1 10980 620 11180 800 0 physical_preamp_n.source\n",
        "rlabel metal1 11380 620 11580 800 0 physical_preamp_n.drain\n",
        "rlabel metal2 11180 610 11360 660 0 physical_preamp_n.gate\n",
        "rlabel metal1 11680 2160 11880 2260 0 physical_preamp_n.body\n",
    ):
        layout = layout.replace(label, "")
    # Child geometry centers: P drain/source/gate=(8480,1000)/(8080,1000)/(8240,630);
    # N drain/source/gate=(11480,1000)/(11080,1000)/(11240,630).
    drain_vias = "" if args.omit_drain_escapes else "rect 8480 970 8540 1030\nrect 11480 1040 11540 1100\n"
    layout = add_section(layout, "via1", drain_vias +
                         "rect 8080 970 8140 1030\nrect 11080 970 11140 1030\n"
                         "rect 8240 600 8300 660\nrect 11240 600 11300 660\n"
                         "rect 1800 2970 1860 3030\nrect 21000 470 21060 530")
    for section in ("via2", "via3", "via4"):
        layout = add_section(layout, section, "rect 8080 970 8140 1030\nrect 11080 970 11140 1030\n"
                             "rect 8240 600 8300 660\nrect 11240 600 11300 660")
    layout = add_section(layout, "via2", "rect 1800 2970 1860 3030\nrect 21000 470 21060 530")
    layout = add_section(layout, "via3", "rect 1800 2970 1860 3030\nrect 21000 470 21060 530")
    layout = add_section(layout, "via4", "rect 1800 2970 1860 3030\nrect 21000 470 21060 530")
    layout = add_section(layout, "metal5", "rect 1800 2970 8240 3030\nrect 8240 630 8300 3000\n"
                         "rect 11240 3470 21000 3530\nrect 11240 630 11300 3500\n"
                         "rect 21000 470 21060 3500\n"
                         "rect 8080 500 8140 1000\nrect 8080 470 9000 530\n"
                         "rect 9000 500 9060 4500\n"
                         "rect 9000 4470 11080 4530\n"
                         "rect 11080 1000 11140 4500")
    drain_labels = "" if args.omit_drain_escapes else "rlabel metal2 8450 970 8570 1030 0 latch_sense_p_ext\n"
    layout = add_section(layout, "labels",
                         "rlabel metal5 9500 4470 9700 4530 0 preamp_iso_tail_ext\n"
                         "rlabel metal1 8680 2160 8880 2260 0 vss_escape\n"
                         "rlabel metal1 11680 2160 11880 2260 0 vss_escape")
    (out / "aimc_converter_macro_active_candidate.mag").write_text(layout.replace("\n\n", "\n"), encoding="utf-8")
    (out / "extract-active-converter-macro.tcl").write_text(
        "drc on\n"
        f"path search +{out}\n"
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
    (out / "candidate-build.json").write_text(json.dumps({
        "result_type": "two_single_preamp_parent_wired",
        "source": str(SOURCE.relative_to(ROOT)),
        "routing": "separate metal5 gate tracks, shared metal5 preamp tail, local drain-to-latch contacts",
        "accepted_converter": False,
        "claim_boundary": "Wired parent experiment only; requires DRC, extraction, strict binding, LVS, and transient validation."
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
