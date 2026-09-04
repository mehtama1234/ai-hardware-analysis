# AIHWKIT Physical Setting Review

This review connects the passing AIHWKIT forward setting to the physical tile boundary.

- review status: `needs_physical_justification`
- candidate setting: `fine_resolution_no_output_noise`
- candidate residual: `0.043358`
- candidate effective input bits: `10`
- candidate effective output bits: `12`
- current tile DAC bits: `4`
- current tile ADC bits: `6`
- current tile converter error: `0.090004`

## First-Principles Reading

A passing simulator setting is not automatically a hardware setting. The simulator setting says how finely the input and output are represented and how much output noise is allowed. The tile operating point says what the local circuit evidence currently pays for.

The passing AIHWKIT setting uses about 10 effective input bits and 12 effective output bits with zero output noise. The current tile boundary is 4-bit DAC and 6-bit ADC with a measured converter-error budget. Those are not the same claim.

So the setting is useful, but only as a target. It tells us what kind of converter and noise boundary would make AIHWKIT pass on these rows. It does not prove that the current tile already has that boundary.

## Concrete Next Proof

Either derive a 10-bit input and 12-bit output converter boundary with its energy, latency, area, and calibration cost, or rerun AIHWKIT using the existing 4-bit DAC and 6-bit ADC boundary and accept the residual result.

## Refused Claim

This review does not prove measured silicon, measured board runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not weaken the guarded importer threshold.
