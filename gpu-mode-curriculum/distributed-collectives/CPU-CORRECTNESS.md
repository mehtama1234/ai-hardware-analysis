# Two-process collective correctness

From the repository root, using the documented CPU PyTorch environment:

```bash
python3 gpu-mode-curriculum/distributed-collectives/run_cpu_correctness.py
python3 -m unittest discover -s gpu-mode-curriculum/distributed-collectives/tests -v
```

Two spawned local processes use Gloo and a temporary file rendezvous. Every rank
checks complete outputs for all-reduce, all-gather, reduce-scatter, all-to-all and
broadcast. Inputs differ by rank; each operation starts fresh. Gather/scatter
outputs start with NaN sentinels. Small integer-valued FP32 inputs permit exact
comparisons, including source ordering and destination slices.

The first isolated CPU execution passed all ten operation/rank comparisons.
The report retains actual and expected arrays, both ranks, the PyTorch version
and source provenance. An operation error fails the run, not an accepted skip.
The parent independently derives expected rank outputs using Python integer
formulas; matching but incorrect child `actual`/`expected` arrays are rejected.
Five report-contract tests cover coverage, invalid values and this rejection.
Collectives have a 30-second process-group timeout; the parent bounds joining at
90 seconds and terminates its remaining children on failure.

This is a correctness fixture, not a benchmark: it does not measure latency,
bandwidth, overlap or GPU execution. It covers one equal-split shape and two
local ranks, not uneven splits, larger worlds, gradients, multi-host fabrics or
NCCL/RCCL. Report-contract unit tests use synthetic records and are not additional
collective executions. This runner and its contract tests are now registered in
the aggregate checkpoint; acceptance of a new aggregate requires a fresh run.

## CPU latency baseline

`python3 gpu-mode-curriculum/distributed-collectives/run_cpu_benchmark.py`
adds a separate measured baseline. It runs five synchronized wall-clock samples
for each of the same five operations on two local Gloo ranks, starts each sample
from fresh rank-specific tensors, validates the full output, and retains both
rank-local raw samples and rank medians in `reports/cpu-benchmark.json`.
The result is useful for comparing a later NCCL/RCCL run, but it is explicitly
CPU-only: its timings do not establish GPU bandwidth, communication overlap,
topology efficiency, or serving performance.

The older `distributed_collectives/benchmark.py` remains unchanged. Its
[acceptance gaps](../advanced-lab-phase/DISTRIBUTED-AUDIT.md) are not fixed merely
by adding this independent correctness fixture.

## CUDA/NCCL smoke promotion

```bash
python3 gpu-mode-curriculum/distributed-collectives/run_nccl_gpu.py
```

On a host with one visible CUDA device this initializes NCCL with
`world_size=1`, executes a 1M-element `all_reduce` and `all_gather`, checks exact
results, and records seven CUDA-event samples in `reports/nccl-gpu.json`. The
artifact labels its scope explicitly: it proves CUDA/NCCL execution, not
multi-GPU communication, topology, scaling, or overlap. A multi-rank GPU run
still requires a host exposing multiple compatible devices.

## Multi-rank NCCL acceptance path

Launch one process per visible GPU on a suitable host:

```bash
torchrun --standalone --nproc_per_node=2 \
  gpu-mode-curriculum/distributed-collectives/run_nccl_multirank.py
```

The runner performs seven synchronized 1M-element all-reduces and checks the
reduced value on every rank before writing `reports/nccl-multirank.json`.
Missing CUDA, NCCL, or a sufficient device count is recorded as `unavailable:*`
and never converted into CPU evidence. The current host's preflight is
explicitly unavailable; a multi-GPU host is still required for acceptance of
distributed performance and topology claims.
