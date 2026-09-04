#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
POLARITY = EVIDENCE / "sky130-polarity-corrected-transistor-handoff.json"
LATCH = EVIDENCE / "sky130-sample-hold-latch-kickback-ngspice.json"
SIZE_SWEEP = EVIDENCE / "sky130-latch-input-size-kickback-sweep.json"
OUT_JSON = EVIDENCE / "sky130-polarity-contract-latch-sar-risk.json"
OUT_MD = EVIDENCE / "sky130-polarity-contract-latch-sar-risk.md"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    polarity = load(POLARITY)
    latch = load(LATCH)
    size = load(SIZE_SWEEP)

    best_output_v = float(polarity["best_setting"]["minimum_abs_polarity_corrected_output_diff_v"])
    target_v = float(polarity["output_margin_target_v"])
    half_lsb_v = float(size["half_lsb_12b_v"])
    best_kickback_v = float(size["best_kickback_v"])
    baseline_kickback_v = float(size["baseline_kickback_v"])
    required_kickback_reduction_x = best_kickback_v / half_lsb_v
    baseline_reduction_to_half_lsb_x = baseline_kickback_v / half_lsb_v
    output_margin_over_target_x = best_output_v / target_v
    output_margin_over_best_kickback_x = best_output_v / best_kickback_v
    latch_resolves_ideal_sample_hold = int(latch["resolved_correct_polarity_count"]) == int(latch["case_count"])
    size_sweep_resolves = all(row.get("resolved_correct_polarity") for row in size["rows"] if not row.get("ngspice_timed_out"))
    kickback_still_blocks = best_kickback_v > half_lsb_v

    blockers = []
    if kickback_still_blocks:
        blockers.append("latch_kickback_above_half_lsb")
    if not latch_resolves_ideal_sample_hold:
        blockers.append("latch_resolution_not_yet_stable")
    if polarity.get("accepted_post_layout_written") is not False:
        blockers.append("unexpected_accepted_evidence")
    blockers.extend(["no_noise_measurement", "no_offset_statistics", "no_sar_bit_cycle", "no_extracted_layout"])

    status = "polarity_contract_ready_for_isolated_latch_design_not_strict" if kickback_still_blocks and latch_resolves_ideal_sample_hold and size_sweep_resolves else "polarity_contract_latch_sar_risk_unresolved"

    return {
        "result_type": "sky130_polarity_contract_latch_sar_risk",
        "status": status,
        "source_polarity_contract": str(POLARITY.relative_to(ROOT)),
        "source_latch_kickback": str(LATCH.relative_to(ROOT)),
        "source_latch_size_sweep": str(SIZE_SWEEP.relative_to(ROOT)),
        "polarity_contract": polarity["polarity_contract"],
        "best_transistor_setting": polarity["best_setting"]["name"],
        "best_polarity_corrected_output_diff_v": best_output_v,
        "output_margin_target_v": target_v,
        "output_margin_over_target_x": output_margin_over_target_x,
        "latch_half_lsb_12b_v": half_lsb_v,
        "baseline_latch_kickback_v": baseline_kickback_v,
        "best_latch_input_width_um": size["best_width_um"],
        "best_latch_kickback_v": best_kickback_v,
        "best_latch_kickback_over_half_lsb_x": required_kickback_reduction_x,
        "baseline_latch_kickback_over_half_lsb_x": baseline_reduction_to_half_lsb_x,
        "transistor_output_margin_over_best_kickback_x": output_margin_over_best_kickback_x,
        "latch_resolves_ideal_sample_hold": latch_resolves_ideal_sample_hold,
        "latch_size_sweep_resolves_all_measured_widths": size_sweep_resolves,
        "kickback_still_blocks_sar_contract": kickback_still_blocks,
        "blockers": blockers,
        "next_circuit_target": {
            "name": "polarity_named_isolated_latch_input",
            "must_preserve": [
                "converter polarity contract",
                "both input signs",
                "at least 0.5 mV corrected preamp margin before latch decision",
                "full latch output resolution",
            ],
            "must_reduce": [
                f"sampled-node differential kickback from {fmt(best_kickback_v)} V to <= {fmt(half_lsb_v)} V",
                f"at least {required_kickback_reduction_x:.3f}x additional kickback reduction from the best width-only latch result",
            ],
            "must_measure_next": [
                "input-referred offset",
                "output noise RMS",
                "kickback after polarity-corrected transistor handoff",
                "decision time",
                "wrong-code risk at the SAR threshold",
            ],
        },
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "claim_boundary": {
            "allowed": "joins the schematic polarity contract to existing latch kickback evidence and names the next isolated latch/SAR target",
            "not_allowed": "does not prove a latch connected to the transistor handoff, does not simulate SAR bit cycling, does not measure noise or offset, and does not create accepted post-layout converter evidence",
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Polarity Contract Latch/SAR Risk",
        "",
        f"- status: `{report['status']}`",
        f"- polarity contract: `{report['polarity_contract']}`",
        f"- best transistor setting: `{report['best_transistor_setting']}`",
        f"- best polarity-corrected output diff V: `{report['best_polarity_corrected_output_diff_v']:.9e}`",
        f"- output margin target V: `{report['output_margin_target_v']:.9e}`",
        f"- output margin over target x: `{report['output_margin_over_target_x']:.6f}`",
        f"- latch half LSB 12b V: `{report['latch_half_lsb_12b_v']:.9e}`",
        f"- best latch kickback V: `{report['best_latch_kickback_v']:.9e}`",
        f"- best latch kickback over half LSB x: `{report['best_latch_kickback_over_half_lsb_x']:.6f}`",
        f"- transistor output margin over best kickback x: `{report['transistor_output_margin_over_best_kickback_x']:.6f}`",
        f"- latch resolves ideal sample-hold: `{report['latch_resolves_ideal_sample_hold']}`",
        f"- kickback still blocks SAR contract: `{report['kickback_still_blocks_sar_contract']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "The transistor handoff now has a named sign: positive model value is the negative raw preamp output difference. That is enough for a schematic sign-map, but it is not enough for a converter.",
        "",
        "A latch is allowed to decide only if it reads the signed voltage without changing the stored value too much. The existing latch evidence resolves direction, but its clock pushes charge back into the sampled nodes. That kickback is larger than the half-LSB line for a 12-bit decision.",
        "",
        "So the next converter question is not only whether the latch output flips to rail. It is whether the latch can decide after the polarity contract while keeping the sampled value inside the error budget that the model will see.",
        "",
        "## Evidence Join",
        "",
        "| object | measured fact | reading |",
        "|---|---:|---|",
        f"| transistor handoff | `{report['best_polarity_corrected_output_diff_v']:.9e}` V corrected output | enough schematic margin after named polarity contract |",
        f"| latch size sweep | `{report['best_latch_kickback_v']:.9e}` V best kickback | still `{report['best_latch_kickback_over_half_lsb_x']:.3f}x` above half-LSB |",
        f"| latch resolution | `{report['latch_resolves_ideal_sample_hold']}` | direction can resolve in the older sample-hold fixture |",
        "",
        "## Next Circuit Target",
        "",
        f"The next circuit target is `{report['next_circuit_target']['name']}`.",
        "",
        "It must preserve:",
    ]
    for item in report["next_circuit_target"]["must_preserve"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("It must reduce:")
    for item in report["next_circuit_target"]["must_reduce"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("It must measure next:")
    for item in report["next_circuit_target"]["must_measure_next"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blockers", ""])
    for item in report["blockers"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print("sky130_polarity_contract_latch_sar_risk")
    print(f"status,{report['status']}")
    print(f"best_transistor_setting,{report['best_transistor_setting']}")
    print(f"output_margin_over_target_x,{report['output_margin_over_target_x']:.6f}")
    print(f"best_latch_kickback_over_half_lsb_x,{report['best_latch_kickback_over_half_lsb_x']:.6f}")
    print(f"kickback_still_blocks_sar_contract,{report['kickback_still_blocks_sar_contract']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
