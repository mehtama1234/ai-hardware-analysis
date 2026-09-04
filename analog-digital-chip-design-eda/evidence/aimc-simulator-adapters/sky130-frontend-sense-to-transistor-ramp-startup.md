# Sky130 Frontend Sense To Transistor Ramp Startup

- status: `frontend_sense_to_transistor_ramp_startup_passed_not_full_handoff_or_strict_evidence`
- uses measured frontend sense voltage: `True`
- uses Sky130 transistor input stage: `True`
- uses input ramp from common mode: `True`
- uses extracted frontend transient: `False`
- case count: `2`
- measured case count: `2`
- sign pass count: `2`
- output margin pass count: `2`
- minimum abs output diff V: `6.264000000e-04`
- minimum gain V/V: `9.349254`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-sense-to-transistor-ramp-startup.csv`

## First Principle

A steady operating point can hide startup problems. This runner starts both transistor inputs at common-mode, then moves them to the measured frontend sense voltages. It asks whether the input pair can acquire the small difference, not merely hold it after being placed there.

If this passes, the next unsolved object is the extracted frontend coupled into transistor gates during startup. That is closer to the real handoff than the OP and short-hold checks, but it still does not include the extracted frontend transient itself.

## Results

| reset mode | input diff mV | output diff mV | gain V/V | sign preserved | margin pass |
|---|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-0.626400` | `9.349254` | `True` | `True` |
| `reset_pulse` | `0.152971` | `0.626400` | `9.349254` | `True` | `True` |

## Refused Claim

does not prove the extracted frontend transient handoff, latch behavior, SAR conversion, post-layout energy, or accepted converter evidence
