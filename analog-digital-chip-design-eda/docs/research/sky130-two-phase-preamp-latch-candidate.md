# Sky130 Two-Phase Preamp-Then-Latch Candidate

This page is generated from a Sky130 ngspice fixture that lets a resistor-load preamp form an internal difference before enabling the regenerative latch.

The intent is to separate the quiet gain phase from the latch regeneration phase. The candidate is useful only if both signs resolve and sampled-node kickback falls below the half-LSB line.

It is schematic candidate evidence only. It is not noise, offset, SAR, extracted layout, DRC/LVS, or accepted post-layout converter evidence.
