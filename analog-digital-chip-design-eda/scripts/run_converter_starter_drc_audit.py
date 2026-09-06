#!/usr/bin/env python3
"""Run Magic DRC on the named starter cells without promoting them."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELL_DIR = WORKBENCH / "cells"
RUN_DIR = WORKBENCH / "extracted"
MAGIC_RC = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
CELLS = ("row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro")
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-drc-audit.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-drc-audit.md"


def run_cell(name: str) -> dict[str, object]:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    tcl = RUN_DIR / f"drc-{name}-audit.tcl"
    tcl.write_text(
        "\n".join(
            [
                f"path search +{CELL_DIR}",
                f"load {name} -force",
                "select top cell",
                "drc on",
                "drc catchup",
                "drc statistics",
                "drc count",
                "quit -noprompt",
                "",
            ]
        ),
        encoding="utf-8",
    )
    command = [str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC), str(tcl)]
    proc = subprocess.run(command, cwd=RUN_DIR, text=True, capture_output=True, check=False, env={**os.environ, "PDK_ROOT": str(Path.home() / "eda-tools" / "pdks")})
    output = proc.stdout + proc.stderr
    counts = [int(value) for value in re.findall(r"Total DRC errors found:\s*(\d+)", output, flags=re.IGNORECASE)]
    counts += [int(value) for value in re.findall(r"\b(\d+)\s+(?:error|errors)\b", output, flags=re.IGNORECASE)]
    drc_count = counts[-1] if counts else None
    return {
        "cell": name,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "drc_error_count": drc_count,
        "drc_count_parsed": drc_count is not None,
        "drc_clean": drc_count == 0 if drc_count is not None else False,
        "stdout_tail": output[-3000:],
    }


def main() -> int:
    rows = [run_cell(cell) for cell in CELLS]
    report = {
        "result_type": "converter_starter_drc_audit",
        "status": "starter_drc_audit_complete_not_converter_signoff" if all(row["returncode"] == 0 for row in rows) else "starter_drc_audit_incomplete",
        "cells": rows,
        "cell_count": len(rows),
        "drc_clean_count": sum(bool(row["drc_clean"]) for row in rows),
        "all_drc_clean": all(bool(row["drc_clean"]) for row in rows),
        "claim_boundary": {
            "allowed": "runs the installed Sky130 Magic DRC command on the four named starter layout cells and records the returned error count",
            "not_allowed": "does not prove a real DAC/ADC layout, LVS, extracted converter behavior, matching, parasitic accuracy, area, or accepted post-layout evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Starter DRC Audit", "",
        f"- status: `{report['status']}`",
        f"- cells: `{report['cell_count']}`",
        f"- DRC-clean cells: `{report['drc_clean_count']}`",
        f"- all DRC clean: `{report['all_drc_clean']}`", "",
        "| cell | return code | DRC errors | clean |", "| --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['cell']}` | `{row['returncode']}` | `{row['drc_error_count']}` | `{row['drc_clean']}` |")
    lines += ["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"drc_clean,{report['drc_clean_count']}/{report['cell_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
