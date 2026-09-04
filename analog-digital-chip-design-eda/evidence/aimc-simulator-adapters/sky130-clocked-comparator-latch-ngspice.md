# Sky130 Clocked Comparator Latch Ngspice

- status: `sky130_clocked_comparator_latch_proxy_passed_not_noise_or_layout_proof`
- topology: `clocked_cross_coupled_inverter_latch_with_sky130_nfet_input_pair`
- target combined offset/noise mV: `0.1530`
- hard budget mV: `0.1567`
- resolved correct polarity count: `2` of `2`
- resolution threshold V: `0.9`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-clocked-comparator-latch-ngspice.csv`

## First Principle

The input-stage proxy only showed that a tiny voltage difference can lean a transistor pair in the right direction. A comparator also has to make a timed decision. A clocked latch starts near an undecided state, then positive feedback pushes one side high and the other side low.

This fixture checks that timed decision in the smallest useful way. It applies the already-derived target-edge input difference, turns on a Sky130 latch, and asks whether the final output polarity matches the input sign with enough voltage separation to be read as a logic decision.

This is still not the finished ADC comparator. The inputs are ideal voltage sources, so this run does not yet measure kickback into the real sampled nodes. It does not run noise, mismatch statistics, SAR bit cycling, extracted layout, or post-layout economics.

## Results

| case | input diff mV | outp final V | outn final V | output diff V | resolved correct polarity |
|---|---:|---:|---:|---:|---|
| `negative_target_edge` | `-0.152971` | `1.624950000` | `0.343430300` | `-1.281520000e+00` | `True` |
| `positive_target_edge` | `0.152971` | `0.343430300` | `1.624950000` | `1.281520000e+00` | `True` |

## Refused Claim

does not prove comparator noise, input-referred offset statistics, kickback into the sampled nodes, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics
