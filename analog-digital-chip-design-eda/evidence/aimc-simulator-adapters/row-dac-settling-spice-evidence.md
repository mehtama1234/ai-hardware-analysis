# Row-DAC Settling SPICE Evidence

This file turns the first converter SPICE handoff test into evidence. It checks one narrow claim: a simple 10-bit row-driver load can settle within half of one DAC step during the 4 ns window used by the behavioral converter estimate.

- status: `row_dac_settling_spice_passes_simple_load`
- cases: `3`
- all cases pass half-LSB settling: `True`
- worst case: `high_code`
- worst absolute error: `0.0001767000000000296` V
- half-LSB limit: `0.00048828125` V
- margin to half-LSB: `0.0003115812499999704` V
- SPICE deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/row_dac_settling_10bit.sp`
- measurement CSV: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/row-dac-settling-spice.csv`

## First-Principles Reading

The 10-bit input target only means something if the row voltage has time to become the requested voltage. A digital control word can name 1024 levels, but a circuit node reaches those levels by charging capacitance through resistance. If the row is still moving when the array is sampled, the array does not see the requested code.

The acceptance rule is half of one 10-bit step. That is the voltage distance between a safe settled value and the nearest wrong code boundary. Passing this test means the simple row-driver load does not by itself destroy the 10-bit input assumption.

## Remaining Converter SPICE Work

- 12-bit SAR readout decision
- shared converter loading
- energy accounting

## Refused Claim

does not prove transistor DAC linearity, mismatch, reference noise, switch charge injection, extracted parasitics, ADC behavior, measured silicon, or board energy
