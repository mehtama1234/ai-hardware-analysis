# Converter Post-Layout Candidate Workspace Audit

- status: `candidate_workspace_still_scaffold`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- template only: `True`
- placeholder count: `29`
- missing or unresolved file count: `3`

This audit tells whether the staging folder is still a scaffold or is ready for preflight.

## First Principle

A candidate workspace becomes useful only when every name points to a real object. A placeholder field means the payload is still an intention. A missing file means the payload cannot be inspected. A `template_only` flag means the packet is deliberately barred from submission.

The audit does not judge whether the converter is good. It only asks whether the packet has stopped being a scaffold.

## Placeholder Fields

- `area.adc_area_um2`: `replace-with-positive-area`
- `area.dac_area_um2`: `replace-with-positive-area`
- `area.run_id`: `replace-with-shared-run-id`
- `break_even_rerun.replacement_decision`: `replace-with-replace-or-keep-digital-fallback`
- `break_even_rerun.rerun_artifact`: `rerun/replace-with-source-break-even-rerun.json`
- `break_even_rerun.run_id`: `replace-with-shared-run-id`
- `converter_id`: `replace-with-real-converter-id`
- `energy.adc_energy_per_conversion`: `replace-with-positive-joules`
- `energy.dac_energy_per_row_drive`: `replace-with-positive-joules`
- `energy.run_id`: `replace-with-shared-run-id`
- `extraction.extracted_netlist`: `netlist/replace-with-extracted-netlist.sp`
- `extraction.parasitic_format`: `replace-with-spef-dspf-or-extracted-spice`
- `latency.conversion_time_ns`: `replace-with-positive-ns`
- `latency.run_id`: `replace-with-shared-run-id`
- `latency.settling_time_ns`: `replace-with-positive-ns`
- `noise.input_referred_noise`: `replace-with-input-referred-noise`
- `noise.output_noise_rms`: `replace-with-rms-at-or-below-0.004`
- `noise.run_id`: `replace-with-shared-run-id`
- `provenance.created_at`: `replace-with-run-timestamp`
- `provenance.generator_or_lab_notebook`: `replace-with-script-or-notebook`
- plus `9` more

## Missing Or Unresolved Files

- `netlist`: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/replace-with-extracted-netlist.sp`
- `model_file_0`: `evidence/aimc-simulator-adapters/candidate-post-layout/models/replace-with-model-file.sp`
- `rerun_artifact`: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/replace-with-source-break-even-rerun.json`

## Next Command

`python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not validate physics, does not submit evidence, and does not replace converter break-even assumptions
