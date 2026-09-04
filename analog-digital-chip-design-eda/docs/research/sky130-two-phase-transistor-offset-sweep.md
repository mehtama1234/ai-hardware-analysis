# Sky130 Two-Phase Transistor Offset Sweep

This page summarizes a deterministic input-threshold sweep of the two-phase transistor preamp/latch fixture. The machine-readable source is `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-offset-sweep.json`.

## Result

- Five signed input differentials were requested: `-0.2`, `-0.1`, `0`, `+0.1`, and `+0.2 mV`.
- All five cases completed with zero timeouts, using a `20 ps` offset-only timestep and stopping before latch regeneration.
- The zero-input case measured exactly zero preamp differential in this balanced fixture.
- All four nonzero cases preserved the expected preamp polarity.
- The measured sweep brackets a preamp zero crossing at `0 mV`.

## First-Principles Reading

Offset is the input value at which the differential chain changes sign. A threshold sweep is stronger than assuming an offset value because it exposes polarity, output magnitude, and simulator runability at the same time. The latch-free boundary matters: an exactly balanced preamp can be measured without asking regenerative positive feedback to choose a side.

## Next Gate

Make the zero-input operating point converge, then repeat the sweep across process, voltage, and temperature corners. Add small-signal transistor noise at the converged operating point and combine its input-referred RMS value with the measured threshold distribution.

## Refused Claim

This result does not prove random noise, mismatch distributions, corner coverage, SAR bit cycling, extracted layout, or accepted converter evidence.
