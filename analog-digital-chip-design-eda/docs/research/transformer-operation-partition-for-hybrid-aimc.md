# Transformer Operation Partition For Hybrid AIMC

This page asks one narrow question: for a transformer running on a hybrid analog and digital chip, which operation should run where?

The answer cannot be "analog is good for matrix multiply." That is too coarse. A transformer block is a sequence of different objects. Some objects are fixed trained weights. Some are changing token memory. Some are scale decisions. Some are comparisons. Some are control choices. The hardware should follow the object.

## The Partition Rule

Use analog only when five facts are true.

1. The operation is mostly multiplication by a resident trained matrix.
2. The same weights are reused enough times to pay for DAC, ADC, scheduling, and calibration.
3. The output can tolerate bounded numeric error after correction.
4. The digital side can measure the error that matters to the next model state.
5. A fallback path exists when calibration age, tile health, cache pressure, or state error becomes too large.

Use digital when the operation is an address, a branch, a comparison, a normalization, a probability decision, or a changing memory movement. These operations are not weak because they are small. They are weak analog targets because the object is not a stored-weight current sum.

## Operation Map

### Token embedding and input lookup

The object is an index selecting a learned vector.

The mathematical form is:

```text
h_0 = E[token_id]
```

This should stay digital. The hard part is not multiplication. The hard part is exact addressing and moving the selected vector into the next block. If the wrong row is selected, the model starts from the wrong symbol. Analog current summation does not help with the index decision.

The evidence is address correctness, SRAM bandwidth, cache behavior, and input-vector delivery time.

The failure boundary is simple: if token identity can be corrupted by the compute path, the analog path is being used for the wrong object.

### Q, K, and V projections

The object is a fixed trained linear map applied to hidden states.

The mathematical form is:

```text
Q = H W_q
K = H W_k
V = H W_v
```

These are analog candidates when the weights are resident in conductance tiles and the batch or prompt length gives enough reuse. The crossbar is useful because each column current is a weighted sum. The digital system still owns tiling, partial-sum accumulation, scaling, correction, and output layout.

The evidence is not only projection RMS error. Measure hidden-state error after attention, next-layer error, energy per token, p95 latency, calibration work, and comparison with an INT8 or FP8 digital baseline.

The failure boundary is score sensitivity. A small projection error can matter if it changes attention score order. Q and K need stricter evidence than a generic dense layer because they feed a comparison.

### Attention score computation

The object is a comparison between the current query and stored token memories.

The mathematical form is:

```text
S = Q K^T / sqrt(d)
```

This is hybrid at best. It is a dot product, but one side is changing token memory, not a fixed trained matrix. K comes from the current request's cache. That makes attention scores a memory-read and comparison problem as much as a multiply problem.

Analog may help only if the system has an efficient way to hold or stream the active K cache with bounded error. Otherwise the cost of moving changing memory through analog boundaries can dominate.

The evidence is score-margin preservation. For each query, measure whether the top competing keys keep the same order after hardware error. Average score error is too weak because softmax cares most about close competitions.

The failure boundary is selection error: if hardware noise changes which memories get large attention weight, the model may retrieve the wrong context even when the score RMS looks acceptable.

### Masking and causal control

The object is a legality rule over positions.

The mathematical form is:

```text
S_masked[i, j] = -infinity when j > i
```

This belongs in digital control. A mask is not a numeric approximation problem. It is a rule that says which positions are allowed to affect the current token.

The evidence is exact causal behavior across prefill, decode, batching, padding, and packed sequences.

The failure boundary is any path where a future token or padded token can influence the state. No analog energy saving compensates for breaking the sequence rule.

### Softmax

The object is turning scores into a normalized selection distribution.

The mathematical form is:

```text
a_i = exp(s_i) / sum_j exp(s_j)
```

This should normally stay digital. Softmax uses exponentials, range control, maximum subtraction, masking, and normalization. Its output is sensitive when two scores are close and less sensitive when one score dominates.

The evidence is not "softmax implemented." The evidence is probability movement: how much attention mass shifts between memories under realistic score error.

The failure boundary is a hidden one. The output can look numerically close while attention mass moves from the right token to a near competitor. That mistake then enters value mixing.

