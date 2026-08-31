# CUDA Memory Kernel

## First Question

A GPU can issue many loads at once, but slow address patterns waste memory bandwidth. This lane asks a small question: do adjacent threads read adjacent data, and how much does that change time per byte?

## What The Code Does

- `programming-projects/cuda-memory-kernel/kernel.cu defines the CUDA source shape.`
- `programming-projects/cuda-memory-kernel/measure.py records the local contract result.`
- `kernel-benchmarks/kernels/cuda/memory.cu is the promotion source for a GPU host.`

## What The Measurement Proves

The measurement proves that the benchmark harness can separate contiguous, strided, and gathered access patterns and preserve the result as JSON. On Colab T4 it also proves the CUDA path can see an NVIDIA GPU.

## What It Does Not Prove

It does not prove peak bandwidth for every GPU. It does not prove that a larger model is memory-bound. It proves the smaller claim first: address pattern changes measured memory behavior.

## Read Next

- `site/kernel-benchmarks.html`
- `programming-projects/cuda-memory-kernel/README.md`
