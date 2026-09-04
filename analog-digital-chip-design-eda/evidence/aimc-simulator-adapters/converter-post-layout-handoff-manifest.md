# Converter Post-Layout Handoff Manifest

- status: `handoff_manifest_ready`
- current candidate status: `candidate_not_ready_for_strict_submission`
- ready for strict submission: `False`
- required file count: `3`
- numeric value count: `19`
- identity and provenance count: `10`

This manifest is the handoff sheet for the person or tool that will produce real converter evidence. It names the files to place in the workspace, the numbers to put in the payload, the fixed target boundary, and the commands to run after filling it.

## First Principle

A handoff is useful only when the receiver can act without guessing. The converter evidence packet needs inspectable objects and concrete values. The objects are the extracted netlist, model files, and source rerun artifact. The values are energy, latency, noise, area, supply, temperature, and the replacement decision.

The manifest does not lower the evidence bar. It makes the bar easy to see.

## Missing Files

- `netlist`: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/replace-with-extracted-netlist.sp`
- `model_file_0`: `evidence/aimc-simulator-adapters/candidate-post-layout/models/replace-with-model-file.sp`
- `rerun_artifact`: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/replace-with-source-break-even-rerun.json`

## Numeric Values

- `area.adc_area_um2`: Use positive square microns for ADC area.
- `area.dac_area_um2`: Use positive square microns for DAC area.
- `area.run_id`: Use the same run id as provenance.run_id.
- `energy.adc_energy_per_conversion`: Use positive joules for one ADC conversion.
- `energy.dac_energy_per_row_drive`: Use positive joules for one DAC row drive.
- `energy.run_id`: Use the same run id as provenance.run_id.
- `latency.conversion_time_ns`: Use positive nanoseconds for the ADC decision window.
- `latency.run_id`: Use the same run id as provenance.run_id.
- `latency.settling_time_ns`: Use positive nanoseconds for the row/sample settling window.
- `noise.input_referred_noise`: Use a numeric input-referred noise value.
- `noise.output_noise_rms`: Use a numeric RMS value at or below 0.004.
- `noise.run_id`: Use the same run id as provenance.run_id.
- `simulation.command`: Record the command or lab procedure so the run can be repeated or audited.
- `simulation.model_files[0]`: Point to an existing model or measurement setup file.
- `simulation.process_corner`: Name the process corner or measured operating condition.
- `simulation.run_id`: Use the same run id as provenance.run_id.
- `simulation.simulator`: Name the simulator or measurement system that produced the values.
- `simulation.temperature_c`: Use a numeric temperature.
- `simulation.voltage_v`: Use a numeric supply voltage.

## Identity And Provenance

- `break_even_rerun.replacement_decision`: Use a real decision such as replace_local_break_even or keep_digital_fallback.
- `break_even_rerun.rerun_artifact`: Point to the source rerun artifact before accepted submission writes its own rerun.
- `break_even_rerun.run_id`: Use the same run id as provenance.run_id.
- `converter_id`: Name the exact converter macro, extracted view, or silicon measurement run.
- `extraction.extracted_netlist`: Point to the extracted netlist file inside the workspace.
- `extraction.parasitic_format`: Say whether the file is SPEF, DSPF, extracted SPICE, or another concrete extraction format.
- `provenance.created_at`: Record the run timestamp.
- `provenance.generator_or_lab_notebook`: Name the script, notebook, or lab record.
- `provenance.operator`: Name the person or CI job responsible for the run.
- `provenance.run_id`: Name the one post-layout or measured run that produced all accepted converter values.

## Fixed Target Boundary

- dac_bits: `10`
- adc_bits: `12`
- output_noise_budget_max: `0.004`
- rows_served: `64`
- columns_served: `4`
- outputs_per_conversion_cost: `16`
- converter_instances: `4`

## Commands

- fill_workspace: `edit evidence/aimc-simulator-adapters/candidate-post-layout/payload.json and place files under netlist/, models/, and rerun/`
- readiness: `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- submit_if_ready: `python3 scripts/submit_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not provide the real files or values, does not submit evidence, and does not prove analog replacement
