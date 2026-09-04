# Converter Post-Layout Candidate Identity Initializer

- status: `identity_initializer_ready`
- source payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- applied to source payload: `False`
- same-run identity validation passed after identity fill: `True`
- strict same-run validation passed after identity fill: `False`

This helper exists to reduce one specific manual error: using different names for the same run in different payload sections.

## First Principle

The first safe edit to a candidate package is identity, not performance. Identity says which converter was run, which files belong to that run, who or what produced it, and what single run id ties the sections together.

This still does not make the payload evidence. Energy, latency, noise, area, extracted files, model files, and the source rerun artifact must still be real before strict submission can pass.

## Fields Initialized

- `converter_id`
- `extraction.extracted_netlist`
- `simulation.model_files[0]`
- `break_even_rerun.rerun_artifact`
- `provenance.created_at`
- `provenance.generator_or_lab_notebook`
- `provenance.operator`
- `provenance.run_id`
- `simulation.run_id`
- `energy.run_id`
- `latency.run_id`
- `noise.run_id`
- `area.run_id`
- `break_even_rerun.run_id`

## Remaining Boundary

numeric evidence values and referenced files still have to be real before strict submission can pass

## Refused Claim

does not invent numeric post-layout values, does not create referenced files, does not remove template_only, and does not write accepted evidence
