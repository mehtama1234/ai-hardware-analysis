# Converter Starter Parasitic Load Estimate

- status: `starter_extracted_parasitic_load_estimated_not_converter_proof`
- supply V: `1.8`
- row driver R ohm: `1000.0`
- ADC input R ohm: `2000.0`
- mux on R ohm: `250.0`
- row count: `7`
- total estimated pin charge energy J: `3.225791e-14`
- max settle 0.1 percent s: `9.559010e-11`
- candidate post-layout written: `False`
- accepted post-layout written: `False`
- csv: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-starter-parasitic-load-estimate.csv`

## First Principle

An extracted capacitance tells us how much charge a node must move when it switches. With voltage fixed, the first-order switching energy is one half times capacitance times voltage squared. With a chosen driver resistance, the first-order settling time is resistance times capacitance.

This is real information from layout extraction, but it is not the converter result. A converter also needs transistor behavior: settling shape, comparator decision, mismatch, noise, supply current, and the same-run system rerun. Capacitance alone can bound load; it cannot prove conversion quality.

## Estimated Loads

| object | capacitance F | energy J | settle 0.1% s | meaning |
|---|---:|---:|---:|---|
| `row_dac_10b.row_drive` | `3.117680e-15` | `5.050642e-15` | `2.153617e-11` | extracted row-drive pin capacitance in the starter row-DAC cell |
| `aimc_converter_macro.row_drive` | `1.936190e-15` | `3.136628e-15` | `1.337473e-11` | extracted row-drive pin capacitance at the starter macro boundary |
| `aimc_converter_macro.column_sense` | `2.094980e-15` | `3.393868e-15` | `3.256112e-11` | extracted column-sense pin capacitance at the starter macro boundary |
| `aimc_converter_macro.digital_code_out` | `2.567420e-15` | `4.159220e-15` | `1.773511e-11` | extracted digital output pin capacitance at the starter macro boundary |
| `shared_converter_mux.mux_bus` | `6.150260e-15` | `9.963421e-15` | `9.559010e-11` | extracted mux bus capacitance in the starter shared converter mux |
| `sar_readout_12b.sample_in` | `4.045760e-15` | `6.554131e-15` | `2.794712e-11` | extracted sample input capacitance in the starter SAR readout cell |
| `aimc_converter_macro.row_to_column_coupling` | `8.871000e-17` | `1.437102e-16` | `6.127870e-13` | direct extracted parasitic coupling between row drive and column sense |

## Refused Claim

does not simulate transistor converter behavior, comparator offset, DAC linearity, ADC decision error, supply current integration, DRC/LVS signoff, or accepted replacement economics
