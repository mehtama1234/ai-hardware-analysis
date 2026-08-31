# JAX Scaling Roofline

## First Question

A workload is limited by the slowest required resource. Roofline analysis compares math work with bytes moved. This lane asks whether a kernel or model shape has enough math per byte to use the compute units well.

## What The Code Does

- `programming-projects/jax-scaling-roofline/roofline_model.py computes arithmetic intensity and bottleneck class.`
- `programming-projects/jax-scaling-roofline/measure.py writes the project measurement.`
- `programming-projects/jax-scaling-roofline/jax-scaling-roofline.ipynb gives the notebook path.`

## What The Measurement Proves

The measurement proves the model can classify test shapes using explicit FLOP, byte, bandwidth, and compute assumptions. It connects the JAX Scaling Book reading to local code.

## What It Does Not Prove

It does not prove hardware counters match the model. A profiler run is needed for that. It proves that the cost model is written down and can be checked.

## Read Next

- `site/project-jax-scaling-roofline.html`
- https://jax-ml.github.io/scaling-book/roofline/
