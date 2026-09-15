# Converter Post-Layout Real Artifact Discovery

- status: `no_complete_real_artifact_package_found`
- accepted post-layout exists: `False`
- candidate non-scaffold file count: `13`
- current candidate submission status: `blocked_before_submission`
- current candidate would write accepted evidence: `False`
- current candidate strict issue count: `22`

## First Principle

A real post-layout claim needs a chain of named objects. The extracted circuit tells us what the layout became. The model file tells us which device and corner equations were used. The rerun artifact tells us whether those measured numbers changed the converter decision. If one part is missing, the claim stays blocked.

## Repo-Local Artifact Counts

- layout_or_extraction_files: `999` real-like `996`
- model_files: `11` real-like `9`
- rerun_artifacts: `12` real-like `11`

## Candidate Workspace

- workspace: `evidence/aimc-simulator-adapters/candidate-post-layout`
- exists: `True`
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-area.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-energy.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-latency.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/measurements/readout-noise.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/sky130-capacitive-isolation-ngspice.includes`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_converter_macro_extracted.sp`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_extracted.spice`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/aimc_readout_candidate_001_manifest.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/row_dac_extracted.sp`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/sar_readout_extracted.sp`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/shared_converter_mux_extracted.sp`
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/aimc_readout_candidate_001_break_even_rerun.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/sky130-capacitive-isolation-post-layout-both-polarity.json`

## Refused Claim

does not prove that no real artifacts exist outside the searched roots, does not verify the physics of any discovered file, and does not turn scaffold or generated proof fixtures into accepted post-layout evidence
