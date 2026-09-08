# Tiny Transformer Integration Lab

This lab connects the lower-level GPU curriculum artifacts to a model-shaped
program. It runs a tiny causal transformer block with:

- layer normalization
- QKV projection
- causal attention
- output projection
- fused bias + GELU + residual custom op
- autotune-record lookups for matmul, normalization, and custom-op families

The local implementation runs on CPU with PyTorch so correctness and timing are
available in CI. CUDA/Triton/custom-extension promotion should keep the report
schema and replace individual operators with accelerator-backed implementations.

## Run

```bash
python3 scripts/run_model_integration.py
python3 scripts/verify_model_integration.py
```

## Recomputed attention training integration

From the repository root:

```bash
python3 -m unittest discover -s gpu-mode-curriculum/model-integration/tests -v
python3 gpu-mode-curriculum/model-integration/run_attention_training.py
```

The existing block now accepts `attention_backend="materialized"` (unchanged
default), `"sdpa"`, or `"recomputed"`. The new paired experiment changes only
attention: both copies use the unfused feed-forward reference, identical initial
parameters, inputs, targets, and SGD momentum settings.

For sequence lengths 1, 17, and 33, it checks three consecutive optimizer steps:
outputs, losses, input gradients, every named parameter gradient, every updated
parameter, and momentum buffers. Length 33 crosses the recomputation tile boundary.
Any missing gradient or numerical disagreement raises an error rather than
producing a passing artifact. The output is `reports/attention-training-cpu.json`.

This is CPU training-equivalence evidence on synthetic regression targets, not
a convergence study, pretrained-model quality result, GPU benchmark, or serving
measurement. It demonstrates integration of the derivative path through QKV,
normalization, projections, residuals, and optimizer state. The isolated
attention report's saved-tensor reduction does not establish total training
peak-memory savings; that still requires allocator instrumentation.

## Training-block timing and allocator experiment

```bash
python3 gpu-mode-curriculum/model-integration/run_attention_benchmark.py --device cpu
# On an authorized CUDA host:
python3 gpu-mode-curriculum/model-integration/run_attention_benchmark.py --device cuda
```

The benchmark compares materialized, PyTorch SDPA, and recomputed attention in
the same block. Each backend must first pass output, input-gradient, and all
parameter-gradient checks against a CPU FP64 block. Timing samples cover gradient
clearing, forward, MSE loss, and backward; weights stay fixed and there is no
optimizer step. Inputs and targets are allocated outside the timed region.
Two warmups precede seven samples by default. The CLI sets one CPU thread and
disables TF32, restoring both settings afterward.

