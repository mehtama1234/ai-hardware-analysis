# Quantization Format Choice

## Claim

Fewer bits reduce storage, but the result is useful only if error and dequantization cost stay inside the workload limit.

## Read The Code

- `quantization-memory-formats/quantization_memory_formats/analyzer.py`
- `quantization-memory-formats/quantization-report.json`
- `numerical-reproducibility/numerical-reproducibility-report.json`
- `programming-projects/hf-quant-serving/measure.py`

## Predict

Predict that smaller formats improve compression but do not all pass the same error check.

## Run

```bash
python3 scripts/run_quantization_memory_formats.py
python3 scripts/run_numerical_reproducibility.py
python3 programming-projects/hf-quant-serving/measure.py
```

## Change One Thing

Tighten the cosine or max-error threshold. Run the report again and see which formats move from pass to calibration-needed.

## Explain The Result

The measured claim is format-by-format: compression, error, cosine similarity, and dequantization tax. There is no single best format without a workload and a tolerance.
