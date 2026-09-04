# Analog Converter Physical Cell Gate

- status: `physical_cells_present_waiting_for_extracted_artifacts`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- required cell count: `4`
- present cell count: `4`
- missing cell count: `0`
- present extracted artifact count: `0`
- ready for candidate post-layout payload: `False`

## First Principle

A converter is not proven by having the right tools. It is proven when there are named physical cells that the layout tool can read, and when those cells produce extracted files that the simulator can use.

The named cells matter because each one controls a different error source. The DAC sets the input voltage, the readout turns the result back into bits, the mux adds shared loading, and the macro fixes the pins and area that the system model must pay for.

## Required Physical Cells

### row_dac_10b

- purpose: turns activation bits into the row voltage driven onto the analog array
- present: `True`
- accepted source names: `row_dac_10b.mag, row_dac_10b.gds, row_dac_10b.sch`
- match: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.mag` (837 bytes)

### sar_readout_12b

- purpose: turns the sensed analog column value back into a bounded digital number
- present: `True`
- accepted source names: `sar_readout_12b.mag, sar_readout_12b.gds, sar_readout_12b.sch`
- match: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.mag` (804 bytes)

### shared_converter_mux

- purpose: connects many rows or columns to a smaller converter bank without hiding load
- present: `True`
- accepted source names: `shared_converter_mux.mag, shared_converter_mux.gds, shared_converter_mux.sch`
- match: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.mag` (949 bytes)

### aimc_converter_macro

- purpose: packages the DAC, readout, mux, supplies, and pins as the converter boundary used by the model
- present: `True`
- accepted source names: `aimc_converter_macro.mag, aimc_converter_macro.gds, aimc_converter_macro.lef`
- match: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.mag` (1050 bytes)

## Required Extracted Artifacts

- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp` present `False` bytes `0`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp` present `False` bytes `0`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp` present `False` bytes `0`
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json` present `False` bytes `0`
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/converter-post-layout-break-even-rerun.json` present `False` bytes `0`

## Refused Claim

does not count environment files, skeleton scripts, or temporary positive-path fixtures as converter layout evidence
