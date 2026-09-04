# Sky130 Capacitive Isolation Both-Polarity Confirm

- status: `sky130_capacitive_isolation_both_polarity_confirmed_not_noise_or_layout_proof`
- confirmed coupling caps fF: `0.1, 0.2`
- target combined offset/noise mV: `0.1530`
- hard kickback limit V: `2.197265625e-04`
- worst kickback V: `2.022000000e-04`
- passing case count: `4` of `4`
- all cases pass: `True`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-capacitive-isolation-both-polarity-confirm.csv`

## First Principle

A useful comparator isolation trick must work for either sign of the input difference. If it only works when the positive side is larger, it is not a comparator front end. It is a one-sided accident.

This run takes only the capacitor values that passed the first capacitive-isolation sweep, then reruns them with positive and negative target-edge inputs. The check is simple: the latch must resolve in the correct direction and the sampled differential kickback must stay below the half-LSB line.

## Results

| cap fF | input diff mV | kickback V | hard limit V | output diff V | expected sign | measured sign | pass |
|---:|---:|---:|---:|---:|---:|---:|---|
| `0.100` | `-0.152971` | `1.191000000e-04` | `2.197265625e-04` | `-1.369890000e+00` | `-1` | `-1` | `True` |
| `0.100` | `0.152971` | `1.191000000e-04` | `2.197265625e-04` | `1.369890000e+00` | `1` | `1` | `True` |
| `0.200` | `-0.152971` | `2.022000000e-04` | `2.197265625e-04` | `-1.365390000e+00` | `-1` | `-1` | `True` |
| `0.200` | `0.152971` | `2.022000000e-04` | `2.197265625e-04` | `1.365390000e+00` | `1` | `1` | `True` |

## Refused Claim

does not prove comparator noise, offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics
