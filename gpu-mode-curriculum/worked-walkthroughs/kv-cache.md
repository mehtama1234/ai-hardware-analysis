# KV Cache Blocks

## Claim

Serving long prompts becomes memory work unless cached key and value blocks are reused and accounted for.

## Read The Code

- `kv-cache-paged-attention/kv_cache_paged_attention/simulator.py`
- `kv-cache-paged-attention/kv-cache-report.json`
- `serving-traces/reports/serving-trace-report.json`

## Predict

Predict that prefix-heavy requests reuse more blocks than unrelated short requests.

## Run

```bash
python3 scripts/run_kv_cache_paged_attention.py
python3 scripts/run_serving_traces.py
```

## Change One Thing

Increase the shared prefix length in a serving fixture. Keep the number of requests fixed. Rebuild the reports.

## Explain The Result

The proof is block accounting: peak blocks, reused blocks, and admitted requests. It is not a claim about a production server until a real serving engine produces the same fields.
