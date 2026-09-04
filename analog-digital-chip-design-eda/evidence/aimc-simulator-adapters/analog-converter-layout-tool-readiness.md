# Analog Converter Layout Tool Readiness

- status: `starter_layout_present_candidate_rehearsal_artifacts_not_accepted`
- all required tools available: `True`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- starter files ready: `True`
- real layout file count: `8`
- candidate post-layout still empty: `False`
- candidate post-layout rehearsal only: `True`

## First Principle

A ready toolchain is not the same as a ready circuit. The tools can open, draw, extract, view, and simulate. The circuit only exists after a concrete layout or imported physical macro exists. This audit separates those two facts.

The useful claim here is narrow: the local machine can start the analog layout work, and the repo now has the starter workbench. The still-missing claim is the physical converter itself.

## Tools

- magic: `/usr/bin/magic`
- xschem: `/usr/local/bin/xschem`
- ngspice: `/usr/bin/ngspice`
- klayout: `/usr/bin/klayout`

## Starter Files

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/README.md` exists `True` bytes `991`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/converter-layout-plan.json` exists `True` bytes `1443`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/magic-extract-skeleton.tcl` exists `True` bytes `295`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/xschem-netlist-skeleton.sh` exists `True` bytes `209`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/post-layout-measurement-record.template.json` exists `True` bytes `1168`

## Real Layout Files Found

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/aimc_converter_macro.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/row_dac_10b.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sar_readout_12b.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/shared_converter_mux.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_balanced_capacitive_isolation_frontend.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_capacitive_isolation_frontend.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_strong_sense_capacitive_frontend.mag`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/cells/sky130_ultra_sense_capacitive_frontend.mag`

## Candidate Evidence Folder

- netlist_files: `2`
- model_files: `1`
- rerun_files: `2`

## Blocking Files Not Yet Present

- aimc_converter_macro.mag or aimc_converter_macro.gds
- aimc_converter_macro_extracted.sp, .dspf, or .spef
- post-layout model/setup file for the same run
- same-run converter break-even rerun JSON

## Refused Claim

does not draw converter layout, does not extract parasitics, does not run DRC/LVS, and does not create accepted post-layout evidence
