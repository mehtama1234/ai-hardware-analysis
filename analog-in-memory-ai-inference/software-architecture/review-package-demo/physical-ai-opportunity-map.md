# Physical AI Opportunity Map

This file explains where an analog inference chip may fit across Physical AI.

It is market framing, not chip proof. It helps choose where to test first.

## Rule

The first market should not be chosen because it sounds large.

It should be chosen because the workload has a real analog fit:

- repeated matrix-heavy work
- local response needed
- limited power or heat budget
- sensor data close to the chip
- clear task metric
- realistic board and lab test setup
- customer willingness to share a model or test scenario

## Best First Targets

| Opportunity | Why It May Fit Analog | Why It Is A Good First Test | Proof Needed |
| --- | --- | --- | --- |
| Smart camera or inspection node | The workload may run repeated vision inference near a sensor. Local processing can reduce data movement. | The setup can be controlled in a lab with repeatable images, power measurement, and clear pass/fail accuracy. | model parse, analog fit, simulator result, compiler mapping, board run, power trace, temperature trace, task accuracy |
| Tactile or force-sensor preprocessing | The system may need fast local interpretation of touch, pressure, slip, vibration, or force data. | The input path is narrow enough to measure, and the task can be tested with repeatable contact events. | sensor path report, latency trace, input energy, calibration record, task result |
| Industrial anomaly detection | The workload may process vibration, temperature, acoustic, or visual data locally where cloud links are limited. | The task metric can be concrete: detect fault, classify state, or flag anomaly within a time and power budget. | dataset, baseline metric, mapped metric, board runtime, power trace, false positive and false negative report |
| Warehouse or factory edge module | The workload may need local perception or sorting decisions without sending all data to a larger processor. | The environment is structured enough for a first pilot, and task success can be measured repeatedly. | workload profile, model split, system runtime, board trace, power trace, task accuracy under repeated runs |
| Low-power mobile robot subsystem | A robot may need local inference for a narrow subsystem, such as a wrist, sensor cluster, or local perception module. | It is narrower than claiming the whole robot brain. The first test can isolate one subsystem. | sensor-to-answer latency, power, thermal, task result, fallback behavior |

## Targets To Treat Carefully

| Opportunity | Why It Is Tempting | Why It Is Risky | What Must Be Proven First |
| --- | --- | --- | --- |
| Full humanoid robot brain | It is visible and attracts attention. | It includes dynamic attention, action timing, safety behavior, many sensors, and frequent updates. | transformer/VLA split, runtime, task, safety boundary, update, rollback, calibration, power, and thermal evidence |
| Full VLA model deployment | It matches where robotics models are moving. | A partial analog fit can be confused with full model support. | analog/digital split, compiler mapping, board run, task accuracy, update readiness, sensor path, fallback |
| Autonomous vehicle central compute | Local inference matters. | Safety, regulation, redundancy, and full-system validation are heavy. | deterministic runtime, safety case, repeated task evidence, thermal proof, failure behavior, certification path |
| Medical device inference | Low power and local response may matter. | Regulation, patient safety, validation, and liability make early claims hard. | controlled task evidence, calibration, reliability, traceability, safety review, regulatory plan |
| General adaptive edge AI | It is a large story. | Analog weight updates may be slow, power-heavy, or endurance-limited. | update scope, write latency, write energy, endurance, retention, rollback, post-update accuracy |

## First-Market Filter

Use these questions before choosing a pilot:

1. Does the workload spend enough time in repeated matrix math?
2. Can the analog/digital split be explained in one page?
3. Is the task metric clear?
4. Can the customer provide a model or representative dataset?
5. Can the board test run in a controlled lab setup?
6. Can power and temperature be measured during the same run?
7. Does the result need frequent weight updates?
8. Can a failed run fall back safely?
9. Can the evidence package show all assumptions and missing proof?

If the answer to several of these is no, the market may be real but it is not a good first proof target.

## Recommended First Wedge

The most realistic first wedge is a narrow physical-edge inference module, not a full robot brain.

Good first wedge:

```text
one model
one sensor path
one board setup
one power budget
one task metric
one final claim boundary
```

Poor first wedge:

```text
all robots
all VLA models
all sensor types
all update modes
all environments
```

## What The Platform Should Show

For every opportunity, the platform should show:

- workload name
- physical system
- sensor path
- model type
- analog candidate layers
- digital-required layers
- expected update need
- proof available
- proof missing
- first test plan
- safe claim
- blocked claim

## Safe Opportunity Language

Safe:

```text
This opportunity is a candidate first market because it has local inference needs, clear measurements, and possible matrix-heavy work.
```

Not safe:

```text
This market proves the analog chip will win.
```

Safe:

```text
The first pilot should test one workload and one setup before broader claims.
```

Not safe:

```text
The chip is ready for all Physical AI systems.
```

## Product Meaning

This map keeps the company focused.

The roadmap should start where proof can be collected quickly and honestly. It should avoid broad claims until the evidence package contains repeated results across models, boards, sensors, power conditions, calibration conditions, update cases, and task scenarios.
