#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELLS = WORKBENCH / "cells"
EXTRACTED = WORKBENCH / "extracted"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-physical-artifacts.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-physical-artifacts.md"

CELL_NAMES = [
    "row_dac_10b",
    "sar_readout_12b",
    "shared_converter_mux",
    "aimc_converter_macro",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def parse_magic_bbox(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    boxes = []
    for match in re.finditer(r"^rect\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)", text, flags=re.MULTILINE):
        x1, y1, x2, y2 = (int(item) for item in match.groups())
        boxes.append((x1, y1, x2, y2))
    if not boxes:
        return {"rect_count": 0, "bbox_lambda": None, "bbox_area_lambda2": 0}
    min_x = min(box[0] for box in boxes)
    min_y = min(box[1] for box in boxes)
    max_x = max(box[2] for box in boxes)
    max_y = max(box[3] for box in boxes)
    return {
        "rect_count": len(boxes),
        "bbox_lambda": [min_x, min_y, max_x, max_y],
        "bbox_area_lambda2": max(0, max_x - min_x) * max(0, max_y - min_y),
    }


def count_spice_objects(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("*")]
    devices = [line for line in lines if line[:1].lower() in {"r", "c", "m", "x", "v", "i"}]
    return {
        "line_count": len(text.splitlines()) if path.is_file() else 0,
        "device_like_line_count": len(devices),
        "has_subckt": any(line.lower().startswith(".subckt") for line in lines),
        "has_end": any(line.lower().startswith(".end") for line in lines),
    }


def build_report() -> dict[str, Any]:
    records = []
    for name in CELL_NAMES:
        mag = CELLS / f"{name}.mag"
        ext = CELLS / f"{name}.ext"
        spice = EXTRACTED / f"{name}_layout_smoke.spice"
        layout = parse_magic_bbox(mag)
        spice_stats = count_spice_objects(spice)
        records.append(
            {
                "name": name,
                "magic_cell": rel(mag),
                "magic_cell_present": mag.is_file() and mag.stat().st_size > 0,
                "ext_file": rel(ext),
                "ext_file_present": ext.is_file() and ext.stat().st_size > 0,
                "extracted_spice": rel(spice),
                "extracted_spice_present": spice.is_file() and spice.stat().st_size > 0,
                **layout,
                **spice_stats,
            }
        )
    all_present = all(
        item["magic_cell_present"] and item["ext_file_present"] and item["extracted_spice_present"]
        for item in records
    )
    macro = next(item for item in records if item["name"] == "aimc_converter_macro")
    return {
        "result_type": "converter_starter_physical_artifacts",
        "status": "starter_physical_artifacts_present_not_accepted_evidence" if all_present else "starter_physical_artifacts_incomplete",
        "workbench": rel(WORKBENCH),
        "cell_count": len(records),
        "complete_cell_count": sum(
            1 for item in records if item["magic_cell_present"] and item["ext_file_present"] and item["extracted_spice_present"]
        ),
        "macro_bbox_area_lambda2": macro["bbox_area_lambda2"],
        "records": records,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "records inspectable starter Magic cells, ext files, extracted SPICE files, and layout-box area from the local workbench",
            "not_allowed": "does not measure converter energy, latency, noise, calibrated bit accuracy, DRC/LVS signoff, or accepted post-layout replacement economics",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Physical Artifacts",
        "",
        f"- status: `{report['status']}`",
        f"- workbench: `{report['workbench']}`",
        f"- cell count: `{report['cell_count']}`",
        f"- complete cell count: `{report['complete_cell_count']}`",
        f"- macro bbox area lambda2: `{report['macro_bbox_area_lambda2']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A layout artifact is stronger than a paragraph because it has shapes, extracted records, and a netlist that another tool can inspect. But it is still weaker than converter evidence if it does not measure the circuit quantities that the system decision depends on.",
        "",
        "The starter cells prove the physical path is alive. They do not prove that the row driver has the requested analog accuracy, that the readout has the requested noise, or that the shared converter cost makes analog replacement worthwhile.",
        "",
        "## Cells",
        "",
    ]
    for item in report["records"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- magic cell: `{item['magic_cell']}` present `{item['magic_cell_present']}`",
                f"- ext file: `{item['ext_file']}` present `{item['ext_file_present']}`",
                f"- extracted spice: `{item['extracted_spice']}` present `{item['extracted_spice_present']}`",
                f"- rect count: `{item['rect_count']}`",
                f"- bbox lambda: `{item['bbox_lambda']}`",
                f"- bbox area lambda2: `{item['bbox_area_lambda2']}`",
                f"- device-like SPICE lines: `{item['device_like_line_count']}`",
                f"- has subckt: `{item['has_subckt']}`",
                "",
            ]
        )
    lines.extend(["## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_physical_artifacts")
    print(f"status,{report['status']}")
    print(f"cell_count,{report['cell_count']}")
    print(f"complete_cell_count,{report['complete_cell_count']}")
    print(f"macro_bbox_area_lambda2,{report['macro_bbox_area_lambda2']}")
    print(f"candidate_post_layout_written,{report['candidate_post_layout_written']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0 if report["status"] == "starter_physical_artifacts_present_not_accepted_evidence" else 1


if __name__ == "__main__":
    raise SystemExit(main())
