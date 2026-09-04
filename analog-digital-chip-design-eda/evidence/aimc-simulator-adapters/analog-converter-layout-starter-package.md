# Analog Converter Layout Starter Package

- status: `starter_package_written_not_extracted_evidence`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- starter file count: `5`
- strict payload still waiting for real files: `False`

## First Principle

A converter layout is not a better paragraph about the converter. It is the physical shape that creates the capacitance, resistance, area, reference loading, mux loading, and rail current that the simulator must then see. The starter package names the cells and run files so the next work can create that physical object instead of adding more claims around it.

The starter files stay in the analog lab workbench. The strict candidate folder stays empty until a real extraction or measured run exists.

## Starter Files

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/README.md` (991 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/converter-layout-plan.json` (1443 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/magic-extract-skeleton.tcl` (295 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/xschem-netlist-skeleton.sh` (209 bytes)
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/post-layout-measurement-record.template.json` (1168 bytes)

## Physical Cells Named

- `row_dac_10b`
- `sar_readout_12b`
- `shared_converter_mux`
- `aimc_converter_macro`

## Candidate Evidence Folder After Write

- netlist_files: `2`
- model_files: `1`
- rerun_files: `2`

## Next Real Actions

- draw or import the four named converter cells
- run DRC/LVS or record why the selected technology setup cannot support it yet
- extract one post-layout netlist for the converter macro
- run one named post-layout simulation using that extracted object
- rerun converter break-even with the extracted values from the same run
- build and preflight the strict candidate payload

## Refused Claim

does not create layout, does not run extraction, does not write candidate evidence files, and does not create accepted post-layout evidence
