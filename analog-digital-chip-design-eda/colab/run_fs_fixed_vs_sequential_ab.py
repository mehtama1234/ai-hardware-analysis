#!/usr/bin/env python3
"""Compare fixed-decision and sequential-control runs at one Sky130 corner."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_sky130_continuous_physical_sar.py"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"


def run_case(name: str, extra: dict[str, str]) -> dict:
    env = os.environ.copy()
    env.update({
        "AIMC_SKY130_CORNER": "fs",
        "AIMC_CONTINUOUS_REFERENCE_PROFILE": "0.6,0.695,0.65,0.7808133,0.89247035",
        "AIMC_CONTINUOUS_SWAP_LATCH_INPUTS": "1",
        "AIMC_CONTINUOUS_INITIAL_DECISION_RESET": "1",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "1",
        "AIMC_CONTINUOUS_PWL_RISE_NS": "0.2",
        "AIMC_CONTINUOUS_OUTPUT_STEM": f"colab-fs-ab-{name}",
    })
    env.update(extra)
    proc = subprocess.run(["python3", str(RUNNER)], cwd=ROOT, env=env,
                          capture_output=True, text=True, check=False)
    artifact = EVIDENCE / f"colab-fs-ab-{name}.json"
    report = None
    if artifact.exists():
        report = json.loads(artifact.read_text(encoding="utf-8"))
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-12000:],
        "stderr": proc.stderr[-12000:],
        "artifact": str(artifact),
        "report": report,
    }


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bootstrap = ROOT / "colab" / "bootstrap_continuous_sar.py"
    preflight = subprocess.run(["python3", str(bootstrap)], cwd=ROOT,
                               capture_output=True, text=True, check=False)
    if preflight.returncode != 0:
        raise SystemExit(f"Sky130 bootstrap failed: {preflight.stderr[-2000:]}")
    fixed = run_case("fixed", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "1",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "0",
    })
    sequential = run_case("sequential", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD": "0.3",
        "AIMC_CONTINUOUS_STATE_CAPTURE_DELAY_NS": "1.0",
        "AIMC_CONTINUOUS_STATE_CAPTURE_WIDTH_NS": "0.5",
        "AIMC_CONTINUOUS_STATE_CAPTURE_RAW": "1",
        "AIMC_CONTINUOUS_STATE_GATE_CAP": "2p",
        "AIMC_CONTINUOUS_STATE_HOLD_CAP": "10p",
        "AIMC_CONTINUOUS_STATE_HOLD_RESISTOR": "1T",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "0",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
        "AIMC_CONTINUOUS_STATE_PHASE_SAFE": "1",
        "AIMC_CONTINUOUS_STATE_RESTORE_LATCH": "1",
        "AIMC_CONTINUOUS_STATE_PULSE_RESTORE": "1",
    })
    fixed_state = run_case("fixed-state", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_SEQUENTIAL_FIXED_STATES": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD": "0.3",
        "AIMC_CONTINUOUS_STATE_PHASE_SAFE": "1",
        "AIMC_CONTINUOUS_STATE_RESTORE_LATCH": "1",
        "AIMC_CONTINUOUS_STATE_PULSE_RESTORE": "1",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "0",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
    })
    direct = run_case("direct", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD": "0.3",
        "AIMC_CONTINUOUS_STATE_CAPTURE_DELAY_NS": "1.0",
        "AIMC_CONTINUOUS_STATE_CAPTURE_WIDTH_NS": "0.5",
        "AIMC_CONTINUOUS_STATE_GATE_CAP": "2p",
        "AIMC_CONTINUOUS_STATE_HOLD_CAP": "10p",
        "AIMC_CONTINUOUS_STATE_HOLD_RESISTOR": "1T",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "1",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
        "AIMC_CONTINUOUS_STATE_PHASE_SAFE": "1",
        "AIMC_CONTINUOUS_STATE_DIRECT_GATES": "1",
    })
    same_mapping = run_case("same-mapping", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_SEQUENTIAL_FIXED_STATES": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD": "0.3",
        "AIMC_CONTINUOUS_STATE_PHASE_SAFE": "1",
        "AIMC_CONTINUOUS_STATE_RESTORE_LATCH": "1",
        "AIMC_CONTINUOUS_STATE_PULSE_RESTORE": "1",
        "AIMC_CONTINUOUS_STATE_ONE_PHASE_AHEAD": "0",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "0",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
    })
    two_control = run_case("two-control", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE_THRESHOLD": "0.9",
        "AIMC_CONTINUOUS_STATE_CAPTURE_DELAY_NS": "3.0",
        "AIMC_CONTINUOUS_STATE_CAPTURE_WIDTH_NS": "2.0",
        "AIMC_CONTINUOUS_STATE_CAPTURE_RAW": "1",
        "AIMC_CONTINUOUS_REFERENCE_PROFILE": "1.10,1.40,1.10,1.40,1.75",
        "AIMC_CONTINUOUS_STATE_GATE_CAP": "2p",
        "AIMC_CONTINUOUS_STATE_HOLD_CAP": "10p",
        "AIMC_CONTINUOUS_STATE_HOLD_RESISTOR": "1T",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "0",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
        "AIMC_CONTINUOUS_TWO_CONTROL": "1",
    })
    two_control_fixed_state = run_case("two-control-fixed-state", {
        "AIMC_CONTINUOUS_FIXED_DECISIONS": "0",
        "AIMC_CONTINUOUS_SEQUENTIAL_CONTROL": "1",
        "AIMC_CONTINUOUS_SEQUENTIAL_FIXED_STATES": "1",
        "AIMC_CONTINUOUS_STATE_QUANTIZE": "1",
        "AIMC_CONTINUOUS_STATE_PHASE_SAFE": "0",
        "AIMC_CONTINUOUS_STATE_ONE_PHASE_AHEAD": "0",
        "AIMC_CONTINUOUS_SAMPLE_RESET": "0",
        "AIMC_CONTINUOUS_SWITCHED_HANDOFF": "0",
        "AIMC_CONTINUOUS_TWO_CONTROL": "1",
    })
    summary = {
        "result_type": "sky130_fs_fixed_vs_sequential_ab",
        "corner": "fs",
        "status": "completed",
        "cases": {"fixed": fixed, "sequential": sequential, "fixed_state": fixed_state, "direct": direct, "same_mapping": same_mapping, "two_control": two_control, "two_control_fixed_state": two_control_fixed_state},
        "preflight": preflight.stdout[-12000:],
        "claim_boundary": "Same-corner A/B diagnostic only; no converter, PVT, mismatch, energy, or workload authorization.",
    }
    out = Path(os.environ.get("AIMC_FS_AB_OUTPUT", "/content/sky130-fs-ab-comparison.json"))
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "output": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
