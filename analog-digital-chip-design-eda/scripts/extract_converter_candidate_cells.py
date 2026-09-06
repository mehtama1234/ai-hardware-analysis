#!/usr/bin/env python3
"""Extract the named Sky130 workbench cells into the non-accepted candidate area."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELLS = WORKBENCH / "cells"
OUT_DIR = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout" / "netlist"
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))

TARGETS = {
    "row_dac_10b": "row_dac_extracted.sp",
    "sar_readout_12b": "sar_readout_extracted.sp",
    "shared_converter_mux": "shared_converter_mux_extracted.sp",
    "aimc_converter_macro": "aimc_converter_macro_extracted.sp",
}


def run_cell(name: str, filename: str) -> dict[str, object]:
    output = OUT_DIR / filename
    tcl = f"""path search +{CELLS}
drc off
load {name} -force
select top cell
extract all
ext2spice lvs
ext2spice cthresh 0
ext2spice rthresh 0
ext2spice -o {output}
quit -noprompt
"""
    with tempfile.NamedTemporaryFile("w", suffix=".tcl", encoding="utf-8", delete=False) as handle:
        handle.write(tcl)
        command_file = Path(handle.name)
    try:
        proc = subprocess.run(
            [str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC), str(command_file)],
            cwd=WORKBENCH,
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PDK_ROOT": str(MAGIC_RC.parents[3])},
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        return {"cell": name, "output": str(output.relative_to(ROOT)), "returncode": None, "timed_out": True, "bytes": 0, "error": str(exc)[-1200:]}
    finally:
        command_file.unlink(missing_ok=True)
    return {
        "cell": name,
        "output": str(output.relative_to(ROOT)),
        "returncode": proc.returncode,
        "timed_out": False,
        "bytes": output.stat().st_size if output.is_file() else 0,
        "extraction_created": output.is_file() and output.stat().st_size > 0,
        "output_tail": (proc.stdout + proc.stderr)[-2500:],
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [run_cell(name, filename) for name, filename in TARGETS.items()]
    report = {
        "result_type": "converter_candidate_cell_extraction",
        "status": "candidate_cell_extraction_complete_not_converter_signoff" if all(row.get("extraction_created") for row in rows) else "candidate_cell_extraction_incomplete",
        "magic": str(MAGIC_BIN),
        "magic_rc": str(MAGIC_RC),
        "rows": rows,
        "created_count": sum(bool(row.get("extraction_created")) for row in rows),
        "cell_count": len(rows),
        "accepted_ready_now": False,
        "claim_boundary": {
            "allowed": "records Magic extraction of the four named workbench cells into the non-accepted candidate workspace",
            "not_allowed": "does not prove active converter topology, full-converter LVS, post-layout timing/noise/energy, area signoff, break-even, silicon behavior, or accepted evidence",
        },
    }
    report_path = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-candidate-cell-extraction.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"created_count,{report['created_count']}/{report['cell_count']}")
    print(f"json,{report_path}")
    return 0 if report["status"].endswith("not_converter_signoff") else 1


if __name__ == "__main__":
    raise SystemExit(main())
