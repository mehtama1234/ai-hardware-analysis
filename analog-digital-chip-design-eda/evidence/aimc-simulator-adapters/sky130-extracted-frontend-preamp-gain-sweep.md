# Sky130 Extracted Frontend Preamp Gain Sweep

- status: `extracted_frontend_preamp_gain_sweep_found_no_margin_passing_setting`
- setting count: `4`
- case count: `8`
- measured case count: `8`
- timed-out case count: `0`
- passing setting count: `0`
- output margin target V: `5.000000000e-04`
- prior minimum abs preamp output diff V: `5.650000000e-05`
- best setting: `known_input_stage_bias`
- best minimum abs preamp output diff V: `5.650000000e-05`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-extracted-frontend-preamp-gain-sweep.csv`

## First Principle

The standalone preamp passes because it sees the full measured sense voltage. Once the same preamp is attached to the extracted frontend, the frontend node is loaded and the voltage reaching the gate is much smaller.

This sweep asks whether a simple gain change can recover that lost voltage. If no setting reaches the margin, the next work is not another load tweak. The frontend-to-preamp interface must preserve more voltage before the preamp tries to amplify it.

## Setting Summary

| setting | rd ohm | itail uA | width | measured | sign pass | margin pass | min sense ratio | min gain V/V | min output mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `known_input_stage_bias` | `100000` | `20.000` | `8.000` | `2` | `2` | `0` | `0.041830` | `8.188406` | `0.056500` |
| `higher_load_same_current` | `180000` | `20.000` | `8.000` | `2` | `2` | `0` | `0.069281` | `1.481132` | `0.015700` |
| `higher_load_lower_current` | `220000` | `10.000` | `8.000` | `2` | `2` | `0` | `0.015686` | `0.506494` | `0.007800` |
| `wider_pair_same_load` | `100000` | `20.000` | `16.000` | `2` | `2` | `0` | `0.014379` | `7.150000` | `0.028600` |

## Refused Claim

does not prove latch behavior, SAR conversion, offset/noise, DRC/LVS, post-layout converter energy, or accepted converter evidence
