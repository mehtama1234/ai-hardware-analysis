#!/usr/bin/env python3
"""Static contract check for generated continuous-SAR decks.

This does not run ngspice. It catches malformed corner selection, split-MSB
connectivity, and accidental ideal control edges before a Colab run.
"""
from __future__ import annotations

import os
import re

from run_sky130_continuous_physical_sar import continuous_deck


def main() -> int:
    deck = continuous_deck()
    corner = os.environ.get("AIMC_SKY130_CORNER", "tt").lower()
    checks = {
        "corner_section": bool(re.search(r"\.lib\s+\"[^\"]+\"\s+" + re.escape(corner) + r"\b", deck)),
        "split_cap_a": "CDAC0A top db0a" in deck,
        "split_cap_b": "CDAC0B top db0b" in deck,
        "split_gate_a": "gp_dac0a" in deck and "gn_dac0a" in deck,
        "split_gate_b": "gp_dac0b" in deck and "gn_dac0b" in deck,
        # The sequential and one-conversion diagnostic decks legitimately
        # contain fewer control edges than the five-conversion campaign. The
        # invariant is that finite PWL controls are present when requested,
        # not a fixed count tied to one campaign size.
        "finite_pwl_controls": (os.environ.get("AIMC_CONTINUOUS_PWL_RISE_NS", "0") == "0") or deck.count("pwl(time") > 0,
        "no_ideal_time_steps": "u(time-" not in deck,
    }
    print(checks)
    if not all(checks.values()):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
