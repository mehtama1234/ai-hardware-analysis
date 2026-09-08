# Autoregressive transformer serving mechanics

Run from the repository root in the documented CPU environment:

```bash
python gpu-kernels-serving-lab/13-capstone-mini-serving-engine/server.py --backend neural
```

The existing `/v1/completions` and `/v1/batch_completions` endpoints now optionally
execute a real character-level transformer: token and learned position embeddings,
causal attention, feed-forward block, final normalization, and vocabulary head.
Greedy decoding feeds each selected token back into the model. Per-request KV
tensors retain past attention keys and values; positions advance with cache length.
The default deterministic transport exercise remains available and unchanged.

This model uses fixed-seed **untrained** weights. It demonstrates actual neural
execution, not useful language generation or pretrained-model quality. No model
is downloaded. Unknown input characters map to `?`, input is lowercased, and the
context limit is 128 characters including requested output. There is no EOS token;
generation always stops at the requested positive count.

The trained-quality protocol is separate from this untrained serving backend:

```bash
python gpu-mode-curriculum/model-integration/run_trained_neural_quality_repeated.py \
  --device cpu --seeds 8181,8282,8383 --steps 400
```

It trains independent copies on the same synthetic train/eval split, checks
held-out next-character accuracy and cached/full decode parity for every seed,
and writes `model-integration/reports/trained-neural-quality-repeated.json`.
The protocol is quality evidence for a tiny synthetic task, not production
language-model quality; the accepted T4 single-seed run remains separately
identified in the GPU promotion index.

Equal-length batch requests use one vectorized autoregressive decode tensor and
report `batch_mode: vectorized`; variable-length batches explicitly use a
`serial-fallback` because this teaching model has no padding/length mask or
paged-cache implementation. There is no continuous admission-time batching,
cross-request prefix reuse, paging, or GPU execution. The reported prefix reuse
is zero.
HTTP compute time covers the whole completion, not time to first token. This is
a local teaching endpoint, not a hardened public service.

```bash
python -m unittest discover -s gpu-kernels-serving-lab/tests -p test_neural_serving.py -v
```

Tests compare every generated step's logits and chosen tokens between cached and
full-sequence autoregression, including the context boundary. They also check
request isolation, serial batch behavior, invalid requests at the generator
boundary, and both HTTP completion endpoints against direct model execution.

The HTTP layer rejects non-object bodies, coerced token counts, non-string
prompts, empty or oversized batches, and oversized request bodies. Teaching limits
are 64 KiB per body, 16 prompts, 4096 characters per prompt and 128 output tokens;
the neural backend additionally enforces its 128-character total context. Body
reads have a ten-second socket timeout. These bounds are request validation, not
admission control. The server now has an opt-in `AdmissionController` with
capacity and queue limits; the default server remains unlimited for backward-
compatible teaching runs.

The bounded CPU contract can be reproduced with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_admission.py
```

It admits one active request, queues two, and rejects additional requests with
HTTP 429 under a synthetic 80-ms workload. This establishes admission semantics
and queue accounting only; it does not prove production serving throughput,
streaming token timing, or GPU capacity.

The neural backend also exposes a bounded SSE-style token stream at
`/v1/stream`. Its CPU contract is exercised with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_streaming.py
```

The experiment checks token count, `[DONE]` framing, direct-generation parity,
and first-token/total-time observations over three closed-loop requests. It is
not a production streaming implementation and does not establish GPU token
timing or client backpressure behavior.

The vectorized batch contract can be reproduced with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_batch.py
```

That probe checks three equal-length prompts through the shared batched decode
path and two variable-length prompts through the explicit serial fallback. It
compares every returned text to independent direct generation and records the
two modes separately in `serving-batch-cpu.json`. This is tensor-batch evidence,
not continuous arrival-time batching or a paged KV-cache implementation.

The separate arrival-time scheduler reference is exercised with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_microbatch.py
```

It submits eight concurrent requests into an 8-ms collection window, enforces a
maximum batch size of three, records each formed batch, and checks exact output
parity. It demonstrates bounded microbatch formation only; the HTTP server does
not claim this scheduler as production admission, cancellation, paging, or GPU
capacity infrastructure.

Bounded rejection and cancellation are exercised separately with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_backpressure.py
```

The probe uses a finite pending queue and a synthetic slow backend, then checks
queue-full rejection, cancellation accounting, output validity, and conservation
of accepted/rejected/cancelled requests. It is a control-plane contract, not a
production tail-capacity or GPU result.

The HTTP integration contract is exercised with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_http_controls.py
```

This starts the handler with the opt-in microbatch scheduler, sends concurrent
loopback requests, and checks vectorized responses plus HTTP 429 queue-full
responses. The default server remains unchanged unless `--microbatch` is
selected; this is bounded control-plane evidence, not production tail capacity.

Paged-cache layout mechanics are exercised independently with:

```bash
python gpu-mode-curriculum/model-integration/run_paged_kv_cache.py
```

The CPU reference allocates fixed-size pages, appends tokens across page
boundaries, gathers a contiguous oracle, frees and reuses pages, and rejects a
capacity overflow. It does not claim a CUDA paged-attention kernel, eviction
policy, or production memory-management behavior.

The native CUDA follow-up is staged with:

```bash
python gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_kv_cuda.py
```

It compiles a page-table gather kernel, checks a non-contiguous multi-sequence
layout against the host oracle, and records CUDA-event samples when `nvcc` and a
GPU are present. On this CPU host it records `unavailable` rather than treating
source presence as hardware evidence.

The fused paged-attention correctness kernel is exercised with:

```bash
python gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_paged_attention_cuda.py
```

On the authenticated T4 it checks three sequences and two heads against a host
softmax oracle (maximum absolute error `1.19209e-7`, median kernel time
`0.02048 ms`). This is a bounded reference kernel, not a production
FlashAttention implementation or a full serving-capacity result.

## Bounded HTTP load experiment

```bash
python gpu-kernels-serving-lab/13-capstone-mini-serving-engine/run_neural_load.py
```

This starts an ephemeral loopback server and checks eight completions at each
client concurrency of 1, 2 and 4 against direct model output. The generated
`out_neural_load.json` records every response, request latency, server compute
time, wall-clock output-token throughput, and imported local source hashes.
The server is shut down after the experiment. It runs in the same process as
the client; CPU contention and HTTP overhead are included. Client executor
waiting is excluded from individual latency but included in whole-wave time.
Eight samples make the nearest-rank p95 simply the maximum; this is a bounded
mechanics experiment, not a statistically strong tail-latency or capacity result.

A larger CPU tail-load sweep is available with:

```bash
python gpu-mode-curriculum/model-integration/run_serving_tail_load.py
```

It runs 16 requests at concurrency 1, 2, 4, and 8 through the opt-in
microbatch HTTP path, retaining every accepted latency, nearest-rank p95,
wave throughput, batch mode, and exact output-parity check. It is still a
same-process CPU experiment with a synthetic untrained model, not production
capacity or GPU performance evidence.
