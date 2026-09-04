# Tile Health Monitoring Spends Calibration Where Error Grows

The object is not the whole analog array. The object is a set of columns, rows, converters, and local wires whose errors move at different rates. A fixed calibration schedule treats every part of the tile as equally unhealthy. Real hardware will not behave that way. Some columns drift faster. Some converters have larger offset. Some rows suffer more from driver error or wire drop.

The constraint is measurement budget. A foundation-model accelerator cannot stop often and fully remeasure every tile, every column, and every row. Calibration costs tokens, time, energy, and scheduling space. If only a small part of the tile is unhealthy, full recalibration wastes work. If the wrong part is ignored, stale error keeps entering the model.

So the useful question changes:

```text
not: when do we recalibrate the whole tile?
but: which tile parts need measurement first?
```

## Health Is Evidence About Future Error

A health monitor is a small measurement loop. It sends known probes through the hardware, compares measured output against expected output, and estimates which parts are becoming unreliable.

For a column, the simplest health signal is:

```text
column_error = abs(measured_probe_output - expected_probe_output)
```

But raw error is not enough. A column with high random noise may look unhealthy even if its average behavior is still centered. A column with a slowly growing bias may look acceptable now but become dangerous later. The monitor needs to distinguish noise, bias, and drift.

The useful health score is closer to:

```text
health_score = estimated_drift + estimated_bias + recent_error_growth
```

A high score means the column should be remeasured sooner.

## Why Selective Calibration Helps

Full calibration spends samples everywhere:

```text
calibration_work = columns * samples_per_column
```

Selective calibration spends samples on the worst columns:

```text
calibration_work = selected_columns * samples_per_column
```

If error is uneven, selective calibration can reduce most of the damaging drift with much lower overhead. This is the same idea as residual correction: spend digital work where analog error is largest.

The risk is missing a hidden failure. A monitor that only checks a few columns can miss a quiet but growing error elsewhere. That means the monitor itself needs a schedule: cheap probes often, full sweeps less often, and emergency recalibration when a health score jumps.

## The Mathematical Boundary

For each column `j`, track an estimated error:

```text
e_j(t) = bias_j + drift_rate_j * age_j + random_noise_j
```

After recalibration, the measured bias and drift estimate are reset:

```text
age_j = 0
estimated_bias_j = measured_bias_j
```

Between recalibrations, age grows:

```text
age_j = tokens_since_column_j_was_calibrated
```

The selection rule is:

```text
recalibrate top_k columns by health_score_j
```

The design target is:

```text
mean_error and worst_column_error stay below tolerance
while calibration_work stays below budget
```

## Concrete Design Move

The concrete design move is to replace one global interval with a two-level policy:

- cheap health probes every small interval
- selective recalibration of the worst columns
- occasional full calibration to catch missed slow failures
- emergency calibration if a column error jumps

This changes calibration from a clock into a controller. The digital side is no longer only correcting analog outputs. It is deciding where the next measurement should be spent.

## Measurement

The measurement should compare:

- no recalibration
- full recalibration on a fixed interval
- selective recalibration on a fixed interval
- selective recalibration with occasional full sweep

Report:

```text
policy, calibration_work, mean_error, worst_error, missed_bad_columns
```

Mean error measures average model damage. Worst error catches one bad column that can dominate an output channel. Missed bad columns reveal whether the health monitor is too narrow.

## Failure Mode

The failure mode is to assume one calibration interval is enough for the whole array. That hides uneven physical behavior. A tile can be mostly healthy while a few columns drift badly, or it can look fine on average while one output channel becomes unreliable.

The first-principles claim is that calibration must become selective when arrays get large. The digital system should spend measurement where error grows. A hybrid analog/digital accelerator is therefore not only an analog compute array with correction. It is an analog array watched by a digital measurement policy.
