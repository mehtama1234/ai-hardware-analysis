# Sky130 Source-Follower Isolated Latch Candidate

This page is generated from a Sky130 ngspice fixture that inserts source-follower buffers between the sampled nodes and the clocked latch input pair.

The intent is to reduce latch kickback by making the sampled nodes drive only follower gates. The candidate is useful only if both signs resolve and sampled-node kickback falls below the half-LSB line.

It is schematic candidate evidence only. It is not noise, offset, SAR, extracted layout, DRC/LVS, or accepted post-layout converter evidence.
