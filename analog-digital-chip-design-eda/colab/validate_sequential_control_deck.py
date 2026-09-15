#!/usr/bin/env python3
"""Validate the opt-in sequential-control deck before a Colab transient."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
import run_sky130_continuous_physical_sar as runner  # noqa: E402


def main() -> int:
    os.environ["AIMC_CONTINUOUS_SEQUENTIAL_CONTROL"] = "1"
    os.environ["AIMC_CONTINUOUS_STATE_PHASE_SAFE"] = "1"
    deck = runner.continuous_deck()
    os.environ["AIMC_CONTINUOUS_TWO_CONTROL"] = "1"
    os.environ["AIMC_CONTINUOUS_STATE_PHASE_SAFE"] = "0"
    two_control_deck = runner.continuous_deck()
    os.environ.pop("AIMC_CONTINUOUS_TWO_CONTROL", None)
    os.environ["AIMC_CONTINUOUS_SPLIT_MSB"] = "1"
    split_deck = runner.continuous_deck()
    os.environ.pop("AIMC_CONTINUOUS_SPLIT_MSB", None)
    os.environ["AIMC_CONTINUOUS_FIXED_DECISIONS"] = "1"
    os.environ.pop("AIMC_CONTINUOUS_SEQUENTIAL_CONTROL", None)
    fixed_deck = runner.continuous_deck()
    os.environ.pop("AIMC_CONTINUOUS_FIXED_DECISIONS", None)
    fixed_pwl_times = []
    for line in fixed_deck.splitlines():
        if line.startswith("VFIX_"):
            fixed_pwl_times.append([float(value) for value in re.findall(r"([0-9]+(?:\.[0-9]+)?)n", line)])
    trial_pulses = re.findall(
        r"VSEQ_TRIAL(\d+) seq_trial\d+ 0 PULSE\(0 1\.8 ([0-9.]+)n 20p 20p ([0-9.]+)n",
        two_control_deck,
    )
    expected_trial_schedule = [(str(bit), 5.0 + bit * 16.0, 14.0) for bit in range(4)]
    checks = {
        "sequential_model": ".model SWSEQ_STATE" in deck,
        "decision_sampler": "SSEQ_STATE1 seq_state1 dec1 seq_clk1 0 SWSEQ_STATE" in deck,
        "held_state_capacitor": "CSEQ_STATE1 seq_state1 0" in deck,
        "voltage_controlled_gate_driver": ("SSEQ_PHI1 gp_dac1 vdd seq_state1 0 SWSEQ_GATE" in deck and "SSEQ_NLO1 gn_dac1 0 seq_inv1 0 SWSEQ_GATE" in deck) or ("SSEQ_PHI1 gp_dac1 vdd seq_logic1 0 SWSEQ_GATE" in deck and "SSEQ_NLO1 gn_dac1 0 seq_logic_inv1 0 SWSEQ_GATE" in deck) or ("SSEQ_PHI1 gp_dac1 vdd seq_p_on1 0 SWSEQ_GATE" in deck and "SSEQ_NLO1 gn_dac1 0 seq_n_on1 0 SWSEQ_GATE" in deck),
        "gate_transition_capacitor": "CSEQ_PGATE1 gp_dac1 0" in deck and "CSEQ_NGATE1 gn_dac1 0" in deck,
        "split_msb_gate_drivers": ("SSEQ_PHI4a gp_dac0a vdd seq_state4 0 SWSEQ_GATE" in split_deck and "SSEQ_PHI4b gp_dac0b vdd seq_state4 0 SWSEQ_GATE" in split_deck) or ("SSEQ_PHI4a gp_dac0a vdd seq_logic4 0 SWSEQ_GATE" in split_deck and "SSEQ_PHI4b gp_dac0b vdd seq_logic4 0 SWSEQ_GATE" in split_deck) or ("SSEQ_PHI4a gp_dac0a vdd seq_p_on4 0 SWSEQ_GATE" in split_deck and "SSEQ_PHI4b gp_dac0b vdd seq_p_on4 0 SWSEQ_GATE" in split_deck),
        "fixed_pwl_timestamps_increasing": bool(fixed_pwl_times) and all(all(a < b for a, b in zip(times, times[1:])) for times in fixed_pwl_times),
        "legacy_behavioral_ngate_absent": "BCONT_NGATE" not in deck and "ECTRL_NGATE" not in deck,
        "two_control_trial_switches": "VSEQ_TRIAL0 seq_trial0 0 PULSE" in two_control_deck and "SSEQ_TRIAL_GP0 gp_dac0 0 seq_trial0 0 SWSEQ_GATE" in two_control_deck,
        "two_control_retention_gating": "BSEQ_RETAIN_CTRL_P1 seq_retain_p1 0" in two_control_deck and "BSEQ_RETAIN_CTRL_N1 seq_retain_n1 0" in two_control_deck,
        "two_control_edge_probes": "trial_gate_p_v" in two_control_deck and "retain_gate_n_v" in two_control_deck,
        "two_control_timing_contract": sorted(
            [(bit, float(start), float(width)) for bit, start, width in trial_pulses]
        ) == expected_trial_schedule and all(
            f"u(0.9-V(seq_trial{bit}))" in two_control_deck for bit in range(4)
        ),
        "two_control_settling_budget": all(
            (float(width) >= 6.7) for _, _, width in trial_pulses
        ),
        "two_control_retention_uses_held_state": "BSEQ_RETAIN_CTRL_P1 seq_retain_p1 0 V={V(seq_state1)*u(0.9-V(seq_trial0))}" in two_control_deck and "BSEQ_RETAIN_CTRL_N1 seq_retain_n1 0 V={V(seq_inv1)*u(0.9-V(seq_trial0))}" in two_control_deck,
    }
    report = {
        "result_type": "sky130_sequential_control_preflight",
        "status": "ready" if all(checks.values()) else "failed",
        "checks": checks,
        "requested_conversion_count": len(runner.CONVERSION_CODES),
        "decision_map": list(runner.CONVERSION_CODES),
        "two_control_schedule": {
            "trial_start_ns": [5.0 + bit * 16.0 for bit in range(4)],
            "break_before_make_ns": float(os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "1.0")),
            "trial_width_ns": max(1.0, 15.0 - float(os.environ.get("AIMC_CONTINUOUS_TWO_CONTROL_DEAD_NS", "1.0"))),
            "period_ns": runner.CONVERSION_PERIOD_NS,
        },
        "deck_sha256": hashlib.sha256(deck.encode()).hexdigest(),
        "claim_boundary": "Structural deck preflight only; no transient, PVT, mismatch, energy, or workload claim.",
    }
    default_output = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-sequential-control-preflight.json"
    output = Path(os.environ.get("AIMC_SEQUENTIAL_PREFLIGHT_OUTPUT", str(default_output)))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
