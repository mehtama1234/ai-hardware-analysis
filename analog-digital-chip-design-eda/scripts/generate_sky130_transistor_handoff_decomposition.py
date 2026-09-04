#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-handoff-decomposition.json"
OUT_MD = EVIDENCE / "sky130-transistor-handoff-decomposition.md"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def load(name: str) -> dict[str, Any]:
    path = EVIDENCE / name
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    frontend = load("sky130-ultra-sense-frontend-candidate.json")
    transistor = load("sky130-comparator-input-stage-ngspice.json")
    macro_handoff = load("sky130-frontend-input-stage-handoff-candidate.json")
    transistor_handoff = load("sky130-frontend-transistor-input-stage-handoff-candidate.json")
    op_handoff = load("sky130-frontend-sense-to-transistor-op-handoff.json")
    short_transient = load("sky130-frontend-sense-to-transistor-short-transient.json")
    ramp_startup = load("sky130-frontend-sense-to-transistor-ramp-startup.json")
    assisted_gate_startup = load("sky130-extracted-frontend-to-transistor-gate-startup.json")
    gate_coupling_sweep = load("sky130-extracted-frontend-gate-coupling-sweep.json")
    source_follower = load("sky130-extracted-frontend-source-follower-handoff.json")
    differential_preamp = load("sky130-extracted-frontend-differential-preamp.json")
    measured_preamp = load("sky130-measured-sense-differential-preamp.json")
    preamp_bias_sweep = load("sky130-measured-sense-preamp-bias-sweep.json")
    preamp_op_map = load("sky130-measured-sense-preamp-op-map.json")
    sanity_gap = load("sky130-preamp-known-good-sanity-gap.json")
    reproduction = load("sky130-preamp-known-good-reproduction.json")
    gain_sweep = load("sky130-extracted-frontend-preamp-gain-sweep.json")
    cap_budget = load("sky130-frontend-preamp-capacitance-budget.json")

    frontend_passes = (
        frontend["passing_sign_case_count"] == frontend["case_count"]
        and frontend["minimum_sample_to_sense_transfer_ratio"] > 0.0
    )
    transistor_stage_passes = (
        transistor["measured_case_count"] == transistor["case_count"]
        and transistor["polarity_pass_count"] == transistor["case_count"]
    )
    macro_handoff_passes = (
        macro_handoff["measured_case_count"] == macro_handoff["case_count"]
        and macro_handoff["sign_pass_count"] == macro_handoff["case_count"]
        and macro_handoff["active_output_margin_pass_count"] == macro_handoff["case_count"]
    )
    real_handoff_runs = transistor_handoff["measured_case_count"] == transistor_handoff["case_count"]
    op_handoff_has_measured_margin = (
        op_handoff["measured_case_count"] > 0
        and op_handoff["sign_pass_count"] == op_handoff["measured_case_count"]
        and op_handoff["output_margin_pass_count"] == op_handoff["measured_case_count"]
    )
    short_transient_passes = (
        short_transient["measured_case_count"] == short_transient["case_count"]
        and short_transient["case_count"] > 0
        and short_transient["sign_pass_count"] == short_transient["case_count"]
        and short_transient["output_margin_pass_count"] == short_transient["case_count"]
    )
    ramp_startup_passes = (
        ramp_startup["measured_case_count"] == ramp_startup["case_count"]
        and ramp_startup["case_count"] > 0
        and ramp_startup["sign_pass_count"] == ramp_startup["case_count"]
        and ramp_startup["output_margin_pass_count"] == ramp_startup["case_count"]
    )
    assisted_gate_startup_runs = assisted_gate_startup["measured_case_count"] == assisted_gate_startup["case_count"]
    assisted_gate_startup_passes = (
        assisted_gate_startup_runs
        and assisted_gate_startup["case_count"] > 0
        and assisted_gate_startup["sign_pass_count"] == assisted_gate_startup["case_count"]
        and assisted_gate_startup["output_margin_pass_count"] == assisted_gate_startup["case_count"]
    )

    blockers = []
    if frontend_passes and transistor_stage_passes and macro_handoff_passes and not real_handoff_runs:
        blockers.append(
            "The failed object is the combined extracted-frontend plus real-transistor transient handoff, not the frontend alone, not the standalone input pair, and not the active-macro signal path."
        )
    if transistor_handoff["timed_out_case_count"]:
        blockers.append(
            "The current handoff produces timeout evidence, so sign, margin, loading, and output-gain claims are unmeasured for the real transistor combined deck."
        )
    if assisted_gate_startup_runs and not assisted_gate_startup_passes:
        blockers.append(
            "The assisted gate-startup deck now runs to completion, but one polarity fails sign and output margin, so the loaded extracted frontend is not yet a reliable source for the real input pair."
        )
    if gate_coupling_sweep["passing_setting_count"] == 0:
        blockers.append(
            "A targeted passive gate-coupling sweep found no setting that preserves both polarities, so the next design move should be a buffer or active preamp, not more passive resistance tuning."
        )
    if source_follower["sign_pass_count"] == 0:
        blockers.append(
            "A simple Sky130 source follower also fails: it loads the sense node down to about 9.5 microvolts and passes almost no differential signal to the readout pair."
        )
    if differential_preamp["timed_out_case_count"] == differential_preamp["case_count"]:
        blockers.append(
            "A direct extracted-frontend differential-preamp transient times out, so the preamp must first be proven with measured sense voltages before reconnecting it to the extracted frontend."
        )
    elif differential_preamp["output_margin_pass_count"] < differential_preamp["case_count"]:
        blockers.append(
            "A direct extracted-frontend differential-preamp transient now runs and preserves sign, but the output difference is below the decision margin, so extracted frontend loading or transfer loss is still the blocker."
        )
    if measured_preamp["timed_out_case_count"] == measured_preamp["case_count"]:
        blockers.append(
            "The same preamp bias also times out when driven by measured sense-voltage sources, so the immediate blocker is preamp bias/topology, not only extracted-frontend loading."
        )
    if preamp_bias_sweep["passing_setting_count"] == 0:
        blockers.append(
            "A measured-source transient bias sweep found no passing simple preamp setting, so the next preamp work should start with DC operating-point bias mapping."
        )
    if preamp_op_map["passing_setting_count"] == 0:
        blockers.append(
            "The first measured-source DC preamp OP map also finds no valid bias point, so the next reduction is an even smaller single-device or known-good differential-pair sanity deck."
        )
    else:
        blockers.append(
            "The corrected measured-source DC preamp OP map now finds a valid bias point, so the remaining preamp question is transient startup and then extracted-frontend loading."
        )
    if reproduction["status"] == "known_good_reproduction_passed_for_known_and_measured_sense_inputs":
        blockers.append(
            "The known-good reproduction now passes at the old target input and the smaller measured frontend input, so the remaining preamp OP-map failure is not the basic Sky130 differential pair."
        )
    else:
        blockers.append(
            "The known-good reproduction failed or timed out, so the local toolchain or deck shape must be fixed before changing the preamp."
        )
    blockers.append(
        "The extracted-frontend preamp gain sweep finds no margin-passing simple gain setting, so the next physical change must preserve more frontend voltage before amplification or add a different isolation interface."
    )
    blockers.append(
        "The capacitance budget turns that into layout terms: reduce wasted sense-node capacitance or increase useful sample-to-sense coupling by about 1.64x before trying another latch handoff."
    )

    return {
        "result_type": "sky130_transistor_handoff_decomposition",
        "status": "combined_real_transistor_handoff_is_current_blocker",
        "source_files": {
            "frontend": rel(EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"),
            "standalone_transistor_input_stage": rel(EVIDENCE / "sky130-comparator-input-stage-ngspice.json"),
            "active_macro_handoff": rel(EVIDENCE / "sky130-frontend-input-stage-handoff-candidate.json"),
            "real_transistor_handoff": rel(EVIDENCE / "sky130-frontend-transistor-input-stage-handoff-candidate.json"),
            "frontend_sense_to_transistor_op_handoff": rel(EVIDENCE / "sky130-frontend-sense-to-transistor-op-handoff.json"),
            "frontend_sense_to_transistor_short_transient": rel(EVIDENCE / "sky130-frontend-sense-to-transistor-short-transient.json"),
            "frontend_sense_to_transistor_ramp_startup": rel(EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.json"),
            "extracted_frontend_to_transistor_assisted_gate_startup": rel(EVIDENCE / "sky130-extracted-frontend-to-transistor-gate-startup.json"),
            "extracted_frontend_gate_coupling_sweep": rel(EVIDENCE / "sky130-extracted-frontend-gate-coupling-sweep.json"),
            "extracted_frontend_source_follower_handoff": rel(EVIDENCE / "sky130-extracted-frontend-source-follower-handoff.json"),
            "extracted_frontend_differential_preamp": rel(EVIDENCE / "sky130-extracted-frontend-differential-preamp.json"),
            "measured_sense_differential_preamp": rel(EVIDENCE / "sky130-measured-sense-differential-preamp.json"),
            "measured_sense_preamp_bias_sweep": rel(EVIDENCE / "sky130-measured-sense-preamp-bias-sweep.json"),
            "measured_sense_preamp_op_map": rel(EVIDENCE / "sky130-measured-sense-preamp-op-map.json"),
            "preamp_known_good_sanity_gap": rel(EVIDENCE / "sky130-preamp-known-good-sanity-gap.json"),
            "preamp_known_good_reproduction": rel(EVIDENCE / "sky130-preamp-known-good-reproduction.json"),
            "extracted_frontend_preamp_gain_sweep": rel(EVIDENCE / "sky130-extracted-frontend-preamp-gain-sweep.json"),
            "frontend_preamp_capacitance_budget": rel(EVIDENCE / "sky130-frontend-preamp-capacitance-budget.json"),
        },
        "checks": {
            "extracted_frontend_sign_and_transfer_passes": frontend_passes,
            "standalone_sky130_input_stage_polarity_passes": transistor_stage_passes,
            "combined_active_macro_handoff_passes": macro_handoff_passes,
            "frontend_sense_to_transistor_op_measured_cases_have_margin": op_handoff_has_measured_margin,
            "frontend_sense_to_transistor_short_transient_passes": short_transient_passes,
            "frontend_sense_to_transistor_ramp_startup_passes": ramp_startup_passes,
            "extracted_frontend_to_transistor_assisted_gate_startup_runs": assisted_gate_startup_runs,
            "extracted_frontend_to_transistor_assisted_gate_startup_passes": assisted_gate_startup_passes,
            "extracted_frontend_gate_coupling_sweep_finds_passing_setting": gate_coupling_sweep["passing_setting_count"] > 0,
            "extracted_frontend_source_follower_handoff_passes": source_follower["status"] == "source_follower_handoff_passed_not_latch_sar_or_strict_evidence",
            "extracted_frontend_differential_preamp_runs": differential_preamp["measured_case_count"] == differential_preamp["case_count"],
            "extracted_frontend_differential_preamp_passes": differential_preamp["status"] == "differential_preamp_handoff_passed_not_latch_sar_or_strict_evidence",
            "measured_sense_differential_preamp_runs": measured_preamp["measured_case_count"] == measured_preamp["case_count"],
            "measured_sense_differential_preamp_passes": measured_preamp["status"] == "measured_sense_differential_preamp_passed_not_extracted_frontend_or_strict_evidence",
            "measured_sense_preamp_bias_sweep_finds_passing_setting": preamp_bias_sweep["passing_setting_count"] > 0,
            "measured_sense_preamp_op_map_finds_valid_bias_point": preamp_op_map["passing_setting_count"] > 0,
            "preamp_known_good_sanity_gap_resolved": sanity_gap["status"] == "known_good_input_stage_and_measured_sense_preamp_op_now_pass",
            "preamp_known_good_reproduction_passes": reproduction["status"] == "known_good_reproduction_passed_for_known_and_measured_sense_inputs",
            "extracted_frontend_preamp_gain_sweep_finds_passing_setting": gain_sweep["passing_setting_count"] > 0,
            "frontend_preamp_capacitance_budget_ready": cap_budget["status"] == "frontend_preamp_interface_capacitance_budget_requires_less_waste_or_more_useful_coupling",
            "combined_real_transistor_handoff_runs_to_completion": real_handoff_runs,
        },
        "key_numbers": {
            "frontend_minimum_transfer_ratio": frontend["minimum_sample_to_sense_transfer_ratio"],
            "frontend_remaining_transfer_improvement_x": frontend["remaining_transfer_improvement_x"],
            "standalone_input_stage_gain_v_per_v": transistor["rows"][1]["gain_v_per_v"],
            "active_macro_minimum_output_diff_v": macro_handoff["minimum_output_diff_v"],
            "op_handoff_measured_case_count": op_handoff["measured_case_count"],
            "op_handoff_minimum_abs_output_diff_v": op_handoff["minimum_abs_output_diff_v"],
            "op_handoff_minimum_gain_v_per_v": op_handoff["minimum_gain_v_per_v"],
            "short_transient_minimum_abs_output_diff_v": short_transient["minimum_abs_output_diff_v"],
            "short_transient_minimum_output_retention_ratio": short_transient["minimum_output_retention_ratio"],
            "ramp_startup_minimum_abs_output_diff_v": ramp_startup["minimum_abs_output_diff_v"],
            "ramp_startup_minimum_gain_v_per_v": ramp_startup["minimum_gain_v_per_v"],
            "assisted_gate_startup_measured_case_count": assisted_gate_startup["measured_case_count"],
            "assisted_gate_startup_sign_pass_count": assisted_gate_startup["sign_pass_count"],
            "assisted_gate_startup_output_margin_pass_count": assisted_gate_startup["output_margin_pass_count"],
            "assisted_gate_startup_minimum_abs_output_diff_v": assisted_gate_startup["minimum_abs_output_diff_v"],
            "assisted_gate_startup_minimum_sense_to_gate_transfer_ratio": assisted_gate_startup["minimum_sense_to_gate_transfer_ratio"],
            "gate_coupling_sweep_setting_count": gate_coupling_sweep["setting_count"],
            "gate_coupling_sweep_passing_setting_count": gate_coupling_sweep["passing_setting_count"],
            "gate_coupling_sweep_timed_out_case_count": gate_coupling_sweep["timed_out_case_count"],
            "source_follower_measured_case_count": source_follower["measured_case_count"],
            "source_follower_sign_pass_count": source_follower["sign_pass_count"],
            "source_follower_minimum_sample_to_sense_transfer_ratio": source_follower["minimum_sample_to_sense_transfer_ratio"],
            "source_follower_minimum_sense_to_buffer_transfer_ratio": source_follower["minimum_sense_to_buffer_transfer_ratio"],
            "differential_preamp_measured_case_count": differential_preamp["measured_case_count"],
            "differential_preamp_timed_out_case_count": differential_preamp["timed_out_case_count"],
            "differential_preamp_sign_pass_count": differential_preamp["sign_pass_count"],
            "differential_preamp_output_margin_pass_count": differential_preamp["output_margin_pass_count"],
            "differential_preamp_minimum_abs_output_diff_v": differential_preamp["minimum_abs_preamp_output_diff_v"],
            "measured_sense_preamp_measured_case_count": measured_preamp["measured_case_count"],
            "measured_sense_preamp_timed_out_case_count": measured_preamp["timed_out_case_count"],
            "preamp_bias_sweep_setting_count": preamp_bias_sweep["setting_count"],
            "preamp_bias_sweep_passing_setting_count": preamp_bias_sweep["passing_setting_count"],
            "preamp_bias_sweep_timed_out_case_count": preamp_bias_sweep["timed_out_case_count"],
            "preamp_op_map_setting_count": preamp_op_map["setting_count"],
            "preamp_op_map_passing_setting_count": preamp_op_map["passing_setting_count"],
            "preamp_op_map_timed_out_case_count": preamp_op_map["timed_out_case_count"],
            "known_good_input_stage_measured_case_count": sanity_gap["known_good_result"]["measured_case_count"],
            "known_good_input_stage_polarity_pass_count": sanity_gap["known_good_result"]["polarity_pass_count"],
            "sanity_gap_preamp_op_timed_out_case_count": sanity_gap["preamp_op_result"]["timed_out_case_count"],
            "known_good_reproduction_op_measured_case_count": reproduction["op_measured_case_count"],
            "known_good_reproduction_polarity_pass_count": reproduction["polarity_pass_count"],
            "preamp_gain_sweep_setting_count": gain_sweep["setting_count"],
            "preamp_gain_sweep_passing_setting_count": gain_sweep["passing_setting_count"],
            "preamp_gain_sweep_best_minimum_abs_output_diff_v": gain_sweep["best_setting"]["minimum_abs_preamp_output_diff_v"],
            "cap_budget_total_cap_reduction_needed_x_if_useful_fixed": cap_budget["total_cap_reduction_needed_x_if_useful_fixed"],
            "cap_budget_useful_coupling_increase_needed_x_if_total_fixed": cap_budget["useful_coupling_increase_needed_x_if_total_fixed"],
            "real_transistor_measured_case_count": transistor_handoff["measured_case_count"],
            "real_transistor_timed_out_case_count": transistor_handoff["timed_out_case_count"],
        },
        "next_debug_probes": [
            "run measured-sense preamp transient startup from the now-passing OP bias",
            "measure whether both input signs preserve output sign, output margin, startup time, and rail headroom",
            "only after the one-stage OP deck settles, reintroduce measured sense-voltage polarity and transient startup",
            "then reconnect the passing preamp to the extracted frontend and check whether loading still collapses the sense signal",
            "only after both polarities preserve sign and margin, remove the gate startup assist and rerun the full free handoff",
        ],
        "claim_boundary": {
            "allowed": "identifies the combined real-transistor handoff transient as the current measured blocker",
            "not_allowed": "does not prove transistor handoff, latch behavior, SAR conversion, accepted post-layout evidence, or replacement economics",
        },
        "strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "blockers": blockers,
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Transistor Handoff Decomposition",
        "",
        f"- status: `{report['status']}`",
        f"- strict payload ready: `{report['strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## What The Split Shows",
        "",
        "| check | passed |",
        "|---|---|",
    ]
    for name, passed in report["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Key Numbers",
            "",
            "| number | value |",
            "|---|---:|",
        ]
    )
    for name, value in report["key_numbers"].items():
        lines.append(f"| `{name}` | `{value}` |")
    lines.extend(["", "## First Principle", ""])
    lines.append(
        "A circuit proof should fail at the smallest named object we can isolate. Here the frontend alone preserves sign, the standalone Sky130 input pair resolves tiny inputs, the active-macro handoff carries the signal forward, and direct gate ramp startup works. The assisted gate-startup run completes, but one polarity fails sign and margin once the extracted frontend is loaded by the gate connection. A targeted passive coupling sweep finds no passing assisted setting. A bare source follower runs, but it destroys the tiny differential signal instead of preserving it. A direct extracted-frontend differential-preamp transient times out. The same preamp bias also times out when driven by measured sense-voltage sources. A small measured-source transient bias sweep still finds no passing setting. The first measured-source OP map also times out. The sanity-gap report shows that this conflicts with older known-good input-stage evidence, so the primitive must be reproduced exactly."
    )
    lines.append("")
    lines.append(
        "That means the next work is not another broad AIMC page. It is a one-stage sanity deck for the preamp primitive itself. We need the smallest transistor pair to settle before adding measured inputs, transient startup, or extracted frontend loading."
    )
    lines.extend(["", "## Next Debug Probes", ""])
    lines.extend(f"- {item}" for item in report["next_debug_probes"])
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in report["blockers"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_transistor_handoff_decomposition")
    print(f"status,{report['status']}")
    for name, passed in report["checks"].items():
        print(f"{name},{passed}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
