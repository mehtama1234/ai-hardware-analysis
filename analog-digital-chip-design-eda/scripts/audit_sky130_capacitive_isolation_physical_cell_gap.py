#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "layout-workbench"
CANDIDATE = ROOT / "evidence" / "aimc-simulator-adapters" / "candidate-post-layout"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
HANDOFF = EVIDENCE / "sky130-capacitive-isolation-post-layout-handoff.json"
OUT_JSON = EVIDENCE / "sky130-capacitive-isolation-physical-cell-gap.json"
OUT_MD = EVIDENCE / "sky130-capacitive-isolation-physical-cell-gap.md"


REQUIRED_OBJECTS = [
    {
        "name": "layout_cell",
        "accepted_paths": [
            "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.mag",
            "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.gds",
            "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.sch",
        ],
        "why": "the isolation capacitor and latch/sample connection must become a physical or schematic cell with a stable name",
    },
    {
        "name": "extracted_frontend_netlist",
        "accepted_paths": [
            "evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sky130_capacitive_isolation_frontend_extracted.sp",
            "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_capacitive_isolation_frontend_extracted.spice",
        ],
        "why": "post-layout proof must simulate the extracted circuit object, not the earlier generated schematic deck",
    },
    {
        "name": "model_or_corner_file",
        "accepted_paths": [
            "evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes",
            "evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-ngspice.includes",
        ],
        "why": "the rerun must say which process model and corner equations produced the numbers",
    },
    {
        "name": "post_layout_both_polarity_rerun",
        "accepted_paths": [
            "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json",
        ],
        "why": "the schematic both-polarity pass must be repeated after extraction because parasitics change the sampled nodes",
    },
    {
        "name": "offset_noise_record",
        "accepted_paths": [
            "evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-offset-noise.json",
        ],
        "why": "kickback alone does not prove comparator input-referred offset or noise",
    },
    {
        "name": "drc_lvs_record",
        "accepted_paths": [
            "evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-drc-lvs.json",
        ],
        "why": "a physical-cell claim needs a check that the drawn object matches the intended circuit and process rules",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def path_record(relpath: str) -> dict[str, Any]:
    path = ROOT / relpath
    present = path.is_file() and path.stat().st_size > 0
    return {"path": relpath, "present": present, "bytes": path.stat().st_size if path.is_file() else 0}


def main() -> None:
    handoff = load_json(HANDOFF)
    records = []
    for item in REQUIRED_OBJECTS:
        paths = [path_record(path) for path in item["accepted_paths"]]
        present = any(path["present"] for path in paths)
        records.append({"name": item["name"], "present": present, "why": item["why"], "accepted_paths": paths})

    present_count = sum(1 for item in records if item["present"])
    missing_count = len(records) - present_count
    all_present = missing_count == 0
    schematic = handoff.get("schematic_confirmation") if isinstance(handoff.get("schematic_confirmation"), dict) else {}
    payload = {
        "result_type": "sky130_capacitive_isolation_physical_cell_gap",
        "status": "physical_cell_gap_blocks_post_layout_candidate" if not all_present else "physical_cell_inputs_present_ready_for_extraction_rerun",
        "source_handoff": str(HANDOFF.relative_to(ROOT)),
        "workbench": str(WORKBENCH.relative_to(ROOT)),
        "candidate_workspace": str(CANDIDATE.relative_to(ROOT)),
        "schematic_confirmation": {
            "all_cases_pass": schematic.get("all_cases_pass"),
            "confirmed_coupling_caps_ff": schematic.get("confirmed_coupling_caps_ff"),
            "worst_kickback_v": schematic.get("worst_kickback_v"),
            "hard_kickback_limit_v": schematic.get("hard_kickback_limit_v"),
        },
        "required_object_count": len(records),
        "present_object_count": present_count,
        "missing_object_count": missing_count,
        "required_objects": records,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "checks whether the confirmed capacitive-isolation schematic has the physical files needed to begin post-layout candidate evidence",
            "not_allowed": "does not treat the starter layout or extracted RC netlist as accepted comparator evidence, does not run DRC/LVS, does not prove noise, and does not write accepted evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Capacitive Isolation Physical Cell Gap",
        "",
        f"- status: `{payload['status']}`",
        f"- source handoff: `{payload['source_handoff']}`",
        f"- required object count: `{payload['required_object_count']}`",
        f"- present object count: `{payload['present_object_count']}`",
        f"- missing object count: `{payload['missing_object_count']}`",
        f"- accepted ready now: `{payload['accepted_ready_now']}`",
        f"- candidate post-layout written: `{payload['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{payload['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The confirmed schematic is a behavior. A physical claim needs an object. The object is a named layout or schematic cell, an extracted netlist, a model corner, and rerun records made from that extracted netlist.",
        "",
        "This audit keeps those two things separate. It lets the schematic result move forward, but blocks accepted evidence until the physical files are present.",
        "",
        "## Required Objects",
        "",
    ]
    for item in records:
        lines.extend([f"### {item['name']}", "", f"- present: `{item['present']}`", f"- why: {item['why']}"])
        for path in item["accepted_paths"]:
            lines.append(f"- `{path['path']}` present `{path['present']}` bytes `{path['bytes']}`")
        lines.append("")
    lines.extend(["## Refused Claim", "", payload["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("sky130_capacitive_isolation_physical_cell_gap")
    print(f"status,{payload['status']}")
    print(f"present_object_count,{present_count}")
    print(f"missing_object_count,{missing_count}")
    print(f"accepted_ready_now,{payload['accepted_ready_now']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")


if __name__ == "__main__":
    main()
