# SAR Readout SPICE Evidence

This file turns the second converter SPICE handoff test into evidence. It checks one narrow readout claim: the sampled voltage can settle within half of one 12-bit ADC step during the 12 ns conversion window used by the behavioral converter estimate.

- status: `sar_readout_spice_passes_simple_sample_load`
- cases: `3`
- all cases pass half-LSB readout: `True`
- worst case: `low_readout`
- worst absolute error: `0.0` V
- half-LSB limit: `0.0001220703125` V
- SAR comparisons: `12`
- SPICE deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sar_readout_12bit.sp`
- measurement CSV: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sar-readout-12bit-spice.csv`

## First-Principles Reading

A 12-bit ADC claim is a claim about small voltage differences. One full-scale volt divided into 4096 codes gives a step of about `0.000244` V. Half of that step is the safe distance from the nearest neighboring decision boundary.

The SAR sequence can only make correct bit decisions if the sampled readout node is already inside that half-step window. This SPICE fixture checks that sampled-node part of the claim. It does not yet check comparator offset, reference movement, capacitor mismatch, or switching kickback.

## Remaining Converter SPICE Work

- shared converter loading
- energy accounting

## Refused Claim

does not prove comparator offset, capacitor mismatch, reference settling, switch charge injection, metastability, extracted parasitics, measured silicon, or board energy
