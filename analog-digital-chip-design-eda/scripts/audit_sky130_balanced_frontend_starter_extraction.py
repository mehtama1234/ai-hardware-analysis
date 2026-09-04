#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
CELL = LAB / "layout-workbench" / "cells" / "sky130_balanced_capacitive_isolation_frontend.mag"
EXT = LAB / "layout-workbench" / "cells" / "sky130_balanced_capacitive_isolation_frontend.ext"
SPICE = LAB / "layout-workbench" / "extracted" / "sky130_balanced_capacitive_isolation_frontend_extracted.spice"
TCL = LAB / "layout-workbench" / "extracted" / "extract-sky130_balanced_capacitive_isolation_frontend-smoke.tcl"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
WORK_ORDER = EVIDENCE / "sky130-balanced-frontend-work-order.json"
OUT_JSON = EVIDENCE / "sky130-balanced-frontend-starter-extraction.json"
OUT_MD = EVIDENCE / "sky130-balanced-frontend-starter-extraction.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def parse_ports(text: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(".subckt sky130_balanced_capacitive_isolation_frontend"):
            port_text = line
            next_index = index + 1
            while next_index < len(lines) and lines[next_index].startswith("+"):
                port_text += " " + lines[next_index][1:].strip()
                next_index += 1
            return port_text.split()[2:]
    return []


def capacitance_totals_ff(text: str, nodes: list[str]) -> dict[str, float]:
    totals = {node: 0.0 for node in nodes}
    for line in text.splitlines():
        match = re.match(r"C\d+\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line.strip())
        if not match:
            continue
        node_a, node_b, value = match.groups()
        for node in (node_a, node_b):
            if node in totals:
                totals[node] += float(value)
    return totals


def file_record(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "present": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Balanced Frontend Starter Extraction",
        "",
        f"- status: `{report['status']}`",
        f"- sense capacitance delta fF: `{report['sense_capacitance_delta_ff']:.6f}`",
        f"- required bias reduction factor: `{report['required_bias_reduction_factor']:.2f}x`",
        f"- accepted ready now: `{report['accepted_ready_now']}`",
        "",
        "## First Principle",
        "",
        "The earlier extracted cell failed because the latch-gate nodes were not balanced measuring nodes. Before asking whether a latch can decide, the physical frontend must show that its two balanced measuring nodes see the same kind of surroundings.",
        "",
        "This starter extraction checks only that first physical condition. It creates a named Sky130 Magic cell, extracts it, and measures the total capacitance connected to each sense node. Equal totals do not prove a comparator, but unequal totals would make the next proof meaningless.",
        "",
        "## Files",
        "",
        "| object | path | present | bytes |",
        "|---|---|---:|---:|",
    ]
    for name, record in report["files"].items():
        lines.append(f"| `{name}` | `{record['path']}` | `{record['present']}` | `{record['bytes']}` |")
    lines.extend(["", "## Extracted Ports", "", "`" + " ".join(report["extracted_ports"]) + "`", "", "## Capacitance Totals", "", "| node | total extracted capacitance fF |", "|---|---:|"])
    for node, value in report["capacitance_totals_ff"].items():
        lines.append(f"| `{node}` | `{value:.6f}` |")
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    work_order = json.loads(WORK_ORDER.read_text(encoding="utf-8"))
    text = SPICE.read_text(encoding="utf-8") if SPICE.is_file() else ""
    ports = parse_ports(text)
    required_ports = [port["name"] for port in work_order["ports"]]
    totals = capacitance_totals_ff(text, required_ports)
    sense_delta = abs(totals.get("sense_p", 0.0) - totals.get("sense_n", 0.0))
    all_files_present = all(path.is_file() and path.stat().st_size > 0 for path in [CELL, EXT, SPICE, TCL])
    ports_match = ports == required_ports
    report = {
        "result_type": "sky130_balanced_frontend_starter_extraction",
        "status": "balanced_frontend_starter_extracted_not_comparator_proof" if all_files_present and ports_match else "balanced_frontend_starter_extraction_incomplete",
        "source_work_order": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-work-order.json",
        "required_bias_reduction_factor": work_order["required_bias_reduction_factor"],
        "max_allowed_wrong_sign_bias_mv": work_order["max_allowed_wrong_sign_bias_mv"],
        "files": {
            "magic_cell": file_record(CELL),
            "magic_ext": file_record(EXT),
            "extracted_spice": file_record(SPICE),
            "extraction_tcl": file_record(TCL),
        },
        "required_ports": required_ports,
        "extracted_ports": ports,
        "ports_match_work_order": ports_match,
        "capacitance_totals_ff": totals,
        "sense_capacitance_delta_ff": sense_delta,
        "sense_capacitance_balanced": sense_delta <= 0.001,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "proves that the new named balanced starter cell exists, extracts, and has matched first-order sense-node capacitance",
            "not_allowed": "does not prove sign preservation, does not include active reset devices, does not prove latch resolution, does not run DRC/LVS, and does not write accepted post-layout evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_balanced_frontend_starter_extraction")
    print(f"status,{report['status']}")
    print(f"ports_match_work_order,{report['ports_match_work_order']}")
    print(f"sense_capacitance_delta_ff,{report['sense_capacitance_delta_ff']:.6f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
