#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
WORKBENCH = LAB / "layout-workbench"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-starter-package.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-layout-starter-package.md"

FILES = {
    "README.md": """# Analog Converter Layout Starter Package

This folder is a starting workbench for the converter layout pass. It is not post-layout evidence.

The source SPICE decks already check converter behavior. This folder names the physical cells, extraction command shape, and measurement record shape needed before the strict post-layout payload can be filled.

## Physical Objects

- `row_dac_10b`: row-drive DAC path for the 10-bit input target.
- `sar_readout_12b`: sample path, comparator path, and SAR readout boundary for the 12-bit output target.
- `shared_converter_mux`: mux and loading path for the shared converter rule.
- `aimc_converter_macro`: top boundary that contains DAC, ADC, references, mux, and sample path.

## Rule

Do not copy these starter files into `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/` as if they were extracted. The candidate folder needs real extracted SPICE, DSPF, or SPEF plus the model/setup files and break-even rerun from the same run.
""",
    "converter-layout-plan.json": """{
  "result_type": "analog_converter_layout_starter_plan",
  "status": "starter_plan_not_extracted_evidence",
  "cells": [
    {
      "name": "row_dac_10b",
      "source_deck": "../spice/row_dac_settling_10bit.sp",
      "layout_target": "matched switch ladder, row driver load, local decoupling, and extracted row-drive settling path",
      "must_measure": ["dac_energy_per_row_drive", "settling_time_ns"]
    },
    {
      "name": "sar_readout_12b",
      "source_deck": "../spice/sar_readout_12bit.sp",
      "layout_target": "sample path, comparator input load, SAR switching load, reference path, and extracted readout path",
      "must_measure": ["adc_energy_per_conversion", "conversion_time_ns", "output_noise_rms"]
    },
    {
      "name": "shared_converter_mux",
      "source_deck": "../spice/shared_converter_loading.sp",
      "layout_target": "shared mux path that preserves the sixteen-output conversion-cost rule",
      "must_measure": ["outputs_per_conversion_cost", "mux_loading_effect"]
    },
    {
      "name": "aimc_converter_macro",
      "source_deck": "../spice/converter_supply_energy.sp",
      "layout_target": "top macro boundary for DAC, ADC, references, mux, sample path, rails, and area",
      "must_measure": ["adc_area_um2", "dac_area_um2", "supply_energy_window"]
    }
  ],
  "refused_claim": "This plan is not layout, not extracted netlist, not DRC/LVS, and not accepted post-layout evidence."
}
""",
    "magic-extract-skeleton.tcl": """# Magic extraction skeleton for the AIMC converter macro.
# Replace the placeholder cell names after real layout cells exist.

drc off
load aimc_converter_macro
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o aimc_converter_macro_extracted.sp
quit
""",
    "xschem-netlist-skeleton.sh": """#!/usr/bin/env bash
set -euo pipefail

echo "This is a skeleton. Replace aimc_converter_macro.sch after the schematic exists."
echo "Expected command shape:"
echo "xschem -q -n -s -x aimc_converter_macro.sch"
""",
    "post-layout-measurement-record.template.json": """{
  "result_type": "analog_converter_post_layout_measurement_record",
  "status": "template_not_evidence",
  "converter_id": "replace-with-real-converter-id",
  "run_id": "replace-with-shared-run-id",
  "measurement_level": "post_layout_simulation",
  "extracted_netlist": "replace-with-extracted-spice-dspf-or-spef",
  "model_files": ["replace-with-model-or-corner-file"],
  "command": "replace-with-reproducible-command",
  "process_corner": "replace-with-corner",
  "voltage_v": "replace-with-positive-number",
  "temperature_c": "replace-with-number",
  "adc_energy_per_conversion": "replace-with-positive-joules",
  "dac_energy_per_row_drive": "replace-with-positive-joules",
  "conversion_time_ns": "replace-with-positive-number",
  "settling_time_ns": "replace-with-positive-number",
  "output_noise_rms": "replace-with-number-at-or-below-0.004",
  "input_referred_noise": "replace-with-number",
  "adc_area_um2": "replace-with-positive-number",
  "dac_area_um2": "replace-with-positive-number",
  "outputs_per_conversion_cost": 16,
  "refused_claim": "This template is not evidence until every placeholder is replaced by one real extracted or measured run."
}
""",
}


