#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-comparator-acceptance-fixture-spec.json"
OUT_MD = EVIDENCE / "sky130-comparator-acceptance-fixture-spec.md"


def load(name: str) -> dict:
    path = EVIDENCE / name
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_v(value: float) -> str:
    return f"{value:.9e}"


def main() -> int:
    input_sweep = load("sky130-differential-dummy-candidate-input-sweep.json")
    mismatch_sweep = load("sky130-differential-dummy-candidate-mismatch-sweep.json")
    decision_margin = load("sky130-differential-dummy-candidate-decision-margin.json")
    offset_noise = load("sky130-differential-dummy-candidate-offset-noise-stress.json")
    work_order = load("sky130-next-transistor-fixture-work-order.json")

    half_lsb_v = float(decision_margin["half_lsb_12b_v"])
    sample_hold_error_v = float(decision_margin["worst_sample_hold_error_v"])
    remaining_budget_mv = float(decision_margin["remaining_comparator_offset_or_noise_budget_mv"])
    max_tested_pass_mv = float(offset_noise["max_passing_decision_uncertainty_mv"])
    min_tested_fail_mv = float(offset_noise["min_failing_decision_uncertainty_mv"])

    required_measurements = [
        {
            "name": "input_referred_static_offset_mv",
            "method": "sweep a small differential input around zero and find the sign-change point",
            "acceptance": f"absolute offset <= {max_tested_pass_mv:.4f} mV target and below {remaining_budget_mv:.4f} mV hard budget",
        },
        {
            "name": "decision_noise_rms_mv",
            "method": "run repeated transient decisions with the same input and measure output-code spread as input-referred voltage",
            "acceptance": "combine with static offset by root-sum-square before comparing with the budget",
        },
        {
            "name": "kickback_on_held_decision_node_v",
            "method": "measure differential held-node movement when the comparator input is connected and clocked",
            "acceptance": f"sample-hold movement plus input-referred decision uncertainty remains below {fmt_v(half_lsb_v)} V",
        },
        {
            "name": "metastability_resolution_ns",
            "method": "measure how long the latch output takes to reach a valid logic level near the smallest accepted input",
            "acceptance": "resolves inside the SAR comparison time used by the converter estimate",
        },
        {
            "name": "supply_energy_per_decision_j",
            "method": "integrate supply current during one comparison event",
            "acceptance": "record the value, but do not use it for break-even until the full extracted converter payload exists",
        },
    ]

    stimulus_cases = [
        {
            "name": "zero_crossing_offset_sweep",
            "input": "small signed differential inputs around zero",
            "purpose": "find whether the comparator decision boundary is shifted away from zero",
        },
        {
            "name": "budget_edge_pass_case",
            "input": f"differential input at {max_tested_pass_mv:.4f} mV plus the measured sample-hold error",
            "purpose": "check the strongest already-passing budget point",
        },
        {
            "name": "budget_edge_fail_guard",
            "input": f"differential input at {min_tested_fail_mv:.4f} mV plus the measured sample-hold error",
            "purpose": "prove the fixture can detect when the known budget is exceeded",
        },
        {
            "name": "low_mid_high_sampled_inputs",
            "input": "reuse the low, mid, and high common-mode cases from the candidate input sweep",
            "purpose": "make sure comparator loading does not destroy the sample-and-hold result that already passed",
        },
        {
            "name": "controlled_width_mismatch_cases",
            "input": "reuse the matched and +/-1% and +/-2% sample-switch width cases",
            "purpose": "keep the current mismatch regression gate alive after the comparator is attached",
        },
    ]

    next_implementation_steps = [
        "start with a clocked differential latch or preamp-latch deck in Sky130 ngspice",
        "drive it from the existing differential dummy sample-and-hold candidate instead of an ideal voltage source only",
        "measure offset first, because a noisy comparator with unknown static offset cannot be interpreted",
        "measure kickback before SAR integration, because kickback spends the same voltage budget as hold error",
        "add repeated-noise or corner-style sweeps only after the nominal transient deck is numerically stable",
        "keep the output as candidate schematic evidence; do not write accepted post-layout evidence",
    ]

    payload = {
        "result_type": "sky130_comparator_acceptance_fixture_spec",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "sky130_comparator_acceptance_fixture_spec_ready_not_comparator_proof",
        "source_artifacts": {
            "input_sweep": "sky130-differential-dummy-candidate-input-sweep.json",
            "mismatch_sweep": "sky130-differential-dummy-candidate-mismatch-sweep.json",
            "decision_margin": "sky130-differential-dummy-candidate-decision-margin.json",
            "offset_noise_stress": "sky130-differential-dummy-candidate-offset-noise-stress.json",
            "fixture_work_order": "sky130-next-transistor-fixture-work-order.json",
        },
        "derived_budget": {
            "half_lsb_12b_v": half_lsb_v,
            "worst_sample_hold_error_v": sample_hold_error_v,
            "remaining_comparator_offset_or_noise_budget_mv": remaining_budget_mv,
            "target_combined_offset_noise_mv": max_tested_pass_mv,
            "first_known_failing_combined_offset_noise_mv": min_tested_fail_mv,
        },
        "input_regression": {
            "input_sweep_cases": input_sweep.get("case_count"),
            "input_sweep_passes": input_sweep.get("all_measured_cases_pass_diff_hold"),
            "mismatch_sweep_cases": mismatch_sweep.get("case_count"),
            "mismatch_sweep_passes": mismatch_sweep.get("all_measured_cases_pass_diff_hold"),
            "work_order_topology": work_order.get("recommended_next_topology"),
        },
        "required_measurements": required_measurements,
        "stimulus_cases": stimulus_cases,
        "next_implementation_steps": next_implementation_steps,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns the measured sample-hold and decision-budget results into a concrete comparator fixture contract",
            "not_allowed": "does not simulate comparator transistors, prove comparator noise, prove SAR conversion, prove extracted layout, or replace converter economics",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Comparator Acceptance Fixture Spec",
        "",
        "This page turns the measured sample-and-hold result into the next comparator test. It does not claim that the comparator exists yet. It says what the comparator must prove before it is allowed to sit behind the passing differential dummy sample-and-hold candidate.",
        "",
        f"- status: `{payload['status']}`",
        f"- half LSB 12b V: `{fmt_v(half_lsb_v)}`",
        f"- worst measured sample-hold error V: `{fmt_v(sample_hold_error_v)}`",
        f"- remaining comparator offset or noise budget mV: `{remaining_budget_mv:.4f}`",
        f"- target combined offset/noise mV: `{max_tested_pass_mv:.4f}`",
        f"- first known failing combined offset/noise mV: `{min_tested_fail_mv:.4f}`",
        f"- candidate post-layout written: `{payload['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{payload['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The sample-and-hold does not produce a final answer. It leaves a small voltage difference for the next circuit to decide. That next circuit is the comparator.",
        "",
        "A comparator can fail even when the sampled voltage is good. Its internal mismatch can move the decision boundary. Its noise can make the same input produce different decisions. Its clock edge can kick charge back into the held node. These are not separate bookkeeping problems. They all spend the same voltage budget between the held decision voltage and the nearest wrong ADC code.",
        "",
        f"The current measured sample-and-hold candidate spends {sample_hold_error_v * 1000:.4f} mV of a {half_lsb_v * 1000:.4f} mV half-LSB budget. That leaves about {remaining_budget_mv:.4f} mV for comparator offset, comparator noise, and comparator loading. The stress table shows that {max_tested_pass_mv:.4f} mV still passes, while {min_tested_fail_mv:.4f} mV starts to fail. The next transistor deck should therefore aim below {max_tested_pass_mv:.4f} mV and treat {remaining_budget_mv:.4f} mV as the hard line unless the sample-and-hold improves.",
        "",
        "## Required Measurements",
        "",
        "| measurement | method | acceptance |",
        "|---|---|---|",
    ]
    for item in required_measurements:
        lines.append(f"| `{item['name']}` | {item['method']} | {item['acceptance']} |")
    lines.extend(["", "## Stimulus Cases", "", "| case | input | purpose |", "|---|---|---|"])
    for item in stimulus_cases:
        lines.append(f"| `{item['name']}` | {item['input']} | {item['purpose']} |")
    lines.extend(["", "## Build Order", ""])
    for item in next_implementation_steps:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Refused Claim",
            "",
            payload["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("sky130_comparator_acceptance_fixture_spec")
    print(f"status,{payload['status']}")
    print(f"target_combined_offset_noise_mv,{max_tested_pass_mv:.4f}")
    print(f"hard_budget_mv,{remaining_budget_mv:.4f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
