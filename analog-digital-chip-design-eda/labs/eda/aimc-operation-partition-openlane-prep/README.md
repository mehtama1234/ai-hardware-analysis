# Lab: AIMC Operation Partition OpenLane Prep

This lab packages the transformer operation-partition RTL for a physical-design run. The object is not the analog array and not the whole request scheduler. The object is the combinational decision logic that maps a transformer operation and current evidence into a hardware placement.

## Workflow Contract

Consumes: operation-partition RTL, operation class fields, model-risk fields, registered physical wrapper, OpenLane package files, CTS debug artifacts, and no-CTS physical-flow results.

Produces: physical-flow evidence for the placement decision boundary, CTS failure characterization, and a clear next experiment for clock-tree behavior.

Supports: the claim that the operation placement rule can become routed exploratory geometry and that its CTS boundary has been isolated as a concrete tool/design question.

Refuses: full compiler lowering, clean CTS signoff, measured runtime, measured energy, analog macro safety, or production readiness.

Handoff: this page connects model placement to physical implementation evidence. Its output informs the backend placement story, but it does not upgrade backend claims unless paired with analog/model evidence and later board measurements.

## Object

The operation partition chooses:

```text
digital
analog
hybrid
```

It also emits a reason code. The inputs describe the operation class, resident-weight availability, estimated state error, attention-selection flip risk, token-choice flip risk, calibration age, and weak tile count.

## Constraint

The logical partition block has no internal register. A physical flow therefore needs a timing boundary around it. The OpenLane package uses a wrapper called `aimc_operation_partition_physical` that registers the inputs and outputs around the combinational partition:

```text
external registers -> operation partition logic -> external registers
```

That does not change the partition rule. It gives OpenLane a clocked top module and gives STA a concrete question to answer.

## Files

- `src/aimc_operation_partition.v`: local copy of the operation-partition RTL
- `src/aimc_operation_partition_physical.v`: clocked wrapper for physical-flow timing boundaries
- `src/aimc_operation_partition_output_registered.v`: lean wrapper that registers only `placement` and `reason`
- `config.json`: OpenLane-style design configuration
- `config.tcl`: compatibility configuration for older `flow.tcl` OpenLane runs
- `config_no_cts.tcl`: exploratory no-CTS configuration
- `config_output_registered.tcl`: CTS-enabled config for the lean output-registered wrapper
- `config_output_registered_no_cts.tcl`: no-CTS config for the lean output-registered wrapper
- `analyze_cts_attempts.py`: extracts the clocking boundary from local OpenLane artifacts
- `cts-debug-summary.md`: generated summary of no-CTS clock violations and CTS attempts
- `run_isolated_cts_experiment.sh`: copies the OpenLane issue reproducible and runs named CTS-only variants with a timeout
- `isolated-cts-experiment-plan.md`: states what each CTS-only variant is testing
- `constraint.sdc`: virtual-clock input/output timing assumptions
- `src/constraint.sdc`: SDC copy for older OpenLane design-folder conventions
- `pin_order.cfg`: stable pin-order intent for review

## Concrete Design Move

Check whether this machine can run the package:

```bash
AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_physical AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/check_aimc_openlane_readiness.sh
```

Run local RTL simulation first:

```bash
cd labs/digital/aimc-control-plane-rtl
iverilog -o aimc_operation_partition_tb aimc_operation_partition.v aimc_operation_partition_tb.v
vvp aimc_operation_partition_tb
```

Run synthesis:

```bash
cd labs/digital/aimc-control-plane-synthesis
yosys synth_aimc_operation_partition.ys
```

The no-CTS exploratory OpenLane flow completed with the clocked wrapper. The final report is `openlane-no-cts-final-report.md`. CTS-enabled attempts with both the full input/output wrapper and the lean output-only wrapper reached clock tree synthesis and then stopped advancing after OpenROAD reported `Number of created patterns = 50000`; that boundary is recorded in `openlane-cts-attempt-report.md`.

Regenerate the compact CTS debug summary:

```bash
cd labs/eda/aimc-operation-partition-openlane-prep
python3 analyze_cts_attempts.py
```

List isolated CTS experiments:

```bash
cd labs/eda/aimc-operation-partition-openlane-prep
./run_isolated_cts_experiment.sh list
```

The useful variants are `baseline`, `single_corner`, `small_clusters`, and `no_post_processing`. They run against a copied issue reproducible under `/tmp`, so the original OpenLane run artifact is not edited.

The experiment plan is in `isolated-cts-experiment-plan.md`.

On this machine, use the Docker runner because `openroad` is available through the OpenLane container rather than on the host:

```bash
AIMC_CTS_RUNNER=docker AIMC_CTS_TIMEOUT_SECONDS=180 ./run_isolated_cts_experiment.sh single_corner
```

Current isolated CTS evidence:

```text
single_corner: reached sky130_fd_sc_hd__clkbuf_8 characterization, created 100000 patterns, did not complete
small_clusters: reached sky130_fd_sc_hd__clkbuf_8 characterization, created 100000 patterns, did not complete
```

That means the observed CTS boundary is not explained by multi-corner library loading or by the first sink-clustering change. The minimal clocked toy design in `labs/eda/minimal-clocked-cts-probe` then reached the same characterization behavior, so the next useful work is either a `no_post_processing` negative control, a CTS characterization-argument change, or a different OpenLane/OpenROAD build. The toy result matters because it separates a local OpenROAD/OpenLane CTS behavior from something specific to the operation-partition wrapper.

When OpenLane is available, the command shape is:

```bash
AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_physical AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/run_aimc_openlane_flow.sh
```

For an exploratory no-CTS run:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_operation_partition_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_physical AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/run_aimc_openlane_flow.sh
```

## Measurement

The first physical-flow measurements should be:

- synthesis success under the selected standard-cell library
- floorplan utilization
- placement legality
- route completion
- virtual-clock worst negative slack and total negative slack
- DRC violation count
- LVS result if the flow reaches layout checking
- final area and cell count

Current no-CTS run summary:

```text
flow_status: flow completed
critical_path_ns: 1.58
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
max slew violation count: 84
max fanout violation count: 1
```

The most important timing question is:

```text
Can placement[1:0] and reason[3:0] settle before the external scheduler samples them?
```

## Failure Mode

The failure mode is treating this block as finished because the no-CTS flow completed. The run produced useful routed-layout evidence, but the max-slew and max-fanout warnings still need design cleanup before this can be treated as a clean physical result.

The CTS attempt makes the next step concrete: reduce the clocking load or pipeline the wrapper before claiming clock-tree signoff.

The generated debug summary narrows that statement: both wrapper shapes failed at the same CTS pattern count, and isolated single-corner plus small-cluster runs kept creating characterization patterns. The next experiment should isolate CTS characterization settings or compare against a minimal clocked toy before changing the partition logic again.
