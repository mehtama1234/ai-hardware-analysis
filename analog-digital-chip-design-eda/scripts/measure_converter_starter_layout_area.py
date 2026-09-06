#!/usr/bin/env python3
"""Measure the loaded Sky130 starter-cell bounding boxes with Magic."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CELL_DIR = WORKBENCH / "cells"
MAGIC_RC = Path(os.environ.get("MAGIC_RC", str(Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "magic" / "sky130A.magicrc")))
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", str(Path.home() / "eda-tools" / "magic-8.3.682" / "bin" / "magic")))
PDK_ROOT = Path(os.environ.get("PDK_ROOT", str(Path.home() / "eda-tools" / "pdks")))
CELLS = ("row_dac_10b", "sar_readout_12b", "shared_converter_mux", "aimc_converter_macro")
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-area-measurement.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "converter-starter-layout-area-measurement.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def measure_cell(name: str) -> dict[str, Any]:
    commands = "\n".join([
        f"path search +{CELL_DIR}",
        f"load {name} -force",
        "select top cell",
        "units microns",
        "puts [box values]",
        "quit -noprompt",
        "",
    ])
    proc = subprocess.run(
        [str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)],
        cwd=WORKBENCH,
        input=commands,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PDK_ROOT": str(PDK_ROOT)},
        timeout=30,
    )
    matches = re.findall(r"(?m)^(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)$", proc.stdout)
    bbox = [float(value) for value in matches[-1]] if matches else None
    width = bbox[2] - bbox[0] if bbox else None
    height = bbox[3] - bbox[1] if bbox else None
    return {
        "name": name,
        "layout": rel(CELL_DIR / f"{name}.mag"),
        "command": f"{MAGIC_BIN} -dnull -noconsole -rcfile {MAGIC_RC}",
        "returncode": proc.returncode,
        "bbox_um": bbox,
        "width_um": width,
        "height_um": height,
        "bounding_area_um2": width * height if width is not None and height is not None else None,
        "measured": proc.returncode == 0 and bbox is not None and width > 0 and height > 0,
        "stdout_tail": proc.stdout[-1200:],
        "stderr_tail": proc.stderr[-1200:],
    }


def main() -> int:
    rows = [measure_cell(name) for name in CELLS]
    report = {
        "result_type": "converter_starter_layout_area_measurement",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "starter_layout_bounding_areas_measured_not_extracted_signoff_area" if all(row["measured"] for row in rows) else "starter_layout_area_measurement_incomplete",
        "units": "um and um2",
        "cells": rows,
        "measured_cell_count": sum(row["measured"] for row in rows),
        "cell_count": len(rows),
        "source": "Magic select top cell; units microns; box values",
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "records reproducible bounding-box area for the four named starter layout cells as loaded by Magic",
            "not_allowed": "does not claim transistor converter area, density, DRC/LVS signoff area, or strict post-layout payload readiness",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Converter Starter Layout Area Measurement",
        "",
        f"- status: `{report['status']}`",
        f"- measured cells: `{report['measured_cell_count']}/{report['cell_count']}`",
        f"- source: `{report['source']}`",
        "",
        "| cell | width (um) | height (um) | bounding area (um2) | measured |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['name']}` | `{row['width_um']}` | `{row['height_um']}` | `{row['bounding_area_um2']}` | `{row['measured']}` |")
    lines.extend([
        "",
        "These are bounding-box measurements of the current starter geometries. They replace a guessed rectangle with a reproducible Magic measurement, but they are not area signoff for the missing integrated transistor converter.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"measured,{report['measured_cell_count']}/{report['cell_count']}")
    for row in rows:
        print(f"{row['name']}_area_um2,{row['bounding_area_um2']}")
    print(f"json,{OUT_JSON}")
    return 0 if report["status"].startswith("starter_layout_bounding_areas_measured") else 1


if __name__ == "__main__":
    raise SystemExit(main())
