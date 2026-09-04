# Sky130 Extracted Frontend Source-Follower Handoff

- status: `source_follower_handoff_failed`
- uses extracted frontend netlist: `True`
- uses Sky130 source-follower buffer: `True`
- uses Sky130 transistor input stage: `True`
- case count: `2`
- measured case count: `2`
- timed-out case count: `0`
- sign pass count: `0`
- output margin pass count: `0`
- minimum abs output diff V: `0.000000000e+00`
- minimum sample-to-sense transfer ratio: `0.062092`
- minimum sense-to-buffer transfer ratio: `0.000004`
- minimum buffer-to-output gain V/V: `0.000000`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-extracted-frontend-source-follower-handoff.csv`

## First Principle

A buffer is a promise to separate two jobs. The first job is to sense the stored charge without disturbing it too much. The second job is to drive the transistor input stage strongly enough for a later digital decision.

A source follower is the simplest transistor version of that promise. Its gate reads the sense node with high input resistance. Its source provides a lower-impedance copy for the readout pair. If this works, the path moves from passive coupling toward an active preamp. If it fails, the design needs either more frontend signal, a different buffer bias, or a different input-stage topology.

## Results

| reset mode | input diff mV | sense diff uV | buffer diff uV | output diff mV | sign preserved | margin pass |
|---|---:|---:|---:|---:|---|---|
| `reset_pulse` | `-0.152971` | `-9.500000` | `0.000038` | `0.000000` | `False` | `False` |
| `reset_pulse` | `0.152971` | `9.500000` | `-0.000470` | `0.000000` | `False` | `False` |

## Refused Claim

does not prove latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence
