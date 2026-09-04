# Converter Post-Layout Break-Even Rerun Path

This report adds the executable step after post-layout payload validation.

- status: `rerun_path_ready_waiting_for_validator_passing_payload`
- rerun script: `scripts/rerun_converter_break_even_from_post_layout_payload.py`
- base break-even: `evidence/aimc-simulator-adapters/aihwkit-converter-break-even.json`
- rejected placeholder/template: `True`

## First-Principles Reading

Validation answers whether the payload is real enough to use. Break-even answers whether the real converter is worth using. These are different questions. A validated payload can still tell the system to keep the digital fallback if the converter energy, latency, area, noise, or sharing rule makes the analog path too expensive.

The rerun script takes the extracted ADC energy, DAC energy, conversion time, settling time, noise, area, and sharing rule from the payload. It then recomputes the analog-output cost against a digital MAC baseline for the same served rows. The default decision comes from the payload sharing rule, not from the earlier local estimate.

## Guarded Dry Run

- `evidence/aimc-simulator-adapters/dry-run/converter-post-layout-evidence.placeholder.json` rejected: `True`
- `sources/evidence/converter-post-layout-payload.template.json` rejected: `True`

## How To Use With A Real Payload

1. Fill `sources/evidence/converter-post-layout-payload.template.json` with extracted or measured values.
2. Run `python3 scripts/validate_converter_post_layout_payload.py FILLED_PAYLOAD.json`.
3. Run `python3 scripts/rerun_converter_break_even_from_post_layout_payload.py FILLED_PAYLOAD.json --output evidence/aimc-simulator-adapters/FILLED_BREAK_EVEN_RERUN.json`.
4. Use the rerun decision, not the local planning estimate, as the converter replacement boundary.

## Refused Claim

does not supply a real post-layout payload and does not replace the current digital fallback decision
