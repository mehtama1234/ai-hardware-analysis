# End-To-End Meaty Goal

This document states what the finished roadmap experience should become.

The finished product should help a reader answer one question:

```text
Can this workload run well on this analog chip, what proof do we have, what breaks, and what must be built or measured next?
```

The answer must be useful to executives and developers at the same time. Executives need to understand the decision. Developers need to understand the build work. Both groups must see the same facts, the same proof level, and the same blocked claims.

## The Finished Experience

Build a readable evidence workbench for an analog AI inference chip company.

The workbench should start with the larger reason the company exists. More AI is moving into machines, sensors, vehicles, robots, industrial systems, and battery-powered devices. These systems often cannot wait for a cloud answer. They often have limited power. They often need to react close to the sensor or motor. This creates a real opening for local inference chips.

The workbench should then explain the company thesis in plain language. Analog in-memory compute may help when a workload spends a lot of time doing repeated matrix math. It does not automatically solve the full problem. A useful product needs a chip, compiler, runtime, board, calibration flow, lab measurement flow, and review package that all line up.

The experience should feel like a guided decision room, not a pile of notes. A reader should move through this order:

1. Why this matters now.
2. What the chip is trying to do.
3. Where analog compute may help.
4. Where digital compute is still required.
5. What proof exists today.
6. What proof is missing.
7. What must be modified or built.
8. What is safe to claim.
9. What must not be claimed yet.
10. What work should happen next.

## Executive Goal

An executive should be able to open the page for five minutes and explain the company story back in simple terms.

The executive view should answer:

- why local physical-edge inference matters now
- which first market is realistic
- why analog may help selected workloads
- why a hybrid analog and digital chip is safer than a purely analog chip
- what evidence exists today
- what evidence is missing
- which claims are safe
- which claims are blocked
- which proof milestone deserves funding next

The executive view should not require knowledge of chip terms. If the page uses a term such as `ADC`, `DAC`, `MLIR`, `VLA`, `calibration`, `bit-slicing`, `tile`, `drift`, `JTAG`, `PCIe`, or `runtime package`, it should explain the idea before it uses the term heavily.

## Developer Goal

A developer should be able to open the same page and identify the next build tasks without reading the source code first.

The developer view should answer:

- what the frontend must show
- what the backend must store
- what each JSON artifact means
- what each external toolkit can help with
- what must be custom-built for our chip
- what compiler passes must be modified or added
- what board and lab files must be imported
- what tests prevent unsupported claims
- what failure paths must be shown to the user

The developer view should be concrete. A phrase such as `add board integration` is not enough. The page should explain that board integration means loading a runtime package onto a board, running it, collecting status, collecting latency, collecting jitter, collecting power, collecting temperature, checking task accuracy, saving firmware details, and tying all of those records to the same setup.

## Concrete Product Scope

The finished workbench should cover the full company stack.

| Area | What Must Be Covered | What The Reader Should Understand |
|---|---|---|
| Silicon | calibration support, temperature monitors, voltage monitors, tile health checks, fallback behavior, power measurement points, board links, runtime status, debug traces | A chip feature is not a product claim until it can be reached, measured, and tied to task results. |
| Compiler and runtime | tiling, bit-slicing, transformer and VLA partitioning, ADC and DAC scheduling, calibration metadata, weight update metadata, runtime package generation, board command generation, failed-calibration handling, rollback handling | Normal model code needs a chip-specific path before it can run on the board. |
| Backend | package storage, model summary, simulator imports, compiler reports, board runtime logs, power traces, thermal traces, firmware metadata, task accuracy results, weak-tile lists, correction values, source notes, failed runs | The backend is the evidence engine. It must keep estimates, simulation, compiler output, board runs, lab measurements, and task results separate. |
| Frontend | plain-language primer, top blocker board, interactive journey, stack change map, evidence ladder, toolkit map, board proof view, calibration proof view, final verdict, export map, readiness audit | The page should let a reader understand the decision without needing a presenter. |
| Proof | source context, estimate, simulator result, compiler result, board runtime, lab measurement, task result, reliability result, missing proof | A claim can only be as strong as the evidence behind it. |

## Diagrams And Animations

The diagrams should reduce confusion. They should not be decoration.

The main diagram should show this path:

```text
User workload
  -> model intake
  -> analog and digital fit
  -> simulator or source-context evidence
  -> compiler mapping
  -> runtime package
  -> board run
  -> power and temperature measurement
  -> task accuracy result
  -> calibration and update checks
  -> final answer
```

The interaction should be simple:

- as the reader moves through steps, the current step is highlighted
- each step shows what evidence feeds it
- each step shows which later claims depend on it
- proof levels are visually separated
- missing proof is visible, not hidden

The evidence animation should teach one rule:

```text
Lower evidence cannot silently become stronger evidence.
```

For example, market context can explain why the company matters. It cannot prove chip performance. A simulator result can show likely analog risk. It cannot prove board energy. A board run can show that code executed. It cannot prove task quality unless a task result from the same setup is attached.

## Writing Rules

The writing should be plain, direct, and complete.

Every technical section should answer:

- what the thing means
- why it matters
- what can go wrong
- what proof is needed
- what the team should do next

Avoid vague claims. Do not use words such as `revolutionary`, `unbeatable`, `flawless`, `seamless`, `perfect`, or `production-ready` unless the sentence states the exact evidence that supports the word. Prefer wording such as `estimated only`, `simulated only`, `measured on this board`, `blocked until measured`, or `not proven yet`.

## Review Package Goal

The final export should stand on its own after a meeting.

It should include:

- workload summary
- chip target
- assumptions
- source notes
- model profile
- analog fit result
- analog accuracy risk
- crossbar layout risk
- hardware cost estimate
- compiler mapping
- transformer and VLA split
- runtime package status
- board runtime result
- power and temperature result
- task accuracy result
- calibration status
- weight update status
- sensor path status
- final answer
- safe claims
- blocked claims
- next engineering work
- archive validation result

The export should be readable as HTML and inspectable as files. Executives should be able to read the brief. Developers should be able to inspect schemas, artifacts, import templates, and tests.

## Acceptance Bar

The end state is acceptable when all of the following are true:

- an executive can identify the current decision, top blockers, safe claims, and next proof milestone
- a developer can identify the next frontend, backend, compiler, runtime, board, lab, and validation tasks
- every acronym is avoided, expanded, or explained near where it appears
- every important claim points to an artifact or source record
- every artifact says what it supports and what it does not prove
- the archive includes the readable docs, schema, manifest, journey data, import templates, and artifacts
- tests fail if the package claims measured power, board proof, calibration proof, update readiness, or full VLA readiness without the required evidence
- the final answer can say `yes`, `partial`, `no`, or `unknown` without hiding why

## Current Demo Boundary

The current package is a demo workbench. It can show the review shape, the evidence structure, the claim rules, and the next build work.

It does not prove measured chip performance. It does not prove board execution. It does not prove power savings. It does not prove calibration on silicon. It does not prove adaptive updates. It does not prove full VLA readiness.
