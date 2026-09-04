# Converter Post-Layout Evidence Contract

This file defines the exact payload that must exist before converter break-even assumptions can be replaced.

- status: `post_layout_contract_defined_placeholder_not_claim_ready`
- schema complete: `True`
- claim-ready to replace break-even: `False`
- placeholder refuses replacement: `True`
- post-layout schema: `sources/evidence/converter-post-layout-evidence-schema.json`
- dry-run placeholder payload: `evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.placeholder.json`

## First-Principles Reading

Post-layout evidence is not just a stronger number. It is a different object. The schematic says what circuit was intended. The extracted netlist says what circuit the geometry actually made after wires and parasitics were added.

For the converter to replace break-even assumptions, the payload must tie the same target to four things at once: extracted circuit contents, simulation conditions, measured energy and timing, and a break-even rerun that actually uses those extracted values.

## Required Top-Level Fields

- `result_type`
- `converter_id`
- `measurement_level`
- `target_boundary`
- `extraction`
- `simulation`
- `energy`
- `latency`
- `noise`
- `area`
- `sharing`
- `break_even_rerun`
- `provenance`
- `claim_boundary`

## Required Extraction Fields

- `extracted_netlist`
- `parasitic_format`
- `includes_row_dac`
- `includes_sar_readout`
- `includes_shared_mux`
- `includes_references`
- `includes_sample_path`

## Required Simulation Fields

- `simulator`
- `command`
- `process_corner`
- `voltage_v`
- `temperature_c`
- `model_files`
- `run_id`

## Required Energy Fields

- `adc_energy_per_conversion`
- `dac_energy_per_row_drive`
- `energy_unit`
- `method`
- `run_id`

## Required Latency Fields

- `adc_comparisons`
- `conversion_time_ns`
- `settling_time_ns`
- `method`
- `run_id`

## Required Noise Fields

- `output_noise_rms`
- `input_referred_noise`
- `meets_output_noise_budget`
- `method`
- `run_id`

## Required Area Fields

- `adc_area_um2`
- `dac_area_um2`
- `replication_or_sharing_rule`
- `method`
- `run_id`

## Required Break-Even Rerun Fields

- `rerun_artifact`
- `uses_extracted_energy`
- `uses_extracted_latency`
- `uses_extracted_noise`
- `uses_extracted_area`
- `uses_same_sharing_rule`
- `replacement_decision`
- `run_id`

## Required Provenance Fields

- `created_at`
- `source_schema`
- `run_id`

## Same-Run Rule

provenance.run_id, simulation.run_id, energy.run_id, latency.run_id, noise.run_id, area.run_id, and break_even_rerun.run_id must name the same non-placeholder post-layout or measured run.

## Refused Claim

does not claim extracted netlists, post-layout simulation results, measured silicon, DRC/LVS signoff, or board energy exist
