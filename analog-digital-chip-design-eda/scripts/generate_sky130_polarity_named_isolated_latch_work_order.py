#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
RISK = EVIDENCE / "sky130-polarity-contract-latch-sar-risk.json"
POLARITY = EVIDENCE / "sky130-polarity-corrected-transistor-handoff.json"
OUT_JSON = EVIDENCE / "sky130-polarity-named-isolated-latch-work-order.json"
OUT_MD = EVIDENCE / "sky130-polarity-named-isolated-latch-work-order.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float) -> str:
    return f"{value:.9e}"


def build_report() -> dict[str, Any]:
    risk = load(RISK)
    polarity = load(POLARITY)
    half_lsb = float(risk["latch_half_lsb_12b_v"])
    best_kickback = float(risk["best_latch_kickback_v"])
    recommended_kickback = half_lsb * 0.5
    required_reduction = best_kickback / half_lsb
    recommended_reduction = best_kickback / recommended_kickback
    transistor_margin = float(risk["best_polarity_corrected_output_diff_v"])
    output_target = float(risk["output_margin_target_v"])

    candidate_moves = [
        {
            "name": "source_follower_input_buffer",
            "what_changes": "the transistor handoff drives a small buffer gate; the latch reads the buffer output",
            "why_it_might_work": "the held analog node sees less clocked latch capacitance",
            "main_risk": "buffer offset and bias current can eat the 0.5 mV margin",
        },
        {
            "name": "sampled_internal_decision_capacitor",
            "what_changes": "copy the polarity-corrected preamp value onto a small internal capacitor, then disconnect the frontend before latch regeneration",
            "why_it_might_work": "kickback lands mostly on the internal decision node instead of the frontend sense node",
            "main_risk": "the extra sampling action adds charge injection and timing error",
        },
        {
            "name": "two_phase_preamp_then_latch",
            "what_changes": "first amplify the polarity-named signal, then enable the latch after the preamp output is settled",
            "why_it_might_work": "the latch sees a larger internal difference and can use smaller input devices",
            "main_risk": "preamp noise, offset, and energy become part of the converter budget",
        },
        {
            "name": "delayed_or_bottom_plate_latch_clock",
            "what_changes": "delay the regenerative clock edge until the sampled handoff nodes are isolated",
            "why_it_might_work": "clock feedthrough is separated from the moment when the analog value is being stored",
            "main_risk": "timing can hide kickback in a later phase unless both before and after values are measured",
        },
    ]

    acceptance_tests = [
        {
            "name": "polarity_contract_preserved",
            "requirement": f"positive model value must still mean `{risk['polarity_contract']}` at the latch/SAR boundary",
        },
        {
            "name": "both_signs_resolve",
            "requirement": "positive and negative target-edge cases must both resolve to full latch output with the contracted sign",
        },
        {
            "name": "kickback_hard_line",
            "requirement": f"worst sampled-node differential kickback must be <= {fmt(half_lsb)} V",
        },
        {
            "name": "kickback_design_target",
            "requirement": f"preferred target is <= {fmt(recommended_kickback)} V, giving half-LSB slack for offset and noise",
        },
        {
            "name": "margin_survives_isolation",
            "requirement": f"corrected pre-latch output must stay >= {fmt(output_target)} V for both signs after isolation is added",
        },
        {
            "name": "wrong_code_proxy",
            "requirement": "the measured sign at the SAR threshold must not flip after applying offset, noise, and kickback budgets",
        },
        {
            "name": "no_strict_claim",
            "requirement": "candidate_post_layout_written=false and accepted_post_layout_written=false until extracted same-run evidence exists",
        },
    ]

    return {
        "result_type": "sky130_polarity_named_isolated_latch_work_order",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "polarity_named_isolated_latch_work_order_ready_not_circuit_proof",
        "source_risk_join": str(RISK.relative_to(ROOT)),
        "source_polarity_contract": str(POLARITY.relative_to(ROOT)),
        "polarity_contract": risk["polarity_contract"],
        "best_transistor_setting": risk["best_transistor_setting"],
        "best_polarity_corrected_output_diff_v": transistor_margin,
        "output_margin_target_v": output_target,
        "output_margin_over_target_x": transistor_margin / output_target,
        "best_existing_latch_kickback_v": best_kickback,
        "half_lsb_12b_v": half_lsb,
        "recommended_kickback_target_v": recommended_kickback,
        "additional_kickback_reduction_needed_to_half_lsb_x": required_reduction,
        "additional_kickback_reduction_needed_to_design_target_x": recommended_reduction,
        "candidate_moves": candidate_moves,
        "acceptance_tests": acceptance_tests,
        "next_executable_step": "build a small ngspice fixture that inserts one isolation move between the polarity-corrected transistor preamp output and the clocked latch input",
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "turns the polarity contract and measured latch kickback failure into the next isolated-latch circuit work order",
            "not_allowed": "does not prove the isolated latch circuit, SAR bit cycling, noise, offset statistics, extracted layout, DRC/LVS, or accepted post-layout converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Polarity-Named Isolated Latch Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- polarity contract: `{report['polarity_contract']}`",
        f"- best transistor setting: `{report['best_transistor_setting']}`",
        f"- best polarity-corrected output diff V: `{report['best_polarity_corrected_output_diff_v']:.9e}`",
        f"- output margin over target x: `{report['output_margin_over_target_x']:.6f}`",
        f"- best existing latch kickback V: `{report['best_existing_latch_kickback_v']:.9e}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- recommended kickback target V: `{report['recommended_kickback_target_v']:.9e}`",
        f"- additional reduction to half LSB x: `{report['additional_kickback_reduction_needed_to_half_lsb_x']:.6f}`",
        f"- additional reduction to design target x: `{report['additional_kickback_reduction_needed_to_design_target_x']:.6f}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The next latch cannot be judged only by whether it produces a digital one or zero. It must read the same signed analog quantity that the transistor handoff produced.",
        "",
        "That means two things have to be true at once. First, the sign convention must remain explicit: positive model value is the negative raw preamp output difference. Second, the latch clock must not push enough charge back into the sampled nodes to change the value being judged.",
        "",
        "The current transistor handoff has enough schematic margin. The current latch family resolves direction, but its best kickback is still above the half-LSB line. The next design is therefore an isolation problem: let the latch see the value without letting the latch clock rewrite the value.",
        "",
        "## Candidate Moves",
        "",
        "| move | what changes | why it might work | main risk |",
        "|---|---|---|---|",
    ]
    for move in report["candidate_moves"]:
        lines.append(f"| `{move['name']}` | {move['what_changes']} | {move['why_it_might_work']} | {move['main_risk']} |")
    lines.extend(["", "## Acceptance Tests", "", "| test | requirement |", "|---|---|"])
    for test in report["acceptance_tests"]:
        lines.append(f"| `{test['name']}` | {test['requirement']} |")
    lines.extend(
        [
            "",
            "## Next Executable Step",
            "",
            report["next_executable_step"],
            "",
            "## Boundary",
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
    print("sky130_polarity_named_isolated_latch_work_order")
    print(f"status,{report['status']}")
    print(f"polarity_contract,{report['polarity_contract']}")
    print(f"additional_reduction_to_half_lsb_x,{report['additional_kickback_reduction_needed_to_half_lsb_x']:.6f}")
    print(f"additional_reduction_to_design_target_x,{report['additional_kickback_reduction_needed_to_design_target_x']:.6f}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
