# Audience Export Map

This file explains how the same review package should be read by different audiences.

The package should not change its facts for each audience. It should change the order and depth of the reading path. Every audience should see the same answer:

```text
The current demo package shows a partial fit and missing proof. It does not prove a finished chip.
```

## Executive

What this person needs:

- the current answer
- why the company is worth building now
- the first realistic market focus
- the top blockers
- what proof would unlock the next funding or partnership step

Start with:

1. `executive-brief.md`
2. `index.html`
3. `completion-audit.md`
4. `meeting-walkthrough.md`

Decision supported:

The executive can decide whether the roadmap is concrete enough to fund the next evidence milestone.

What the package must not hide:

- no measured silicon proof is present in this demo package
- no board run is present unless a board trace has been imported
- no measured power or temperature claim is present unless lab traces exist
- no full VLA claim is safe until compiler mapping, runtime, task, update, and fallback evidence exist

## Customer Technical Team

What this team needs:

- whether its workload is a fit, partial fit, not a fit, or unknown
- which model parts may fit analog compute
- which parts stay digital
- which measurements are missing
- what evidence would be needed before a pilot

Start with:

1. `index.html`
2. `artifacts/final_answer.json`
3. `artifacts/analog_fit.json`
4. `artifacts/compiler_mapping.json`
5. `artifacts/board_runtime.json`
6. `artifacts/task_accuracy.json`

Decision supported:

The customer can decide whether to share a model, dataset, board setup, or pilot requirements.

What the package must not hide:

- a compiler estimate is not a board run
- a board run is not task accuracy
- a task result is only valid for the dataset, workload, and setup that produced it
- calibration, power, thermal, and update gaps can change the final fit answer

## Investor

What this person needs:

- why this market is moving toward local physical-edge compute
- why analog may have a role
- what proof discipline the company has
- what claims are safe today
- what proof would reduce technical risk

Start with:

1. `executive-brief.md`
2. `source-review-register.md`
3. `completion-audit.md`
4. `meeting-walkthrough.md`

Decision supported:

The investor can decide whether the next financing should fund simulation, compiler work, board bring-up, lab measurement, customer pilots, or a narrower first product.

What the package must not hide:

- market trends explain timing, not chip proof
- another company's model, sensor, or board does not prove this chip works
- funding announcements do not prove product readiness
- production readiness requires repeated measured evidence, not a single demo

## Engineering Lead

What this person needs:

- the build queue
- schemas and import templates
- which adapters exist today
- which adapters are future work
- which tests prevent overclaiming
- what board and lab files must be collected

Start with:

1. `engineering-work-queue.md`
2. `schema.md`
3. `import-templates/README.md`
4. `completion-audit.md`
5. `roadmap-journey-demo.json`

Decision supported:

The engineering lead can assign concrete work across frontend, backend, compiler, runtime, board, lab, and validation.

What the package must not hide:

- demo JSON is not a live adapter result
- import templates are not proof until they are filled, validated, and linked to the same package
- the real chip target needs chip-specific compiler lowering and runtime command generation
- calibration, fallback, update, power, thermal, and task evidence need separate adapters and tests

## Product Or Program Manager

What this person needs:

- the end-to-end workflow
- the missing evidence list
- the dependency order
- what can be shown now
- what must wait

Start with:

1. `meeting-walkthrough.md`
2. `index.html`
3. `completion-audit.md`
4. `engineering-work-queue.md`

Decision supported:

The product or program manager can turn the roadmap into milestones, owners, dates, and review gates.

What the package must not hide:

- a blocked claim needs a named next action
- a next action needs an owner before it becomes a delivery plan
- a broad roadmap item is not complete until the evidence file exists and passes validation
- the first customer pilot should be narrower than the full company vision

## Shared Rule

Every audience gets the same claim boundary:

```text
Use the package to explain the path and current evidence. Do not use it to claim measured chip performance until measured artifacts exist.
```
