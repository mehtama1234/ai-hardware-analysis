# Multi-Tile Scheduler Runtime Trace

This trace connects the per-tile health action to a system-level scheduling decision over a token stream.

```text
tile action 0 = serve
tile action 1 = recalibrate
tile action 2 = disable
tile action 3 = probe
decision 0 = digital fallback
decision 1 = analog service
decision 2 = recalibration
decision 3 = probe
```

## Event Counts

- analog_accepted: 17
- calibration_done: 1
- digital_fallback: 5
- probe_failed: 1
- residual_fallback_disable: 1
- residual_fallback_observe: 1
- stale_fallback_recalibrate: 2

## Trace

| token | requested | candidate | budget | before | busy | decision | selected | reason | event | after |
| ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 0 | 0 | 1 | 1 | 0003 | 0000 | 1 | 0 | requested_tile_serves | analog_accepted | 0003 |
| 1 | 1 | 1 | 1 | 0003 | 0000 | 1 | 1 | requested_tile_serves | analog_accepted | 0003 |
| 2 | 2 | 1 | 1 | 0003 | 0000 | 1 | 2 | requested_tile_serves | analog_accepted | 0003 |
| 3 | 3 | 1 | 1 | 0003 | 0000 | 1 | 0 | spare_tile_serves | analog_accepted | 0003 |
| 4 | 0 | 1 | 1 | 0003 | 0000 | 1 | 0 | requested_tile_serves | analog_accepted | 0003 |
| 5 | 1 | 1 | 1 | 0003 | 0000 | 1 | 1 | requested_tile_serves | residual_fallback_observe | 0003 |
| 6 | 2 | 0 | 1 | 0003 | 0000 | 0 | 2 | analog_not_allowed | digital_fallback | 0003 |
| 7 | 3 | 1 | 1 | 0003 | 0000 | 1 | 0 | spare_tile_serves | analog_accepted | 0003 |
| 8 | 0 | 1 | 1 | 0003 | 0000 | 1 | 0 | requested_tile_serves | analog_accepted | 0003 |
| 9 | 1 | 1 | 0 | 0003 | 0000 | 1 | 1 | requested_tile_serves | analog_accepted | 0003 |
| 10 | 2 | 1 | 0 | 0003 | 0000 | 1 | 2 | requested_tile_serves | analog_accepted | 0003 |
| 11 | 3 | 1 | 1 | 0003 | 0000 | 1 | 0 | spare_tile_serves | analog_accepted | 0003 |
| 12 | 0 | 1 | 1 | 0003 | 0000 | 1 | 0 | requested_tile_serves | analog_accepted | 0003 |
| 13 | 1 | 0 | 1 | 0003 | 0000 | 0 | 1 | analog_not_allowed | digital_fallback | 0003 |
| 14 | 2 | 1 | 1 | 0003 | 0000 | 1 | 2 | requested_tile_serves | stale_fallback_recalibrate | 0013 |
| 15 | 3 | 1 | 1 | 0013 | 0000 | 1 | 0 | spare_tile_serves | analog_accepted | 0013 |
| 16 | 0 | 1 | 1 | 0013 | 0000 | 1 | 0 | requested_tile_serves | analog_accepted | 0013 |
| 17 | 1 | 1 | 0 | 0013 | 0000 | 1 | 1 | requested_tile_serves | residual_fallback_disable | 0213 |
| 18 | 2 | 1 | 1 | 0213 | 1100 | 2 | 2 | recalibrate_before_probe | calibration_done | 0203 |
| 19 | 3 | 1 | 1 | 0203 | 1110 | 3 | 3 | probe_disabled_tile | probe_failed | 0202 |
| 20 | 0 | 0 | 1 | 0202 | 0000 | 0 | 0 | analog_not_allowed | digital_fallback | 0202 |
| 21 | 1 | 1 | 1 | 0202 | 0000 | 1 | 0 | spare_tile_serves | analog_accepted | 0202 |
| 22 | 2 | 1 | 1 | 0202 | 0000 | 1 | 2 | requested_tile_serves | analog_accepted | 0202 |
| 23 | 3 | 1 | 1 | 0202 | 1111 | 0 | 3 | all_tiles_unusable_or_busy | digital_fallback | 0202 |
| 24 | 0 | 1 | 1 | 0202 | 0000 | 1 | 0 | requested_tile_serves | stale_fallback_recalibrate | 1202 |
| 25 | 1 | 1 | 1 | 1202 | 0000 | 1 | 2 | spare_tile_serves | analog_accepted | 1202 |
| 26 | 2 | 1 | 1 | 1202 | 0000 | 1 | 2 | requested_tile_serves | analog_accepted | 1202 |
| 27 | 3 | 0 | 1 | 1202 | 0000 | 0 | 3 | analog_not_allowed | digital_fallback | 1202 |

## Interpretation

The useful boundary is that the scheduler does not create trust. It spends visible trust. A serving tile can handle analog work. A recalibrating tile consumes maintenance budget before it serves again. A disabled tile cannot serve directly; it must enter probe and pass. If the requested tile is weak but a spare tile can serve, analog remains useful. If no tile can serve and maintenance budget is zero, the correct decision is digital fallback.
