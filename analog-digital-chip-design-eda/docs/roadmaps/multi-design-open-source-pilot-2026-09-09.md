# Multi-design open-source verification pilot

## Goal

Turn the existing seeded-counter vertical slice into a customer-shaped,
simulation/formal-first verification pilot that can process multiple RTL
designs through the same evidence-backed workflow. The pilot must demonstrate
failure detection, evidence-linked diagnosis, human-gated repair, retest, and
reproducible proof-of-value metrics without proprietary EDA tools or hardware.

## Current starting point

The counter benchmark already exercises specification ingestion, typed IR,
procedural-check generation, Icarus/VVP execution, waveform triage, formal
counterexample handling, bounded repair, closure, artifact hashing, and AIMC
claim separation. It proves the workflow mechanics for one design.

The shared benchmark setup now emits typed specification IR, a verification
plan, planning queue, and reviewable generated SVA checks for every benchmark.
This keeps generated intent visible even when the measured open-source
simulator cannot execute concurrent SVA.

## First expansion delivered

`benchmarks/seeded_fifo/` adds a different stateful bug class: an attempted
write while a two-entry FIFO is full incorrectly increments `count`. Its
testbench, recorded Icarus/VVP runs, waveform, failure parser, source marker,
and triage report use the same execution contract. The failure is observed as
`count expected=2 actual=3` at cycle 3.

`benchmarks/multi_design_pilot/run_pilot.py` runs the benchmarks independently
and writes a content-hashed aggregate summary. The current pilot also includes
the hierarchical `register_peripheral` workbench (bus wrapper plus separate CSR
implementation), whose nonzero write incorrectly updates `control`. The
aggregate pilot reports four designs, four classified failures, and zero
blocked backends.

Each benchmark now has a bounded human-approved retest. Repairs are applied
only to separate copies, then compiled and simulated through recorded adapters.
The aggregate report records four failed baselines, four passing retests, and an
`allowed` repair decision for each design.

The pilot also writes and verifies a content-addressed artifact manifest for
each baseline and retest. Its current metrics report complete diagnosis
evidence for all four designs, four unique failure signatures, 0% baseline
functional-check coverage, 100% retest coverage, recorded adapter runtime, and
verified artifact integrity across every run.

Retest reports also carry original and repaired source hashes and assert that
the seeded source remains unchanged. The current aggregate records this
invariant for all four designs, alongside the explicit `allowed` approval
decision.

`validate_pilot.py` copies the complete benchmark bundle to a temporary clean
root and independently recomputes the pilot digest and every baseline/retest
artifact manifest. This prevents a successful generating process from being
the only evidence that its report is reproducible.

## Completion gate

The pilot is complete when at least three representative designs, multiple
seeded bug classes, approved repair/retest flows, formal or simulation
evidence, coverage and regression metrics, and a clean one-command aggregate
report all pass from a clean checkout. Unsupported tools must remain explicit
`blocked` evidence, and no report may promote simulation or formal artifacts
to physical AIMC claims.

## Next implementation steps

1. Factor the repeated benchmark stages into a shared pilot adapter while
   preserving per-design evidence roots.
2. Add a clean-checkout validation command that verifies all report digests and
   artifact manifests after copying the evidence bundle.