def write_starter_files() -> list[dict[str, Any]]:
    WORKBENCH.mkdir(parents=True, exist_ok=True)
    written = []
    for name, text in FILES.items():
        path = WORKBENCH / name
        path.write_text(text, encoding="utf-8")
        if name.endswith(".sh"):
            path.chmod(0o755)
        written.append({"path": rel(path), "bytes": path.stat().st_size})
    return written


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def candidate_evidence_files() -> dict[str, int]:
    candidate = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
    return {
        "netlist_files": sum(1 for path in (candidate / "netlist").glob("*") if path.is_file() and path.stat().st_size > 0),
        "model_files": sum(1 for path in (candidate / "models").glob("*") if path.is_file() and path.stat().st_size > 0),
        "rerun_files": sum(1 for path in (candidate / "rerun").glob("*") if path.is_file() and path.stat().st_size > 0),
    }


def build_report() -> dict[str, Any]:
    files = write_starter_files()
    candidate_counts = candidate_evidence_files()
    return {
        "result_type": "analog_converter_layout_starter_package",
        "status": "starter_package_written_not_extracted_evidence",
        "workbench": rel(WORKBENCH),
        "starter_file_count": len(files),
        "starter_files": files,
        "physical_cells_named": ["row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro"],
        "candidate_post_layout_counts_after_write": candidate_counts,
        "strict_payload_still_waiting_for_real_files": all(value == 0 for value in candidate_counts.values()),
        "next_real_actions": [
            "draw or import the four named converter cells",
            "run DRC/LVS or record why the selected technology setup cannot support it yet",
            "extract one post-layout netlist for the converter macro",
            "run one named post-layout simulation using that extracted object",
            "rerun converter break-even with the extracted values from the same run",
            "build and preflight the strict candidate payload",
        ],
        "claim_boundary": {
            "allowed": "creates a concrete source-side layout workbench from the converter work order",
            "not_allowed": "does not create layout, does not run extraction, does not write candidate evidence files, and does not create accepted post-layout evidence",
        },
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Analog Converter Layout Starter Package",
        "",
        f"- status: `{report['status']}`",
        f"- workbench: `{report['workbench']}`",
        f"- starter file count: `{report['starter_file_count']}`",
        f"- strict payload still waiting for real files: `{report['strict_payload_still_waiting_for_real_files']}`",
        "",
        "## First Principle",
        "",
        "A converter layout is not a better paragraph about the converter. It is the physical shape that creates the capacitance, resistance, area, reference loading, mux loading, and rail current that the simulator must then see. The starter package names the cells and run files so the next work can create that physical object instead of adding more claims around it.",
        "",
        "The starter files stay in the analog lab workbench. The strict candidate folder stays empty until a real extraction or measured run exists.",
        "",
        "## Starter Files",
        "",
        *[f"- `{item['path']}` ({item['bytes']} bytes)" for item in report["starter_files"]],
        "",
        "## Physical Cells Named",
        "",
        *[f"- `{name}`" for name in report["physical_cells_named"]],
        "",
        "## Candidate Evidence Folder After Write",
        "",
        *[f"- {key}: `{value}`" for key, value in report["candidate_post_layout_counts_after_write"].items()],
        "",
        "## Next Real Actions",
        "",
        *[f"- {item}" for item in report["next_real_actions"]],
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print("analog_converter_layout_starter_package")
    print(f"status,{report['status']}")
    print(f"workbench,{report['workbench']}")
    print(f"starter_file_count,{report['starter_file_count']}")
    print(f"strict_payload_still_waiting_for_real_files,{report['strict_payload_still_waiting_for_real_files']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
