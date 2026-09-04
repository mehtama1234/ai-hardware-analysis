# Converter Post-Layout Payload Preflight

- status: `ready_for_strict_submission`
- source payload: `/home/mehtama1/git-repo/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/starter-post-layout-candidate/payload.json`
- shape validation passed: `True`
- referenced file validation passed: `True`
- same-run validation passed: `True`
- issue count: `0`

Preflight is a review step. It reads the candidate package and explains whether the payload is ready for strict submission. It does not write accepted evidence.

## First Principle

A real converter package has to connect a number to the thing that made the number. Energy must come from the converter being claimed. Latency must come from the same conversion path. Noise must be below the same output boundary. Area must belong to the same ADC and DAC objects. The sharing rule must match the break-even calculation.

The preflight report separates three mistakes. A shape mistake means the payload is not saying enough. A file mistake means the payload says the right kind of thing, but the evidence cannot be inspected. A same-run mistake means the values are not tied to one experiment or one post-layout simulation.

## Issues

- none

## Next Command If Ready

`python3 scripts/submit_converter_post_layout_payload.py /home/mehtama1/git-repo/analog-digital-chip-design-eda/evidence/aimc-simulator-adapters/starter-post-layout-candidate/payload.json`

## Refused Claim

does not import the payload, does not write accepted evidence, and does not replace converter break-even assumptions