### Value mixing

The object is weighted summation of token memories.

The mathematical form is:

```text
Z = A V
```

This is hybrid. It is a multiply-add, but both A and V are request-dependent. The values live in the cache, and the attention weights come from the current scores. Analog is less natural here than for fixed trained weights.

If value mixing is analog, the chip must explain where A and V live, how they are converted, how often they are reused, and how probability error combines with value error. If those costs are high, digital value mixing is cleaner.

The evidence is context-vector error, not only multiply error. Measure the vector sent to the attention output projection.

The failure boundary is cache movement. If the analog path saves arithmetic but spends more energy moving changing values through converters and buffers, the partition is wrong.

### Attention output projection

The object is a fixed trained linear map after value mixing.

The mathematical form is:

```text
O = Z W_o
```

This is a strong analog candidate. The weight matrix is fixed, dense, and reused. Unlike attention scores, the matrix is trained weight storage, not changing token memory.

The evidence is downstream hidden-state error after residual addition and normalization. The projection can tolerate more bounded error if the residual path and later normalization keep the state stable.

The failure boundary is persistent channel bias. If one output channel is always high or low, the residual stream can carry that bias across layers.

### MLP up projection

The object is a large fixed expansion matrix.

The mathematical form is:

```text
U = H W_up
```

This is one of the best analog candidates. The matrix is large, dense, and reused across tokens. It is often more suitable than attention because the weights are fixed and the operation does not directly choose between memories.

The evidence is activation error after the nonlinearity, not only projection error before it. If the activation function clips, gates, or amplifies errors, the relevant measurement is after that step.

The failure boundary is converter dominance. If high DAC and ADC precision is needed for every use, the array's cheap multiplication no longer controls the cost.

### MLP activation and gating

The object is a nonlinear transformation of the expanded features.

The mathematical form is:

```text
G = act(U)              or              G = act(U_1) * U_2
```

This should usually stay digital or near-digital. The operation is not a resident weight matrix. It is a function applied to changing activations. Gated activations also multiply two changing values, which is different from multiplying an activation by a fixed stored weight.

The evidence is post-activation error and saturation behavior. A small pre-activation error can be harmless far from a threshold and harmful near a sharp bend.

The failure boundary is nonlinear amplification. If the activation turns bounded analog noise into feature selection changes, the analog partition must move back.

### MLP down projection

The object is a fixed trained compression matrix.

The mathematical form is:

```text
M = G W_down
```

This is a strong analog candidate. Like the up projection, it is fixed, dense, and repeated. It also returns the expanded representation to the model width, so its output directly enters the residual stream.

The evidence is residual-state error after:

```text
H_next = H + M
```

The failure boundary is layer-to-layer drift. A tolerable one-layer error can become harmful if the same columns or tiles create stable bias across depth.

### Residual addition

The object is preserving the old state while adding a computed update.

The mathematical form is:

```text
H_next = H + F(H)
```

This belongs in digital accumulation. It is simple arithmetic, but it is a control point for model state. Keeping it digital gives the system a clean place to apply correction, compare error, clamp formats, and decide fallback.

The evidence is state preservation. Measure whether the residual stream remains stable across many layers when analog projections have gain, offset, quantization, and drift.

The failure boundary is losing the reference state. If both the update and the preserved state pass through uncontrolled analog boundaries, the design loses its clean comparison point.

### Normalization

The object is controlling scale before or after a block.

The mathematical form is:

```text
norm(h) = gamma * (h - mean(h)) / sqrt(var(h) + epsilon) + beta
```

This should stay digital. Normalization is a scale measurement and division problem. It uses statistics of the current activation, not a fixed trained matrix alone.

The evidence is stable variance, overflow avoidance, and distribution match to the digital baseline.

The failure boundary is scale drift. If normalization is wrong, every later projection receives activations in the wrong range, and the DAC boundary becomes harder to trust.

### KV-cache write

The object is storing newly produced K and V vectors at the correct token position.

The mathematical form is:

```text
cache_K[t] = K_t
cache_V[t] = V_t
```

This is digital memory work. The hard part is address, lifetime, layout, bandwidth, and eviction. It is not a stored trained matrix.

