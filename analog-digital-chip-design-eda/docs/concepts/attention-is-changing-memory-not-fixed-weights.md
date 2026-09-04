# Attention Is Changing Memory, Not Fixed Weights

The object is the token memory used by attention. This is different from the trained weights in an MLP or projection layer. A trained weight matrix is fixed during inference. The KV cache is created by the request itself. Every new token writes new keys and values. Every later token reads some of them back.

That difference changes the hardware problem. A conductance array is a natural place for a fixed matrix because the device can hold a weight while many inputs reuse it. Attention state is not like that. The stored object changes with sequence position, context window, batch, eviction policy, and serving schedule.

The constraint is that attention has two jobs at once. It must compare the new query against previous keys, and it must use the resulting weights to mix previous values:

```text
scores = Q K^T
weights = softmax(scores + mask)
output = weights V
```

The first and third lines contain dot products. The second line is control over range and probability. If the scores are wrong, softmax may place weight on the wrong token. If the values are read with too much error, the output vector becomes a damaged memory recall. If the mask is wrong, the model can attend to tokens it should not see.

## Why This Is Not A Static Crossbar

A static crossbar answers this kind of question:

```text
given fixed W and changing x, compute W x many times
```

Attention during decode asks a different question:

```text
given new q and a growing memory K,V, compare q with stored K and mix stored V
```

The keys and values are generated activations. They are not long-lived trained parameters. In ordinary serving, the cache grows as the request grows. In windowed attention, older entries are dropped or compressed. In paged attention, blocks are moved through a memory manager. In all cases, the controlled object is changing memory.

This does not mean analog attention is impossible. It means the analog target has changed. The useful analog object may be a short-lived memory cell, a gain-cell array, a charge-domain store, or an analog dot-product unit near the cache. The test is no longer only conductance programming accuracy. It includes write cost, retention, read disturbance, refresh, address selection, and softmax sensitivity.

## The Mathematical Boundary

For fixed projections, reuse is roughly:

```text
weight_reuse ~= tokens_that_use_the_same_matrix
```

For attention cache state, reuse is different:

```text
cache_entry_reuse ~= future_tokens_that_read_this key/value
```

A token near the beginning of a long context may be read many times. A token near the end may be read only a few times. A sliding-window design limits reuse deliberately:

```text
attention_reads_per_decode_step ~= window_tokens * layers * heads
```

This can make hardware easier because the active memory is smaller. It can also change the model behavior because old tokens are no longer available unless compressed or summarized.

The KV storage size is:

```text
KV bytes = 2 * layers * tokens * hidden * bytes_per_value
```

The score work for one decode step is roughly:

```text
score_macs = layers * heads * window_tokens * head_dim
```

Since `heads * head_dim = hidden`, the score work is:

```text
score_macs = layers * window_tokens * hidden
```

The value-mixing work has the same order. The memory movement can still dominate because every step touches many cache entries.

## Concrete Design Move

The concrete design move is to separate three attention placements:

```text
digital cache + analog projections
analog-near-cache score/value dot products
analog cache state with digital softmax and control
```

The first design keeps attention memory digital. It uses analog only for Q, K, V, output, and MLP projections. This is the safest first hybrid machine.

The second design keeps the cache logically digital but places dot-product hardware near it. This attacks memory movement without requiring long analog retention.

The third design stores some attention state in analog form. This is the hardest version. It must prove that write noise, retention loss, read disturbance, and refresh do not move attention enough to damage the next-token distribution.

## Measurement

The measurement is not only attention throughput. It must include:

- bytes read from KV cache per generated token
- score and value dot products per generated token
- cache write cost per token
- retention time for analog state
- read disturbance after repeated accesses
- softmax output change under score error
- final logit change after attention error

The most important check is whether the same hardware result holds for short prompts, long prompts, small batches, large batches, full attention, and sliding-window attention. A design that works only with a small context window should say so directly.

## Failure Mode

The failure mode is to call attention a matrix multiply and stop there. Attention contains matrix multiplies, but its hard object is generated memory under control. The model is not only multiplying by `K` and `V`; it is deciding which earlier token state should influence the next state.

The first-principles claim is that analog attention must be judged as a memory system before it is judged as a multiply engine. Fixed projections ask whether analog can preserve a trained matrix operation. Attention asks whether analog can preserve changing token memory, comparison, selection, and value recall. Those are related problems, but they are not the same problem.
