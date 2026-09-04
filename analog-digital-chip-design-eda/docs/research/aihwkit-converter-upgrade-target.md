# AIHWKIT Converter Upgrade Target

This page reviews the converter and noise target implied by the AIHWKIT setting that passes the held-out MatMul rows.

It is not a claim that the present tile is good enough. It is the opposite: it names the missing design work precisely.

## Object

The object is the same fixed-weight MatMul family used by the current AIHWKIT sweep and current-tile replay.

The current 4-bit DAC and 6-bit ADC tile replay fails every checked row. The fine-resolution AIHWKIT setting passes every checked row, but it uses a much finer input and output boundary.

## Reading Rule

A simulator setting becomes useful only when the hardware can pay for it.

That means the next proof must name the converter architecture, range, calibration method, energy, latency, area, and noise budget. Without those costs, the passing setting is only a target.

## Decision Boundary

If the stronger converter boundary is affordable and still passes held-out rows, those rows can move toward an analog-positive claim.

If the stronger converter boundary is too expensive, or if nonzero noise breaks the residual boundary again, those rows should remain digital fallback.

The generated evidence below gives the exact current boundary, target boundary, and precision gap.
