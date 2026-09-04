# Sky130 Polarity Contract Latch/SAR Risk

This page joins the polarity-corrected transistor handoff to the existing latch kickback evidence.

The transistor handoff has enough schematic voltage after the polarity contract. The latch evidence says direction can resolve, but sampled-node kickback is still too large for a 12-bit decision. The next converter stage therefore needs an isolated latch input or equivalent sampled decision network before SAR work can be trusted.

It is an evidence-join page. It does not prove a new latch, a SAR loop, layout, DRC/LVS, noise, offset, or accepted post-layout converter evidence.
