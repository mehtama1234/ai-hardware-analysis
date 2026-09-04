# Sky130 Frontend Sense To Transistor OP Handoff

- status: `frontend_sense_to_transistor_op_handoff_failed`
- uses measured frontend sense voltage: `True`
- uses Sky130 transistor input stage: `True`
- uses extracted frontend transient: `False`
- case count: `4`
- measured case count: `2`
- sign pass count: `2`
- output margin pass count: `2`
- minimum abs output diff V: `6.166000000e-04`
- minimum gain V/V: `9.202985`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-frontend-sense-to-transistor-op-handoff.csv`

## First Principle

The full transient handoff joins two hard things: an extracted floating-capacitance frontend and real transistor device equations. This OP handoff removes the frontend transient and asks one narrower question: when the transistor pair sees the measured frontend sense voltage as a steady input, does it produce the right output sign and enough output difference?

If this passes while the full transient times out, the immediate blocker is not transistor gain at the measured sense voltage. The blocker is the dynamic handoff: how the frontend nodes, transistor gates, bias path, and solver move together in time.

## Results

| reset mode | input diff mV | sense diff uV | output diff mV | gain V/V | sign preserved | margin pass |
|---|---:|---:|---:|---:|---|---|
| `quiet_vcm` | `-0.152971` | failed | failed | failed | `False` | `False` |
| `quiet_vcm` | `0.152971` | failed | failed | failed | `False` | `False` |
| `reset_pulse` | `-0.152971` | `-67.000000` | `-0.616600` | `9.202985` | `True` | `True` |
| `reset_pulse` | `0.152971` | `67.000000` | `0.616600` | `9.202985` | `True` | `True` |

## Refused Claim

does not prove the full extracted-frontend transient handoff, latch behavior, SAR conversion, post-layout energy, or accepted converter evidence
