# AIMC Operation Partition No-CTS OpenLane Final Report

This report records the exploratory no-CTS OpenLane run for the clocked physical wrapper around the transformer operation-partition logic.

## Run

Command:

```bash
PDK_ROOT=/home/mehtama1/eda-tools/pdks TAG=aimc_operation_partition_no_cts CONFIG_NAME=config_no_cts AIMC_OPENLANE_PREP=aimc-operation-partition-openlane-prep AIMC_OPENLANE_DESIGN=aimc_operation_partition_physical AIMC_OPENLANE_RTL=aimc_operation_partition.v ./scripts/run_aimc_openlane_flow.sh
```

Run directory:

```text
/home/mehtama1/eda-tools/OpenLane/designs/aimc_operation_partition_physical/runs/aimc_operation_partition_no_cts
```

The first attempt used the pure combinational top and failed at placement-stage STA because the OpenLane script expected `CLOCK_PORT`. The fix was to keep `aimc_operation_partition` as the logical combinational block and add `aimc_operation_partition_physical`, a wrapper that registers inputs and outputs around that block.

## Final Metrics

```text
flow_status: flow completed
total_runtime: 0h9m52s0ms
routed_runtime: 0h7m5s0ms
synth_cell_count: 177
TotalCells: 1153
CoreArea_um^2: 9594.2016
DIEAREA_mm^2: 0.013064351025
wire_length: 6284
vias: 1938
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 1.58
suggested_clock_period: 5.0
suggested_clock_frequency: 200.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

Final artifacts:

```text
def/aimc_operation_partition_physical.def: present
gds/aimc_operation_partition_physical.gds: present
lef/aimc_operation_partition_physical.lef: present
lib/aimc_operation_partition_physical.lib: present
mag/aimc_operation_partition_physical.mag: present
maglef/aimc_operation_partition_physical.mag: present
sdc/aimc_operation_partition_physical.sdc: present
sdf/aimc_operation_partition_physical.sdf: present
spef/aimc_operation_partition_physical.spef: present
verilog/aimc_operation_partition_physical.v: present
```

## Physical Checks

The run reached routing, parasitic extraction, multi-corner STA, GDS generation, Magic/KLayout comparison, LVS, Magic DRC, antenna checking, and ERC screening.

Manufacturability report:

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

The detailed router initially iterated on four `met3` spacing violations, then resolved them:

```text
No DRC violations after detailed routing.
No DRC violations after GDS streaming out.
```

## Timing Boundary

The final metrics report says:

```text
wns: 0.0
tns: 0.0
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 1.58
```

The flow also reports:

```text
There are no hold violations in the design at the typical corner.
There are no setup violations in the design at the typical corner.
```

This is useful routed-layout timing evidence for the no-CTS wrapper run. It is not full clock-tree signoff.

## Remaining Warnings

The flow completed with warnings:

```text
Current core area is too small for the power grid settings chosen. The power grid will be scaled down.
VSRC_LOC_FILES is not defined. The IR drop analysis will run, but the values may be inaccurate.
There are max slew violations in the design at the typical corner.
There are max fanout violations in the design at the typical corner.
```

The check report gives:

```text
max slew violation count 84
max fanout violation count 1
```

Those warnings matter. They mean this run is not a clean physical signoff result even though it produced routed layout, final views, zero setup/hold slack violations, zero DRC violations, zero LVS errors, and zero antenna violations.

A CTS-enabled run was attempted to address the clock fanout and slew warnings. It reached clock tree synthesis and then stopped advancing after OpenROAD reported `Number of created patterns = 50000`. See `openlane-cts-attempt-report.md`. Until CTS completes, the correct claim remains: completed no-CTS exploratory physical flow, not clock-tree signoff.

The generated `cts-debug-summary.md` records the no-CTS clock violations and both CTS attempts from local run artifacts.

## What This Proves

This run proves that the operation-partition decision can be packaged as a clocked physical object, accepted by OpenLane, placed, routed, extracted, streamed to GDS, and checked for DRC/LVS/antenna in an exploratory no-CTS flow.

It does not prove final chip readiness. The next design move is to reduce the clocking problem by simplifying or staging the wrapper, then attempt CTS again or run a fuller OpenROAD/OpenSTA flow with explicit clock-tree assumptions.
