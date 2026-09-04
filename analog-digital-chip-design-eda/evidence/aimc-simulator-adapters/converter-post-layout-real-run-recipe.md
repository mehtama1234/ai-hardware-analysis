# Converter Post-Layout Real Run Recipe Artifact

- status: `real_run_recipe_ready_not_evidence`
- current candidate status: `candidate_not_ready_for_strict_submission`
- ready for strict submission: `False`
- step count: `9`
- source checklist: `evidence/aimc-simulator-adapters/converter-post-layout-candidate-fill-checklist.json`
- source handoff manifest: `evidence/aimc-simulator-adapters/converter-post-layout-handoff-manifest.json`

This generated artifact turns the current fill checklist and handoff manifest into one ordered run recipe.

## Ordered Steps

### 1. choose_converter_layout

- action: Choose one converter layout for the 10-bit DAC input and 12-bit ADC readout target.
- proof object: `one named converter macro, extracted view, or silicon measurement object`
- payload fields: `converter_id`

### 2. extract_post_layout_circuit

- action: Produce an inspectable extracted circuit file and place it under the candidate netlist folder.
- proof object: `extracted SPICE, DSPF, SPEF, or equivalent extracted circuit artifact`
- payload fields: `extraction.extracted_netlist`, `extraction.parasitic_format`, `netlist`

### 3. collect_run_models_or_measurement_setup

- action: Place process model files or measurement setup records under the candidate models folder.
- proof object: `model deck, corner include, parasitic include, or measurement setup record`
- payload fields: `simulation.model_files[0]`, `model_file_0`

### 4. run_one_named_experiment

- action: Use one non-placeholder run id for the whole post-layout or measured-silicon run.
- proof object: `shared run identity`
- payload fields: `provenance.created_at`, `provenance.generator_or_lab_notebook`, `provenance.operator`, `provenance.run_id`, `simulation.run_id`, `energy.run_id`, `latency.run_id`, `noise.run_id`, `area.run_id`, `break_even_rerun.run_id`

### 5. record_physical_values

- action: Record energy, latency, noise, area, voltage, temperature, and process or measured condition from that same run.
- proof object: `numbers tied to the extracted converter or measured silicon object`
- payload fields: `energy.adc_energy_per_conversion`, `energy.dac_energy_per_row_drive`, `energy.run_id`, `latency.conversion_time_ns`, `latency.run_id`, `latency.settling_time_ns`, `noise.input_referred_noise`, `noise.output_noise_rms`, `noise.run_id`, `area.adc_area_um2`, `area.dac_area_um2`, `area.run_id`, `simulation.voltage_v`, `simulation.temperature_c`, `simulation.process_corner`, `simulation.command`, `simulation.simulator`

### 6. check_fixed_boundary

- action: Keep the fixed DAC, ADC, noise, and sharing boundary unless the break-even model changes too.
- proof object: `fixed target boundary`
- payload fields: `target_boundary`, `sharing`

### 7. rerun_break_even

- action: Rerun the break-even calculation with extracted or measured values and place the source rerun JSON under the candidate rerun folder.
- proof object: `source break-even rerun artifact`
- payload fields: `break_even_rerun.replacement_decision`, `break_even_rerun.rerun_artifact`, `break_even_rerun.run_id`, `rerun_artifact`

### 8. fill_candidate_payload

- action: Fill payload.json, remove template_only only after all placeholders and file paths are real, then run readiness.
- proof object: `candidate payload ready for strict preflight`
- payload fields: `payload.json`, `template_only`

### 9. strict_submit_only_if_ready

- action: Submit only after readiness reports ready for strict submission.
- proof object: `accepted post-layout rerun and submission report written by the strict command`
- payload fields: `accepted-post-layout`

## Shared Run Id Fields

- `provenance.run_id`
- `simulation.run_id`
- `energy.run_id`
- `latency.run_id`
- `noise.run_id`
- `area.run_id`
- `break_even_rerun.run_id`

## Fixed Target Boundary

- adc_bits: `12`
- columns_served: `4`
- converter_instances: `4`
- dac_bits: `10`
- output_noise_budget_max: `0.004`
- outputs_per_conversion_cost: `16`
- rows_served: `64`

## Commands

- readiness: `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- submit_if_ready: `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Manual Write Boundary

accepted-post-layout must be written only by scripts/submit_converter_post_layout_payload.py

## Refused Claim

does not provide extracted files, measured values, accepted evidence, or analog replacement proof
