#!/usr/bin/env python3
"""Connect the two-phase comparator margin to a deterministic 12-bit SAR cycle."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE = EVIDENCE / "sky130-two-phase-preamp-latch-candidate.json"
NOISE_SWEEP = EVIDENCE / "sky130-two-phase-offset-noise-sweep.json"
OUT_JSON = EVIDENCE / "sky130-two-phase-sar-bit-cycle.json"
OUT_MD = EVIDENCE / "sky130-two-phase-sar-bit-cycle.md"


def sar_trace(value: float, bits: int, error: float) -> tuple[int, list[dict[str, Any]]]:
    code = 0
    trace: list[dict[str, Any]] = []
    denominator = (1 << bits) - 1
    for decision, bit in enumerate(reversed(range(bits)), start=1):
        trial = code | (1 << bit)
        threshold = trial / denominator
        observed = value + error
        accepted = observed >= threshold
        if accepted:
            code = trial
        trace.append(
            {
                "decision": decision,
                "bit": bit,
                "trial_code": trial,
                "threshold": threshold,
                "observed": observed,
                "accepted": accepted,
            }
        )
    return code, trace


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    proxy = json.loads(NOISE_SWEEP.read_text(encoding="utf-8"))
    bits = 12
    denominator = (1 << bits) - 1
    selected_codes = [0, 1, 2, 127, 128, 1023, 1024, 2047, 2048, 3071, 3072, 4093, 4094, 4095]
    values = []
    for code in selected_codes:
        center = code / denominator
        values.append((f"code_{code}_below", max(0.0, center - 1e-6), code))
        values.append((f"code_{code}_above", min(1.0, center + 1e-6), code))

    offsets = [0.0, 100e-6, 200e-6]
    noises = [0.0, 50e-6, 100e-6]
    kickbacks = [0.0, float(source["worst_sampled_diff_kickback_v"]), float(source["worst_sampled_diff_kickback_v"]) * 5.0]
    disturbance_signs = [-1.0, 1.0]
    cases: list[dict[str, Any]] = []
    for name, value, expected_code in values:
        for offset, noise, kickback, disturbance_sign in itertools.product(offsets, noises, kickbacks, disturbance_signs):
            # Worst-case signed disturbance. The purpose is a deterministic
            # boundary test, not a random-noise performance estimate.
            error = disturbance_sign * (offset + 3.0 * noise + kickback)
            actual_code, trace = sar_trace(value, bits, error)
            cases.append(
                {
                    "name": name,
                    "value": value,
                    "expected_code": expected_code,
                    "offset_v": offset,
                    "noise_rms_v": noise,
                    "kickback_v": kickback,
                    "disturbance_sign": disturbance_sign,
                    "error_v": error,
                    "actual_code": actual_code,
                    "comparison_count": len(trace),
                    "bit_trace": trace,
                    "wrong_code_proxy_pass": actual_code == expected_code,
                }
            )

    passing = [case for case in cases if case["wrong_code_proxy_pass"]]
    report = {
        "result_type": "sky130_two_phase_sar_bit_cycle",
        "status": "sar_12_comparison_wrong_code_proxy_swept_not_transistor_sar_proof",
        "source_two_phase_candidate": str(SOURCE.relative_to(ROOT)),
        "source_offset_noise_proxy": str(NOISE_SWEEP.relative_to(ROOT)),
        "bits": bits,
        "comparison_count_per_case": bits,
        "critical_code_count": len(selected_codes),
        "case_count": len(cases),
        "passing_case_count": len(passing),
        "wrong_code_count": len(cases) - len(passing),
        "pass_fraction": len(passing) / len(cases),
        "maximum_error_v_tested": max(case["error_v"] for case in cases),
        "worst_failed_case": next((case for case in cases if not case["wrong_code_proxy_pass"]), None),
        "claim_boundary": {
            "allowed": "connects measured two-phase comparator margin to a deterministic 12-comparison SAR wrong-code proxy",
            "not_allowed": "does not prove a transistor-level capacitor DAC, comparator noise, mismatch, reference settling, extracted SAR layout, or accepted converter evidence",
        },
        "cases": cases,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Two-Phase SAR Bit Cycle",
        "",
        f"- status: `{report['status']}`",
        f"- bits: `{bits}`",
        f"- comparisons per case: `{bits}`",
        f"- critical code points: `{len(selected_codes)}`",
        f"- cases: `{len(cases)}`",
        f"- wrong-code proxy passes: `{len(passing)}`",
        f"- wrong-code proxy failures: `{len(cases) - len(passing)}`",
        f"- pass fraction: `{len(passing) / len(cases):.3f}`",
        f"- maximum tested error: `{max(case['error_v'] for case in cases):.9e}` V",
        "",
        "## What This Tests",
        "",
        "Each case executes exactly twelve sequential decisions, from the most significant bit to the least significant bit. The test concentrates on code transitions where a small analog error can change the result. Offset, three-sigma noise, and kickback are combined as a worst-case signed disturbance.",
        "",
        "The current sweep is a deterministic wrong-code proxy. It connects the measured two-phase signal and kickback to the SAR algorithm, but it does not turn assumed offset/noise values into circuit measurements.",
        "",
        "## Next Gate",
        "",
        "Replace the proxy disturbance with a transistor-level comparator and capacitor-DAC loop, then repeat the same critical-transition trace with reference settling, mismatch, noise, and conversion time recorded.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("sky130_two_phase_sar_bit_cycle")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"passing_case_count,{report['passing_case_count']}")
    print(f"wrong_code_count,{report['wrong_code_count']}")
    print(f"json,{OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
