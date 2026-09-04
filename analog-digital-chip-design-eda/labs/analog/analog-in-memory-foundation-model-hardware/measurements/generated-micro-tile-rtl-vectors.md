# Generated Micro-Tile RTL Vectors

These rows are generated from the analog-side micro-tile assumptions and consumed by the Verilog controller testbench.

The central rule is that analog placement is only permission to try a tile. The readout can still refuse the measured value. The counters then turn repeated evidence into a serving action.

```text
tile_health_action 0 = serve
tile_health_action 1 = recalibrate
tile_health_action 2 = disable
tile_health_action 3 = probe
```

| case | placement | readout reason | expected path | expected reason | fallback count | accepted count | residual fallbacks | stale fallbacks | action |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| qkv_analog_readout_accepted | analog | ok | 1 | 1 | 0 | 1 | 0 | 0 | 0 |
| qkv_residual_forces_fallback | analog | residual_high | 0 | 10 | 1 | 1 | 1 | 0 | 0 |
| qkv_stale_calibration_fallback | analog | calibration_stale | 0 | 11 | 2 | 1 | 1 | 1 | 1 |
| qkv_disabled_tile_fallback | analog | tile_disabled | 0 | 9 | 3 | 1 | 1 | 1 | 1 |
| attention_score_hybrid_review | hybrid_review | not_sampled | 2 | 2 | 3 | 1 | 1 | 1 | 1 |
| softmax_partition_digital | digital | not_sampled | 0 | 0 | 3 | 1 | 1 | 1 | 1 |
| missing_weights_partition_digital | digital | not_sampled | 0 | 3 | 3 | 1 | 1 | 1 | 1 |
| second_residual_disables_tile | analog | residual_high | 0 | 10 | 4 | 1 | 2 | 1 | 2 |

The important transition is visible in the final three analog-failure rows. A stale-calibration fallback requests recalibration because old correction evidence can be refreshed. A disabled tile falls back without changing the reason-specific residual or stale counters. The second residual failure disables analog service because the tile is failing after correction.
