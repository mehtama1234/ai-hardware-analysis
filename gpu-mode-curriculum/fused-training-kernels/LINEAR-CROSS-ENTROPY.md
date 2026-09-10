# Recomputed linear cross-entropy

This executable operation starts training-capstone package D. It uses PyTorch
matrix operations and a custom first-order backward. GPU fusion, native reduced
precision, real-data learning, and end-to-end speed/memory measurements remain
open. The scenario timings in `fused-training-report.json` are modeled inputs;
they are not measurements of this implementation.

For hidden states X[N,H], output weights W[V,H], bias b[V], and labels y[N]:

```
Z = X W^T + b
L = sum_valid(logsumexp(Z_i) - Z_i,y_i) / M
P = softmax(Z)
G_i = (P_i - one_hot(y_i)) / M      for valid rows; zero otherwise
dX = G W
dW = G^T X
db = sum_rows(G)
```

M is the number of non-ignored labels for mean reduction and one for sum
reduction. Every derivative also multiplies by the upstream scalar gradient.
The implementation follows these identities independently in each token chunk;
weight and bias gradients accumulate across chunks. Backward recomputes logits
and softmax from the saved inputs. It retains X, W, labels, optional bias, and
the valid count, but no N-by-V logit/probability activation. Temporary logits
scale with chunk_size times V; total training peak memory also includes model
activations, gradients, optimizer state, allocator behavior, and overlapping
temporaries. Saved-tensor inspection does not establish GPU peak-memory savings.

The public contract currently accepts float32/float64, optional bias, int64
labels, mean/sum reduction, and an ignore index. Autocast and second derivatives
are unsupported. An all-ignored mean returns NaN with zero gradients, matching
the reference behavior. Label validation reads a device scalar; its cost must
remain included in application benchmarks. Frozen weights and tied embedding/
output weights are supported through ordinary autograd accumulation.

Run from the repository root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m unittest discover \
  -s gpu-mode-curriculum/fused-training-kernels/tests -v
```

Tests check numerical finite-difference gradients for noncontiguous inputs,
awkward chunks, both reductions, bias, ignored labels, and upstream scaling;
large-logit stability; frozen weights; saved activations; and tied-weight AdamW
updates over three seeds. The update test uses synthetic examples and establishes
implementation parity only. It does not establish learning quality.

Next: integrate this loss with pinned real-data fine-tuning and held-out splits,
compare saved versus recomputed loss implementations under matched tokens and
seeds, record synchronized GPU step time and peak memory, then evaluate a selected
checkpoint through serving. Native low-precision and a fused kernel are separate
interventions requiring new correctness and quality evidence.
