# Analog Converter Physical Flow Run

- status: `physical_flow_ready_for_manual_extraction_commands`
- workbench: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench`
- source gate status: `physical_cells_present_waiting_for_extracted_artifacts`
- required cell count: `4`
- present cell count: `4`
- missing cell count: `0`
- blocked command count: `0`
- runnable command count: `4`

## First Principle

A physical flow has to start from shapes, not from intent. If the named cells are missing, the correct result is a stopped run with a precise reason.

The stopped run is still useful because it fixes the next executable boundary. Once the cells exist, the same command list becomes the extraction path that produces the files consumed by candidate preflight.

## Missing Cells


## Blocked Extraction Commands

- none

## Runnable Extraction Commands

- `magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl row_dac_10b.mag` -> `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp`
- `magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl sar_readout_12b.mag` -> `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp`
- `magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl shared_converter_mux.mag` -> `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp`
- `magic -dnull -noconsole -rcfile .magicrc magic-extract-skeleton.tcl aimc_converter_macro.mag` -> `evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json`

## Next After Extraction

- `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- `python3 scripts/build_converter_post_layout_candidate_from_real_run.py --workspace evidence/aimc-simulator-adapters/candidate-post-layout ...`
- `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not fabricate Magic output, extracted netlists, area records, rerun artifacts, or accepted post-layout evidence
