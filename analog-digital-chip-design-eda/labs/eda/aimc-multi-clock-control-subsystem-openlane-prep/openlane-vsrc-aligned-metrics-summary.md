# aimc_multi_clock_control_subsystem OpenLane Metrics Summary

This file is generated from the selected completed OpenLane run artifacts.

```text
run_dir: /home/mehtama1/eda-tools/OpenLane/designs/aimc_multi_clock_control_subsystem/runs/aimc_multi_clock_control_subsystem_vsrc_aligned
flow_status: flow completed
total_runtime: 0h10m55s0ms
routed_runtime: 0h9m22s0ms
synth_cell_count: 1640
TotalCells: 8702
CoreArea_um^2: 64347.96479999999
DIEAREA_mm^2: 0.0735315588
wire_length: 69777
vias: 16188
wns: -0.63
tns: -8.74
spef_wns: 0.0
spef_tns: 0.0
critical_path_ns: 10.44
suggested_clock_period: 10.0
suggested_clock_frequency: 100.0
tritonRoute_violations: 0
Magic_violations: 0
pin_antenna_violations: 0
net_antenna_violations: 0
lvs_total_errors: 0
```

## Final Artifact Check

```text
def/aimc_multi_clock_control_subsystem.def: present
gds/aimc_multi_clock_control_subsystem.gds: present
lef/aimc_multi_clock_control_subsystem.lef: present
lib/aimc_multi_clock_control_subsystem.lib: present
sdc/aimc_multi_clock_control_subsystem.sdc: present
sdf/aimc_multi_clock_control_subsystem.sdf: present
spef/aimc_multi_clock_control_subsystem.spef: present
```

## Manufacturability Extract

```text
Total Magic DRC violations is 0
Design is LVS clean.
Pin violations: 0
Net violations: 0
```

## Boundary

This summary is from a CTS-enabled OpenLane run. It is local open-source flow evidence, not foundry or commercial-tool tapeout signoff.

Modeled IR-drop worst cases: VPWR 3.87e-03 V, VGND 3.67e-03 V.
The IR-drop run used explicit modeled VPWR/VGND source locations aligned to legal PDN nodes.
These are local package-analysis assumptions, not measured package or board data.
