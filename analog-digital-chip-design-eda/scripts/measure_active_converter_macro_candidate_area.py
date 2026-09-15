#!/usr/bin/env python3
"""Measure an assembled active macro candidate with Magic.

The result is deliberately a candidate bounding-box measurement, not the
strict extracted converter area record.  It is useful for sizing and cost
diagnostics while the SAR/mux integration and post-layout signoff remain open.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench"
MAGIC_BIN = Path(os.environ.get("MAGIC_BIN", "/home/mehtama1/eda-tools/magic-8.3.682/bin/magic"))
MAGIC_RC = WORKBENCH / ".magicrc"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve()
    layout = candidate / "aimc_converter_macro_active_candidate.mag"
    if not layout.is_file():
        raise SystemExit(f"candidate layout not found: {layout}")
    commands = "\n".join([
        f"path search +{candidate}",
        f"load {layout.stem} -force",
        "select top cell",
        "units microns",
        "puts [box values]",
        "quit -noprompt",
        "",
    ])
    proc = subprocess.run(
        [str(MAGIC_BIN), "-dnull", "-noconsole", "-rcfile", str(MAGIC_RC)],
        cwd=candidate,
        input=commands,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
        env={**os.environ, "PDK_ROOT": "/home/mehtama1/eda-tools/pdks"},
    )
    matches = re.findall(r"(?m)^(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)$", proc.stdout)
    bbox = [float(value) for value in matches[-1]] if matches else None
    width = bbox[2] - bbox[0] if bbox else None
    height = bbox[3] - bbox[1] if bbox else None
    report = {
        "result_type": "active_converter_macro_candidate_area_measurement",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_dir": str(candidate),
        "layout": str(layout),
        "layout_sha256": __import__("hashlib").sha256(layout.read_bytes()).hexdigest(),
        "units": "um and um2",
        "bbox_um": bbox,
        "width_um": width,
        "height_um": height,
        "bounding_area_um2": width * height if width is not None and height is not None else None,
        "measured": proc.returncode == 0 and bbox is not None and width > 0 and height > 0,
        "status": "active_macro_bounding_area_measured_not_extracted_signoff_area" if proc.returncode == 0 and bbox else "active_macro_area_measurement_incomplete",
        "source": "Magic select top cell; units microns; box values",
        "strict_signoff": False,
        "claim_boundary": {
            "allowed": "reproducible bounding-box area of the assembled active macro candidate",
            "not_allowed": "does not prove extracted transistor converter area, full-converter LVS, post-layout energy, or strict gate readiness",
        },
        "stdout_tail": proc.stdout[-1200:],
        "stderr_tail": proc.stderr[-1200:],
    }
    path = candidate / "active-converter-macro-area-measurement.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "bounding_area_um2": report["bounding_area_um2"], "output": str(path)}, indent=2))
    return 0 if report["measured"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
