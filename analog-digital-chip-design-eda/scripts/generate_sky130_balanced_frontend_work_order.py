#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
OUT_JSON = EVIDENCE / "sky130-balanced-frontend-work-order.json"
OUT_MD = EVIDENCE / "sky130-balanced-frontend-work-order.md"
REDESIGN = EVIDENCE / "sky130-extracted-frontend-redesign-target.json"
PHYSICAL_GAP = EVIDENCE / "sky130-capacitive-isolation-physical-cell-gap.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def missing_names(physical_gap: dict[str, Any]) -> list[str]:
    return [item["name"] for item in physical_gap.get("required_objects", []) if item.get("present") is not True]


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Balanced Frontend Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- target cell: `{report['target_cell_name']}`",
        f"- required wrong-sign bias reduction: `{report['required_bias_reduction_factor']:.2f}x`",
        f"- maximum wrong-sign gate bias: `{report['max_allowed_wrong_sign_bias_mv']:.6f} mV`",
        f"- missing post-layout objects: `{', '.join(report['missing_post_layout_objects'])}`",
        "",
        "## First Principle",
        "",
        "The analog frontend has one job before the latch fires: keep the sign of the sampled voltage difference. It does not need to understand the model, the token, or the layer. It only needs to make `gp - gn` carry the same sign as `sample_p - sample_n` while keeping kickback below the ADC boundary.",
        "",
        "The failed extracted cell tells us what broke. The physical metal and node loading made a preferred latch-gate direction that was much larger than the signal. So the next cell must be built as a balance problem first and a latch problem second.",
        "",
        "## Build Object",
        "",
        f"Create `{report['target_cell_name']}` beside the current starter cell. Keep the same external role, but add explicit balance and reset structure instead of relying on accidental symmetry.",
        "",
        "| port | role | rule |",
        "|---|---|---|",
    ]
    for port in report["ports"]:
        lines.append(f"| `{port['name']}` | {port['role']} | {port['rule']} |")
    lines.extend(["", "## Required Design Moves", ""])
    for item in report["required_design_moves"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Acceptance Checks", ""])
    for item in report["acceptance_checks"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Rejected Shortcuts", ""])
    for item in report["rejected_shortcuts"]:
        lines.append(f"- {item}")
    lines.extend(["", "## End-To-End Fit", "", report["end_to_end_fit"], "", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    redesign = load(REDESIGN)
    physical_gap = load(PHYSICAL_GAP)
    report = {
        "result_type": "sky130_balanced_frontend_work_order",
        "status": "ready_to_build_balanced_extracted_frontend_candidate",
        "source_redesign_target": "evidence/aimc-simulator-adapters/sky130-extracted-frontend-redesign-target.json",
        "source_physical_gap": "evidence/aimc-simulator-adapters/sky130-capacitive-isolation-physical-cell-gap.json",
        "target_cell_name": "sky130_balanced_capacitive_isolation_frontend",
        "target_layout_path": "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_balanced_capacitive_isolation_frontend.mag",
        "target_extracted_netlist_path": "labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_balanced_capacitive_isolation_frontend_extracted.spice",
        "required_bias_reduction_factor": redesign["required_bias_reduction_factor"],
        "max_allowed_wrong_sign_bias_mv": redesign["max_allowed_wrong_sign_bias_mv"],
        "target_differential_signal_mv": redesign["target_differential_signal_mv"],
        "missing_post_layout_objects": missing_names(physical_gap),
        "ports": [
            {"name": "vss", "role": "quiet reference", "rule": "route symmetrically near both latch-gate sides"},
            {"name": "vdd", "role": "supply reference", "rule": "do not let one latch-gate side see a different supply plate area"},
            {"name": "sample_p", "role": "positive held sample", "rule": "couple only to the positive measuring node before latch fire"},
            {"name": "sense_p", "role": "positive balanced measuring node", "rule": "reset to common-mode before sampling and isolate from regeneration"},
            {"name": "clk_sample", "role": "sample handoff clock", "rule": "must not share a large unbalanced plate with one sense node"},
            {"name": "vcm_reset", "role": "common-mode reset", "rule": "forces sense_p and sense_n to the same voltage before handoff"},
            {"name": "clk_latch", "role": "regeneration clock", "rule": "fires only after the sense nodes have formed the sign"},
            {"name": "sense_n", "role": "negative balanced measuring node", "rule": "match sense_p total extracted capacitance within the bias target"},
            {"name": "sample_n", "role": "negative held sample", "rule": "mirror the positive sample path in metal length, area, and neighbors"},
        ],
        "required_design_moves": [
            "split the old latch_gate_p/latch_gate_n nodes into sense_p/sense_n and later latch inputs",
            "add matched reset devices from sense_p and sense_n to vcm_reset",
            "keep sample_p-to-sense_p and sample_n-to-sense_n plates mirrored in drawn area and neighboring conductors",
            "route clk_sample and clk_latch as separate controls so sampling disturbance is not mixed with regeneration disturbance",
            "shield sense_p and sense_n with symmetric vss or vcm neighbors before either node approaches vdd or substrate plates",
            "extract the new cell and compute total sense_p and sense_n capacitance before running the latch proof",
        ],
        "acceptance_checks": [
            "extracted netlist exists for the new balanced cell name",
            "normal port mapping preserves both signs for the target positive and negative input differences",
            "absolute wrong-sign gate bias is below the redesign target before latch fire",
            "sample-node kickback remains below the hard half-LSB limit from the comparator acceptance fixture",
            "offset/noise record exists and combines with the static target by root-sum-square",
            "DRC/LVS record exists for the same cell name used in the extracted rerun",
            "accepted evidence remains false until all checks come from the same extracted physical candidate",
        ],
        "rejected_shortcuts": [
            "do not accept an ideal capacitor overlay as physical evidence",
            "do not swap ports to hide a one-direction extracted bias",
            "do not use a schematic-only pass after layout parasitics have contradicted it",
            "do not write accepted post-layout evidence while offset/noise or DRC/LVS is missing",
        ],
        "end_to_end_fit": "This work order is the next physical object in the chain from analog tile output to digital code. The model and simulator path can only trust an analog readout if this frontend first preserves the sign of the tiny sampled voltage. Once the balanced frontend passes extraction, it can feed the comparator acceptance fixture, then the converter post-layout payload, then the digital governor that decides whether an analog result is safe to use.",
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "defines the next buildable Sky130 frontend candidate and its acceptance checks",
            "not_allowed": "does not create the new layout, does not prove the comparator works, does not run DRC/LVS, and does not write accepted post-layout evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_balanced_frontend_work_order")
    print(f"status,{report['status']}")
    print(f"target_cell,{report['target_cell_name']}")
    print(f"required_bias_reduction_factor,{report['required_bias_reduction_factor']:.2f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
