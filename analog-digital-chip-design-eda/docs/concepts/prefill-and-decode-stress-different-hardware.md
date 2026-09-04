# Prefill And Decode Stress Different Hardware

The object is transformer inference over time. A foundation model does not do the same hardware work for the whole request. It first reads the prompt. Then it generates new tokens one at a time. These two phases use the same learned weights, but they stress the machine differently.

Prefill processes many prompt tokens together. The model applies the same projection weights to many activations. This is friendly to hardware that keeps weights stationary, because the expensive stored matrix is reused across a large block of work. An analog in-memory tile is most plausible here: the conductances can hold projection weights while many input vectors are driven through the rows.

Decode processes one new token at a time. The batch of useful work can be much smaller. The model must read the KV cache, update it, compute attention against prior tokens, and choose the next token. Dense projections still exist, but memory movement and control become harder to hide. If the analog tile waits for tiny batches, ADC/DAC conversion and scheduling overhead can become a larger share of the step.

The constraint is reuse. Analog in-memory compute pays fixed boundary costs: DACs must drive rows, ADCs must read columns, partial sums must be accumulated, and outputs must be corrected. Those costs are easier to amortize when many activations use the same resident weights. They are harder to amortize when the machine handles a single new token and must also serve a growing cache.

The mathematical shape is not only `y = Wx`. It is work per boundary crossing:

```text
useful projection work / conversion and scheduling cost
```

During prefill, useful projection work is large because many tokens can share the same loaded weights. During decode, useful projection work per step is smaller while the KV cache grows with generated length:

```text
KV bytes ~= 2 * layers * tokens * hidden * bytes_per_value
```

That memory object is not a fixed weight matrix. It changes as generation proceeds.

The concrete design move is to evaluate analog acceleration separately for prefill and decode. For prefill, ask whether MLP and Q/K/V projections can run through analog tiles with enough reuse to pay for conversion. For decode, ask whether the system can keep the tile busy, read the KV cache efficiently, and avoid spending more energy on boundary movement than it saves on multiplication.

The measurement is tokens per joule and latency per token separated by phase. A useful result should not report one average number without saying the prompt length, generated length, batch size, sequence length, tile size, ADC/DAC precision, and cache placement. Those choices decide whether analog compute is operating in a high-reuse regime or a cache-limited regime.

The failure mode is to benchmark only a dense matrix multiply and call it LLM inference. A projection is a major part of a transformer, but inference includes phase behavior. If a design accelerates prefill but not decode, that can still be valuable. It just must be stated. If a design assumes large batches, short context, or static attention memory, it may not solve the long-context serving problem people imagine.

The first-principles claim is that analog foundation-model hardware should be judged by regime. Dense analog projections are strongest when weights are reused across many tokens. They are weakest when generation becomes a memory-and-control loop around the KV cache. The same chip can be good for one phase and weak for the other.
