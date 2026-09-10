# Real-model graph decode experiment

This experiment implements the first A/B/C milestone of the
[long-term program](../LONG-TERM-END-TO-END-GOAL.md). It compares native dynamic
KV-cache decoding, fixed-capacity eager decoding, and the same fixed-capacity
step in a CUDA graph. It does not implement dynamic request admission.

## Run

Local numerical and state-reuse tests:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m pytest gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_graph_decode.py -q
```

On a CUDA host with compatible PyTorch and Transformers 5.12.1:

```bash
python3 gpu-mode-curriculum/batch1-decode-vertical-slice/run_real_model_graph_decode.py --output-dir /tmp/gpt2-graph-experiment
python3 gpu-mode-curriculum/batch1-decode-vertical-slice/verify_graph_decode.py /tmp/gpt2-graph-experiment/real-model-graph-decode.json
```

The dedicated Colab handoff uploads only this experiment and its tests, runs
GPU checks before the pretrained benchmark, downloads the report/source/trace
archive, and stops its owned session:

```bash
bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
```

## Read the evidence

The model and tokenizer are pinned. Two batch/capacity configurations each
reuse one graph across three prompt fixtures. Five samples per mode rotate
execution order; raw tokens are compared with library generation and unbatched
references. Complete generation timing includes prefill and static cache reset,
but excludes graph construction. All modes retain the same resident static
cache and graph during memory measurements. These memory values are not an
isolated comparison of each mode's minimum footprint.

Graph replay removes per-operation host dispatch inside decode, but does not
remove the GPU operations themselves. Static attention still processes the full
masked capacity. Prefill, validation, token-buffer copies, and result assembly
remain outside the captured step. Capture is specific to batch and capacity;
unsupported requests are rejected by this experimental engine.

The source snapshots inside each imported result are authoritative for that
run. A subsequent code fix does not rewrite historical measurements. The
[progress ledger](../LONG-TERM-PROGRESS.md) records results and open gates.

## Next acceptance gates

- Matched profiles for all three modes and separate prefill/decode timing.
- Broader shape/length fixtures and pretrained logit-error checks.
- Exact source-bundle replay with dependency identity validation.
- Per-slot cursor/cache state, admission, EOS, cancellation, and resource reuse.
- Integration into actual HTTP serving with sustained arrival-load measurements.

## Replay a captured v0.2 experiment

The benchmark now writes `graph-decode-source.tar.gz`, a source manifest, and
recorded package versions. To replay that captured code on a fresh Colab session:

```bash
GRAPH_REPLAY_REPORT=gpu-mode-curriculum/gpu-runs/imports/graph-decode-20260909T184008/reports/real-model-graph-decode.json bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh
```

The wrapper checks archive/source/dependency hashes, recursively checks required
package versions, extracts into a fresh temporary directory, and clears
`PYTHONPATH` for the experiment subprocess. It compares runtime, workload,
reference tokens, correctness, and whether graph medians remain below both eager
modes. That last check establishes repeatability of the performance conclusion,
not equality of absolute latency across sessions. The replay writes
`graph-reproduction.json` and the experiment's usual raw report/trace artifacts.

The generated [decision and timing table](../analysis/graph-decode-decision.md)
contains matched profiles and stage measurements. Its caveats describe the
additional stage synchronization and differing prefill setup boundaries.
