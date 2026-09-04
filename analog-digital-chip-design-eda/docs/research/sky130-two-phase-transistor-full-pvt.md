# Sky130 Two-Phase Transistor Full PVT Matrix

This page reports an independent `3 process x 3 temperature x 3 supply` matrix at the latch-free preamp boundary. It is the next step after the earlier three diagonal corners.

## Acceptance Rule

For `+/-0.2 mV` input differences, the preamp must preserve polarity and produce at least `0.5 mV` differential magnitude before latch fire. A polarity pass without amplitude margin is not an analog-service pass.

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-full-pvt.json`.

## Reproduce

```bash
python3 scripts/run_two_phase_transistor_full_pvt.py
```

## Boundary

This matrix measures deterministic schematic behavior across independent process, temperature, and supply settings. It does not prove random mismatch or noise yield, SAR conversion, extracted layout, board performance, or silicon.
