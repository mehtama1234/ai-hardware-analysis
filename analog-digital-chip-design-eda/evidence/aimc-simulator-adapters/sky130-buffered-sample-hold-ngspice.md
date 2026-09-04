# Sky130 Buffered Sample-Hold Ngspice

- status: `sky130_buffered_sample_hold_characterized_not_converter_proof`
- topology: `nfet_source_follower_readout_buffer_after_sample_capacitor`
- PDK model library: `/home/mehtama1/eda-tools/pdks/sky130A/libs.tech/ngspice/sky130.lib.spice`
- generated deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_buffered_sample_hold.sp`
- case count: `3`
- measured case count: `0`
- timed out case count: `3`
- half LSB 12b V: `2.197265625e-04`
- worst sample hold abs delta V: `not measured`
- worst output hold abs delta V: `not measured`
- sample hold pass count: `0` of `3`
- output hold pass count: `0` of `3`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-buffered-sample-hold-ngspice.csv`

## First Principle

A stored voltage should remember charge, not drive the rest of the readout path by itself. If the same tiny node both stores the value and drives load capacitance, any charge pulled by that load becomes voltage error on the memory node.

This fixture puts a MOS source follower after the sample capacitor. The capacitor drives a gate, so the readout load is moved to a different node. That tests one concrete version of the buffered sample-and-hold idea from the topology decision gate.

This is still only a first circuit candidate. A source follower has threshold drop, finite gain, bias current, input capacitance, limited swing, and possible convergence trouble. The useful question here is not whether this is a finished ADC front end. The question is whether isolating the stored node produces a measurable hold-mode improvement that deserves a stronger buffer design.

## Results

| case | input V | acquired sample V | held sample V | acquired output V | held output V | sample hold delta V | output hold delta V |
|---|---:|---:|---:|---:|---:|---:|---:|
| low_buffered_hold | `0.300000000` | timeout | timeout | timeout | timeout | timeout | timeout |
| mid_buffered_hold | `0.900000000` | timeout | timeout | timeout | timeout | timeout | timeout |
| high_buffered_hold | `1.500000000` | timeout | timeout | timeout | timeout | timeout | timeout |

## Reading The Result

If the sample node still moves more than half an LSB, the buffer has not solved the memory problem. If the output node moves less but has poor gain or swing, the next buffer must be redesigned rather than accepted. If the cases time out, the fixture is also not acceptable evidence, because a converter proof has to be rerunnable and numerically stable.

## Refused Claim

does not prove a rail-to-rail buffer, comparator decision, SAR conversion, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics
