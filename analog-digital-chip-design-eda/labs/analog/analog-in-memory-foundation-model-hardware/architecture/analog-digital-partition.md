# Analog/Digital Partition

The analog part should be assigned the repeated weighted sums. The digital part should keep state, scale values, correct measured errors, choose the next operation, and move data through memory.

```text
activation SRAM -> DAC bank -> conductance tile -> ADC bank -> digital accumulator
        ^                                                        |
        |                                                        v
   scheduler <- KV cache / control / normalization / correction logic
```

Good analog candidates:

- MLP up projection
- MLP down projection
- attention Q/K/V projections
- low-rank adapter projection

Better digital candidates:

- RMSNorm and LayerNorm
- softmax
- KV-cache addressing
- token sampling
- routing
- calibration tables
- residual correction

The failure mode is mapping a whole transformer block to analog because some of its operations are matrix multiplies. The useful split is smaller: analog tiles compute bounded approximate projections, and digital logic keeps the model state coherent.

## Boundary Accounting

The partition must count four costs:

- moving activations to the tile
- converting digital activations into row voltages
- converting column currents back into numbers
- correcting and accumulating partial sums

The array can reduce multiply-add energy while losing the total system comparison if these four costs dominate. This is why the lab keeps an energy model next to the matrix model. The physical dot product and the system-level accelerator are different claims.

## Calibration Loop

The digital side should periodically run known vectors through the array. The expected output is computed or stored digitally. The measured output is used to estimate column gain and bias:

```text
y_true ~= gain * y_measured + bias
```

This correction is cheap compared with redesigning the analog array, but it has limits. It corrects stable column-scale errors better than random read noise. It works better when drift is slow than when device state changes unpredictably during inference. The corrected output is still evidence-bound: the accelerator knows what it measured and what correction it applied.

## Residual Correction

A stronger digital fallback is residual correction. The analog tile produces an approximate vector. The digital side estimates which outputs are most likely to be wrong, recomputes or corrects only those positions, and leaves the rest alone.

This is a trade between full digital recomputation and blind analog trust:

```text
y = y_analog + sparse_digital_residual
```

The object is no longer the whole matrix multiply. The object is the error tail. If a small number of output channels carry most of the error, sparse correction can recover accuracy with limited digital work. If error is spread evenly across all channels, residual correction becomes full recomputation and loses its point.
