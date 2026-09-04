# Softmax Turns Score Error Into Selection Error

The object is the attention choice made from a set of scores. A score is not the final model state. It is a number used to decide how much the model reads from each earlier token. When hardware noise changes a score, the next question is not only how large the score error is. The next question is whether the read choice changed.

Attention computes:

```text
scores = Q K^T / sqrt(head_dim)
weights = softmax(scores + mask)
output = weights V
```

The constraint is competition. Softmax compares scores against each other. If one score is much larger than the rest, small noise may not matter. If two scores are close, small noise can move probability from one token to another. The same absolute score error can be harmless in one layer and harmful in another layer.

This is why analog attention cannot be evaluated only by dot-product error. A current error becomes a score error. A score error becomes a probability change. A probability change becomes a different mixture of value vectors. That mixture becomes the next hidden state. The model sees the last object, not the current error by itself.

## The First-Principles Chain

The chain is:

```text
query/key dot product -> score error -> softmax weight movement -> value mixture error -> logit change
```

Each step can shrink or amplify the previous error.

Softmax is shift-invariant: adding the same constant to every score changes nothing. But changing one score relative to another changes the distribution. This means common-mode analog error may be less damaging than rank-changing error. A per-column offset, a local retention error, or a read disturbance that affects only some keys can change the ordering of close scores.

The mathematical form for a noisy score is:

```text
s_noisy_i = s_i + delta_i
p_i = exp(s_i) / sum_j exp(s_j)
p_noisy_i = exp(s_noisy_i) / sum_j exp(s_noisy_j)
```

The output error is:

```text
delta_output = sum_i p_noisy_i V_i - sum_i p_i V_i
```

The important value is not only `delta_i`. It is whether `p_noisy` moves mass onto a different value vector.

## Why Close Scores Matter

Suppose two prior tokens have scores `4.01` and `4.00`. A score error of `0.03` can change which one is largest. If their value vectors are similar, the output may barely move. If their value vectors point in different directions, the output can change strongly.

Now suppose the largest score is `8.00` and the next score is `3.00`. The same `0.03` error probably does not change the read choice. The softmax distribution is already concentrated.

So the sensitivity of attention depends on margin:

```text
margin = top_score - second_score
```

Small margin means the hardware must preserve ordering more carefully. Large margin gives more room for analog error.

## Concrete Design Move

The concrete design move is to measure attention error after softmax, not before it. For every analog attention proposal, report:

- score RMS error
- top-attended-token flip rate
- softmax probability movement
- output-vector relative error
- final logit movement if a downstream readout is available
- results binned by score margin

This makes the analog hardware claim test the model object that matters: the selected memory read.

## Measurement

The measurement should vary score noise, context length, value-vector diversity, and attention margin. A good result should show when noise is tolerable and when it changes token selection.

The minimum useful experiment is:

```text
make Q and K with two close top scores
compute clean attention
add score noise
compute noisy attention
measure probability movement, top-index flip, and output error
```

If the top index flips often at the noise level expected from the circuit, the attention path is fragile. If probability moves but the output vector barely changes, the value memory may be redundant enough to tolerate it. If the final logits move little, the layer may be robust even though attention weights changed.

## Failure Mode

The failure mode is to report an average score error and imply that attention is safe. Average error hides the hard cases. The hard cases are close competitions where the model is deciding between different memories.

The first-principles claim is that attention noise matters when it changes selection. Analog hardware must preserve enough score ordering and value recall for the next hidden state to stay useful. A dot product can be approximately correct while the memory choice is wrong.
