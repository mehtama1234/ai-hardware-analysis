# Current Simulator Adapter Status

This page answers one narrow question:

Can the current local system run AIHWKIT or CrossSim as real simulator evidence for the analog in-memory compute path?

Current answer: both tools are installed in the optional simulator environment,
and both have produced small strict payloads. CrossSim also has accepted
calibrated replay payloads for named workload fixtures. AIHWKIT has run a small
fixture, but its deeper replay is retained as a rejected result and the guarded
runtime falls back to digital execution.

This still does not mean the whole analog chip is proven. It means the next simulator-evidence step can run small fixtures and write strict payloads for review.

## Object

The object is the analog simulator adapter.

It sits between the local analog evidence and stronger external simulator evidence.

The local evidence says:

- which model operators were considered for analog execution
- what local analog residual was estimated
- which rows the digital governor allowed or blocked

The stronger evidence exists only for the named fixtures that actually ran. It
does not automatically apply to every model, layer, or the physical converter.

## Constraint

The hard part is not naming the tool.

The hard part is proving that the tool executed and that its output matches the same object being reviewed.

For AIHWKIT, the object should be a model or layer running with analog device assumptions.

For CrossSim, the object should be a crossbar-style matrix operation with array, converter, noise, and parasitic assumptions.

If the tool is missing, the system must say missing. It must not turn a skipped check into simulation evidence.

## Design Move

The bridge now runs:

```bash
python3 scripts/check_aimc_simulator_adapters.py
```

That script checks whether the expected Python modules are importable.

The general tool check also reports the same next-proof gap:

```bash
./scripts/check_tools.sh
```

It treats `aihwkit` and CrossSim Python modules as optional simulator adapters. If the simulator venv exists, the command uses it for these checks. If the modules are missing, the command reports `OPTIONAL-MISSING` instead of failing the required EDA tool check.

It then writes:

- `evidence/aimc-simulator-adapters/simulator-adapter-status.json`
- `evidence/aimc-simulator-adapters/simulator-adapter-status.md`

The run-output contract is defined in `analog-simulator-adapter-output-contract.md`.

The optional install path is explained in `optional-aimc-simulator-install-path.md`.

The current result from the optional simulator environment is:

- AIHWKIT: available
- CrossSim: available
- AIHWKIT smoke: ran
- CrossSim smoke: ran
- analog candidates compared against local residuals: 3
- claim effect: broad chip claims are not upgraded

The future run payload paths are:

- `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`

Those files now exist after small optional simulator fixtures ran. They are
bounded to those fixtures. Larger calibrated CrossSim payloads are imported for
named projection, attention, transformer-block, and deep-MLP replays; they are
simulator evidence, not physical converter evidence. The AIHWKIT payload is
retained, but its small-fixture pass must not be read as full-model accuracy.

The guarded backend import path is explained in `guarded-simulator-payload-import.md`.

The smoke-report paths are:

- `evidence/aimc-simulator-adapters/aihwkit-smoke-run.json`
- `evidence/aimc-simulator-adapters/crosssim-smoke-run.json`

Those files are written only if the corresponding module is importable and the tiny smoke run succeeds. A smoke run proves tool availability only. It does not prove task accuracy, board behavior, or silicon behavior.

## Evidence

There are two levels of evidence here. The adapter-status file is an
availability and boundary report. The separate strict payloads are actual small
simulator runs with stated assumptions and measured output differences.

It proves:

- the bridge checked for AIHWKIT
- the bridge checked for CrossSim
- the bridge recorded tool availability
- both smoke checks ran in the optional simulator environment
- optional strict payload files were generated and validated
- the bridge refused to turn small fixture output into measured silicon or production evidence

The cross-repo proof now records the same status:

- `aihwkit_adapter,available`
- `crosssim_adapter,available`
- `optional_simulator_payloads,{"aihwkit": "wrote_payload", "crosssim": "wrote_payload"}`

## Allowed Claim

The system can say:

The combined AIMC bridge checks whether AIHWKIT and CrossSim are available, runs small availability fixtures when they are installed, and prevents those fixtures from becoming broader hardware claims.

## Refused Claim

The system cannot say:

- AIHWKIT validated the full model
- CrossSim validated the full crossbar design
- external simulator agreement exists for the whole AIMC system
- analog accuracy is proven by AIHWKIT or CrossSim
- the chip is calibrated
- board latency or power is measured
- production readiness is proven

Those claims need real tool output or measured hardware evidence.

## Next Handoff

The next real improvement is feeding calibrated simulator residuals back into the
analog placement and governor decision, while keeping the physical converter
gate separate.

For AIHWKIT, the adapter should:

- load or build a small model layer
- apply explicit analog device assumptions
- run inference
- measure output difference from the digital baseline
- export a strict `analog_error_simulation` payload only if the run succeeds

For CrossSim, the adapter should:

- build a concrete matrix-vector case from the selected analog candidate
- state the array size, bit slicing, ADC range, DAC precision, and parasitic assumptions
- run the simulator
- compare the result to the local residual
- export a strict `analog_error_simulation` payload only if the run succeeds

Until then, the small simulator payloads are useful, but they are not proof of analog hardware behavior.
