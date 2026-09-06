#!/usr/bin/env python3
"""Select a continuous-SAR LSB trim from measured five-conversion runs."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
RUNNER = ROOT / "scripts" / "run_sky130_continuous_physical_sar.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-section", default="tt")
    parser.add_argument("--supply-v", type=float, default=1.8)
    parser.add_argument("--temperature-c", type=float, default=27.0)
    parser.add_argument("--scales", default="1.5,1.75,2.0")
    parser.add_argument("--output-stem", default="sky130-continuous-trim-calibration")
    args = parser.parse_args()
    scales = [float(value.strip()) for value in args.scales.split(",") if value.strip()]
    if not scales:
        raise SystemExit("--scales must contain at least one numeric trim")

    trials = []
    selected = None
    for index, scale in enumerate(scales, start=1):
        stem = f"{args.output_stem}-{args.model_section}-{args.supply_v:g}v-{args.temperature_c:g}c-lsb{scale:g}"
        env = os.environ.copy()
        env.update(
            {
                "AIMC_COUPLED_MODEL_SECTION": args.model_section,
                "AIMC_COUPLED_SUPPLY_V": str(args.supply_v),
                "AIMC_COUPLED_TEMPERATURE_C": str(args.temperature_c),
                "AIMC_COUPLED_LSB_SCALE": str(scale),
                "AIMC_CONTINUOUS_CONVERSION_COUNT": "5",
                "AIMC_CONTINUOUS_OUTPUT_STEM": stem,
            }
        )
        result = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, env=env, text=True, capture_output=True, check=False)
        artifact = EVIDENCE / f"{stem}.json"
        row = {"trial": index, "lsb_scale": scale, "artifact": str(artifact.relative_to(ROOT)), "returncode": result.returncode, "stdout_tail": (result.stdout + result.stderr)[-600:]}
        if artifact.exists():
            measured = json.loads(artifact.read_text(encoding="utf-8"))
            row.update({"status": measured.get("status"), "measured": measured.get("measured"), "all_conversions_correct": measured.get("all_conversions_correct"), "bottom_plate_in_legal_range": measured.get("bottom_plate_in_legal_range")})
            if measured.get("all_conversions_correct") is True and measured.get("bottom_plate_in_legal_range") is True and selected is None:
                selected = row
        trials.append(row)

    report = {
        "schema_version": "sky130_continuous_sar_trim_calibration.v1",
        "status": "trim_selected" if selected else "no_trim_passed",
        "corner": {"model_section": args.model_section, "supply_v": args.supply_v, "temperature_c": args.temperature_c},
        "trials": trials,
        "selected_trim": selected,
        "claim_boundary": "measured schematic-level trim selection for the named five-conversion fixture; not silicon calibration, yield, extracted-layout, board, or production evidence",
    }
    output = EVIDENCE / f"{args.output_stem}-{args.model_section}-{args.supply_v:g}v-{args.temperature_c:g}c.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"selected_lsb_scale,{selected['lsb_scale'] if selected else 'none'}")
    print(f"report,{output}")
    return 0 if selected else 1


if __name__ == "__main__":
    raise SystemExit(main())
