# Sky130 Extracted Frontend To Transistor Gate Startup

This page adds the next measured rung between the passing direct gate-ramp check and the failing full real-transistor handoff.

The question is simple: if the extracted frontend is present in the same SPICE deck as real Sky130 input transistors, and the gate nodes are started gently instead of left to the hardest free transient, does the small sign still reach the transistor output?

This is useful evidence, but it is not final evidence. It uses assisted gate startup. The full converter still needs an unassisted extracted-frontend handoff, latch decision, SAR loop, energy, latency, area, DRC/LVS, and strict accepted payload.
