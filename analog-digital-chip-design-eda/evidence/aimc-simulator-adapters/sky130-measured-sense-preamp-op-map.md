# Sky130 Measured Sense Preamp OP Map

- status: `measured_sense_preamp_op_map_found_valid_bias_point_not_transient_or_extracted_frontend`
- setting count: `1`
- case count: `2`
- OP measured case count: `2`
- timed-out case count: `0`
- passing setting count: `1`
- uses DC operating point: `True`
- uses measured frontend sense voltage: `True`
- uses extracted frontend transient: `False`
- accepted post-layout written: `False`

## First Principle

A transient run asks two questions at once: where should the circuit settle, and how does it get there over time? A DC operating-point run asks only the first question. That is the right next test when transient preamp runs time out.

A useful preamp bias point must leave the tail node and both output nodes away from the rails. It must also give the right output sign for both tiny input directions. Only then is it worth spending time on transient startup.

## Setting Summary

| setting | rd ohm | itail uA | width | OP measured | bias pass | sign pass | margin pass | min output mV | min gain V/V |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `known_input_stage_bias` | `100000` | `20.000` | `8.000` | `2` | `2` | `2` | `2` | `0.616600` | `9.202985` |

## Best Observed Bias

- setting: `known_input_stage_bias`
- OP measured cases: `2`
- bias-window passes: `2`
- sign passes: `2`
- margin passes: `2`

## Refused Claim

does not prove transient startup, extracted frontend loading, latch behavior, SAR conversion, DRC/LVS, post-layout energy, or accepted converter evidence
