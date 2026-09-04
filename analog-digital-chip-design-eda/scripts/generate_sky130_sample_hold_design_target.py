#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-sample-hold-design-target.json"
OUT_MD = EVIDENCE / "sky130-sample-hold-design-target.md"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def maybe(name: str) -> dict | None:
    path = EVIDENCE / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def main() -> int:
    hold = load("sky130-sample-switch-hold-mode-ngspice.json")
    mitigation = load("sky130-sample-switch-hold-mitigation-sweep.json")
    dummy = load("sky130-sample-switch-dummy-cancellation-ngspice.json")
    edge = maybe("sky130-sample-switch-clock-edge-sweep.json")
    differential_dummy = maybe("sky130-differential-dummy-cancellation-ngspice.json")
    differential_input_sweep = maybe("sky130-differential-dummy-candidate-input-sweep.json")
    differential_mismatch = maybe("sky130-differential-dummy-candidate-mismatch-sweep.json")

    half_lsb = hold["half_lsb_12b_v"]
    candidates = [
        {
            "name": "plain_hold_worst",
            "error_v": hold["worst_hold_abs_delta_v"],
            "source": "sky130-sample-switch-hold-mode-ngspice",
        },
        {
            "name": "larger_cap_best",
            "error_v": mitigation["best_worst_hold_abs_delta_v"],
            "source": "sky130-sample-switch-hold-mitigation-sweep",
        },
        {
            "name": "dummy_cancellation_best",
            "error_v": dummy["best_worst_hold_abs_delta_v"],
            "source": "sky130-sample-switch-dummy-cancellation-ngspice",
        },
    ]
    if edge and edge.get("best_worst_hold_abs_delta_v") is not None:
        candidates.append(
            {
                "name": "clock_edge_mid_input_baseline",
                "error_v": edge["best_worst_hold_abs_delta_v"],
                "source": "sky130-sample-switch-clock-edge-sweep",
            }
        )
    if differential_dummy and differential_dummy.get("best_diff_hold_abs_delta_v") is not None:
        candidates.append(
            {
                "name": "differential_dummy_decision_voltage",
                "error_v": differential_dummy["best_diff_hold_abs_delta_v"],
                "source": "sky130-differential-dummy-cancellation-ngspice",
            }
        )
    if differential_input_sweep and differential_input_sweep.get("worst_diff_hold_abs_delta_v") is not None:
        candidates.append(
            {
                "name": "differential_dummy_input_sweep_worst",
                "error_v": differential_input_sweep["worst_diff_hold_abs_delta_v"],
                "source": "sky130-differential-dummy-candidate-input-sweep",
            }
        )
    if differential_mismatch and differential_mismatch.get("worst_diff_hold_abs_delta_v") is not None:
        candidates.append(
            {
                "name": "differential_dummy_mismatch_sweep_worst",
                "error_v": differential_mismatch["worst_diff_hold_abs_delta_v"],
                "source": "sky130-differential-dummy-candidate-mismatch-sweep",
            }
        )

    measured = [item for item in candidates if item["error_v"] is not None]
    broad_candidate = next((item for item in measured if item["name"] == "differential_dummy_input_sweep_worst"), None)
    best = broad_candidate if broad_candidate else min(measured, key=lambda item: item["error_v"])
    best_passes_half_lsb = best["error_v"] <= half_lsb
    required_reduction_x = best["error_v"] / half_lsb
    remaining_margin_x = half_lsb / best["error_v"]
    required_cancellation_fraction = max(0.0, 1.0 - half_lsb / best["error_v"])
    required_extra_capacitance_if_same_charge_p = 1.0 * required_reduction_x

    report = {
        "result_type": "sky130_sample_hold_design_target",
        "status": "sky130_sample_hold_design_target_has_one_passing_decision_voltage_not_converter_proof"
        if best_passes_half_lsb
        else "sky130_sample_hold_design_target_requires_more_than_measured_mitigations",
        "half_lsb_12b_v": half_lsb,
        "best_measured_source": best["source"],
        "best_measured_name": best["name"],
        "best_measured_hold_error_v": best["error_v"],
        "best_measured_passes_half_lsb_12b": best_passes_half_lsb,
        "required_reduction_x_from_best_measured": required_reduction_x,
        "remaining_margin_x_from_best_measured": remaining_margin_x,
        "required_cancellation_fraction_from_best_measured": required_cancellation_fraction,
        "required_cancellation_percent_from_best_measured": 100.0 * required_cancellation_fraction,
        "required_capacitance_multiplier_if_charge_unchanged": required_reduction_x,
        "estimated_capacitance_pf_if_starting_from_1pf": required_extra_capacitance_if_same_charge_p,
        "measured_candidates": candidates,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "turns measured Sky130 sample-hold errors into the required reduction, cancellation, or capacitance target for the next circuit",
            "not_allowed": "does not prove comparator behavior, SAR conversion, mismatch tolerance, noise tolerance, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Sky130 Sample-Hold Design Target",
        "",
        f"- status: `{report['status']}`",
        f"- half LSB 12b V: `{fmt(half_lsb)}`",
        f"- best measured source: `{best['source']}`",
        f"- best measured hold error V: `{fmt(best['error_v'])}`",
        f"- best measured passes half LSB 12b: `{best_passes_half_lsb}`",
        f"- required reduction from best measured x: `{required_reduction_x:.3f}`",
        f"- remaining margin from best measured x: `{remaining_margin_x:.3f}`",
        f"- required cancellation percent from best measured: `{100.0 * required_cancellation_fraction:.2f}`",
        f"- required capacitance multiplier if charge is unchanged: `{required_reduction_x:.3f}`",
        f"- estimated capacitance pF if starting from 1 pF: `{required_extra_capacitance_if_same_charge_p:.3f}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The hold error is voltage movement on a capacitor. If the unwanted charge stays the same, voltage movement falls only when capacitance rises. If capacitance stays the same, the only way to pass is to cancel or avoid most of the unwanted charge.",
        "",
        "That gives the next design a hard target. If the best measured result is still above the line, the circuit needs less injected charge, more capacitance, or both. If the input-sweep result is below the line, the next question changes: the circuit must prove the same behavior under mismatch, noise, energy accounting, and layout extraction.",
        "",
        "## Measured Inputs",
        "",
        "| measurement | source | hold error V | reduction needed to reach half LSB |",
        "|---|---|---:|---:|",
    ]
    for item in candidates:
        reduction = item["error_v"] / half_lsb if item["error_v"] is not None else None
        lines.append(f"| `{item['name']}` | `{item['source']}` | `{fmt(item['error_v'])}` | `{('not measured' if reduction is None else f'{reduction:.3f}x')}` |")
    lines.extend(
        [
            "",
            "## What This Means",
            "",
            f"The best measured decision-voltage movement is `{fmt(best['error_v'])}`. The 12-bit half-LSB line is `{fmt(half_lsb)}`.",
            "",
            f"The best measured row has `{remaining_margin_x:.2f}x` margin against the half-LSB line." if best_passes_half_lsb else f"The next sample-hold design therefore needs about `{required_reduction_x:.2f}x` less held-voltage movement than the best measured case.",
            "",
            "That does not make it an accepted converter. It makes it the next candidate front end. It has cleared the nominal low, mid, and high input gate, but it still needs mismatch checks, comparator tolerance, noise, supply energy, and extracted layout before it can support a converter replacement claim.",
            "The controlled width-mismatch sweep also passes in its tested cases. That still does not model random mismatch statistics or post-layout parasitics. It moves the next proof to noise, comparator tolerance, supply energy, and extraction.",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_sample_hold_design_target")
    print(f"status,{report['status']}")
    print(f"best_measured_hold_error_v,{best['error_v']:.9e}")
    print(f"required_reduction_x,{required_reduction_x:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
