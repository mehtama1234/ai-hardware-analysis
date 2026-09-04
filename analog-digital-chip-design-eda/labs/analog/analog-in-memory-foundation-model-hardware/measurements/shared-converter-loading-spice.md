# Shared Converter Loading SPICE

This report executes the third converter SPICE handoff testbench. It checks whether a shared readout path can still settle inside the 12-bit half-LSB window when extra mux and sample capacitance are attached to the converter input.

- SPICE deck: `spice/shared_converter_loading.sp`
- cases: `4`
- conversion window: `12.0` ns
- ADC LSB: `0.000244141` V
- half-LSB acceptance limit: `0.000122070` V
- worst sampled error: `0.000000000` V
- all cases pass half-LSB shared loading: `True`

## Results

| case | input V | active loads | sampled V | abs error V | half LSB V | pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| single_load_mid | 0.500000 | 1 | 0.500000000 | 0.000000000 | 0.000122070 | True |
| shared_16_mid | 0.500000 | 16 | 0.500000000 | 0.000000000 | 0.000122070 | True |
| shared_16_high | 0.875000 | 16 | 0.875000000 | 0.000000000 | 0.000122070 | True |
| shared_32_mid_stress | 0.500000 | 32 | 0.500000000 | 0.000000000 | 0.000122070 | True |

## First-Principles Reading

Sharing a converter saves area and energy only if the shared path does not move the signal too much before the ADC decision. The extra mux and sample load behave like extra capacitance. Extra capacitance does not change the final voltage, but it slows the movement toward that voltage.

The physical question is therefore small and testable: after the same 12 ns readout window, is the sampled node still within half of one 12-bit code step? If not, converter sharing has made the numerical readout too late even if the digital schedule looks efficient.

This fixture checks that loading term only. It does not prove switch charge injection, comparator offset, capacitor mismatch, routing parasitics, extracted layout, or measured converter energy.
