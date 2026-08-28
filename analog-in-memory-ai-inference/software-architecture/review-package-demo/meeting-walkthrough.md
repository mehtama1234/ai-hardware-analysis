# Meeting Walkthrough

This guide explains how to walk through the review package in a meeting.

Use it for an executive review, investor review, customer technical review, or internal engineering review. It keeps the discussion tied to one question:

```text
Can this workload run well on this analog chip, what proof do we have, what breaks, and what must be built or measured next?
```

## Before The Meeting

Open these files:

1. `index.html`
2. `executive-brief.md`
3. `completion-audit.md`
4. `engineering-work-queue.md`
5. `source-review-register.md`

Keep this rule visible:

```text
Outside sources explain context. Demo artifacts explain the review shape. Only measured or validated artifacts prove product claims.
```

## 20-Minute Walkthrough

### Minute 0-2: Start With The Decision

Say:

The current answer is partial fit with missing proof. Analog compute may help selected matrix-heavy parts of the workload, but the package does not prove a full chip, full VLA model, measured power, calibration, updates, or production readiness.

Open:

- `executive-brief.md`
- the Executive Answer section in `index.html`

Decision supported:

- whether the audience understands the current safe claim before seeing any detail

Do not say:

- the chip is proven
- the board ran
- power savings are measured
- full VLA execution is ready

### Minute 2-5: Explain The Evidence Levels

Say:

This package separates source context, demo evidence, estimates, simulation, compiler mapping, board runtime, lab measurement, task accuracy, and reliability evidence. Lower evidence cannot silently become stronger evidence.

Open:

- `schema.md`
- `completion-audit.md`

Decision supported:

- whether the audience trusts the package discipline

Do not say:

- a simulator result is hardware proof
- board latency proves task accuracy
- market momentum proves product readiness

### Minute 5-8: Walk The Fourteen Steps

Say:

Each step has one artifact. Each artifact says what it supports, what it does not prove, what evidence is missing, and what work comes next.

Open:

- `index.html`
- the Engineering Work Queue section
- the Journey Dependency Map section

Decision supported:

- whether the audience sees a repeatable workflow instead of a one-off narrative

Do not say:

- all steps are complete
- missing evidence is the same as a failed result
- demo context is measured evidence

### Minute 8-12: Show The Concrete Build Work

Say:

The roadmap becomes real only when silicon, compiler/runtime, backend, frontend, and proof all line up. A chip feature alone is not enough.

Open:

- `engineering-work-queue.md`
- `import-templates/README.md`

Decision supported:

- what must be staffed, built, measured, or deferred

Do not say:

- analog-mlir is already a deployment compiler for our chip
- AIHWKIT handles board runtime or system proof
- a board link alone proves energy or accuracy

### Minute 12-15: Review The Import Templates

Say:

These templates define the files real adapters and lab workflows must produce. They cover compiler placement, analog simulation, board runtime, power and thermal data, calibration, weight updates, sensor path, and task accuracy.

Open:

- `import-templates/compiler-placement.template.json`
- `import-templates/board-runtime-trace.template.json`
- `import-templates/calibration-trace.template.json`
- `import-templates/task-accuracy-report.template.json`

Decision supported:

- whether the dev team knows the next concrete integration targets

Do not say:

- templates are proof
- a filled template is valid without backend validation
- one filled template unlocks unrelated claims

### Minute 15-18: Review Source Boundaries

Say:

Outside examples explain why the roadmap matters. They do not prove that this chip supports those models, sensors, boards, or toolchains.

Open:

- `source-review-register.md`

Decision supported:

- which external examples may be used in public or investor language

Do not say:

- Google, Microsoft, NXP, Sony, Prophesee, OpenAI, or Aspirare examples prove our product
- funding trends prove chip readiness
- another company's benchmark applies to this chip

### Minute 18-20: End With Next Gates

Say:

The next milestone is a stronger evidence package for one workload. The package should add real model intake, analog simulation, crossbar simulation, compiler mapping, runtime estimate, board run, power trace, temperature trace, task accuracy, calibration record, update evidence, and final claim boundary.

Open:

- `completion-audit.md`
- `engineering-work-queue.md`

Decision supported:

- whether to fund, staff, narrow scope, find partners, or prepare a customer pilot

Do not say:

- the current package is the final product
- the next step is a broader claim
- production readiness is one test away

## Audience-Specific Use

### Executive

Focus on:

- current answer
- top blockers
- next milestone
- what claims are safe
- what claims are not safe

Skip:

- raw JSON unless asked
- detailed adapter internals

### Customer Technical Team

Focus on:

- workload fit
- artifact proof levels
- missing evidence
- import templates
- claim boundaries

Skip:

- broad market framing after the first few minutes

### Engineering Team

Focus on:

- engineering work queue
- import templates
- schema
- journey dependencies
- smoke tests
- remaining build gates

Skip:

- investor-style market claims

### Investor

Focus on:

- why now
- repeatable proof system
- source boundaries
- concrete next gates
- evidence needed for stronger claims

Skip:

- unsupported comparisons to other chips

## Closeout Sentence

Use this sentence to end the review:

```text
The current package does not prove the chip, but it does prove the company has a clear path for turning a workload into evidence, separating assumptions from measurements, and naming the exact work needed before stronger claims are allowed.
```
