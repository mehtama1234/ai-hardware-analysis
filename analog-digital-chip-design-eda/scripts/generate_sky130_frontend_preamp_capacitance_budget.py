#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
EXTRACTED = LAB / "layout-workbench" / "extracted" / "sky130_ultra_sense_capacitive_frontend_extracted.spice"
INTERFACE_TARGET = EVIDENCE / "sky130-frontend-preamp-interface-redesign-target.json"
OUT_JSON = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
OUT_MD = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_caps() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in EXTRACTED.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*(C\d+)\s+(\S+)\s+(\S+)\s+([-+0-9.]+)f\b", line)
        if not match:
            continue
        name, node_a, node_b, value_ff = match.groups()
        rows.append({"name": name, "node_a": node_a, "node_b": node_b, "value_ff": float(value_ff)})
    return rows


def node_total(rows: list[dict[str, Any]], node: str) -> float:
    return sum(row["value_ff"] for row in rows if row["node_a"] == node or row["node_b"] == node)


def pair_total(rows: list[dict[str, Any]], left: str, right: str) -> float:
    target = tuple(sorted((left, right)))
    return sum(row["value_ff"] for row in rows if tuple(sorted((row["node_a"], row["node_b"]))) == target)


def build_report() -> dict[str, Any]:
    target = load(INTERFACE_TARGET)
    rows = parse_caps()
    sense_p_total = node_total(rows, "sense_p")
    sense_n_total = node_total(rows, "sense_n")
    useful_p = pair_total(rows, "sample_p", "sense_p")
    useful_n = pair_total(rows, "sample_n", "sense_n")
    useful_avg = (useful_p + useful_n) / 2.0
    total_avg = (sense_p_total + sense_n_total) / 2.0
    current_cap_ratio = useful_avg / total_avg if total_avg else 0.0
    required_transfer_ratio = float(target["required_sample_to_sense_transfer_ratio_at_current_gain"])
    required_total_if_useful_fixed_ff = useful_avg / required_transfer_ratio
    required_useful_if_total_fixed_ff = required_transfer_ratio * total_avg
    return {
        "result_type": "sky130_frontend_preamp_capacitance_budget",
        "status": "frontend_preamp_interface_capacitance_budget_requires_less_waste_or_more_useful_coupling",
        "source_extracted_frontend_netlist": rel(EXTRACTED),
        "source_interface_target": rel(INTERFACE_TARGET),
        "sense_p_total_cap_ff": sense_p_total,
        "sense_n_total_cap_ff": sense_n_total,
        "average_sense_total_cap_ff": total_avg,
        "sample_p_to_sense_p_cap_ff": useful_p,
        "sample_n_to_sense_n_cap_ff": useful_n,
        "average_useful_sample_to_sense_cap_ff": useful_avg,
        "current_useful_over_total_cap_ratio": current_cap_ratio,
        "measured_attached_transfer_ratio": target["current_sample_to_sense_transfer_ratio"],
        "required_transfer_ratio": required_transfer_ratio,
        "required_transfer_improvement_x": target["required_transfer_improvement_x"],
        "required_total_cap_if_useful_coupling_fixed_ff": required_total_if_useful_fixed_ff,
        "required_useful_coupling_if_total_cap_fixed_ff": required_useful_if_total_fixed_ff,
        "total_cap_reduction_needed_x_if_useful_fixed": total_avg / required_total_if_useful_fixed_ff if required_total_if_useful_fixed_ff else None,
        "useful_coupling_increase_needed_x_if_total_fixed": required_useful_if_total_fixed_ff / useful_avg if useful_avg else None,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "design_choices": [
            "reduce non-signal capacitance on sense_p and sense_n while keeping sample coupling",
            "increase intentional sample-to-sense coupling without increasing wasted capacitance at the same rate",
            "insert an isolation device whose input capacitance is much smaller than the direct preamp gate load",
            "measure the redesigned attached-preamp output before any latch or SAR claim",
        ],
        "claim_boundary": {
            "allowed": "converts extracted capacitance and measured preamp failure into a physical interface budget",
            "not_allowed": "does not edit layout, prove a new circuit, prove latch resolution, prove SAR conversion, or write accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Frontend Preamp Capacitance Budget",
        "",
        f"- status: `{report['status']}`",
        f"- average useful sample-to-sense capacitance fF: `{report['average_useful_sample_to_sense_cap_ff']:.6f}`",
        f"- average sense total capacitance fF: `{report['average_sense_total_cap_ff']:.6f}`",
        f"- current useful-over-total capacitance ratio: `{report['current_useful_over_total_cap_ratio']:.6f}`",
        f"- measured attached transfer ratio: `{report['measured_attached_transfer_ratio']:.6f}`",
        f"- required transfer ratio: `{report['required_transfer_ratio']:.6f}`",
        f"- required transfer improvement x: `{report['required_transfer_improvement_x']:.3f}`",
        f"- required total cap if useful coupling fixed fF: `{report['required_total_cap_if_useful_coupling_fixed_ff']:.6f}`",
        f"- required useful coupling if total cap fixed fF: `{report['required_useful_coupling_if_total_cap_fixed_ff']:.6f}`",
        f"- total cap reduction needed x if useful fixed: `{report['total_cap_reduction_needed_x_if_useful_fixed']:.3f}`",
        f"- useful coupling increase needed x if total fixed: `{report['useful_coupling_increase_needed_x_if_total_fixed']:.3f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The frontend stores a small voltage as charge. The preamp input reads that charge through a node that also has capacitance to supply, ground, substrate, clocked regions, and internal metal. The voltage at the preamp input is the useful sample coupling divided by everything that must be moved.",
        "",
        "That is why gain alone did not fix the attached preamp. The preamp can amplify the voltage it receives, but the extracted node is giving it only a small fraction of the sampled difference.",
        "",
        "## Physical Budget",
        "",
        f"The extracted frontend has about `{report['average_useful_sample_to_sense_cap_ff']:.3f} fF` of useful sample-to-sense coupling and about `{report['average_sense_total_cap_ff']:.3f} fF` total sense-node capacitance. To reach the required transfer without changing preamp gain, either total sense capacitance must fall toward `{report['required_total_cap_if_useful_coupling_fixed_ff']:.3f} fF`, or useful coupling must rise toward `{report['required_useful_coupling_if_total_cap_fixed_ff']:.3f} fF` without dragging equal wasted capacitance with it.",
        "",
        "## Design Choices",
        "",
    ]
    lines.extend(f"- {item}" for item in report["design_choices"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_frontend_preamp_capacitance_budget")
    print(f"status,{report['status']}")
    print(f"required_transfer_improvement_x,{report['required_transfer_improvement_x']:.3f}")
    print(f"total_cap_reduction_needed_x_if_useful_fixed,{report['total_cap_reduction_needed_x_if_useful_fixed']:.3f}")
    print(f"useful_coupling_increase_needed_x_if_total_fixed,{report['useful_coupling_increase_needed_x_if_total_fixed']:.3f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
