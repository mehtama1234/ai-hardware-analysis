# Sky130 Extracted Frontend Preamp Gain Sweep

- status: `extracted_frontend_preamp_gain_sweep_found_no_margin_passing_setting`
- setting count: `4`
- case count: `8`
- measured case count: `8`
- timed-out case count: `0`
- passing setting count: `0`
- output margin target V: `5.000000000e-04`
- prior minimum abs preamp output diff V: `5.650000000e-05`
- best setting: `low_cin_500k_5ua`
- best minimum abs preamp output diff V: `8.275000000e-04`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-low-cin-preamp-targeted-sweep.csv`

## First Principle

The standalone preamp passes because it sees the full measured sense voltage. Once the same preamp is attached to the extracted frontend, the frontend node is loaded and the voltage reaching the gate is much smaller.

This sweep asks whether a simple gain change can recover that lost voltage. If no setting reaches the margin, the next work is not another load tweak. The frontend-to-preamp interface must preserve more voltage before the preamp tries to amplify it.

## Setting Summary

| setting | rd ohm | itail uA | width | measured | sign pass | margin pass | min sense ratio | min gain V/V | min output mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `low_cin_1m_5ua` | `1000000` | `5.000` | `0.500` | `2` | `2` | `0` | `0.346405` | `0.011698` | `0.000620` |
| `low_cin_2m_5ua` | `2000000` | `5.000` | `0.500` | `2` | `2` | `0` | `0.346405` | `0.001887` | `0.000100` |
| `low_cin_1m_10ua` | `1000000` | `10.000` | `0.500` | `2` | `2` | `0` | `0.346405` | `0.003774` | `0.000200` |
| `low_cin_500k_5ua` | `500000` | `5.000` | `1.000` | `2` | `1` | `2` | `0.215686` | `8.275000` | `0.827500` |

## Refused Claim

does not prove latch behavior, SAR conversion, offset/noise, DRC/LVS, post-layout converter energy, or accepted converter evidence
