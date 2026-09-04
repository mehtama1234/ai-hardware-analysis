# Converter Supply Energy SPICE

This report executes the fourth converter SPICE handoff testbench. It integrates supply work for the row-drive, ADC-reference, and shared-mux capacitive loads in the same settling and conversion windows used by the converter target.

- SPICE deck: `spice/converter_supply_energy.sp`
- cases: `3`
- rail: `1.0` V
- settling window: `4.0` ns
- conversion window: `12.0` ns
- worst total energy: `4.273039300000e-12` J
- all cases have positive integrated energy: `True`

## Results

| case | input V | DAC energy J | ADC energy J | mux energy J | total energy J | pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| low_conversion | 0.125000 | 3.848910000000e-15 | 3.988100000000e-12 | 1.965350000000e-15 | 3.993914260000e-12 | True |
| mid_conversion | 0.500000 | 6.159560000000e-14 | 3.988100000000e-12 | 3.144570000000e-14 | 4.081141300000e-12 | True |
| high_conversion | 0.875000 | 1.886370000000e-13 | 3.988100000000e-12 | 9.630230000000e-14 | 4.273039300000e-12 | True |

## First-Principles Reading

Energy is charge moved through a voltage. A converter may be accurate and still be a bad hardware choice if too much charge is moved every time an activation is driven or a column value is read.

This fixture names the rail and integrates the work done by three simple sources: row drive, ADC reference charging, and shared mux charging. It gives a circuit-derived energy scale for the clean load model. It does not include layout parasitics, bias currents, clock tree power, leakage, comparator short-circuit current, or measured board power.
