# Sky130 Frontend Sense To Transistor Short Transient

- status: `frontend_sense_to_transistor_short_transient_passed_not_full_handoff_or_strict_evidence`
- uses measured frontend sense voltage: `True`
- uses Sky130 transistor input stage: `True`
- uses OP initial conditions: `True`
- uses extracted frontend transient: `False`
- case count: `2`
- measured case count: `2`
- sign pass count: `2`
- output margin pass count: `2`
- minimum abs output diff V: `6.300000000e-04`
- minimum output retention ratio: `1.021732`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-sense-to-transistor-short-transient.csv`

## First Principle

The OP handoff proves a static point. The full handoff asks for a moving extracted frontend and transistor stage together. This short transient sits between them: it starts the transistor pair at the measured OP state and asks whether the output sign and margin survive a small time step.

If this passes, the transistor pair can hold the measured frontend sense voltage dynamically once it is already at the right operating point. The remaining hard problem is then startup and coupling from the extracted frontend into that operating point.

## Results

| reset mode | input diff mV | output diff mV | retention | sign preserved | margin pass |
|---|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-0.630000` | `1.021732` | `True` | `True` |
| `reset_pulse` | `0.152971` | `0.630000` | `1.021732` | `True` | `True` |

## Refused Claim

does not prove the full extracted-frontend transient handoff, latch behavior, SAR conversion, post-layout energy, or accepted converter evidence
