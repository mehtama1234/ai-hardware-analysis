# Analog Tile State Trace

This trace follows one analog tile over a token stream. The object is not a static dot-product error. The object is tile state: programmed gain, bias, drift age, calibration events, residual error, and the governor decision that follows from them.

## Reason Counts

- analog_but_recalibrate_soon: 7
- analog_within_budget: 26
- state_error_budget_spent: 3

## Trace

| token | event | age | gain error | bias | residual q8 | sensitivity q8 | cumulative | decision | reason | next cumulative |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |
| 0 | full_calibration | 0 | 0.0051 | 0.0021 | 12 | 90 | 0 | analog | analog_within_budget | 4 |
| 1 | serve | 1 | 0.0051 | 0.0021 | 10 | 140 | 4 | analog | analog_within_budget | 9 |
| 2 | serve | 2 | 0.0051 | 0.0021 | 9 | 210 | 9 | analog | analog_within_budget | 16 |
| 3 | serve | 3 | 0.0051 | 0.0021 | 8 | 150 | 16 | analog | analog_within_budget | 22 |
| 4 | serve | 4 | 0.0051 | 0.0021 | 12 | 120 | 22 | analog | analog_within_budget | 29 |
| 5 | serve | 5 | 0.0051 | 0.0021 | 10 | 230 | 29 | analog | analog_within_budget | 38 |
| 6 | serve | 6 | 0.0051 | 0.0021 | 9 | 160 | 38 | analog | analog_within_budget | 47 |
| 7 | serve | 7 | 0.0051 | 0.0021 | 8 | 100 | 47 | analog | analog_within_budget | 55 |
| 8 | serve | 8 | 0.0051 | 0.0021 | 12 | 90 | 55 | analog | analog_within_budget | 65 |
| 9 | column_3_calibration | 0 | 0.0014 | 0.0026 | 10 | 140 | 65 | analog | analog_within_budget | 69 |
| 10 | serve | 1 | 0.0014 | 0.0026 | 9 | 210 | 69 | analog | analog_within_budget | 75 |
| 11 | serve | 2 | 0.0014 | 0.0026 | 8 | 150 | 75 | analog | analog_but_recalibrate_soon | 80 |
| 12 | serve | 3 | 0.0014 | 0.0026 | 12 | 120 | 80 | analog | analog_but_recalibrate_soon | 87 |
| 13 | serve | 4 | 0.0014 | 0.0026 | 10 | 230 | 87 | analog | analog_but_recalibrate_soon | 96 |
| 14 | full_calibration | 0 | 0.0053 | 0.0049 | 9 | 160 | 96 | recalibrate | state_error_budget_spent | 96 |
| 15 | serve | 1 | 0.0053 | 0.0049 | 8 | 100 | 24 | analog | analog_within_budget | 28 |
| 16 | serve | 2 | 0.0053 | 0.0049 | 12 | 90 | 28 | analog | analog_within_budget | 33 |
| 17 | serve | 3 | 0.0053 | 0.0049 | 10 | 140 | 33 | analog | analog_within_budget | 39 |
| 18 | serve | 4 | 0.0053 | 0.0049 | 9 | 210 | 39 | analog | analog_within_budget | 47 |
| 19 | serve | 5 | 0.0053 | 0.0049 | 8 | 150 | 47 | analog | analog_within_budget | 55 |
| 20 | column_3_calibration | 0 | 0.0032 | 0.0044 | 12 | 120 | 55 | analog | analog_within_budget | 59 |
| 21 | serve | 1 | 0.0032 | 0.0044 | 10 | 230 | 59 | analog | analog_within_budget | 65 |
| 22 | serve | 2 | 0.0032 | 0.0044 | 9 | 160 | 65 | analog | analog_within_budget | 71 |
| 23 | serve | 3 | 0.0032 | 0.0044 | 8 | 100 | 71 | analog | analog_within_budget | 76 |
| 24 | serve | 4 | 0.0032 | 0.0044 | 12 | 90 | 76 | analog | analog_but_recalibrate_soon | 83 |
| 25 | full_calibration | 0 | 0.0018 | 0.0032 | 10 | 140 | 83 | analog | analog_but_recalibrate_soon | 87 |
| 26 | serve | 1 | 0.0018 | 0.0032 | 9 | 210 | 87 | analog | analog_but_recalibrate_soon | 93 |
| 27 | serve | 2 | 0.0018 | 0.0032 | 8 | 150 | 93 | recalibrate | state_error_budget_spent | 93 |
| 28 | serve | 3 | 0.0018 | 0.0032 | 12 | 120 | 24 | analog | analog_within_budget | 31 |
| 29 | serve | 4 | 0.0018 | 0.0032 | 10 | 230 | 31 | analog | analog_within_budget | 40 |
| 30 | serve | 5 | 0.0018 | 0.0032 | 9 | 160 | 40 | analog | analog_within_budget | 48 |
| 31 | serve | 6 | 0.0018 | 0.0032 | 8 | 100 | 48 | analog | analog_within_budget | 56 |
| 32 | serve | 7 | 0.0018 | 0.0032 | 12 | 90 | 56 | analog | analog_within_budget | 65 |
| 33 | serve | 8 | 0.0018 | 0.0032 | 10 | 140 | 65 | analog | analog_within_budget | 75 |
| 34 | serve | 9 | 0.0018 | 0.0032 | 9 | 210 | 75 | analog | analog_but_recalibrate_soon | 87 |
| 35 | serve | 10 | 0.0018 | 0.0032 | 8 | 150 | 87 | recalibrate | state_error_budget_spent | 87 |

## First-Principles Reading

A tile is not healthy or unhealthy forever. It moves. Calibration pulls gain and bias back toward the intended dot-product map. Drift pushes them away as tokens pass. The governor should therefore read tile state as a moving measurement, not as a fixed label.

The residual is the visible error at the model boundary. The age is a warning that the visible error may grow. The cumulative budget remembers how much accepted analog error has already entered model state. A useful analog accelerator joins all three. It does not ask only whether the crossbar worked once; it asks whether this tile, at this age, with this residual, on this model path, can be trusted for the next token.
