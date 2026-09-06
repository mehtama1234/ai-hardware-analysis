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
CELL = CELL_DIR / "row_dac_10b.mag"
PDK_MAGIC_RC = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc"
PDK_ROOT = Path.home() / "eda-tools" / "pdks"
LOCAL_MAGIC = Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-10b-layout-smoke.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "row-dac-10b-layout-smoke.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def write_tcl() -> Path:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    tcl = EXTRACT_DIR / "extract-row-dac-10b-smoke.tcl"
    tcl.write_text(
        "\n".join(
            [
                "drc off",
                f"path search +{CELL_DIR}",
                "load row_dac_10b -force",
                "select top cell",
                "extract all",
                "ext2spice lvs",
                "ext2spice cthresh 0",
                "ext2spice rthresh 0",
                "ext2spice -o row_dac_10b_layout_smoke.spice",
                "quit -noprompt",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tcl


def run_magic(tcl: Path) -> dict[str, Any]:
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


def build_report() -> dict[str, Any]:
    tcl = write_tcl()
    run = run_magic(tcl)
    outputs = [
        CELL_DIR / "row_dac_10b.ext",
        EXTRACT_DIR / "row_dac_10b_layout_smoke.spice",
    ]
    output_records = [
        {"path": rel(path), "present": path.is_file() and path.stat().st_size > 0, "bytes": path.stat().st_size if path.is_file() else 0}
        for path in outputs
    ]
    passed = run["returncode"] == 0 and all(item["present"] for item in output_records)
    return {
        "result_type": "row_dac_10b_layout_smoke",
        "status": "row_dac_10b_layout_smoke_passed_not_candidate_evidence" if passed else "row_dac_10b_layout_smoke_failed",
        "cell": rel(CELL),
        "cell_present": CELL.is_file() and CELL.stat().st_size > 0,
        "pdk_magic_rc": str(PDK_MAGIC_RC),
        "pdk_magic_rc_present": PDK_MAGIC_RC.is_file(),
        "run": run,
        "outputs": output_records,
        "passed": passed,
        "writes_candidate_post_layout_evidence": False,
        "claim_boundary": {
            "allowed": "proves the named row_dac_10b Magic starter cell can be read and extracted by the local Sky130 Magic path",
            "not_allowed": "does not prove a production 10-bit DAC, matching, monotonicity, DRC clean signoff, LVS, area, accepted post-layout payload, or model replacement readiness",
        },
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Row DAC 10b Layout Smoke",
        "",
        f"- status: `{report['status']}`",
        f"- cell: `{report['cell']}`",
        f"- cell present: `{report['cell_present']}`",
        f"- passed: `{report['passed']}`",
        f"- writes candidate post-layout evidence: `{report['writes_candidate_post_layout_evidence']}`",
        "",
        "## First Principle",
        "",
        "The first physical step is not to claim converter quality. It is to make a named cell that the layout tool can read and turn into an extracted circuit file.",
        "",
        "This cell is a starter row-drive boundary with rails, a row-drive node, and switch-column placeholders. It proves the extraction path for one named block, not the electrical correctness of a full 10-bit DAC.",
        "",
        "## Command",
        "",
        f"`{report['run']['command']}`",
        "",
        "## Outputs",
        "",
    ]
    lines.extend(f"- `{item['path']}` present `{item['present']}` bytes `{item['bytes']}`" for item in report["outputs"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("row_dac_10b_layout_smoke")
    print(f"status,{report['status']}")
    print(f"passed,{report['passed']}")
    print(f"cell_present,{report['cell_present']}")
    print(f"writes_candidate_post_layout_evidence,{report['writes_candidate_post_layout_evidence']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
