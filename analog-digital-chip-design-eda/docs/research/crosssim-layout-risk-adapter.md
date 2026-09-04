# CrossSim Layout-Risk Adapter

This page is the review page for the physical-risk record behind the current CrossSim-backed placement decision.

The generated source report is:

- `evidence/aimc-simulator-adapters/crosssim-layout-risk-adapter.json`
- `evidence/aimc-simulator-adapters/crosssim-layout-risk-adapter.md`
- `labs/analog/analog-in-memory-foundation-model-hardware/measurements/crosssim-layout-risk-adapter.csv`

## Object

The object is each MatMul row that survived residual-aware placement.

The row already has model-level evidence: CrossSim kept the calibrated fixed-weight MatMul output inside the residual boundary. This page asks a different question: what physical assumptions did that row depend on?

## Boundary

Model residual and layout risk are different evidence types.

Model residual asks whether the output number stayed close enough.

Layout risk asks whether the array size, row wire, converter precision, bit slicing, and column current assumptions are still believable before physical design.

## Refused Claim

This page does not prove macro layout, extraction, DRC, LVS, calibrated silicon, measured latency, measured energy, production readiness, or tapeout readiness.

## Next Handoff

The next step is to replace this local layout-risk estimate with extracted macro parasitics or a stronger crossbar simulation flow. Until then, it is a review record, not a signoff record.
