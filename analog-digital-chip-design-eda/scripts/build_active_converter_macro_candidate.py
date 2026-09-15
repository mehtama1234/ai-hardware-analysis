#!/usr/bin/env python3
"""Assemble a real hierarchical Sky130 candidate macro for extraction.

This is an evidence-building experiment.  It deliberately does not write the
strict post-layout payload: the existing DAC/ADC/mux cells are starter
geometry, while the latch instance is transistor geometry.  The output is a
single inspectable hierarchical layout and extracted SPICE netlist that makes
that boundary explicit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from audit_extracted_converter_boundary import audit as audit_preamp_boundary


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELLS = WORKBENCH / "cells"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def use_line(cell: str, instance: str, x: int, y: int, w: int, h: int) -> str:
    return f"use {cell} {instance}\ntimestamp 1788727000\ntransform 1 0 {x} 0 1 {y}\nbox {x} {y} {x + w} {y + h}"


def escaped_macro_text() -> str:
    return "\n".join(
        [
            "magic", "tech sky130A", "timestamp 1788727000",
            use_line("row_dac_10b", "row_dac_10b_0", 0, 0, 1200, 520),
            use_line("sar_readout_12b", "sar_readout_12b_0", 2200, 0, 1400, 640),
            use_line("shared_converter_mux", "shared_converter_mux_0", 0, 1600, 1600, 700),
            use_line("escaped_input_latch", "converter_latch_0", 10000, 0, 18060, 17060),
            "<< metal1 >>", "rect 0 2400 30000 2480", "rect 0 25500 30000 25580",
            "<< metal2 >>", "rect 1800 0 1860 25580", "rect 21000 0 21060 500",
            "<< via1 >>", "rect 1170 230 1230 290",
            "<< via2 >>", "rect 1170 230 1230 290", "rect 1770 230 1830 290",
            "rect 3970 230 4030 290", "rect 20970 230 21030 290",
            "rect 2290 470 2350 530",
            "rect 2290 17970 2350 18030",
            "<< via3 >>", "rect 3970 230 4030 290", "rect 15970 230 16030 290",
            "rect 20970 230 21030 290", "rect 2290 17970 2350 18030",
            "rect 28970 200 29030 260",
            "<< metal3 >>", "rect 1170 230 4030 290",
            "rect 2290 470 2350 18030",
            "<< metal4 >>", "rect 3970 230 4030 290", "rect 15970 230 21030 290",
            "rect 2290 17970 29030 18030", "rect 28970 230 29030 18030",
            "rect 2970 3970 4030 4030", "rect 15970 3970 23030 4030",
            "rect 2970 12250 4030 12310", "rect 2970 15050 4030 15110",
            "rect 15970 10470 17030 10530", "rect 15970 13470 17030 13530",
            "rect 2970 16970 4030 17030",
            "rect 3970 970 4030 1030", "rect 15970 970 16030 1030",
            "rect 3970 -530 4030 -470", "rect 15970 15770 16030 15830",
            "<< labels >>",
            "rlabel metal1 0 2400 30000 2480 0 vss", "port 1 nsew",
            "rlabel metal1 0 25500 30000 25580 0 vdd", "port 2 nsew",
            "rlabel metal2 1800 0 1860 25580 0 row_drive", "port 3 nsew",
            "rlabel metal2 21000 0 21060 500 0 sar_comparator_input", "port 4 nsew",
            "rlabel metal4 2970 3970 3030 4030 0 decision_p", "port 5 nsew",
            "rlabel metal4 22970 3970 23030 4030 0 decision_n", "port 6 nsew",
            "rlabel metal4 2970 12250 3030 12310 0 reset", "port 7 nsew",
            "rlabel metal4 2970 15050 3030 15110 0 eval", "port 8 nsew",
            "rlabel metal4 2970 16970 3030 17030 0 vss_escape", "port 9 nsew",
            "rlabel metal4 3970 970 4030 1030 0 latch_sense_p_ext", "port 10 nsew",
            "rlabel metal4 15970 970 16030 1030 0 latch_sense_n_ext", "port 11 nsew",
            "rlabel metal4 3970 -530 4030 -470 0 iso_tail_ext", "port 12 nsew",
            "rlabel metal4 15970 15770 16030 15830 0 tail_ext", "port 13 nsew",
            "rlabel metal4 16970 10470 17030 10530 0 vdd_active_ext", "port 14 nsew",
            "rlabel metal4 16970 13470 17030 13530 0 vdd_ext", "port 15 nsew",
            "<< end >>", "",
        ]
    )


def macro_text(latch_cell: str = "sky130_isolated_frontend_active_load_latch_v2") -> str:
    if latch_cell == "escaped_input_latch":
        return escaped_macro_text()
    return "\n".join(
        [
            "magic",
            "tech sky130A",
            "timestamp 1788727000",
            use_line("row_dac_10b", "row_dac_10b_0", 0, 0, 1200, 520),
            use_line("sar_readout_12b", "sar_readout_12b_0", 2200, 0, 1400, 640),
            use_line("shared_converter_mux", "shared_converter_mux_0", 0, 1600, 1600, 700),
            use_line("sky130_isolated_frontend_active_load_latch_v2", "converter_latch_0", 5200, 0, 17000, 17000),
            "<< metal1 >>",
            "rect 0 2400 22200 2480",
            "rect 0 25500 22200 25580",
            "<< metal2 >>",
            "rect 1800 0 1860 25580",
            "rect 4000 0 4060 25580",
            "rect 21000 0 21060 25580",
            "<< via1 >>",
            "rect 1170 230 1230 290",
            "<< via2 >>",
            "rect 1170 230 1230 290",
            "rect 1770 230 1830 290",
            "rect 5670 250 5730 310",
            "<< metal3 >>",
            "rect 1170 230 5730 290",
            "<< labels >>",
            "rlabel metal1 0 2400 22200 2480 0 vss",
            "port 1 nsew",
            "rlabel metal1 0 25500 22200 25580 0 vdd",
            "port 2 nsew",
            "rlabel metal2 1800 0 1860 25580 0 row_drive",
            "port 3 nsew",
            "rlabel metal2 4000 0 4060 25580 0 column_sense",
            "port 4 nsew",
            "rlabel metal2 21000 0 21060 25580 0 digital_code_out",
            "port 5 nsew",
            "<< end >>",
            "",
        ]
    )


def physical_preamp_macro_text() -> str:
    """Add the extracted active-isolation pair in front of the latch.

    The pair is a real Sky130 transistor cell.  Its drain loads remain an
    explicit transient assumption until a matched physical load is laid out.
    """
    source = escaped_macro_text().replace(
        use_line("escaped_input_latch", "converter_latch_0", 10000, 0, 18060, 17060),
        use_line("escaped_input_latch", "converter_latch_0", 10000, 0, 18060, 17060)
        + "\n" + use_line("sky130_transistor_active_isolation_pair", "physical_preamp_0", 32000, 0, 2200, 1200),
    )
    if os.environ.get("AIMC_PREAMP_NO_ROUTES") == "1":
        return source

    def add(layer: str, geometry: str) -> None:
        nonlocal source
        source = source.replace(f"<< {layer} >>", f"<< {layer} >>\n{geometry}", 1)

    source = source.replace("rect 0 2400 30000 2480", "rect 0 2400 36000 2480")
    source = source.replace("rect 0 25500 30000 25580", "rect 0 25500 36000 25580")
    add("metal2", "rect 21000 470 33780 530\nrect 33750 270 33810 530")
    add("via2", "rect 1800 350 1860 410\nrect 32560 270 32620 330\nrect 32770 1770 32830 1830\nrect 33570 2170 33630 2230")
    add("via3", "rect 1800 350 1860 410\nrect 32560 270 32620 330\nrect 32770 1770 32830 1830\nrect 33570 2170 33630 2230")
    add("via1", "rect 32770 1770 32830 1830\nrect 33570 2170 33630 2230")
    add("metal3", "rect 1770 320 1860 380\nrect 1800 320 32560 380\nrect 32530 270 32590 350")
    add("metal4", "rect 3970 900 32800 960\nrect 32770 900 32830 1830\nrect 15970 1040 33600 1100\nrect 33570 1040 33630 2230\nrect 32770 1770 32830 1830\nrect 33570 2170 33630 2230")
    add("labels", "rlabel metal1 32700 620 32900 800 0 latch_sense_p_ext\n"
                    "rlabel metal1 33500 620 33700 800 0 latch_sense_n_ext\n"
                    "rlabel metal1 32300 620 32500 800 0 preamp_iso_tail_ext\n"
                    "port 16 nsew")
    return source


def tcl_text(output_name: str, search_dir: Path | None = None, flatten: bool = False) -> str:
    search = f"path search +{search_dir}\npath search +{CELLS}" if search_dir else f"path search +{CELLS}"
    flatten_command = (
        "flatten aimc_converter_macro_active_candidate_flat\n"
        "load aimc_converter_macro_active_candidate_flat -force\n"
        "select top cell"
        if flatten else ""
    )
    return "\n".join(
        [
            "drc on",
            search,
            "load aimc_converter_macro_active_candidate -force",
            "select top cell",
            flatten_command,
            "drc check",
            "drc catchup",
            "drc count",
            "extract all",
            "ext2spice lvs",
            "ext2spice cthresh 0",
            "ext2spice rthresh 0",
            f"ext2spice -o {output_name}",
            "quit -noprompt",
            "",
        ]
    )


def parse_drc(stdout: str) -> int | None:
    error_tiles = [int(value) for value in re.findall(r"has (\d+) error tiles", stdout)]
    if error_tiles and max(error_tiles):
        return max(error_tiles)
    match = re.search(r"Total DRC errors found:\s*(\d+)", stdout)
    if match:
        return int(match.group(1))
    for line in stdout.splitlines():
        if "drc count" in line.lower():
            continue
        parts = line.strip().split()
        if len(parts) == 1 and parts[0].isdigit():
            return int(parts[0])
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--latch-source", type=Path, help="Use a generated latch cell with explicit edge input escapes.")
    parser.add_argument("--physical-preamp-source", type=Path, help="Add the extracted Sky130 active-isolation pair ahead of the latch.")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = (args.output_dir or EVIDENCE / "active-converter-macro-candidate" / stamp).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    top = output_dir / "aimc_converter_macro_active_candidate.mag"
    tcl = output_dir / "extract-active-converter-macro.tcl"
    netlist_name = "aimc_converter_macro_active_candidate_extracted.spice"
    netlist = output_dir / netlist_name
    latch_cell = "sky130_isolated_frontend_active_load_latch_v2"
    if args.latch_source:
        latch_cell = "escaped_input_latch"
        shutil.copy2(args.latch_source.resolve(), output_dir / "escaped_input_latch.mag")
    if args.physical_preamp_source and not args.latch_source:
        raise SystemExit("--physical-preamp-source requires --latch-source")
    top.write_text(physical_preamp_macro_text() if args.physical_preamp_source else macro_text(latch_cell), encoding="utf-8")
    if args.latch_source:
        for starter_cell in ("row_dac_10b", "sar_readout_12b", "shared_converter_mux"):
            shutil.copy2(CELLS / f"{starter_cell}.mag", output_dir / f"{starter_cell}.mag")
    if args.physical_preamp_source:
        shutil.copy2(args.physical_preamp_source.resolve(), output_dir / "sky130_transistor_active_isolation_pair.mag")
    tcl.write_text(tcl_text(netlist_name, output_dir if args.latch_source else None, bool(args.physical_preamp_source)), encoding="utf-8")
    magic_bin = os.environ.get("MAGIC_BIN", "/home/mehtama1/eda-tools/magic-8.3.682/bin/magic")
    magic_env = os.environ.copy()
    magic_env.setdefault("PDK_ROOT", "/home/mehtama1/eda-tools/pdks")
    result = subprocess.run(
        [magic_bin, "-dnull", "-noconsole", "-rcfile", str(WORKBENCH / ".magicrc"), str(tcl)],
        cwd=output_dir,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
        env=magic_env,
    )
    netlist_text = netlist.read_text(encoding="utf-8") if netlist.is_file() else ""
    top_match = re.search(r"(?ms)^\.subckt aimc_converter_macro_active_candidate(?:_flat)?\s+(.+?)\n(?=X|C|\.ends)", netlist_text)
    top_ports = [port for port in top_match.group(1).split() if port != "+"] if top_match else []
    required_top_ports = ["vss", "vdd", "row_drive", "sar_comparator_input", "decision_p", "decision_n", "reset", "eval"]
    top_level_ports_complete = all(port in top_ports for port in required_top_ports)
    ext_path = output_dir / (
        "aimc_converter_macro_active_candidate_flat.ext"
        if args.physical_preamp_source
        else "aimc_converter_macro_active_candidate.ext"
    )
    ext_text = ext_path.read_text(encoding="utf-8") if ext_path.is_file() else ""
    physical_preamp_equivalences = {
        "iso_p_to_latch_sense_p": 'equiv "physical_preamp_0.iso_p" "latch_sense_p_ext_uq0"',
        "iso_n_to_latch_sense_n": 'equiv "physical_preamp_0.iso_n" "latch_sense_n_ext_uq0"',
        "iso_tail_to_external_bias": 'equiv "preamp_iso_tail_ext" "physical_preamp_0.iso_tail"',
        "sense_p_to_row_drive": 'equiv "row_drive" "converter_latch_0.sense_p"',
        "sense_n_to_sar_input": 'equiv "sar_comparator_input" "converter_latch_0.sense_n"',
    }
    final_netlist_boundary = audit_preamp_boundary(netlist_text)
    physical_preamp_routing_complete = bool(
        args.physical_preamp_source
        and final_netlist_boundary["physical_preamp_routing_complete"]
        and 'merge "converter_latch_0/latch_sense_n" "converter_latch_0/latch_sense_p"' not in ext_text
    )
    physical_preamp_routing_incomplete = bool(args.physical_preamp_source and not physical_preamp_routing_complete)
    if result.returncode == 0 and netlist.is_file() and physical_preamp_routing_incomplete:
        status = "active_macro_physical_preamp_routing_incomplete"
    elif result.returncode == 0 and netlist.is_file():
        status = "hierarchical_active_macro_extracted_not_converter_signoff" if top_level_ports_complete else "active_macro_extraction_topology_incomplete"
    else:
        status = "active_macro_extraction_failed"
    report = {
        "result_type": "sky130_active_converter_macro_candidate",
        "status": status,
        "run_id": stamp,
        "layout": rel(top),
        "extraction_script": rel(tcl),
        "extracted_netlist": rel(netlist),
        "magic_returncode": result.returncode,
        "magic_drc_count": parse_drc(result.stdout),
        "netlist_exists": netlist.is_file(),
        "top_level_ports": top_ports,
        "required_top_level_ports": required_top_ports,
        "top_level_ports_complete": top_level_ports_complete,
        "physical_preamp_routing_complete": physical_preamp_routing_complete,
        "physical_preamp_routing_incomplete": physical_preamp_routing_incomplete,
        "physical_preamp_final_netlist_audit": final_netlist_boundary if args.physical_preamp_source else None,
        "physical_preamp_extracted_equivalences": {
            name: marker in ext_text for name, marker in physical_preamp_equivalences.items()
        } if args.physical_preamp_source else {},
        "extracted_sky130_device_count": sum(
            1 for line in netlist.read_text(encoding="utf-8").splitlines()
            if "sky130_fd_pr__" in line
        ) if netlist.is_file() else 0,
        "extracted_subcircuit_count": sum(
            1 for line in netlist.read_text(encoding="utf-8").splitlines()
            if line.startswith(".subckt ")
        ) if netlist.is_file() else 0,
        "included_cells": ["row_dac_10b", "sar_readout_12b", "shared_converter_mux", latch_cell]
        + (["sky130_transistor_active_isolation_pair"] if args.physical_preamp_source else []),
        "transistor_geometry_present": True,
        "starter_geometry_present": True,
        "verified_top_level_connections": ["row_drive_to_latch_sense_p"] if not args.latch_source else (["row_drive_to_latch_sense_p", "sar_comparator_input_to_latch_sense_n_escape", "latch_out_p_to_decision_p", "latch_out_n_to_decision_n"] if not args.physical_preamp_source else ["latch_out_p_to_decision_p", "latch_out_n_to_decision_n"]),
        "unverified_top_level_connections": ["sar_comparator_input_to_latch_sense_n", "sample_path_to_column_sense", "sar_done_to_digital_code_out"] if not args.latch_source else (["sample_path_to_column_sense", "sar_done_to_digital_code_out", "sar_comparator_cell_to_macro_input", "reset_to_latch", "eval_to_latch", "vdd_active_to_latch"] if not args.physical_preamp_source else ["physical_preamp_iso_p_to_latch_sense_p", "physical_preamp_iso_n_to_latch_sense_n", "physical_preamp_sense_p_to_row_drive", "physical_preamp_sense_n_to_sar_input", "sample_path_to_column_sense", "sar_done_to_digital_code_out"]),
        "differential_input_integration_complete": False,
        "strict_signoff_ready": False,
        "claim_boundary": {
            "allowed": "one hierarchical layout containing the named starter converter regions and a real extracted Sky130 transistor latch instance",
            "not_allowed": "does not prove connected converter behavior, post-layout energy/latency/noise, full-converter LVS, area signoff, or break-even replacement",
        },
        "magic_output_tail": (result.stdout + result.stderr)[-2000:],
    }
    report_path = output_dir / "active-converter-macro-candidate.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("sky130_active_converter_macro_candidate")
    print(f"status,{report['status']}")
    print(f"magic_returncode,{result.returncode}")
    print(f"magic_drc_count,{report['magic_drc_count']}")
    print(f"netlist_exists,{report['netlist_exists']}")
    print(f"report,{report_path}")
    return 0 if report["status"] not in ("active_macro_extraction_failed", "active_macro_extraction_topology_incomplete", "active_macro_physical_preamp_routing_incomplete") else 1


if __name__ == "__main__":
    raise SystemExit(main())
