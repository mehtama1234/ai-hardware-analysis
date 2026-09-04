# AIHWKIT Target Noise Sensitivity

This page reviews whether the 10-bit input and 12-bit output AIHWKIT target still works when output noise is not zero.

The earlier target page showed the precision needed to pass. The cost page showed that this precision is expensive. This page asks whether the target is also fragile.

## Object

The object is the same held-out MatMul family used by the current-tile replay and converter target.

The converter resolution is held fixed at the target setting. Only the output-noise value changes.

## Reading Rule

Output noise is not a detail after the fact. It is part of the value that the digital system receives.

If the target passes only when output noise is zero, then the target is not yet a circuit claim. If it passes with small nonzero noise, that nonzero value becomes a concrete budget for the next circuit proof.

## Decision Boundary

A passing nonzero-noise target can move to circuit-level design work.

A zero-only target stays a simulator target and keeps digital fallback as the default.

The generated evidence below shows the noise settings and held-out residuals.
