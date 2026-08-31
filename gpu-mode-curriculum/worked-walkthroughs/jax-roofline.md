# JAX Roofline Model

## Claim

A workload is compute-limited only when it has enough arithmetic work for each byte moved.

## Read The Code

- `programming-projects/jax-scaling-roofline/roofline_model.py`
- `programming-projects/jax-scaling-roofline/measure.py`
- `programming-projects/jax-scaling-roofline/measurements.json`

## Predict

Pick one shape and predict whether bytes or FLOPs limit it. Write down the arithmetic intensity before running the code.

## Run

```bash
python3 programming-projects/jax-scaling-roofline/measure.py
```

## Change One Thing

Double the hidden size, then double the sequence length. Compare which change moves the bottleneck label.

## Explain The Result

The model proves only the math of the estimate. Hardware counters are a separate test. A good answer names both the estimate and the missing counter evidence.
