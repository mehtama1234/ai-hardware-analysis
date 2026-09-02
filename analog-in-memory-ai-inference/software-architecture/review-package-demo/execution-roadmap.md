# Execution Roadmap

Start from the main workbench [Connected System Map](../connected-system-map.html). This roadmap uses the same object, constraint, design move, evidence, allowed claim, refused claim, and next-handoff contract.

This file turns the review package into a staged build plan.

The roadmap should not be read as a promise that the chip already works. It is a plan for moving from a readable demo package to measured evidence.

## Roadmap Rule

Each milestone must have:

- a clear owner
- a concrete output file or system behavior
- an exit test
- a claim that becomes safer
- a claim that still stays blocked

If a milestone has no output file and no exit test, it is not ready to be called done.

## Phase 1: Proof Workbench

Time range:

`0-3 months`

Purpose:

Build the product shell that keeps the company honest. The user should be able to open one page, follow one workload through the fourteen proof steps, see what evidence exists, and see what is still missing.

Primary owners:

- frontend owner
- backend owner
- product owner
- technical writing owner

Deliverables:

- interactive roadmap page
- readable package index
- fourteen step artifacts
- package manifest
- package schema
- final answer artifact
- source review register
- import templates
- archive builder
- smoke tests that block unsupported claims

Exit criteria:

- package smoke test passes
- readability contract passes
- archive includes all required package files
- a reviewer can open the static package without backend access
- each artifact says what it supports, what it does not prove, what is missing, and what comes next

Claim that becomes safer:

```text
The company has a clear proof workflow for reviewing one workload against one analog chip target.
```

Claim that stays blocked:

```text
Measured silicon performance.
```

## Phase 2: Model-Level Evidence

Time range:

`3-9 months`

Purpose:

Replace demo assumptions with evidence tied to the actual model and workload.

Primary owners:

- model tooling owner
- simulation owner
- compiler owner
- backend owner

Deliverables:

- model intake runner for ONNX first
- analog-fit classifier
- analog accuracy adapter
- crossbar layout adapter or local estimator
- hardware estimate adapter
- transformer and VLA checker
- normalized artifact validation for each adapter

Exit criteria:

- uploaded model produces `model_intake.json`
- analog candidate and blocked regions are listed with reasons
- analog accuracy result states assumptions and proof level
- crossbar layout result states tile, wire, bit-slicing, and converter assumptions
- transformer/VLA result separates analog candidates from digital-required regions
- missing evidence remains blocked in final answer

Claim that becomes safer:

```text
For this uploaded model, these regions may be analog candidates under stated assumptions.
```

Claim that stays blocked:

```text
The model runs on the real board.
```

## Phase 3: Chip-Specific Compiler And Runtime

Time range:

`6-15 months`

Purpose:

Move from generic analog mapping ideas to a chip-specific compiler and runtime package.

Primary owners:

- compiler owner
- runtime owner
- firmware owner
- backend owner

Deliverables:

- chip target description
- physical tile rules
- bit-slicing rules
- ADC and DAC scheduling rules
- memory placement rules
- analog/digital task graph
- runtime package format
- register and firmware interface
- failed-mapping reason model

Exit criteria:

- compiler mapping artifact includes tile placement, slice plan, analog/digital split, unsupported operators, runtime package status, calibration metadata, update metadata, and failure reasons
- runtime package can be created for a simulated or prototype target
- failed mapping gives a clear reason instead of silently dropping work
- final answer does not treat compiler success as board proof

Claim that becomes safer:

```text
The compiler can produce a target-specific execution package for the tested workload.
```

Claim that stays blocked:

```text
The package ran successfully on silicon.
```

## Phase 4: Board Bring-Up Evidence

Time range:

`9-18 months`

Purpose:

Prove that the package can be loaded, commanded, and observed on a prototype board or lab setup.

Primary owners:

- hardware owner
- firmware owner
- runtime owner
- lab owner
- backend owner

Deliverables:

- board interface summary
- board id and revision
- firmware version record
- power rail map
- runtime command log
- board runtime trace import
- debug trace import
- failure reason import

Exit criteria:

