# Platform Roadmap Architecture

Related compiler target roadmap:

- [analog-mlir Chip Target Roadmap](analog-mlir-chip-target-roadmap.md)

## Purpose

This document describes what we need to build end to end.

The platform exists to answer one practical question:

```text
Can this workload run well on this analog chip, what proof do we have, what breaks, and what must be built or measured next?
```

The answer must come from the whole system, not from one simulator, one chart, or one chip claim.

The system must combine:

- the user's model
- the target analog chip profile
- simulator results
- compiler mapping
- board runtime
- power and thermal measurements
- task accuracy
- weight update evidence
- sensor path evidence
- safe claims
- blocked claims
- next engineering work

## Simple Product Architecture

```text
User
  |
  | uploads model, selects workload, selects target chip, sets success target
  v
Frontend Workbench
  |
  | shows 14-step journey, run buttons, results, proof, gaps, final answer
  v
Backend API
  |
  | creates package, runs checks, stores artifacts, normalizes evidence
  v
Evidence Engine
  |
  | combines model analysis, adapters, imports, claim rules, archive files
  v
External Tool Adapters
  |
  | AIHWKIT, CrossSim, analog-mlir, SST/Golem, ALPINE, NeuroSim, board, power, task
  v
Normalized Evidence
  |
  | every result is translated into the same product language
  v
Final Review Package
  |
  | fit, proof, breaks, safe claims, blocked claims, next work, export archive
  v
Engineer / Customer / Investor Review
```

## Why This Architecture

Analog chips are not judged by one number.

A workload may look good because the matrix math is efficient, but still fail because:

- the model has unsupported operators
- attention or Softmax stays digital
- sensor preprocessing was ignored
- board runtime is slower than expected
- power measurement counted only the core, not the full path
- analog drift hurts accuracy
- weights cannot be updated often enough
- the compiler cannot map the model automatically
- task accuracy drops after analog mapping

So the platform must work like a proof machine.

It must collect every important piece of evidence, show what each piece proves, and block claims that are not supported.

## The 14-Step Roadmap

```text
01 Model Intake
   |
02 Analog Fit
   |
03 Analog Accuracy Risk
   |
04 Crossbar Layout Risk
   |
05 Hardware Cost Estimate
   |
06 Compiler Mapping
   |
07 Transformer And VLA Check
   |
08 Full-System Runtime
   |
09 Board Runtime
   |
10 Power And Thermal
   |
11 Task Accuracy
   |
12 Weight Update Readiness
   |
13 Sensor To Model Path
   |
14 Final Answer
```

Each step must have:

- user benefit
- user question
- required input
- backend artifact
- supporting tools
- result
- proof level
- missing evidence
- next action

## Now, Next, Later

### Now: Build The Usable Demo

The near-term goal is to make the platform usable for review and demos.

We should build:

- a clear frontend journey
- package selection
- visual progress graph
- current evidence status
- toolkit support by step
- local evidence runs
- installed AIHWKIT and CrossSim smoke runs
- clear final answer preview
- exportable package

The current frontend should answer:

```text
Here is the model package.
Here are the 14 proof steps.
Here is what has a result.
Here is what is only checked.
Here is what still needs setup.
Here are the toolkits that support each step.
Here is what the user should do next.
```

This is not full production proof yet. It is the operating surface for the proof workflow.

### Next: Make The Frontend Operable

The next frontend build should add per-step actions.

Each journey card should become expandable.

Inside each step, the user should see:

- current result
- raw evidence summary
- proof level
- toolkits available
- toolkits missing
- input needed
- run button when runnable
- import button when external evidence is needed
- blocked reason
- next action

Example:

```text
Step 3: Analog Accuracy Risk

User benefit:
Know whether analog chip behavior may hurt model accuracy.

Current status:
Result available.

Run:
Run AIHWKIT
Run local analog estimate

Import:
Import external analog simulation report

Result:
Expected accuracy change: shown here.
Confidence: shown here.

Do not claim:
This does not prove board power or production silicon.
```

### Later: Replace Demo Evidence With Strong Evidence

Later work replaces smoke tests and estimates with stronger proof.

We should add:

