# Converter Starter Layout Smoke

- status: `converter_starter_layout_smoke_passed_not_candidate_evidence`
- cell count: `4`
- passed cell count: `4`
- passed: `True`
- writes candidate post-layout evidence: `False`

## First Principle

The next physical step is to make every named converter block concrete enough for the layout tool to read it. That is still not the same as proving the circuit. It only proves that the physical names now point to extractable shapes.

Each starter cell names a boundary that later has to become a real circuit: row drive, sampled readout, shared loading, and the top macro. The smoke keeps this separate from candidate post-layout evidence.

## Cells

### row_dac_10b

- purpose: starter row-drive boundary with rails, row-drive bus, and switch-column placeholders
- cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.mag`
- cell present: `True`
- passed: `True`
- command: `/home/mehtama1/eda-tools/magic-8.3.682/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-row_dac_10b-starter-smoke.tcl`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.ext` present `True` bytes `1217`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/row_dac_10b_layout_smoke.spice` present `True` bytes `256`

### sar_readout_12b

- purpose: starter sample/readout boundary with sample input, comparator input, reference switch, and SAR bit placeholders
- cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.mag`
- cell present: `True`
- passed: `True`
- command: `/home/mehtama1/eda-tools/magic-8.3.682/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-sar_readout_12b-starter-smoke.tcl`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.ext` present `True` bytes `1176`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sar_readout_12b_layout_smoke.spice` present `True` bytes `262`

### shared_converter_mux

- purpose: starter shared loading boundary with column inputs and a mux bus
- cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.mag`
- cell present: `True`
- passed: `True`
- command: `/home/mehtama1/eda-tools/magic-8.3.682/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-shared_converter_mux-starter-smoke.tcl`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.ext` present `True` bytes `1174`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/shared_converter_mux_layout_smoke.spice` present `True` bytes `246`

### aimc_converter_macro

- purpose: starter top boundary that names the DAC region, readout region, shared mux region, rails, and external pins
- cell: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.mag`
- cell present: `True`
- passed: `True`
- command: `/home/mehtama1/eda-tools/magic-8.3.682/bin/magic -dnull -noconsole -rcfile /home/mehtama1/eda-tools/pdks/sky130A/libs.tech/magic/sky130A.magicrc /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/extract-aimc_converter_macro-starter-smoke.tcl`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.ext` present `True` bytes `2365`
- output: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice` present `True` bytes `799`

## Refused Claim

does not prove production DAC/ADC/mux quality, DRC clean signoff, LVS, extracted parasitic accuracy, accepted post-layout payload, or model replacement readiness
