# Sky130 Sampled Internal Decision-Cap Latch Candidate

This page is generated from a Sky130 ngspice fixture that copies the sampled value onto small internal decision capacitors before latch regeneration.

The intent is to let the latch read an internal node while protecting the original sampled nodes from clock kickback. The candidate is useful only if both signs resolve and sampled-node kickback falls below the half-LSB line.

It is schematic candidate evidence only. It is not noise, offset, SAR, extracted layout, DRC/LVS, or accepted post-layout converter evidence.
