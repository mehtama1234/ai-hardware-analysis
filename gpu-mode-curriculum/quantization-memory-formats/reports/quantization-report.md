# GPUMODE Quantization And Memory Formats

Generated: `2026-08-31T01:53:18.528091+00:00`
Status: `quantization-ready`

## Format Sweep

| format | bits | compression | max abs error | cosine | dequant tax | speedup proxy | serving fit | status |
|---|---:|---:|---:|---:|---:|---:|---|---|
| fp32-reference | 32 | 1.0 | 0.0 | 0.99999988 | 0.1566 | 0.8646 | debug-only | passed |
| bf16-activation | 16 | 2.0 | 0.122993 | 0.99999881 | 1.4695 | 0.8099 | good | passed |
| fp8-e4m3-sim | 8 | 4.0 | 1.680189 | 0.99968785 | 7.4277 | 0.8 | debug-only | needs-calibration |
| int8-per-tensor | 8 | 4.0 | 0.92488 | 0.99990535 | 0.6308 | 2.4528 | best | passed |
| int8-per-channel | 8 | 3.9385 | 0.752085 | 0.99998999 | 0.6981 | 2.3194 | good | passed |
| int4-symmetric | 4 | 7.7576 | 10.188474 | 0.9967792 | 0.9375 | 4.004 | debug-only | needs-calibration |
| nf4-weight-only | 4 | 7.7576 | 8.692532 | 0.99550164 | 29.9441 | 1.5515 | debug-only | needs-calibration |

## Recommendations

- `debug-correctness`: `bf16-activation` - Preserves high cosine similarity while cutting payload bytes in half for activation-oriented checks.
- `interactive-serving`: `int8-per-channel` - Balances 4x weight compression with low output drift and avoids the larger dequantization tax of 4-bit formats.
- `memory-constrained-serving`: `nf4-weight-only` - Maximizes memory compression for serving when a fused dequantization kernel can hide the codebook lookup cost.
- `tensor-core-kernel-promotion`: `fp8-e4m3-sim` - Models FP8-style range and mantissa pressure before promoting to hardware-specific tensor-core kernels.

## GPU Promotion Commands

- `python3 scripts/run_gpu_host_preflight.py`
- `nvidia-smi --query-gpu=name,memory.total,power.draw --format=csv`
- `python3 scripts/run_gpu_promotion_suite.py --run-id quantization-memory --execute`
- `vllm serve <model> --quantization <awq|gptq|fp8> --max-model-len <tokens>`
- `ncu --set full -o quantization-memory python3 <quantized_kernel_probe.py>`
- `nsys profile -o quantization-serving python3 <serving_quant_probe.py>`
