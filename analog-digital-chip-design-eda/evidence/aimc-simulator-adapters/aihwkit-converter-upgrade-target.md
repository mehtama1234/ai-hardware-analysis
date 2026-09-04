# AIHWKIT Converter Upgrade Target

This artifact turns the AIHWKIT sweep result into a concrete design target.

- status: `target_defined_not_justified`
- source physical review: `evidence/aimc-simulator-adapters/aihwkit-physical-setting-review.json`
- source current-tile replay: `evidence/aimc-simulator-adapters/aihwkit-current-tile-boundary-replay.json`

## Current Boundary

- DAC bits: `4`
- ADC bits: `6`
- input steps: `15`
- output steps: `63`
- current-tile passing rows: `0`
- current-tile failing rows: `16`
- current-tile max residual: `1.0`

## Minimum Passing Target

- AIHWKIT setting: `fine_resolution_no_output_noise`
- effective input bits: `10`
- effective output bits: `12`
- input steps: `1024`
- output steps: `4096`
- output noise: `0.0`
- passing rows: `16` of `16`
- max residual: `0.043357808474276574`

## Precision Gap

- input bit gap: `6`
- output bit gap: `6`
- input step ratio: `68.267`
- output step ratio: `65.016`

## First-Principles Reading

The current tile does not fail because the MatMul shape is wrong. The ideal-forward proof already showed that the row, column, sign, and weight orientation are correct. It fails when the signal has to pass through the coarse input and output bins of the current tile.

The passing setting gives a target, not a victory. It says the same rows pass when the input side is represented with about 10 effective bits, the output side with about 12 effective bits, and output noise is removed from this local test. Compared with the current tile, that is six more input bits and six more output bits. In step terms, the input must be about 68 times finer and the output about 65 times finer.

That extra precision is not free. The next design has to pay for it with converter architecture, range selection, calibration, energy, latency, area, and a noise budget. If that cost is too high, the correct architecture is not to force analog placement. The correct architecture is to keep those rows on the digital path.

## Required Next Evidence

- converter architecture for the target input and output precision
- noise budget showing why zero-output-noise simulation is a valid approximation or what nonzero noise remains
- energy per conversion or per MatMul row under the stronger converter boundary
- latency per conversion or per MatMul row under the stronger converter boundary
- area or macro-level placement cost for the stronger converter boundary
- calibration method that maps device conductance and converter range to the held-out MatMul rows
- AIHWKIT replay that passes held-out rows without weakening the guarded importer threshold

## Refused Claim

does not prove the current 4-bit DAC and 6-bit ADC tile has this target precision, noise, energy, latency, area, or calibration behavior
