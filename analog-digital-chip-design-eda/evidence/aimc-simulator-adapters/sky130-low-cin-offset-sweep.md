# Sky130 Extracted Frontend Preamp Gain Sweep

- status: `extracted_frontend_preamp_gain_sweep_found_no_margin_passing_setting`
- setting count: `4`
- case count: `12`
- measured case count: `12`
- timed-out case count: `0`
- passing setting count: `0`
- output margin target V: `5.000000000e-04`
- prior minimum abs preamp output diff V: `5.650000000e-05`
- best setting: `offset_probe_500k_4ua_w1`
- best minimum abs preamp output diff V: `1.447400000e-03`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-low-cin-offset-sweep.csv`

## First Principle

The standalone preamp passes because it sees the full measured sense voltage. Once the same preamp is attached to the extracted frontend, the frontend node is loaded and the voltage reaching the gate is much smaller.

This sweep asks whether a simple gain change can recover that lost voltage. If no setting reaches the margin, the next work is not another load tweak. The frontend-to-preamp interface must preserve more voltage before the preamp tries to amplify it.

## Setting Summary

| setting | rd ohm | itail uA | width | measured | sign pass | margin pass | min sense ratio | min gain V/V | min output mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `offset_probe_300k_5ua_w1` | `300000` | `5.000` | `1.000` | `3` | `1` | `3` | `0.000000` | `8.204082` | `0.804000` |
| `offset_probe_400k_5ua_w1` | `400000` | `5.000` | `1.000` | `3` | `1` | `3` | `0.000000` | `8.782857` | `0.922200` |
| `offset_probe_500k_5ua_w1` | `500000` | `5.000` | `1.000` | `3` | `1` | `3` | `0.000000` | `8.275000` | `0.827500` |
| `offset_probe_500k_4ua_w1` | `500000` | `4.000` | `1.000` | `3` | `1` | `3` | `0.000000` | `10.488406` | `1.447400` |

## Refused Claim

does not prove latch behavior, SAR conversion, offset/noise, DRC/LVS, post-layout converter energy, or accepted converter evidence
