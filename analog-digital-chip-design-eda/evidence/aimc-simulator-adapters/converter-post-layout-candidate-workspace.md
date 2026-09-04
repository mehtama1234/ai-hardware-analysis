# Converter Post-Layout Candidate Workspace

- status: `candidate_workspace_ready_not_evidence`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- preflight rejects default payload: `True`
- submission rejects default payload: `True`

This is the concrete staging folder for the first real converter package. It keeps the file layout simple: payload, extracted netlist, model files, break-even rerun artifact, and one shared run id across every value section.

## First Principle

A real evidence packet is a small filesystem, not just one number. The JSON says what is being claimed. The netlist or measurement files show the physical object. The model files define the electrical conditions. The rerun artifact shows the system-level decision that follows from those numbers.

The default workspace is intentionally rejected. That prevents an empty folder from looking like a completed post-layout run.

## Next Command

`python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not claim extracted post-layout evidence exists and does not write accepted evidence
