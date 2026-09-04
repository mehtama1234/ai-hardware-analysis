# Converter Post-Layout Candidate Identity Initializer

This page describes the helper for the first safe edit to the candidate post-layout payload.

The helper fills identity and file-name fields with one shared run id. It does not fill energy, latency, noise, area, or other measured values.

## First Principle

Before a converter can be judged, the project has to know which converter is being judged.

That means the payload should name one converter, one run, one extracted netlist path, one model or setup file path, one source rerun path, and one provenance record. Those names do not prove the converter is good. They only prevent a worse mistake: mixing values from different runs and calling them one result.

## Safe Use

Run the self-test first:

`python3 scripts/initialize_converter_post_layout_candidate_identity.py --self-test`

When a real run exists, use the helper with real names and either write to a draft payload or apply it to the candidate payload.

The helper keeps `template_only` unchanged. The payload must stay blocked until all measured values and referenced files are real.

## Refused Claim

This helper does not create post-layout evidence, does not create netlist/model/rerun files, does not fill measured values, and does not write accepted evidence.
