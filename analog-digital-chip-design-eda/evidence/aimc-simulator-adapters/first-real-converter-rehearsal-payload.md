# First Real Converter Rehearsal Payload

- status: `rehearsal_payload_written_still_rejected`
- source packet: `evidence/aimc-simulator-adapters/first-real-converter-candidate-packet.json`
- payload: `evidence/aimc-simulator-adapters/first-real-converter-rehearsal-payload/payload.json`
- canonical candidate payload touched: `False`
- ready for strict submission: `False`
- strict issue count: `15`
- preflight status: `not_ready_for_strict_submission`
- preview would write accepted evidence: `False`

## First Principle

A rehearsal payload is a controlled failure. It fills the identity fields, setup fields, and existing file references so we can see what remains when the easy wiring mistakes are gone.

The result should still fail. If it passed, the validator would be treating starter RC evidence as a complete converter. The useful result is a smaller and clearer failure list.

## Blockers Removed Compared With The Canonical Scaffold

- `identity_run_id_placeholders`: removed in rehearsal
- `simulation_voltage_temperature_placeholders`: removed in rehearsal
- `referenced_file_placeholders`: removed in rehearsal

## Remaining Real Blockers

- `converter_object`: the rehearsal netlist is an RC starter macro and does not include real row DAC, SAR readout, shared mux, or references
- `adc_energy`: ADC/readout supply energy is still not measured
- `conversion_latency`: full conversion decision latency is still not measured
- `noise`: output noise and input-referred noise are still not measured
- `area`: ADC and DAC physical area are still not measured
- `break_even`: rerun uses starter estimates, not accepted extracted energy, latency, noise, and area

## Strict Issues

- `incomplete_converter_object`: extraction.includes_row_dac must be true
- `incomplete_converter_object`: extraction.includes_sar_readout must be true
- `incomplete_converter_object`: extraction.includes_shared_mux must be true
- `incomplete_converter_object`: extraction.includes_references must be true
- `energy_missing`: energy.adc_energy_per_conversion must be positive
- `latency_missing`: latency.conversion_time_ns must be positive
- `noise_missing`: noise.output_noise_rms must be numeric
- `noise_missing`: noise.input_referred_noise must be numeric
- `noise_missing`: noise.meets_output_noise_budget must be true
- `area_missing`: area.adc_area_um2 must be positive
- `area_missing`: area.dac_area_um2 must be positive
- `not_same_evidence_level`: break_even_rerun.uses_extracted_energy must be true
- `not_same_evidence_level`: break_even_rerun.uses_extracted_latency must be true
- `not_same_evidence_level`: break_even_rerun.uses_extracted_noise must be true
- `not_same_evidence_level`: break_even_rerun.uses_extracted_area must be true

## Refused Claim

does not modify the canonical candidate payload, does not write accepted evidence, and does not make the starter RC macro a real converter
