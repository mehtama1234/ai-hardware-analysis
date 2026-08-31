# Compiler Runtime Inspection

Generated: `2026-08-31T01:52:59.236107+00:00`
Status: `inspection-ready`
Sources: `13`
Groups: `cuda, custom-op, hip, triton`

## Feature Counts

| feature | sources |
|---|---:|
| global_kernel | 10 |
| shared_memory | 4 |
| barrier | 4 |
| vectorized_load | 4 |
| tensor_core_hint | 5 |
| launch_indexing | 10 |
| bounds_mask | 10 |
| atomic | 0 |

## Source Rows

| group | path | lines | risks | promotion commands |
|---|---|---:|---|---|
| cuda | `kernel-benchmarks/kernels/cuda/matmul_mlp.cu` | 25 | none | nvcc -O3 --ptx kernel-benchmarks/kernels/cuda/memory.cu -o /tmp/gpumode-memory.ptx<br>ncu --set full python3 scripts/run_kernel_benchmarks.py |
| cuda | `kernel-benchmarks/kernels/cuda/memory.cu` | 25 | none | nvcc -O3 --ptx kernel-benchmarks/kernels/cuda/memory.cu -o /tmp/gpumode-memory.ptx<br>ncu --set full python3 scripts/run_kernel_benchmarks.py |
| cuda | `kernel-benchmarks/kernels/cuda/reduction.cu` | 27 | none | nvcc -O3 --ptx kernel-benchmarks/kernels/cuda/memory.cu -o /tmp/gpumode-memory.ptx<br>ncu --set full python3 scripts/run_kernel_benchmarks.py |
| cuda | `kernel-benchmarks/kernels/cuda/softmax_layernorm.cu` | 47 | none | nvcc -O3 --ptx kernel-benchmarks/kernels/cuda/memory.cu -o /tmp/gpumode-memory.ptx<br>ncu --set full python3 scripts/run_kernel_benchmarks.py |
| triton | `kernel-benchmarks/kernels/triton/matmul_mlp.py` | 17 | tensor_core_without_shape_contract | TRITON_KERNEL_DUMP=1 python3 scripts/run_kernel_benchmarks.py<br>python3 scripts/build_autotune_db.py |
| triton | `kernel-benchmarks/kernels/triton/memory.py` | 11 | none | TRITON_KERNEL_DUMP=1 python3 scripts/run_kernel_benchmarks.py<br>python3 scripts/build_autotune_db.py |
| triton | `kernel-benchmarks/kernels/triton/reduction.py` | 11 | none | TRITON_KERNEL_DUMP=1 python3 scripts/run_kernel_benchmarks.py<br>python3 scripts/build_autotune_db.py |
| triton | `kernel-benchmarks/kernels/triton/softmax_layernorm.py` | 26 | none | TRITON_KERNEL_DUMP=1 python3 scripts/run_kernel_benchmarks.py<br>python3 scripts/build_autotune_db.py |
| custom-op | `custom-ops/csrc/fused_bias_gelu_residual.cpp` | 15 | tensor_core_without_shape_contract | python3 scripts/run_custom_ops.py<br>nsys profile python3 scripts/run_model_integration.py |
| custom-op | `custom-ops/csrc/fused_bias_gelu_residual_kernel.cu` | 48 | none | python3 scripts/run_custom_ops.py<br>nsys profile python3 scripts/run_model_integration.py |
| hip | `programming-projects/rocm-hip-port/kernel.hip.cpp` | 12 | none | hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port<br>rocprof /tmp/rocm-hip-port |
| hip | `programming-projects/rocm-hip-port/measure.py` | 65 | none | hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port<br>rocprof /tmp/rocm-hip-port |
| hip | `programming-projects/rocm-hip-port/starter.py` | 46 | none | hipcc programming-projects/rocm-hip-port/kernel.hip.cpp -o /tmp/rocm-hip-port<br>rocprof /tmp/rocm-hip-port |

## GPU Host Promotion

Static inspection identifies source-level compiler/runtime risks; final acceptance requires PTX/LLVM/profiler evidence from a GPU host.
