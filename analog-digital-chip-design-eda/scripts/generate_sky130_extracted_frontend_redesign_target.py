#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-extracted-frontend-redesign-target.json"
OUT_MD = EVIDENCE / "sky130-extracted-frontend-redesign-target.md"
STRENGTH = EVIDENCE / "sky130-capacitive-isolation-extracted-coupling-strength-sweep.json"
PORT_MAPPING = EVIDENCE / "sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json"
PHYSICAL_GAP = EVIDENCE / "sky130-capacitive-isolation-physical-cell-gap.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Extracted Frontend Redesign Target",
        "",
        f"- status: `{report['status']}`",
        f"- measured wrong-sign bias mV: `{report['measured_wrong_sign_bias_mv']:.6f}`",
        f"- target differential signal mV: `{report['target_differential_signal_mv']:.6f}`",
        f"- bias-to-signal ratio: `{report['bias_to_signal_ratio']:.2f}`",
        f"- required bias reduction factor: `{report['required_bias_reduction_factor']:.2f}`",
        f"- accepted ready now: `{report['accepted_ready_now']}`",
        "",
        "## First Principle",
        "",
        "A comparator is only useful after its input nodes carry the thing we want to compare. The latch input must first be a balanced measuring node, then it can become a decision node. If the layout moves both latch inputs in one preferred direction, the latch is no longer measuring the sampled voltage difference. It is mostly reading the layout's own imbalance.",
        "",
        "The extracted frontend failed in that exact way. The negative input case should make `gp - gn` negative, but the extracted cell made it positive by about 11 mV. The actual target signal is only about 0.153 mV. That means the unwanted physical bias is roughly 72 times larger than the signal we are trying to preserve.",
        "",
        "Adding more ideal sample-to-gate capacitance did not fix both signs. That tells us the next move is not a small sizing patch. The front end needs a different physical handoff: balanced latch-gate loading, controlled common-mode reset, symmetric shielding, and a separated sampling phase before regeneration.",
        "",
        "## Concrete Redesign Target",
        "",
        "| target | value | reason |",
        "|---|---:|---|",
        f"| maximum wrong-sign gate bias before latch fire | `{report['max_allowed_wrong_sign_bias_mv']:.6f} mV` | leaves half of the target signal as usable sign margin |",
        f"| required reduction from current extracted bias | `{report['required_bias_reduction_factor']:.2f}x` | current wrong-sign bias is much larger than the target differential signal |",
        f"| minimum sign cases | `{report['minimum_sign_cases']}` | both positive and negative target-edge inputs must preserve sign |",
        f"| accepted extracted evidence | `{report['accepted_evidence_required']}` | the same physical cell must pass extraction, rerun, DRC/LVS, and offset/noise record |",
        "",
        "## Required Topology Changes",
        "",
    ]
    for item in report["required_topology_changes"]:
        lines.append(f"- {item}")
    lines.extend([
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    strength = load(STRENGTH)
    port_mapping = load(PORT_MAPPING)
    physical_gap = load(PHYSICAL_GAP)
    target_mv = abs(float(strength["rows"][0]["input_diff_mv"]))
    wrong_sign_rows = [row for row in port_mapping["rows"] if row["mapping"] == "normal" and row["expected_sign"] == -1]
    wrong_sign_bias_mv = abs(float(wrong_sign_rows[0]["gate_diff_after_v"])) * 1000.0
    max_allowed_wrong_sign_bias_mv = target_mv / 2.0
    required_reduction = wrong_sign_bias_mv / max_allowed_wrong_sign_bias_mv
    report = {
        "result_type": "sky130_extracted_frontend_redesign_target",
        "status": "redesign_required_before_post_layout_acceptance",
        "source_coupling_strength_sweep": "evidence/aimc-simulator-adapters/sky130-capacitive-isolation-extracted-coupling-strength-sweep.json",
        "source_port_mapping_diagnostic": "evidence/aimc-simulator-adapters/sky130-capacitive-isolation-extracted-port-mapping-diagnostic.json",
        "source_physical_cell_gap": "evidence/aimc-simulator-adapters/sky130-capacitive-isolation-physical-cell-gap.json",
        "target_differential_signal_mv": target_mv,
        "measured_wrong_sign_bias_mv": wrong_sign_bias_mv,
        "bias_to_signal_ratio": wrong_sign_bias_mv / target_mv,
        "max_allowed_wrong_sign_bias_mv": max_allowed_wrong_sign_bias_mv,
        "required_bias_reduction_factor": required_reduction,
        "minimum_sign_cases": 2,
        "accepted_evidence_required": "same extracted physical cell passes both-polarity sign preservation, kickback, offset/noise, DRC, and LVS",
        "physical_gap_missing_objects": physical_gap.get("missing_objects", []),
        "required_topology_changes": [
            "make each latch-gate input see the same total capacitance to clock, supply, ground, substrate, and sample nodes",
            "add a reset or precharge phase that forces both latch-gate inputs to the same common-mode before the sampled signal is handed off",
            "shield or distance the latch-gate nodes so clock and supply movement cannot create a one-direction gate difference larger than the sampled signal",
            "separate the sampling phase from the regenerative latch phase so the latch cannot push charge back into the held sample while the sign is being formed",
            "rerun the extracted physical cell after layout, not an ideal overlay, before any accepted evidence is written",
        ],
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns the failed extracted-RC diagnostics into a measurable redesign target for the next physical frontend",
            "not_allowed": "does not claim a working comparator, does not modify layout, does not replace DRC/LVS, and does not prove accepted post-layout converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_extracted_frontend_redesign_target")
    print(f"status,{report['status']}")
    print(f"measured_wrong_sign_bias_mv,{report['measured_wrong_sign_bias_mv']:.6f}")
    print(f"target_differential_signal_mv,{report['target_differential_signal_mv']:.6f}")
    print(f"required_bias_reduction_factor,{report['required_bias_reduction_factor']:.2f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
