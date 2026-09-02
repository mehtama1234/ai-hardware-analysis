# Engineering Work Queue

Package: `demo-analog-roadmap-001`

This file turns the demo package into concrete build work.

Start from the main workbench [Connected System Map](../connected-system-map.html) before using this queue. The queue uses the same object, constraint, evidence, claim-boundary, and next-handoff contract, then turns missing proof into engineering work.

## Rule

Every stronger claim needs a matching artifact. If the artifact is missing, weak, estimated, simulated, or from the wrong setup, the claim stays blocked.

## Connected-System Contract

Every build item below should produce or improve one object in this chain:

```text
workload -> model graph -> hardware placement -> analog/simulator evidence -> governor row -> RTL/EDA evidence -> backend import -> claim readiness
```

The build queue should not create features that only look complete in the UI. A feature is complete only when it emits a named artifact, records provenance, states what claim it can support, and states what stronger claim remains blocked.

## Build Now

1. Model intake

   Build or connect a parser that records model inputs, outputs, layer list, operator list, shape data, parameter count, and unsupported operators.

2. Analog fit

   Add a classifier that marks each model region as analog candidate, digital required, fallback required, or blocked. The output must explain why.

3. Analog accuracy risk

   Connect AIHWKIT or a local analog error adapter. The artifact must record noise, drift, precision, write variation, temperature assumptions, baseline accuracy, and mapped accuracy.

4. Crossbar layout risk

   Connect CrossSim or a local layout estimator. The artifact must record tile size, wire assumptions, bit-slicing rule, converter range, and layout risk.

5. Hardware cost estimate

   Add area, memory, energy, latency, converter, and data movement estimates. Label every number as estimate until measured.

6. Compiler mapping

   Add the chip target path. The compiler must output tile placement, bit-slicing, analog and digital split, runtime commands, register writes, calibration metadata, update metadata, and failure reasons.

7. Transformer and VLA check

   Add scanning for transformer blocks, VLA action heads, sensor frontends, attention, normalization, unsupported operators, digital boundaries, and fallback points.

8. Full-system runtime

   Add a runtime estimator that counts host dispatch, memory movement, synchronization, ADC timing, DAC timing, tile parallelism, digital accumulation, and fallback cost.

9. Board runtime

   Define the measured board trace import contract. Required fields include package id, workload id, board id, board revision, runtime version, load status, start status, finish status, repeated latency values, synchronized start/end timestamps, host-overhead boundary, fallback events, failure reason, and debug trace.

10. Power and thermal evidence

   Define measured import contracts for power rails, energy per run, average power, peak power, voltage/current samples, temperature trace, equipment, sampling rate, runtime trace id, integration window, board version, firmware version, and package id.

11. Task accuracy

   Define the task result artifact. It must include baseline metric, mapped-model metric, hardware-run metric when available, tolerance, sample count, scenario description, and package id.

12. Weight update readiness

   Define update class and proof. Required fields include write scope, write time, write energy, endurance, retention, rollback, failed update behavior, and post-update accuracy.

13. Sensor boundary readiness

   Define the sensor path artifact. Required fields include sensor type, capture latency, preprocessing cost, buffering cost, synchronization cost, input energy, and task linkage.

14. Final answer

   Build the claim engine. It must combine all artifacts and return fit, proof level, broken parts, safe claims, blocked claims, and next work.

## Backend Work

The backend must:

- validate every artifact against the package schema
- reject missing required fields
- keep demo evidence separate from measured evidence
- preserve imported raw files
- normalize simulator, compiler, board, power, thermal, task, update, and sensor outputs
- expose package-level and per-artifact endpoints
- export the package for review

## Frontend Work

The frontend must:

- show the package source and proof warning
- show all fourteen steps
- show artifact status and proof level
- show what each artifact supports
- show what each artifact does not prove
- show missing evidence
- show next work
- keep safe claims and blocked claims visible together

## Test Work

The test suite must prove:

- the manifest has fourteen artifacts
- each artifact has required fields
- the journey and package stay aligned
- broad claim words are qualified or blocked
- the readable package index exists
- the main roadmap links to the package index and schema
- missing board proof cannot unlock power or production claims
- simulator evidence cannot unlock measured hardware claims
- board runtime cannot unlock task accuracy claims
