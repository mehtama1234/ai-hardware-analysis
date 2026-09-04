#!/usr/bin/env python3
"""Sweep a bounded wrong-code proxy around the passing two-phase latch fixture."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE = EVIDENCE / "sky130-two-phase-preamp-latch-candidate.json"
OUT_JSON = EVIDENCE / "sky130-two-phase-offset-noise-sweep.json"
OUT_MD = EVIDENCE / "sky130-two-phase-offset-noise-sweep.md"


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row.get("ngspice_returncode") == 0]
    signal_v = min(abs(float(row["preamp_diff_before_latch_v"])) for row in rows)
    measured_kickback_v = max(float(row["sampled_diff_kickback_v"]) for row in rows)
    half_lsb_v = float(source["half_lsb_12b_v"])

    offset_values_v = [0.0, 50e-6, 100e-6, 150e-6, 200e-6]
    noise_values_v = [0.0, 25e-6, 50e-6, 100e-6]
    kickback_multipliers = [0.5, 1.0, 2.0, 5.0]
    cases: list[dict[str, Any]] = []
    for offset_v, noise_rms_v, kickback_multiplier in itertools.product(offset_values_v, noise_values_v, kickback_multipliers):
        kickback_v = measured_kickback_v * kickback_multiplier
        # Three-sigma noise is used as a conservative wrong-code proxy. This
        # is a budget calculation, not a claim that circuit noise was measured.
        remaining_margin_v = signal_v - abs(offset_v) - 3.0 * noise_rms_v - kickback_v
        cases.append(
            {
                "offset_v": offset_v,
                "noise_rms_v": noise_rms_v,
                "kickback_multiplier": kickback_multiplier,
                "kickback_v": kickback_v,
                "remaining_margin_v": remaining_margin_v,
                "wrong_code_proxy_pass": remaining_margin_v > 0.0,
                "kickback_below_half_lsb": kickback_v <= half_lsb_v,
            }
        )

    passing = [row for row in cases if row["wrong_code_proxy_pass"]]
    max_offset_noise_pass = max(
        (row for row in cases if row["wrong_code_proxy_pass"]),
        key=lambda row: (row["offset_v"] + 3.0 * row["noise_rms_v"], -row["kickback_multiplier"]),
        default=None,
    )
    report = {
        "result_type": "sky130_two_phase_offset_noise_sweep",
        "status": "wrong_code_proxy_swept_not_circuit_noise_proof",
        "source_two_phase_candidate": str(SOURCE.relative_to(ROOT)),
        "source_measured_signal_v": signal_v,
        "source_measured_kickback_v": measured_kickback_v,
        "half_lsb_12b_v": half_lsb_v,
        "offset_values_v": offset_values_v,
        "noise_values_rms_v": noise_values_v,
        "kickback_multipliers": kickback_multipliers,
        "case_count": len(cases),
        "passing_case_count": len(passing),
        "pass_fraction": len(passing) / len(cases),
        "worst_remaining_margin_v": min(row["remaining_margin_v"] for row in cases),
        "largest_passing_offset_plus_3sigma_noise_v": (
            max_offset_noise_pass["offset_v"] + 3.0 * max_offset_noise_pass["noise_rms_v"]
            if max_offset_noise_pass
            else None
        ),
        "cases": cases,
        "claim_boundary": {
            "allowed": "computes a conservative wrong-code margin proxy around measured two-phase schematic values",
            "not_allowed": "does not measure transistor noise, offset distributions, mismatch, SAR bit cycling, extracted parasitics, or accepted converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    worst = min(cases, key=lambda row: row["remaining_margin_v"])
    lines = [
        "# Sky130 Two-Phase Offset And Noise Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- measured pre-latch signal V: `{signal_v:.9e}`",
        f"- measured kickback V: `{measured_kickback_v:.9e}`",
        f"- half-LSB V: `{half_lsb_v:.9e}`",
        f"- cases: `{len(cases)}`",
        f"- wrong-code proxy passing cases: `{len(passing)}`",
        f"- pass fraction: `{len(passing) / len(cases):.3f}`",
        f"- worst remaining margin V: `{worst['remaining_margin_v']:.9e}`",
        "",
        "## First-Principles Reading",
        "",
        "The latch does not know whether an error came from offset, random noise, or clock kickback. It only sees the remaining distance between the intended differential signal and the decision boundary. This sweep subtracts the absolute offset, three standard deviations of a supplied noise assumption, and the measured kickback multiplier from the measured pre-latch signal.",
        "",
        "This is a wrong-code proxy. It is useful for sizing the next experiment, but it is not a measurement of offset or noise.",
        "",
        "## Worst Case",
        "",
        f"- offset: `{worst['offset_v']:.9e}` V",
        f"- noise RMS: `{worst['noise_rms_v']:.9e}` V",
        f"- kickback multiplier: `{worst['kickback_multiplier']:.3f}`",
        f"- remaining margin: `{worst['remaining_margin_v']:.9e}` V",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_phase_offset_noise_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"worst_remaining_margin_v,{report['worst_remaining_margin_v']:.9e}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
