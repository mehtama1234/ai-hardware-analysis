# Sky130 Isolated Latch Debug Ladder

This page is generated from the three failed isolated-latch candidate runs.

The source-follower, sampled-decision-capacitor, and two-phase preamp/latch branches all timed out before producing useful circuit measurements. This page turns those failures into a smaller debug sequence: preamp alone, latch alone from measured voltages, clock timing, coupled kickback, and SAR threshold wrong-code risk.

It is a debug plan, not a circuit proof, not SAR evidence, and not accepted post-layout converter evidence.
