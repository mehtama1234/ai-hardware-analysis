#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import run_sky130_strong_sense_frontend_candidate as strong


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
MEASUREMENTS = LAB / "measurements"

strong.CELL = LAB / "layout-workbench" / "cells" / "sky130_ultra_sense_capacitive_frontend.mag"
strong.EXT = LAB / "layout-workbench" / "cells" / "sky130_ultra_sense_capacitive_frontend.ext"
strong.EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
strong.TCL = LAB / "layout-workbench" / "extracted" / "extract-sky130_ultra_sense_capacitive_frontend-smoke.tcl"
strong.OUT_JSON = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
strong.OUT_MD = EVIDENCE / "sky130-ultra-sense-frontend-candidate.md"
strong.OUT_CSV = MEASUREMENTS / "sky130-ultra-sense-frontend-candidate.csv"
strong.DECK_OUT = LAB / "spice" / "sky130_ultra_sense_frontend_candidate.sp"


def main() -> int:
    rc = strong.main()
    path = strong.OUT_JSON
    data = json.loads(path.read_text(encoding="utf-8"))
    transfer = data["minimum_sample_to_sense_transfer_ratio"]
    target = data["target_sample_to_sense_transfer_ratio"]
    data["result_type"] = "sky130_ultra_sense_frontend_candidate"
    data["status"] = "ultra_sense_candidate_transfer_still_below_latch_target" if transfer < target else "ultra_sense_candidate_reaches_latch_transfer_target_not_accepted"
    data["candidate_name"] = "sky130_ultra_sense_capacitive_frontend"
    data["source_strong_sense_candidate"] = "evidence/aimc-simulator-adapters/sky130-strong-sense-frontend-candidate.json"
    data["next_gate"] = (
        "This ultra candidate gets closer, but transfer is still below the latch target. The next physical move should reduce wasted sense capacitance or add a measured preamp/buffer."
        if transfer < target
        else "The transfer target is reached, but accepted comparator evidence still requires latch resolution, kickback, offset/noise, DRC, and LVS for the same physical candidate."
    )
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    strong.write_md(data)
    md = strong.OUT_MD.read_text(encoding="utf-8")
    md = md.replace("# Sky130 Strong Sense Frontend Candidate", "# Sky130 Ultra Sense Frontend Candidate")
    md = md.replace("Strong Sense Frontend Candidate", "Ultra Sense Frontend Candidate")
    md = md.replace("stronger sample-to-sense", "ultra sample-to-sense")
    md = md.replace("closer-spaced sample-to-sense", "ultra-spaced sample-to-sense")
    strong.OUT_MD.write_text(md, encoding="utf-8")
    print("sky130_ultra_sense_frontend_candidate")
    print(f"status,{data['status']}")
    print(f"direct_coupling_improvement_x,{data['direct_coupling_improvement_x']:.2f}")
    print(f"minimum_sample_to_sense_transfer_ratio,{transfer:.6f}")
    print(f"remaining_transfer_improvement_x,{data['remaining_transfer_improvement_x']}")
    print(f"json,{path}")
    print(f"markdown,{strong.OUT_MD}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
