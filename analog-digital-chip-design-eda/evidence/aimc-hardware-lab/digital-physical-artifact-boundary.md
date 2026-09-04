# Digital Physical Artifact Boundary

- status: `digital_physical_artifacts_present_analog_converter_post_layout_missing`
- metrics files checked: `6`
- digital physical flow supported count: `6`
- CTS-enabled supported count: `4`
- no-CTS supported count: `2`
- analog converter post-layout supported: `False`

## First Principle

A routed digital controller and an extracted analog converter are different physical objects. The controller evidence says that the decision logic can become gates, wires, timing views, and layout views. The converter evidence must say what the DAC, ADC, reference, mux, and sampling path cost after their own layout and extraction. One cannot substitute for the other.

## Checked Runs

### aimc_tile_service_scheduler_physical

- metrics file: `labs/eda/aimc-tile-service-scheduler-openlane-prep/openlane-cts-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_tile_service_scheduler_physical/runs/aimc_tile_service_scheduler_cts`
- clock boundary: `cts_enabled_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `2.52`
- suggested clock period: `5.0`

### aimc_error_budget_governor_physical

- metrics file: `labs/eda/aimc-error-budget-governor-openlane-prep/openlane-cts-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_error_budget_governor_physical/runs/aimc_error_budget_governor_cts`
- clock boundary: `cts_enabled_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `4.71`
- suggested clock period: `5.0`

### aimc_scheduler_governor_physical

- metrics file: `labs/eda/aimc-scheduler-governor-openlane-prep/openlane-cts-8ns-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_physical/runs/aimc_scheduler_governor_cts_8ns`
- clock boundary: `cts_enabled_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `6.14`
- suggested clock period: `8.0`

### aimc_scheduler_governor_pipelined

- metrics file: `labs/eda/aimc-scheduler-governor-pipelined-openlane-prep/openlane-5ns-control-reset-fanout20-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_scheduler_governor_pipelined/runs/aimc_scheduler_governor_pipelined_5ns_control_reset_fanout20`
- clock boundary: `cts_enabled_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `4.99`
- suggested clock period: `5.0`

### aimc_control_plane

- metrics file: `labs/eda/aimc-control-plane-openlane-prep/openlane-no-cts-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_control_plane/runs/aimc_control_plane_no_cts`
- clock boundary: `no_cts_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `1.75`
- suggested clock period: `10.0`

### aimc_micro_tile_controller

- metrics file: `labs/eda/aimc-micro-tile-controller-openlane-prep/openlane-no-cts-metrics-summary.md`
- run dir: `/home/mehtama1/eda-tools/OpenLane/designs/aimc_micro_tile_controller/runs/aimc_micro_tile_controller_recovery_probe_no_cts`
- clock boundary: `no_cts_exploratory`
- final views complete: `True`
- physical flow supported: `True`
- critical path ns: `8.57`
- suggested clock period: `12.0`

## Refused Claim

does not claim analog converter layout, analog tile layout, measured silicon, board power, or production signoff
