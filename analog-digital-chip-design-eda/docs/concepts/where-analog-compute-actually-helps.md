# Where Analog Compute Actually Helps

The object is a model operation placed on a physical machine. The question is not whether a foundation model is analog or digital. A foundation model is a sequence of different operations. Some are repeated weighted sums. Some are memory reads. Some are comparisons. Some are range controls. Some are discrete choices. The hardware should follow that difference.

Analog in-memory compute helps most when the operation is a large fixed matrix used many times. The weight is already stored as conductance. The input arrives as a voltage. The column current gives the sum. If many activations reuse the same conductance array, the machine saves repeated weight movement and repeated digital multiply work.

The constraint is that this advantage exists only inside a narrow physical bargain. The array gives cheap local summation, but it asks the rest of the chip to pay for DACs, ADCs, partial sums, calibration, error correction, and scheduling. If the operation does not reuse weights enough, or if the output needs high precision at every step, the boundary cost can erase the array advantage.

## The Useful Split

The useful split is not "analog versus digital." It is:

```text
stable weight, dense sum, bounded error -> analog candidate
changing state, exact control, indexed memory, fragile range -> digital candidate
```

MLP projections are the strongest analog candidate. Their matrices are large. Their weights are fixed during inference. They are used in every layer and every token. The operation is mostly a dense linear map followed by a nonlinearity and another dense map. If the model tolerates the analog error, this is where a crossbar can do real work.

Q, K, and V projections are also plausible. They are dense maps from hidden state to attention state. During prefill, many tokens pass through the same projection weights, so reuse is high. During decode, the projection work still exists, but only for the new token. That makes converter overhead and scheduling more visible.

The attention score step is mixed. The score is a dot product between a query and many keys. It has multiplication and summation, but the keys are not a fixed trained weight matrix. They are generated state. A static conductance array is less natural unless the system has a fast way to write and read that state, or unless it uses analog memory for the cache itself.

Softmax is a poor analog target in the first version. It controls range, exponentials, normalization, masking, and probability shape. Small errors can change which tokens are attended to. It is better treated as digital control until the rest of the path is measured well enough.

Normalization is also a poor first target. It protects scale. It decides whether the next layer receives values in the range the model expects. If analog errors shift the mean or variance, normalization may amplify the damage instead of hiding it. Keep it digital until there is a measured reason to move it.

The KV cache is a memory object, not a weight matrix. It grows with generated tokens:

```text
KV bytes ~= 2 * layers * tokens * hidden * bytes_per_value
```

That object changes during inference. It must be written, indexed, read, and sometimes paged across memory levels. Analog multiplication does not automatically solve that movement.

Token sampling and control flow should stay digital. They choose the next discrete state of the computation. If this step is wrong, the future request follows a different path. There is little value in making it analog when it is not the main energy object and when correctness is discrete.

## The Mathematical Test

The mathematical form is not a single layer equation. It is a cost and error test for each operation:

```text
benefit = saved_weight_movement + saved_multiply_energy
cost = DAC + ADC + accumulation + correction + extra_memory_movement
accept if benefit > cost and model_error <= tolerance
```

This test has to be run separately for prefill and decode. Prefill gives many prompt tokens at once:

```text
reuse_prefill ~= prompt_tokens * batch
```

Decode gives one new token per step:

```text
reuse_decode ~= batch
```

If batch is small, decode gives the analog tile less useful work per boundary crossing. The same matrix can be a good analog target in prefill and a weaker target in decode.

## Concrete Design Move

The concrete design move is to build a partition table before claiming acceleration:

```text
operation          likely home      reason
MLP up/down        analog + digital dense fixed weights, high reuse
QKV projection     analog + digital dense fixed weights, phase-dependent reuse
output projection  analog + digital dense fixed weights
attention scores   digital first    token state changes, range matters
softmax            digital          normalization and masking control
layer norm         digital          scale control
KV cache           digital memory   changing indexed state
sampling           digital          discrete next-token decision
calibration        digital          measured correction
residual repair    digital          sparse correction of analog damage
```

This table is not a slogan. It is a design constraint. Each analog candidate must state its input precision, output precision, tile size, accumulation path, calibration method, and tolerated layer error. Each digital operation must state why keeping it digital protects the model state.

## Measurement

The measurement is phase-separated tokens per joule and phase-separated latency:

```text
prefill_latency(prompt_tokens, batch)
decode_latency(generated_tokens, batch)
prefill_energy(prompt_tokens, batch)
decode_energy(generated_tokens, batch)
```

Report the numbers with ADC bits, DAC bits, tile size, KV-cache bytes, row-tile count, column-tile count, and partial-sum count. A single averaged throughput number hides the central issue.

The model-level measurement is change in output quality under the same boundary. Circuit error alone is not enough. If a row loses voltage but calibration absorbs it, the design may still work. If a tiny ADC error changes logits in a sensitive layer, the design may fail even when circuit error looks small.

## Failure Mode

The failure mode is to move everything into the analog story because the crossbar computes a dot product. That loses the shape of the transformer. A transformer is not one dot product repeated in isolation. It is a controlled state machine with dense maps, changing memory, scale protection, masking, probability normalization, and discrete token choices.

The first-principles claim is that analog compute helps only where the physical operation matches the model operation. Large fixed projections match conductance arrays. Changing memory and exact control match digital logic and digital memory. A strong hybrid accelerator is not less digital. It is more honest about which part of the model is actually a dense stored-weight sum.
