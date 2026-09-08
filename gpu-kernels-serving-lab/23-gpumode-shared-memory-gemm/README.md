# Shared-memory GEMM: evidence boundaries

Run from the repository root:

```bash
python3 -m unittest discover -s gpu-kernels-serving-lab/tests -v
python3 gpu-kernels-serving-lab/23-gpumode-shared-memory-gemm/run.py
```

Requires PyTorch for the CPU demonstration. CUDA compilation additionally
requires `nvcc` and execution requires a compatible visible device. This is not
yet a pinned-environment reproduction package.

## What is measured

The CPU paths implement scalar Python accumulation, a tiled sequence of CPU
PyTorch matrix products, and a CPU PyTorch library baseline. Their raw
`samples_seconds` include output allocation and Python dispatch, but exclude
input construction and reference checks. Warm-up and repetition counts are
recorded per row. These are CPU operation latencies, not CUDA performance or
hardware shared-memory measurements.

The reference uses FP64 multiplication of the same FP32 input values. Elementwise
acceptance uses `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)` with
explicit shape and finite-value checks. The separate 15-case result set tests
three implementations on scalar, rectangular/tail, noncontiguous, zero, and
cancellation inputs. It is useful coverage, not an exhaustive numerical proof.

The traffic model counts logical loads and is explicitly analytical. It does not
measure DRAM bytes, cache hits, bank conflicts, or occupancy. In particular, a
CPU tiled speedup must not be attributed to measured GPU memory-traffic savings.

## GPU acceptance

Missing `nvcc` is a skip and leaves `gpu_execution_accepted` false. Compilation
failure, process failure, missing metrics, non-finite metrics, unacceptable
reported errors, or nonpositive timing makes the overall run fail. The process
returns nonzero on failed checks. A successful CPU-only run does not close the
GPU acceptance gate.

The CUDA runner requests 256x256x256, 5x7x11, and 31x17x33 (M,N,K), compiling
each specialization into a temporary directory. The source initializes outputs
to a NaN sentinel, compares against CPU FP64 accumulation, and rejects non-finite
outputs or absolute error above 1e-4. It reports seven event-timed batch means,
each over 30 launches, plus their median. These are batch averages, not individual
launch latency percentiles. Compilation and transfers are outside event timing.
See the [CUDA event API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__EVENT.html)
for event timing semantics.

All three GPU implementations use the same event timing helper and input
buffers. The added cuBLAS SGEMM baseline uses `CUBLAS_PEDANTIC_MATH` for an
explicit FP32 comparison, not a fastest-possible mixed-precision baseline.
Because cuBLAS stores matrices column-major, the call computes C-transpose as
B-transpose times A-transpose, with operands and M/N swapped. See the
[cuBLAS reference](https://docs.nvidia.com/cuda/cublas/).
Its output is checked against the same CPU FP64 reference. The report includes
CUDA driver/runtime and cuBLAS versions, compute capability and device memory.
The Python acceptance checks require seven positive finite samples for each
implementation and agreement between their median and reported duration.

Source hashing and compile commands are recorded. The CUDA path still needs
complete environment provenance, profiler capture,
and hardware validation before meeting the advanced goal. GPU source has not
been compiled or executed during this CPU-only development pass; mocked runner
tests prove orchestration behavior only.

## Exercises

1. Explain why a 5x7x11 case with tile 4 needs tail handling in all dimensions.
2. Compare naive and tiled outputs against FP64; deliberately corrupt one element
   and confirm failure even if the total checksum stays unchanged.
3. Inspect the cancellation and noncontiguous cases before proposing a tolerance
   change. A wider tolerance needs evidence, not just a desire to pass.
4. Compare raw timing distributions, then explain why Python dispatch dominates
   small CPU shapes and why these results cannot predict CUDA speedups.
5. On an authorized GPU host, extend the CUDA shape suite and collect profiler
   evidence before claiming the traffic model explains measured performance.
