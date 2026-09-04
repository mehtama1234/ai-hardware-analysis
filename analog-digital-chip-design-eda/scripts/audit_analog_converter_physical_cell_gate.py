#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-physical-cell-gate.md"

REQUIRED_CELLS = [
    {
        "name": "row_dac_10b",
        "purpose": "turns activation bits into the row voltage driven onto the analog array",
        "required_any": ["row_dac_10b.mag", "row_dac_10b.gds", "row_dac_10b.sch"],
    },
    {
        "name": "sar_readout_12b",
        "purpose": "turns the sensed analog column value back into a bounded digital number",
        "required_any": ["sar_readout_12b.mag", "sar_readout_12b.gds", "sar_readout_12b.sch"],
    },
    {
        "name": "shared_converter_mux",
        "purpose": "connects many rows or columns to a smaller converter bank without hiding load",
        "required_any": ["shared_converter_mux.mag", "shared_converter_mux.gds", "shared_converter_mux.sch"],
    },
    {
        "name": "aimc_converter_macro",
        "purpose": "packages the DAC, readout, mux, supplies, and pins as the converter boundary used by the model",
        "required_any": ["aimc_converter_macro.mag", "aimc_converter_macro.gds", "aimc_converter_macro.lef"],
    },
]

EXTRACTED_ARTIFACTS = [
    "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp",
    "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp",
    "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp",
    "evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json",
    "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/converter-post-layout-break-even-rerun.json",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def find_cell_file(filename: str) -> Path | None:
    if not WORKBENCH.exists():
        return None
    for path in WORKBENCH.rglob(filename):
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def build_report() -> dict[str, Any]:
    cell_records = []
    for cell in REQUIRED_CELLS:
        matches = []
        for filename in cell["required_any"]:
            path = find_cell_file(filename)
            if path:
                matches.append({"path": rel(path), "bytes": path.stat().st_size})
        cell_records.append(
            {
                "name": cell["name"],
                "purpose": cell["purpose"],
                "required_any": cell["required_any"],
                "present": bool(matches),
                "matches": matches,
            }
        )

    extracted_records = []
    for item in EXTRACTED_ARTIFACTS:
        path = ROOT / item
        extracted_records.append({"path": item, "present": path.is_file() and path.stat().st_size > 0, "bytes": path.stat().st_size if path.is_file() else 0})

    present_cells = sum(1 for item in cell_records if item["present"])
    present_extracted = sum(1 for item in extracted_records if item["present"])
    all_cells_present = present_cells == len(REQUIRED_CELLS)
    all_extracted_present = present_extracted == len(EXTRACTED_ARTIFACTS)
    if all_cells_present and not all_extracted_present:
        status = "physical_cells_present_waiting_for_extracted_artifacts"
    elif all_cells_present and all_extracted_present:
        status = "physical_cell_gate_ready_for_candidate_post_layout_payload"
    else:
        status = "physical_cell_gate_waiting_for_real_converter_cells"

    return {
        "result_type": "analog_converter_physical_cell_gate",
        "status": status,
        "workbench": rel(WORKBENCH),
        "required_cell_count": len(REQUIRED_CELLS),
        "present_cell_count": present_cells,
        "missing_cell_count": len(REQUIRED_CELLS) - present_cells,
        "required_cells": cell_records,
        "required_extracted_artifact_count": len(EXTRACTED_ARTIFACTS),
        "present_extracted_artifact_count": present_extracted,
        "missing_extracted_artifact_count": len(EXTRACTED_ARTIFACTS) - present_extracted,
        "required_extracted_artifacts": extracted_records,
        "all_required_cells_present": all_cells_present,
        "all_required_extracted_artifacts_present": all_extracted_present,
        "ready_for_candidate_post_layout_payload": all_cells_present and all_extracted_present,
        "claim_boundary": {
            "allowed": "checks whether named converter layout cells and extracted follow-on artifacts exist",
            "not_allowed": "does not count environment files, skeleton scripts, or temporary positive-path fixtures as converter layout evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter Physical Cell Gate",
        "",
        f"- status: `{report['status']}`",
        f"- workbench: `{report['workbench']}`",
        f"- required cell count: `{report['required_cell_count']}`",
        f"- present cell count: `{report['present_cell_count']}`",
        f"- missing cell count: `{report['missing_cell_count']}`",
        f"- present extracted artifact count: `{report['present_extracted_artifact_count']}`",
        f"- ready for candidate post-layout payload: `{report['ready_for_candidate_post_layout_payload']}`",
        "",
        "## First Principle",
        "",
        "A converter is not proven by having the right tools. It is proven when there are named physical cells that the layout tool can read, and when those cells produce extracted files that the simulator can use.",
        "",
        "The named cells matter because each one controls a different error source. The DAC sets the input voltage, the readout turns the result back into bits, the mux adds shared loading, and the macro fixes the pins and area that the system model must pay for.",
        "",
        "## Required Physical Cells",
        "",
    ]
    for cell in report["required_cells"]:
        lines.extend(
            [
                f"### {cell['name']}",
                "",
                f"- purpose: {cell['purpose']}",
                f"- present: `{cell['present']}`",
                f"- accepted source names: `{', '.join(cell['required_any'])}`",
            ]
        )
        if cell["matches"]:
            lines.extend(f"- match: `{match['path']}` ({match['bytes']} bytes)" for match in cell["matches"])
        lines.append("")
    lines.extend(["## Required Extracted Artifacts", ""])
    lines.extend(f"- `{item['path']}` present `{item['present']}` bytes `{item['bytes']}`" for item in report["required_extracted_artifacts"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("analog_converter_physical_cell_gate")
    print(f"status,{report['status']}")
    print(f"present_cell_count,{report['present_cell_count']}")
    print(f"missing_cell_count,{report['missing_cell_count']}")
    print(f"present_extracted_artifact_count,{report['present_extracted_artifact_count']}")
    print(f"ready_for_candidate_post_layout_payload,{report['ready_for_candidate_post_layout_payload']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
