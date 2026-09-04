# AIHWKIT Forward Setting Sweep

This page is the review page for the AIHWKIT forward-setting sweep.

The generated source report is:

- `evidence/aimc-simulator-adapters/aihwkit-forward-setting-sweep.json`
- `evidence/aimc-simulator-adapters/aihwkit-forward-setting-sweep.md`

## Object

The object is the same fixed-weight MatMul row used by the AIHWKIT residual diagnostic and ideal-forward mapping proof.

The sweep keeps the input, weight, output reference, layer size, and weight orientation fixed. It changes only the AIHWKIT forward-path assumptions.

## Boundary

This page answers a narrow question: which forward settings move the residual below the positive boundary?

It does not decide whether those settings are physically justified. A setting can be numerically helpful and still need a real device, converter, layout, and calibration argument before it can support a stronger hardware claim.

## Refused Claim

This page does not prove measured silicon, measured board runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not weaken the guarded importer threshold.

## Next Handoff

Use the best passing setting as a candidate mapping target. The next step is to decide whether that setting can be tied to a plausible analog tile: input range, ADC/DAC resolution, output noise, conductance mapping, and calibration.
