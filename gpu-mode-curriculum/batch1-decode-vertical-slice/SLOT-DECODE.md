# Per-request graph slots and continuous admission

This extends the fixed-batch graph experiment with independent KV-cache cursors,
slot ownership, cancellation, and reuse. It is part of the
[long-term program](../LONG-TERM-END-TO-END-GOAL.md).

## Components

- `slot_decode.py`: `SlotDecode` provides `admit`, `tick`, and `cancel`. Its
  generation-tagged handles protect new owners against stale cancellation.
- `continuous_service.py`: a single worker admits requests between decode ticks;
  canceled and completed slots can serve a replacement while peers remain live.
- `run_slot_decode.py`: pretrained eager/graph lifecycle correctness proof.
- `run_continuous_http.py`: actual HTTP streaming cancellation/reuse proof.
- `verify_slot_system.py`: validates source snapshots, output tokens, event
  indices, request identity, reuse, client/server accounting, and declared checks.

## Run

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m pytest gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_slot_decode.py -q
python3 -m pytest gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_continuous_service.py -q
GRAPH_EXPERIMENT=slots bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
GRAPH_EXPERIMENT=continuous bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
```

The handoff creates a separate owned T4 session, runs tests before pretrained
experiments, captures reports and source snapshots, downloads them, and stops
the session. Validate each resulting `slot-lifecycle.json` or
`continuous-http.json` by passing its path to `verify_slot_system.py`.

## Semantics and limits

All model/cache mutation belongs to one worker. Admission uses an unpadded
single-request prefill and copies its KV state into a free slot. Decode uses a
fixed slot count and capacity with per-slot positions. Reclamation zeros state
before reuse; inactive slots do not advance their cursors. Cancellation is
cooperative at decode boundaries and does not interrupt an executing CUDA kernel.

Prefill is synchronous and unchunked, so an admission can delay existing decode
work. The HTTP proof currently uses a fixed output-token limit and three requests.
It demonstrates dynamic admission and peer isolation, not sustained capacity,
latency-target goodput, or a production-serving performance advantage. Natural
EOS quality, variable HTTP output budgets, overload, independent replay, and
broader workload coverage remain separate acceptance gates.

See the [progress ledger](../LONG-TERM-PROGRESS.md) for accepted run identities.


## Per-request budgets and repeated arrival windows

`continuous_http.make_server` exposes `max_new_tokens` on `/stream`. It must be
an integer in `1..scheduler.max_tokens`; null, booleans, fractional values,
strings, and out-of-range values return HTTP 400 before admission. Terminal
records include the requested budget and a finish reason (`length`, `eos`, or
cancellation/failure status). This transport is separate from the historical
fixed-budget server used by earlier captured experiments.

```bash
python3 -m pytest gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_continuous_http.py -q
GRAPH_EXPERIMENT=load bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
```

The load runner uses two slots, queue limit eight, budgets 1/8/16/32, and rates
4/16/48 requests per second over eight-second arrival windows, repeated in reverse
order. It records load-generator lateness and includes drain time in throughput
and goodput denominators. Its declared targets are TTFT <=1 second, completion
<=3 seconds, and maximum inter-token gap <=0.5 seconds. A separate controlled
EOS request validates HTTP early termination. Run `verify_continuous_load.py`
against the downloaded `continuous-load.json` to recompute its acceptance and
metrics from raw client/server records.

These bounded windows characterize this exact loopback workload. A native
microbatch baseline comparison and an independent source-bundle replay are
separate open gates; the earlier fixed-batch graph replay does not prove them.


## Matched serving controls

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m pytest gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_microbatch_control.py -q
GRAPH_EXPERIMENT=comparison bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
```

The three-way comparison uses native microbatching with compacted dynamic caches,
graph microbatching that holds a group until completion, and graph continuous
admission. Requests keep their individual budgets; completed native rows are
removed from further model execution. Both fixed-group schedulers wait up to five
milliseconds to assemble a group. Graph modes prefill individual requests, while
the native control batches prefill. These choices are part of the comparison.

All modes use the same prompts, budgets, rates (16/48 requests per second), queue
limit (eight), active slot limit (two), and latency targets. Three rounds put each
mode in every order position once at each rate. Eight-second arrival windows
retain planned/actual client times, completed/rejected counts, budget mixes,
reference outputs, and server records. Validate the captured `serving-comparison.json`
with `verify_serving_comparison.py`; generate the decision with
`scripts/build_serving_comparison.py`.

Native-vs-graph results combine execution and prefill changes. Graph group-vs-
continuous results compare grouping/admission policies using the same slot engine.
Neither comparison establishes production capacity or independent replay by itself.
