#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
CAP_BUDGET = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
GAIN_SWEEP = EVIDENCE / "sky130-extracted-frontend-preamp-gain-sweep.json"
WORK_ORDER = EVIDENCE / "sky130-frontend-preamp-interface-work-order.json"
OUT_JSON = EVIDENCE / "sky130-frontend-preamp-interface-candidate.json"
OUT_MD = EVIDENCE / "sky130-frontend-preamp-interface-candidate.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    budget = load(CAP_BUDGET)
    sweep = load(GAIN_SWEEP)
    work_order = load(WORK_ORDER)

    required_ratio = float(budget["required_transfer_ratio"])
    current_ratio = float(budget["measured_attached_transfer_ratio"])
    improvement = float(budget["required_transfer_improvement_x"])
    useful_ff = float(budget["average_useful_sample_to_sense_cap_ff"])
    total_ff = float(budget["average_sense_total_cap_ff"])
    target_total_ff = float(budget["required_total_cap_if_useful_coupling_fixed_ff"])
    target_useful_ff = float(budget["required_useful_coupling_if_total_cap_fixed_ff"])
    best_gain = float(sweep["best_setting"]["minimum_sense_to_preamp_gain_v_per_v"])
    output_target = float(sweep["output_margin_target_v"])
    current_best_output = float(sweep["best_setting"]["minimum_abs_preamp_output_diff_v"])

    candidates = [
        {
            "name": "lower_waste_sense_node",
            "test_kind": "first_order_capacitance_budget",
            "current_value": total_ff,
            "target_value": target_total_ff,
            "change_needed_x": total_ff / target_total_ff,
            "passes_now": False,
            "next_measurement": "edit extracted frontend geometry, re-extract sense_p/sense_n total capacitance, then rerun attached-preamp transient",
        },
        {
            "name": "stronger_useful_coupling",
            "test_kind": "first_order_capacitance_budget",
            "current_value": useful_ff,
            "target_value": target_useful_ff,
            "change_needed_x": target_useful_ff / useful_ff,
            "passes_now": False,
            "next_measurement": "increase intentional sample-to-sense coupling, re-extract useful capacitance, then rerun frontend-only transfer and attached-preamp transient",
        },
        {
            "name": "low_input_capacitance_isolation",
            "test_kind": "loss_budget",
            "current_value": improvement,
            "target_value": 2.0,
            "change_needed_x": improvement / 2.0,
            "passes_now": False,
            "next_measurement": "insert a low-input-capacitance isolation stage and prove attached sense loss is 2x or better before judging preamp gain",
        },
    ]
    ranked = sorted(candidates, key=lambda item: float(item["change_needed_x"]))
    return {
        "result_type": "sky130_frontend_preamp_interface_candidate",
        "status": "frontend_preamp_interface_candidate_ranked_not_yet_layout_proven",
        "source_capacitance_budget": rel(CAP_BUDGET),
        "source_gain_sweep": rel(GAIN_SWEEP),
        "source_work_order": rel(WORK_ORDER),
        "candidate_count": len(candidates),
        "current_attached_transfer_ratio": current_ratio,
        "required_transfer_ratio": required_ratio,
        "required_transfer_improvement_x": improvement,
        "current_best_output_margin_v": current_best_output,
        "output_margin_target_v": output_target,
        "best_measured_sense_to_preamp_gain_v_per_v": best_gain,
        "ranked_candidate_names": [item["name"] for item in ranked],
        "recommended_first_candidate": ranked[0]["name"],
        "candidate_results": candidates,
        "work_order_candidate_names": [item["name"] for item in work_order["candidates"]],
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "ranks the three interface work-order candidates by the measured size of the remaining physical change",
            "not_allowed": "does not edit layout, re-extract a redesigned frontend, prove preamp margin, prove latch/SAR behavior, or write accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Frontend Preamp Interface Candidate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate count: `{report['candidate_count']}`",
        f"- recommended first candidate: `{report['recommended_first_candidate']}`",
        f"- current attached transfer ratio: `{report['current_attached_transfer_ratio']:.6f}`",
        f"- required transfer ratio: `{report['required_transfer_ratio']:.6f}`",
        f"- required transfer improvement x: `{report['required_transfer_improvement_x']:.3f}`",
        f"- current best output margin V: `{report['current_best_output_margin_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- best measured sense-to-preamp gain V/V: `{report['best_measured_sense_to_preamp_gain_v_per_v']:.6f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The interface has one job: move enough of the sampled voltage to the preamp input. A candidate is better when it asks the layout to change a smaller physical quantity before the same preamp is tested again.",
        "",
        "The current attached run is not short by a vague amount. It needs about 9.54x more voltage transfer, or the preamp output stays around 56.5 uV instead of the 0.5 mV margin target.",
        "",
        "## Candidate Ranking",
        "",
        "| rank | candidate | measured object | current | target | change needed x | passes now | next measurement |",
        "|---:|---|---|---:|---:|---:|---|---|",
    ]
    ranked = sorted(report["candidate_results"], key=lambda item: float(item["change_needed_x"]))
    for index, item in enumerate(ranked, start=1):
        lines.append(
            f"| {index} | `{item['name']}` | `{item['test_kind']}` | `{item['current_value']:.6f}` | `{item['target_value']:.6f}` | `{item['change_needed_x']:.3f}` | `{item['passes_now']}` | {item['next_measurement']} |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "The smallest first move is not automatically the final design. It is the cheapest honest next test. If useful coupling or wasted capacitance can move by about 1.64x after extraction, the attached-preamp margin should be tested again. If neither physical capacitance move is practical, the isolation path becomes the circuit fork.",
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
    print("sky130_frontend_preamp_interface_candidate")
    print(f"status,{report['status']}")
    print(f"candidate_count,{report['candidate_count']}")
    print(f"recommended_first_candidate,{report['recommended_first_candidate']}")
    print(f"required_transfer_improvement_x,{report['required_transfer_improvement_x']:.3f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
