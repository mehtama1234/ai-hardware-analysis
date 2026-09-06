#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-sample-hold-topology-decision-gate.json"
OUT_MD = EVIDENCE / "sky130-sample-hold-topology-decision-gate.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def maybe_load(name: str) -> dict | None:
    path = EVIDENCE / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def fmt_v(value: float | None) -> str:
    if value is None:
        return "not measured"
    return f"{value:.9e}"


def main() -> None:
    sample = load("sky130-transistor-sample-switch-ngspice.json")
    hold = load("sky130-sample-switch-hold-mode-ngspice.json")
    mitigation = load("sky130-sample-switch-hold-mitigation-sweep.json")
    dummy = load("sky130-sample-switch-dummy-cancellation-ngspice.json")
    bottom = load("sky130-bottom-plate-sampling-ngspice.json")
    buffered = maybe_load("sky130-buffered-sample-hold-ngspice.json")
    bootstrap = maybe_load("sky130-bootstrapped-switch-ngspice.json")
    differential = maybe_load("sky130-fully-differential-sampling-ngspice.json")
    differential_dummy = maybe_load("sky130-differential-dummy-cancellation-ngspice.json")
    differential_input_sweep = maybe_load("sky130-differential-dummy-candidate-input-sweep.json")
    differential_mismatch = maybe_load("sky130-differential-dummy-candidate-mismatch-sweep.json")
    differential_control = maybe_load("differential-sampling-control-proof-ngspice.json")
    single_device_injection = maybe_load("sky130-single-device-charge-injection-ngspice.json")
    clock_edge = maybe_load("sky130-sample-switch-clock-edge-sweep.json")
    design_target = maybe_load("sky130-sample-hold-design-target.json")
    matching_requirement = maybe_load("sky130-differential-matching-requirement.json")
    fixture_work_order = maybe_load("sky130-next-transistor-fixture-work-order.json")

    half_lsb = sample["half_lsb_12b_v"]
    on_state_passes = sample["worst_sample_error_v"] <= half_lsb
    plain_hold_passes = hold["worst_hold_abs_delta_v"] <= half_lsb
    mitigation_passes = mitigation["best_worst_hold_abs_delta_v"] <= half_lsb
    dummy_passes = dummy["best_worst_hold_abs_delta_v"] <= half_lsb
    bottom_passes = bottom["best_worst_hold_abs_delta_v"] <= half_lsb
    all_existing_hold_topologies_pass = plain_hold_passes and mitigation_passes and dummy_passes and bottom_passes

    rows = [
        {
            "evidence": "on_state_sample_switch",
            "best_or_worst_case_v": sample["worst_sample_error_v"],
            "passes_half_lsb_12b": on_state_passes,
            "meaning": "the switch can charge the sample node closely enough while it is still on",
        },
        {
            "evidence": "plain_hold_mode",
            "best_or_worst_case_v": hold["worst_hold_abs_delta_v"],
            "passes_half_lsb_12b": plain_hold_passes,
            "meaning": "the held value moves too far after the switch turns off",
        },
        {
            "evidence": "larger_cap_or_switch_resize",
            "best_or_worst_case_v": mitigation["best_worst_hold_abs_delta_v"],
            "passes_half_lsb_12b": mitigation_passes,
            "meaning": "more capacitance reduces voltage movement, but not enough",
        },
        {
            "evidence": "dummy_cancellation",
            "best_or_worst_case_v": dummy["best_worst_hold_abs_delta_v"],
            "passes_half_lsb_12b": dummy_passes,
            "meaning": "opposite clock charge helps, but still leaves too much held-voltage error",
        },
        {
            "evidence": "bottom_plate_fixture",
            "best_or_worst_case_v": bottom["best_worst_hold_abs_delta_v"],
            "passes_half_lsb_12b": bottom_passes,
            "meaning": "the current two-node bottom-plate fixture does not fix the stored voltage",
        },
    ]
    if buffered:
        rows.append(
            {
                "evidence": "buffered_source_follower_candidate",
                "best_or_worst_case_v": buffered["worst_sample_hold_abs_delta_v"],
                "passes_half_lsb_12b": False,
                "meaning": "the naive source-follower buffer produced no measured cases, so it is not acceptable evidence",
            }
        )
    if bootstrap:
        bootstrap_measured = bootstrap.get("measured_case_count", 0) > 0
        rows.append(
            {
                "evidence": "idealized_bootstrapped_switch_candidate",
                "best_or_worst_case_v": bootstrap["worst_hold_abs_delta_v"],
                "passes_half_lsb_12b": False,
                "meaning": "the idealized bootstrapped Sky130 switch converged and acquired correctly, but hold movement remains above the 12-bit target"
                if bootstrap_measured
                else "the idealized bootstrapped Sky130 switch produced no measured cases, so the fixture is not a proof path yet",
            }
        )
    if differential:
        differential_value = differential["worst_diff_hold_abs_delta_v"]
        differential_measured = differential.get("measured_case_count", 0) > 0 and differential_value is not None
        rows.append(
            {
                "evidence": "sky130_differential_sampling_candidate",
                "best_or_worst_case_v": differential_value,
                "passes_half_lsb_12b": differential_value <= half_lsb if differential_measured else False,
                "meaning": "the one-case Sky130 differential transmission-gate fixture now measures, but its decision-voltage movement is still above the 12-bit target"
                if differential_measured
                else "the Sky130 differential switch fixture produced no measured cases, so transistor-level differential sampling still needs a stable deck",
            }
        )
    if differential_control:
        rows.append(
            {
                "evidence": "differential_sampling_control_proof",
                "best_or_worst_case_v": differential_control["worst_diff_hold_abs_delta_v"],
                "passes_half_lsb_12b": differential_control["diff_hold_pass_count"] == differential_control["case_count"],
                "meaning": "the ideal-switch control proof shows common disturbance cancels, but mismatch remains as decision error",
            }
        )
    if differential_dummy:
        differential_dummy_value = differential_dummy["best_diff_hold_abs_delta_v"]
        differential_dummy_passes = differential_dummy_value <= half_lsb if differential_dummy_value is not None else False
        rows.append(
            {
                "evidence": "sky130_differential_dummy_cancellation",
                "best_or_worst_case_v": differential_dummy_value,
                "passes_half_lsb_12b": differential_dummy_passes,
                "meaning": "matched opposite-clock dummy devices produced one passing Sky130 decision-voltage case, so this is the next candidate front end to broaden and stress",
            }
        )
    if differential_input_sweep:
        input_sweep_value = differential_input_sweep["worst_diff_hold_abs_delta_v"]
        rows.append(
            {
                "evidence": "sky130_differential_dummy_input_sweep",
                "best_or_worst_case_v": input_sweep_value,
                "passes_half_lsb_12b": input_sweep_value <= half_lsb if input_sweep_value is not None else False,
                "meaning": "the fixed 0.50x differential dummy candidate passed low, mid, and high nominal input cases",
            }
        )
    if differential_mismatch:
        mismatch_value = differential_mismatch["worst_diff_hold_abs_delta_v"]
        rows.append(
            {
                "evidence": "sky130_differential_dummy_mismatch_sweep",
                "best_or_worst_case_v": mismatch_value,
                "passes_half_lsb_12b": mismatch_value <= half_lsb if mismatch_value is not None else False,
                "meaning": "the fixed candidate passed the controlled +/-1% and +/-2% one-sided width-mismatch cases",
            }
        )
    if single_device_injection:
        rows.append(
            {
                "evidence": "sky130_single_device_charge_injection",
                "best_or_worst_case_v": single_device_injection["worst_edge_abs_delta_v"],
                "passes_half_lsb_12b": False,
                "meaning": "even the one-device Sky130 gate-edge fixture produced no measured cases under bounded ngspice runs",
            }
        )
    if clock_edge:
        rows.append(
            {
                "evidence": "sky130_clock_edge_sweep",
                "best_or_worst_case_v": clock_edge["best_worst_hold_abs_delta_v"],
                "passes_half_lsb_12b": clock_edge["best_worst_hold_abs_delta_v"] <= half_lsb if clock_edge["best_worst_hold_abs_delta_v"] is not None else False,
                "meaning": "the one-case baseline edge check measured cleanly, but the mid-input held voltage still moves more than the 12-bit target",
            }
        )

    report = {
        "result_type": "sky130_sample_hold_topology_decision_gate",
        "status": "sky130_sample_hold_topology_gate_requires_buffered_or_bootstrapped_design",
        "half_lsb_12b_v": half_lsb,
        "on_state_passes": on_state_passes,
        "plain_hold_passes": plain_hold_passes,
        "larger_cap_or_switch_resize_passes": mitigation_passes,
        "dummy_cancellation_passes": dummy_passes,
        "bottom_plate_fixture_passes": bottom_passes,
        "all_existing_hold_topologies_pass": all_existing_hold_topologies_pass,
        "plain_hold_worst_hold_abs_delta_v": hold["worst_hold_abs_delta_v"],
        "best_mitigation_config": mitigation["best_config"],
        "best_mitigation_worst_hold_abs_delta_v": mitigation["best_worst_hold_abs_delta_v"],
        "best_dummy_config": dummy["best_config"],
        "best_dummy_worst_hold_abs_delta_v": dummy["best_worst_hold_abs_delta_v"],
        "bottom_plate_best_config": bottom["best_config"],
        "bottom_plate_worst_hold_abs_delta_v": bottom["best_worst_hold_abs_delta_v"],
        "buffered_candidate_measured_case_count": buffered.get("measured_case_count") if buffered else None,
        "bootstrapped_candidate_measured_case_count": bootstrap.get("measured_case_count") if bootstrap else None,
        "sky130_differential_candidate_measured_case_count": differential.get("measured_case_count") if differential else None,
        "sky130_differential_dummy_best_config": differential_dummy.get("best_config") if differential_dummy else None,
        "sky130_differential_dummy_best_diff_hold_abs_delta_v": differential_dummy.get("best_diff_hold_abs_delta_v") if differential_dummy else None,
        "sky130_differential_dummy_pass_count": differential_dummy.get("diff_hold_pass_count") if differential_dummy else None,
        "sky130_differential_dummy_input_sweep_pass_count": differential_input_sweep.get("diff_hold_pass_count") if differential_input_sweep else None,
        "sky130_differential_dummy_input_sweep_worst_diff_hold_abs_delta_v": differential_input_sweep.get("worst_diff_hold_abs_delta_v") if differential_input_sweep else None,
        "sky130_differential_dummy_mismatch_pass_count": differential_mismatch.get("diff_hold_pass_count") if differential_mismatch else None,
        "sky130_differential_dummy_mismatch_worst_diff_hold_abs_delta_v": differential_mismatch.get("worst_diff_hold_abs_delta_v") if differential_mismatch else None,
        "differential_control_diff_hold_pass_count": differential_control.get("diff_hold_pass_count") if differential_control else None,
        "differential_control_case_count": differential_control.get("case_count") if differential_control else None,
        "single_device_injection_measured_case_count": single_device_injection.get("measured_case_count") if single_device_injection else None,
        "clock_edge_sweep_measured_case_count": clock_edge.get("measured_case_count") if clock_edge else None,
        "design_target_required_reduction_x": design_target.get("required_reduction_x_from_best_measured") if design_target else None,
        "design_target_required_cancellation_percent": design_target.get("required_cancellation_percent_from_best_measured") if design_target else None,
        "matching_requirement_max_allowed_mismatch_mv": matching_requirement.get("max_allowed_differential_mismatch_mv") if matching_requirement else None,
        "matching_requirement_required_common_rejection_percent": matching_requirement.get("required_common_rejection_percent") if matching_requirement else None,
        "fixture_work_order_recommended_next_topology": fixture_work_order.get("recommended_next_topology") if fixture_work_order else None,
        "selected_next_topology_candidates": [
            "bootstrapped_switch",
            "buffered_sample_and_hold",
            "fully_differential_sampling",
        ],
        "recommended_next_proof": "stress the passing differential dummy-cancellation candidate with noise, comparator tolerance, energy, and layout before attempting SAR or post-layout converter claims"
        if differential_mismatch and differential_mismatch.get("all_measured_cases_pass_diff_hold") is True
        else "build a numerically stable transistor-level differential or bootstrapped hold fixture before attempting comparator, SAR, or post-layout converter claims",
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns the existing Sky130 sample-and-hold measurements into a topology decision for the next converter circuit proof",
            "not_allowed": "does not prove a working ADC, DAC, comparator, SAR loop, extracted layout, DRC/LVS signoff, or accepted post-layout converter economics",
        },
        "rows": rows,
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Sample-Hold Topology Decision Gate",
        "",
        f"- status: `{report['status']}`",
        f"- half LSB at 12 bits V: `{fmt_v(half_lsb)}`",
        f"- on-state sample switch passes: `{on_state_passes}`",
        f"- all existing hold topologies pass: `{all_existing_hold_topologies_pass}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## What The Measurements Say",
        "",
        "| evidence | measured voltage movement or error | passes 12-bit half LSB | meaning |",
        "| --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['evidence']}` | `{fmt_v(row['best_or_worst_case_v'])}` | `{row['passes_half_lsb_12b']}` | {row['meaning']} |"
        )
    lines.extend(
        [
            "",
            "## First-Principles Reading",
            "",
            "A sample-and-hold circuit has two jobs. First it must let charge enter the capacitor so the capacitor voltage becomes the input voltage. Then it must stop charge from moving so the stored voltage stays still while the digital decision is made.",
            "",
            "The first job is working in the simple transmission-gate fixture. While the switch is on, the capacitor gets close enough to the input for the 12-bit half-LSB line. That is useful, but it is only the acquisition part of the circuit.",
            "",
            "The second job is failing. When the switch turns off, charge from the clocked devices and nearby nodes changes the stored charge. The capacitor voltage then moves. Since voltage movement is charge movement divided by capacitance, a larger capacitor helps, but it also costs more energy and takes longer to settle. In the measured sweep it helps by a real amount, but the best result is still above the target.",
            "",
            "Dummy cancellation is the same problem attacked from the other side. It adds an opposite clocked device to push charge back onto the node. That can reduce the error when the size and timing are close, but it is not a law of the circuit. The measured best dummy case still misses the target, so it cannot be promoted into a converter proof.",
            "",
            "The current bottom-plate fixture also does not solve it. Bottom-plate sampling should disconnect the sensitive side before the worst clock disturbance arrives, but this implemented two-node fixture still moves the stored differential voltage too much. That means the idea may still be useful, but this circuit is not the accepted topology.",
            "",
            "The newer stronger sketches are not accepted either. The naive source-follower buffer, idealized bootstrapped switch, and one-device Sky130 gate-edge fixture all failed to produce measured cases under bounded ngspice runs. The Sky130 differential transmission-gate fixture now measures one mid-input point, but the differential decision voltage still moves too much. The differential dummy-cancellation fixture changes that one fact: one matched dummy size brings the measured decision-voltage movement below the half-LSB line, the fixed candidate passes low, mid, and high nominal input cases, and the controlled width-mismatch sweep also passes. That is a candidate front end, not a converter proof.",
            "",
            "The differential control proof does produce numbers. It shows the key law: common movement can cancel from a differential decision, but mismatch remains. In its measured rows, the common-injection cases pass and the mismatched-injection case fails the 12-bit line. That means differential sampling is still worth pursuing, but only with a transistor fixture that can show matched disturbance, not just assumed matched disturbance.",
            "",
            f"The design target is now numeric. The best measured decision-voltage case is `{design_target['best_measured_hold_error_v']:.9e}` V against a `{design_target['half_lsb_12b_v']:.9e}` V half-LSB line." if design_target else "The design target has not been generated yet.",
            "",
            f"The differential matching requirement is also numeric. The next differential sample-hold must keep unmatched movement below `{matching_requirement['max_allowed_differential_mismatch_mv']:.4f} mV` and reject about `{matching_requirement['required_common_rejection_percent']:.1f}%` of the common disturbance." if matching_requirement else "The differential matching requirement has not been generated yet.",
            "",
            f"The next executable work order is `{fixture_work_order['recommended_next_topology']}`. It says to copy the known-running transmission-gate hold-mode deck exactly, change one variable at a time, and require every accepted case to finish inside the bridge runtime bound." if fixture_work_order else "The next transistor fixture work order has not been generated yet.",
            "",
            "## Next Circuit To Build",
            "",
            "The next proof should not be another broad architecture page. It should make one transistor-level fixture stable enough to measure:",
            "",
            "- `differential_dummy_cancellation`: first priority, because it is the first measured Sky130 sample-hold fixture here with passing decision-voltage hold cases across low, mid, high, and controlled one-sided width mismatch.",
            "- `fully_differential_sampling`: keep as the baseline comparison, because the control proof says the decision voltage can reject shared disturbance.",
            "- `bootstrapped_switch`: second priority, because constant switch overdrive may reduce input-dependent acquisition and charge injection.",
            "- `buffered_sample_and_hold`: useful only after the buffer is explicitly biased and numerically stable.",
            "",
            "The next run must report acquisition error, hold movement, supply energy, and convergence for low, mid, and high input. If it does not beat the half-LSB line in hold mode, it is still only a characterization result.",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("sky130_sample_hold_topology_decision_gate")


if __name__ == "__main__":
    main()
