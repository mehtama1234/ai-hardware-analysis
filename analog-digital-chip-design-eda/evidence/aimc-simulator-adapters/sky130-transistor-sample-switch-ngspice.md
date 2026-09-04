# Sky130 Transistor Sample Switch Ngspice

- status: `sky130_transistor_sample_switch_passed_not_converter_proof`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_transistor_sample_switch.sp`
- device models: `sky130_fd_pr__nfet_01v8, sky130_fd_pr__pfet_01v8`
- case count: `3`
- worst sample error V: `1.369000000e-04`
- half LSB 12b V: `2.197265625e-04`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-transistor-sample-switch-ngspice.csv`

## First Principle

A sample switch is a controlled path for charge. When the gate turns on, the input node and sample capacitor are connected through real transistor channel behavior. The sampled value is correct only if enough charge moves before the switch turns off.

This fixture asks that question directly. It drives low, middle, and high input voltages through a Sky130 transmission gate into a sample capacitor. Then it checks whether the sample node is within half of one 12-bit output step while the switch is still on. That is one small part of an ADC boundary: the voltage must arrive before the digital decision can mean anything.

This is not a full converter. It has no hold-mode feedthrough test, no capacitor DAC, no comparator, no SAR loop, no reference ladder, no mismatch run, and no extracted transistor layout. It proves only that this starter MOS sample path can be simulated with the installed Sky130 models and can settle under this fixture.

## Results

| case | input V | sampled V | error V | half LSB 12b V | pass |
|---|---:|---:|---:|---:|---|
| low_sample | `0.300000000` | `0.300000000` | `0.000000000e+00` | `2.197265625e-04` | `True` |
| mid_sample | `0.900000000` | `0.900136900` | `1.369000000e-04` | `2.197265625e-04` | `True` |
| high_sample | `1.500000000` | `1.500000000` | `0.000000000e+00` | `2.197265625e-04` | `True` |

## Refused Claim

does not prove hold-mode feedthrough, DAC ladder behavior, SAR capacitor array behavior, comparator decision, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
