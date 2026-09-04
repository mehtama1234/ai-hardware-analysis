# Converter Starter Physical Artifacts

- status: `starter_physical_artifacts_present_not_accepted_evidence`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- cell count: `4`
- complete cell count: `4`
- macro bbox area lambda2: `2376000`
- candidate post-layout written: `False`
- accepted post-layout written: `False`

## First Principle

A layout artifact is stronger than a paragraph because it has shapes, extracted records, and a netlist that another tool can inspect. But it is still weaker than converter evidence if it does not measure the circuit quantities that the system decision depends on.

The starter cells prove the physical path is alive. They do not prove that the row driver has the requested analog accuracy, that the readout has the requested noise, or that the shared converter cost makes analog replacement worthwhile.

## Cells

### row_dac_10b

- magic cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.mag` present `True`
- ext file: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.ext` present `True`
- extracted spice: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/row_dac_10b_layout_smoke.spice` present `True`
- rect count: `15`
- bbox lambda: `[0, 0, 1200, 520]`
- bbox area lambda2: `624000`
- device-like SPICE lines: `6`
- has subckt: `True`

### sar_readout_12b

- magic cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.mag` present `True`
- ext file: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.ext` present `True`
- extracted spice: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sar_readout_12b_layout_smoke.spice` present `True`
- rect count: `15`
- bbox lambda: `[0, 0, 1400, 640]`
- bbox area lambda2: `896000`
- device-like SPICE lines: `6`
- has subckt: `True`

### shared_converter_mux

- magic cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.mag` present `True`
- ext file: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.ext` present `True`
- extracted spice: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/shared_converter_mux_layout_smoke.spice` present `True`
- rect count: `19`
- bbox lambda: `[0, 0, 1600, 700]`
- bbox area lambda2: `1120000`
- device-like SPICE lines: `5`
- has subckt: `True`

### aimc_converter_macro

- magic cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.mag` present `True`
- ext file: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.ext` present `True`
- extracted spice: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice` present `True`
- rect count: `17`
- bbox lambda: `[0, 0, 2200, 1080]`
- bbox area lambda2: `2376000`
- device-like SPICE lines: `20`
- has subckt: `True`

## Refused Claim

does not measure converter energy, latency, noise, calibrated bit accuracy, DRC/LVS signoff, or accepted post-layout replacement economics
