# Sky130 Measured Sense Preamp Bias Sweep

- status: `measured_sense_preamp_bias_sweep_found_passing_setting_not_extracted_frontend`
- setting count: `4`
- case count: `8`
- measured case count: `8`
- timed-out case count: `0`
- passing setting count: `1`
- uses measured frontend sense voltage: `True`
- uses extracted frontend transient: `False`
- accepted post-layout written: `False`

## First Principle

Before a preamp can be blamed for loading the extracted frontend, it must first work when the tiny input voltage is supplied directly. This sweep changes current, load resistance, and transistor width while keeping the input voltage equal to the measured frontend sense voltage.

A useful setting must do three things at once: run to completion, preserve the sign for both input directions, and create enough output difference for the next decision stage.

## Setting Summary

| setting | rd ohm | itail uA | width | measured | sign pass | margin pass | min output mV | min gain V/V |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `low_current_wide_load` | `100000` | `5.000` | `2.000` | `2` | `2` | `0` | `0.294000` | `4.388060` |
| `baseline_softened` | `100000` | `10.000` | `4.000` | `2` | `2` | `0` | `0.491000` | `7.328358` |
| `known_input_stage_bias` | `100000` | `20.000` | `8.000` | `2` | `2` | `2` | `0.626400` | `9.349254` |
| `higher_load_low_current` | `180000` | `5.000` | `4.000` | `2` | `2` | `0` | `0.462000` | `6.895522` |

## Refused Claim

does not prove extracted frontend loading, latch behavior, SAR conversion, DRC/LVS, post-layout energy, or accepted converter evidence
