# Fused Training Kernels

## First Question

Training does forward math, backward math, and optimizer updates. If each small operation launches its own kernel and writes full tensors to memory, time is lost to launches and memory traffic. This lane asks which groups of operations can share one pass over data.

## What The Code Does

- `fused-training-kernels/fused_training_kernels/analyzer.py models the fused training cases.`
- `custom-ops/custom_ops/fused_bias_gelu_residual.py gives a concrete fused operator path.`
- `model-integration/model_integration/tiny_transformer.py connects the operator to a transformer-shaped block when present.`

## What The Measurement Proves

The measurement proves each training case has a correctness bound, a launch reduction estimate, an HBM reduction estimate, and a promotion path.

## What It Does Not Prove

It does not prove numerical safety for every model size or optimizer. It proves each fused choice states the saved work and the error bound.

## Read Next

- `site/fused-training-kernels.html`
- `site/custom-ops.html`
- `site/model-integration.html`
