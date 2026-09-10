# Packed int4 weight representation

`quantization_memory_formats/packed_int4.py` provides a row-wise symmetric
signed-int4 container for even-width floating weight matrices. Each row stores
one float32 scale and two signed nibbles per byte. Quantization rounds to
`[-8, 7]`; zero rows use scale one. Dequantization reconstructs a floating
matrix, and `linear` is an explicit dequantize-then-GEMM reference path.

The implementation reports packed bytes plus scale bytes and rejects nonfinite,
integer, odd-width, or incompatible inputs. It is a storage and numerical
round-trip artifact. It does not claim native int4 tensor-core execution,
activation quantization, calibration quality, or application throughput.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover \
  -s gpu-mode-curriculum/quantization-memory-formats/tests -v
```

Three tests pass: round-trip error and storage accounting, signed nibble/zero
row behavior, and reference linear parity with invalid-input rejection. Next
steps are calibration on the pinned training checkpoint, error growth through
the model, supported GPU low-bit execution, and quality/serving comparison.

`quantization_memory_formats/quality.py` measures application-level output
error, RMSE, relative L2 error, cosine similarity, packed/float storage bytes,
and storage ratio for a batch of inputs. Five quantization tests now pass
(including two quality-metric cases). These metrics must be rerun on calibrated
model weights and representative activations before any serving decision.