CUDA samples synchronize before and after the measured operation. A separate
warmed forward/backward records baseline allocation, peak allocation, and the
increment above baseline using the
[PyTorch allocator API](https://docs.pytorch.org/docs/main/generated/torch.cuda.memory.max_memory_allocated.html).
These are tensor allocations tracked by PyTorch, not total device consumption
or reserved cache. CPU peak memory is explicitly unavailable. Previous backend
device tensors are released before measuring the next backend.

Reports are `reports/attention-benchmark-cpu.json` and
`reports/attention-benchmark-cuda.json`. A CUDA request with no runtime writes
an unavailable report with no rows and exits 2. It does not rerun on CPU.
GPU acceptance, if attained, applies only to this block experiment; it does
not establish that the recomputed path is a fused kernel or faster than SDPA.

## KV-cached block decoding

```bash
python3 gpu-mode-curriculum/model-integration/run_cached_decode.py
```

`model.eval().forward_cached(x, cache=None)` returns output and a `(keys, values)`
tuple. Each batch owns its cache. Never reuse a cache after changing the weights
or for different sequence contents. Cache shape/device/dtype mismatches fail.
The inference-only method runs without autograd and leaves the prior cache
unchanged; append currently uses concatenation, not a paged allocator.

For a cached prefix of length p, local query i may attend to key j when
`j <= p + i`. Reusing an upper-left mask without that offset would hide valid
prefix keys. The tests compare token-at-a-time and chunked calls against a full
causal forward pass, including chunks crossing the recomputation block boundary.

The replay report records seven sessions per backend, each with a 17-vector
prefill and eight supplied-vector decode steps. Outputs are checked against the
same full SDPA block; raw CPU call latencies and final cache payload bytes are
recorded. These are not generated tokens, end-user TTFT, a server load test,
peak memory, or GPU performance evidence. Real serving integration remains open.

## Packed-weight block inference

```bash
python3 gpu-mode-curriculum/model-integration/run_packed_model.py
```

The experiment copies the existing block and replaces all linear layers with
`PackedInt4Linear`. Each replacement stores only byte payload, FP32 block scales,
and an optional FP32 bias. It has no retained FP32 weight parameter. Layer norms
and the block's other non-linear-layer parameters remain FP32. Conversion leaves
the source model unchanged. Packed format/shape/block metadata accompanies the
state dict and incompatible metadata is rejected on load.

Each linear call unpacks to a temporary FP32 matrix. Therefore this demonstrates
weight-storage reduction and executable integration, not native INT4 arithmetic
or a guaranteed runtime-memory reduction. The report measures resident model
tensor storage, full-forward latency including unpacking, and output drift on
synthetic inputs. Cached decoding must agree with the quantized full forward.

The block is untrained; output drift is not a task-quality score. Quality remains
explicitly unaccepted. The packed modules reject training mode and require FP32
inputs; no gradient-based packed-weight training is implemented.

## Whole-block compiler integration

```bash
python gpu-mode-curriculum/model-integration/run_compiled_training.py
```

This extends the paired training protocol with a CPU Inductor candidate. The
reference and candidate both use SDPA and start with identical parameters; only
the candidate block is passed to `torch.compile(..., fullgraph=True)`. Three
consecutive steps compare outputs, loss, input gradients, every named parameter
gradient, updated weights, and SGD momentum buffers. The optimizer remains
eager, so this does not claim compilation of the entire training loop.

The sequence is 17, batch 2, hidden width 16 and two heads. Model seed 71 and
data seed 72 match the existing training protocol. The paired reference is FP32
eager execution, unlike the separate operation compiler experiment's FP64
oracle. These answer different questions: multi-step application equivalence
versus operation-level numerical error.

The runner uses a temporary compiler cache and a 300-second worker timeout.
It captures generated forward/backward source via the PyTorch 2.4.1 private
hook described in the [compiler walkthrough](../compiler-runtime-inspection/README.md).
No fallback is substituted when compilation fails. Consult
`reports/compiled-training-cpu.json` for the actual outcome; merely having this
runner does not establish acceptance. The reported total elapsed time includes
compilation and validation and is **not** application throughput.

The timing extension records ten reset-state training steps per backend after
three warmup pairs. Each measured interval includes gradient clearing, forward,
MSE loss, backward and eager SGD update. Model/optimizer state restoration and
input cloning occur outside the interval. Eager/compiled order alternates, and
both reuse the final synthetic training batch. This measures a small repeated
training step, not a data-loading pipeline or sustained production training job.
Compilation completes during correctness checks and warmups; inspect captured
module counts and raw samples for signs of additional specialization. Broader
shapes, repeated independent sessions and task quality remain open.

### CUDA promotion

```bash
python3 gpu-mode-curriculum/model-integration/run_compiled_training_cuda.py
```

On an authorized CUDA host this compares the same eager and fullgraph-Inductor
pair on-device. It synchronizes CUDA timing and checks three optimizer steps,
including gradients, updated parameters and momentum. The report is
`reports/compiled-training-cuda.json`; a missing CUDA runtime produces an
explicit unavailable result rather than silently falling back to CPU. A Colab
handoff can preserve the report's source hashes alongside the paired attention
report, then verify both together with:

```bash
python3 gpu-mode-curriculum/scripts/verify_colab_attention_training.py <handoff-directory>
```

This remains a small synthetic block experiment: it does not establish
full-model throughput, quality, distributed training, or production serving.

The initial run passed all three paired steps and captured separate forward and
backward modules. Maximum errors across those steps were `4.77e-7` for outputs,
`2.24e-8` for parameter gradients, `5.96e-8` for updated parameters and `2.99e-8`
for momentum buffers. These are the scoped results in the
[compiled training report](reports/compiled-training-cpu.json), not evidence for
untested shapes, optimizers or architectures.

The timing extension also passed all correctness checks and captured exactly
two generated modules. Ten samples per backend yielded medians of 2.59 ms eager
and 3.05 ms compiled in that run: about 17% slower for the compiled block with
eager SGD. Both the isolated operation and this application slice therefore
showed measured losses on the tested small CPU workload. This is not a general
conclusion about Inductor or GPU compilation. The experiment is now registered
in the aggregate checkpoint. Its expanded isolated CPU reproduction subsequently
passed 65 tests and eleven experiments, including this training benchmark.
