# CUDA Memory Access

## Claim

Adjacent threads should read adjacent addresses when the goal is high bandwidth.

## Read The Code

- `programming-projects/cuda-memory-kernel/kernel.cu`
- `programming-projects/cuda-memory-kernel/measure.py`
- `kernel-benchmarks/reports/kernel-benchmark-report.json`

## Predict

Before running the code, predict that contiguous reads finish faster than strided or gathered reads for the same number of values.

## Run

```bash
python3 programming-projects/cuda-memory-kernel/measure.py
python3 scripts/run_kernel_benchmarks.py
```

## Change One Thing

Change the stride or gathered index pattern in the measurement code. Keep the element count fixed. Run the same command again.

## Explain The Result

If time changes while the element count stays fixed, the address pattern changed the memory work seen by the hardware. The claim is not that the GPU reached peak bandwidth. The claim is that layout is a measured variable.
