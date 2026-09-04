# Transformer Block Error Is State Drift

The object is the hidden state after a transformer block. A hardware error is not important only because it changes one multiply. It is important because the changed value becomes the input to later operations. The model carries that state forward.

A simplified transformer block is:

```text
x1 = x + attention(norm(x))
x2 = x1 + mlp(norm(x1))
```

Analog hardware may approximate some dense maps inside attention and MLP. The digital side may keep normalization, softmax, residual addition, sampling, and control. The constraint is that the final state `x2` must stay close enough to the digital reference for the next block to use it.

This changes the measurement. It is not enough to say that one analog matrix multiply has a small error. The block combines several possible errors:

- Q, K, V projection error
- attention score error
- softmax selection movement
- value mixture error
- output projection error
- MLP projection error
- residual-path interaction

The model sees the combined state movement.

## Why Residual Paths Help And Do Not Solve It

Residual addition carries the previous state around a noisy sublayer:

```text
x_next = x + noisy_update
```

This helps because the update is only part of the next state. If the update is damaged but small, the residual path can limit the relative state movement. But residuals do not make the error disappear. If every block adds a biased update, the state can drift layer by layer.

The important object is therefore drift:

```text
state_error_l = x_l_noisy - x_l_clean
```

A random error may partly cancel. A stable bias may accumulate. A selection error in attention may move the state in a semantically different direction. Those are different failure modes.

## The Mathematical Boundary

A noisy block can be written as:

```text
attn_noisy = attention(x, delta_qkv, delta_score, delta_value)
mlp_noisy = mlp(x + attn_noisy, delta_up, delta_down)
x_noisy_next = x + attn_noisy + mlp_noisy
```

The reference block is:

```text
x_clean_next = x + attn_clean + mlp_clean
```

The measured object is:

```text
relative_state_error = rms(x_noisy_next - x_clean_next) / rms(x_clean_next)
```

This number is not a full language-model benchmark. It is a stronger lab object than isolated current error because it measures the state that would enter the next block.

## Concrete Design Move

The concrete design move is to test combined errors in the order the model experiences them:

```text
analog QKV -> noisy scores -> digital softmax -> value mix -> analog output projection -> analog MLP -> residual state
```

Then compare variants:

- projection noise only
- score noise only
- projection plus score noise
- higher ADC/DAC precision
- residual correction on the largest output channels
- full-context attention versus windowed attention

This reveals whether the danger is converter precision, attention selection, MLP amplification, or accumulated bias.

## Measurement

The measurement is relative state error after the block, plus the intermediate quantities that explain it:

- attention output error
- top-attended-token flip rate
- MLP output error
- final block state error
- whether the error is random or biased

If attention score noise flips the selected memory but the value vectors are similar, the state may remain close. If the value vectors differ strongly, a small score error can produce a large state movement. If MLP projection error is stable and biased, residual addition can carry that bias into later layers.

## Failure Mode

The failure mode is to validate each part in isolation and never measure the state after the block. A crossbar can have acceptable current error, an ADC can have acceptable code error, and an attention score can have acceptable RMS error, while their combination still moves the hidden state too far.

The first-principles claim is that hybrid analog/digital foundation-model hardware must be judged at the state boundary. The chip is not trying to preserve a single current. It is trying to preserve the sequence of hidden states that make the model behave like the intended model.
