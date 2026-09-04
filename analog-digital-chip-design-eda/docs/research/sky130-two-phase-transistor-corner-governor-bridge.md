# Sky130 Two-Phase Transistor Corner Governor Bridge

This page connects the transistor-level corner measurement to the runtime decision that matters: may this analog path serve a model operation, or must the operation use the digital reference path?

## Result

The bridge reads `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-full-pvt.json` and applies its measured preamp margin to the existing governor:

- target margin: `0.5 mV`
- measured rows above the target: analog eligible in this fixture
- measured rows below the target: digital fallback
- non-convergent rows: digital fallback

The low-supply result is the important finding. At `ss/-20 C/1.62 V`, the `+/-0.2 mV` input produces only about `15.5 uV` of preamp differential. Its polarity is still correct, but the signal is too small to carry an honest analog-service claim after offset, noise, kickback, and latch uncertainty are included. The full matrix also records a non-convergent case; a circuit that cannot produce a result within the run budget is not eligible for analog service.

## Why This Matters

A sign-only test answers whether the circuit points in the right direction. It does not answer whether the next circuit can reliably distinguish that signal. The runtime must carry the physical limit forward, or a model can silently receive a bad analog result at a corner that looked logically correct.

The correct behavior is therefore explicit: reject analog service for that operating point, use the digital reference path, record the reason, and revisit the analog bias or supply policy later.

## Reproduce

```bash
python3 scripts/run_transistor_corner_governor_bridge.py
```

Outputs:

- `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-corner-governor-bridge.json`
- `evidence/aimc-simulator-adapters/sky130-two-phase-transistor-corner-governor-bridge.md`

## Boundary

This proves only that measured deterministic corner margin reaches a digital policy decision. It does not prove random mismatch or noise yield, a full PVT matrix, transistor SAR bit cycling, extracted layout, board performance, or silicon.