The evidence is cache correctness under long context, batching, paging, and request interleaving.

The failure boundary is wrong memory. If the cache returns the wrong token state, the attention mechanism is comparing against the wrong past.

### KV-cache read

The object is retrieving active token memory for attention.

The mathematical form is:

```text
K_active, V_active = cache[request_id, active_positions]
```

This should stay digital unless a specific memory-compute design proves otherwise. Reading many changing vectors can dominate decode. Analog arrays do not solve this by themselves because the cache is not fixed weight storage.

The evidence is memory traffic per generated token, cache hit behavior, bandwidth pressure, and end-to-end decode latency.

The failure boundary is pretending decode is only dense projection. In long-context decode, memory movement can dominate even if analog projection is fast.

### Logit projection

The object is mapping the hidden state to vocabulary scores.

The mathematical form is:

```text
logits = H W_vocab
```

This can be analog in principle because the vocabulary matrix is fixed and dense. It is also risky because its output feeds token choice. Approximation error matters most near competing tokens.

The evidence is rank preservation among top candidates, not full-vector average error. Measure top-k overlap, margin changes, and next-token distribution movement.

The failure boundary is wrong token selection. If analog error changes the sampled or selected token too often, the design may save energy while changing the model's behavior.

### Sampling, top-k, and control decisions

The object is choosing a next token or a restricted candidate set.

The mathematical form is:

```text
token_next = sample(filter(logits))
```

This belongs in digital logic or digital software. It contains comparisons, random choices, policy rules, safety filters, and request control.

The evidence is exact policy behavior, reproducibility when required, latency, and correct handling of temperature, top-p, top-k, and constraints.

The failure boundary is control corruption. Once a token is chosen, it changes every later step.

### Low-rank adapters and fine-tuning layers

The object is a small learned update around a frozen base model.

The mathematical form is:

```text
y = W x + B A x
```

This is a good hybrid candidate. The base matrix may live in analog tiles while the low-rank update stays digital, or the adapter itself may be placed in a smaller calibrated analog region. The right answer depends on reuse, update frequency, and isolation.

The evidence is adapter-specific output change and whether the low-rank update can repair or worsen analog error.

The failure boundary is update churn. If adapters change often, programming conductance arrays may cost more than digital execution.

### Calibration probes

The object is measuring the chip's current behavior.

The mathematical form is:

```text
error = measured_output - expected_output
correction = fit(error)
```

This is a digital-controlled measurement loop around analog hardware. The array produces measurements, but the decision about what to probe, what to fit, and when to trust the fit is digital.

The evidence is error reduction on held-out activation patterns, calibration age, per-tile health, and model-state improvement.

The failure boundary is stale correction. A calibration table is not truth. It is a timed estimate of a moving physical system.

### Tile health and serving policy

The object is deciding whether a request is allowed to use analog hardware.

The mathematical form is a guarded decision:

```text
analog_allowed =
  resident_weights
  and healthy_tiles
  and calibration_fresh
  and estimated_state_error <= budget
  and cache_pressure <= limit
```

This belongs in digital control logic. The analog array cannot decide whether its own approximation is acceptable for the current request. The control plane must expose a path and a reason.

The evidence is the request-level record: phase, batch, context length, cache pressure, tile health, calibration age, estimated state error, selected path, fallback reason, latency, energy, and output change.

The failure boundary is silent degradation. If the chip cannot explain why it used analog or why it fell back to digital, the analog result is not operationally trustworthy.

## What The Full Partition Says

The analog core is not a transformer engine. It is a resident-weight projection engine. That is still valuable because transformers contain many large fixed projections. But the rest of the chip matters just as much: SRAM, cache management, DACs, ADCs, accumulation, correction, calibration, fallback, and control.

The strongest first build is therefore:

```text
analog: Q/K/V projections, attention output projection, MLP up/down, maybe vocab projection
digital: embedding lookup, masks, softmax, normalization, residual control, KV cache, sampling
hybrid: attention score experiments, value mixing experiments, adapters, correction
```

This is the project direction. Build analog where the object is fixed weighted summation. Build digital where the object is state, address, rule, comparison, or proof. Measure the model state after the boundary, not only the circuit value inside the boundary.
