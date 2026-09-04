# Sky130 Switched-Capacitor DAC

This page measures the first capacitor charge-redistribution boundary for the SAR converter. A binary-weighted array is sampled, its bottom plates are switched to the reference or ground, and the top-plate voltage is measured after redistribution.

The first fixture uses ideal switch models. That isolates the capacitor law and code-dependent settling, but it is not yet transistor-switch evidence. The current six-code run measures every code, but fails the half-LSB top-plate target; it is therefore not accepted as a DAC for the SAR loop.

## Reproduce

```bash
python3 scripts/run_sky130_switched_capacitor_dac.py
```

The machine-readable result is `evidence/aimc-simulator-adapters/sky130-switched-capacitor-dac.json`.

## Boundary

This is a measured capacitor-array boundary. It does not prove switch resistance, charge injection, capacitor mismatch, reference loading, comparator coupling, SAR conversion, extracted layout, or silicon.
