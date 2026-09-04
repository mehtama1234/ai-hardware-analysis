# Converter Post-Layout Candidate Edit Plan

- status: `candidate_edit_plan_ready`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- edit count: `32`
- blocked edit count: `32`

This plan says how to edit the candidate payload once real post-layout or measured converter evidence exists. It keeps the fill work tied to evidence sources, accepted value shapes, and the command that checks the result.

## First Principle

Editing the payload is part of the proof. Each value must come from the same converter object. If energy comes from one run, noise from another, and area from a guess, the package is only a collection of numbers. The candidate becomes evidence only when the fields point back to one physical converter path.

The plan therefore starts with inspectable files, then fills identity and simulation conditions, then fills cost values, and only then records the break-even decision.

## Recommended Order

- `files`
- `identity`
- `simulation`
- `extraction`
- `energy`
- `latency`
- `noise`
- `area`
- `break_even`
- `provenance`

## Field Edits

### area.adc_area_um2

- group: `area`
- current value: `replace-with-positive-area`
- evidence source: layout area report
- accepted value shape: positive square microns
- validator check: Use positive square microns for ADC area.
- currently blocked: `True`

### area.dac_area_um2

- group: `area`
- current value: `replace-with-positive-area`
- evidence source: layout area report
- accepted value shape: positive square microns
- validator check: Use positive square microns for DAC area.
- currently blocked: `True`

### area.run_id

- group: `area`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### break_even_rerun.replacement_decision

- group: `break_even`
- current value: `replace-with-replace-or-keep-digital-fallback`
- evidence source: source break-even rerun summary
- accepted value shape: replace_converter_break_even_assumption or keep_digital_fallback
- validator check: Use a real decision such as replace_local_break_even or keep_digital_fallback.
- currently blocked: `True`

### break_even_rerun.rerun_artifact

- group: `break_even`
- current value: `rerun/replace-with-source-break-even-rerun.json`
- evidence source: source break-even rerun with extracted values
- accepted value shape: path to an existing rerun JSON
- validator check: Point to the source rerun artifact before accepted submission writes its own rerun.
- currently blocked: `True`

### break_even_rerun.run_id

- group: `break_even`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### converter_id

- group: `identity`
- current value: `replace-with-real-converter-id`
- evidence source: layout run name or silicon run id
- accepted value shape: non-empty string naming one converter object
- validator check: Name the exact converter macro, extracted view, or silicon measurement run.
- currently blocked: `True`

### energy.adc_energy_per_conversion

- group: `energy`
- current value: `replace-with-positive-joules`
- evidence source: supply integration over ADC conversion window
- accepted value shape: positive joules
- validator check: Use positive joules for one ADC conversion.
- currently blocked: `True`

### energy.dac_energy_per_row_drive

- group: `energy`
- current value: `replace-with-positive-joules`
- evidence source: supply integration over row-drive window
- accepted value shape: positive joules
- validator check: Use positive joules for one DAC row drive.
- currently blocked: `True`

### energy.run_id

- group: `energy`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### extraction.extracted_netlist

- group: `extraction`
- current value: `netlist/replace-with-extracted-netlist.sp`
- evidence source: post-layout extraction output
- accepted value shape: path to an existing extracted netlist file
- validator check: Point to the extracted netlist file inside the workspace.
- currently blocked: `True`

### extraction.parasitic_format

- group: `extraction`
- current value: `replace-with-spef-dspf-or-extracted-spice`
- evidence source: extraction tool output type
- accepted value shape: SPEF, DSPF, extracted SPICE, or a similarly concrete format
- validator check: Say whether the file is SPEF, DSPF, extracted SPICE, or another concrete extraction format.
- currently blocked: `True`

### latency.conversion_time_ns

- group: `latency`
- current value: `replace-with-positive-ns`
- evidence source: ADC decision timing measurement
- accepted value shape: positive nanoseconds
- validator check: Use positive nanoseconds for the ADC decision window.
- currently blocked: `True`

### latency.run_id

- group: `latency`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### latency.settling_time_ns

- group: `latency`
- current value: `replace-with-positive-ns`
- evidence source: row/sample settling measurement
- accepted value shape: positive nanoseconds
- validator check: Use positive nanoseconds for the row/sample settling window.
- currently blocked: `True`

### noise.input_referred_noise

