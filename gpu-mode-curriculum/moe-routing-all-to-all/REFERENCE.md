# MoE dispatch, expert computation and combine reference

## Relationship to primary sources

Shazeer et al. define a weighted expert sum and apply softmax after retaining
top-k noisy logits (section 2, equations 1 and 3–5). Their distributed design
places different experts on different devices (section 3.1). Our selected-logit
normalization and sharded ownership illustrate related mechanisms, but omit
learned noise and the paper's balancing objectives. This is not a reproduction
of its trained architecture or performance. [Sparsely-Gated MoE, v1](https://arxiv.org/html/1701.06538v1).

Switch uses top-1 routing; its router pseudocode selects a probability from a
softmax over all experts. Its capacity treatment includes overflow and a residual
path. Our lab instead normalizes only selected logits, uses explicit global
rank-ordered capacity, and has no residual path. [Switch Transformers, section
2.2 and figures 15–16](https://www.jmlr.org/papers/volume23/21-0998/21-0998.pdf).

Consequently, in this lab `top_k=1` gives gate one and zero derivative with respect
to router logits while the selection stays fixed. It is useful for dispatch
tests, but is not Switch's gate or an adequate task-gradient mechanism for
training this top-1 router. At `top_k>1`, the selected-logit gate derivatives can
be nonzero. A future trained router must choose and test its gating objective
explicitly instead of inferring learning behavior from successful dispatch.

Review scope: selected routing/distribution sections and Switch pseudocode, not
full-paper reproduction or an audit of every reported experiment.

## Local implementation

### Exercise: distinguish dispatch from router learning

Use one token with scalar value 2, two experts with scalar weights 1 and 3, and
router logits `[2,0]`. For selected-only top-1 softmax, derive the output and both
logit derivatives. Repeat when selecting the highest probability from a full
two-expert softmax without renormalizing it.

Solution: selected-only normalization gives gate 1, output 2 and derivatives
`[0,0]` while expert selection is unchanged. In the alternative, let
`p = exp(2)/(exp(2)+1)`. Output is `2p`, and derivatives are
`[2p(1-p), -2p(1-p)]`. The reference suite checks both using autograd and the
explicit derivative formula. This is a gate-semantics exercise, not a complete
implementation of a published router or its auxiliary losses.

A second controlled test holds two scalar experts fixed at 0 and 2, uses both
experts, and updates only two router logits toward target output 1.5. Thirty
fixed gradient-descent updates must reduce squared error by at least 99%.
This checks the learning mechanism; one fixed token is neither a held-out task
nor evidence of generalization, specialization or load balance.

`moe_routing_all_to_all/reference.py` adds a CPU FP32/FP64 tensor reference next
to the existing load-count simulator. It performs real linear expert computation;
it is not a fused kernel, distributed exchange or trained MoE model.

For tokens `X[T,D]`, router logits `L[T,E]` and expert weights `W[E,O,D]`:

1. Select `k` distinct experts per token by descending logit. Equal logits use
   increasing expert index for a deterministic tie break.
2. Apply softmax only to the selected logits. These gates sum to one before
   capacity dropping; this is an explicit local routing policy, not a claim that
   all MoE architectures use the same normalization.
3. Each expert accepts at most `capacity` assignments, in increasing token order.
   Drop later assignments. Do not renormalize surviving gates. A token with no
   accepted assignment receives a zero output.
4. Batch each expert's accepted tokens, apply its linear weight, multiply by the
   corresponding gates and sum contributions into each original token's output.

The output is `Y[t] = sum(g[t,j] * W[e[t,j]] @ X[t])` over accepted assignments.
Return routing indices, gates, acceptance mask, offered/accepted loads and drop
count so learners can inspect the exact dispatch decision.

Gradients flow through selected logits, inputs and expert weights, with routing
indices and capacity decisions held fixed. This does not differentiate across
top-k or capacity boundaries. Biases, expert MLPs, auxiliary load-balancing losses,
router training and residual paths are not implemented in this reference.

```bash
python3 -m unittest discover -s gpu-mode-curriculum/moe-routing-all-to-all/tests -v
```

Tests compare outputs and all three input gradients with a separate token-by-token
scalar-dot-product oracle across FP32/FP64, k=1/2/4 and capacities including zero.
Hand-computed cases check ties, unique assignments, dropping and absence of
post-drop renormalization. Empty token batches and invalid contracts are tested.
The suite is now registered in the aggregate advanced checkpoint.

Eight tests now pass. Additional checks cover finite-difference gradients away
from routing boundaries and noncontiguous input/weight views. Identity experts
must reconstruct each token multiplied by its retained gate mass; with no drops,
dispatch/combine reconstructs the original tokens. The all-dropped case also
checks finite FP32 inputs of magnitude `1e38` and exact zero gradients. Zero
bookkeeping multiplies each value by zero before summing, avoiding an unnecessary
overflow in a sum that contributes no expert output.

Next: broaden numerical/shape coverage and add expert MLP integration, then
partition expert ownership across processes and compare
distributed outputs with this reference. CPU reference correctness does not
establish GPU performance, communication overlap or trained task quality.

## CUDA reference promotion

```bash
python3 gpu-mode-curriculum/moe-routing-all-to-all/run_gpu_moe.py
```

The CUDA probe runs the same selected-logit routing, capacity mask, expert
linear computation and combine path on `256 x 32` tokens with eight experts and
top-2 capacity 64. It compares outputs and gradients with the CPU FP64
reference, checks route and acceptance masks, and records seven synchronized
forward/backward CUDA-event samples in `reports/gpu-reference.json`. This is a
single-GPU correctness/timing promotion; it does not claim multi-rank
all-to-all communication or production MoE throughput.
