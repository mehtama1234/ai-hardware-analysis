# Analog Converter Layout Work Order

- status: `layout_work_order_ready_waiting_for_converter_layout`
- all starting SPICE decks exist: `True`
- repo-local analog layout file count: `9`
- deliverable count: `5`

## First Principle

The existing SPICE decks test behavior. A post-layout claim needs geometry. Geometry adds wire capacitance, wire resistance, device area, placement distance, reference loading, mux loading, and extracted timing. The work order exists to move from behavior decks to extracted converter objects without confusing the two.

## Starting Decks

- `labs/analog/analog-in-memory-foundation-model-hardware/spice/row_dac_settling_10bit.sp` exists `True`
- `labs/analog/analog-in-memory-foundation-model-hardware/spice/sar_readout_12bit.sp` exists `True`
- `labs/analog/analog-in-memory-foundation-model-hardware/spice/shared_converter_loading.sp` exists `True`
- `labs/analog/analog-in-memory-foundation-model-hardware/spice/converter_supply_energy.sp` exists `True`

## Deliverables

### row_dac_layout

- target: 10-bit row-drive DAC path
- candidate file: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp`
- payload fields: `extraction.extracted_netlist, energy.dac_energy_per_row_drive, latency.settling_time_ns`
- acceptance: extracted netlist exists, includes row DAC path, and reports positive DAC row-drive energy and settling time

### sar_readout_layout

- target: 12-bit sample/readout ADC path
- candidate file: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp`
- payload fields: `energy.adc_energy_per_conversion, latency.conversion_time_ns, noise.output_noise_rms`
- acceptance: extracted netlist exists, includes sample path and SAR readout, and output noise is at or below 0.004 RMS

### shared_mux_layout

- target: shared converter mux and loading path
- candidate file: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp`
- payload fields: `sharing.outputs_per_conversion_cost, area.replication_or_sharing_rule`
- acceptance: extracted netlist includes shared mux loading and preserves the 16-output sharing rule used by break-even

### converter_macro_area

- target: combined DAC, ADC, reference, mux, and sample layout boundary
- candidate file: `evidence/aimc-simulator-adapters/candidate-post-layout/models/converter_layout_area_record.json`
- payload fields: `area.adc_area_um2, area.dac_area_um2`
- acceptance: positive ADC and DAC area values come from the layout or extracted macro boundary

### same_run_break_even_rerun

- target: break-even decision using extracted converter values
- candidate file: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/converter-post-layout-break-even-rerun.json`
- payload fields: `break_even_rerun.rerun_artifact, break_even_rerun.replacement_decision, break_even_rerun.run_id`
- acceptance: rerun artifact uses extracted energy, latency, noise, area, and the same sharing rule as the payload

## Strict Payload Commands After Layout

- `python3 scripts/build_converter_post_layout_candidate_from_real_run.py --workspace evidence/aimc-simulator-adapters/candidate-post-layout ...`
- `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not create layout, does not create extracted netlists, does not fill measured values, and does not submit accepted post-layout evidence
