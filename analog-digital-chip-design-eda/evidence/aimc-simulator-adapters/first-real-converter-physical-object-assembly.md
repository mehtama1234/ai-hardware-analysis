# First Real Converter Physical Object Assembly

- status: `b1_physical_object_assembled_from_starter_extractions_not_accepted_evidence`
- candidate id: `aimc_readout_candidate_001`
- netlist: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- manifest: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_manifest.json`

## First Principle

The first converter blocker asks for one object. A number such as energy or noise only has meaning if it belongs to a named circuit. This assembly creates that named circuit from the local extracted starter cells.

The result is still narrow. It closes the object-name problem, not the measurement problem. The next blockers must still measure energy, latency, noise, and area on this same object.

## Source Extractions

- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/row_dac_10b_layout_smoke.spice`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sar_readout_12b_layout_smoke.spice`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/shared_converter_mux_layout_smoke.spice`
- `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice`

## Included Parts

- `row_dac`
- `sar_readout`
- `shared_mux`
- `references`
- `sample_path`

## Refused Claim

does not prove energy, latency, noise, area, break-even replacement, or accepted post-layout converter evidence
