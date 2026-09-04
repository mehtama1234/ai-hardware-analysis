# Row-DAC Settling SPICE

This report executes the first converter SPICE handoff testbench. It checks whether a 10-bit row-drive boundary can settle a representative row load inside the 4 ns window used by the behavioral converter estimate.

- SPICE deck: `spice/row_dac_settling_10bit.sp`
- cases: `3`
- settling window: `4.0` ns
- DAC LSB: `0.000976562` V
- half-LSB acceptance limit: `0.000488281` V
- worst settled error: `0.000176700` V
- all cases pass half-LSB settling: `True`

## Results

| case | target V | settled V | abs error V | half LSB V | pass |
| --- | ---: | ---: | ---: | ---: | --- |
| low_code | 0.125000 | 0.124974800 | 0.000025200 | 0.000488281 | True |
| mid_code | 0.500000 | 0.499899000 | 0.000101000 | 0.000488281 | True |
| high_code | 0.875000 | 0.874823300 | 0.000176700 | 0.000488281 | True |

## First-Principles Reading

A DAC code is not useful at the model boundary until the selected row voltage has actually moved close enough to its target. The row driver has resistance, the row has resistance, and the selected row load has capacitance. That makes the row voltage a time-dependent circuit state, not an instant number.

For a 10-bit row drive, one code step is full scale divided by 1024. The settling rule used here is stricter than one full code step: after 4 ns, the row voltage must be within half of one step. If it is not, the hardware is effectively using fewer than 10 reliable input bits even if the control word has 10 bits.

This SPICE fixture therefore tests a concrete part of the converter claim. It does not prove a transistor DAC, reference ladder, switch linearity, mismatch, layout parasitics, or silicon noise. It only proves that this simple driver-load model can meet the 4 ns half-LSB settling condition.
