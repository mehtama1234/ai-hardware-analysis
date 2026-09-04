# Sky130 Sample-Hold Latch Kickback Ngspice

- status: `sky130_sample_hold_latch_kickback_proxy_characterized_not_accepted`
- topology: `differential_dummy_sample_hold_driving_clocked_sky130_latch_input_pair`
- target combined offset/noise mV: `0.1530`
- hard budget mV: `0.1567`
- half LSB 12b V: `2.197265625e-04`
- resolved correct polarity count: `2` of `2`
- kickback below half LSB count: `0` of `2`
- worst sampled differential kickback V: `1.203400000e-02`
- all cases pass coupled gate: `False`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-sample-hold-latch-kickback-ngspice.csv`

## First Principle

A latch is not only a reader. It is also a load. When its clock moves, transistor capacitances can push charge back into the sampled nodes. That movement changes the same small voltage difference the latch is supposed to decide.

This fixture connects the differential dummy sample-and-hold candidate to the clocked Sky130 latch proxy. It measures the sampled differential voltage before latch evaluation, measures it again after the latch has switched, and checks whether the latch both resolves in the correct direction and keeps sampled-node kickback below the 12-bit half-LSB line.

This is the first coupled sample-hold plus latch check. It is stronger than driving the latch from ideal voltage sources. It is still not a full comparator proof because it does not include noise, offset statistics, SAR bit cycling, extracted layout, or DRC/LVS.

## Results

| case | input diff mV | sampled diff before V | sampled diff after V | kickback V | output diff V | resolved | kickback pass |
|---|---:|---:|---:|---:|---:|---|---|
| `negative_target_edge` | `-0.152971` | `-4.831680000e-05` | `1.198570000e-02` | `1.203400000e-02` | `-1.310520000e+00` | `True` | `False` |
| `positive_target_edge` | `0.152971` | `4.831680000e-05` | `-1.198570000e-02` | `1.203400000e-02` | `1.310520000e+00` | `True` | `False` |

## Refused Claim

does not prove comparator noise, input-referred offset statistics, SAR bit cycling, extracted layout, DRC/LVS signoff, or accepted replacement economics