- board runtime artifact records package id, workload id, board id, firmware version, load status, start status, finish status, latency, jitter, failure reason, and debug trace
- failed board runs are stored as failed evidence, not missing data
- board result is tied to the exact package that produced it
- final answer does not treat board runtime as power, thermal, or task proof

Claim that becomes safer:

```text
This package ran or failed on this board setup, and the package records what happened.
```

Claim that stays blocked:

```text
The chip saves energy and preserves task accuracy.
```

## Phase 5: Calibration, Power, Thermal, And Task Proof

Time range:

`12-24 months`

Purpose:

Tie runtime, calibration, power, temperature, and task accuracy to the same package and setup.

Primary owners:

- lab owner
- calibration owner
- runtime owner
- task evaluation owner
- backend owner

Deliverables:

- calibration trace
- weak-tile list
- correction values
- failed-calibration handling
- power trace
- temperature trace
- task accuracy result
- synchronized run id across board, lab, calibration, and task artifacts

Exit criteria:

- calibration profile is tied to board id, chip id, timestamp, monitor readings, weak tiles, correction values, pass/fail status, and fallback behavior
- power and thermal artifacts include rail map, energy per run, peak power, temperature trace, sampling rate, equipment, board id, firmware id, package id, and measurement timing
- task artifact includes dataset or scenario id, metric, baseline result, candidate result, hardware result when available, tolerance, sample count, and failure slices
- final answer only allows claims supported by matching package id and setup id

Claim that becomes safer:

```text
Under this tested setup, the package has measured runtime, measured energy, measured temperature, calibration status, and task result.
```

Claim that stays blocked:

```text
The product is ready for all customers or all environments.
```

## Phase 6: Update, Drift, Reliability, And Pilot Readiness

Time range:

`18-36 months`

Purpose:

Decide whether the chip is fixed-weight only, periodic-update capable, adapter-update capable, or adaptive Physical AI capable.

Primary owners:

- device owner
- calibration owner
- runtime owner
- reliability owner
- customer pilot owner

Deliverables:

- write/update report
- write latency evidence
- write energy evidence
- endurance evidence
- retention evidence
- drift evidence
- rollback evidence
- recalibration-after-update evidence
- post-update task accuracy evidence
- customer pilot package

Exit criteria:

- update report states update scope, write latency, write energy, endurance, retention, rollback, recalibration, failed-update behavior, and post-update accuracy
- drift tests cover meaningful time, temperature, voltage, and workload conditions
- rollback is proven for failed update cases
- customer pilot package includes model, chip target, board setup, calibration, power, thermal, task result, failure trace, and final claim boundary

Claim that becomes safer:

```text
The product supports the tested update class under the measured conditions.
```

Claim that stays blocked:

```text
The chip supports unrestricted local adaptation for every Physical AI workload.
```

## Cross-Phase Owners

| Owner | Responsible For | Output |
| --- | --- | --- |
| Product | Keeps the central question clear and prevents scope drift. | package question, audience map, claim boundary |
| Frontend | Makes the workflow readable and usable. | roadmap page, package index, action views |
| Backend | Stores and validates evidence. | artifact schema, package endpoint, archive |
| Compiler | Turns model regions into chip-specific execution plans. | compiler mapping, runtime package |
| Runtime/Firmware | Loads packages, commands the board, records status and failures. | board runtime trace, debug trace |
| Silicon/Device | Defines tile, memory, monitor, converter, update, and health behavior. | chip profile, calibration profile, update evidence |
| Lab | Measures power, temperature, calibration, and board behavior. | power trace, thermal trace, calibration trace |
| Task Evaluation | Checks whether the mapped or hardware-run model solves the user task. | task accuracy artifact |

## Program Review Questions

Use these questions at the end of each milestone:

1. What artifact changed?
2. What proof level changed?
3. What claim became safer?
4. What claim is still blocked?
5. What owner has the next action?
6. What test prevents overclaiming?
7. Does the result use the same package, workload, chip target, board, firmware, calibration, and measurement setup?

## Product Meaning

This roadmap turns broad strategy into review gates.

The team should not ask, "Did we make progress?" in a vague way.

The team should ask:

```text
Which artifact did we produce, what proof level does it have, what claim can it support, and what must still stay blocked?
```
