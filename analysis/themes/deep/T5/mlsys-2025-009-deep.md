# SparseTransX: Efficient Training of Translation-Based Knowledge Graph Embeddings Using Sparse Matrix Operations

**Venue:** MLSYS 2025 · **Subtheme:** Sparse Matrix Operations for Embedding Training

## What It Does

SparseTransX reformulates translational knowledge graph embedding (KGE) training to replace fine-grained scatter/gather operations with bulk sparse matrix multiplication (SpMM). For each training triplet (head, relation, tail), the method constructs a sparse incidence matrix A where each row represents one triplet: +1 in the head entity column and -1 in the tail entity column (for head-tail expressions) or additionally +1 in the relation column at offset entity_count (for head+relation-tail expressions). Multiplying A (sparse, M × (N+R)) by the embedding matrix E (dense, (N+R) × d) directly computes batched (head - tail) or (head + relation - tail) expressions via a single SpMM call instead of M individual lookups.

The method supports four translational models: TransE (h+r-t computation with L2 norm), TransR (head-tail with per-relation projection matrices Mr applied separately), TransH (two head-tail computations with hyperplane projections), and TorusE (h+r-t with torus distance). The backward pass benefits equally: gradients reduce to SpMM on the transpose A^T, avoiding materialization of intermediate activation tensors. The library uses iSpLib (compressed sparse row CSR format, SIMD vectorized with loop unrolling and cache blocking) for CPU and DGL g-SpMM (coordinate COO format with WARP-level operations) for GPU acceleration.

## The Key Result

On CPU (AMD EPYC 7763 64-core) and GPU (NVIDIA A100-SXM4 40GB), SparseTransX achieves up to 5.3x speedup on TransE training versus TorchKGE and up to 4.2x on GPU. For TransH specifically, GPU memory usage is reduced 11x (0.28 GB vs 3.1 GB), and total FLOPs drop from 483.87 billion to 220 billion on TransE. Cache miss rates improve from 29.37% (TorchKGE) to 26.54%.

## Why This Approach

KGE training triplets are inherently sparse: each triplet touches only 2-3 entity/relation embeddings out of millions, yet existing frameworks (TorchKGE, DGL-KE, PyG) perform dense embedding lookups (indirection through global embedding tables) followed by element-wise operations. This creates irregular memory access patterns and high backpropagation overhead. Sparse matrix libraries (iSpLib, DGL g-SpMM) are highly optimized for exactly this access pattern—bulk extraction of rows/columns from dense matrices—and provide SIMD vectorization, WARP-level parallelism, and automatic cache blocking. By reformulating the computation as a single SpMM, SparseTransX unifies multiple embedding operations into one high-level primitive that the library can optimize globally, bypassing Python-level overheads and enabling loop unrolling that scattered lookups cannot achieve.

## What It Leaves Open

- TorusE speedup is lower than TransE because the torus L2 dissimilarity function (applied post-embedding-extraction) dominates compute time; the SpMM speedup is offset by expensive distance calculation per triplet.
- TransH shows only moderate speedup because the per-relation projection matrices Mr are applied separately after SpMM extraction, making SpMM a smaller fraction of total training time.
- TransR backward performance on CPU is slower than DGL-KE in some configurations because DGL-KE uses custom gradient implementations via the DGL graph API; sparse matrix transpose and multiply may not be faster than specialized kernels.
- Distributed training results shown only as preliminary in Appendix F; not a primary evaluation focus, leaving scalability to multi-node training unclear.
- COO format for GPU requires format conversion overhead; performance on different sparsity patterns and tensor sizes may vary with format conversion cost.
