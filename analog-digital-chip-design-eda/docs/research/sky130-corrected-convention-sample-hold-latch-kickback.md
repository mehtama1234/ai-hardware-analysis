# Sky130 Corrected-Convention Sample-Hold Latch Kickback

The clocked latch output convention is now named, but that does not prove the latch can be attached to sampled analog nodes.

This page appends the coupled ngspice evidence. The circuit reconnects the latch to the sample-hold nodes, applies the corrected `outp - outn` output definition, and measures whether latch evaluation changes the sampled differential voltage.
