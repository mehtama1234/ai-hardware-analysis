# Paper-to-code mapping

Reviewed [FlashAttention, paper revision 2](https://arxiv.org/html/2205.14135v2), section 3.1,
appendix B.2 and selected B.4 algorithm text. This is a scoped correspondence
audit, not full-paper reproduction.

| Paper mechanism | Local `recomputed.py` |
|---|---|
| Online softmax statistics and rescaling | `maximum`, `denominator`, `correction`, `numerator` |
| Recompute probabilities during backward | `exp(scores - lse)` |
| Row correction using output and output gradient | `delta = (out * grad_output).sum(-1)` |
| Softmax derivative and input-gradient accumulation | `ds`, then tiled `dq`, `dk`, `dv` updates |
| On-chip tiled execution and dropout-state replay | Not implemented locally |

Our code stores log-sum-exp, uses query-major Python loops, and retains ordinary
PyTorch intermediates. It neither controls SRAM placement nor inherits the
paper's IO bound or speedups. Arbitrary masks remain caller-owned saved tensors;
only causal masks are generated per tile. Block size is user-selected, not
derived from SRAM capacity. Dropout and higher-order derivatives are unsupported.

Acceptance still needs a fused kernel, explicit resource/tile accounting, actual
device measurements and numerical tests against the same reference. Logical
saved-tensor bytes are not allocator peaks or measured HBM traffic.
