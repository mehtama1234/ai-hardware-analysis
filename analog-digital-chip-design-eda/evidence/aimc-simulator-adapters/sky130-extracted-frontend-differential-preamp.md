# Sky130 Extracted Frontend Differential Preamp

- status: `differential_preamp_handoff_failed`
- uses extracted frontend netlist: `True`
- uses Sky130 differential preamp: `True`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- sign pass count: `2`
- output margin pass count: `0`
- minimum abs preamp output diff V: `5.650000000e-05`
- minimum sample-to-sense transfer ratio: `0.041830`
- minimum sense-to-preamp gain V/V: `8.188406`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-extracted-frontend-differential-preamp.csv`

## First Principle

A differential preamp spends current to make the small difference visible before a hard decision. The frontend should only have to move transistor gates. The preamp then converts the small gate-voltage difference into a larger drain-voltage difference.

This is the first active version after passive gate coupling and a source follower both failed. It asks whether a simple biased pair is enough to make both signs survive at the preamp output.

## Results

| reset mode | input diff mV | sense diff uV | preamp output diff mV | sign preserved | margin pass |
|---|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-6.900000` | `-0.056500` | `True` | `False` |
| `reset_pulse` | `0.152971` | `6.400000` | `0.059300` | `True` | `False` |

## Refused Claim

does not prove latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence
