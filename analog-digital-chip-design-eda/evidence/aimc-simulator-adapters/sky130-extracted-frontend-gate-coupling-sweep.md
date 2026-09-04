# Sky130 Extracted Frontend Gate Coupling Sweep

- status: `gate_coupling_sweep_found_no_passing_assisted_setting`
- setting count: `4`
- case count: `8`
- measured case count: `0`
- timed-out case count: `8`
- passing setting count: `0`
- uses extracted frontend netlist: `True`
- uses Sky130 transistor input stage: `True`
- uses assisted gate startup: `True`
- uses full free gate handoff: `False`
- same-run strict payload ready: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-extracted-frontend-gate-coupling-sweep.csv`

## First Principle

A tiny sampled voltage is not only a number. It is charge sitting on small capacitances. When a transistor gate is attached, the same charge sees a new electrical object. The voltage can shrink, move, or flip because the gate path and bias path now share the node.

This sweep changes two resistances. The sense-to-gate resistance controls how hard the frontend is loaded by the transistor input. The prebias resistance controls how hard the startup guide pulls the gate toward the previously measured sense voltage. If one setting passed both polarities, the next move would be to remove the guide gradually. If no setting passes, the frontend needs a buffer, a stronger differential sense node, or a cleaner port topology before latch work is meaningful.

## Setting Summary

| sense-to-gate ohm | prebias ohm | measured | sign pass | margin pass | min output mV | min sense-to-gate |
|---:|---:|---:|---:|---:|---:|---:|
| `300000` | `50000` | `0` | `0` | `0` | `0.000000` | `0.000000` |
| `1000000` | `50000` | `0` | `0` | `0` | `0.000000` | `0.000000` |
| `1000000` | `100000` | `0` | `0` | `0` | `0.000000` | `0.000000` |
| `3000000` | `100000` | `0` | `0` | `0` | `0.000000` | `0.000000` |

## Best Observed Setting

- by margin: sense-to-gate `300000` ohm, prebias `50000` ohm, sign passes `0`, margin passes `0`
- by sign: sense-to-gate `300000` ohm, prebias `50000` ohm, sign passes `0`, margin passes `0`

## Refused Claim

does not prove full free gate handoff, latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence
