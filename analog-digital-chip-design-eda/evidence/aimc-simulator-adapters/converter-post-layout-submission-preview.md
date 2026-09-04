# Converter Post-Layout Submission Preview

- status: `blocked_before_submission`
- source payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- output dir: `evidence/aimc-simulator-adapters/accepted-post-layout`
- converter id ready: `False`
- would write accepted evidence: `False`
- strict issue count: `22`

This preview answers one practical question before submission: if the strict submitter ran on this payload, would it write accepted evidence, and which files would it write?

## First Principle

Submission should be boring. The only time it should create accepted evidence is when the payload already names one real converter, one real run, real referenced files, and real numeric values. A preview step lets a reviewer inspect that boundary without creating the accepted directory.

## Would Write Files

- `evidence/aimc-simulator-adapters/accepted-post-layout/blocked-until-real-converter-id.break-even-rerun.json`
- `evidence/aimc-simulator-adapters/accepted-post-layout/blocked-until-real-converter-id.submission-report.json`

## Submission Command

`python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Strict Issues

- `numeric_boundary`: simulation.voltage_v must be positive
- `numeric_boundary`: simulation.temperature_c must be numeric
- `numeric_boundary`: energy.adc_energy_per_conversion must be positive
- `numeric_boundary`: energy.dac_energy_per_row_drive must be positive
- `numeric_boundary`: latency.conversion_time_ns must be positive
- `numeric_boundary`: latency.settling_time_ns must be positive
- `numeric_boundary`: noise.output_noise_rms must be numeric
- `numeric_boundary`: noise.input_referred_noise must be numeric
- `numeric_boundary`: area.adc_area_um2 must be positive
- `numeric_boundary`: area.dac_area_um2 must be positive
- `missing_file`: extraction.extracted_netlist must point to an existing file
- `missing_file`: simulation.model_files[0] must point to an existing file
- `missing_file`: break_even_rerun.rerun_artifact must point to an existing file
- `same_run_identity`: provenance.run_id must not be a placeholder
- `same_run_identity`: simulation.run_id must not be a placeholder
- `same_run_identity`: energy.run_id must not be a placeholder
- `same_run_identity`: latency.run_id must not be a placeholder
- `same_run_identity`: noise.run_id must not be a placeholder
- `same_run_identity`: area.run_id must not be a placeholder
- `same_run_identity`: break_even_rerun.run_id must not be a placeholder
- `template_boundary`: template payloads cannot pass same-run consistency
- `template_boundary`: template payloads cannot be submitted

## Refused Claim

does not submit evidence, does not create accepted-post-layout, does not run break-even, and does not prove post-layout converter replacement
