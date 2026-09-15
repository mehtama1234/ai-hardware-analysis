#!/usr/bin/env python3
"""Check that each captured SAR decision drives exactly its matching DAC bit."""
from __future__ import annotations

import os
import re
import sys

import run_sky130_continuous_physical_sar as runner


def main() -> int:
    os.environ["AIMC_CONTINUOUS_SEQUENTIAL_CONTROL"] = "1"
    os.environ["AIMC_CONTINUOUS_STATE_QUANTIZE"] = "1"
    deck = runner.continuous_deck()
    errors: list[str] = []
    for decision in range(1, 5):
        bit = decision % 4
        capture = f"SSEQ_STATE{decision} seq_state{decision} dec{decision} seq_clk{decision} 0 SWSEQ_STATE"
        if capture not in deck:
            errors.append(f"decision {decision} capture is not connected to dec{decision}")
        for suffix in (("a", "b") if bit == 0 and "gp_dac0a" in deck else ("",)):
            gp = f"SSEQ_PHI{decision}{suffix} gp_dac{bit}{suffix} vdd seq_logic{decision} 0 SWSEQ_GATE"
            gn = f"SSEQ_NHI{decision}{suffix} gn_dac{bit}{suffix} vdd seq_logic{decision} 0 SWSEQ_GATE"
            phase_gp = f"SSEQ_PHI{decision}{suffix} gp_dac{bit}{suffix} vdd seq_p_on{decision} 0 SWSEQ_GATE"
            phase_gn = f"SSEQ_NHI{decision}{suffix} gn_dac{bit}{suffix} vdd seq_p_on{decision} 0 SWSEQ_GATE"
            if (gp not in deck or gn not in deck) and (phase_gp not in deck or phase_gn not in deck):
                errors.append(f"decision {decision} does not drive DAC bit {bit}{suffix}")
    # No sequential driver may cross-drive a different DAC bit.
    for match in re.finditer(r"SSEQ_PHI(\d+)([ab]?) gp_dac(\d+)", deck):
        if int(match.group(1)) % 4 != int(match.group(3)):
            errors.append(f"cross-drive {match.group(0)}")
    report = {
        "result_type": "sequential_bit_mapping_contract",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "claim_boundary": "Static state-to-bit wiring contract only; no transient, PVT, mismatch, energy, or workload claim.",
    }
    print(report)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
