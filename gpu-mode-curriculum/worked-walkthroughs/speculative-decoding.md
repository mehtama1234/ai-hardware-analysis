# Speculative Decoding

## Claim

A draft model helps only when accepted tokens save more target-model work than rejected tokens waste.

## Read The Code

- `speculative-decoding-serving/speculative_decoding_serving/analyzer.py`
- `speculative-decoding-serving/speculative-decoding-report.json`
- `lesson-labs/lesson-096-lecture-22-hacker-s-guide-to-speculative-decoding-in-vllm/measurements.json`

## Predict

Predict that low acceptance raises wasted draft work even if the draft model is cheap.

## Run

```bash
python3 scripts/run_speculative_decoding_serving.py
python3 scripts/verify_speculative_decoding_serving.py
```

## Change One Thing

Lower one scenario's acceptance rate. Keep the target model cost fixed. Check whether the scenario moves to review.

## Explain The Result

The measurement proves the scheduler records acceptance, rollback, waste, and speedup together. It does not prove one draft model is always best.
