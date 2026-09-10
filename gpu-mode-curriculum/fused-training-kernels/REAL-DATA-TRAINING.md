# Real-data training integration

The first workload uses pretrained GPT-2 at revision
`607a30d783dfa663caf39e06633721c8d4cfcd7e` and the
[Tiny Shakespeare corpus](https://github.com/karpathy/char-rnn/blob/6f9487a6fe5b420b7ca9afb0d7c078e37c1d1b4e/data/tinyshakespeare/input.txt).
The raw corpus SHA-256 is
`86c4e6aa9db7c042ec79f339dcb96d42b0075e16b8fc2e86bf0ca57e2dc565ed`.

`prepare_training_data.py` verifies that hash and tokenizes contiguous 90/5/5
percent character ranges independently. `data/manifest.json` records boundaries,
text hashes, token-file hashes, tokenizer revision, and the preparation source
hash. The ranges contain 301,966 / 18,066 / 17,995 tokens respectively. No
training example crosses a split boundary. Contiguous character splitting can
divide a scene or word; it does not establish independence of literary themes.

`run_real_training.py` runs standard and recomputed linear cross-entropy on the
same pretrained initialization, seed-specific sampled training offsets, tokens,
optimizer settings, and a fixed validation token range. All parameters are trainable,
including the tied input/output embedding. Dropout is disabled in both arms to
isolate the loss intervention. Order alternates across seeds. Test tokens are
not loaded by this runner. The v0.2 runner defaults to the full validation split (18,065 scored targets).
Use `--validation-tokens` only for an explicitly labeled prefix probe. Historical
v0.1 evidence used two small blocks and is not full-validation evidence.

From the repository root:

```bash
python3 gpu-mode-curriculum/fused-training-kernels/prepare_training_data.py
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 \
  gpu-mode-curriculum/fused-training-kernels/run_real_training.py \
  --output-dir /tmp/real-training-smoke --steps 1 --sequence 8 \
  --chunk-size 3 --seeds 7 --validation-tokens 16
```

Use `--device cuda` for measured GPU execution; an unavailable GPU is an error.
Step time includes forward, backward, and optimizer update, with device
synchronization. The first update includes optimizer-state allocation and is not
a steady-state performance sample. CUDA peak allocated memory covers the whole
step, not just loss activations. CPU peak memory is not measured.

`--save-checkpoints` saves each completed model plus optimizer/RNG state and
file hashes. This runner does not yet resume training or select a winning
checkpoint. Each invocation needs a fresh report directory. Partial progress
and exceptions are retained in its report.

Remaining gates: larger matched multi-seed runs, full validation evaluation,
predeclared quality target and time-to-target, parameter/gradient comparison of
paired runs, independently verified raw reports, source/dependency replay,
checkpoint reload and serving evaluation, optimizer alternatives, native reduced
precision, and fused-device implementation. A one-step CPU run is integration
evidence only and cannot close these gates.

The first [CPU smoke report](reports/real-data-cpu-smoke-01/real-training.json)
completed both one-step arms with identical training offsets and matching initial
validation loss. Post-update validation losses were 6.108181 and 6.108179, both
above the initial 6.099797. It provides integration evidence only. Captured source
files match the report hashes. Checkpoint saving was not exercised.

`check_real_training_parity.py` performs a separate one-update correctness
experiment on actual corpus tokens and pinned pretrained GPT-2. It compares
every trainable parameter's gradient, updated value, and both AdamW moments.
Reference tensors live in a temporary directory and are removed on exit; source
snapshots and per-tensor error summaries are retained with the report. This is
not a speed benchmark. Tolerances are fixed before execution: gradients/moments
use atol 2e-5 and rtol 5e-4; parameters use atol 2e-6 and rtol 2e-5; loss uses
atol 5e-5 and rtol 2e-5. Every element must satisfy its bound and be finite.

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 \
  gpu-mode-curriculum/fused-training-kernels/check_real_training_parity.py \
  --output-dir /tmp/real-training-parity
```

The defaults match the first real-data smoke: seed 7, eight target tokens,
chunk size three. Passing this case would not establish multi-step or multi-seed
learning parity; those remain separate required experiments.

`fused_training_kernels/evaluation.py` provides full-split token-weighted
evaluation for the next runner revision. It resets context per block, shares
one input token between blocks, and scores every target exactly once including
the final partial block. Its coverage/count test passed against a uniform model.
The v0.2 runner now uses this helper and captures its source. Two tests verify
complete target coverage and token weighting when the last block is shorter.
The measured v0.1 report continues to describe its original two-block probe;
v0.2 has not yet been executed end to end.

The first full-model real-data parity check **failed** its predeclared bounds:
29 gradient tensors, 56 updated-parameter tensors, and one first-moment tensor
had out-of-bound elements. The original
[failed report](reports/real-data-parity-cpu-01/real-training-parity.json) remains
authoritative. The small synthetic tests and matching losses do not override it.

A [focused projection diagnostic](reports/loss-numerics-cpu-01/loss-numerics.json)
found the same maximum hidden-gradient difference for native chunked autograd
and the chunked custom backward relative to full projection. Full-projection
custom backward differed by about 1.5e-8. `--candidate native_chunked` adds a
full-model native-autograd control for this numerical effect; that run is pending.
The candidate identity is recorded explicitly in the report (the existing
`losses.recomputed` field denotes the candidate arm even for this control).
No tolerance changes or custom-loss promotion follow from the diagnostic alone.

Current forward loss uses target values selected from `log_softmax`, fixing
cancellation in explicit `logsumexp - target_logit`. Six local tests passed,
including a large common-offset regression. Real-data parity remains unresolved.
The new `--reference-chunk-size 3` option can compare the custom operation against
native autograd with identical projection chunking. This diagnostic is distinct
from the original full-projection comparison and has not yet been executed.

A bounded [real GPT-2 output-head parity report](reports/output-head-parity-cpu-01/output-head-parity.json)
passed. It checks all 38,597,376 output-head elements, 6,144 hidden-gradient
elements, loss, and one update using actual pretrained hidden states. Max errors
are 1.19e-5 (loss), 1.67e-5 (hidden gradient), 1.11e-4 (head gradient), and
2.98e-8 (updated head). This gate does not prove full-model optimizer parity,
multistep learning, or GPU performance.

The v0.2 [CPU probe](reports/real-data-v02-cpu-probe-01/real-training.json)
completed and passes the verifier. Both arms used the same eight training tokens
and 16 validation targets. After one update, mean NLL was 6.5332005 (standard)
and 6.5331960 (recomputed), difference -4.53e-6. The generated decision remains
`review`: one seed/step and a tiny validation prefix are integration evidence only.

The [checkpoint smoke](reports/real-data-checkpoint-cpu-01/real-training.json)
completed and passed both the training and checkpoint verifiers. Both arms saved
model plus optimizer/RNG state with four recorded files per run; each checkpoint
directory is 1,493,420,983 bytes. The decision remains `review` because the probe
uses one seed, one update, and 16 validation targets. Checkpoint reload through
serving is still open.

The saved [recomputed checkpoint reload](reports/real-data-checkpoint-cpu-01/checkpoint-reload-v2.json)
passed a deterministic four-token greedy generation smoke using the pinned
tokenizer and explicit attention mask. This is a CPU reload gate; serving transport
and GPU latency integration remain open.

The saved recomputed checkpoint also passed a [continuous HTTP serving smoke](reports/real-data-checkpoint-cpu-01/checkpoint-http-smoke.json). One four-token request matched reference tokens, completed with the declared budget, drained accounting, and left the KV cache empty. This is CPU loopback integration evidence; GPU serving and larger quality evaluation remain open.

The checkpoint HTTP report is also mechanically verified by
`verify_checkpoint_http_smoke.py`, including checkpoint hashes, token parity,
budget terminal, scheduler drain, and cache cleanup.

A [two-seed CPU quality probe](reports/real-data-multiseed-cpu-01/real-training.json)
completed and passes verification. Both arms improved validation NLL over two
updates; the median recomputed-minus-standard difference was -1.31e-6. The
decision remains `review` because the budget is tiny and CPU timing is not GPU
evidence.
