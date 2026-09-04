# AIHWKIT Converter Cost Model

This page reviews the cost of the AIHWKIT converter target.

The target says what precision makes the local AIHWKIT rows pass. This page asks whether that precision still leaves a useful analog accelerator.

## Object

The object is the converter boundary around the same four-column MatMul read used by the local converter sweep.

The present tile uses a 4-bit DAC and 6-bit ADC. The AIHWKIT target asks for about a 10-bit input side and a 12-bit output side.

## Reading Rule

More converter bits reduce quantization error, but they also add circuit work.

The output side is especially important because a SAR ADC spends comparison steps to decide the output code. More output bits mean more decision time per column read unless the design pays for more parallelism.

## Decision Boundary

If the target precision has affordable energy, latency, area, calibration, and noise evidence, it can become a candidate analog boundary.

If the target precision costs more than the analog array saves, the correct system decision is digital fallback.

The generated evidence below gives the local relative cost estimate.
