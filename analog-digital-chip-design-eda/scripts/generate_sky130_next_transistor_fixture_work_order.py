#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-next-transistor-fixture-work-order.json"
OUT_MD = EVIDENCE / "sky130-next-transistor-fixture-work-order.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def fmt(value: float) -> str:
    return f"{value:.9e}"


def main() -> int:
    target = load("sky130-sample-hold-design-target.json")
    matching = load("sky130-differential-matching-requirement.json")
    decision = load("sky130-sample-hold-topology-decision-gate.json")
    decision_margin = load("sky130-differential-dummy-candidate-decision-margin.json")
    offset_noise = load("sky130-differential-dummy-candidate-offset-noise-stress.json")

    half_lsb = target["half_lsb_12b_v"]
    required_reduction = target["required_reduction_x_from_best_measured"]
    margin = target.get("remaining_margin_x_from_best_measured", 0.0)
    best_source = target.get("best_measured_source")
    max_mismatch_mv = matching["max_allowed_differential_mismatch_mv"]
    remaining_decision_budget_mv = decision_margin["remaining_comparator_offset_or_noise_budget_mv"]
    max_passing_uncertainty_mv = offset_noise["max_passing_decision_uncertainty_mv"]

    acceptance_tests = [
        {
            "name": "runtime",
            "requirement": "each ngspice case finishes inside 180 seconds",
            "why": "a proof fixture has to be repeatable in the bridge, not only possible by hand",
        },
        {
            "name": "low_mid_high_inputs",
            "requirement": "keep the input-range and controlled width-mismatch cases passing while adding noise and comparator tolerance",
            "why": "the nominal and simple mismatch gates now pass, so the next risk is whether the margin survives decision noise",
        },
        {
            "name": "comparator_offset_noise_budget",
            "requirement": f"input-referred comparator offset plus noise should target <= {max_passing_uncertainty_mv:.4f} mV in the tested grid and must stay below {remaining_decision_budget_mv:.4f} mV unless the sample-hold error is reduced further",
            "why": "sample-hold error and comparator uncertainty spend the same decision-voltage budget",
        },
        {
            "name": "acquisition_error",
            "requirement": f"sampled value before turn-off is within half LSB, {fmt(half_lsb)} V",
            "why": "a hold result is not useful if the capacitor was never charged correctly",
        },
        {
            "name": "hold_error",
            "requirement": f"decision-voltage movement after turn-off is below {fmt(half_lsb)} V for every accepted case",
            "why": "this is the direct 12-bit sample-hold target",
        },
        {
            "name": "differential_mismatch",
            "requirement": f"if differential, unmatched movement stays below {max_mismatch_mv:.4f} mV",
            "why": "common movement can cancel, but mismatch becomes decision error",
        },
        {
            "name": "claim_boundary",
            "requirement": "candidate_post_layout_written=false and accepted_post_layout_written=false",
            "why": "transistor schematic evidence is not extracted post-layout converter evidence",
        },
    ]

    recommended_order = [
        "copy the known-running transmission-gate hold-mode deck exactly",
        "keep the passing 0.50x differential dummy case as the candidate baseline",
        "keep the low/mid/high input sweep as the regression gate",
        "keep the controlled width-mismatch sweep as a regression gate",
        "add noise and comparator threshold offset before adding SAR behavior",
        "add supply-energy measurement after the decision-voltage/noise behavior is bounded",
        "record timeouts as failed fixtures, not as circuit conclusions",
        "only update break-even or post-layout pages after a strict accepted payload exists",
    ]

    report = {
        "result_type": "sky130_next_transistor_fixture_work_order",
        "status": "sky130_next_transistor_fixture_work_order_ready_not_converter_proof",
        "recommended_next_topology": "broaden_differential_dummy_cancellation_candidate",
        "half_lsb_12b_v": half_lsb,
        "required_reduction_x": required_reduction,
        "remaining_margin_x": margin,
        "best_measured_source": best_source,
        "remaining_comparator_offset_or_noise_budget_mv": remaining_decision_budget_mv,
        "max_passing_tested_decision_uncertainty_mv": max_passing_uncertainty_mv,
        "required_cancellation_percent": target["required_cancellation_percent_from_best_measured"],
        "max_allowed_differential_mismatch_mv": max_mismatch_mv,
        "known_working_source": "sky130-sample-switch-hold-mode-ngspice",
        "known_working_mid_hold_error_v": decision["plain_hold_worst_hold_abs_delta_v"],
        "best_measured_hold_error_v": target["best_measured_hold_error_v"],
        "acceptance_tests": acceptance_tests,
        "recommended_order": recommended_order,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "defines the next Sky130 transistor fixture contract from measured sample-hold and matching targets",
            "not_allowed": "does not prove a new circuit, comparator, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Next Transistor Fixture Work Order",
        "",
        f"- status: `{report['status']}`",
        f"- recommended next topology: `{report['recommended_next_topology']}`",
        f"- known working source: `{report['known_working_source']}`",
        f"- best measured source: `{best_source}`",
        f"- best measured hold error V: `{fmt(report['best_measured_hold_error_v'])}`",
        f"- half LSB 12b V: `{fmt(half_lsb)}`",
        f"- required reduction x: `{required_reduction:.3f}`",
        f"- remaining margin x: `{margin:.3f}`",
        f"- required cancellation percent: `{report['required_cancellation_percent']:.2f}`",
        f"- max allowed differential mismatch mV: `{max_mismatch_mv:.4f}`",
        f"- remaining comparator offset or noise budget mV: `{remaining_decision_budget_mv:.4f}`",
        f"- max passing tested decision uncertainty mV: `{max_passing_uncertainty_mv:.4f}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A useful next SPICE run must answer one physical question. Does a concrete transistor circuit keep the decision voltage still enough after the sampling switch turns off?",
        "",
        f"The target is no longer vague. The differential dummy-cancellation candidate now passes nominal input range and a controlled width-mismatch sweep. The remaining budget for comparator offset or noise is about {remaining_decision_budget_mv:.4f} mV, and the tested offset/noise grid passes up to about {max_passing_uncertainty_mv:.4f} mV of combined decision uncertainty. A useful next proof must show that a concrete decision circuit stays inside that budget.",
        "",
        "## Acceptance Tests",
        "",
        "| test | requirement | why it matters |",
        "|---|---|---|",
    ]
    for item in acceptance_tests:
        lines.append(f"| `{item['name']}` | {item['requirement']} | {item['why']} |")
    lines.extend(
        [
            "",
            "## Build Order",
            "",
        ]
    )
    for step in recommended_order:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("sky130_next_transistor_fixture_work_order")
    print(f"status,{report['status']}")
    print(f"required_reduction_x,{required_reduction:.3f}")
    print(f"max_allowed_differential_mismatch_mv,{max_mismatch_mv:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
