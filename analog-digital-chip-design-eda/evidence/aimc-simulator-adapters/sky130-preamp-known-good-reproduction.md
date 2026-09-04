# Sky130 Preamp Known-Good Reproduction

- status: `known_good_reproduction_passed_for_known_and_measured_sense_inputs`
- topology: `same_resistively_loaded_sky130_nfet_differential_pair_with_ideal_tail_bias_as_known_good_input_stage`
- case count: `2`
- OP measured case count: `2`
- timed-out case count: `0`
- polarity pass count: `2`
- accepted post-layout written: `False`

## First Principle

A failed larger circuit should be reduced to the smallest circuit that already had evidence. If that smallest circuit no longer runs, the problem is the run setup or the toolchain. If it still runs at the old input and at the smaller measured input, the next problem is loading or topology, not the basic differential pair.

This test uses the same node names, ideal tail, resistive loads, output capacitors, device size, common-mode voltage, and OP flow as the passing input-stage deck. It changes only the input difference.

## Cases

| case | source | input mV | OP measured | output mV | gain V/V | polarity pass |
|---|---|---:|---:|---:|---:|---:|
| `known_good_positive_target_edge` | `evidence/aimc-simulator-adapters/sky130-comparator-input-stage-ngspice.json` | `0.152970585` | `True` | `1.407600000` | `9.201769` | `True` |
| `measured_frontend_positive_sense_edge` | `evidence/aimc-simulator-adapters/sky130-frontend-sense-to-transistor-ramp-startup.json` | `0.067000000` | `True` | `0.616600000` | `9.202985` | `True` |

## Refused Claim

does not prove extracted frontend loading, a preamp topology change, clocked latch behavior, SAR conversion, layout extraction, DRC/LVS, or accepted converter evidence
