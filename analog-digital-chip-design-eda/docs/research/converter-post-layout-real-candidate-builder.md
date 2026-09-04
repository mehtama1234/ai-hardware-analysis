# Converter Post-Layout Real Candidate Builder

This page explains the command that turns a real converter run into the candidate payload used by preflight, preview, and strict submission.

The builder is for the moment when real files already exist. It does not create physics. It copies the named files into the candidate workspace, writes one payload, and lets the existing validators decide whether the package is ready.

## First Principle

The hard part of a converter claim is not writing a number. The hard part is tying the number to the physical object that produced it.

For this workflow, that object has four pieces:

- the extracted netlist or measured setup
- the model or measurement condition file
- the numeric energy, latency, noise, and area terms
- the source rerun artifact that records the claimed replace-or-fallback decision

Those pieces must share one converter id and one run id. If they do not, the system cannot know whether energy came from one run, noise came from another run, and area came from a third object.

## Command Shape

`python3 scripts/build_converter_post_layout_candidate_from_real_run.py --netlist REAL.sp --model-file MODEL.sp --rerun-artifact RERUN.json --converter-id CONVERTER --run-id RUN --parasitic-format extracted-spice --simulator ngspice --command "..." --process-corner tt --voltage-v 0.8 --temperature-c 25 --adc-energy-per-conversion 1e-12 --dac-energy-per-row-drive 1e-13 --conversion-time-ns 5 --settling-time-ns 2 --output-noise-rms 0.001 --input-referred-noise 0.001 --adc-area-um2 1000 --dac-area-um2 500 --replacement-decision keep_digital_fallback --energy-method "..." --latency-method "..." --noise-method "..." --area-method "..." --operator PERSON_OR_CI --notebook SCRIPT_OR_NOTEBOOK`

## What It Writes

The builder writes the candidate package, not accepted evidence:

- `evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`
- `evidence/aimc-simulator-adapters/candidate-post-layout/netlist/...`
- `evidence/aimc-simulator-adapters/candidate-post-layout/models/...`
- `evidence/aimc-simulator-adapters/candidate-post-layout/rerun/...`

After that, the next command is the submission preview:

`python3 scripts/preview_converter_post_layout_submission.py --payload evidence/aimc-simulator-adapters/candidate-post-layout/payload.json`

Only if the preview says it would write accepted evidence should the strict submitter run.

## Refused Claim

This builder does not write accepted evidence, does not bypass strict submission, and does not prove that the input files came from silicon or extracted layout.
