#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PDK_ROOT = Path.home() / "eda-tools" / "pdks"
PDK = PDK_ROOT / "sky130A"
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-pdk-readiness.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "analog-converter-pdk-readiness.md"

REQUIRED_FILES = {
    "magic_tech": PDK / "libs.tech" / "magic" / "sky130A.tech",
    "magic_rc": PDK / "libs.tech" / "magic" / "sky130A.magicrc",
    "xschem_rc": PDK / "libs.tech" / "xschem" / "xschemrc",
    "ngspice_model_library": PDK / "libs.tech" / "ngspice" / "sky130.lib.spice",
    "ngspice_tt_corner": PDK / "libs.tech" / "ngspice" / "corners" / "tt.spice",
}


def rel_or_abs(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def file_record(name: str, path: Path) -> dict[str, Any]:
    return {
        "name": name,
        "path": rel_or_abs(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else 0,
    }


def build_report() -> dict[str, Any]:
    records = [file_record(name, path) for name, path in REQUIRED_FILES.items()]
    all_present = all(item["exists"] and item["bytes"] > 0 for item in records)
    missing_workbench_layout = not any(
        path.is_file() and path.stat().st_size > 0
        for pattern in ("*.sch", "*.mag", "*.gds", "*.lef", "*.dspf", "*.spef")
        for path in WORKBENCH.rglob(pattern)
    ) if WORKBENCH.exists() else True
    if all_present and not missing_workbench_layout:
        status = "sky130_pdk_ready_first_converter_starter_cell_present"
    elif all_present:
        status = "sky130_pdk_ready_waiting_for_converter_physical_cells"
    else:
        status = "pdk_readiness_needs_review"
    return {
        "result_type": "analog_converter_pdk_readiness",
        "status": status,
        "pdk_root": str(PDK_ROOT),
        "pdk": "sky130A",
        "required_files": records,
        "all_required_pdk_files_present": all_present,
        "selected_process_corner": "tt",
        "selected_voltage_v": 1.8,
        "selected_temperature_c": 25,
        "workbench": rel_or_abs(WORKBENCH),
        "workbench_has_converter_physical_cells": not missing_workbench_layout,
        "candidate_payload_use": {
            "simulation.model_files": [rel_or_abs(REQUIRED_FILES["ngspice_model_library"]), rel_or_abs(REQUIRED_FILES["ngspice_tt_corner"])],
            "simulation.process_corner": "sky130A_tt_1p8V_25C",
            "simulation.voltage_v": 1.8,
            "simulation.temperature_c": 25,
            "extraction.parasitic_format": "extracted-spice",
        },
        "next_real_actions": [
            "create or import sky130A physical cells for row_dac_10b, sar_readout_12b, shared_converter_mux, and aimc_converter_macro",
            "run Magic DRC using the sky130A tech file",
            "run extraction against the named macro",
            "run ngspice with sky130.lib.spice and the tt corner",
            "copy the extracted netlist, model files, and same-run rerun into the candidate payload workspace",
        ],
        "claim_boundary": {
            "allowed": "proves the local Sky130 PDK files needed by the analog layout path are present and named",
            "not_allowed": "does not prove converter layout, DRC, LVS, extraction, post-layout simulation, measured silicon, or accepted evidence",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Analog Converter PDK Readiness",
        "",
        f"- status: `{report['status']}`",
        f"- PDK root: `{report['pdk_root']}`",
        f"- PDK: `{report['pdk']}`",
        f"- all required PDK files present: `{report['all_required_pdk_files_present']}`",
        f"- selected process corner: `{report['selected_process_corner']}`",
        f"- selected voltage V: `{report['selected_voltage_v']}`",
        f"- selected temperature C: `{report['selected_temperature_c']}`",
        f"- workbench has converter physical cells: `{report['workbench_has_converter_physical_cells']}`",
        "",
        "## First Principle",
        "",
        "A process file gives meaning to drawn shapes. Without it, a rectangle is only a drawing. With it, the tools can interpret layers, design rules, parasitic extraction, device models, and simulation corners. This audit proves that the local Sky130 process support is present, while also saying that the converter cells themselves still have to be drawn or imported.",
        "",
        "## Required PDK Files",
        "",
    ]
    lines.extend(f"- {item['name']}: `{item['path']}` exists `{item['exists']}` bytes `{item['bytes']}`" for item in report["required_files"])
    lines.extend([
        "",
        "## Candidate Payload Mapping",
        "",
        f"- simulation.model_files: `{', '.join(report['candidate_payload_use']['simulation.model_files'])}`",
        f"- simulation.process_corner: `{report['candidate_payload_use']['simulation.process_corner']}`",
        f"- simulation.voltage_v: `{report['candidate_payload_use']['simulation.voltage_v']}`",
        f"- simulation.temperature_c: `{report['candidate_payload_use']['simulation.temperature_c']}`",
        f"- extraction.parasitic_format: `{report['candidate_payload_use']['extraction.parasitic_format']}`",
        "",
        "## Next Real Actions",
        "",
    ])
    lines.extend(f"- {item}" for item in report["next_real_actions"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("analog_converter_pdk_readiness")
    print(f"status,{report['status']}")
    print(f"pdk_root,{report['pdk_root']}")
    print(f"all_required_pdk_files_present,{report['all_required_pdk_files_present']}")
    print(f"workbench_has_converter_physical_cells,{report['workbench_has_converter_physical_cells']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