- group: `noise`
- current value: `replace-with-input-referred-noise`
- evidence source: same noise result referred to the input boundary
- accepted value shape: numeric value
- validator check: Use a numeric input-referred noise value.
- currently blocked: `True`

### noise.output_noise_rms

- group: `noise`
- current value: `replace-with-rms-at-or-below-0.004`
- evidence source: readout noise measurement from same path
- accepted value shape: number at or below 0.004
- validator check: Use a numeric RMS value at or below 0.004.
- currently blocked: `True`

### noise.run_id

- group: `noise`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### provenance.created_at

- group: `provenance`
- current value: `replace-with-run-timestamp`
- evidence source: run metadata
- accepted value shape: timestamp for the run
- validator check: Record the run timestamp.
- currently blocked: `True`

### provenance.generator_or_lab_notebook

- group: `provenance`
- current value: `replace-with-script-or-notebook`
- evidence source: run metadata
- accepted value shape: script, notebook, lab record, or CI job
- validator check: Name the script, notebook, or lab record.
- currently blocked: `True`

### provenance.operator

- group: `provenance`
- current value: `replace-with-person-or-ci-job`
- evidence source: run metadata
- accepted value shape: person, tool, or CI job that produced the evidence
- validator check: Name the person or CI job responsible for the run.
- currently blocked: `True`

### provenance.run_id

- group: `provenance`
- current value: `replace-with-shared-run-id`
- evidence source: run metadata
- accepted value shape: same non-empty run id used by simulation, energy, latency, noise, area, and break_even_rerun
- validator check: Name the one post-layout or measured run that produced all accepted converter values.
- currently blocked: `True`

### simulation.command

- group: `simulation`
- current value: `replace-with-reproducible-command`
- evidence source: reproducible run record
- accepted value shape: command, script path, or lab procedure id
- validator check: Record the command or lab procedure so the run can be repeated or audited.
- currently blocked: `True`

### simulation.model_files[0]

- group: `simulation`
- current value: `models/replace-with-model-file.sp`
- evidence source: process, parasitic, or measurement model
- accepted value shape: path to an existing model/setup file
- validator check: Point to an existing model or measurement setup file.
- currently blocked: `True`

### simulation.process_corner

- group: `simulation`
- current value: `replace-with-corner-or-measurement-condition`
- evidence source: model deck or measured condition
- accepted value shape: corner name or measured operating condition
- validator check: Name the process corner or measured operating condition.
- currently blocked: `True`

### simulation.run_id

- group: `simulation`
- current value: `replace-with-shared-run-id`
- evidence source: same run as provenance
- accepted value shape: must equal provenance.run_id
- validator check: Use the same run id as provenance.run_id.
- currently blocked: `True`

### simulation.simulator

- group: `simulation`
- current value: `replace-with-simulator`
- evidence source: simulation or measurement setup
- accepted value shape: non-empty simulator, lab setup, or measurement system name
- validator check: Name the simulator or measurement system that produced the values.
- currently blocked: `True`

### simulation.temperature_c

- group: `simulation`
- current value: `replace-with-numeric-temperature`
- evidence source: same run as energy/noise/latency
- accepted value shape: number in Celsius
- validator check: Use a numeric temperature.
- currently blocked: `True`

### simulation.voltage_v

- group: `simulation`
- current value: `replace-with-numeric-supply`
- evidence source: same run as energy/noise/latency
- accepted value shape: positive number in volts
- validator check: Use a numeric supply voltage.
- currently blocked: `True`

### netlist

- group: `files`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/replace-with-extracted-netlist.sp`
- evidence source: post-layout extraction output
- accepted value shape: create the referenced netlist file
- validator check: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.
- currently blocked: `True`

### model_file_0

- group: `files`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/models/replace-with-model-file.sp`
- evidence source: process, parasitic, or measurement model
- accepted value shape: create the referenced model/setup file
- validator check: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.
- currently blocked: `True`

### rerun_artifact

- group: `files`
- current value: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/replace-with-source-break-even-rerun.json`
- evidence source: source break-even rerun
- accepted value shape: create the referenced rerun JSON
- validator check: Create or copy this referenced file into the candidate workspace, then update payload.json if the file name changes.
- currently blocked: `True`

## Check Command

`python3 scripts/run_converter_post_layout_candidate_readiness.py`

## Refused Claim

does not create post-layout files, does not invent values, does not submit evidence, and does not prove analog replacement
