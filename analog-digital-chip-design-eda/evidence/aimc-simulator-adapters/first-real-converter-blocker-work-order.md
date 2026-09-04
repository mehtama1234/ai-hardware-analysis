# First Real Converter Blocker Work Order

- status: `six_experiment_work_order_ready`
- candidate id: `aimc_readout_candidate_001`
- run id: `aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001`
- rehearsal strict issue count: `15`
- work item count: `6`

## First Principle

The remaining failures are not one problem. They are six different measurements or build tasks. A complete converter claim needs one physical object, energy, latency, noise, area, and a rerun that uses those values.

Each item below says what question must be answered, what experiment answers it, what file should be produced, and which payload fields that file unlocks.

## Work Items

### B1. converter_object

- status: `open`
- question: What physical object is the converter/readout candidate?
- experiment: Build or select one extracted netlist that includes row DAC, SAR/readout, shared mux, references, and sample path under one subckt or manifest.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- acceptance check: strict payload no longer reports any extraction.includes_* failure and the netlist path exists
- simple meaning: The candidate must be one inspectable circuit object, not separate loose evidence fragments.
- payload fields:
  - `extraction.extracted_netlist`
  - `extraction.includes_row_dac`
  - `extraction.includes_sar_readout`
  - `extraction.includes_shared_mux`
  - `extraction.includes_references`
  - `extraction.includes_sample_path`

### B2. adc_energy

- status: `open`
- question: How much supply energy does the readout decision spend?
- experiment: Run a supply-current integration deck over the ADC/comparator decision window for the same run id.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-energy.json`
- acceptance check: ADC and DAC energy are positive joule values and energy.run_id equals provenance.run_id
- simple meaning: The converter cost is voltage times supply current over the event, not a guessed label.
- payload fields:
  - `energy.adc_energy_per_conversion`
  - `energy.dac_energy_per_row_drive`
  - `energy.method`
  - `energy.run_id`

### B3. conversion_latency

- status: `open`
- question: When is the digital value safe to read?
- experiment: Measure row settling plus readout/comparator/SAR decision time in one transient run.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-latency.json`
- acceptance check: conversion_time_ns and settling_time_ns are positive and measured from the same command/run id
- simple meaning: Latency is the wait between asking for a value and having a value the digital side can trust.
- payload fields:
  - `latency.conversion_time_ns`
  - `latency.settling_time_ns`
  - `latency.method`
  - `latency.run_id`

### B4. noise

- status: `open`
- question: How uncertain is the produced digital value?
- experiment: Measure or simulate output noise and input-referred noise at the readout boundary for the same circuit and run id.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-noise.json`
- acceptance check: output_noise_rms is numeric, input_referred_noise is numeric, and output_noise_rms <= 0.004
- simple meaning: The model sees noise as a wrong or uncertain number, so the converter must keep that uncertainty inside the model budget.
- payload fields:
  - `noise.output_noise_rms`
  - `noise.input_referred_noise`
  - `noise.meets_output_noise_budget`
  - `noise.run_id`

### B5. area

- status: `open`
- question: How much physical space does the ADC/readout and DAC/row-drive path consume?
- experiment: Compute area from the selected physical cells or extracted layout boundary for the same candidate object.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-area.json`
- acceptance check: ADC and DAC area are positive square-micron values tied to the same candidate id
- simple meaning: Area is the chip space paid for the circuit; if it must be repeated too often, the system cost changes.
- payload fields:
  - `area.adc_area_um2`
  - `area.dac_area_um2`
  - `area.method`
  - `area.run_id`

### B6. break_even

- status: `open`
- question: Do the measured converter numbers change the analog-versus-digital decision?
- experiment: Rerun converter break-even using the measured energy, latency, noise, area, and same sharing rule.
- output artifact: `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/aimc_readout_candidate_001_break_even_rerun.json`
- acceptance check: rerun artifact exists, all uses_extracted_* fields are true, and break_even_rerun.run_id equals provenance.run_id
- simple meaning: Accepted evidence must change or confirm the system decision, not just sit beside it.
- payload fields:
  - `break_even_rerun.rerun_artifact`
  - `break_even_rerun.uses_extracted_energy`
  - `break_even_rerun.uses_extracted_latency`
  - `break_even_rerun.uses_extracted_noise`
  - `break_even_rerun.uses_extracted_area`
  - `break_even_rerun.run_id`

## Next Payload Check

`python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not create the missing measurements, does not modify the canonical candidate payload, and does not write accepted post-layout evidence
