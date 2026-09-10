# GPU Host Handoff

This layer packages the generated GPU promotion manifest, dry-run command suite, GPU-run collector, and validation commands into a single handoff bundle for accelerator machines.

Run locally:

```bash
python3 scripts/build_gpu_handoff.py
python3 scripts/verify_gpu_handoff.py
```

On a GPU host:

```bash
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --dry-run
bash gpu-handoff/bin/run-gpu-host-handoff.sh h100-node-001 --execute
```

For the real-model inference decision slice on the existing Colab path, use
[`real-model-decision-colab-config.json`](real-model-decision-colab-config.json)
with `mode: real-model-decision`. It writes
`batch1-decode-vertical-slice/reports/real-model-serving-comparison.json`,
which is the input to the analog-workbench importer.
The `real-model-characterization` mode extends this with synchronized
prefill/decode timing, KV allocator peaks, output parity, and batch sizes 1/2/4
in `real-model-serving-characterization.json`.

For the next Colab gate, use
[`real-model-extended-characterization-colab-config.json`](real-model-extended-characterization-colab-config.json).
It adds longer-context scaling, synchronized serialized and concurrent
tail-latency samples, and a CUDA operator/data-movement profile. Power remains explicitly pending unless a
synchronized Colab power sensor is available.

The fused serving continuation is available with
[`real-model-fused-paged-decode-colab-config.json`](real-model-fused-paged-decode-colab-config.json).
It routes every one-token GPT-2 decode attention layer through the CUDA
paged-attention prototype and requires exact generated-token parity. Its
current Python allocator overhead is measured and reported separately; it is
not a production-performance or silicon claim.

The recovered real-model loop has two additional modes:

- `real-model-profile`: eager, SDPA, paged and persistent full-model comparisons,
  with separate compressed CUDA traces downloaded beside the report.
- `real-model-http`: actual streamed HTTP requests, native serial/microbatch
  comparisons, bounded queue rejection, and in-flight cancellation.
- `real-model-http-repeated`: four counterbalanced rounds including optimized
  custom paging, execution counts, measured KV bytes, and a source archive.
- `real-model-http-replay`: checks dependencies and replays the captured
  `colab-real-model-http-repeated-gpt2-20260909` archive in an isolated folder.

Set `COLAB_HANDOFF_MODE`, a fresh `COLAB_RUN_ID`, and a fresh
`COLAB_SESSION_NAME` when using `scripts/run_colab_gpu_handoff_local.sh`.
Verify the downloaded report with
`python3 batch1-decode-vertical-slice/verify_real_model_system.py <report.json>`.
Run `python3 scripts/build_real_model_decision.py` followed by
`python3 scripts/build_workbench.py` to refresh the decision and workbench.
See the [active checkpoint](../batch1-decode-vertical-slice/END-TO-END-GOAL.md)
for what remains unproven.
