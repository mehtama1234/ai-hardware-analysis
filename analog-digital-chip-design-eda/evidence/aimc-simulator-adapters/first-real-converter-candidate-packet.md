# First Real Converter Candidate Packet

- status: `partial_measurement_packet_ready_not_strict_submission_ready`
- candidate id: `aimc_readout_candidate_001`
- proposed run id: `aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001`
- ready for strict submission: `False`
- accepted post-layout written: `False`
- current candidate non-scaffold files: `2`
- current preflight status: `not_ready_for_strict_submission`
- current preflight issue count: `22`
- missing packet files: `0`

## First Principle

A candidate packet is not a claim that the converter works. It is the smallest honest bundle of things we know about one candidate. It separates measured terms from missing terms so the payload cannot quietly turn estimates into accepted evidence.

The present packet says the extracted-RC path runs, the starter capacitance has a first-order energy and settling estimate, and the ultra frontend preserves signal sign but still loses too much voltage before the latch target.

## Measured Terms Available Now

- supply voltage V: `1.8`
- assumed temperature C for this packet: `27.0`
- starter row final V: `1.800000000`
- starter row 90 when s: `1.199360e-10`
- starter row 99 when s: `1.243690e-10`
- starter total pin charge energy J: `3.225791e-14`
- starter max settle 0.1 percent s: `9.559010e-11`
- ultra frontend transfer ratio: `0.437908`
- ultra frontend remaining transfer improvement: `2.28x`
- ultra frontend direct sample-to-sense capacitance fF: `0.8`
- ultra frontend passing sign cases: `4`

## Payload Terms We Can Fill Now

- `converter_id`: `aimc_readout_candidate_001`
- `run_id`: `aimc_readout_candidate_001_sky130_tt_1p8v_27c_run001`
- `measurement_level`: `post_layout_simulation`
- `simulation.simulator`: `ngspice`
- `simulation.voltage_v`: `1.8`
- `simulation.temperature_c`: `27.0`
- `extraction.parasitic_format`: `extracted-spice`

These fields are identity and setup fields. They do not make the candidate accepted.

## Payload Terms Still Missing

- `extraction.extracted_netlist`: one complete extracted netlist for the claimed converter/readout object
- `simulation.model_files`: same-run model/setup file for the claimed converter/readout object
- `energy.adc_energy_per_conversion`: supply-current integration for the readout decision, not only pin capacitance
- `energy.dac_energy_per_row_drive`: supply-current integration for the row-drive event, not only pin capacitance
- `latency.conversion_time_ns`: full readout decision time, not only row RC settling
- `noise.output_noise_rms`: measured or simulated output noise at the digital code boundary
- `noise.input_referred_noise`: input-referred readout noise for the same run
- `area.adc_area_um2`: physical ADC/readout area for the claimed object
- `area.dac_area_um2`: physical DAC/row-drive area for the claimed object
- `break_even_rerun.rerun_artifact`: break-even rerun produced from the same measured values

## File Packet

- `starter macro extracted RC netlist`: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_layout_smoke.spice` exists `True` bytes `799`
- `starter macro transient deck`: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/aimc_converter_macro_extracted_rc_step.sp` exists `True` bytes `996`
- `starter macro transient measurements`: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/converter-starter-extracted-rc-ngspice.csv` exists `True` bytes `182`
- `ultra sense extracted frontend netlist`: `labs/analog/analog-in-memory-foundation-model-hardware/layout-workbench/extracted/sky130_ultra_sense_capacitive_frontend_extracted.spice` exists `True` bytes `2402`
- `ultra sense frontend ngspice deck`: `labs/analog/analog-in-memory-foundation-model-hardware/spice/sky130_ultra_sense_frontend_candidate.sp` exists `True` bytes `1023`
- `ultra sense frontend measurements`: `labs/analog/analog-in-memory-foundation-model-hardware/measurements/sky130-ultra-sense-frontend-candidate.csv` exists `True` bytes `646`

## Next Commands

- `python3 scripts/run_converter_starter_extracted_rc_ngspice.py`
- `python3 scripts/generate_first_real_converter_candidate_packet.py`
- `python3 scripts/run_converter_post_layout_candidate_readiness.py`
- `python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not fill the canonical candidate payload, does not write accepted post-layout evidence, and does not prove a 10-bit DAC, 12-bit ADC, comparator noise, DRC/LVS, or replacement economics
