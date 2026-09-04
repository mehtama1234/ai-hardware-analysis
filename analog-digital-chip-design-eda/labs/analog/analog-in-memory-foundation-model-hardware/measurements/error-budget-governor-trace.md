# Error-Budget Governor Trace

This trace turns analog measurement into a serving decision. The object is not the analog multiply by itself. The object is the right to spend another analog error inside a model state that already carries previous error.

```text
decision 0 = digital fallback
decision 1 = analog service
action 0 = keep serving
action 1 = recalibrate before more analog service
action 2 = disable until probe or repair
```

## Reason Counts

- analog_but_recalibrate_soon: 3
- analog_within_budget: 15
- calibration_too_old: 3
- no_sample: 2
- not_analog_candidate: 3
- residual_too_high: 2
- sensitive_path_needs_digital: 2
- state_error_budget_spent: 2

## Trace

| token | valid | candidate | residual | drift age | sensitivity | cumulative | decision | action | reason | next cumulative |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 0 | 0 | 1 | 8 | 2 | 80 | 0 | 0 | 0 | no_sample | 0 |
| 1 | 1 | 1 | 11 | 3 | 96 | 0 | 1 | 0 | analog_within_budget | 6 |
| 2 | 1 | 1 | 17 | 4 | 128 | 6 | 1 | 0 | analog_within_budget | 15 |
| 3 | 1 | 1 | 22 | 5 | 176 | 15 | 1 | 0 | analog_within_budget | 27 |
| 4 | 1 | 1 | 31 | 6 | 208 | 27 | 0 | 0 | sensitive_path_needs_digital | 27 |
| 5 | 1 | 0 | 15 | 7 | 112 | 27 | 0 | 0 | not_analog_candidate | 27 |
| 6 | 1 | 1 | 48 | 8 | 144 | 27 | 0 | 2 | residual_too_high | 27 |
| 7 | 1 | 1 | 19 | 9 | 224 | 27 | 1 | 1 | analog_but_recalibrate_soon | 42 |
| 8 | 1 | 1 | 26 | 0 | 80 | 24 | 1 | 0 | analog_within_budget | 31 |
| 9 | 1 | 1 | 33 | 1 | 96 | 31 | 1 | 0 | analog_within_budget | 41 |
| 10 | 1 | 1 | 12 | 12 | 128 | 41 | 0 | 1 | calibration_too_old | 41 |
| 11 | 1 | 1 | 9 | 13 | 176 | 24 | 0 | 1 | calibration_too_old | 24 |
| 12 | 1 | 1 | 21 | 14 | 208 | 24 | 0 | 1 | calibration_too_old | 24 |
| 13 | 1 | 0 | 37 | 0 | 112 | 24 | 0 | 0 | not_analog_candidate | 24 |
| 14 | 1 | 1 | 28 | 1 | 144 | 24 | 1 | 0 | analog_within_budget | 34 |
| 15 | 1 | 1 | 16 | 2 | 224 | 34 | 1 | 0 | analog_within_budget | 43 |
| 16 | 1 | 1 | 8 | 3 | 80 | 43 | 1 | 0 | analog_within_budget | 48 |
| 17 | 1 | 1 | 11 | 4 | 96 | 48 | 1 | 0 | analog_within_budget | 55 |
| 18 | 1 | 1 | 17 | 5 | 128 | 82 | 1 | 1 | analog_but_recalibrate_soon | 92 |
| 19 | 1 | 1 | 22 | 0 | 176 | 89 | 0 | 1 | state_error_budget_spent | 89 |
| 20 | 1 | 1 | 31 | 0 | 208 | 96 | 0 | 0 | sensitive_path_needs_digital | 96 |
| 21 | 0 | 1 | 15 | 1 | 112 | 96 | 0 | 0 | no_sample | 96 |
| 22 | 1 | 1 | 48 | 2 | 144 | 96 | 0 | 2 | residual_too_high | 96 |
| 23 | 1 | 1 | 19 | 3 | 224 | 96 | 0 | 1 | state_error_budget_spent | 96 |
| 24 | 1 | 1 | 26 | 0 | 80 | 24 | 1 | 0 | analog_within_budget | 31 |
| 25 | 1 | 1 | 33 | 1 | 96 | 31 | 1 | 0 | analog_within_budget | 41 |
| 26 | 1 | 1 | 12 | 2 | 128 | 41 | 1 | 0 | analog_within_budget | 47 |
| 27 | 1 | 1 | 9 | 3 | 176 | 47 | 1 | 0 | analog_within_budget | 54 |
| 28 | 1 | 1 | 21 | 4 | 208 | 54 | 1 | 0 | analog_within_budget | 65 |
| 29 | 1 | 0 | 37 | 5 | 112 | 65 | 0 | 0 | not_analog_candidate | 65 |
| 30 | 1 | 1 | 28 | 6 | 144 | 65 | 1 | 0 | analog_within_budget | 78 |
| 31 | 1 | 1 | 16 | 7 | 224 | 78 | 1 | 1 | analog_but_recalibrate_soon | 90 |

## Interpretation

The governor refuses analog work for four different reasons. A high residual says this tile did not reproduce the local projection. Old calibration says the measurement may be stale even before this token is served. A sensitive path says a modest numeric error can move the model decision. A spent state budget says previous accepted analog work has already used the room that was available.

The important design move is that digital fallback is not failure. It is the mechanism that keeps analog compute bounded. Analog service is useful only when the control plane can say why this particular use is still inside the budget.
