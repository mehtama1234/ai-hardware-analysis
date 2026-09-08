# Executable exercises: memory, derivatives, and decoding

These exercises connect the current reference implementations to their tests.
They require Python, PyTorch tensors/autograd, matrix multiplication, and basic
binary arithmetic. Use the [CPU environment recipe](ENVIRONMENT.md), run commands
from the repository root, and make experimental changes in a separate working
copy. The reference implementations remain the tested solutions; do not modify
acceptance tolerances to make an incorrect candidate pass.

## 1. Why four-bit storage is not always an eightfold saving

For the local packed format, derive the storage for `n` FP32 weights using one
FP32 scale per block of `b` elements. Evaluate `(n,b)=(1,32),(33,32),(65,32)`.
Explain why a partial block and an odd element count require different padding.
Then reconstruct the byte encoding of `[-7,7,0,1]` with block size four.

Solution: payload bytes are `ceil(n/2)`; scale bytes are `4*ceil(n/b)`.
The totals are 5, 25, and 45 bytes, versus 4, 132, and 260 FP32 bytes. A single
weight therefore grows in storage. Block padding supports scale calculation;
it must not add logical weights. Byte padding supplies only the unused nibble
when the logical count is odd. Codes are signed quantized values plus eight,
and the first element occupies the low nibble. Here the scale is one, yielding
codes `[1,15,8,9]` and bytes `[241,152]`.

Inspect [packing and validation](../../gpu-kernels-serving-lab/common/packed_int4.py)
and [the solution tests](../../gpu-kernels-serving-lab/tests/test_packed_int4.py):

```bash
python -m unittest discover -s gpu-kernels-serving-lab/tests -p test_packed_int4.py -v
```

Extension: explain why the reconstruction bound is half a scale (up to floating
roundoff) but this does not bound a transformer's task accuracy. Explain why
unpacking followed by FP32 matmul is not a native INT4 compute benchmark.

## 2. Recompute probabilities without losing the gradient

Let `P=softmax(QKᵀ/sqrt(d))` and `O=PV`. Given an upstream derivative `G`,
derive `dV`, `dP`, `dS`, `dQ`, and `dK`. Identify which quadratic intermediate a
backward implementation can reconstruct instead of saving. Predict the failure
when the first visited key tile is entirely masked and an implementation blindly
subtracts negative infinity from negative infinity.

Solution: `dV=PᵀG`, `dP=GVᵀ`, and rowwise
`dS=P*(dP-sum(P*dP))`. Then `dQ=dS K/sqrt(d)` and
`dK=dSᵀ Q/sqrt(d)`. Reconstruct probability tiles from score tiles and saved
row log-normalizers. The row correction also equals `sum(O*G)`.
An initially all-masked tile contributes zero, not NaN; online rescaling must
handle that state explicitly until a finite score arrives.

Inspect [the recomputed solution](../flash-attention-backward/flash_attention_backward/recomputed.py)
and [its gradient and storage tests](../flash-attention-backward/tests/test_recomputed.py):

```bash
python -m unittest discover -s gpu-mode-curriculum/flash-attention-backward/tests -v
```

Acceptance checks outputs and all three derivatives, finite-difference gradients,
tile tails, masks, and saved tensors. Saved logical tensor bytes are not allocator
peak bytes: temporary allocations and externally supplied masks still matter.
This Python implementation is not a fused accelerator kernel.

## 3. A causal mask must follow the cache position

You have cached 17 tokens and receive a chunk of three more. Write the allowable
key indices for each new query. Why does a freshly constructed upper-left `3x20`
triangular mask produce the wrong result? How would you test request isolation?

Solution: query-local index `i` may see keys `j <= 17+i`, so the final allowed
indices are 17, 18, and 19 respectively. An unshifted mask instead stops at
0, 1, and 2, hiding almost all cached context. Position embeddings must use the
same cache offset. Keep cache state request-local; run prompt A, then unrelated B,
then A again and compare outputs. Compare every step's logits with full-sequence
recomputation as well as the chosen token: argmax agreement alone can hide errors.

Inspect [block caching](../model-integration/model_integration/tiny_transformer.py),
[autoregressive generation](../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/neural_generator.py),
and [the HTTP exercise](../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/NEURAL-BACKEND.md).

```bash
python -m unittest discover -s gpu-mode-curriculum/model-integration/tests -p test_cached_attention.py -v
python -m unittest discover -s gpu-kernels-serving-lab/tests -p test_neural_serving.py -v
```

The solution tests cover chunk partitions, token decoding, all three block
backends, unchanged prior cache tensors, generated-logit equivalence and HTTP
responses. These do not establish trained language quality, paged-cache behavior,
continuous batching, or GPU performance.

## 4. Page a KV cache without changing logical sequence order

A sequence has page size four and logical length seven. Given a page table
`[5, 1, 9]`, map logical token indices 0 through 6 to physical page/offset
pairs. Then explain why freeing a sequence must return every page exactly once,
and why a reused page must not expose stale tokens beyond the new logical length.

Solution: indices 0–3 map to page 5 offsets 0–3; indices 4–6 map to page 1
offsets 0–2; page 9 is reserved for a later append. Gather only iterates the
logical length, so stale tail slots are never visible. The reference allocator
sorts returned page IDs and rejects an append that exceeds free capacity.

Inspect [the paged-cache reference](../../gpu-kernels-serving-lab/13-capstone-mini-serving-engine/paged_cache.py)
and run:

```bash
python gpu-mode-curriculum/model-integration/run_paged_kv_cache.py
```

The native T4 extensions additionally compare page-table gather and fused
softmax attention with host oracles; they are correctness kernels, not a claim
of optimized paged-attention throughput.

## 5. Distinguish batching from backpressure

Why can a batch size of four coexist with a pending queue limit of three? What
should happen when a fifth request arrives while the worker is computing, and
how should a cancelled future affect batch accounting?

Solution: `max_batch` limits one execution group while `max_pending` limits
queued work, so they control different resources. A full queue returns an
explicit rejection (HTTP 429 at the opt-in server boundary); cancellation
removes work before execution and is counted separately from completion or
rejection. Test both layers:

```bash
python gpu-mode-curriculum/model-integration/run_serving_backpressure.py
python gpu-mode-curriculum/model-integration/run_serving_http_controls.py
```

Neither synthetic probe establishes production tail capacity, client disconnect
semantics, or GPU scheduling fairness.

## 6. Preserve ownership when dispatching requests across ranks

Two ranks receive local request lists of lengths three and two. Define a global
ordering that is deterministic even when local lengths differ, then state the
invariants needed before combining responses: no duplicate `(rank, local_index)`
pairs, every response matches its prompt, and every peer observes the same
ownership metadata.

Solution: rank-major order followed by local index is deterministic for this
contract. The two-rank CPU/Gloo reference checks exactly those invariants and
retains both rank reports:

```bash
python gpu-mode-curriculum/model-integration/run_distributed_serving_cpu.py
```

This is a dispatch/control-plane oracle. It does not establish NCCL/RCCL
transport, multi-GPU inference, network latency, or distributed gradients.

## Evidence review assignment

Run the [checkpoint](EXECUTABLE-CHECKPOINT.md). For one report, identify the exact
operation timed, excluded setup, raw samples, source hashes, and correctness
oracle. Find one claim the report cannot support. For HTTP load, individual
request latency excludes client executor waiting; whole-wave throughput includes
it. Eight requests per load level cannot establish reliable production p95.
There is no automatic pass condition for this written interpretation exercise.
