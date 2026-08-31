# GPUMODE Comprehensive Labs

This layer is the deliberate code plan that sits above the 118 generated per-lesson scaffolds.

The labs are not one template stamped 118 times. Each lab is a hand-written runnable program that combines related GPUMODE lessons into a coherent implementation:

1. `memory_hierarchy.py`: coalescing, striding, bank conflicts, occupancy, roofline signals.
2. `tiled_attention.py`: tiled matrix multiplication, online softmax, attention memory accounting.
3. `compiler_autotune.py`: block-shape search, fusion decisions, Triton/CUDA-style schedule scoring.
4. `quantization_formats.py`: int8, int4, fp8-style, nvfp4-style quantization and error analysis.
5. `serving_kv_cache.py`: paged KV cache allocation, prefix sharing, continuous batching.
6. `portability_rocm_hip.py`: CUDA/HIP portability checks and source migration planning.
7. `distributed_collectives.py`: ring/tree all-reduce and topology latency/bandwidth models.
8. `profiler_evidence.py`: profiler counter classification, roofline diagnosis, remediation plans.

Run all comprehensive labs:

```bash
python3 scripts/build_comprehensive_lab_plan.py
python3 scripts/run_comprehensive_labs.py
python3 scripts/verify_comprehensive_labs.py
```

Local runtime caveat: these labs are executable local implementations and models. CUDA, HIP, Nsight, NCCL, and GPU-resident Triton execution remain environment gated on this machine.
