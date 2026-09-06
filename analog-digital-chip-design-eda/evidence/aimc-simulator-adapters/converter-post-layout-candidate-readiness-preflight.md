# Converter Post-Layout Payload Preflight

- status: `not_ready_for_strict_submission`
- source payload: `/home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- shape validation passed: `False`
- referenced file validation passed: `False`
- same-run validation passed: `False`
- issue count: `22`

Preflight is a review step. It reads the candidate package and explains whether the payload is ready for strict submission. It does not write accepted evidence.

## First Principle

A real converter package has to connect a number to the thing that made the number. Energy must come from the converter being claimed. Latency must come from the same conversion path. Noise must be below the same output boundary. Area must belong to the same ADC and DAC objects. The sharing rule must match the break-even calculation.

The preflight report separates three mistakes. A shape mistake means the payload is not saying enough. A file mistake means the payload says the right kind of thing, but the evidence cannot be inspected. A same-run mistake means the values are not tied to one experiment or one post-layout simulation.

## Issues

- `numeric_boundary`: simulation.voltage_v must be positive
- `numeric_boundary`: simulation.temperature_c must be numeric
- `numeric_boundary`: energy.adc_energy_per_conversion must be positive
- `numeric_boundary`: energy.dac_energy_per_row_drive must be positive
- `numeric_boundary`: latency.conversion_time_ns must be positive
- `numeric_boundary`: latency.settling_time_ns must be positive
- `noise_boundary`: noise.output_noise_rms must be numeric
- `noise_boundary`: noise.input_referred_noise must be numeric
- `numeric_boundary`: area.adc_area_um2 must be positive
- `numeric_boundary`: area.dac_area_um2 must be positive
- `claim_boundary`: template payloads cannot be submitted
- `missing_file`: extraction.extracted_netlist must point to an existing file
- `missing_file`: simulation.model_files[0] must point to an existing file
- `missing_file`: break_even_rerun.rerun_artifact must point to an existing file
- `claim_boundary`: provenance.run_id must not be a placeholder
- `claim_boundary`: simulation.run_id must not be a placeholder
- `claim_boundary`: energy.run_id must not be a placeholder
- `claim_boundary`: latency.run_id must not be a placeholder
- `noise_boundary`: noise.run_id must not be a placeholder
- `claim_boundary`: area.run_id must not be a placeholder
- `claim_boundary`: break_even_rerun.run_id must not be a placeholder
- `claim_boundary`: template payloads cannot pass same-run consistency

## Next Command If Ready

`python3 scripts/submit_converter_post_layout_payload.py /home/mehtama1/git-repo/ai-hardware-analysis/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not import the payload, does not write accepted evidence, and does not replace converter break-even assumptions
