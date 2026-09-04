# Converter Post-Layout Blocker Ledger

- status: `blocked_on_real_post_layout_evidence`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- preflight status: `not_ready_for_strict_submission`
- template only: `True`
- blocker count: `45`

This ledger is the current reason the converter cannot be accepted as post-layout evidence. It reads the candidate workspace and strict preflight result, then turns each failure into a concrete evidence action.

## First Principle

A converter claim is not made true by a payload shape. It becomes testable only when a value is tied to a physical object. The physical objects are the extracted netlist, the model files, and the break-even rerun artifact. The values are energy, time, noise, area, supply, temperature, and the replace-or-fallback decision.

Until those objects and values are real, the right answer is not a weaker claim. The right answer is a clear list of blockers.

## Blockers By Category

- `claim_boundary`: `8`
- `missing_file`: `6`
- `noise_boundary`: `3`
- `numeric_boundary`: `8`
- `placeholder`: `20`

## Current Blockers

### area.adc_area_um2

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-positive-area`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### area.run_id

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-shared-run-id`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### break_even_rerun.replacement_decision

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-replace-or-keep-digital-fallback`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### break_even_rerun.rerun_artifact

- source: `workspace_audit`
- category: `placeholder`
- current value: `rerun/replace-with-source-break-even-rerun.json`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### converter_id

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-real-converter-id`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### energy.adc_energy_per_conversion

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-positive-joules`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### extraction.extracted_netlist

- source: `workspace_audit`
- category: `placeholder`
- current value: `netlist/replace-with-extracted-netlist.sp`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### extraction.parasitic_format

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-spef-dspf-or-extracted-spice`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### latency.conversion_time_ns

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-positive-ns`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### noise.input_referred_noise

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-input-referred-noise`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### noise.output_noise_rms

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-rms-at-or-below-0.004`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### provenance.created_at

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-run-timestamp`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### provenance.generator_or_lab_notebook

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-script-or-notebook`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### provenance.operator

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-person-or-ci-job`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.command

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-reproducible-command`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.model_files[0]

- source: `workspace_audit`
- category: `placeholder`
- current value: `models/replace-with-model-file.sp`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.process_corner

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-corner-or-measurement-condition`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.simulator

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-simulator`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.temperature_c

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-numeric-temperature`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### simulation.voltage_v

- source: `workspace_audit`
- category: `placeholder`
- current value: `replace-with-numeric-supply`
- why it blocks: A placeholder is a promise to fill evidence later, not evidence.
- evidence action: Replace this field with a real value from the extracted simulation or measured silicon run.

### netlist

- source: `workspace_audit`
- category: `missing_file`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/replace-with-extracted-netlist.sp`
- why it blocks: The payload cannot be inspected if the named evidence file is absent.
- evidence action: Supply the referenced file and keep the payload path inspectable.

### model_file_0

- source: `workspace_audit`
- category: `missing_file`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/models/replace-with-model-file.sp`
- why it blocks: The payload cannot be inspected if the named evidence file is absent.
- evidence action: Supply the referenced file and keep the payload path inspectable.

### rerun_artifact

- source: `workspace_audit`
- category: `missing_file`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/replace-with-source-break-even-rerun.json`
- why it blocks: The payload cannot be inspected if the named evidence file is absent.
- evidence action: Run the source break-even calculation with the extracted values and place the resulting JSON in the candidate rerun folder.

### simulation.voltage_v

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `simulation.voltage_v must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### simulation.temperature_c

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `simulation.temperature_c must be numeric`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### energy.adc_energy_per_conversion

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `energy.adc_energy_per_conversion must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### energy.dac_energy_per_row_drive

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `energy.dac_energy_per_row_drive must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### latency.conversion_time_ns

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `latency.conversion_time_ns must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### latency.settling_time_ns

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `latency.settling_time_ns must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### noise.output_noise_rms

- source: `strict_preflight`
- category: `noise_boundary`
- current value: `noise.output_noise_rms must be numeric`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Use the measured or simulated readout noise from the same converter path and keep output_noise_rms at or below 0.004.

### noise.input_referred_noise

- source: `strict_preflight`
- category: `noise_boundary`
- current value: `noise.input_referred_noise must be numeric`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Use the measured or simulated readout noise from the same converter path and keep output_noise_rms at or below 0.004.

### area.adc_area_um2

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `area.adc_area_um2 must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### area.dac_area_um2

- source: `strict_preflight`
- category: `numeric_boundary`
- current value: `area.dac_area_um2 must be positive`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Replace the placeholder with a numeric value from the same post-layout simulation or measured run.

### template payloads cannot be submitted

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `template payloads cannot be submitted`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### extraction.extracted_netlist

- source: `strict_preflight`
- category: `missing_file`
- current value: `extraction.extracted_netlist must point to an existing file`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Place the extracted post-layout converter netlist in the candidate netlist folder and point extraction.extracted_netlist at it.

### simulation.model_files[0]

- source: `strict_preflight`
- category: `missing_file`
- current value: `simulation.model_files[0] must point to an existing file`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Place the process, parasitic, or measurement model file in the candidate models folder and list it in simulation.model_files.

### break_even_rerun.rerun_artifact

- source: `strict_preflight`
- category: `missing_file`
- current value: `break_even_rerun.rerun_artifact must point to an existing file`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Run the source break-even calculation with the extracted values and place the resulting JSON in the candidate rerun folder.

### provenance.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `provenance.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### simulation.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `simulation.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### energy.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `energy.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### latency.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `latency.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### noise.run_id

- source: `strict_preflight`
- category: `noise_boundary`
- current value: `noise.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Use the measured or simulated readout noise from the same converter path and keep output_noise_rms at or below 0.004.

### area.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `area.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### break_even_rerun.run_id

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `break_even_rerun.run_id must not be a placeholder`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

### template payloads cannot pass same-run consistency

- source: `strict_preflight`
- category: `claim_boundary`
- current value: `template payloads cannot pass same-run consistency`
- why it blocks: Strict preflight rejects payloads whose numbers, files, or boundaries cannot support a replacement decision.
- evidence action: Fix the claim boundary so the payload says only what the evidence can support.

## Fixed Target Boundary

- adc_bits: `12`
- columns_served: `4`
- converter_instances: `4`
- dac_bits: `10`
- output_noise_budget_max: `0.004`
- outputs_per_conversion_cost: `16`
- rows_served: `64`

## Next Command

`python3 scripts/run_converter_post_layout_candidate_readiness.py`

## Refused Claim

does not supply extracted files, measured values, accepted post-layout evidence, or analog replacement proof
