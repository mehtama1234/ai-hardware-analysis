# AIHWKIT Converter Break-Even Boundary

This file turns the converter target into a break-even question. The target can pass the replay only if the input and output codes are much finer. The hardware question is whether enough array work is being saved to pay for that finer conversion.

- target ADC bits: `12`
- target DAC bits: `10`
- target converter energy relative to 4x4 baseline: `206.222`
- highest all-pass output noise: `0.004`
- passing break-even scenarios: `2` of `4`
- default decision: `digital_fallback_until_real_converter_and_array_savings_are_measured`

## Scenario Table

| scenario | rows | sharing | target analog/output | digital/output | margin | beats digital | outputs needed to pay converter |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| four-row_fixture_no_sharing | 4 | 1 | 206.622 | 4.000 | -202.622 | False | 57.28 |
| sixty_four_row_tile_no_sharing | 64 | 1 | 212.622 | 64.000 | -148.622 | False | 3.58 |
| sixty_four_row_tile_shared_over_16_outputs | 64 | 16 | 19.289 | 64.000 | 44.711 | True | 3.58 |
| two_fifty_six_row_tile_shared_over_64_outputs | 256 | 64 | 28.822 | 256.000 | 227.178 | True | 0.90 |

## First-Principles Reading

An analog array saves work only on multiplication and accumulation. The converter sits at the edge of that array. If the converter spends more energy than the array saves, the analog result is not useful even when the numerical residual is small.

The break-even object is therefore not a single MatMul. It is a served volume: rows, columns, outputs, tokens, and how many outputs share one converter cost. A tiny four-row fixture cannot pay for a high-precision converter. A larger tile can begin to pay for it only if the converter is reused across enough useful outputs and if the analog MAC energy is truly lower than the digital fallback for the same rows.

The current local scenarios say the target is still a candidate, not permission. It can become interesting when the rows are larger and the converter cost is shared. It still needs real circuit energy, real timing, area, and a noise source that keeps the output disturbance inside the 0.004 budget.

## Required Next Evidence

- real ADC and DAC energy for the target precision
- number of rows and columns served per converter instance
- whether converters are per-column, shared, multiplexed, or reused across tokens
- analog array energy for the same matrix rows
- digital fallback energy and latency for the same rows
- noise source that explains why output noise stays at or below 0.004

## Refused Claim

not measured converter energy, measured latency, layout area, silicon noise, or board power