- model-level AIHWKIT runs
- model-level CrossSim runs
- analog-mlir compiler bridge
- NeuroSim hardware cost adapter
- SST/Golem co-simulation adapter
- ALPINE/gem5-X full-system adapter
- dataset-backed task accuracy runner
- board trace import
- power and thermal trace import
- weight update measurement import
- sensor path import
- final claim engine

The later system should answer:

```text
This claim is supported by measured board data.
This claim is supported by simulator output only.
This claim is blocked.
This claim needs compiler proof.
This claim needs power measurement.
This claim needs task accuracy.
```

## Frontend Architecture

```text
Frontend Workbench
  |
  +-- Package Picker
  |
  +-- Central Question Panel
  |     "Can this workload run well on this analog chip?"
  |
  +-- 14-Step Visual Graph
  |     status for every step
  |
  +-- 14-Step Journey Cards
  |     user benefit
  |     user question
  |     supporting toolkits
  |     result
  |     proof level
  |     next action
  |
  +-- Step Detail Drawer
  |     current artifact
  |     adapter runs
  |     imported evidence
  |     missing evidence
  |     safe claim
  |     blocked claim
  |
  +-- Run And Import Controls
  |     run local adapter
  |     run installed toolkit
  |     import JSON evidence
  |     validate before saving
  |
  +-- Final Answer Panel
        fit
        proof
        breaks
        do-not-claim
        next work
        export
```

### Frontend Screens To Build

#### 1. Start Screen

Purpose:

```text
Let the user start from a model and a chip target.
```

Fields:

- model file
- workload type
- target chip profile
- modality
- runtime mode
- calibration profile
- success target
- optional dataset

#### 2. Journey Overview Screen

Purpose:

```text
Show the whole evaluation in one place.
```

Must show:

- visual graph
- step cards
- current status
- result count
- evidence count
- missing count
- next action count

#### 3. Step Detail Screen

Purpose:

```text
Let the user understand and operate one proof step.
```

Must show:

- user benefit
- what the step proves
- what it cannot prove
- supporting toolkits
- input needed
- current result
- raw artifact link
- run/import controls
- missing evidence
- next action

#### 4. Toolkit Results Screen

Purpose:

```text
Show what each toolkit contributed, but not make toolkit names the main journey.
```

Must show:

- toolkit name
- why it matters
- which journey step it supports
- whether installed
- whether configured
- last run result
- what it proves
- what it cannot prove

#### 5. Final Answer Screen

Purpose:

```text
Give the answer a founder, customer, investor, or engineer can use.
```

Must show:

- overall fit
- evidence summary
- broken areas
- missing evidence
- safe claims
- blocked claims
- next engineering work
- export button

## Backend Architecture

```text
Backend API
  |
  +-- Package Service
  |     create package
  |     select package
  |     archive package
  |
  +-- Journey Service
  |     produce 14-step roadmap state
  |     status per step
  |     next action per step
  |
  +-- Artifact Services
  |     model_intake.json
  |     analog_fit.json
  |     analog_accuracy_risk.json
  |     crossbar_layout_risk.json
  |     hardware_cost_estimate.json
  |     compiler_mapping.json
  |     transformer_vla_check.json
  |     full_system_runtime.json
  |     board_runtime.json
  |     power_thermal.json
  |     task_accuracy.json
  |     weight_update_readiness.json
  |     sensor_boundary_readiness.json
  |     final_answer.json
  |
  +-- Adapter Runner
  |     probe
  |     run
  |     normalize
  |     validate
  |     import
  |     save raw failure
  |
  +-- Evidence Store
  |     imported evidence
  |     generated evidence
  |     failed evidence
  |     source-checked context
  |
  +-- Claim Engine
        safe claims
        blocked claims
        do-not-claim list
        next work
```

## Backend APIs To Build

### Package APIs

```text
GET  /deployment-packages
GET  /deployment-packages/{package_id}
POST /deployment-packages
GET  /deployment-packages/{package_id}/archive
```

### Journey APIs

```text
GET  /deployment-packages/{package_id}/roadmap-journey
GET  /deployment-packages/{package_id}/roadmap-journey/{step_id}
POST /deployment-packages/{package_id}/roadmap-journey/{step_id}/run
```

