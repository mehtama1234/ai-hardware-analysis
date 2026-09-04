#!/usr/bin/env python3
"""Turn measured transistor corner margin into an analog/digital policy trace."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SOURCE = EVIDENCE / "sky130-two-phase-transistor-full-pvt.json"
OUT_JSON = EVIDENCE / "sky130-two-phase-transistor-corner-governor-bridge.json"
OUT_MD = EVIDENCE / "sky130-two-phase-transistor-corner-governor-bridge.md"
PY_DIR = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware" / "python"
sys.path.insert(0, str(PY_DIR))
from integrated_scheduler_governor_runtime import govern  # noqa: E402


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    target = float(source["margin_target_v"])
    rows = []
    for row in source["rows"]:
        if float(row["input_diff_mv"]) == 0.0:
            continue
        measured = bool(row.get("measured"))
        magnitude = abs(float(row.get("preamp_diff_before_latch_v", 0.0))) if measured else None
        margin_pass = measured and magnitude >= target
        candidate = int(margin_pass)
        decision, action, reason, next_error = govern(
            sample_valid=1,
            analog_candidate=candidate,
            residual_q8=8 if margin_pass else 255,
            drift_age=1,
            sensitivity_q8=128,
            cumulative_error_q8=0,
        )
        rows.append({
            "corner": row["name"],
            "input_diff_mv": row["input_diff_mv"],
            "measured": measured,
            "preamp_abs_v": magnitude,
            "preamp_margin_target_v": target,
            "margin_pass": margin_pass,
            "analog_candidate": candidate,
            "governor_decision": decision,
            "governor_action": action,
            "governor_reason": reason,
            "next_cumulative_error_q8": next_error,
            "policy": "analog_service" if decision == 1 else "digital_fallback",
        })
    report = {
        "result_type": "sky130_two_phase_transistor_corner_governor_bridge",
        "status": "measured_corner_margin_connected_to_governor",
        "source": str(SOURCE.relative_to(ROOT)),
        "preamp_margin_target_v": target,
        "case_count": len(rows),
        "measured_case_count": sum(r["measured"] for r in rows),
        "analog_service_count": sum(r["policy"] == "analog_service" for r in rows),
        "digital_fallback_count": sum(r["policy"] == "digital_fallback" for r in rows),
        "rows": rows,
        "claim_boundary": {
            "allowed": "the runtime policy refuses measured corners below the preamp margin target",
            "not_allowed": "does not prove a transistor SAR, random mismatch/noise yield, extracted layout, board behavior, or silicon",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Two-Phase Transistor Corner Governor Bridge", "",
        "This report feeds measured transistor corner amplitude into the existing digital governor.", "",
        f"- measured cases: `{report['case_count']}`",
        f"- analog-service decisions: `{report['analog_service_count']}`",
        f"- digital-fallback decisions: `{report['digital_fallback_count']}`",
        f"- preamp margin target: `{target:.6g} V`", "",
        "## First-Principles Reading", "",
        "A comparator sign can remain correct while its differential signal becomes too small for noise, offset, kickback, and latch uncertainty. The governor therefore treats the measured preamp amplitude as an eligibility condition.", "",
        "The nominal and fast/high-supply rows remain eligible in this fixture. The slow/cold/low-supply rows fall back to digital because their measured amplitude is below the handoff target. This is a control decision backed by a circuit measurement, not a claim that the circuit works across PVT.", "",
        "## Refused Claim", "",
        report["claim_boundary"]["not_allowed"], "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"analog_service_count,{report['analog_service_count']}")
    print(f"digital_fallback_count,{report['digital_fallback_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
