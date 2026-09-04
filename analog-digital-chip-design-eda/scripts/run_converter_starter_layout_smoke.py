#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELL_DIR = WORKBENCH / "cells"
EXTRACT_DIR = WORKBENCH / "extracted"
PDK_MAGIC_RC = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc"
PDK_ROOT = Path.home() / "eda-tools" / "pdks"
LOCAL_MAGIC = Path.home() / "eda-tools" / "magic" / "bin" / "magic"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-smoke.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-smoke.md"

CELLS = [
    {
        "name": "row_dac_10b",
        "purpose": "starter row-drive boundary with rails, row-drive bus, and switch-column placeholders",
    },
    {
        "name": "sar_readout_12b",
        "purpose": "starter sample/readout boundary with sample input, comparator input, reference switch, and SAR bit placeholders",
    },
    {
        "name": "shared_converter_mux",
        "purpose": "starter shared loading boundary with column inputs and a mux bus",
    },
    {
        "name": "aimc_converter_macro",
        "purpose": "starter top boundary that names the DAC region, readout region, shared mux region, rails, and external pins",
    },
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def write_tcl(cell_name: str) -> Path:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    tcl = EXTRACT_DIR / f"extract-{cell_name}-starter-smoke.tcl"
    tcl.write_text(
        "\n".join(
            [
                "drc off",
                f"path search +{CELL_DIR}",
                f"load {cell_name} -force",
                "select top cell",
                "extract all",
                "ext2spice lvs",
                "ext2spice cthresh 0",
                "ext2spice rthresh 0",
                f"ext2spice -o {cell_name}_layout_smoke.spice",
                "quit -noprompt",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tcl


def run_magic(cell_name: str) -> dict[str, Any]:
    tcl = write_tcl(cell_name)
    magic_bin = Path(os.environ.get("MAGIC_BIN", str(LOCAL_MAGIC if LOCAL_MAGIC.is_file() else "magic")))
    command = [str(magic_bin), "-dnull", "-noconsole", "-rcfile", str(PDK_MAGIC_RC), str(tcl)]
    env = {**os.environ, "PDK_ROOT": str(PDK_ROOT)}
    proc = subprocess.run(command, cwd=EXTRACT_DIR, text=True, capture_output=True, check=False, env=env)
    return {
        "command": " ".join(command),
        "magic_binary": str(magic_bin),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def cell_report(cell: dict[str, str]) -> dict[str, Any]:
    name = cell["name"]
    cell_path = CELL_DIR / f"{name}.mag"
    run = run_magic(name)
    outputs = [
        CELL_DIR / f"{name}.ext",
        EXTRACT_DIR / f"{name}_layout_smoke.spice",
    ]
    output_records = [
        {"path": rel(path), "present": path.is_file() and path.stat().st_size > 0, "bytes": path.stat().st_size if path.is_file() else 0}
        for path in outputs
    ]
    passed = cell_path.is_file() and cell_path.stat().st_size > 0 and run["returncode"] == 0 and all(item["present"] for item in output_records)
    return {
        "name": name,
        "purpose": cell["purpose"],
        "cell": rel(cell_path),
        "cell_present": cell_path.is_file() and cell_path.stat().st_size > 0,
        "run": run,
        "outputs": output_records,
        "passed": passed,
    }


def build_report() -> dict[str, Any]:
    cell_reports = [cell_report(cell) for cell in CELLS]
    passed = all(item["passed"] for item in cell_reports)
    return {
        "result_type": "converter_starter_layout_smoke",
        "status": "converter_starter_layout_smoke_passed_not_candidate_evidence" if passed else "converter_starter_layout_smoke_failed",
        "cell_count": len(cell_reports),
        "passed_cell_count": sum(1 for item in cell_reports if item["passed"]),
        "cells": cell_reports,
        "passed": passed,
        "pdk_magic_rc": str(PDK_MAGIC_RC),
        "pdk_magic_rc_present": PDK_MAGIC_RC.is_file(),
        "writes_candidate_post_layout_evidence": False,
        "claim_boundary": {
            "allowed": "proves the four named starter cells exist and can be extracted by local Sky130 Magic into workbench-level files",
            "not_allowed": "does not prove production DAC/ADC/mux quality, DRC clean signoff, LVS, extracted parasitic accuracy, accepted post-layout payload, or model replacement readiness",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Converter Starter Layout Smoke",
        "",
        f"- status: `{report['status']}`",
        f"- cell count: `{report['cell_count']}`",
        f"- passed cell count: `{report['passed_cell_count']}`",
        f"- passed: `{report['passed']}`",
        f"- writes candidate post-layout evidence: `{report['writes_candidate_post_layout_evidence']}`",
        "",
        "## First Principle",
        "",
        "The next physical step is to make every named converter block concrete enough for the layout tool to read it. That is still not the same as proving the circuit. It only proves that the physical names now point to extractable shapes.",
        "",
        "Each starter cell names a boundary that later has to become a real circuit: row drive, sampled readout, shared loading, and the top macro. The smoke keeps this separate from candidate post-layout evidence.",
        "",
        "## Cells",
        "",
    ]
    for cell in report["cells"]:
        lines.extend(
            [
                f"### {cell['name']}",
                "",
                f"- purpose: {cell['purpose']}",
                f"- cell: `{cell['cell']}`",
                f"- cell present: `{cell['cell_present']}`",
                f"- passed: `{cell['passed']}`",
                f"- command: `{cell['run']['command']}`",
            ]
        )
        lines.extend(f"- output: `{item['path']}` present `{item['present']}` bytes `{item['bytes']}`" for item in cell["outputs"])
        lines.append("")
    lines.extend(["## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("converter_starter_layout_smoke")
    print(f"status,{report['status']}")
    print(f"passed,{report['passed']}")
    print(f"cell_count,{report['cell_count']}")
    print(f"passed_cell_count,{report['passed_cell_count']}")
    print(f"writes_candidate_post_layout_evidence,{report['writes_candidate_post_layout_evidence']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
