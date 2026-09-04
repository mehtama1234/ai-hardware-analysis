# Sky130 Extracted Frontend To Transistor Gate Startup

- status: `extracted_frontend_to_transistor_assisted_gate_startup_failed`
- uses extracted frontend netlist: `True`
- uses Sky130 transistor input stage: `True`
- uses assisted gate startup: `True`
- uses full free gate handoff: `False`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- sign pass count: `1`
- output margin pass count: `1`
- minimum abs output diff V: `1.170000000e-04`
- minimum sample-to-sense transfer ratio: `3.862745`
- minimum sense-to-gate transfer ratio: `0.012257`
- minimum gate-to-output gain V/V: `7.940741`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-extracted-frontend-to-transistor-gate-startup.csv`

## First Principle

The open problem is no longer whether a small voltage can be amplified. We already measured that. The open problem is whether the extracted frontend can touch real transistor gates without losing the tiny sign or making the transient run unusable.

This runner keeps the extracted frontend in the same SPICE deck as the Sky130 input pair. It also gives the gate nodes a weak startup guide toward the measured sense voltages. That makes this an assisted handoff test. It is useful because it separates two questions: can the loaded frontend still produce the right sign, and can the real input pair still turn that loaded gate difference into output margin?

A pass here would not finish the converter. It would only say the next gap is full free gate startup. A fail here would say the problem is already visible before latch or SAR logic enter the circuit.

## Results

| reset mode | input diff mV | sense diff uV | gate diff uV | output diff mV | sign preserved | margin pass |
|---|---:|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-669.000000` | `-8.200000` | `0.117000` | `False` | `False` |
| `reset_pulse` | `0.152971` | `-591.000000` | `67.500000` | `0.536000` | `True` | `True` |

## Refused Claim

does not prove the full free extracted-frontend-to-transistor handoff, latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence
