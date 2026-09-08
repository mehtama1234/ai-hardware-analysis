# Native tensor-core GEMM promotion

The planner in `tensor_core_gemm/planner.py` describes CTA, warp, MMA, shared
memory, and epilogue choices. The native promotion probe makes one of those
designs executable:

```bash
python3 run_native.py
```

`native_wmma_runner.cu` uses a 16x16x16 WMMA instruction shape on a 128x128x128
FP16-input, FP32-accumulator GEMM. It compares the result with an independent
FP64 host reference and with a cuBLAS FP32 baseline, and records seven
CUDA-event samples for both paths. The acceptance artifact is
`native-execution.json`; it includes hashes for the CUDA probe and launcher.

The WMMA result uses a 0.02 absolute-error bound against the FP64 reference,
while cuBLAS uses 5e-4 because its FP32 accumulation is the baseline being
measured. This is a correctness and timing probe, not a claim of production
throughput or complete CUTLASS/CuTe coverage. SASS inspection and profiler
counters remain separate promotion steps.

For the SASS and counter evidence:

```bash
python3 profile_native.py
```

This rebuilds with `-lineinfo`, checks `cuobjdump --dump-sass` for `HMMA`/`MMA`
instructions, and attempts an Nsight Compute CSV capture of
`sm__inst_executed_pipe_tensor.sum`. Tool absence or a failed counter capture
is recorded explicitly; it is not converted into a passing measurement.
