# Sky130 Two-Phase Transistor Corner Sweep

This page summarizes the three-corner latch-free transistor preamp sweep. The machine-readable source is `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-corner-sweep.json`.

## Result

- Nine cases completed with zero timeouts.
- All six nonzero cases preserved polarity.
- All three zero-input cases measured a balanced preamp.
- The nominal `tt/25 C/1.8 V` corner produced about `0.973 mV` at `+/-0.2 mV` input.
- The `ss/-20 C/1.62 V` corner produced only about `15.5 uV`, far below the `0.5 mV` handoff target.
- The `ff/85 C/1.98 V` corner produced about `1.638 mV` at `+/-0.2 mV` input.

## First-Principles Reading

Polarity is necessary but not sufficient. The latch needs amplitude margin, and transistor gain changes with process, supply, and temperature. The slow, cold, low-supply corner keeps the sign while losing almost all useful differential amplitude. It must be rejected or assigned a separate digital fallback policy.

## Next Gate

Run the full declared PVT matrix and device mismatch sweep. Either redesign the isolation/preamp bias for the low-supply corner or make the runtime governor refuse analog service there. Then add transistor noise at each accepted operating point.

## Refused Claim

This result does not prove random noise, mismatch distributions, full PVT coverage, SAR bit cycling, extracted layout, or accepted converter evidence.
