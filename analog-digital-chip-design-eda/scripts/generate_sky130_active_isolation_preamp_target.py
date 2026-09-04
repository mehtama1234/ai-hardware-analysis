#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE_FOLLOWER = EVIDENCE / "sky130-extracted-frontend-source-follower-handoff.json"
LOWER_WASTE = EVIDENCE / "sky130-lower-waste-frontend-preamp-candidate.json"
COMBINED_PASSIVE = EVIDENCE / "sky130-combined-coupling-waste-frontend-preamp-candidate.json"
CAP_BUDGET = EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"
OUT_JSON = EVIDENCE / "sky130-active-isolation-preamp-target.json"
OUT_MD = EVIDENCE / "sky130-active-isolation-preamp-target.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    follower = load(SOURCE_FOLLOWER)
    lower = load(LOWER_WASTE)
    combined = load(COMBINED_PASSIVE)
    budget = load(CAP_BUDGET)
    output_target = float(combined["output_margin_target_v"])
    combined_best = float(combined["minimum_abs_preamp_output_diff_v"])
    lower_best = float(lower["minimum_abs_preamp_output_diff_v"])
    follower_best = float(follower["minimum_abs_output_diff_v"])
    source_loss = float(budget["required_transfer_improvement_x"])
    target_sense_loss = 2.0
    target_output_gain = output_target / max(float(budget["measured_attached_transfer_ratio"]) * 0.00015297058540778352, 1e-15)
    return {
        "result_type": "sky130_active_isolation_preamp_target",
        "status": "active_isolation_preamp_target_ready_after_passive_and_source_follower_failures",
        "source_passive_lower_waste": rel(LOWER_WASTE),
        "source_passive_combined": rel(COMBINED_PASSIVE),
        "source_source_follower": rel(SOURCE_FOLLOWER),
        "source_capacitance_budget": rel(CAP_BUDGET),
        "passive_lower_waste_measured_cases": lower["measured_case_count"],
        "passive_lower_waste_sign_pass_count": lower["sign_pass_count"],
        "passive_lower_waste_margin_pass_count": lower["output_margin_pass_count"],
        "passive_lower_waste_best_output_v": lower_best,
        "passive_combined_measured_cases": combined["measured_case_count"],
        "passive_combined_sign_pass_count": combined["sign_pass_count"],
        "passive_combined_margin_pass_count": combined["output_margin_pass_count"],
        "passive_combined_best_output_v": combined_best,
        "source_follower_measured_cases": follower["measured_case_count"],
        "source_follower_sign_pass_count": follower["sign_pass_count"],
        "source_follower_margin_pass_count": follower["output_margin_pass_count"],
        "source_follower_best_output_v": follower_best,
        "output_margin_target_v": output_target,
        "best_passive_output_to_target_ratio": combined_best / output_target if output_target else 0.0,
        "attached_sense_loss_current_x": source_loss,
        "attached_sense_loss_target_x": target_sense_loss,
        "active_isolation_requirements": [
            {
                "name": "low_input_capacitance",
                "requirement": "the isolation input must not reduce the frontend sense voltage by more than 2x",
                "measurement": "compare frontend sense voltage with and without isolation input attached",
            },
            {
                "name": "differential_preservation",
                "requirement": "both input polarities must keep the correct sign through the isolation output",
                "measurement": "two reset-pulse transient cases, one positive and one negative input difference",
            },
            {
                "name": "usable_output_margin",
                "requirement": "the preamp output difference must reach at least 0.5 mV in both polarities",
                "measurement": "same attached frontend, same Sky130 device models, same output-margin gate",
            },
            {
                "name": "bounded_power_cost",
                "requirement": "the isolation stage must report its bias current before any system break-even claim changes",
                "measurement": "integrate or record supply current for the same run that measures margin",
            },
        ],
        "next_required_script": "run_sky130_active_isolation_preamp_candidate.py",
        "next_required_page": "docs/research/sky130-active-isolation-preamp-candidate.md",
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "turns the passive and source-follower failures into numeric acceptance requirements for the next active isolation candidate",
            "not_allowed": "does not prove an active isolation circuit, latch decision, SAR conversion, DRC/LVS, post-layout converter energy, or accepted converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Active Isolation Preamp Target",
        "",
        f"- status: `{report['status']}`",
        f"- passive lower-waste measured cases: `{report['passive_lower_waste_measured_cases']}`",
        f"- passive lower-waste margin pass count: `{report['passive_lower_waste_margin_pass_count']}`",
        f"- passive combined measured cases: `{report['passive_combined_measured_cases']}`",
        f"- passive combined margin pass count: `{report['passive_combined_margin_pass_count']}`",
        f"- source-follower measured cases: `{report['source_follower_measured_cases']}`",
        f"- source-follower sign pass count: `{report['source_follower_sign_pass_count']}`",
        f"- source-follower margin pass count: `{report['source_follower_margin_pass_count']}`",
        f"- best passive output to target ratio: `{report['best_passive_output_to_target_ratio']:.6f}`",
        f"- attached sense loss current x: `{report['attached_sense_loss_current_x']:.3f}`",
        f"- attached sense loss target x: `{report['attached_sense_loss_target_x']:.3f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The frontend is not failing because the sign is unknowable. It is failing because the next circuit stage asks too much from a tiny stored charge.",
        "",
        "Passive capacitance edits helped define the problem, but they did not create enough output margin. The simple source follower also failed because its output did not carry the small differential voltage forward. The next active isolation stage must therefore do two jobs at once: touch the frontend lightly, then drive the preamp strongly.",
        "",
        "## Acceptance Requirements",
        "",
        "| requirement | plain meaning | measurement |",
        "|---|---|---|",
    ]
    for item in report["active_isolation_requirements"]:
        lines.append(f"| `{item['name']}` | {item['requirement']} | {item['measurement']} |")
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
    print("sky130_active_isolation_preamp_target")
    print(f"status,{report['status']}")
    print(f"best_passive_output_to_target_ratio,{report['best_passive_output_to_target_ratio']:.6f}")
    print(f"source_follower_sign_pass_count,{report['source_follower_sign_pass_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
