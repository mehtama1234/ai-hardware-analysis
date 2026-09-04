# Converter SPICE Handoff Spec

This file says what the next converter proof must simulate. The current behavioral estimate is useful because it makes the math visible. It is still too clean. A SPICE handoff must turn each clean term into a circuit measurement.

- ADC target: `12` bits
- DAC target: `10` bits
- output noise budget: `0.004`
- behavioral output noise RMS to beat or explain: `0.000851121`
- settling window: `4.0` ns
- conversion window: `12.0` ns
- sharing point: `64` rows, `4` columns, `16` outputs per conversion cost

## First-Principles Handoff

The behavioral model says the converter target can fit under the noise budget if the row voltage settles, the quantization steps are fine enough, and comparator and driver noise stay small. SPICE must test those same nouns as circuit nodes and currents. A row DAC is no longer just `10 bits`; it is a reference ladder, switches, output resistance, capacitance, load, and settling time. A SAR ADC is no longer just `12 bits`; it is a sample node, comparator, reference movement, switching sequence, and timed decision chain.

The important question is not whether the SPICE run produces a pretty waveform. The question is whether each waveform can replace one field in the converter evidence contract: energy, latency, output noise, input-referred noise, area or area proxy, and sharing rule.

## Required Testbenches

### S1. 10-bit row DAC settling

- object: row-driver DAC output node before the crossbar row input
- stimulus: step through low, midscale, and near-full-scale codes with the selected row load attached
- measurement: settled voltage error after the allowed settling window
- acceptance: absolute settled error stays below half of one 10-bit DAC step and the row-driver noise term stays within the evidence budget

### S2. 12-bit SAR readout decision

- object: ADC comparator, capacitor ladder or equivalent DAC, reference path, and sample node
- stimulus: sweep input around every critical transition used by the selected output range
- measurement: code transition error, comparator decision noise, conversion time, and failed-decision cases
- acceptance: RMS readout error plus comparator noise stays below the budget carried by the behavioral estimate

### S3. shared converter loading

- object: four shared converter instances serving the 64-row, 4-column, 16-output sharing point
- stimulus: toggle the muxed source, output load, and sample timing across the sharing schedule
- measurement: extra settling error, added conversion latency, and loading-dependent noise
- acceptance: sharing does not push total output noise above 0.004 and does not remove the break-even margin in the passing 64-row shared scenario

### S4. energy accounting

- object: row DAC references, ADC references, comparator, switch ladder, sampling capacitors, and mux control
- stimulus: same conversion sequence used in the accuracy replay
- measurement: integrated supply energy per row drive and per output conversion
- acceptance: energy fields can replace the relative behavioral units with SPICE-derived numbers and a named voltage rail

## Required Output Fields

- measurement_level=circuit_simulation or post_layout_simulation
- adc_energy_per_conversion with units and rail voltage
- dac_energy_per_row_drive with units and row load
- conversion_time_ns from the timed decision path
- settling_time_ns from the row-drive and sample path
- output_noise_rms from transition, comparator, settling, and driver terms
- input_referred_noise for the row-drive boundary
- adc_area_um2 and dac_area_um2 if layout exists, otherwise explicit area proxy
- sharing rule that names rows, columns, instances, and outputs per conversion cost
- netlist path, model corner, simulator command, seed if noise is randomized, and date

## Claim Boundary

Transistor-level SPICE can improve the behavioral converter model. It still cannot replace the break-even assumptions unless the evidence level becomes `post_layout_simulation` or `measured_silicon`.

Refused claim: does not claim a designed converter exists, does not claim extracted parasitics, does not claim measured silicon, and does not upgrade board energy
