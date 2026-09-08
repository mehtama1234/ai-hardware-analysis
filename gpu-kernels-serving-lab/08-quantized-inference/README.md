# Quantization: drift simulation versus packed storage

`run.py` measures reconstruction drift and estimates bit-budget storage. Its
returned quantized values are dequantized floating tensors, not packed weights.
Block helpers preserve partial final blocks by padding and trimming.

## Actual packed INT4 experiment

```bash
python3 -m unittest discover -s gpu-kernels-serving-lab/tests -p test_packed_int4.py -v
python3 gpu-kernels-serving-lab/08-quantized-inference/run_packed_int4.py
```

The local teaching format uses signed integer codes -7 through 7, encoded as
code+8 in a nibble. The first value occupies the low nibble, the second the high
nibble. A final odd value uses one padded nibble. Each block of 32 original
values has one FP32 scale. Quantization uses symmetric maximum-absolute scaling
and nearest rounding; zero blocks use scale 1. The reserved code 0 is rejected
on unpack. This is not a vendor-specific kernel format, NVFP4 or MXFP4.

The report measures backing storage for byte payload and FP32 scales, rather
than assuming four bits per weight. It reports reconstructed FP32 storage too:
unpacking can erase the storage advantage during computation. Python objects,
shape metadata and allocator overhead are excluded from buffer totals.

Separate raw samples cover packing, unpacking, FP32 matmul, and unpack-plus-
matmul. Inputs are created before timing; allocations performed by those
operations remain inside timing. All work is synchronous CPU execution.

Reconstruction error must stay within half the corresponding scale (with a
small floating-point tolerance). Output error is reported, not silently treated
as an acceptable model-quality change. The experiment uses synthetic matrices,
not a trained model or a task dataset. Native low-precision kernels and joint
model quality/performance validation remain future acceptance requirements.

Exercises: explain why the scale overhead is 32/32 = 1 extra bit per weight for
complete blocks; compare tiny tails with large matrices; measure when unpacking
costs outweigh any storage savings; then connect the format to a trained model
before choosing a task-quality threshold.

## Trained-model held-out quality experiment

```bash
python3 -m unittest discover -s gpu-kernels-serving-lab/tests -p test_digits_protocol.py -v
python3 gpu-kernels-serving-lab/08-quantized-inference/run_digits_quality.py
```

Requires scikit-learn in addition to PyTorch. The
[bundled digits dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html)
contains labeled 8x8 handwritten digit images and requires no download here.
This is a new stratified 80/20 split of that bundled dataset, not the original
UCI train/test benchmark protocol. Split seed 142 and model seed 141 are fixed.

A 64→64→10 ReLU MLP trains for exactly 150 full-batch Adam steps at learning rate
0.01. Pixels are divided by the fixed range 16. Only training examples enter
optimization; quantization uses learned weights alone, with no calibration data.
The held-out set is used once after training and packing, not for hyperparameter,
checkpoint, tolerance, or block-size selection.

The predeclared task gate requires FP32 accuracy at least 90%, packed accuracy
loss at most two percentage points, and lower packed model tensor storage.
This is a local teaching acceptance criterion, not a universal quality standard.
The report preserves split indices, labels, predictions, losses, dataset/state
hashes, package versions, storage and inference samples. A rejected gate writes
its results and exits nonzero; thresholds must not be loosened to make it green.

Interpretation is limited to one trained MLP, one split, and one seed. It cannot
establish LLM quality, robustness across seeds, native INT4 compute, or GPU speed.
## Repeated trained quality checks

For a repeated quality check, run:

```bash
python gpu-kernels-serving-lab/08-quantized-inference/run_digits_repeats.py
```

This uses predeclared `(model seed, split seed)` pairs `(141,142)`, `(171,172)`
and `(201,202)`. Every run retains the same training procedure and requires FP32
accuracy at least 90%, no more than two percentage points of packed accuracy
loss, and reduced packed storage. All runs, including failures, remain in
`out_digits_repeats.json` with indices, predictions, losses and timings. The
aggregate fails if any run fails; thresholds are not adjusted from the results.
Different splits overlap, so this is a small repeated-protocol check—not pooled
independent test examples or a confidence interval for general model quality.

All three initial runs passed. FP32/packed accuracies were 96.70%/97.25%,
97.53%/96.98%, and 96.15%/95.88%, respectively. The worst packed accuracy drop
was about 0.55 percentage points. This mixed direction across seeds is a reason
not to interpret the first run's improvement as a general quantization benefit.

## Local INT4 versus standardized MXFP4

The [OCP MX v1.0 specification, sections 5.1–5.3.3](https://www.opencompute.org/documents/ocp-microscaling-formats-mx-v1-0-spec-final-pdf)
defines MXFP4 with E2M1 elements, 32-element blocks and an eight-bit E8M0 scale.
It does not prescribe physical memory ordering. FP4 conversion must support
ties-to-even rounding, subnormals and saturation; four-bit storage alone is not
format conformance.

| Property | Local teaching INT4 | OCP MXFP4 |
|---|---|---|
| Elements | Integer values −7 through 7, offset encoding | E2M1 floating point |
| Shared scale | FP32 | E8M0 |
| Block size | Configurable | 32 |
| Bytes for 32 elements, excluding metadata | 16 payload + 4 scale = 20 | 16 payload + 1 scale = 17 |

The byte totals are derived from field widths, not device allocation measurements.
Our low-nibble-first packing is a local choice. Neither the packed INT4 module
nor the earlier MXFP4-like simulation is an accepted MXFP4 implementation.
Scale/conversion conformance tests and native execution remain separate work.
