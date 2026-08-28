# Demo Review Package Schema

This schema explains the demo review package in plain language.

The package is not measured chip proof. It is the file shape the platform should produce when it reviews one workload against one analog chip target.

## Manifest

The manifest file is `manifest.json`.

It tells the reader:

- which package they are looking at
- whether the package is demo evidence or measured proof
- how many artifacts should exist
- which artifact files belong to the package
- which audiences the package is meant to support
- what rule controls claims

Required manifest fields:

- `schema_version`: the manifest format version
- `package_id`: the package identifier
- `package_type`: the kind of package
- `main_question`: the question the whole review answers
- `warning`: the proof warning shown to the reader
- `artifact_count`: the number of step artifacts expected
- `artifacts`: the artifact file list, in journey order
- `audiences`: the intended reader groups
- `review_rule`: the rule that prevents unsupported claims

## Step Artifact

Each step artifact is one JSON file in `artifacts/`.

Each artifact must answer the same questions:

1. What step is this?
2. What proof level does it have?
3. What does the result mean in plain English?
4. What claim can it support?
5. What claim does it not prove?
6. What evidence is missing?
7. What should the team do next?

Required artifact fields:

- `schema_version`: the artifact format version
- `artifact_id`: a stable name for the artifact
- `step`: the step number from 1 to 14
- `title`: the step title shown in the page
- `proof_level`: the proof type, such as estimate, simulation, compiler mapping, board runtime, or task result
- `status`: the current state, such as demo context, estimate only, missing hardware, or blocked
- `plain_reading`: the short human explanation
- `what_this_supports`: claims this artifact can support
- `what_this_does_not_prove`: claims this artifact must not be used to support
- `missing_evidence`: evidence still needed before stronger claims are allowed
- `next_actions`: engineering or lab actions that should happen next

## Import Templates

The import templates live in `import-templates/`.

They show the normalized JSON shapes that future adapters and lab workflows should fill before the backend treats the result as evidence. They are examples, not proof.

Required import template fields:

- `schema_version`: the import template format version
- `source_id`: the evidence source, such as board runtime, power and thermal, calibration trace, or task accuracy
- `artifact_name`: the filename a filled import should use
- `plain_reading`: the human explanation of what this evidence captures
- `required_fields`: the fields a filled import must provide
- `template_payload`: an example payload with replaceable values
- `claim_rule`: the rule that says what claim this evidence can and cannot support

The demo package includes templates for compiler placement, analog error simulation, board runtime, power and thermal measurement, calibration, weight updates, sensor path, and task accuracy.

## Alignment Rule

The journey file is `../roadmap-journey-demo.json`.

The package is valid only if:

- the journey has 14 steps
- the manifest has 14 artifacts
- every journey step points to the matching artifact filename
- every journey step title matches the artifact title
- every journey proof level matches the artifact proof level
- every journey step lists `upstream_evidence`
- every journey step lists `downstream_claims`
- every journey step lists `depends_on_steps`
- every journey step lists `unlocks_steps`

This prevents the page from saying one thing while the package exports another.

## Journey Dependency Fields

The journey file explains the proof order.

Each step must include:

- `upstream_evidence`: the evidence, inputs, or assumptions that must exist before the step can support a useful result
- `downstream_claims`: the later claims, decisions, or product areas that depend on this step
- `depends_on_steps`: the journey step numbers that feed this step in the interactive diagram
- `unlocks_steps`: the journey step numbers that depend on this step in the interactive diagram

These fields keep the package readable after a meeting. A reader can see why a missing board trace blocks power claims, why missing calibration proof blocks trust claims, or why a partial transformer split does not prove full VLA readiness.

## Claim Rule

Every claim must point to an artifact and proof level.

Examples:

- A local estimate can support planning language.
- A simulator result can support risk language.
- A compiler report can support mapping language.
- A board trace can support a measured runtime claim for that exact setup.
- A power trace can support a measured energy claim only for the same package and setup.
- A task result can support an accuracy claim only for the tested workload.

If the artifact is missing, the claim stays blocked.
