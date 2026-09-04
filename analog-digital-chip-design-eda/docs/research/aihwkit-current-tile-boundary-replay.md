# AIHWKIT Current Tile Boundary Replay

This page is the review page for the AIHWKIT current-tile replay.

The generated source report is:

- `evidence/aimc-simulator-adapters/aihwkit-current-tile-boundary-replay.json`
- `evidence/aimc-simulator-adapters/aihwkit-current-tile-boundary-replay.md`

## Object

The object is the same AIHWKIT MatMul row, but constrained to the current local tile converter boundary.

The tile boundary is 4-bit DAC and 6-bit ADC. That means the input and output cannot carry arbitrary real values. They must pass through finite bins.

## Boundary

This page is the countercheck to the stronger AIHWKIT forward-setting sweep.

The sweep tells us what settings can pass. This replay tells us what the current local tile boundary does. If the residual is too high here, the honest next step is either a stronger converter design or digital fallback for those rows.

## Refused Claim

This page does not prove measured silicon, measured runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not weaken the guarded residual threshold.

## Next Handoff

Use this replay to decide whether the current tile is enough for the tested MatMul rows. If not, design the stronger converter/noise boundary explicitly instead of hiding it inside a simulator setting.
