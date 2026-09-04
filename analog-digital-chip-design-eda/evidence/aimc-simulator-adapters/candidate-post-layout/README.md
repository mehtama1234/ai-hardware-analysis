# Candidate Converter Post-Layout Workspace

This folder is a staging area for a real converter post-layout or measured-silicon package.

Replace `payload.json` placeholders with real values. Put the extracted netlist under `netlist/`, model or measurement setup files under `models/`, and the source break-even rerun artifact under `rerun/`. Use one shared `run_id` across provenance, simulation, energy, latency, noise, area, and break-even rerun fields.

Run preflight before submission:

```bash
python3 scripts/preflight_converter_post_layout_payload.py evidence/aimc-simulator-adapters/candidate-post-layout/payload.json
```

Only after preflight reports ready should the payload be submitted.

## Refused Claim

This workspace is not evidence. It is a staging folder and the default payload is intentionally rejected.
