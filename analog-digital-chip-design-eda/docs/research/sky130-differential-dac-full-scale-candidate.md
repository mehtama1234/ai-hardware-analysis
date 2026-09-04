# Sky130 Differential DAC Full-Scale Candidate

This page records the current physical converter candidate that feeds the
mixed-memory transformer vertical slice.

## Requirement

The 4-bit DAC must measure all 16 thermometer codes, remain monotonic, provide
at least the `56.25 mV` half-LSB adjacent spacing, cover at least `1.6875 V`,
keep both plates within the `0..1.8 V` supply, and preserve comparator polarity
for every nonzero differential case.

## Measured Result

The complementary break-before-make cell uses sixteen positive and sixteen
negative 1 pF capacitors and `4x` top-plate dummy capacitance. At `0.9 V`
source common mode and `2.59 ns` source acquisition it measured `16/16` codes,
`83.5273 mV` minimum spacing, `1.7651 V` span, legal plate range, monotonic
transfer, and correct nonzero polarity.

## Remaining Gate

The physical calibrated SAR is not closed. The level-shifted follow-up measured
`16/16` calibration codes and `20/20` conversion comparisons, but only `2/5`
representative conversions were correct at the stable tested attenuation.
The source interface must preserve low-end convergence while covering the full
external input range. Until that is demonstrated, the compiler keeps analog
matrix operations behind a physical-converter gate and uses digital fallback.

## Evidence

See `evidence/aimc-simulator-adapters/sky130-differential-dac-full-scale-candidate.md`
and `evidence/aimc-simulator-adapters/sky130-thermometer-calibrated-physical-sar.md`.
