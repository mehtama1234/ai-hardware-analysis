# Converter Post-Layout Same-Run Gate

- status: `same_run_gate_passed`
- current scaffold rejected: `True`
- temporary same-run fixture accepted: `True`

This gate checks one simple rule: the converter values must come from one named run. Energy, latency, noise, area, simulation conditions, and the break-even rerun cannot be mixed from unrelated sources.

## First Principle

A converter payload is a claim about one physical path. If the energy is from one run, the noise is from another run, and the area is from a third source, the project cannot know what converter it is judging. The same-run id is the thread that ties those values back to one experiment or one post-layout simulation.

The current scaffold is rejected because it has no real run identity. A temporary complete fixture is accepted only after every value section carries the same run id as provenance.

## Required Run Id Fields

- `provenance.run_id`
- `simulation.run_id`
- `energy.run_id`
- `latency.run_id`
- `noise.run_id`
- `area.run_id`
- `break_even_rerun.run_id`

## Refused Claim

does not create real post-layout evidence, does not submit evidence, and does not prove analog replacement
