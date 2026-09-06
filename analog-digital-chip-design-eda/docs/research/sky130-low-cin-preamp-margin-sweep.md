# Sky130 Low-Capacitance Preamp Margin Sweep

The extracted ultra-sense frontend was attached to a Sky130 transistor differential preamp and swept around the first low-input-capacitance operating point.

The sweep covered six settings and twelve transient cases in total. Every case completed without timeout. Several settings produced more than the required `0.5 mV` output magnitude, but none passed both polarity and margin together.

| setting | load | tail current | input width | minimum output magnitude | polarity cases | margin cases |
|---|---:|---:|---:|---:|---:|---:|
| `margin_300k_5ua_w1` | `300 kΩ` | `5 µA` | `1 µm` | `0.804 mV` | `1/2` | `2/2` |
| `margin_400k_5ua_w1` | `400 kΩ` | `5 µA` | `1 µm` | `0.922 mV` | `1/2` | `2/2` |
| `margin_500k_5ua_w1` | `500 kΩ` | `5 µA` | `1 µm` | `0.828 mV` | `1/2` | `2/2` |
| `margin_600k_5ua_w1` | `600 kΩ` | `5 µA` | `1 µm` | `0.202 mV` | `1/2` | `0/2` |
| `margin_500k_4ua_w1` | `500 kΩ` | `4 µA` | `1 µm` | `1.447 mV` | `1/2` | `2/2` |
| `margin_500k_6ua_w1` | `500 kΩ` | `6 µA` | `1 µm` | `0.035 mV` | `2/2` | `0/2` |

The complete evidence is [sky130-low-cin-margin-sweep.json](../../evidence/aimc-simulator-adapters/sky130-low-cin-margin-sweep.json). The runner now supports the reproducible `AIMC_PREAMP_SWEEP_PROFILE=low_cin_margin` profile and a separate output stem.

## Interpretation

This is the first measured transistor path with enough raw output magnitude to be worth calibration work. The failure is not lack of gain alone: the high-margin settings resolve only one polarity because the preamp has a deterministic input-referred offset or common-mode imbalance. The next design/test must measure the zero-differential output, subtract or trim that offset, and then rerun both target edges with the same `0.5 mV` margin requirement.

## Boundary

This remains an extracted-frontend plus schematic transistor-preamp result. It does not prove a drawn preamp layout, offset statistics, noise, latch kickback, DRC/LVS, SAR conversion, or accepted post-layout converter evidence.
