# AIHWKIT Physical Setting Review

This page is the review page for the AIHWKIT physical-setting review.

The generated source report is:

- `evidence/aimc-simulator-adapters/aihwkit-physical-setting-review.json`
- `evidence/aimc-simulator-adapters/aihwkit-physical-setting-review.md`

## Object

The object is the passing AIHWKIT setting as a possible analog tile boundary.

The question is not whether the setting reduces residual. The sweep already shows that it does. The question is whether the setting means something physically honest: input precision, output precision, output noise, converter energy, latency, area, and calibration.

## Boundary

The current local tile boundary is 4-bit DAC and 6-bit ADC. The passing AIHWKIT fine-resolution setting behaves more like a finer converter boundary with zero output noise.

That difference matters. A simulator setting can be useful as a target while still being too strong for the current circuit evidence.

## Refused Claim

This page does not claim that the current tile already has the passing AIHWKIT boundary. It does not prove measured silicon, measured runtime, measured power, macro layout, PCM device accuracy, or production readiness.

## Next Handoff

Choose one path: either design and cost the stronger converter/noise boundary implied by the passing setting, or rerun AIHWKIT with the existing tile boundary and accept the stricter residual result.
