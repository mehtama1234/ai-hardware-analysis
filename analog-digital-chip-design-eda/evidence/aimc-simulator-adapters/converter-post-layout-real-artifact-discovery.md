# Converter Post-Layout Real Artifact Discovery

- status: `no_complete_real_artifact_package_found`
- accepted post-layout exists: `False`
- candidate non-scaffold file count: `2`
- current candidate submission status: `blocked_before_submission`
- current candidate would write accepted evidence: `False`
- current candidate strict issue count: `22`

## First Principle

A real post-layout claim needs a chain of named objects. The extracted circuit tells us what the layout became. The model file tells us which device and corner equations were used. The rerun artifact tells us whether those measured numbers changed the converter decision. If one part is missing, the claim stays blocked.

## Repo-Local Artifact Counts

- layout_or_extraction_files: `13` real-like `13`
- model_files: `1` real-like `1`
- rerun_artifacts: `5` real-like `4`

## Candidate Workspace

- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- exists: `True`
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes`
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json`

## Refused Claim

does not prove that no real artifacts exist outside the searched roots, does not verify the physics of any discovered file, and does not turn scaffold or generated proof fixtures into accepted post-layout evidence