### Evidence APIs

```text
GET  /deployment-packages/{package_id}/measurement-evidence
POST /deployment-packages/{package_id}/evidence/validate
POST /deployment-packages/{package_id}/evidence/import
GET  /deployment-packages/{package_id}/evidence-audit
```

### Adapter APIs

```text
GET  /adapters
GET  /adapters/{adapter_id}/probe
POST /adapters/{adapter_id}/run
```

### Claim APIs

```text
GET  /deployment-packages/{package_id}/claim-readiness
GET  /deployment-packages/{package_id}/final-answer
GET  /deployment-packages/{package_id}/review-report
```

## Artifact Architecture

Every step should produce one stable artifact.

```text
roadmap-journey.json
  |
  +-- step_id
  +-- step_name
  +-- user_benefit
  +-- user_question
  +-- status
  +-- tools
  +-- result_summary
  +-- proof_level
  +-- evidence_sources
  +-- missing_evidence
  +-- safe_claim
  +-- blocked_claim
  +-- next_action
  +-- artifact_refs
```

Each individual artifact should use the same base fields:

```text
artifact_name
package_id
step_id
provenance
confidence
created_at
source_type
is_measured
is_simulated
is_estimated
tool_name
tool_version
result_summary
limitations
next_action
raw_output_refs
```

## External Tool Adapter Architecture

External tools should plug in behind adapters.

The frontend should not parse raw AIHWKIT, CrossSim, analog-mlir, SST, ALPINE, or NeuroSim output.

```text
Raw Toolkit
  |
  | tool-specific logs, files, metrics, failures
  v
Adapter
  |
  | translate into product fields
  v
Normalized Artifact
  |
  | stable evidence contract
  v
Evidence Store
  |
  | validation and claim rules
  v
Frontend
  |
  | simple result and next action
```

### Adapter Pattern

Each adapter must support:

- probe
- run
- normalize
- validate
- save raw output
- save raw failure
- return product summary

### Adapter Families

```text
AIHWKIT
  -> analog accuracy risk
  -> drift/noise/converter simulation
  -> weight update simulation later

CrossSim
  -> crossbar layout risk
  -> wire resistance/read noise/programming error

analog-mlir
  -> compiler mapping
  -> static weight isolation
  -> analog/digital task graph

SST/Golem
  -> system timing
  -> CPU-to-accelerator dispatch
  -> memory and synchronization overhead

ALPINE/gem5-X
  -> full-system runtime
  -> CPU, memory, OS, analog accelerator behavior

NeuroSim
  -> area, energy, latency, memory estimate

TxSim / XBTorch / RxNN
  -> update risk, training risk, device behavior

Board Runtime
  -> measured latency and runtime trace

Power And Thermal
  -> measured energy, power, and heat

Task Accuracy
  -> whether the mapped model still solves the actual task
```

## Evidence Strength Ladder

The platform must show evidence strength clearly.

```text
Weakest
  |
  +-- source-checked context
  +-- local estimate
  +-- toolkit smoke result
  +-- simulator output
  +-- compiler mapping
  +-- system simulation
  +-- board runtime
  +-- power and thermal measurement
  +-- task accuracy result
  +-- repeated reliability and update evidence
  |
Strongest
```

The system must not let a weak proof support a strong claim.

Examples:

```text
AIHWKIT can support analog-risk discussion.
It cannot prove board power.

CrossSim can support crossbar-risk discussion.
It cannot prove final packaged silicon.

Board runtime can support latency.
It cannot prove task accuracy unless task accuracy was tested.

Power measurement can support energy.
It cannot prove compiler readiness.
```

## Roadmap Timeline

### Phase 0: What Exists Now

Already started:

- static frontend workbench
- backend package generation
- adapter registry
- local evidence adapters
- AIHWKIT installed and smoke runnable
- CrossSim installed and smoke runnable
- analog-mlir cloned but blocked by LLVM/MLIR setup
- SST cloned but blocked by missing system build dependency
- ALPINE cloned with partial checker path, full build blocked
- 14-step journey design
- toolkit result page
- platform completion goal

What this gives us:

```text
A demoable workflow that shows the proof journey and can run some local evidence paths.
```

What it does not give us yet:

