# Performance Regression Ledger

This layer extracts stable metrics from the generated reports and records them
in one regression ledger. It is the place to compare future runs against the
current local baseline.

Included layers:

- kernel benchmark median timings
- custom-op correctness, timing, and throughput
- autotune selected speedup estimates
- tiny transformer model throughput and correctness
- serving trace TTFT, TPOT, throughput, and prefix-cache savings

## Run

```bash
python3 scripts/build_regression_ledger.py
python3 scripts/verify_regression_ledger.py
```
