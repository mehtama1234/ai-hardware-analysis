# Converter Post-Layout Candidate Fill Checklist

- status: `fill_checklist_ready`
- source audit: `evidence/aimc-simulator-adapters/converter-post-layout-candidate-workspace-audit.json`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- checklist items: `32`

This checklist translates the scaffold audit into the exact edits needed before preflight can pass.

## First Principle

Filling the payload is not clerical work. Each field ties a number to a physical object. The netlist says what circuit was tested. The model files say what electrical world the circuit lived in. Energy, latency, noise, and area say what the converter costs. The rerun artifact says what system decision follows from those costs.

When every placeholder is gone and every referenced file exists, the next question becomes physics: whether the numbers are good enough. Until then the question is simpler: the packet is still incomplete.

## Area

- `area.adc_area_um2` currently `replace-with-positive-area`: Use positive square microns for ADC area.
- `area.dac_area_um2` currently `replace-with-positive-area`: Use positive square microns for DAC area.
- `area.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.

## Break Even

- `break_even_rerun.replacement_decision` currently `replace-with-replace-or-keep-digital-fallback`: Use a real decision such as replace_local_break_even or keep_digital_fallback.
- `break_even_rerun.rerun_artifact` currently `rerun/replace-with-source-break-even-rerun.json`: Point to the source rerun artifact before accepted submission writes its own rerun.
- `break_even_rerun.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.

## Energy

- `energy.adc_energy_per_conversion` currently `replace-with-positive-joules`: Use positive joules for one ADC conversion.
- `energy.dac_energy_per_row_drive` currently `replace-with-positive-joules`: Use positive joules for one DAC row drive.
- `energy.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.

## Extraction

- `extraction.extracted_netlist` currently `netlist/replace-with-extracted-netlist.sp`: Point to the extracted netlist file inside the workspace.
- `extraction.parasitic_format` currently `replace-with-spef-dspf-or-extracted-spice`: Say whether the file is SPEF, DSPF, extracted SPICE, or another concrete extraction format.

## Files

- `netlist` currently `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/replace-with-extracted-netlist.sp`: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.
- `model_file_0` currently `evidence/aimc-simulator-adapters/candidate-post-layout/models/replace-with-model-file.sp`: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.
- `rerun_artifact` currently `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/replace-with-source-break-even-rerun.json`: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.

## Identity

- `converter_id` currently `replace-with-real-converter-id`: Name the exact converter macro, extracted view, or silicon measurement run.

## Latency

- `latency.conversion_time_ns` currently `replace-with-positive-ns`: Use positive nanoseconds for the ADC decision window.
- `latency.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.
- `latency.settling_time_ns` currently `replace-with-positive-ns`: Use positive nanoseconds for the row/sample settling window.

## Noise

- `noise.input_referred_noise` currently `replace-with-input-referred-noise`: Use a numeric input-referred noise value.
- `noise.output_noise_rms` currently `replace-with-rms-at-or-below-0.004`: Use a numeric RMS value at or below 0.004.
- `noise.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.

## Provenance

- `provenance.created_at` currently `replace-with-run-timestamp`: Record the run timestamp.
- `provenance.generator_or_lab_notebook` currently `replace-with-script-or-notebook`: Name the script, notebook, or lab record.
- `provenance.operator` currently `replace-with-person-or-ci-job`: Name the person or CI job responsible for the run.
- `provenance.run_id` currently `replace-with-shared-run-id`: Name the one post-layout or measured run that produced all accepted converter values.

## Simulation

- `simulation.command` currently `replace-with-reproducible-command`: Record the command or lab procedure so the run can be repeated or audited.
- `simulation.model_files[0]` currently `models/replace-with-model-file.sp`: Point to an existing model or measurement setup file.
- `simulation.process_corner` currently `replace-with-corner-or-measurement-condition`: Name the process corner or measured operating condition.
- `simulation.run_id` currently `replace-with-shared-run-id`: Use the same run id as provenance.run_id.
- `simulation.simulator` currently `replace-with-simulator`: Name the simulator or measurement system that produced the values.
- `simulation.temperature_c` currently `replace-with-numeric-temperature`: Use a numeric temperature.
- `simulation.voltage_v` currently `replace-with-numeric-supply`: Use a numeric supply voltage.

## Next Commands

- `python3 scripts/audit_converter_post_layout_candidate_workspace.py`
- `python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not supply real values, does not validate physics, does not submit evidence, and does not replace converter break-even assumptions
