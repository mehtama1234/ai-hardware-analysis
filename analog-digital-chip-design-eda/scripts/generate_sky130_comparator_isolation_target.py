#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-comparator-isolation-target.json"
OUT_MD = EVIDENCE / "sky130-comparator-isolation-target.md"


def load(name: str) -> dict:
    path = EVIDENCE / name
    if not path.exists():
        raise SystemExit(f"missing input artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def main() -> int:
    size_sweep = load("sky130-latch-input-size-kickback-sweep.json")
    coupled = load("sky130-sample-hold-latch-kickback-ngspice.json")
    comparator_spec = load("sky130-comparator-acceptance-fixture-spec.json")

    half_lsb = float(size_sweep["half_lsb_12b_v"])
    baseline_kickback = float(size_sweep["baseline_kickback_v"])
    best_kickback = float(size_sweep["best_kickback_v"])
    best_width = float(size_sweep["best_width_um"])
    target_mv = float(size_sweep["target_combined_offset_noise_mv"])
    hard_budget_mv = float(comparator_spec["derived_budget"]["remaining_comparator_offset_or_noise_budget_mv"])
    required_additional_reduction = best_kickback / half_lsb
    total_reduction_from_baseline = baseline_kickback / half_lsb
    observed_width_reduction = baseline_kickback / best_kickback
    required_kickback_v = half_lsb
    recommended_target_v = half_lsb * 0.5
    recommended_additional_reduction = best_kickback / recommended_target_v

    candidate_options = [
        {
            "name": "source_follower_or_preamp_buffer",
            "purpose": "make the sampled capacitor drive a small gate instead of the latch input pair directly",
            "risk": "adds offset, gain error, bias current, bandwidth limits, and its own input capacitance",
        },
        {
            "name": "sampled_comparator_input_capacitor",
            "purpose": "copy the held voltage onto a small internal decision capacitor before the latch clock moves",
            "risk": "adds a second sampling error and needs careful clock order",
        },
        {
            "name": "bottom_plate_or_delayed_latch_clock",
            "purpose": "separate sampling switch turn-off from the latch regenerative edge",
            "risk": "can reduce one kickback path while increasing another if timing is wrong",
        },
        {
            "name": "tiny_input_pair_plus_preamplification",
            "purpose": "keep latch input capacitance low while restoring enough signal before regeneration",
            "risk": "the preamp may spend more energy and introduce input-referred offset",
        },
    ]

    next_acceptance_tests = [
        {
            "name": "kickback_margin",
            "requirement": f"worst sampled differential kickback <= {fmt(recommended_target_v)} V target and must be below {fmt(required_kickback_v)} V hard line",
        },
        {
            "name": "resolution_preserved",
            "requirement": "both positive and negative target-edge cases still resolve with correct polarity",
        },
        {
            "name": "budget_connection",
            "requirement": f"target-edge input difference remains tied to {target_mv:.4f} mV, with {hard_budget_mv:.4f} mV as the hard comparator budget",
        },
        {
            "name": "no_post_layout_claim",
            "requirement": "candidate_post_layout_written=false and accepted_post_layout_written=false",
        },
    ]

    payload = {
        "result_type": "sky130_comparator_isolation_target",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "sky130_comparator_isolation_target_defined_not_circuit_proof",
        "source_artifacts": {
            "latch_input_size_sweep": "sky130-latch-input-size-kickback-sweep.json",
            "coupled_latch_kickback": "sky130-sample-hold-latch-kickback-ngspice.json",
            "comparator_acceptance_spec": "sky130-comparator-acceptance-fixture-spec.json",
        },
        "measured_boundary": {
            "baseline_coupled_kickback_v": baseline_kickback,
            "baseline_coupled_status": coupled.get("status"),
            "best_width_um": best_width,
            "best_kickback_v": best_kickback,
            "half_lsb_12b_v": half_lsb,
            "observed_width_reduction_x": observed_width_reduction,
            "additional_reduction_needed_to_reach_half_lsb_x": required_additional_reduction,
            "additional_reduction_needed_to_reach_half_lsb_half_margin_x": recommended_additional_reduction,
            "total_reduction_needed_from_original_baseline_x": total_reduction_from_baseline,
        },
        "target": {
            "hard_kickback_limit_v": required_kickback_v,
            "recommended_kickback_target_v": recommended_target_v,
            "target_combined_offset_noise_mv": target_mv,
            "hard_comparator_budget_mv": hard_budget_mv,
        },
        "candidate_options": candidate_options,
        "next_acceptance_tests": next_acceptance_tests,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "converts measured latch kickback failures into the isolation reduction target for the next Sky130 comparator circuit",
            "not_allowed": "does not prove an isolated comparator, comparator noise, mismatch, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Comparator Isolation Target",
        "",
        "This page turns the latch kickback failure into the next circuit target. It does not claim a new circuit works. It says how much isolation the next circuit must add before the sampled-node result can support a 12-bit decision.",
        "",
        f"- status: `{payload['status']}`",
        f"- baseline coupled kickback V: `{fmt(baseline_kickback)}`",
        f"- best tested input width um: `{best_width}`",
        f"- best measured kickback V: `{fmt(best_kickback)}`",
        f"- half LSB 12b V: `{fmt(half_lsb)}`",
        f"- observed width reduction x: `{observed_width_reduction:.3f}`",
        f"- additional reduction needed to reach half LSB x: `{required_additional_reduction:.3f}`",
        f"- recommended additional reduction for half-LSB margin x: `{recommended_additional_reduction:.3f}`",
        f"- recommended kickback target V: `{fmt(recommended_target_v)}`",
        f"- candidate post-layout written: `{payload['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{payload['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The sampled capacitor stores the decision voltage as charge. The latch should read that charge, but its input devices also connect capacitance to fast clocked internal nodes. When those internal nodes move, some charge returns to the sampled nodes. That is kickback.",
        "",
        "The width sweep showed the direction clearly. Smaller latch input devices reduce kickback because they reduce the capacitance coupled to the sampled nodes. But the best tested width still moved the differential sampled voltage by more than the half-LSB line. This means sizing alone is not enough. The next circuit needs an isolation mechanism.",
        "",
        f"The hard line is {fmt(half_lsb)} V. The best measured width still has {fmt(best_kickback)} V of kickback, so the next circuit needs at least {required_additional_reduction:.3f}x more reduction. A practical target is half the half-LSB line, {fmt(recommended_target_v)} V, which needs about {recommended_additional_reduction:.3f}x more reduction from the best tested width.",
        "",
        "## Candidate Isolation Moves",
        "",
        "| move | purpose | risk |",
        "|---|---|---|",
    ]
    for option in candidate_options:
        lines.append(f"| `{option['name']}` | {option['purpose']} | {option['risk']} |")
    lines.extend(["", "## Next Acceptance Tests", "", "| test | requirement |", "|---|---|"])
    for test in next_acceptance_tests:
        lines.append(f"| `{test['name']}` | {test['requirement']} |")
    lines.extend(["", "## Refused Claim", "", payload["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("sky130_comparator_isolation_target")
    print(f"status,{payload['status']}")
    print(f"best_kickback_v,{best_kickback:.9e}")
    print(f"half_lsb_12b_v,{half_lsb:.9e}")
    print(f"additional_reduction_needed_x,{required_additional_reduction:.3f}")
    print(f"recommended_additional_reduction_x,{recommended_additional_reduction:.3f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
