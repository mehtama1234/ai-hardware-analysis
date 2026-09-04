# Stable Bias Accumulates Across Layers

The object is repeated state update. A foundation model is not one layer. It is many layers applied in sequence. The output of one block becomes the input of the next block. That means hardware error has a history.

Random error and stable bias are different physical objects. Random error changes direction from use to use. Stable bias points in a similar direction each time. A single-layer RMS number can hide this difference.

The constraint is accumulation. If a hardware path adds a small zero-mean error, later operations may shrink, rotate, or partly cancel it. If a hardware path adds the same offset or gain error at every layer, the model may carry that error forward:

```text
x_{l+1,noisy} = block_l(x_{l,noisy}) + b_l
```

Even when `b_l` is small, the repeated addition can move the state. The damage is not only the size of one error. It is whether the error has direction and persistence.

## The Difference Between Noise And Bias

Random noise is uncertainty around a value:

```text
error_l ~ random with mean near 0
```

Stable bias is a systematic shift:

```text
error_l ~= same direction each use
```

In analog in-memory compute, random error can come from thermal noise, stochastic read variation, or random quantization residue. Stable bias can come from column gain error, ADC offset, DAC offset, drift that is not recalibrated, or a repeated scale mismatch.

A model can sometimes tolerate random noise because each layer sees a different perturbation. Stable bias is harder because the model may keep receiving the same push.

## The Mathematical Boundary

For a stack of blocks, state error evolves roughly as:

```text
e_{l+1} = J_l e_l + hardware_error_l
```

`J_l` is the local sensitivity of the next block to the current state. If `hardware_error_l` changes randomly, the stack may not move in one clean direction. If `hardware_error_l` has a stable component, the stack can drift.

This is why calibration matters. Calibration is not just a cosmetic improvement to a current readout. It tries to remove the stable part of the error:

```text
measured = gain * ideal + offset + random_noise
corrected = (measured - offset) / gain
```

Correction does not remove all noise. It removes the part that would otherwise keep pushing the state in a repeatable direction.

## Concrete Design Move

The concrete design move is to report errors by type:

- random output noise
- fixed output bias
- fixed gain error
- drift since last calibration
- residual error after calibration
- final state error after many layers

Then run the same toy stack twice. In the first run, draw new random error at every layer. In the second run, apply a stable bias direction at every layer. Match their first-layer RMS error. If the biased stack drifts more over depth, the accelerator needs calibration or residual correction.

## Measurement

The measurement is state error as a function of layer count:

```text
relative_state_error(depth)
```

The useful table should show one-layer, four-layer, eight-layer, and sixteen-layer behavior. It should also show whether the mean signed error grows. RMS error tells size. Mean signed error tells direction.

A good hardware claim should not only say the average layer error is small. It should say whether the error is random, stable, calibrated, drifting, or corrected. Those categories decide whether the model survives depth.

## Failure Mode

The failure mode is to treat all analog error as one noise number. That loses the physics. A noisy comparator, a biased ADC, a drifting conductance, and an uncorrected column gain are not the same problem.

The first-principles claim is that depth turns hardware error into a state-history problem. One approximate block can look acceptable while many approximate blocks drift. Hybrid analog/digital design must therefore measure not only error magnitude, but error persistence.
