# Tiny Transformer Integration Lab

This lab connects the lower-level GPU curriculum artifacts to a model-shaped
program. It runs a tiny causal transformer block with:

- layer normalization
- QKV projection
- causal attention
- output projection
- fused bias + GELU + residual custom op
- autotune-record lookups for matmul, normalization, and custom-op families

The local implementation runs on CPU with PyTorch so correctness and timing are
available in CI. CUDA/Triton/custom-extension promotion should keep the report
schema and replace individual operators with accelerator-backed implementations.

## Run

```bash
python3 scripts/run_model_integration.py
python3 scripts/verify_model_integration.py
```
