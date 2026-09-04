# AIMC Compiler, Simulator Adapters, and Physical Evidence

This page is the plain-language map of the workbench as it exists now. It
connects the workload portfolio, compiler, simulator adapters, guarded runtime,
and Sky130 physical converter evidence. The HTML version is generated from this
source by `scripts/build_site.py`.

## The end-to-end goal

The goal is to take a real model or workload, decide which operations belong in
analog memory and which stay digital, turn that decision into an executable
schedule, check the analog operations against simulator and circuit evidence,
and eventually run the schedule on hardware with measured accuracy, latency,
energy, and reliability.

The work is deliberately split into gates:

```text
workload
  -> compiler placement and schedule
  -> target-review commands and SRAM map
  -> simulator adapter evidence
  -> guarded runtime decision
  -> physical DAC/comparator gate
  -> firmware and board measurement
```

The first four parts are substantially built. The physical converter gate is
measured but blocked. Firmware, board execution, and silicon measurement are
not yet complete.

## What the compiler now does

The shared compiler covers `12` workloads and `91` operators. It produces:

| output | current result | simple meaning |
| --- | ---: | --- |
| ordered target commands | `321` | the operations the target would perform |
| register-write records | `460` | the control values needed by those commands |
| planning cycles | `687` | a deterministic schedule estimate |
| review bytecode words | `321` | one deterministic 64-bit review encoding per command |
| SRAM maps | `12/12` fit | every workload has a bounded map inside the stated `64 KiB` arena |

The compiler handles workload-dependent placement. It records why an operation
is analog-capable, why another remains digital, how data moves through SRAM,
and where digital fallback is required. This is a meaningful compiler and
runtime handoff, but the 64-bit words are review artifacts. They are not yet an
ISA-validated firmware image, and none of these commands has been observed on a
physical board.

## What workloads are covered

The portfolio spans transformer-style MLPs, attention projections, language
model serving, audio, vision, robotics, and vision-language or physical-AI
intake cases. The portfolio contains `12` workload packages with `91` total
operator rows.

Some named numerical fixtures have positive bounded simulator results. For
example, calibrated CrossSim replay reports approximately:

| fixture | relative output difference |
| --- | ---: |
| projection stack | `5.06455e-8` |
| attention block | `4.17733e-8` |
| transformer MLP block | `4.94498e-8` |
| deep transformer MLP stack | `6.71635e-8` |

These are output comparisons for named fixtures under stated simulator
assumptions. They are not proof of end-task accuracy for a pretrained model.
The guarded runtime currently retains `46` analog-candidate commands but sends
`46` corresponding commands through digital fallback because the physical
converter gate is blocked.

## What the simulator adapters prove

AIHWKIT and CrossSim are installed and both availability smoke tests ran. A
smoke test proves that the tool can be imported and that a tiny operation can
execute; it does not prove the chip design.

Separate strict payloads also exist for small fixtures. CrossSim has additional
accepted calibrated payloads for the named projection, attention,
transformer-block, and deep-MLP replays listed above. AIHWKIT’s small fixture
ran, while its deeper result is retained but rejected by the current accuracy
rule. The adapter evidence is therefore useful for placement and model-level
reasoning, but it cannot authorize analog execution by itself.

The adapter boundary is important:

```text
simulator output = evidence about a modeled array or layer
physical SAR output = evidence about the DAC/comparator circuit
board result = evidence about integrated hardware
```

Those are related checks, not interchangeable checks.

## What the physical converter currently does

The continuous Sky130 candidate uses one shared DAC top plate, four sequential
decisions per conversion, decision-dependent bottom-plate controls, and one
400 ns transient for five requested conversions. The completed run measured all
five conversions at a 20 ps transient step.

| requested code | returned code | result |
| ---: | ---: | --- |
| `0` | `0` | pass |
| `2` | `0` | fail |
| `4` | `3` | fail |
| `6` | `6` | pass |
| `7` | `7` | pass |

The sampled top-plate values stayed within `0..1.8 V`, which means the added
break-before-make timing prevented the shared node from immediately leaving its
legal range. Some internal bottom-plate nodes still went below `0 V` or above
`1.8 V`, and two of five conversions returned the wrong code. The physical gate
therefore remains blocked. This is a concrete circuit result, not an absence of
implementation.

The separate low-source calibrated SAR artifact is stronger in its own named
scope: it completed a 16-code calibration and representative isolated
conversions. It does not close the continuous multicycle gate because the
cycle-to-cycle control and charge-transfer behavior is different.

## What is finished and what remains

| area | status | honest interpretation |
| --- | --- | --- |
| workload portfolio | complete for the current review set | 12 packages are described and validated |
| compiler placement | complete for the current review set | analog, digital, fallback, and SRAM decisions are explicit |
| target lowering | complete as a review artifact | 321 commands, 460 writes, 321 64-bit words; not firmware |
| simulator adapters | bounded evidence complete | named fixtures ran; claims remain fixture-specific |
| guarded runtime | complete | blocked analog candidates fall back to digital |
| continuous physical SAR | measured candidate, rejected | 5 conversions measured; 3/5 correct; internal rail violation remains |
| ISA firmware | open | target bytecode still needs a real instruction-set mapping and validation |
| board execution | open | no synchronized board trace, latency, energy, or thermal result |
| silicon and production readiness | open | no fabricated-device evidence exists |

## Reproduce the current review

```bash
python3 scripts/validate_aimc_workload_portfolio.py
python3 scripts/compile_hybrid_transformer_execution_package.py
python3 scripts/run_aimc_end_to_end_regression.py
python3 scripts/validate_aimc_physical_evidence.py
python3 scripts/validate_project.py
python3 scripts/build_site.py
```

The detailed source artifacts are in
`evidence/aimc-hybrid-compiler-runtime/`,
`evidence/aimc-hardware-lab/`, and
`evidence/aimc-simulator-adapters/`. The main physical decision is recorded in
`sky130-continuous-physical-sar.json`.

## Claim boundary

The project can claim a validated software vertical slice: multiple workloads
are compiled into a shared deterministic schedule, named simulator fixtures
provide bounded analog replay evidence, and blocked analog commands are guarded
with digital fallback.

The project cannot yet claim a working physical AIMC converter, validated
firmware, board performance, measured energy, silicon accuracy, or production
readiness. Those require the remaining physical converter repair, ISA firmware,
board run, and hardware measurements.
