# Shared Converter Loading SPICE Evidence

This file turns the third converter SPICE handoff test into evidence. It checks one narrow sharing claim: the readout node can still settle within half of one 12-bit ADC step when a simple shared mux/load term is added to the converter input.

- status: `shared_converter_loading_spice_passes_simple_mux_load`
- cases: `4`
- all cases pass half-LSB shared loading: `True`
- worst case: `single_load_mid`
- worst absolute error: `0.0` V
- half-LSB limit: `0.0001220703125` V
- max active loads: `32`
- converter instances: `4`
- outputs per conversion cost: `16`
- SPICE deck: `labs/analog/analog-in-memory-foundation-model-hardware/spice/shared_converter_loading.sp`
- measurement CSV: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/shared-converter-loading-spice.csv`

## First-Principles Reading

Converter sharing is a bargain only if the shared path does not turn saved hardware into late or wrong voltage decisions. A shared mux adds resistance and capacitance. Resistance limits how quickly charge can move. Capacitance increases how much charge must move. Together they stretch the settling time.

The test is therefore not abstract. At the end of the 12 ns readout window, the sampled node must be close enough that a 12-bit ADC would not cross into a neighboring code. This artifact checks that timing-and-loading term before any energy win is trusted.

## Remaining Converter SPICE Work

- energy accounting

## Refused Claim

does not prove switch charge injection, comparator offset, capacitor mismatch, extracted routing parasitics, measured converter energy, measured silicon, or full shared ADC macro behavior
