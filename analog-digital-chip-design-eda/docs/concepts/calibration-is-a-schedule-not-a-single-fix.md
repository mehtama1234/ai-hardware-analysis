# Calibration Is A Schedule, Not A Single Fix

The object is a hardware path whose error changes over time. Calibration measures that path and fits a correction. But the correction is only true for the state of the hardware when it was measured. If the device drifts, the calibration becomes stale.

Analog in-memory compute often has stable error that can be corrected: column gain, column offset, DAC offset, ADC offset, and programmed-conductance mismatch. It also has time movement: device drift, temperature change, supply movement, aging, and repeated-read disturbance. The constraint is that the digital correction must be updated often enough to track the stable part of the error, but not so often that calibration work erases the compute advantage.

The first calibration equation is simple:

```text
measured = gain * ideal + offset + residual_noise
corrected = (measured - offset) / gain
```

This is useful only while `gain` and `offset` remain close to the measured values. When they move, the correction begins to inject error.

## Why One Calibration Is Not Enough

A one-time calibration assumes the analog path is stationary:

```text
gain(t) ~= gain(0)
offset(t) ~= offset(0)
```

Real hardware does not promise that. Conductance can drift. Temperature can move device behavior. Supply noise can shift readout. Converter offsets can change. If the model serves many tokens after calibration, later tokens may be computed under a different hardware state than the one correction was fitted for.

So calibration has two costs:

- the direct cost of measuring known inputs
- the indirect cost of using stale correction between measurements

Calibrating too rarely leaves drift uncorrected. Calibrating too often spends too much time and energy on measurement instead of inference.

## The Mathematical Boundary

Let drift grow with token time:

```text
drift_since_calibration = drift_rate * tokens_since_calibration
```

Let calibration cost grow with the number of samples:

```text
calibration_cost = samples_per_calibration * calibrations
```

The design target is not minimum error alone:

```text
total_cost = inference_cost + calibration_cost
residual_error <= model_tolerance
```

The useful question is: what calibration interval is long enough to keep overhead low and short enough to keep residual drift below tolerance?

## Concrete Design Move

The concrete design move is to report calibration as a schedule:

- calibration samples per tile
- tokens between calibration events
- drift rate assumed
- residual error just before recalibration
- energy or latency spent on calibration
- throughput loss from taking calibration measurements
- model-quality loss when calibration is stale

For a foundation-model accelerator, this should be phase-aware. Prefill may run many tokens through fixed weights quickly. Decode may run for a long time while the same arrays are used token by token. The best calibration interval may differ by phase, layer, tile, and temperature state.

## Measurement

The measurement is residual error and overhead versus interval:

```text
interval_tokens, calibration_overhead, mean_error, worst_error
```

The worst error matters because stale calibration is most dangerous just before the next calibration event. Mean error can make a long interval look acceptable while hiding the end-of-interval drift.

A good lab should compare:

- no calibration
- calibrate every short interval
- calibrate every long interval
- higher sample count per calibration
- lower sample count with noisier correction

The output should reveal the bargain: more frequent calibration reduces stale drift but raises overhead.

## Failure Mode

The failure mode is to report calibrated accuracy without saying when calibration happened, how many samples it used, and how long the hardware ran before the next measurement. That makes the result look cleaner than the deployed system.

The first-principles claim is that calibration is part of the runtime architecture. It is not a one-time cleanup step. If analog compute depends on digital correction, then the schedule for measuring, fitting, applying, and refreshing that correction is part of the accelerator design.
