# AIHWKIT Converter Cost Model

This file prices the AIHWKIT converter target with the same relative cost formula used by the local converter sweep.

- status: `fallback_preferred_until_cost_is_justified`
- source target: `evidence/aimc-simulator-adapters/aihwkit-converter-upgrade-target.json`
- formula source: `labs/analog/analog-in-memory-foundation-model-hardware/python/converter_boundary_sweep.py`

## Current Tile Cost

- ADC bits: `6`
- DAC bits: `4`
- energy relative to 4x4 baseline: `3.222`
- SAR comparisons per four-column read: `24`

## Target Cost

- ADC bits: `12`
- DAC bits: `10`
- energy relative to 4x4 baseline: `206.222`
- SAR comparisons per four-column read: `48`

## Delta

- energy multiplier versus current tile: `64.000`
- latency comparison multiplier versus current tile: `2.000`
- extra ADC comparisons per four-column read: `24`

## First-Principles Reading

The target fixes the numerical problem by asking the converters to make much finer decisions. That changes the hardware problem. A converter is not a label on a diagram; it is a timed circuit that spends switching, comparison, reference, routing, and calibration cost to turn an analog value into a code.

The current tile uses a small converter boundary because analog compute only helps when the array work saved is larger than the converter work added. The 10-bit input and 12-bit output target may make AIHWKIT residuals pass, but under this local formula it makes converter energy far larger than the current operating point and adds more output comparison work.

So the honest architecture rule is simple: until that cost is justified by measured or circuit-level evidence, the high-precision target is a design candidate, not an analog placement permission. Rows that need this much precision should stay on the digital path unless a later proof shows the higher-precision analog path wins for the same workload.

## Required Next Evidence

- measured or circuit-level energy for the stronger ADC and DAC choice
- timing model showing whether the extra SAR comparisons fit prefill or decode latency
- macro area estimate for converter replication, sharing, or multiplexing
- AIHWKIT replay with a nonzero noise model that matches the proposed converter design
- scheduler policy showing when the high-precision analog path beats digital fallback

## Refused Claim

not measured silicon energy, board energy, layout area, or production power
