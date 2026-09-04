# Sky130 Transistor DAC Calibration Analysis

- status: `monotonic_lut_candidate_not_calibration_proof`
- measured codes: `16` of `16`
- measured ordering monotonic: `True`
- ideal code step V: `1.125000000e-01`
- maximum absolute error LSB: `1.8388`

## First-Principles Reading

Calibration can remove a repeatable code-to-voltage error. It cannot repair a missing code, a non-monotonic transfer, or an error that changes with supply, temperature, mismatch, noise, or aging. The first question is therefore ordering; the second is repeatability; only then does a lookup table become meaningful.

The measured points are monotonic, so a deterministic lookup table is a possible future correction. The largest measured error is still several LSBs, and only 16 of 16 codes are present in the source run. No calibration claim is accepted yet.

## Refused Claim

does not prove calibration repeatability, missing-code behavior, PVT stability, mismatch/noise yield, SAR accuracy, or silicon
