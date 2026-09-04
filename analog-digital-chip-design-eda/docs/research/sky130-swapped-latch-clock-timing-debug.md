# Sky130 Swapped Latch Clock Timing Debug

The latch-alone polarity fix is not enough by itself. The next smaller question is whether the same corrected mapping still works when the latch clock is moved.

This page appends the measured ngspice evidence. The important boundary is that sampled nodes are still removed, so this is a latch timing and sign-convention check, not a coupled-kickback proof.
