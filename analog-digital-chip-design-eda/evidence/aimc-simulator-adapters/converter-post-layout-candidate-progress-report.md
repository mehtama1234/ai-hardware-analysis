# Converter Post-Layout Candidate Progress Report

- status: `candidate_waiting_for_real_values`
- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- payload: `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- template only: `True`
- placeholder count: `29`
- missing or unresolved file count: `3`
- open checklist items: `32`
- ready for preflight: `False`

This report is the short answer for the candidate package. It reads the workspace audit and the fill checklist, then says whether the packet is still a scaffold or ready for preflight.

## First Principle

A post-layout converter claim needs two things at once: numbers and objects. The numbers are energy, latency, noise, area, voltage, temperature, and the replace-or-fallback decision. The objects are the netlist, model files, and rerun artifact that let someone inspect where those numbers came from.

If either side is missing, the packet is not almost evidence. It is still an editable packet. This report keeps that boundary visible.

## Open Groups

- `area`
- `break_even`
- `energy`
- `extraction`
- `files`
- `identity`
- `latency`
- `noise`
- `provenance`
- `simulation`

## Next Commands

- `python3 scripts/audit_converter_post_layout_candidate_workspace.py`
- `python3 scripts/generate_converter_post_layout_candidate_fill_checklist.py`
- `python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

## Refused Claim

does not supply real post-layout values, does not validate circuit physics, and does not submit accepted converter evidence
