# AIHWKIT And CrossSim Adapter Boundary

This page explains how AIHWKIT-style and CrossSim-style tools should connect to the combined AIMC workbench.

The current skipped-or-ran status page is `current-simulator-adapter-status.md`.

The normalized output contract for a real run is `analog-simulator-adapter-output-contract.md`.

The question is not "which simulator is best?"

The question is:

What evidence can each simulator produce, and which backend claim is allowed to change after that evidence is imported?

## Workflow Contract

Consumes: backend placement rows, analog candidate layers, weights, activation ranges, DAC/ADC settings, device-error assumptions, array-size assumptions, wire assumptions, and task outputs.

Produces: normalized analog-error evidence, layout-risk evidence, comparison tables against the local lab model, skipped-state records when tools are absent, and clear next-measurement gaps.

Supports: a stronger analog simulation discussion than the local hand-written model when assumptions, tool version, input layer, and output metrics are recorded.

Refuses: board latency, measured power, calibrated silicon, analog macro signoff, production yield, or tapeout readiness.

## Why These Tools Are Adapters, Not The Product

AIHWKIT and CrossSim answer different questions.

AIHWKIT-style simulation asks:

```text
If the neural-network layer runs with analog-like device behavior,
does the model output still look acceptable?
```

CrossSim-style simulation asks:

```text
If the mapped layer is implemented as a crossbar with array effects,
does the hardware-shaped error damage the algorithm result?
```

Both are useful. Neither is the whole system.

The workbench still needs model import, placement, compiler handoff, digital fallback, runtime scheduling, board traces, power measurement, package evidence, and claim readiness. That is why the tools should sit behind adapters. The frontend should not parse raw simulator output. The backend should receive normalized evidence records with provenance and claim boundaries.

## AIHWKIT Boundary

AIHWKIT is best treated as model-level analog behavior evidence.

It should consume:

- a layer or small model selected from the backend placement artifact
- weights and activation range
- device noise assumptions
- programming error assumptions
- drift assumptions
- ADC and DAC precision
- hardware-aware training setting, if used
- task metric or model-output comparison

It should produce:

- analog-error distribution
- model-output change
- task metric change, if a task dataset is attached
- layer-by-layer sensitivity
- simulator version and config
- skipped-state report if AIHWKIT is not installed

It can feed:

```text
analog_error_simulation
```

It can help `C4` only when paired with task accuracy evidence. By itself, it should not unlock accuracy support.

It must not feed:

```text
board_runtime
power_thermal
compiler_mapping
production_readiness
```

AIHWKIT can make analog behavior evidence stronger. It cannot prove the chip runs fast, uses less power, routes cleanly, or survives manufacturing.

## CrossSim-Style Boundary

CrossSim-style work is best treated as crossbar layout-risk evidence.

It should consume:

- backend placement rows
- tile shape
- array size
- row and column wire assumptions
- bit slicing
- read noise
- programming variation
- conductance range
- ADC range
- DAC range
- saturation policy

It should produce:

- expected residual from array effects
- saturation risk
- wire-drop risk
- bit-slicing risk
- ADC/DAC range risk
- layer-level pass/fail against residual budget
- tool version and config, if an external tool is used
- skipped-state report if the external tool is absent

It can feed:

```text
analog_error_simulation
```

It can also enrich the placement discussion when it explains why a tile shape or layer should stop being an analog candidate.

It must not be treated as:

```text
analog macro layout signoff
measured silicon behavior
board runtime
measured energy
production readiness
```

A crossbar simulator can say the selected array assumptions look risky or tolerable. It cannot say the final chip layout works unless extraction, DRC/LVS, timing, power, calibration, and silicon measurement are also present.

## The Normalized Adapter Record

The adapter output should not be a screenshot or a raw simulator log.

It should become a record shaped like this:

```text
source_id: analog_error_simulation
tool: aihwkit | crosssim | local-layout-risk
tool_version
input_artifact: backend-hardware-placement.json
layer_ids
analog_assumptions
converter_assumptions
array_assumptions
error_summary
model_or_task_effect
pass
provenance
claim_boundary
```

The record should say what changed in the number and what that means for the model. It should not only say the simulator ran.

## Comparison Against The Local Lab

The first useful adapter run should compare three things:

```text
local nonideality stack residual
AIHWKIT-style residual
CrossSim-style layout-risk residual
```

For each selected analog candidate, the table should show:

- layer id
- operator kind
- local residual
- AIHWKIT residual or skipped reason
- CrossSim-style residual or skipped reason
- model sensitivity class
- governor action
- claim effect

This comparison matters because disagreement is information. If the local model says a projection is safe but CrossSim-style risk says wire drop or ADC range is bad, the placement should move from analog candidate to needs review. If AIHWKIT shows the model is sensitive to drift, the governor should receive a larger residual or sensitivity field.

## Skipped Is A Valid State

If AIHWKIT or CrossSim is not installed, the adapter should not pretend success.

It should emit a skipped or blocked integration record:

```text
tool: aihwkit
status: skipped
reason: package not installed
next_action: install tool or provide container path
claim_effect: no claim upgraded
```

Skipped records are useful for project management. They are not evidence that analog behavior is safe.

## Claim Effect

The claim effect should be strict:

- AIHWKIT evidence can strengthen `analog_error_simulation`.
- CrossSim-style evidence can strengthen `analog_error_simulation` and explain placement risk.
- A task dataset is still needed for `task_accuracy`.
- A board or stronger runtime trace is still needed for `board_runtime`.
- A meter-backed trace is still needed for `power_thermal`.
- Production readiness remains blocked.

The backend should therefore keep these tools inside the evidence ledger, not let them bypass claim readiness.

## What To Build Next

First build a local adapter wrapper that can run even when the external tools are absent.

Done means:

- it reads `backend-hardware-placement.json`
- it selects the analog candidate rows
- it writes an AIHWKIT skipped-or-ran report
- it writes a CrossSim-style skipped-or-local-layout-risk report
- it emits a comparison Markdown file
- it exports a normalized `analog_error_simulation` candidate record only when the payload says what changed and why
- the bridge checker records pass or intentional skip

Only after that should we consider patching AIHWKIT, CrossSim, or any lower-level simulator.

## Where This Page Fits

Previous pages:

- `backend-hardware-placement-first-principles.md`
- `toolchain-map.md`

Next pages:

- `aimc-evidence-ledger.md`
- `evidence-import-and-claim-readiness-first-principles.md`
- `cross-repo-aimc-loop-proof.md`

Old source pages:

```text
ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/aihwkit-tool-stack-plan.html
ai-hardware-analysis/analog-in-memory-ai-inference/software-architecture/external-tool-integration-spec.md
```
