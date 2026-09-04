# AIHWKIT Ideal Forward Mapping Proof

This page is the review page for the AIHWKIT ideal-forward mapping proof.

The generated source report is:

- `evidence/aimc-simulator-adapters/aihwkit-ideal-forward-mapping-proof.json`
- `evidence/aimc-simulator-adapters/aihwkit-ideal-forward-mapping-proof.md`

## Object

The object is the fixed-weight MatMul row as AIHWKIT receives it: input values, weight matrix, output values, layer dimensions, and weight orientation.

This is narrower than the full analog claim. It asks whether the mathematical matrix multiply is being handed to AIHWKIT correctly before analog noise, converter limits, drift, or PCM-like assumptions are applied.

## Boundary

If this proof passes, it means the shape and transpose path are not the reason the larger AIHWKIT payloads fail.

That matters because the repair target becomes sharper. The next experiment should tune the non-perfect forward path: input range, converter resolution, output noise, conductance mapping, and calibration. It should not change the guarded residual threshold just to make a failing payload look acceptable.

## Refused Claim

This page does not prove that AIHWKIT's default inference path is accurate enough for positive analog placement. It does not prove PCM behavior, measured silicon, measured runtime, measured power, macro layout, or production readiness.

## Next Handoff

Use this proof as the baseline for the next AIHWKIT experiment. Keep the same rows and the same digital references, then change one non-perfect forward assumption at a time and rerun the residual diagnostic.
