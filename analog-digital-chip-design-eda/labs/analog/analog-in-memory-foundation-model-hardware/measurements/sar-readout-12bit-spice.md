# SAR Readout 12-Bit SPICE

This report executes the second converter SPICE handoff testbench. It checks whether the sampled readout node can settle close enough for a 12-bit ADC decision inside the 12 ns conversion window used by the behavioral converter estimate.

- SPICE deck: `spice/sar_readout_12bit.sp`
- cases: `3`
- conversion window: `12.0` ns
- SAR comparisons: `12`
- ADC LSB: `0.000244141` V
- half-LSB acceptance limit: `0.000122070` V
- worst sampled error: `0.000000000` V
- all cases pass half-LSB readout: `True`

## Results

| case | input V | sampled V | abs error V | half LSB V | pass |
| --- | ---: | ---: | ---: | ---: | --- |
| low_readout | 0.125000 | 0.125000000 | 0.000000000 | 0.000122070 | True |
| mid_readout | 0.500000 | 0.500000000 | 0.000000000 | 0.000122070 | True |
| high_readout | 0.875000 | 0.875000000 | 0.000000000 | 0.000122070 | True |

## First-Principles Reading

A SAR ADC is a timed sequence of decisions. The circuit first has to hold a readout voltage on a sample node. Then each comparison decides one bit. If the sampled voltage is still moving by more than half of one 12-bit step, the ADC can choose the wrong neighboring code even if the digital comparison sequence is correct.

This fixture isolates the sampled readout node. It does not prove comparator offset, capacitor mismatch, reference settling, switch charge injection, or metastability. It proves a narrower thing: this readout load can place the sample node within the half-LSB voltage window before the 12-bit decision sequence finishes.
