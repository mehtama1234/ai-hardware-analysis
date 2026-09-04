# AIHWKIT Residual Diagnostic

This page is the review page for AIHWKIT residual failures.

The generated source report is:

- `evidence/aimc-simulator-adapters/aihwkit-residual-diagnostic.json`
- `evidence/aimc-simulator-adapters/aihwkit-residual-diagnostic.md`

## Object

The object is the set of AIHWKIT simulator payloads that already run in the AIMC bridge.

The question is not whether AIHWKIT is installed. It is installed. The question is which model-shaped rows exceed the positive residual boundary and what mapping work should come next.

## Boundary

A threshold-fail payload is still useful evidence.

It tells us that the current analog mapping damages the output too much for a positive claim. That is different from a tool failure. The tool ran; the mapping did not yet preserve the digital result closely enough.

## Refused Claim

This page does not convert AIHWKIT threshold-fail payloads into positive analog evidence. It does not prove calibrated silicon, measured runtime, measured power, layout signoff, or production readiness.

## Next Handoff

Use the ranked worst rows to choose the next mapping experiment. Change scaling, conductance range, calibration, or output correction one step at a time, then rerun the same guarded payloads.
