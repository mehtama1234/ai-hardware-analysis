#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audit_analog_converter_physical_cell_gate import build_report as build_gate_report


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-flow-run.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-flow-run.md"

CELL_COMMANDS = [
    {
        "cell": "row_dac_10b",
        "extract_target": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp",
        "command": "magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl row_dac_10b.mag",
    },
    {
        "cell": "sar_readout_12b",
        "extract_target": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp",
        "command": "magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl sar_readout_12b.mag",
    },
    {
        "cell": "shared_converter_mux",
        "extract_target": "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp",
        "command": "magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl shared_converter_mux.mag",
    },
    {
        "cell": "aimc_converter_macro",
        "extract_target": "evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json",
        "command": "magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl aimc_converter_macro.mag",
    },
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def build_report() -> dict[str, Any]:
    gate = build_gate_report()
    missing_cells = [
        cell["name"]
        for cell in gate.get("required_cells", [])
        if isinstance(cell, dict) and cell.get("present") is not True
    ]
    blocked_commands = [
        {**item, "reason": f"missing physical cell {item['cell']}"}
        for item in CELL_COMMANDS
        if item["cell"] in missing_cells
    ]
    runnable_commands = [
        item for item in CELL_COMMANDS if item["cell"] not in missing_cells
    ]
    status = "physical_flow_blocked_waiting_for_converter_cells"
    if gate.get("all_required_cells_present") is True:
        status = "physical_flow_ready_for_manual_extraction_commands"
    return {
        "result_type": "analog_converter_physical_flow_run",
        "status": status,
        "workbench": rel(WORKBENCH),
        "source_gate_status": gate.get("status"),
        "required_cell_count": gate.get("required_cell_count"),
        "present_cell_count": gate.get("present_cell_count"),
        "missing_cell_count": gate.get("missing_cell_count"),
        "missing_cells": missing_cells,
        "blocked_command_count": len(blocked_commands),
        "runnable_command_count": len(runnable_commands),
        "blocked_commands": blocked_commands,
        "runnable_commands": runnable_commands,
        "next_after_extraction": [
            "python3 scripts/run_converter_post_layout_candidate_readiness.py",
            "python3 scripts/build_converter_post_layout_candidate_from_real_run.py --workspace evidence/aimc-simulator-adapters/candidate-post-layout ...",
            "python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json",
        ],
        "claim_boundary": {
            "allowed": "names the physical extraction command sequence and records why it cannot run yet",
            "not_allowed": "does not fabricate Magic output, extracted netlists, area records, rerun artifacts, or accepted post-layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter Physical Flow Run",
        "",
        f"- status: `{report['status']}`",
        f"- workbench: `{report['workbench']}`",
        f"- source gate status: `{report['source_gate_status']}`",
        f"- required cell count: `{report['required_cell_count']}`",
        f"- present cell count: `{report['present_cell_count']}`",
        f"- missing cell count: `{report['missing_cell_count']}`",
        f"- blocked command count: `{report['blocked_command_count']}`",
        f"- runnable command count: `{report['runnable_command_count']}`",
        "",
        "## First Principle",
        "",
        "A physical flow has to start from shapes, not from intent. If the named cells are missing, the correct result is a stopped run with a precise reason.",
        "",
        "The stopped run is still useful because it fixes the next executable boundary. Once the cells exist, the same command list becomes the extraction path that produces the files consumed by candidate preflight.",
        "",
        "## Missing Cells",
        "",
    ]
    lines.extend(f"- `{cell}`" for cell in report["missing_cells"])
    lines.extend(["", "## Blocked Extraction Commands", ""])
    if report["blocked_commands"]:
        lines.extend(
            f"- `{item['command']}` -> `{item['extract_target']}` ({item['reason']})"
            for item in report["blocked_commands"]
        )
    else:
        lines.append("- none")
    lines.extend(["", "## Runnable Extraction Commands", ""])
    if report["runnable_commands"]:
        lines.extend(f"- `{item['command']}` -> `{item['extract_target']}`" for item in report["runnable_commands"])
    else:
        lines.append("- none")
    lines.extend(["", "## Next After Extraction", ""])
    lines.extend(f"- `{command}`" for command in report["next_after_extraction"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("analog_converter_physical_flow_run")
    print(f"status,{report['status']}")
    print(f"present_cell_count,{report['present_cell_count']}")
    print(f"missing_cell_count,{report['missing_cell_count']}")
    print(f"blocked_command_count,{report['blocked_command_count']}")
    print(f"runnable_command_count,{report['runnable_command_count']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
