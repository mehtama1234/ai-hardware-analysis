# Triton Fused Softmax

## Claim

Softmax can avoid extra memory traffic by keeping row state inside one fused program.

## Read The Code

- `programming-projects/triton-fused-softmax/kernel.py`
- `programming-projects/triton-fused-softmax/measure.py`
- `programming-projects/triton-fused-softmax/measurements.json`

## Predict

Predict that a fused row operation should write fewer intermediate values than a step-by-step version.

## Run

```bash
python3 programming-projects/triton-fused-softmax/measure.py
python3 scripts/run_kernel_benchmarks.py
```

## Change One Thing

Change the row length or block size. Do not change the expected output. Run the measurement again.

## Explain The Result

The useful result is not a single fastest number. The useful result is whether the same correctness check survives while the block shape changes timing.
