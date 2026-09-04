#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CAP_BUDGET = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
GAIN_SWEEP = EVIDENCE / "sky130-extracted-frontend-preamp-gain-sweep.json"
OUT_JSON = EVIDENCE / "sky130-frontend-preamp-interface-work-order.json"
OUT_MD = EVIDENCE / "sky130-frontend-preamp-interface-work-order.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    budget = load(CAP_BUDGET)
    sweep = load(GAIN_SWEEP)
    required_ratio = float(budget["required_transfer_ratio"])
    current_ratio = float(budget["measured_attached_transfer_ratio"])
    useful_ff = float(budget["average_useful_sample_to_sense_cap_ff"])
    total_ff = float(budget["average_sense_total_cap_ff"])
    target_total_ff = float(budget["required_total_cap_if_useful_coupling_fixed_ff"])
    target_useful_ff = float(budget["required_useful_coupling_if_total_cap_fixed_ff"])
    output_margin_v = float(sweep["output_margin_target_v"])
    candidates = [
        {
            "name": "lower_waste_sense_node",
            "physical_move": "keep about the same useful sample-to-sense coupling but remove non-signal capacitance from sense_p and sense_n",
            "target": f"average sense-node capacitance <= {target_total_ff:.3f} fF with useful coupling near {useful_ff:.3f} fF",
            "why": "the sampled charge would be divided over less total capacitance, so the same charge makes a larger voltage",
            "acceptance": "attached-preamp run measures both signs, preserves sign, and reaches at least 0.5 mV output difference",
        },
        {
            "name": "stronger_useful_coupling",
            "physical_move": "increase intentional sample_p-to-sense_p and sample_n-to-sense_n coupling without growing every other sense-node capacitance at the same rate",
            "target": f"useful sample-to-sense coupling >= {target_useful_ff:.3f} fF while average sense-node capacitance stays near {total_ff:.3f} fF",
            "why": "more of the sampled voltage reaches the preamp input before the preamp tries to amplify it",
            "acceptance": "frontend-only transfer reaches the required ratio, then attached-preamp output reaches margin",
        },
        {
            "name": "low_input_capacitance_isolation",
            "physical_move": "insert an isolation device or prebuffer whose input capacitance is materially smaller than the direct preamp gate load",
            "target": "attached sense voltage should be within 2x of the standalone measured-source voltage before gain is judged",
            "why": "the preamp should read the frontend without draining most of the frontend voltage into its input capacitance",
            "acceptance": "measured attached sense loss is reduced from about 10.47x to 2x or better, then preamp margin is retested",
        },
    ]
    return {
        "result_type": "sky130_frontend_preamp_interface_work_order",
        "status": "frontend_preamp_interface_work_order_ready_not_design_proof",
        "source_capacitance_budget": rel(CAP_BUDGET),
        "source_gain_sweep": rel(GAIN_SWEEP),
        "current_attached_transfer_ratio": current_ratio,
        "required_transfer_ratio": required_ratio,
        "required_transfer_improvement_x": budget["required_transfer_improvement_x"],
        "average_useful_sample_to_sense_cap_ff": useful_ff,
        "average_sense_total_cap_ff": total_ff,
        "target_average_sense_total_cap_ff_if_useful_fixed": target_total_ff,
        "target_useful_sample_to_sense_cap_ff_if_total_fixed": target_useful_ff,
        "output_margin_target_v": output_margin_v,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "next_required_script": "run_sky130_frontend_preamp_interface_candidate.py",
        "next_required_page": "docs/research/sky130-frontend-preamp-interface-candidate.md",
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "defines buildable frontend-to-preamp interface candidates and the exact measurement gate each one must pass",
            "not_allowed": "does not edit layout, run a new redesigned circuit, prove latch resolution, prove SAR conversion, or write accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Frontend Preamp Interface Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- candidate count: `{report['candidate_count']}`",
        f"- current attached transfer ratio: `{report['current_attached_transfer_ratio']:.6f}`",
        f"- required transfer ratio: `{report['required_transfer_ratio']:.6f}`",
        f"- required transfer improvement x: `{report['required_transfer_improvement_x']:.3f}`",
        f"- average useful sample-to-sense capacitance fF: `{report['average_useful_sample_to_sense_cap_ff']:.6f}`",
        f"- average sense total capacitance fF: `{report['average_sense_total_cap_ff']:.6f}`",
        f"- target total cap if useful fixed fF: `{report['target_average_sense_total_cap_ff_if_useful_fixed']:.6f}`",
        f"- target useful coupling if total fixed fF: `{report['target_useful_sample_to_sense_cap_ff_if_total_fixed']:.6f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The preamp cannot repair a voltage that was lost before the gate. The interface must first deliver enough voltage to the preamp input. After that, gain, latch timing, and SAR logic become meaningful tests.",
        "",
        "A useful next circuit change must therefore name which physical quantity it changes: less wasted capacitance, more useful coupling, or lower input capacitance between frontend and preamp.",
        "",
        "## Candidate Work",
        "",
        "| candidate | physical move | numeric target | acceptance test |",
        "|---|---|---|---|",
    ]
    for item in report["candidates"]:
        lines.append(f"| `{item['name']}` | {item['physical_move']} | {item['target']} | {item['acceptance']} |")
    lines.extend(
        [
            "",
            "## Next Artifact",
            "",
            f"- script: `{report['next_required_script']}`",
            f"- page: `{report['next_required_page']}`",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_frontend_preamp_interface_work_order")
    print(f"status,{report['status']}")
    print(f"candidate_count,{report['candidate_count']}")
    print(f"required_transfer_improvement_x,{report['required_transfer_improvement_x']:.3f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
