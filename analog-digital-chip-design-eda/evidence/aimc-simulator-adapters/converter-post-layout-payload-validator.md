# Converter Post-Layout Payload Validator

This report turns the post-layout converter contract into an executable gate.

- status: `post_layout_payload_validator_ready_waiting_for_extracted_payload`
- rejected placeholder: `True`
- validator: `scripts/validate_converter_post_layout_payload.py`
- placeholder payload: `evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.placeholder.json`

## First-Principles Reading

The hard question is not whether a converter number exists. The question is whether the number came from the same physical object that the system wants to use. A post-layout payload must therefore name the extracted circuit, the simulation conditions, the measured energy, the measured time, the measured noise, the measured area, and the break-even rerun that consumed those values.

The placeholder intentionally has the right shape and the wrong evidence. The validator rejects it because it has no extracted netlist, no model files, no positive energy, no positive timing, no area, no passing noise result, and no break-even rerun using extracted values.

## Accepted Payload Boundary

- measurement level must be `post_layout_simulation` or `measured_silicon`
- target must remain 10-bit input and 12-bit output
- output noise RMS must be at or below `0.004`
- sharing must remain 64 rows, 4 columns, 4 converters, and 16 outputs per conversion cost
- break-even must be rerun with extracted energy, latency, noise, area, and the same sharing rule

## Refused Claim

does not provide an extracted netlist, post-layout simulation, measured silicon, or a replacement break-even result
