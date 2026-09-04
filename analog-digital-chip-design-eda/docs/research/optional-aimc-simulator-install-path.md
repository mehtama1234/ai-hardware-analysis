# Optional AIMC Simulator Install Path

This page explains how the optional AIHWKIT and CrossSim tools are installed and used.

The point is not to make the environment look complete. The point is to make the next evidence step executable.

## Object

The object is the optional simulator environment:

- AIHWKIT for model-level analog behavior
- CrossSim for crossbar-style matrix behavior
- the local adapter scripts that decide whether either tool actually ran

These tools sit after the local ngspice and RTL bridge. They can add stronger simulator evidence, but only for the model, layer, or crossbar case they actually execute.

## Constraint

Installation is not evidence.

A Python module can be importable and still prove nothing about the selected analog workload. It becomes useful only when it runs on a concrete object, states its device and array assumptions, measures the difference from a digital reference, and writes the strict JSON payload required by `analog-simulator-adapter-output-contract.md`.

## Design Move

Use the optional installer:

```bash
./scripts/install_optional_aimc_simulators.sh --all
```

It creates a local virtual environment under `$HOME/eda-tools/aimc-simulators-venv` by default.

Current local install:

- AIHWKIT: installed in the optional simulator venv
- CrossSim: installed from the Sandia `cross-sim` checkout
- simulator venv: `$HOME/eda-tools/aimc-simulators-venv`
- CrossSim checkout: `$HOME/eda-tools/cross-sim`

AIHWKIT follows the official IBM install path:

```bash
pip install aihwkit
```

CrossSim follows the Sandia GitHub install path:

```bash
git clone https://github.com/sandialabs/cross-sim.git
pip install ./cross-sim
```

After install, activate the environment:

```bash
source "$HOME/eda-tools/aimc-simulators-venv/bin/activate"
```

Then run:

```bash
./scripts/check_tools.sh
python3 scripts/check_aimc_simulator_adapters.py
```

If either module is importable, the adapter script tries a tiny smoke run. A smoke run proves that the tool can execute a small case. It does not prove the analog foundation-model design.

## Evidence

The first evidence after installation is availability evidence:

- `./scripts/check_tools.sh` should stop reporting `OPTIONAL-MISSING` for the installed module
- `evidence/aimc-simulator-adapters/simulator-adapter-status.json` should record whether the adapter was skipped, ran, or failed
- `evidence/aimc-simulator-adapters/aihwkit-smoke-run.json` or `crosssim-smoke-run.json` should appear only if the tiny smoke run succeeds

The stronger evidence is a strict simulator payload:

- `evidence/aimc-simulator-adapters/aihwkit-analog-error-simulation.json`
- `evidence/aimc-simulator-adapters/crosssim-analog-error-simulation.json`

Those files must pass:

```bash
python3 scripts/import_analog_simulator_payload.py <payload.json>
```

Only after validate-only mode passes should `--import` be used.

## Allowed Claim

The system can say:

The lab has a reproducible install path for optional AIHWKIT and CrossSim adapters, and the bridge can check whether those tools are missing, importable, smoke-runnable, or ready to produce strict simulator evidence.

## Refused Claim

The system cannot say:

- AIHWKIT evidence exists because `pip install aihwkit` completed
- CrossSim evidence exists because the repository was cloned
- a smoke run proves model accuracy
- a simulator payload proves board latency, board power, calibrated silicon, package reliability, or tapeout readiness
- optional simulator availability changes the production claim

## Next Handoff

The next real work is a run adapter that maps one selected analog candidate into AIHWKIT or CrossSim, compares it with the digital baseline, and exports a strict payload.

If the upstream tools do not expose the required fields, patch the adapter first. Patch AIHWKIT or CrossSim only when the missing field cannot be recovered outside the tool.
