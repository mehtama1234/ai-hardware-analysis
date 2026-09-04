# Integrated Scheduler And Governor Runtime

This trace joins two different decisions. The scheduler asks which tile action is available. The governor asks whether another analog error should be spent at all.

## Operating Point Assumed By This Trace

| name | ADC | DAC | row case ohm | row loss % | converter error | converter energy x | SAR comparisons | signed-crossbar error | residual q8 | sensitivity q8 | drift age | governor assumption |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| lowest_energy_useful_converter_boundary | 6 | 4 | 100 | 6.93 | 0.0900 | 3.22 | 24 | 2.979e-16 | 12 | 140 | 4 | eligible for analog service while cumulative state budget remains available |

## Final Reason Counts

- analog_recalibrate_soon: 4
- analog_requested_tile: 5
- analog_spare_tile: 8
- no_sample: 2
- not_analog_candidate: 3
- scheduler_digital: 8
- scheduler_probe: 4
- scheduler_recalibrate: 2

## Trace

| token | evidence | actions | busy | residual | drift | sensitivity | cumulative | scheduler | governor | final | selected | reason | next |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 0 | full_calibration | 0003 | 0000 | 12 | 0 | 90 | 0 | 0 | 0 | 0 | 0 | no_sample | 0 |
| 1 | serve | 0003 | 0100 | 10 | 1 | 140 | 4 | 1 | 1 | 1 | 0 | analog_spare_tile | 9 |
| 2 | serve | 0003 | 0010 | 9 | 2 | 210 | 9 | 1 | 1 | 1 | 0 | analog_spare_tile | 16 |
| 3 | serve | 0003 | 1100 | 8 | 3 | 150 | 16 | 1 | 1 | 1 | 2 | analog_spare_tile | 22 |
| 4 | serve | 0003 | 1110 | 12 | 4 | 120 | 22 | 3 | 1 | 3 | 3 | scheduler_probe | 29 |
| 5 | serve | 0013 | 1111 | 10 | 5 | 230 | 29 | 0 | 1 | 0 | 1 | scheduler_digital | 38 |
| 6 | serve | 0013 | 0000 | 9 | 6 | 160 | 38 | 0 | 0 | 0 | 2 | not_analog_candidate | 38 |
| 7 | serve | 0013 | 0100 | 8 | 7 | 100 | 47 | 1 | 1 | 1 | 0 | analog_spare_tile | 55 |
| 8 | serve | 0013 | 0010 | 12 | 8 | 90 | 55 | 1 | 1 | 1 | 0 | analog_requested_tile | 65 |
| 9 | column_3_calibration | 0013 | 1100 | 10 | 0 | 140 | 65 | 2 | 1 | 2 | 2 | scheduler_recalibrate | 69 |
| 10 | serve | 0213 | 1110 | 9 | 1 | 210 | 69 | 3 | 1 | 3 | 3 | scheduler_probe | 75 |
| 11 | serve | 0213 | 1111 | 8 | 2 | 150 | 75 | 0 | 1 | 0 | 3 | scheduler_digital | 80 |
| 12 | serve | 0213 | 0000 | 12 | 3 | 120 | 80 | 1 | 1 | 1 | 0 | analog_recalibrate_soon | 87 |
| 13 | serve | 0213 | 0100 | 10 | 4 | 230 | 87 | 1 | 1 | 1 | 0 | analog_recalibrate_soon | 96 |
| 14 | full_calibration | 0213 | 0010 | 9 | 0 | 160 | 96 | 0 | 0 | 0 | 2 | not_analog_candidate | 96 |
| 15 | serve | 0203 | 1100 | 8 | 1 | 100 | 24 | 1 | 1 | 1 | 2 | analog_spare_tile | 28 |
| 16 | serve | 0203 | 1110 | 12 | 2 | 90 | 28 | 3 | 1 | 3 | 3 | scheduler_probe | 33 |
| 17 | serve | 0203 | 1111 | 10 | 3 | 140 | 33 | 0 | 1 | 0 | 1 | scheduler_digital | 39 |
| 18 | serve | 0203 | 0000 | 9 | 4 | 210 | 39 | 1 | 1 | 1 | 2 | analog_requested_tile | 47 |
| 19 | serve | 0203 | 0100 | 8 | 5 | 150 | 47 | 1 | 1 | 1 | 0 | analog_spare_tile | 55 |
| 20 | column_3_calibration | 0202 | 0010 | 12 | 0 | 120 | 55 | 1 | 1 | 1 | 0 | analog_requested_tile | 59 |
| 21 | serve | 0202 | 1100 | 10 | 1 | 230 | 59 | 1 | 1 | 1 | 2 | analog_spare_tile | 65 |
| 22 | serve | 0202 | 1110 | 9 | 2 | 160 | 65 | 0 | 1 | 0 | 2 | scheduler_digital | 71 |
| 23 | serve | 0202 | 1111 | 8 | 3 | 100 | 71 | 0 | 1 | 0 | 3 | scheduler_digital | 76 |
| 24 | serve | 0202 | 0000 | 12 | 4 | 90 | 76 | 1 | 1 | 1 | 0 | analog_recalibrate_soon | 83 |
| 25 | full_calibration | 1202 | 0100 | 10 | 0 | 140 | 83 | 1 | 1 | 1 | 2 | analog_recalibrate_soon | 87 |
| 26 | serve | 1202 | 0010 | 9 | 1 | 210 | 87 | 2 | 1 | 2 | 0 | scheduler_recalibrate | 93 |
| 27 | serve | 1202 | 1100 | 8 | 2 | 150 | 93 | 0 | 0 | 0 | 3 | no_sample | 93 |
| 28 | serve | 1202 | 1110 | 12 | 3 | 120 | 24 | 0 | 1 | 0 | 0 | scheduler_digital | 31 |
| 29 | serve | 1202 | 1111 | 10 | 4 | 230 | 31 | 0 | 1 | 0 | 1 | scheduler_digital | 40 |
| 30 | serve | 0003 | 0000 | 9 | 5 | 160 | 40 | 1 | 1 | 1 | 2 | analog_requested_tile | 48 |
| 31 | serve | 0003 | 0100 | 8 | 6 | 100 | 48 | 0 | 0 | 0 | 3 | not_analog_candidate | 48 |
| 32 | serve | 0003 | 0010 | 12 | 7 | 90 | 56 | 1 | 1 | 1 | 0 | analog_requested_tile | 65 |
| 33 | serve | 0003 | 1100 | 10 | 8 | 140 | 65 | 1 | 1 | 1 | 2 | analog_spare_tile | 75 |
| 34 | serve | 0003 | 1110 | 9 | 9 | 210 | 75 | 3 | 1 | 3 | 3 | scheduler_probe | 87 |
| 35 | serve | 0013 | 1111 | 8 | 10 | 150 | 87 | 0 | 0 | 0 | 3 | scheduler_digital | 87 |

## Interpretation

The combined policy prevents two common mistakes. A healthy available tile is not enough, because the governor can still refuse the analog error spend. A strict governor is not enough, because maintenance and spare-tile decisions still need tile-state scheduling. Analog service is allowed only when both conditions are true: a tile can serve, and the next analog error remains inside the model-state budget.

The governor evidence in this trace is loaded from `analog-tile-state-trace.csv`. The operating point is loaded from `tile-operating-point.csv`. Together they state the full claim: signed weights are represented by differential conductance, the 100 ohm row-wire case loses measured current, ADC/DAC conversion has a chosen cost/error boundary, and each token still needs a runtime decision before analog output can become model state.
