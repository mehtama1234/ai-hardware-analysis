# Analog Converter Layout Starter Package

This folder is a starting workbench for the converter layout pass. It is not post-layout evidence.

The source SPICE decks already check converter behavior. This folder names the physical cells, extraction command shape, and measurement record shape needed before the strict post-layout payload can be filled.

## Physical Objects

- `row_dac_10b`: row-drive DAC path for the 10-bit input target.
- `sar_readout_12b`: sample path, comparator path, and SAR readout boundary for the 12-bit output target.
- `shared_converter_mux`: mux and loading path for the shared converter rule.
- `aimc_converter_macro`: top boundary that contains DAC, ADC, references, mux, and sample path.

## Rule

Do not copy these starter files into `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/` as if they were extracted. The candidate folder needs real extracted SPICE, DSPF, or SPEF plus the model/setup files and break-even rerun from the same run.
