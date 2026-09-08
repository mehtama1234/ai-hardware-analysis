# Attention backward: analytical and executable evidence

See the [paper-to-code mapping](PAPER-MAPPING.md) for the scoped primary-source
audit and the boundary between mathematical correspondence and device execution.

There are three distinct implementations here:

- `flash_attention_backward/analyzer.py` uses scenario constants for latency,
  error, and resource estimates. Its generated reports are analytical, not
  measurements of an executed FlashAttention backward kernel.
- `flash_attention_backward/reference.py` executes materialized attention with
  an explicit first-order backward formula in PyTorch. It is a mathematical
  reference for future tiled kernels, not a FlashAttention implementation and
  not a claim of reduced memory use or accelerated performance.
- `flash_attention_backward/recomputed.py` executes blockwise online softmax and
  recomputes probability tiles in backward from saved log-sum-exp statistics.
  It is still a Python/PyTorch teaching implementation, not a fused CUDA kernel.

## Derivation

For S = Q K-transpose / sqrt(d), P = softmax(S), and O = P V, given upstream G:

1. dV = P-transpose G.
2. dP = G V-transpose.
3. dS = P * (dP - row_sum(dP * P)).
4. dQ = dS K / sqrt(d); dK = dS-transpose Q / sqrt(d).

Step 3 is the softmax vector-Jacobian product without constructing a full
Jacobian. Masked entries have zero probability and hence zero dS. This reference
saves the full probability matrix, so its memory remains quadratic in sequence
length. The recomputed implementation instead saves Q/K/V, output, row
log-sum-exp, and any caller-provided mask. It recovers each P tile with
exp(S-tile - row-log-sum-exp). The row reduction in step 3 equals row_sum(O*G),
so backward needs no full dP matrix. Causal masks are constructed per tile.
An explicit dense caller mask can itself remain quadratic; it is not free.

## Reproduce correctness checks

From the repository root, with PyTorch installed:

```bash
python3 -m unittest discover -s gpu-mode-curriculum/flash-attention-backward/tests -v
python3 gpu-mode-curriculum/flash-attention-backward/run_reference.py
```

Tests compare outputs and dQ/dK/dV to PyTorch SDPA in FP32/FP64, run FP64
finite-difference gradcheck, and exercise rectangular causal and boolean masks.
Mask True means allowed; rectangular causal alignment is upper-left, following
the [PyTorch SDPA contract](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html).
Fully masked rows are explicitly rejected. No dropout, GQA, additive masks,
broadcasted batch/head dimensions, FP16/BF16, or higher-order gradients yet.
The tests are CPU evidence unless explicitly extended and executed on a GPU.

The runner writes `reports/executable-reference-cpu.json` with provenance,
forward-plus-backward timing samples, and saved-tensor payloads captured by
autograd hooks. Saved logical bytes include retained inputs and outputs; they
are neither unique storage nor peak allocated memory. Timings use one CPU thread
and restore the previous thread setting. No GPU speedup follows from this report.

## Exercises and remaining acceptance

- Derive step 3 and verify that each dS row sums approximately to zero.
- Corrupt the scale factor in dQ and show that finite differences detect it.
- Explain why rectangular decode masking may need different alignment; do not
  silently substitute that convention for this reference's documented one.
- Vary recomputation block sizes, verify tail handling, and compare saved-tensor
  payloads with actual allocator peak measurements on an authorized GPU host.
- Add architecture-appropriate fused kernels, profile them, and compare against
  pinned library backends. Passing these reference tests alone cannot establish
  an optimized GPU implementation or speedup.
