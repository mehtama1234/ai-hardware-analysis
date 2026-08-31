# Distributed Collectives

## Claim

A training step can wait on communication even when each GPU has enough compute.

## Read The Code

- `distributed-collectives/distributed_collectives/analyzer.py`
- `distributed-collectives/distributed_collectives/benchmark.py`
- `distributed-collectives/reports/collective-benchmark-run.json`
- `programming-projects/distributed-collectives/collective_model.py`

## Predict

Predict that larger payloads care more about bandwidth, while smaller payloads care more about latency.

## Run

```bash
python3 scripts/run_distributed_collectives.py
python3 scripts/run_distributed_collectives_benchmark.py
```

## Change One Thing

Change payload bytes in the benchmark command. On a multi-GPU host, run with torch distributed and compare all-reduce with all-gather.

## Explain The Result

The local code proves the communication model and artifact schema. A single-GPU Colab run cannot prove multi-GPU bandwidth; the failed gate records that limit.
