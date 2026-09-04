# Sky130 Differential DAC Full-Scale Candidate

- status: `nominal_dac_candidate_sar_pending`
- topology: `16 positive and 16 negative unit capacitors with break-before-make bottom switching`
- source common mode: `0.9 V`
- top-plate dummy capacitance: `4x` unit capacitance
- bottom switch scale: `1x`
- source acquisition: `2.59 ns`
- codes measured: `16/16`
- minimum spacing: `83.5273 mV`
- total span: `1.76513629 V`
- required 4-bit span: `1.6875 V`
- legal plate range: `True`
- monotonic: `True`
- correct nonzero polarities: `True`

## Interpretation

This is the first nominal differential DAC candidate in the topology sweep to
pass complete-code convergence, spacing, full-scale, legal-range, and
nonzero-polarity checks. It is not a SAR or system acceptance result. The
level-shifted physical SAR follow-up measured `16/16` calibration codes and
`20/20` conversion comparisons at the stable `0.8x` attenuation setting, but
only `2/5` representative conversions were correct. A `0.9x` setting reduced
low-end convergence to `12/14` comparisons and achieved `1/5`. The source common-mode and
input-range interface therefore remains the next physical design gate. The
complete source-interface sweep is recorded in
`evidence/aimc-simulator-adapters/sky130-differential-source-interface-sweep.md`.
