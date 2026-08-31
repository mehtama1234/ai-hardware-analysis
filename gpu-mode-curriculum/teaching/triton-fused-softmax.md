# Triton Fused Softmax

## First Question

Softmax reads a row, finds a maximum, computes exponentials, sums them, and writes normalized values. If each step writes a full temporary tensor, memory traffic grows. This lane asks whether one program can keep the row state close to the compute units.

## What The Code Does

- `programming-projects/triton-fused-softmax/kernel.py holds the Triton source.`
- `kernel-benchmarks/kernels/triton/softmax_layernorm.py gives the benchmark promotion path.`
- `scripts/run_kernel_benchmarks.py records correctness and timing fields.`

## What The Measurement Proves

The measurement proves the fused path returns the expected values for the tested shapes and records timing in the same format as other kernel families.

## What It Does Not Prove

It does not prove the selected block size is optimal. It does not replace a profiler trace. It proves that fusion can be tested with a fixed contract.

## Read Next

- `site/project-triton-fused-softmax.html`
- `site/autotune-db.html`
