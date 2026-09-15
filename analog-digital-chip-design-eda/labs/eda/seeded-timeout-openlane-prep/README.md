# Seeded timeout OpenLane package

This package is the physical-design input for the model-repaired temporal
timeout benchmark. The repaired source is staged into a disposable OpenLane
design directory; the canonical one-cycle-late defect is never overwritten.

It supports local synthesis, placement, CTS, routing, extracted STA, GDS, DRC,
antenna, XOR, and LVS evidence. It is not commercial signoff or silicon
evidence.
