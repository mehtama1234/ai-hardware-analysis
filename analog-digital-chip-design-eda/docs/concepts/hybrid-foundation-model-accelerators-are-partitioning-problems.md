# Hybrid Foundation-Model Accelerators Are Partitioning Problems

The object is a computation graph mapped onto unlike physical machines. A foundation model is not one operation. It has dense projections, attention score computation, masking, softmax, normalization, residual addition, activation functions, KV-cache reads and writes, sampling, and control decisions. Analog arrays are good candidates for repeated linear maps. Digital logic is better for exact control, indexing, comparison, sparse movement, nonlinear functions, and correction. The architecture problem is deciding which object goes where.

The constraint is that moving across the boundary costs time, energy, and error. If a tensor leaves digital memory, passes through DACs, enters crossbars, returns through ADCs, and then immediately needs exact digital processing, the boundary crossing must be worth it. A partition is good only when the analog block receives enough reuse and tolerance to pay for conversion and calibration.

A useful first-principles split is:

```text
analog-friendly: dense matrix-vector or matrix-matrix products with bounded precision needs
digital-needed: normalization, softmax, token sampling, cache addressing, control, correction
shared: accumulation, scaling, activation buffering, scheduling
```

The concrete design move is tile scheduling. Keep weights stationary in conductance arrays when they are reused across many tokens or batches. Stream activations through DACs. Read partial sums through ADCs. Accumulate digitally. Apply normalization and attention control digitally. Send the next projection back through analog only when the data movement and conversion costs are justified. This turns the accelerator into a scheduling problem, not just a circuit problem.

The mathematical form is error propagation through layers:

```text
h_next = f((W + delta_W)(h + delta_h) + delta_adc + delta_dac)
```

Residual connections may carry clean information around a noisy analog block. Normalization may shrink some scale errors. But attention can amplify small differences if they change which tokens receive weight. The model-level question is whether the next-token distribution changes enough to matter.

The measurement is not a single matrix multiply benchmark. Measure per-layer error, end-to-end output drift, token distribution change, latency per token, energy per token, and memory traffic. Compare three systems: digital quantized baseline, analog array without correction, and analog array with calibration plus digital residual correction. If the corrected analog path only wins for large batches, that must be stated.

The failure mode is drawing an analog accelerator as if every transformer block were a dot product. Attention is not just a dot product. The KV cache is not just storage. Sampling is not linear algebra. Hybrid hardware works only when the partition respects the physical strengths of each side: analog for cheap approximate weighted sums, digital for control and evidence.
