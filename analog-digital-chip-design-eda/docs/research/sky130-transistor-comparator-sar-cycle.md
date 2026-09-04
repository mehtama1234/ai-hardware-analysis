# Sky130 Transistor Comparator SAR Cycle

This page reports the first sequential SAR loop that uses the Sky130 transistor preamp/latch as its comparison primitive.

For each bit, the controller forms a trial code, computes the signed difference between the input and the trial threshold, runs ngspice on the transistor comparator, reads the regenerated output, and retains or clears the bit.

The first DAC threshold is numerical and ideal. It is deliberately separated from the transistor comparator result so the report does not claim a capacitor-DAC implementation that has not been simulated. The current run is incomplete: timeout and wrong-code results keep this primitive rejected for converter use.

## Reproduce

```bash
python3 scripts/run_sky130_transistor_comparator_sar_cycle.py
```

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-transistor-comparator-sar-cycle.json`.

## Boundary

This is transistor-comparator-in-the-loop evidence. It does not prove capacitor-DAC settling, mismatch, noise yield, extracted layout, board behavior, or silicon.
