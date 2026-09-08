# GPUMODE CUTLASS CuTe Tensor Core GEMM

Generated: `2026-09-07T05:56:47.871329+00:00`
Status: `tensor-core-gemm-ready`

| scenario | status | dtype | CTA | MMA | smem | regs | intensity | epilogue |
|---|---|---|---|---|---:|---:|---:|---|
| bf16-mlp-up-projection | passed | bf16 | 128x128x64 | 16x8x16 | 98304 | 264 | 1214.6759 | bias-gelu |
| fp16-attention-qkv | passed | fp16 | 128x128x64 | 16x8x16 | 98304 | 260 | 1068.5217 | bias |
| int8-weight-only-decode | passed | int8 | 64x128x64 | 16x8x32 | 49152 | 168 | 390.0952 | dequant-bias |
| fp8-training-gemm | passed | fp8 | 128x128x128 | 16x8x32 | 131072 | 264 | 1365.3333 | amax-scale |
| small-batch-lora | passed | bf16 | 64x64x64 | 16x8x16 | 32768 | 100 | 50.5679 | residual-add |

## GPU Host Promotion

- `python3 scripts/run_gpu_host_preflight.py`
- `python3 scripts/run_tensor_core_gemm.py`
- `python3 scripts/verify_tensor_core_gemm.py`
- `ncu --set full -o tensor-core-gemm python3 <cutlass_gemm_probe.py>`
- `cuobjdump --dump-sass <cutlass_gemm_binary> | rg -i 'mma|wgmma'`
- `python3 scripts/run_gpu_promotion_suite.py --run-id tensor-core-gemm --execute`