```text
Full model-level analog simulation, real compiler mapping, real board proof, real power proof, or production claim support.
```

### Phase 1: Frontend Operating Surface

Build now:

- expandable 14-step cards
- per-step result drawer
- per-step run buttons
- per-step import buttons
- final answer preview
- visual gap ranking
- clearer safe-claim and blocked-claim panels

Done when:

```text
The user can operate the review from the frontend without reading backend files.
```

### Phase 2: Backend Journey Endpoint

Build next:

- `roadmap-journey.json`
- `/deployment-packages/{package_id}/roadmap-journey`
- one normalized status object per step
- artifact references per step
- evidence references per step
- missing evidence per step
- next action per step

Done when:

```text
The frontend renders the 14-step journey from backend data instead of hardcoded page data.
```

### Phase 3: Real Local Tool Runs

Build next:

- model-level AIHWKIT runner
- model-level CrossSim runner
- hardware cost estimator
- better compiler placement runner
- dataset-backed task runner
- evidence validators for each artifact

Done when:

```text
The platform can produce useful simulator and estimate evidence for a real uploaded model.
```

### Phase 4: External Compiler And System Simulation

Build later:

- analog-mlir setup path
- SST/Golem service adapter
- ALPINE/gem5-X service adapter
- attention partitioner
- transformer/VLA mapping report
- system-runtime normalized artifact

Done when:

```text
The platform can show whether the model can move from graph to analog/digital execution plan.
```

### Phase 5: Board And Lab Evidence

Build later:

- board runtime import
- board runtime service adapter
- power meter import
- thermal trace import
- firmware/run metadata
- synchronized board/power/task evidence

Done when:

```text
The platform can support measured lab claims for latency, energy, heat, and task behavior.
```

### Phase 6: Claim Engine And Investor Package

Build later:

- final answer endpoint
- safe claim generator
- blocked claim generator
- do-not-claim list
- next-work ranking
- investor view
- customer pilot view
- engineering work-order view
- package export

Done when:

```text
The platform can generate a review package that a technical customer, investor, or engineering lead can audit.
```

## What We Do Now

The immediate work should focus on the frontend and backend shape.

Build:

1. expandable frontend journey cards
2. final answer panel
3. backend roadmap journey artifact
4. API endpoint for 14-step state
5. frontend uses backend journey data
6. per-step run/import controls for existing adapters
7. archive includes roadmap journey
8. smoke test confirms missing evidence remains blocked

Why this first:

```text
This gives us the complete product shell and makes every future toolkit connection plug into a known place.
```

## What We Do Later

After the shell is working, add stronger proof sources.

Build:

1. model-level AIHWKIT
2. model-level CrossSim
3. NeuroSim adapter
4. analog-mlir environment and adapter
5. SST/Golem service adapter
6. ALPINE/gem5-X service adapter
7. real task accuracy runner
8. board runtime service
9. power and thermal measurement service
10. weight update measurement workflow
11. sensor path import workflow
12. final investor/customer review exports

Why later:

```text
These are deeper integrations. They are valuable only if the frontend and backend already know how to display, validate, store, and use their results.
```

## Final End State

The completed platform should behave like this:

```text
User uploads a model
  -> platform reads it
  -> platform maps analog and digital parts
  -> platform runs simulator/toolkit checks
  -> platform imports board and lab proof
  -> platform checks task accuracy
  -> platform checks weight updates and sensor path
  -> platform generates safe and blocked claims
  -> platform ranks next engineering work
  -> platform exports the review package
```

The final answer should be written plainly:

```text
This workload is a partial fit.

Proof we have:
- compiler estimate says these layers may map to analog
- AIHWKIT simulation says analog noise risk is low under these assumptions
- CrossSim smoke result is available
- local runtime estimate exists

What breaks:
- transformer attention still needs digital handling
- no real board runtime exists
- no measured power trace exists
- no real task accuracy result exists
- weight update evidence is missing

Safe claim:
This package supports early analog-fit discussion only.

Do not claim:
Do not claim measured power, production readiness, or adaptive Physical AI.

Next work:
Run real model-level simulation, add compiler mapping, import board runtime, import power trace, and run task accuracy.
```
