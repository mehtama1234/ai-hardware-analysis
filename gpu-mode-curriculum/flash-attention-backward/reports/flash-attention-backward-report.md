# GPUMODE FlashAttention backward

Generated: `2026-08-31T01:53:09.049488+00:00`
Status: `flash-attention-backward-ready`

| scenario | status | speedup | HBM reduction | recompute overhead | occupancy | max error | gradients |
|---|---|---:|---:|---:|---:|---:|---|
| training-prefill-bf16 | passed | 1.5806 | 0.860532 | 0.18 | 1.0 | 0.0015 | dQ, dK, dV, dSoftmax |
| long-context-checkpointed | passed | 1.5593 | 0.926317 | 0.24 | 0.9458 | 0.0028 | dQ, dK, dV, dSoftmax |
| dropout-causal-training | passed | 1.4894 | 0.860822 | 0.28 | 0.8533 | 0.0035 | dQ, dK, dV, dSoftmax |
| gqa-decode-finetune | passed | 1.5604 | 0.658854 | 0.2 | 1.0 | 0.0022 | dQ, dK, dV, dSoftmax |
| fp8-activation-review | passed | 1.4419 | 0.860532 | 0.34 | 0.75 | 0.009 | dQ, dK, dV, dSoftmax |
| noncausal-cross-attention | passed | 1.6585 | 0.881781 | 0.16 | 1.0 | 0.0018 | dQ, dK, dV, dSoftmax |

## GPU Host Promotion

- `python3 scripts/run_flash_attention_backward.py`
- `python3 scripts/verify_flash_attention_backward.py`
- `python3 scripts/run_attention_serving_stack.py`
- `ncu --set full -o flash-attention-backward python3 <flash_attention_backward_probe.py>`
- `nsys profile -o flash-attention-training-step python3 <flash_attention_training_step.py>`
- `python3 scripts/run_gpu_promotion_suite.py --run-id flash-attention-backward --execute`
